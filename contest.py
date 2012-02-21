# -*- coding: utf-8 -*-

from judge import ContestDBMixin
from judge.base import BaseHandler

class ContestHandler(BaseHandler, ContestDBMixin):
    def get(self):
        pass

class ContestListHandler(BaseHandler, ContestDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        title = self._("Contest List")
        contests = self.select_contest_visible(start = int(start))
        self.render("contest_list.html", locals())
