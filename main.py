# -*- coding: utf-8 -*-

import re
import sys
import markdown
import datetime
from jinja2 import Environment, FileSystemLoader

import tornado.web
import tornado.locale
import tornado.ioloop
import tornado.options
import tornado.database
import tornado.httpserver
from tornado.options import define
from tornado.options import options

from config import site_config
from config import mysql_config

from judge import MemberDBMixin
from judge.base import BaseHandler
from judge.utils import escape
from judge.filters import filters

from api import ProblemGetAPIHandler
from lang import SetLangeuageHandler
from home import HomeHandler
from note import NoteHandler
from note import CreateNoteHandler
from note import DeleteNoteHandler
from note import MemberNotesHandler
from forum import ForumIndexHandler
from forum import ForumNodeHandler
from forum import TopicCreateHandler
from forum import TopicHandler
from member import MemberHandler
from member import SigninHandler
from member import SignupHandler
from member import SignoutHandler
from member import SettingsHandler
from member import ResetPasswordHandler
from member import ChangePasswordHandler
from member import ForgetPasswordHandler
from problem import ProblemHandler
from problem import ProblemListHandler
from problem import SubmitListHandler
from contest import ContestHandler
from contest import ContestListHandler
from backstage import BackstageHandler
from backstage import AddProblemHandler
from backstage import CreateNodeHandler
from backstage import CreateContestHandler

tornado.options.parse_command_line()

define("mysql_host",     default = mysql_config['mysql_host'])
define("mysql_database", default = mysql_config['mysql_database'])
define("mysql_user",     default = mysql_config['mysql_user'])
define("mysql_password", default = mysql_config['mysql_password'])

class TestHandler(BaseHandler, MemberDBMixin):
    def get(self):
        self.render('test.html', locals())

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/signin', SigninHandler), 
            (r'/signup', SignupHandler), 
            (r'/signout', SignoutHandler), 
            (r'/settings', SettingsHandler), 
            (r'/settings/changepass', ChangePasswordHandler), 
            (r'/forget', ForgetPasswordHandler), 
            (r'/reset/([\w\d]{32})', ResetPasswordHandler), 
            (r'/member/([\w\d]*)', MemberHandler), 
            (r'/member/([\w\d]*)/notes', MemberNotesHandler), 
            (r'/lang/(.*)', SetLangeuageHandler), 
            (r'/problem/([\d]*)', ProblemHandler), 
            (r'/problem', ProblemListHandler), 
            (r'/contest/([\d]*)', ContestHandler), 
            (r'/contest', ContestListHandler), 
            (r'/submit', SubmitListHandler), 
            (r'/note/create', CreateNoteHandler), 
            (r'/note/([\d]*)', NoteHandler), 
            (r'/note/([\d]*)/remove', DeleteNoteHandler), 
            (r'/forum', ForumIndexHandler), 
            (r'/forum/go/(.*)', ForumNodeHandler),
            (r'/forum/new/(.*)', TopicCreateHandler), 
            (r'/forum/t/([\d]*)', TopicHandler), 
            (r'/api/problem/get/([\d]*)', ProblemGetAPIHandler),
            (r'/backstage', BackstageHandler), 
            (r'/backstage/problem/add', AddProblemHandler), 
            (r'/backstage/node/create', CreateNodeHandler), 
            (r'/backstage/contest/create', CreateContestHandler), 
            (r'/test', TestHandler), 
        ]
        tornado.web.Application.__init__(self, handlers, **site_config)
        tornado.locale.set_default_locale('zh_CN')
        tornado.locale.load_gettext_translations(self.settings['i18n_path'], "onlinejudge")
        self.markdown = markdown.Markdown(['codehilite(force_linenos=True)', 'tables'], safe_mode=True)
        jinja_env = Environment(loader = FileSystemLoader(self.settings['template_path']))
        jinja_env.filters.update(filters)
        self.jinja2 = jinja_env
        self.db = tornado.database.Connection(
                  host=options.mysql_host, database=options.mysql_database,
                  user=options.mysql_user, password=options.mysql_password)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(8080))
    tornado.ioloop.IOLoop.instance().start()
