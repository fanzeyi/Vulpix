# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: home.py
# CREATED: 02:00:16 08/03/2012
# MODIFIED: 03:06:43 08/03/2012
# DESCRIPTION: Home handler

from judge.base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        title = self._("Home")
        breadcrumb = []
        breadcrumb.append((self._("Home"), "/"))
        self.render("home.html", locals())

__all__ = ["HomeHandler"]
