# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: member.py
# CREATED: 02:18:23 09/03/2012
# MODIFIED: 03:10:44 09/03/2012
# DESCRIPTION: member handlers

import re

from judge.db import MemberDBMixin
from judge.base import BaseHandler
from judge.base import unauthenticated

class SigninHandler(BaseHandler, MemberDBMixin):
    @unauthenticated
    def get(self):
        self.render("signin.html", locals())

class SignupHandler(BaseHandler, MemberDBMixin):
    @unauthenticated
    def get(self):
        self.render("signup.html", locals())

__all__ = ["SigninHandler", "SignupHandler"]
