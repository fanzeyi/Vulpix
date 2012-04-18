# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: member.py
# CREATED: 02:18:23 09/03/2012
# MODIFIED: 20:29:11 18/04/2012
# DESCRIPTION: member handlers

import re
import copy
import uuid
import binascii
import bcrypt
import datetime
from sqlalchemy.orm.exc import NoResultFound

from tornado.web import HTTPError
from tornado.web import authenticated

from judge.db import Member
from judge.db import MemberDBMixin
from judge.db import ProblemDBMixin
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
            try:
                member = self.select_member_by_usr_pwd(usr, pwd)
            except NoResultFound:
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
        member.password = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
        member.email = email
        member.gravatar_link = self.get_gravatar_url(email)
        member.create = datetime.datetime.now()
        self.db.add(member)
        self.db.commit()
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

class ChangePasswordHandler(BaseHandler, MemberDBMixin):
    @authenticated
    def post(self):
        oldpwd = self.get_argument('oldpwd', default = None)
        newpwd = self.get_argument('newpwd', default = None)
        error = []
        error.extend(self.check_password(oldpwd))
        error.extend(self.check_password(newpwd))
        oldpwd_hash = bcrypt.hashpw(oldpwd, self.settings['bcrypt_salt'])
        if oldpwd_hash != self.current_user.password:
            error.append(self._("Wrong Passowrd"))
        if error:
            title = self._("Change Password")
            self.render("settings_changepass.html", locals())
            return
        member = self.current_user
        member.password = bcrypt.hashpw(newpwd, self.settings['bcrypt_salt'])
        self.update_member_password(member)
        self.delete_auth_by_member_id(member.id)
        auth = self.create_auth(member.id)
        self.set_secure_cookie('auth', auth.secret)
        self.set_secure_cookie('uid', str(auth.member_id))
        self.set_secure_cookie('msg', self._('Password Updated.'))
        self.redirect('/settings')

class MemberHandler(BaseHandler, MemberDBMixin, ProblemDBMixin):
    def get(self, username):
        title = username
        username = username.lower()
        member = self.select_member_by_username_lower(username)
        if not member:
            raise HTTPError(404)
        submits = self.select_submit_by_member_id(member.id, 5)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((member.username, '/member/%s' % member.username))
        self.render("member.html", locals())

class ListMemberHandler(BaseHandler, MemberDBMixin):
    @authenticated
    def get(self):
        start = self.get_argument("start", default = 0)
        try:
            start = int(start)
        except ValueError:
            start = 0
        breadcrumb = []
        breadcrumb.append((self._('Home'),  '/'))
        breadcrumb.append((self._('Member List'), '/member'))
        title = self._("Member List")
        members = self.select_member_order_by_id(start = start)
        count = self.count_member()
        pages = self.get_page_count(count, 20)
        for member in members:
            member.accepted = self.count_accepted_by_member_id(member.id)
            member.submit = self.count_submit_by_member_id(member.id)
            member.rating = 0.0
            if member.submit:
                member.rating = round(float(member.accepted) / member.submit * 100, 2)
        self.render("member_list.html", locals())

class TestHandler(BaseHandler, MemberDBMixin):
    def post(self):
        usr = binascii.b2a_hex(uuid.uuid4().bytes)[3:10]
        pwd = binascii.b2a_hex(uuid.uuid4().bytes)[3:10]
        email = usr + "@gmail.com"
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
        member.password = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
        member.email = email
        member.gravatar_link = self.get_gravatar_url(email)
        member.create = datetime.datetime.now()
        self.db.add(member)
        self.db.commit()
        auth = self.create_auth(member.id)
        self.set_secure_cookie('auth', auth.secret)
        self.set_secure_cookie('uid', str(auth.member_id))
        self.redirect('/')

__all__ = ["SigninHandler", "SignupHandler", "SignoutHandler", "SettingsHandler", "ChangePasswordHandler", "MemberHandler", "ListMemberHandler", "TestHandler"]
