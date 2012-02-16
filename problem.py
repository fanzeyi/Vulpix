# -*- coding: utf-8 -*- 

from tornado.web import HTTPError

from judge import Problem
from judge import ProblemDBMixin
from judge import RelatedProblemDBMixin
from judge.base import BaseHandler

class ProblemHandler(BaseHandler, ProblemDBMixin, RelatedProblemDBMixin):
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

class ProblemListHandler(BaseHandler, ProblemDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        problems = self.select_problem_order_by_id(20, start)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Problem'), '/problem'))
        title = self._("Problems")
        self.render("problem_list.html", locals())
