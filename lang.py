# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from base import BaseHandler
from config import accept_lang

class SetLangeuageHandler(BaseHandler):
    def get(self, lang):
        if lang not in accept_lang.keys():
            raise HTTPError(404)
        self.set_cookie('OJ_LANG', accept_lang[lang])
        if self.request.headers.has_key('Referer'):
            self.redirect(self.request.headers['Referer'])
            return
        self.redirect('/')
