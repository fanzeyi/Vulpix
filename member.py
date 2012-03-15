# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: member.py
# CREATED: 02:18:23 09/03/2012
# MODIFIED: 13:32:38 15/03/2012
# DESCRIPTION: member handlers

import re
import copy
import bcrypt

from tornado.web import authenticated

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
        usr = self.get_argument("usr", default = "")
        pwd = self.get_argument("pwd", default = "")
        error = []
        error.extend(self.check_username(usr.lower()))
        error.extend(self.check_password(pwd))
        pwd = pwd.encode("utf-8")
        pwd = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
        if not error:
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
        usr = self.get_argument("usr", default = "")
        pwd = self.get_argument("pwd", default = "")
        email = self.get_argument("email", default = "")
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

class SettingsHandler(BaseHandler, MemberDBMixin):
    @staticmethod
    def get_lang_code(lang):
        lang_dict = {
            'pas' : 1, 
            'c'   : 2, 
            'cpp' : 3, 
        }
        if lang not in lang_dict.keys():
            return 1
        return lang_dict[lang]
    @authenticated
    def get(self):
        title = self._("Settings")
        msg = self.get_secure_cookie("msg")
        if msg:
            self.clear_cookie("msg")
        member = self.current_user
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self.current_user.username, '/member/%s' % self.current_user.username))
        breadcrumb.append((self._('Settings'), '/settings'))
        self.render("settings.html", locals())
    @authenticated
    def post(self):
        email = self.get_argument("email", default = None)
        website = self.get_argument("website", default = "")
        tagline = self.get_argument("tagline", default = "")
        lang = self.get_argument("lang", default = "pas").lower()
        bio = self.get_argument("bio", default = "")
        error = []
        member = copy.copy(self.current_user)
        error.extend(self.check_email(email))
        error.extend(self.check_text_value(website, self._("Website"), max = 200, \
                                           regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')))
        error.extend(self.check_text_value(tagline, self._("Tagline"), max = 70))
        error.extend(self.check_text_value(lang, self._("Code Language"), vaild=["pas", "c", "cpp"]))
        error.extend(self.check_text_value(bio, self._("Bio"), max = 20000))
        member.email = self.xhtml_escape(email)
        member.website = self.xhtml_escape(website)
        member.tagline = self.xhtml_escape(tagline)
        member.bio = self.xhtml_escape(bio)
        member.lang = self.get_lang_code(lang)
        if error:
            title = self._("Settings")
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self.current_user.username, '/member/%s' % self.current_user.username))
            breadcrumb.append((self._('Settings'), '/settings'))
            self.render("settings.html", locals())
            return
        member.gravatar_link = self.get_gravatar_url(email)
        self.update_member(member)
        self.set_secure_cookie('msg', self._('Settings Updated.'))
        self.redirect('/settings')

__all__ = ["SigninHandler", "SignupHandler", "SignoutHandler", "SettingsHandler"]
