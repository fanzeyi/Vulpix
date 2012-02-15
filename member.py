# -*- coding: utf-8 -*-

import re
import uuid
import bcrypt
import binascii
import datetime
from MySQLdb import escape_string

import tornado.web
import tornado.escape
import tornado.locale
from tornado.web import HTTPError
from tornado.web import authenticated

from judge import Member
from judge import AuthDBMixin
from judge import NoteDBMixin
from judge import MemberDBMixin
from judge import ResetMailDBMixin
from judge.base import BaseHandler
from judge.base import unauthenticated
from judge.utils import escape
from judge.utils import to_ascii
from judge.utils import unicode_len

class SigninHandler(BaseHandler, AuthDBMixin, MemberDBMixin):
    @unauthenticated
    def get(self):
        title = self._("Sign In")
        self.render("signin.html", locals())
    @unauthenticated
    def post(self):
        usr   = self.get_argument("usr", default = None)
        pwd   = self.get_argument("pwd", default = None)
        error = []
        if not usr and not pwd:
            self.redirect("/signin")
            return
        if not usr or not pwd:
            error.append(self._("Wrong Username and password combination."))
        else:
            p = re.compile(r'^([\w\d]*)$')
            if p.match(usr):
                """ TODO: check username and password is valid. """
                pwd = to_ascii(pwd)
                auth = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
                member = self.select_member_by_usr_pwd(usr, auth)
                if not member:
                    error.append(self._("Wrong Username and password combination."))
            else:
                error.append(self._("A username can only contain letters and digits."))
        if error:
            title = self._("Sign In")
            self.render("signin.html", locals())
            return
        auth = self.create_auth(member.id)
        if auth:
            self.set_cookie('auth', auth.secret)
            self.set_cookie('uid', str(auth.uid))
            go_next = self.get_argument('next', default = None)
            if go_next:
                self.redirect(go_next)
                return
            self.redirect('/')
        else:
            print "aa"
            raise HTTPError(500)

class SignupHandler(BaseHandler, MemberDBMixin, AuthDBMixin,):
    @unauthenticated
    def get(self):
        title = self._("Sign Up")
        self.render("signup.html", locals())
    @unauthenticated
    def post(self):
        self.require_setting('bcrypt_salt', 'bcrypt for Password')
        usr   = self.get_argument("usr", default = None)
        pwd   = self.get_argument("pwd", default = None)
        email = self.get_argument("email", default = None)
        error = []
        if usr:
            if len(usr) < 3 or len(usr) > 20:
                error.append(self._("A username should be between 3 and 15 characters long."))
            else:
                p = re.compile(r'^([\w\d]*)$')
                if p.match(usr):
                    """ TODO: check is username had been token. """
                    member = self.select_member_by_username(usr)
                    if member:
                        error.append(self._("That username is taken. Please choose another."))
                else:
                    error.append("A username can only contain letters and digits.")
        else:
            error.append(self._("A username is required!"))
        if pwd:
            if unicode_len(pwd) < 6 or unicode_len(pwd) > 32:
                error.append(self._("A password should be between 6 and 32 characters long."))
            else:
                pwd = to_ascii(pwd)
        else:
            error.append(self._("A password is required!"))
        if email:
            if len(email) > 100:
                error.append(self._("Email address cannot be longer than 100 characters long."))
            else:
                p = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
                if p.match(email):
                    email = email.lower()
                    """ TODO: check is email had been token. """
                    member = self.select_member_by_email(email)
                    if member:
                        error.append("That Email is taken. Please choose another.")
                else:
                    error.append(self._("Your Email address is invalid."))
        else:
            error.append(self._("Email Address is required!"))
        if error:
            title = self._("Sign Up")
            self.render("signup.html", locals())
            return
        member = Member()
        member.password = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
        member.username = usr
        member.email = email
        member.gravatar_link = self.get_gravatar_url(email)
        self.insert_member(member)
        auth = self.create_auth(member.id)
        self.set_cookie('auth', auth.secret)
        self.set_cookie('uid', str(auth.uid))
        self.redirect('/')

