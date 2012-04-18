# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: home.py
# CREATED: 02:00:16 08/03/2012
# MODIFIED: 18:26:17 18/04/2012
# DESCRIPTION: Home handler

from contest import get_contest_status

from judge.db import ForumDBMixin
from judge.db import MemberDBMixin
from judge.db import ContestDBMixin
from judge.db import ProblemDBMixin
from judge.base import BaseHandler

class HomeHandler(BaseHandler, MemberDBMixin, ProblemDBMixin, ContestDBMixin, ForumDBMixin):
    def get(self):
        title = self._("Home")
        breadcrumb = []
        breadcrumb.append((self._("Home"), "/"))
        latest_problem = self.select_latest_visible_problem_order_by_id(count = 5)
        latest_contest = self.select_visible_contest(count = 5)
        latest_submit = self.select_submit_order_by_id(count = 5)
        for contest in latest_contest:
            contest.status = get_contest_status(contest)
        latest_topic = []
        latest_node = self.select_latest_node()
        count_problem = self.count_visible_problem()
        count_member = self.count_member()
        self.render("home.html", locals())

__all__ = ["HomeHandler"]
