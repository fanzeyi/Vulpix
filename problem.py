# -*- coding: utf-8 -*- 

import os
import time

from tornado.web import HTTPError
from tornado.web import authenticated

from judge import Submit
from judge import Problem
from judge import SubmitDBMixin
from judge import ProblemDBMixin
from judge import RelatedProblemDBMixin
from judge.base import BaseHandler

class ProblemHandler(BaseHandler, ProblemDBMixin, RelatedProblemDBMixin, SubmitDBMixin):
    def get(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if problem:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Problem'), '/problem'))
            breadcrumb.append((problem.title, '/problem/%d' % problem.id))
            title = self._("Problem") + u" › " + problem.title
            related_note = self.select_related_problem_by_pid(problem.id)
            self.render("problem.html", locals())
        else:
            raise HTTPError(404)
    @authenticated
    def post(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if not problem:
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
                if lang not in ['1', '2', '3']:
                    error.append(self._('Error Code Language Select'))
        if error:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Problem'), '/problem'))
            breadcrumb.append((problem.title, '/problem/%d' % problem.id))
            title = self._("Problem") + u" › " + problem.title
            related_note = self.select_related_problem_by_pid(problem.id)
            self.render("problem.html", locals())
            return
        code_dir = os.path.join(self.settings['code_save_path'], str(self.current_user.id))
        if not os.path.exists(code_dir):
            os.mkdir(code_dir)
        timestamp = int(time.time())
        code_file_path = os.path.join(code_dir, '%s%s.%d' % (problem.shortname, fileext, timestamp))
        with open(code_file_path, 'w') as codefp:
            codefp.write(codefile.body)
        submit = Submit()
        submit.member_id = self.current_user.id
        submit.problem_id = problem.id
        submit.lang = lang
        submit.user_agent = self.request.headers['User-Agent']
        submit.ip = self.request.remote_ip
        submit.timestamp = timestamp
        self.insert_submit(submit)
        self.redirect("/submit")

class ProblemListHandler(BaseHandler, ProblemDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        problems = self.select_problem_order_by_id(20, start)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Problem'), '/problem'))
        title = self._("Problem")
        self.render("problem_list.html", locals())

class SubmitListHandler(BaseHandler, SubmitDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        submits = self.select_submit_desc(start = start)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Submit'), '/submit'))
        title = self._("Submit")
        self.render("submit.html", locals())
