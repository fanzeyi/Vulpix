# -*- coding: utf-8

import functools

import tornado.web
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
    def prepare(self):
        pass
    def get_current_user(self):
        return None
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
        ren = tpl.render(page = self, **args)
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
