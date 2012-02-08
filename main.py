# -*- coding: utf-8 -*-

import os
import sys

import tornado.web
import tornado.ioloop
#import tornado.database
import tornado.httpserver
from tornado.options import define
from tornado.options import options

from jinja2 import Environment, FileSystemLoader

from base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        self.render('home.html', test = 'a')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
        ]
        settings = {
            'site_title' : u'Online Judge',
            'login_url' : '/signin',
            'template_path' : os.path.join(os.path.dirname(__file__), 'tpl'),
            'static_path' : os.path.join(os.path.dirname(__file__), "static"),
            'xsrf_cookies' : True,
            'cookie_secret' : '32954k1s668c4ad48dad436vd0402905',
        }
        tornado.web.Application.__init__(self, handlers, **settings)
        self.jinja2 = Environment(loader = FileSystemLoader(self.settings['template_path']))
#        self.db = tornado.database.Connection(
#                  host=options.mysql_host, database=options.mysql_database,
#                  user=options.mysql_user, password=options.mysql_password)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(sys.argv[-1]))
    tornado.ioloop.IOLoop.instance().start()
