# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: member.py
# CREATED: 02:18:23 09/03/2012
# MODIFIED: 16:25:52 13/03/2012
# DESCRIPTION: member handlers

import re
import bcrypt

from judge.db import Member
from judge.db import MemberDBMixin
from judge.base import BaseHandler
from judge.base import unauthenticated

class SigninHandler(BaseHandler, MemberDBMixin):
    @unauthenticated
    def get(self):
        self.render("signin.html", locals())
    @unauthenticated
    def post(self):
        usr = self.get_argument("usr", default = None)
        pwd = self.get_argument("pwd", default = None)
        error = []
        error.extend(self.check_username(usr.lower()))
        error.extend(self.check_password(pwd))
        pwd = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
        member = self.select_member_by_usr_pwd(usr, pwd)
        if not member:
            error.append(self._("Wrong Username and password combination."))
        if error:
            self.render("signin.html", locals())
            return
        auth = self.create_auth(member.id)
        self.set_secure_cookie("auth", auth.secret)
        self.set_secure_cookie("uid", str(auth.member_id))
        go_next = self.get_argument("next", default = None)
        if go_next:
            self.redirect(go_next)
            return
        self.redirect("/")

class SignupHandler(BaseHandler, MemberDBMixin):
    @unauthenticated
    def get(self):
        self.render("signup.html", locals())
    @unauthenticated
    def post(self):
        self.require_setting('bcrypt_salt', 'bcrypt for Password')
        usr = self.get_argument("usr", default = None)
        pwd = self.get_argument("pwd", default = None)
        email = self.get_argument("email", default = None)
        error = []
        error.extend(self.check_username(usr.lower(), queryDB = True))
        error.extend(self.check_password(pwd))
        error.extend(self.check_email(email, queryDB = True))
        if error:
            self.render("signup.html", locals())
            return
        member = Member()
        member.username = usr
        member.username_lower = usr.lower()
        member.passowrd = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
        member.email = email
        member.gravatar_link = self.get_gravatar_url(email)
        self.insert_member(member)
        auth = self.create_auth(member.id)
        self.set_secure_cookie('auth', auth.secret)
        self.set_secure_cookie('uid', str(auth.member_id))
        self.redirect('/')

class SignoutHandler(BaseHandler, MemberDBMixin):
    @authenticated
    def get(self):
        auth = self.get_secure_cookie('auth')
        self.delete_auth_by_secret(auth)
        self.clear_cookie('auth')
        self.clear_cookie('uid')
        self.redirect('/')

__all__ = ["SigninHandler", "SignupHandler", "SignoutHandler"]
