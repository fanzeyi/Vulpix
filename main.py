# -*- coding: utf-8 -*-

import os
import sys
import datetime

import tornado.web
import tornado.locale
import tornado.ioloop
import tornado.options
import tornado.database
import tornado.httpserver
from tornado.options import define
from tornado.options import options

from jinja2 import Environment, FileSystemLoader

from base import BaseHandler
from config import mysql_config

from lang import LangeuageSetHandler
from member import MemberHandler
from member import SigninHandler
from member import SignupHandler
from member import SignoutHandler
from member import SettingsHandler
from member import ChangePasswordHandler

tornado.options.parse_command_line()

define("mysql_host",     default = mysql_config['mysql_host'])
define("mysql_database", default = mysql_config['mysql_database'])
define("mysql_user",     default = mysql_config['mysql_user'])
define("mysql_password", default = mysql_config['mysql_password'])

class HomeHandler(BaseHandler):
    def get(self):
        if self.current_user:
            title = self._("Home")
            self.render('home.html', locals())
        else:
            self.render('index.html', locals())

class TestHandler(BaseHandler):
    def get(self):
        self.set_secure_cookie_new('test', 'test')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/signin', SigninHandler), 
            (r'/signup', SignupHandler), 
            (r'/signout', SignoutHandler), 
            (r'/settings', SettingsHandler), 
            (r'/settings/changepass', ChangePasswordHandler), 
            (r'/member/(.*)', MemberHandler), 
            (r'/lang/(.*)', LangeuageSetHandler), 
            (r'/test', TestHandler), 
        ]
        settings = {
            'site_title' : u'Online Judge',
            'login_url' : '/signin',
            'template_path' : os.path.join(os.path.dirname(__file__), 'tpl'),
            'static_path' : os.path.join(os.path.dirname(__file__), "static"),
            'i18n_path' : os.path.join(os.path.dirname(__file__), 'i18n'), 
            'xsrf_cookies' : True,
            'cookie_secret' : '32954k1s668c4ad48dad436vd0402905',
            'bcrypt_salt' : '$2a$04$WL.FEXqZFwMOso3dsXOwuO', 
            'debug'   : True,
        }
        tornado.web.Application.__init__(self, handlers, **settings)
        tornado.locale.set_default_locale('zh_CN')
        tornado.locale.load_gettext_translations(self.settings['i18n_path'], "onlinejudge")
        self.jinja2 = Environment(loader = FileSystemLoader(self.settings['template_path']))
        self.db = tornado.database.Connection(
                  host=options.mysql_host, database=options.mysql_database,
                  user=options.mysql_user, password=options.mysql_password)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(8080))
    tornado.ioloop.IOLoop.instance().start()
