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
from base import BaseHandler
from base import unauthenticated
from utils import escape
from utils import to_ascii
from utils import unicode_len

class SigninHandler(BaseHandler):
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
                sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' and `password` = '%s' LIMIT 1""" \
                         % (escape_string(usr.lower()), auth)
                users = self.db.get(sql)
                if not users:
                    error.append(self._("Wrong Username and password combination."))
            else:
                error.append(self._("A username can only contain letters and digits."))
        if error:
            title = self._("Sign In")
            self.render("signin.html", locals())
            return
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `auth` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                 % (users['id'], random)
        self.db.execute(sql)
        self.set_cookie('auth', random)
        self.set_cookie('uid', str(users['id']))
        go_next = self.get_argument('next', default = None)
        if go_next:
            self.redirect(go_next)
            return
        self.redirect('/')

class SignupHandler(BaseHandler):
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
                    sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' LIMIT 1""" \
                             % usr.lower()
                    users = self.db.get(sql)
                    if users:
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
                    sql = """SELECT * FROM `member` WHERE `email` = '%s' LIMIT 1""" \
                             % escape(email)
                    users = self.db.get(sql)
                    if users:
                        error.append("That Email is taken. Please choose another.")
                else:
                    error.append(self._("Your Email address is invalid."))
        else:
            error.append(self._("Email Address is required!"))
        if error:
            title = self._("Sign Up")
            self.render("signup.html", locals())
            return
        pwd = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
        sql = """INSERT INTO `member` (`username`, `username_lower`, `password`,  `email`, `create`) \
                 VALUES ('%s', '%s', '%s', '%s', UTC_TIMESTAMP())""" \
                 % (usr, usr.lower(), pwd, email)
        uid = self.db.execute(sql)
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `auth` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                 % (uid, random)
        self.db.execute(sql)
        self.set_cookie('auth', random)
        self.set_cookie('uid', str(uid))
        self.redirect('/')

class SignoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        auth = self.get_cookie('auth')
        sql = """DELETE FROM `auth` WHERE `secret` = '%s' LIMIT 1""" \
                 % escape_string(auth)
        self.db.execute(sql)
        self.clear_cookie('auth')
        self.clear_cookie('uid')
        self.redirect('/')

class SettingsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        title = self._("Settings")
        msg = self.get_secure_cookie("msg")
        if msg:
            msg = self._(msg)
            self.clear_cookie("msg")
        self.render("settings.html", locals())
    @tornado.web.authenticated
    def post(self):
        email = self.get_argument("email", default = None)
        website = self.get_argument("website", default = "")
        tagline = self.get_argument("tagline", default = "")
        bio = self.get_argument("bio", default = "")
        error = []
        if email and email != self.current_user['email']:
            if len(email) > 100:
                error.append(self._("Email address cannot be longer than 100 characters long."))
            else:
                p = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
                if p.match(email):
                    email = escape_string(email.lower())
                    """ TODO: check is email had been token. """
                    sql = """SELECT * FROM `member` WHERE `email` = '%s' LIMIT 1""" \
                             % email
                    users = self.db.get(sql)
                    if users:
                        error.append("That Email is taken. Please choose another.")
                else:
                    error.append(self._("Your Email address is invalid."))
        elif email == None:
            error.append(self._("Email Address is required!"))
        if tagline:
            if unicode_len(tagline) > 70:
                error.append(self._("Tagline cannot be longer than 70 characters long."))
            else:
                tagline = escape(tornado.escape.xhtml_escape(tagline))
        if website:
            if unicode_len(website) > 200:
                error.append(self._("Website address cannot be longer than 200 characters long.")); 
            p = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            if (p.match(website)):
                website = escape(tornado.escape.xhtml_escape(website))
            else:
                error.append(self._("Website address is invalid."))
        if bio:
            if unicode_len(bio) > 2000:
                error.append(self._("Bio cannot be longer than 2000 characters long."))
            else:
                bio = escape(tornado.escape.xhtml_escape(bio))
        if error:
            title = self._("Settings")
            self.render("settings.html", locals())
            return 
        sql = """UPDATE `member` SET `email` = '%s', \
                                     `website` = '%s', \
                                     `tagline` = '%s', \
                                     `bio` = '%s' \
                                 WHERE `id` = '%d'""" % \
                 (email, website, tagline, bio, self.current_user['id'])
        self.db.execute(sql)
        self.set_secure_cookie('msg', 'Settings Updated.')
        self.redirect('/settings')

