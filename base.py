# -*- coding: utf-8

import datetime
import functools
from MySQLdb import escape_string

import tornado.web
import tornado.locale
from tornado.web import HTTPError

from werkzeug.contrib.securecookie import SecureCookie

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
    _ = lambda self, text: self.locale.translate(text)
    def prepare(self):
        pass
    def get_current_user(self):
        auth = self.get_cookie('auth', default = None)
        uid = self.get_cookie('uid', default = None)
        user = None
        if auth and uid:
            auth = escape_string(auth)
            uid = escape_string(uid)
            sql = """SELECT * FROM `auth` WHERE `secret` = '%s' AND `uid` = '%s' LIMIT 1""" \
                     % (auth, uid)
            auth = self.db.get(sql)
            if auth:
                sql = """SELECT * FROM `member` WHERE `id` = '%d' LIMIT 1""" \
                         % (auth['uid'])
                user = self.db.get(sql)
                delta = auth['create'] - datetime.datetime.now() 
                if delta.days > 20:
                    """ Refresh Token """
                    sql = """DELETE FROM `auth` WHERE `secret` = '%s' LIMIT 1""" \
                             % auth
                    self.db.execute(sql)
                    random = binascii.b2a_hex(uuid.uuid4().bytes)
                    sql = """INSERT INTO `auth` (`uid`, `secret`, `create`) \
                             VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                             % (uid, random)
                    self.db.execute(sql)
                    self.set_cookie('auth', random)
                    self.set_cookie('uid', str(uid))
        return user
    def get_user_locale(self):
        result = self.get_cookie('OJ_LANG', default = None)
        if result == None:
            result = self.get_browser_locale()
        else:
            result = tornado.locale.get(result)
        return result
    @property
    def db(self):
        return self.application.db
    @property
    def jinja2(self):
        return self.application.jinja2
    def render(self, tplname, args = {}):
        if 'self' in args.keys():
            args.pop('self')
        tpl = self.jinja2.get_template(tplname)
        ren = tpl.render(page = self, _ = self.locale.translate, user = self.current_user, **args)
        self.write(ren)
        self.finish()
    def set_secure_cookie_new(self, name, value, expires_days = 30, **kwargs):
        self.require_setting('cookie_secret', 'secure cookie')
        x = SecureCookie({name : value}, self.settings['cookie_secret'])
        self.set_secure_cookie(name, x.serialize(), expires_days, **kwargs)
    def get_secure_cookie_new(self, name, value = None, max_age_days = 31):
        data = self.get_secure_cookie(name, value, max_age_days)
        if not data:
            return value
        x = SecureCookie.unserialize(data, self.settings['cookie_secret'])
        return x[name]
