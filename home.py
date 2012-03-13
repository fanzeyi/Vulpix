# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: home.py
# CREATED: 02:00:16 08/03/2012
# MODIFIED: 19:38:23 10/03/2012
# DESCRIPTION: Home handler

from judge.base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        title = self._("Home")
        breadcrumb = []
        breadcrumb.append((self._("Home"), "/"))
        latest_problem = []
        latest_contest = []
        latest_topic = []
        count_problem = 0
        count_topic = 0
        count_member = 0
        self.render("home.html", locals())

__all__ = ["HomeHandler"]
