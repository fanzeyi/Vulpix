# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: problem.py
# CREATED: 04:04:57 15/03/2012
# MODIFIED: 04:09:32 15/03/2012

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

__all__ = ["ViewProblemHandler"]