class SignoutHandler(BaseHandler, AuthDBMixin):
    @authenticated
    def get(self):
        auth = self.get_cookie('auth')
        self.delete_auth_by_secret(auth)
        self.clear_cookie('auth')
        self.clear_cookie('uid')
        self.redirect('/')

class SettingsHandler(BaseHandler, MemberDBMixin):
    @authenticated
    def get(self):
        title = self._("Settings")
        msg = self.get_secure_cookie("msg")
        if msg:
            msg = self._(msg)
            self.clear_cookie("msg")
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
        lang = self.get_argument("lang", default = "")
        bio = self.get_argument("bio", default = "")
        error = []
        member = None
        if email and email != self.current_user['email']:
            if len(email) > 100:
                error.append(self._("Email address cannot be longer than 100 characters long."))
            else:
                p = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
                if p.match(email):
                    email = escape_string(email.lower())
                    """ TODO: check is email had been token. """
                    member = self.select_member_by_email(email)
                    if member:
                        error.append("That Email is taken. Please choose another.")
                else:
                    error.append(self._("Your Email address is invalid."))
        elif email == None:
            error.append(self._("Email Address is required!"))
        if tagline:
            if unicode_len(tagline) > 70:
                error.append(self._("Tagline cannot be longer than 70 characters long."))
            else:
                tagline = tornado.escape.xhtml_escape(tagline)
        if website:
            if unicode_len(website) > 200:
                error.append(self._("Website address cannot be longer than 200 characters long.")); 
            p = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            if (p.match(website)):
                website = tornado.escape.xhtml_escape(website)
            else:
                error.append(self._("Website address is invalid."))
        if lang:
            if lang in ['pas', 'c', 'cpp']:
                if lang == 'pas':
                    lang = 1
                elif lang == 'c':
                    lang = 2
                elif lang == 'cpp':
                    lang = 3
            else:
                error.append(self._("Wrong Language select."))
        else:
            error.append(self._("Wrong Language select."))
        if bio:
            if unicode_len(bio) > 2000:
                error.append(self._("Bio cannot be longer than 2000 characters long."))
            else:
                bio = tornado.escape.xhtml_escape(bio)
        if error:
            if member:
                del member
            title = self._("Settings")
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self.current_user.username, '/member/%s' % self.current_user.username))
            breadcrumb.append((self._('Settings'), '/settings'))
            self.render("settings.html", locals())
            return 
        member = self.select_member_by_id(self.current_user['id'])
        member.email = email
        member.gravatar_link = self.get_gravatar_url(email)
        member.website = website
        member.tagline = tagline
        member.bio = bio
        member.lang = lang
        self.update_member(member)
        self.set_secure_cookie('msg', 'Settings Updated.')
        self.redirect('/settings')

class ChangePasswordHandler(BaseHandler, MemberDBMixin, AuthDBMixin):
    @authenticated
    def post(self):
        oldpwd = self.get_argument('oldpwd', default = None)
        newpwd = self.get_argument('newpwd', default = None)
        error = []
        if oldpwd:
            if unicode_len(oldpwd) < 6 or unicode_len(oldpwd) > 32:
                error.append(self._("A password should be between 6 and 32 characters long."))
            else:
                oldpwd = to_ascii(oldpwd)
                auth = bcrypt.hashpw(oldpwd, self.settings['bcrypt_salt'])
                users = self.select_member_by_usr_pwd(self.current_user['username_lower'], auth)
                if not users:
                    error.append(self._("Wrong password."))
        else:
            error.append(self._('Current password is required.'))
        if newpwd:
            if unicode_len(newpwd) < 6 or unicode_len(newpwd) > 32:
                error.append(self._("A password should be between 6 and 32 characters long."))
            else:
                newpwd = to_ascii(newpwd)
        else:
            error.append(self._("New password is required."))
        if error:
            title = self._("Change Password")
            self.render("settings_changepass.html", locals())
            return
        member = self.select_member_by_id(self.current_user['id'])
        member.password = bcrypt.hashpw(newpwd, self.settings['bcrypt_salt'])
        self.update_member(member)
        self.delete_auth_by_uid(member.id)
        auth = self.create_auth(member.id)
        self.set_cookie('auth', auth.secret)
        self.set_cookie('uid', str(auth.uid))
        self.set_secure_cookie('msg', 'Password Updated.')
        self.redirect('/settings')

