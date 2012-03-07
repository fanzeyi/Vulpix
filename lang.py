# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: lang.py
# CREATED: 02:44:51 08/03/2012
# MODIFIED: 02:54:55 08/03/2012
# DESCRIPTION: Set language handler

from tornado.web import HTTPError

from config import accept_lang

from judge.base import BaseHandler

class SetLanguageHandler(BaseHandler):
    ''' `/lang/(.*)` - set language. '''
    def get(self, lang):
        if lang not in accept_lang.keys():
            raise HTTPError(404)
        self.set_cookie('LANG', accept_lang[lang])
        if self.request.headers.has_key('Referer'):
            self.redirect(self.request.headers['Referer'])
            return
        self.redirect('/')

__all__ = ["SetLanguageHandler"]
