# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/base/__init__.py
# CREATED: 01:49:33 08/03/2012
# MODIFIED: 01:54:14 08/03/2012
# DESCRIPTION: Base handler

import tornado.web
import tornado.escape

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
    def render(self):
        '''Rewrite render func for use jinja2'''
        pass
    def write_error(self):
        '''Rewrite write_error for custom error page'''
        pass