class MemberHandler(BaseHandler, MemberDBMixin, NoteDBMixin):
    def get(self, username):
        title = username
        username = escape_string(username.lower())
        member = self.select_member_by_username(username)
        if not member:
            raise HTTPError(404)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((member.username, '/member/%s' % member.username))
        notes = self.select_note_by_mid(member.id, count = 5)
        self.render("member.html", locals())

class ForgetPasswordHandler(BaseHandler, MemberDBMixin, ResetMailDBMixin):
    @unauthenticated
    def get(self):
        title = self._("Forget Password")
        self.render("forget.html", locals())
    @unauthenticated
    def post(self):
        usr = self.get_argument('usr', default = None)
        email = self.get_argument('email', default = None)
        error = []
        users = ""
        if usr:
            p = re.compile(r'^([\w\d]*)$')
            if p.match(usr):
                users = self.select_member_by_username(usr)
                if not users:
                    error.append(self._("Sorry, We couldn't find you."))
            else:
                error.append(self._('A username can only contain letters and digits.'))
        else:
            error.append(self._('A username is required!'))
        if email:
            p = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
            if p.match(email):
                email = escape_string(email.lower())
                if users and users['email'] != email:
                    error.append(self._("Wrong Username and Email combination."))
            else:
                error.append(self._("Your Email address is invalid."))
        else:
            error.append(self._('Email Address is required!'))
        if users:
            query = self.select_reset_mail_last_by_uid(users.id)
            if query:
                delta = datetime.datetime.now() - query['create']
                if delta.days < 1:
                    error.append(self._("You can only request one reset mail in a day."))
        if error:
            title = self._("Forget Password")
            self.render("forget.html", locals())
            return
        reset = self.create_reset_mail(users.id)
        msg = """Hello, %s

    Please use this link to change your password:

        http://%s/reset/%s

    Here are some information about the requester:

    UA: %s
    IP: %s

%s""" % (users['username'], self.settings['base_domain'], reset.secret, self.request.headers['User-Agent'], self.request.remote_ip, self.settings['site_title'])
        self.sendmail(users['email'], "[%s] Reset Your Password" % (self.settings['site_title']), msg)
        self.redirect('/')

class ResetPasswordHandler(BaseHandler, MemberDBMixin, ResetMailDBMixin, AuthDBMixin):
    @unauthenticated
    def get(self, secret):
        if len(secret) != 32:
            raise HTTPError(404)
        reset = self.select_reset_mail_by_secret(secret)
        if reset: 
            title = self._('Reset Password')
            reset_user = self.select_member_by_id(reset.uid)
            self.render('reset.html', locals())
        else:
            raise HTTPError(404)
    @unauthenticated
    def post(self, secret):
        if len(secret) != 32:
            raise HTTPError(404)
        reset = self.select_reset_mail_by_secret(secret)
        if reset:
            newpwd = self.get_argument('newpwd', default = None)
            repeatpwd = self.get_argument('repeatpwd', default = None)
            error = []
            reset_user = self.select_member_by_id(reset.uid)
            if not reset_user:
                raise HTTPError(404)
            if newpwd != repeatpwd:
                error.append(_('Two passwords do not match.'))
            else:
                if unicode_len(newpwd) < 6 or unicode_len(newpwd) > 32:
                    error.append(self._("A password should be between 6 and 32 characters long."))
                else:
                    newpwd = to_ascii(newpwd)
            if error:
                title = self._("Reset Password")
                self.render('reset.html', locals())
                return
            reset_user.auth = bcrypt.hashpw(newpwd, self.settings['bcrypt_salt'])
            self.update_member(reset_user)
            self.delete_auth_by_uid(reset_user.id)
            auth = self.create_auth(reset_user.id)
            success = 1
            self.render('reset.html', locals())
        else:
            raise HTTPError(404)