class ChangePasswordHandler(BaseHandler):
    @tornado.web.authenticated
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
                sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' and `password` = '%s' LIMIT 1""" \
                         % (self.current_user['username_lower'], auth)
                users = self.db.get(sql)
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
        auth = bcrypt.hashpw(newpwd, self.settings['bcrypt_salt'])
        sql = """UPDATE `member` SET `password` = '%s' WHERE `id` = '%d'""" \
                 % (auth, self.current_user['id'])
        self.db.execute(sql)
        sql = """DELETE FROM `auth` WHERE `uid` = '%d'""" \
                 % (self.current_user['id'])
        self.db.execute(sql)
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `auth` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                 % (users['id'], random)
        self.db.execute(sql)
        self.set_cookie('auth', random)
        self.set_cookie('uid', str(users['id']))
        self.set_secure_cookie('msg', 'Password Updated.')
        self.redirect('/settings')

class MemberHandler(BaseHandler):
    def get(self, username):
        title = username
        username = escape_string(username.lower())
        sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' LIMIT 1""" \
                 % username
        member = self.db.get(sql)
        if not member:
            raise HTTPError(404)
        self.render("member.html", locals())

class ForgetPasswordHandler(BaseHandler):
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
                    sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' LIMIT 1""" \
                             % usr.lower()
                    users = self.db.get(sql)
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
            sql = """SELECT * FROM `reset_mail` WHERE `uid` = '%d' ORDER BY `create` DESC LIMIT 1""" % (users['id'])
            query = self.db.get(sql)
            if query:
                delta = datetime.datetime.now() - query['create']
                if delta.days < 1:
                    error.append(self._("You can only request one reset mail in a day."))
        if error:
            title = self._("Forget Password")
            self.render("forget.html", locals())
            return
        secret = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `reset_mail` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                 % (users['id'], secret)
        self.db.execute(sql)
        msg = """Hello, %s

    Please use this link to change your password:

        http://%s/reset/%s

    Here are some information about the requester:

    UA: %s
    IP: %s

%s""" % (users['username'], self.settings['base_domain'], secret, self.request.headers['User-Agent'], self.request.remote_ip, self.settings['site_title'])
        self.sendmail(users['email'], "[%s] Reset Your Password" % (self.settings['site_title']), msg)
        self.redirect('/')

class ResetPasswordHandler(BaseHandler):
    @unauthenticated
    def get(self, secret):
        if len(secret) != 32:
            raise HTTPError(404)
        sql = """SELECT * FROM `reset_mail` WHERE `secret` = '%s' LIMIT 1""" % (escape(secret))
        query = self.db.get(sql)
        if query:
            title = self._('Reset Password')
            sql = """SELECT * FROM `member` WHERE `id` = '%d' LIMIT 1""" % (query['uid'])
            reset_user = self.db.get(sql)
            self.render('reset.html', locals())
        else:
            raise HTTPError(404)
    @unauthenticated
    def post(self, secret):
        if len(secret) != 32:
            raise HTTPError(404)
        sql = """SELECT * FROM `reset_mail` WHERE `secret` = '%s' LIMIT 1""" % (escape(secret))
        query = self.db.get(sql)
        if query:
            newpwd = self.get_argument('newpwd', default = None)
            repeatpwd = self.get_argument('repeatpwd', default = None)
            error = []
            sql = """SELECT * FROM `member` WHERE `id` = '%d' LIMIT 1""" % (query['uid'])
            reset_user = self.db.get(sql)
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
            auth = bcrypt.hashpw(newpwd, self.settings['bcrypt_salt'])
            sql = """UPDATE `member` SET `password` = '%s' WHERE `id` = '%d'""" \
                     % (auth, reset_user['id'])
            self.db.execute(sql)
            sql = """DELETE FROM `auth` WHERE `uid` = '%d'""" \
                     % (reset_user['id'])
            self.db.execute(sql)
            sql = """DELETE FROM `reset_mail` WHERE `uid` = '%d'""" \
                     % (reset_user['id'])
            print sql
            self.db.execute(sql)
            success = 1
            self.render('reset.html', locals())
        else:
            raise HTTPError(404)
