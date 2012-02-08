# -*- coding: utf-8

import os
import uuid
import marshal
import binascii

import tornado.web

from werkzeug.contrib.securecookie import SecureCookie

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    @property
    def jinja2(self):
        return self.application.jinja2
    def render(self, tplname, **kwargs):
        self.write(self.jinja2.get_template(tplname).render(**kwargs))
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
