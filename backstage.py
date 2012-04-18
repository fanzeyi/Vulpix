# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: backstage.py
# CREATED: 02:43:49 15/03/2012
# MODIFIED: 18:31:05 18/04/2012

import re
import datetime
import functools
from sqlalchemy.orm.exc import NoResultFound

from tornado.web import HTTPError

from judge.db import Node
from judge.db import Judger
from judge.db import Contest
from judge.db import Problem
from judge.db import ForumDBMixin
from judge.db import JudgerDBMixin
from judge.db import ContestDBMixin
from judge.db import ProblemDBMixin
from judge.base import BaseHandler

def backstage(method):
    """Decorate methods with this to require that user be NOT logged in"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            if self.current_user.admin:
                return method(self, *args, **kwargs)
        raise HTTPError(404)
    return wrapper

class AddProblemHandler(BaseHandler, ProblemDBMixin):
    @backstage
    def get(self):
        title = self._("Add Problem")
        pid = self.get_argument("pid", default = None)
        problem = None
        if pid:
            title = self._("Edit Problem")
            problem = self.select_problem_by_id(pid)
            if not problem:
                raise HTTPError(404)
            problem.content = self.xhtml_escape(problem.content)
            tagquery = self.select_problem_tag_by_problem_id(problem.id)
            tags = []
            for tag in tagquery:
                tags.append(tag.tagname)
        self.render("backstage/add_problem.html", locals())
    @backstage
    def post(self):
        probtitle = self.get_argument('probtitle', default = None)
        shortname = self.get_argument('shortname', default = None)
        timelimit = self.get_argument('timelimit', default = 1000)
        memlimit = self.get_argument('memlimit', default = 128)
        testpoint = self.get_argument('testpoint', default = None)
        invisible = self.get_argument('invisible', default = 0)
        content = self.get_argument('content', default = None)
        pid = self.get_argument('pid', default = 0)
        tags = self.get_arguments('tags[]')
        tags = map(self.xhtml_escape, tags)
        problem = Problem()
        error = []
        error.extend(self.check_text_value(probtitle, self._("Title"), required = True))
        error.extend(self.check_text_value(shortname, self._("Short Name"), required = True))
        error.extend(self.check_text_value(timelimit, self._("Time Limit"), required = True, is_num = True))
        error.extend(self.check_text_value(memlimit, self._("Memory Limit"), required = True, is_num = True))
        error.extend(self.check_text_value(testpoint, self._("Testpoint"), required = True, is_num = True))
        error.extend(self.check_text_value(invisible, self._("Invisible"), is_num = True, vaild = [0, 1]))
        error.extend(self.check_text_value(content, self._("Content"), max = 1000000, required = True))
        error.extend(self.check_text_value(testpoint, self._("Test Point"), required = True))
        problem.id = int(pid)
        problem.title = self.xhtml_escape(probtitle)
        problem.shortname = self.xhtml_escape(shortname)
        problem.timelimit = self.xhtml_escape(timelimit)
        problem.memlimit = self.xhtml_escape(memlimit)
        problem.testpoint = self.xhtml_escape(testpoint)
        problem.invisible = self.xhtml_escape(invisible)
        if error:
            problem.content = self.xhtml_escape(content)
            title = self._("Edit Problem")
            self.render("backstage/add_problem.html", locals())
            return
        problem.content = content
        if problem.id:
            self.update_problem(problem)
            self.delete_problem_tag_by_problem_id(problem.id)
        else:
            self.insert_problem(problem)
        for tag in tags:
            self.insert_problem_tag(tag, problem.id)
        self.redirect('/problem/%d' % problem.id)

class AddContestHandler(BaseHandler, ProblemDBMixin, ContestDBMixin):
    @backstage
    def get(self):
        title = self._("Add Contest")
        cid = self.get_argument("cid", default = 0)
        contest = None
        if cid:
            contest = self.select_contest_by_id(cid)
            title = self._("Edit Contest")
            related_problem = self.select_contest_problem_by_contest_id(contest.id)
        self.render("backstage/add_contest.html", locals())
    @backstage
    def post(self):
        title = self.get_argument("title", default = "")
        description = self.get_argument("description", default = "")
        start_time = self.get_argument("start_time", default = "")
        end_time = self.get_argument("end_time", default = "")
        invisible = self.get_argument("invisible", default = 0)
        cid = self.get_argument("cid", default = None)
        related_problem = self.get_arguments("link_problem[]")
        contest = Contest()
        contest.id = cid
        error = []
        error.extend(self.check_text_value(title, self._("Title"), required = True, max = 100))
        error.extend(self.check_text_value(description, self._("Description"), max = 20000))
        try:
            start_datetime = datetime.datetime.strptime(start_time, "%m/%d/%Y %H:%M")
            end_datetime = datetime.datetime.strptime(end_time, "%m/%d/%Y %H:%M")
        except ValueError:
            error.append(self._("Start/End Time Format is Invalid."))
        else:
            if start_datetime > end_datetime:
                error.append(self._("Start/End Time is invalid."))
        contest.title = self.xhtml_escape(title)
        contest.description = self.xhtml_escape(description)
        contest.start_time = self.xhtml_escape(start_time)
        contest.end_time = self.xhtml_escape(end_time)
        contest.invisible = self.xhtml_escape(invisible)
        contest.related_problem = related_problem
        if error:
            title = self._("Add Contest")
            related_problem = []
            for pid in contest.related_problem:
                related_problem.append(self.select_problem_by_id(pid))
            self.render("backstage/contest_create.html", locals())
            return
        contest.start_time = start_datetime
        contest.end_time = end_datetime
        if contest.id:
            self.update_contest(contest)
            self.delete_contest_problem_by_contest_id(contest.id)
        else:
            self.insert_contest(contest)
        for pid in contest.related_problem:
            self.insert_contest_problem(contest.id, pid)
        self.redirect("/contest/%d" % int(contest.id))

class AddNodeHandler(BaseHandler, ForumDBMixin):
    @backstage
    def get(self):
        title = self._("Add Node")
        nid = self.get_argument("nid", default = 0)
        node = None
        try:
            nid = int(nid)
        except ValueError:
            raise HTTPError(404)
        if nid:
            node = self.select_node_by_id(nid)
            if not node:
                raise HTTPError(404)
            title = self._("Edit Node")
        self.render("backstage/add_node.html", locals())
    @backstage
    def post(self):
        name = self.get_argument("name", default = "")
        link = self.get_argument("link", default = "").lower()
        nid = self.get_argument("nid", default = 0)
        error = []
        node = Node()
        error.extend(self.check_text_value(name, self._("Name"), required = True, max = 100))
        error.extend(self.check_text_value(link, self._("Link"), required = True, max = 100))
        if not error:
            try:
                duplinode = self.select_node_by_link(link)
            except NoResultFound:
                pass
            else:
                error.append(self._("This link have taken."))
        if nid:
            node.id = nid
        node.name = name
        node.link = link
        node.description = ""
        if error:
            title = self._("Edit Node")
            self.render("backstage/add_node.html", locals())
            return
        if node.id:
            self.update_node(node)
        else:
            self.insert_node(node)
        self.redirect("/go/%s" % node.link)

class ManageJudgerHandler(BaseHandler, JudgerDBMixin):
    @backstage
    def get(self):
        title = self._("Judger Manage")
        judgers = self.select_judgers()
        self.render("backstage/judger.html", locals())

class AddJudgerHandler(BaseHandler, JudgerDBMixin):
    @backstage
    def get(self):
        title = self._("Add Judger")
        jid = self.get_argument("jid", default = 0)
        judger = None
        try:
            jid = int(jid)
        except ValueError:
            raise HTTPError(404)
        if jid:
            judger = self.select_judger_by_id(jid)
            if not judger:
                raise HTTPError(404)
            title = self._("Edit Judger")
        self.render("backstage/add_judger.html", locals())
    @backstage
    def post(self):
        name = self.get_argument("name", default = "")
        description = self.get_argument("description", default = "")
        path = self.get_argument("path", default = "")
        priority = self.get_argument("priority", default = 0)
        pubkey = self.get_argument("pubkey", default = "")
        jid = self.get_argument("jid", default = 0)
        judger = Judger()
        error = []
        error.extend(self.check_text_value(name, self._("Name"), required = True, min = 1, max = 100))
        error.extend(self.check_text_value(description, self._("Description"), max = 5000))
        error.extend(self.check_text_value(path, self._("Path"), required = True, regex = re.compile(r"^http://(.*)"), max = 200))
        error.extend(self.check_text_value(priority, self._("Priority"), is_num = True))
        error.extend(self.check_text_value(pubkey, self._("RSA Public Key"), required = True))
        judger.id = jid
        judger.name = self.xhtml_escape(name)
        judger.description = self.xhtml_escape(description)
        judger.path = self.xhtml_escape(path)
        judger.priority = priority
        judger.pubkey = self.xhtml_escape(pubkey)
        if error:
            title = self._("Edit Judger")
            self.render("backstage/add_judger.html", locals())
            return
        if judger.id:
            self.update_judger(judger)
        else:
            self.insert_judger(judger)
        self.redirect("/backstage/judger")

__all__ = ["backstage", "AddProblemHandler", "AddContestHandler", "ManageJudgerHandler", "AddJudgerHandler", "AddNodeHandler"]
