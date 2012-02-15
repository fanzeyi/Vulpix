# -*- coding: utf-8

import smtplib
import hashlib
import datetime
import functools
from email.mime.text import MIMEText
from MySQLdb import escape_string
from werkzeug.contrib.securecookie import SecureCookie

import tornado.web
import tornado.escape
import tornado.locale
from tornado.web import HTTPError

from judge import Member
from judge.utils import unicode_len


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
    xhtml_escape = lambda self, text: tornado.escape.xhtml_escape(text) if text else text
    def prepare(self):
        pass
    def _check_text_value(self, text, title, required = False, max = 0):
        error = []
        if text:
            if max:
                if unicode_len(text) > max:
                    error.append(self._('%s is too long.' % title))
        else:
            if required:
                error.append(self._('%s is Required!' % title))
        return error
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
                user = Member()
                query = self.db.get(sql)
                if query:
                    user._init_row(query)
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
                else:
                    self.clear_cookie('auth')
                    self.clear_cookie('uid')
        return user
    def get_user_locale(self):
        result = self.get_cookie('OJ_LANG', default = None)
        if result == None:
            result = self.get_browser_locale()
        else:
            result = tornado.locale.get(result)
        return result
    def sendmail(self, to, subject, msg):
        self.require_setting('default_mail', 'Send Mail')
        self.require_setting('mail_server', 'Send Mail')
        msg = MIMEText(msg)
        msg['Subject'] = subject
        msg['From'] = self.settings['default_mail']
        msg['To'] = to
        s = smtplib.SMTP(self.settings['mail_server'])
        s.sendmail(self.settings['default_mail'], [to], msg.as_string())
        s.quit()
    @property
    def db(self):
        return self.application.db
    @property
    def jinja2(self):
        return self.application.jinja2
    @property
    def markdown(self):
        return self.application.markdown
    def get_gravatar_url(self, email):
        gravatar_id = hashlib.md5(email.lower()).hexdigest()
        return "http://www.gravatar.com/avatar/%s?d=mm" % (gravatar_id) 
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
