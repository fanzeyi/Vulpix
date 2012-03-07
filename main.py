# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: main.py
# CREATED: 01:37:19 08/03/2012
# MODIFIED: 01:47:54 08/03/2012
# DESCRIPTION: Main Server File,  run as `python2 main.py [port_num]`

import re
import sys
import httplib
from jinja2 import Environment, FileSystemLoader

httplib.responses[418] = "I'm a teapot" # hack for HTTP 418 :D

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.database
import tornado.httpserver
from tornado.options import define
from tornado.options import options

from judge.filters import filters

from config import site_config
from config import mysql_config
from handlers import handlers

tornado.options.parse_command_line()

# Set MySQL
define("mysql_host",     default = mysql_config['mysql_host'])
define("mysql_database", default = mysql_config['mysql_database'])
define("mysql_user",     default = mysql_config['mysql_user'])
define("mysql_password", default = mysql_config['mysql_password'])

class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, handlers, **site_config)
        tornado.locale.load_gettext_translations(self.settings['i18n_path'], "vulpix")
        # Set Jinja2
        jinja_env = Environment(loader = FileSystemLoader(self.settings['template_path']))
        jinja_env.filters.update(filters)
        self.jinja2 = jinja_env
        self.db = tornado.database.Connection(
                  host=options.mysql_host, database=options.mysql_database,
                  user=options.mysql_user, password=options.mysql_password)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(sys.argv[-1]))
    tornado.ioloop.IOLoop.instance().start()
