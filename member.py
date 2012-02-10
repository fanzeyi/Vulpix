# -*- coding: utf-8 -*-

import re
import uuid
import binascii
import bcrypt
import datetime

import tornado.web
import tornado.locale
from base import BaseHandler
from base import unauthenticated

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
            """ TODO: check username and password is valid. """
            auth = bcrypt.hashpw(pwd, self.settings['bcrypt_salt'])
            sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' and `password` = '%s' LIMIT 1""" \
                     % (usr.lower(), auth)
            users = self.db.get(sql)
            if not users:
                error.append(self._("Wrong Username and password combination."))
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
                if usr.isalnum():
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
            if len(pwd) < 6 or len(pwd) > 32:
                error.append(self._("A password should be between 6 and 32 characters long."))
        else:
            error.append(self._("A password is required!"))
        if email:
            if len(email) > 32:
                error.append(self._("Email address cannot be longer than 32 characters long."))
            else:
                p = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
                if p.search(email):
                    email = email.lower()
                    """ TODO: check is email had been token. """
                    sql = """SELECT * FROM `member` WHERE `email` = '%s' LIMIT 1""" \
                             % email
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
                 % auth
        self.db.execute(sql)
        self.clear_cookie('auth')
        self.clear_cookie('uid')
        self.redirect('/')
