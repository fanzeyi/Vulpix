# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: backstage.py
# CREATED: 02:43:49 15/03/2012
# MODIFIED: 15:53:23 15/03/2012

import datetime
import functools

from tornado.web import HTTPError

from judge.db import Contest
from judge.db import Problem
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
            related_problem_id = self.select_contest_problem_by_contest_id(contest.id)
            related_problem = []
            for pid in related_problem_id:
                related_problem.append(self.select_problem_by_id(pid))
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
            self.delete_contest_problem_by_cid(contest.id)
        else:
            self.insert_contest(contest)
        for pid in contest.related_problem:
            self.insert_contest_problem(cid = contest.id, pid = pid)
        self.redirect("/contest/%d" % int(contest.id))

__all__ = ["AddProblemHandler", "AddContestHandler"]
