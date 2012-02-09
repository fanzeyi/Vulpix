# -*- coding: utf-8 -*-

from base import BaseHandler
from base import unauthenticated

class SigninHandler(BaseHandler):
    @unauthenticated
    def get(self):
        self.render("signin.html", { 'title' : u"Sign In" })
    @unauthenticated
    def post(self):
        pass
