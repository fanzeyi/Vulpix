# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/base/__init__.py
# CREATED: 01:49:33 08/03/2012
# MODIFIED: 15:42:49 19/04/2012
# DESCRIPTION: Base handler

import re
import time
import urllib
import hashlib
import httplib
import datetime
import functools
import traceback
import simplejson as json
from operator import itemgetter
from pygments import highlight
from pygments.lexers import CLexer
from pygments.lexers import CppLexer
from pygments.lexers import DelphiLexer
from pygments.formatters import HtmlFormatter
from sqlalchemy.exc import StatementError
from sqlalchemy.orm.exc import NoResultFound

import tornado.web
import tornado.escape
from tornado.httpclient import AsyncHTTPClient

from judge.db import Auth
from judge.db import Member
from judge.utils import _len

CODE_LEXER = {
    1 : DelphiLexer, 
    2 : CLexer, 
    3 : CppLexer, 
}

CODE_LANG = {
    1 : "delphi", 
    2 : "c", 
    3 : "cpp", 
}

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
    def get_page_count(self, count, pre = 10):
        '''Return page num by input item num'''
        return count / pre + (1 if count % pre else 0)
    def get_current_user(self):
        '''Check user is logined'''
        auth = self.get_secure_cookie("auth")
        member_id = self.get_secure_cookie("uid")
        member = None
        if auth and member_id:
            try:
                auth = self.db.query(Auth).filter_by(secret = auth).filter_by(member_id = member_id).one()
            except StatementError:
                # for mysql session broken
                self.db.rollback()
                auth = self.db.query(Auth).filter_by(secret = auth).filter_by(member_id = member_id).one()
            if auth:
                member = self.db.query(Member).get(auth.member_id)
                if member:
                    delta = auth.create - datetime.datetime.now()
                    if delta.days > 20:
                        """ Refresh Token """
                        auth.delete()
                        self.db.commit()
                        auth = Auth()
                        auth.member_id = member_id
                        auth.secret = binascii.b2a_hex(uuid.uuid4().bytes)
                        auth.create = datetime.datetime.now()
                        self.db.add(auth)
                        self.db.commit()
                        self.set_cookie('auth', auth.secret)
                        self.set_cookie('uid', auth.member_id)
                else:
                    self.clear_cookie("auth")
                    self.clear_cookie("uid")
        return member
    def get_user_locale(self):
        '''Get user locale, first check cookie, then browser'''
        result = self.get_cookie('LANG', default = None)
        if result == None:
            result = self.get_browser_locale()
        else:
            result = tornado.locale.get(result)
        return result
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
        self.db.close()
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
    def check_text_value(self, value, valName, required = False, max = 65535, min = 0, regex = None, regex_msg = None, is_num = False, vaild = []):
        ''' Common Check Text Value Function '''
        error = []
        if not value:
            if required:
                error.append(self._("%s is required") % valName)
            return error
        if is_num:
            try:
                tmp = int(value)
            except ValueError:
                return [self._("%s must be a number.") % valName]
            else:
                if vaild and tmp not in vaild:
                    return [self._("%s is invalid.") % valName]
                return []
        if _len(value) > max:
            error.append(self._("%s is too long.") % valName)
        elif _len(value) < min:
            error.append(self._("%s is too short.") % valName)
        if regex:
            if not regex.match(value):
                if regex_msg:
                    error.append(regex_msg)
                else:
                    error.append(self._("%s is invalid.") % valName)
        elif vaild and value not in vaild:
            errora.append(self._("%s is invalid.") % valName)
        return error
    def check_username(self, usr, queryDB = False):
        error = []
        error.extend(self.check_text_value(usr, self._("Username"), required = True, max = 20, min = 3, \
                                           regex = re.compile(r'^([\w\d]*)$'), \
                                           regex_msg = self._("A username can only contain letters and digits.")))
        if not error and queryDB:
            try:
                query = self.select_member_by_username_lower(usr.lower())
            except NoResultFound:
                pass
            else:
                error.append(self._("That username is taken. Please choose another."))
        return error
    def check_password(self, pwd):
        return self.check_text_value(pwd, self._("Password"), required = True, max = 32, min = 6)
    def check_email(self, email, queryDB = False):
        error = []
        error.extend(self.check_text_value(email, self._("E-mail"), required = True, max = 100, min = 3, \
                                           regex = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE), \
                                           regex_msg = self._("Your Email address is invalid.")))
        if not error and queryDB:
            try:
                query = self.select_member_by_email(email)
            except NoResultFound:
                pass
            else:
                error.append(self._("That Email is taken. Please choose another."))
        return error
    def get_gravatar_url(self, email):
        gravatar_id = hashlib.md5(email.lower()).hexdigest()
        return "http://www.gravatar.com/avatar/%s?d=mm" % (gravatar_id) 
    def post_to_judger(self, query, judger, callback = None):
        query["time"] = time.time()
        query["code"] = query["code"].decode("utf-8")
        query = dict(sorted(query.iteritems(), key=itemgetter(1)))
        jsondump = json.dumps(query)
        sign = hashlib.sha1(jsondump + judger.pubkey.strip()).hexdigest()
        query["sign"] = sign
        http_client = AsyncHTTPClient()
        http_client.fetch(judger.path, method = "POST", body = urllib.urlencode({"query" : json.dumps(query)}), callback = callback)
    def highlight_code(self, code, lang):
        return highlight(code, CODE_LEXER[lang](), HtmlFormatter(linenos = True))   
        codestr = highlight(code, CODE_LEXER[lang](), HtmlFormatter(nowrap = True))
        table = '<div class="highlight"><table><tr><td class="gutter"><pre class="line-numbers">'
        code = ''
        lines = codestr.split("\n")
        for index, line in zip(range(len(lines)), lines):
            table  +=  "<span class='line-number'>%d</span>\n" % (index + 1)
            code   +=  "<span class='line'>%s</span>\n" % line
        table  +=  "</pre></td><td class='code'><pre><code class='%s'>%s</code></pre></td></tr></table></div>" % (CODE_LANG[lang], code)
        return table
    @property
    def db(self):
        return self.application.db
    @property
    def jinja2(self):
        return self.application.jinja2
