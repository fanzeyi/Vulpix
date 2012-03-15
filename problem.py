# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: problem.py
# CREATED: 04:04:57 15/03/2012
# MODIFIED: 01:14:52 16/03/2012

from tornado.web import HTTPError

from judge.db import Problem
from judge.db import ProblemDBMixin
from judge.base import BaseHandler

class ViewProblemHandler(BaseHandler, ProblemDBMixin):
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
            problems = self.select_problem_order_by_id(10, start)
        else:
            count = self.count_visible_problem()
            problems = self.select_problem_order_by_id_visible(10, start)
        pages = self.get_page_count(count)
        self.render("problem_list.html", locals())

__all__ = ["ViewProblemHandler", "ListProblemHandler"]
