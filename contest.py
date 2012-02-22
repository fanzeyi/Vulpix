# -*- coding: utf-8 -*-

import datetime

from tornado.web import HTTPError
from tornado.web import authenticated

from judge import ContestDBMixin
from judge.base import BaseHandler

class ContestHandler(BaseHandler, ContestDBMixin):
    @authenticated
    def get(self, cid):
        try:
            cid = int(cid)
        except ValueError:
            raise HTTPError(404)
            return
        contest = self.select_contest_by_id(cid)
        if not contest:
            raise HTTPError(404)
            return
        related_problem = self.select_contest_submit_by_cid_and_uid(contest.id, self.current_user.id)
        now = datetime.datetime.now()
        self.render("contest.html", locals())


class ContestListHandler(BaseHandler, ContestDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        title = self._("Contest List")
        if self.current_user and self.current_user.admin:
            contests = self.select_contest(start = int(start))
        else:
            contests = self.select_contest_visible(start = int(start))
        self.render("contest_list.html", locals())
