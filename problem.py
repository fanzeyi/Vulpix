# -*- coding: utf-8 -*- 

from tornado.web import HTTPError

from judge import Submit
from judge import Problem
from judge import SubmitDBMixin
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
            if problem.invisible and (self.current_user == None or self.current_user.admin == 0):
                    raise HTTPError(404)
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
        try:
            start = int(start)
        except ValueError:
            start = 0
        problems = self.select_problem_order_by_id(10, start)
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

class SubmitListHandler(BaseHandler, SubmitDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        submits = self.select_submit_desc(start = start)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Submit'), '/submit'))
        title = self._("Submit")
        self.render("submit.html", locals())
