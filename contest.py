# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: contest.py
# CREATED: 15:46:17 15/03/2012
# MODIFIED: 15:46:36 15/03/2012

import datetime

from tornado.web import HTTPError
from tornado.web import authenticated

from judge.db import Contest
from judge.db import ContestDBMixin
from judge.base import BaseHandler

class ViewContestHandler(BaseHandler, ContestDBMixin):
    @authenticated
    def get(self, cid):
        try:
            cid = int(cid)
        except ValueError:
            raise HTTPError(404)
        contest = self.select_contest_by_id(cid)
        if not contest:
            raise HTTPError(404)
        now = datetime.datetime.now()
        self.render("contest.html", locals())

class ListContestHandlder(BaseHandler, ContestDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        title = self._("Contest List")
        try:
            start = int(start)
        except ValueError:
            start = 0
        if self.current_user and self.current_user.admin:
            count = self.count_contest()
            contests = self.select_contest(start = start)
        else:
            count = self.count_visible_contest()
            contests = self.select_visible_contest(start = start)
        pages = self.get_page_count(count)
        self.render("contest_list.html", locals())

__all__ = ["ViewContestHandler"]
