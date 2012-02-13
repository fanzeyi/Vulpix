# -*- coding: utf-8 -*- 

from tornado.web import HTTPError

from judge import Problem
from judge import ProblemDBMixin
from judge.base import BaseHandler

class HomeHandler(BaseHandler, ProblemDBMixin):
    def get(self):
        if self.current_user:
            title = self._("Home")
            breadcrumb = []
            breadcrumb.append((self._("Home"), '/'))
            newest_problem = self.select_problem_by_create(5)
            self.render('home.html', locals())
        else:
            self.render('index.html', locals())
