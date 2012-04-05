# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: problem.py
# CREATED: 04:04:57 15/03/2012
# MODIFIED: 16:59:41 05/04/2012

import os
import time

from tornado.web import HTTPError
from tornado.web import asynchronous
from tornado.web import authenticated

from judge.db import Judger
from judge.db import Submit
from judge.db import Problem
from judge.db import JudgerDBMixin
from judge.db import ProblemDBMixin
from judge.base import BaseHandler

LANG_DICT = {
    "pascal" : 1, 
    "c"      : 2, 
    "cpp"    : 3, 
}

LANG_EXT = {
    "pascal" : ".pas", 
    "c"      : ".c", 
    "cpp"    : ".cc", 
}

class ViewProblemHandler(BaseHandler, ProblemDBMixin, JudgerDBMixin):
    def get(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if not problem:
            raise HTTPError(404)
        if problem.invisible and (self.current_user == None or self.current_user.admin == 0):
            raise HTTPError(404)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Problem'), '/problem'))
        breadcrumb.append((problem.title, '/problem/%d' % problem.id))
        title = problem.title
        tags = self.select_problem_tag_by_problem_id(problem.id)
        self.render("problem.html", locals())
    @authenticated
    @asynchronous
    def post(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if not problem:
            raise HTTPError(404)
        if problem.invisible and (self.current_user == None or self.current_user.admin == 0):
            raise HTTPError(404)
        lang = self.get_argument("lang", default = 0)
        error = []
        try:
            codefile = self.request.files['codefile'][0]
        except KeyError:
            error.append(self._('Please Choose Your Code File'))
        else:
            filename, fileext = os.path.splitext(codefile.filename)
            if fileext not in ['.c', '.cc', '.cpp', '.cxx', '.pas']:
                error.append(self._('File Type Error!'))
            else:
                if lang not in ["c", "cpp", "pascal"]:
                    error.append(self._('Error Code Language Select'))
                else:
                    judger = self.select_judger_by_queue()
                    if not judger:
                        error.append(self._("No Judger Seted!"))
        if error:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Problem'), '/problem'))
            breadcrumb.append((problem.title, '/problem/%d' % problem.id))
            title = problem.title
            tags = self.select_problem_tag_by_problem_id(problem.id)
            self.render("problem.html", locals())
            return
        submit = Submit()
        submit.problem_id = problem.id
        submit.member_id = self.current_user.id
        submit.status = 0
        submit.timestamp = int(time.time())
        submit.code = codefile.body
        submit.user_agent = self.request.headers['User-Agent']
        submit.ip = self.request.remote_ip
        submit.lang = LANG_DICT[lang]
        self.insert_submit(submit)
        query = {}
        query["id"] = submit.id
        query["code"] = submit.code
        query["lang"] = submit.lang
        query["filename"] = problem.shortname + LANG_EXT[lang]
        query["shortname"] = problem.shortname
        query["timelimit"] = problem.timelimit
        query["memlimit"] = problem.memlimit
        query["testpoint"] = problem.testpoint
        self.post_to_judger(query, judger)
        self.redirect("/submit")

class ListProblemHandler(BaseHandler, ProblemDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        try:
            start = int(start)
        except ValueError:
            start = 0
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Problem'), '/problem'))
        title = self._("Problem")
        if self.current_user and self.current_user.admin:
            count = self.count_problem()
            problems = self.select_problem_order_by_id(20, start)
        else:
            count = self.count_visible_problem()
            problems = self.select_visible_problem_order_by_id(20, start)
        pages = self.get_page_count(count, 20)
        if self.current_user:
            for problem in problems:
                problem.submit = self.select_last_submit_by_problem_id_member_id(problem.id)
        self.render("problem_list.html", locals())

class ViewTagHandler(BaseHandler, ProblemDBMixin):
    def get(self, tagname):
        start = self.get_argument("start", default = 0)
        try:
            start = int(start)
        except ValueError:
            start = 0
        tagname = self.xhtml_escape(tagname)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Tag'), '/problem'))
        breadcrumb.append((tagname, '/tag/' + tagname))
        title = self._("Problem")
        if self.current_user and self.current_user.admin:
            count = self.count_problem_by_tagname(tagname)
            problems = self.select_problem_by_tagname(tagname, 20, start)
        else:
            count = self.count_visible_problem_by_tagname(tagname)
            problems = self.select_visible_problem_by_tagname(tagname, 20, start)
        pages = self.get_page_count(count, 20)
        if self.current_user:
            for problem in problems:
                problem.submit = self.select_last_submit_by_problem_id_member_id(problem.id)
        self.render("problem_list.html", locals())

class ListSubmitHandler(BaseHandler, ProblemDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        try:
            start = int(start)
        except ValueError:
            start = 0
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Submit'), '/submit'))
        title = self._("Submit List")
        count = self.count_submit()
        submits = self.select_submit_order_by_id(10, start)
        pages = self.get_page_count(count)
        self.render("submit_list.html", locals())

class ViewSubmitHandler(BaseHandler, ProblemDBMixin):
    def get(self, sid):
        try:
            sid = int(sid)
        except ValueError:
            raise HTTPError(404)
        submit = self.select_submit_by_id(sid)
        if not submit:
            raise HTTPError(404)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Submit'), '/submit'))
        breadcrumb.append(("# %d" % submit.id, '/submit/%d' % submit.id))
        title = self._("Submit #%d - %s") % (submit.id, submit.title)
        testpoint = []
        if submit.testpoint:
            testpoint = zip(range(1, len(submit.testpoint) + 1), submit.testpoint, \
                            submit.testpoint_time.split(","), submit.testpoint_memory.split(","))
        code_highlighted = self.highlight_code(submit.code, submit.lang)
        self.render("submit.html", locals())

__all__ = ["ViewProblemHandler", "ListProblemHandler", "ViewTagHandler", "ListSubmitHandler", "ViewSubmitHandler"]
