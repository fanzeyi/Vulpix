# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: contest.py
# CREATED: 15:46:17 15/03/2012
# MODIFIED: 14:50:32 16/03/2012

import datetime

from tornado.web import HTTPError
from tornado.web import authenticated

from judge.db import Contest
from judge.db import ContestDBMixin
from judge.base import BaseHandler

def get_contest_status(contest):
    status = 0
    now = datetime.datetime.now()
    if now >= contest.start_time and now <= contest.end_time:
        status = 1 #"Running"
    elif now <= contest.start_time:
        status = 2 #"Waiting"
    elif now >= contest.end_time:
        status = 3 #"Finished"
    if contest.invisible:
        status = 4 #"Invisible"
    if not status:
        status = 5 #"Unknown"
    return status

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
        contest.status = get_contest_status(contest)
        problems = self.select_contest_problem_by_contest_id(cid)
        for problem in problems:
            problem.submit = self.select_contest_submit_by_contest_id_problem_id_user_id(cid, problem.problem_id)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Contest'), '/contest'))
        breadcrumb.append((contest.title, '/contest/%d' % contest.id))
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
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Contest'), '/contest'))
        pages = self.get_page_count(count)
        for contest in contests:
            contest.status = get_contest_status(contest)
        self.render("contest_list.html", locals())

__all__ = ["ViewContestHandler", "ListContestHandlder"]
