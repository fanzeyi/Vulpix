# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: api.py
# CREATED: 00:26:38 16/03/2012
# MODIFIED: 00:30:53 16/03/2012

from tornado.web import HTTPError
from tornado.web import authenticated

from judge.db import Problem
from judge.db import ProblemDBMixin
from judge.base import BaseHandler

class GetProblemHandler(BaseHandler, ProblemDBMixin):
    @authenticated
    def get(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if not problem:
            raise HTTPError(404)
        self.write(problem.title)
        self.finish()

__all__ = ["GetProblemHandler"]
