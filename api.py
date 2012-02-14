# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from judge import ProblemDBMixin
from judge.base import BaseHandler

class ProblemGetAPIHandler(BaseHandler, ProblemDBMixin):
    def get(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
            return
        problem = self.select_problem_by_id(pid)
        if problem:
            self.write(problem.title)
            return
        raise HTTPError(404)
