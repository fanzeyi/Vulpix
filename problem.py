# -*- coding: utf-8 -*- 

from tornado.web import HTTPError

from judge import Problem
from judge import ProblemDBMixin
from judge.base import BaseHandler

class ProblemHandler(BaseHandler, ProblemDBMixin):
    def get(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if problem:
            title = self._("Problem") + u" › " + problem.title
            self.render("problem.html", locals())
        else:
            raise HTTPError(404)
