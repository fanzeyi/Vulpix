# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/base/__init__.py
# CREATED: 01:49:33 08/03/2012
# MODIFIED: 16:12:25 13/03/2012
# DESCRIPTION: Base handler

import re
import hashlib
import httplib
import functools
import traceback

import tornado.web
import tornado.escape

def unauthenticated(method):
    """Decorate methods with this to require that user be NOT logged in"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            if self.request.method in ("GET", "HEAD"):
                self.redirect("/")
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(tornado.web.RequestHandler):
    _ = lambda self, text: self.locale.translate(text) # i18n func
    xhtml_escape = lambda self, text: tornado.escape.xhtml_escape(text) if text else text # xhtml escape
    def _check_text_value(self):
        '''Check text value is vaild'''
        pass
    def get_page_num(self):
        '''Return page num by input item num'''
        pass
    def get_current_user(self):
        '''Check user is logined'''
        pass
    def get_user_locale(self):
        '''Get user locale, first check cookie, then browser'''
        pass
    def sendmail(self):
        '''Send mail func, send mail to someone'''
        pass
    def render(self, tplname, args = {}):
        '''Rewrite render func for use jinja2'''
        if "self" in args.keys():
            args.pop("self")
        tpl = self.jinja2.get_template(tplname)
        ren = tpl.render(page = self, _ = self._, user = self.current_user, **args)
        self.write(ren)
        self.finish()
    def write_error(self, status_code, **kwargs):
        '''Rewrite write_error for custom error page'''
        if status_code == 404:
            self.render("404.html")
            return
        elif status_code == 500:
            error = []
            for line in traceback.format_exception(*kwargs['exc_info']):
                error.append(line)
            error = "\n".join(error)
            self.render("500.html", locals())
            return
        msg = httplib.responses[status_code]
        self.render("error.html", locals())
    @staticmethod
    def check_text_value(value, valName, max = 65535, min = 0, regex = None, regex_msg = None):
        ''' Common Check Text Value Function '''
        return []
    def check_username(self, usr, queryDB = False):
        error = []
        error.extend(self.check_text_value(usr, self._("Username"), max = 20, min = 3, \
                                           regex = re.compile(r'^([\w\d]*)$'), \
                                           regex_msg = self._("A username can only contain letters and digits.")))
        if not error and queryDB:
            query = self.select_member_by_username_lower(usr.lower())
            if query:
                error.append(self._("That username is taken. Please choose another."))
        return error
    def check_password(self, pwd):
        return self.check_text_value(pwd, self._("Password"), max = 32, min = 6)
    def check_email(self, email, queryDB = False):
        error = []
        error.extend(self.check_text_value(email, self._("E-mail"), max = 100, min = 3, \
                                           regex = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE), \
                                           regex_msg = self._("Your Email address is invalid.")))
        if not error and queryDB:
            query = self.select_member_by_email(email)
            if query:
                error.append(self._("That Email is taken. Please choose another."))
        return error
    def get_gravatar_url(self, email):
        gravatar_id = hashlib.md5(email.lower()).hexdigest()
        return "http://www.gravatar.com/avatar/%s?d=mm" % (gravatar_id) 
    @property
    def db(self):
        return self.application.db
    @property
    def jinja2(self):
        return self.application.jinja2

class BaseDBObject(object):
    ''' Base Table Object '''
    def __repr__(self):
        ''' for debug '''
        result = ", \n".join(["'%s': '%s'" % (attr, getattr(self, attr)) for attr in dir(self) if attr[0] != '_' and not callable(getattr(self, attr)) ])
        return "<{%s}>" % result
    def _init_row(self, row):
        keys = row.keys()
        for key in keys:
            setattr(self, key, row[key])

class BaseDBMixin(object):
    ''' Base Database Mixin '''
    def _new_object_by_row(self, Obj, row):
        obj = Obj()
        obj._init_row(row)
        return obj

