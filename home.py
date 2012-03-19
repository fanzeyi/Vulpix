# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: home.py
# CREATED: 02:00:16 08/03/2012
# MODIFIED: 19:51:24 19/03/2012
# DESCRIPTION: Home handler

from contest import get_contest_status

from judge.db import ContestDBMixin
from judge.db import ProblemDBMixin
from judge.base import BaseHandler

class HomeHandler(BaseHandler, ProblemDBMixin, ContestDBMixin):
    def get(self):
        title = self._("Home")
        breadcrumb = []
        breadcrumb.append((self._("Home"), "/"))
        latest_problem = self.select_latest_visible_problem_order_by_id()
        latest_contest = self.select_visible_contest(count = 5)
        for contest in latest_contest:
            contest.status = get_contest_status(contest)
        latest_topic = []
        count_problem = 0
        count_topic = 0
        count_member = 0
        self.render("home.html", locals())

__all__ = ["HomeHandler"]
