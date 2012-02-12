# -*- coding: utf-8 -*-

import functools
from tornado.web import HTTPError
from tornado.web import authenticated

from base import BaseHandler
from utils import escape

def backstage(method):
    """Decorate methods with this to require that user be NOT logged in"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            if self.current_user['admin']:
                return method(self, *args, **kwargs)
        raise HTTPError(404)
    return wrapper


class BackstageHandler(BaseHandler):
    @backstage
    def get(self):
        title = self._("Backstage")
        self.render("backstage/index.html", locals())

class AddProblemHandler(BaseHandler):
    def _check_value(self, text, title, required = False):
        error = []
        if not text:
            if required:
                error.append(self._('%s is Required!' % title))
        return error
    @backstage
    def get(self):
        title = self._("Add Problem")
        self.render("backstage/problem_add.html", locals())
    @backstage
    def post(self):
        probtitle = self.get_argument('probtitle', default = None)
        shortname = self.get_argument('shortname', default = None)
        content = self.get_argument('content', default = None)
        inputfmt = self.get_argument('inputfmt', default = None)
        outputfmt = self.get_argument('outputfmt', default = None)
        samplein = self.get_argument('samplein', default = None)
        sampleout = self.get_argument('sampleout', default = None)
        error = []
        error.extend(self._check_value(probtitle, "Title", True))
        error.extend(self._check_value(shortname, "Short Name", True))
        error.extend(self._check_value(content, "Content", True))
        error.extend(self._check_value(inputfmt, "Input Format"))
        error.extend(self._check_value(outputfmt, "Output Format"))
        error.extend(self._check_value(samplein, "Sample Input"))
        error.extend(self._check_value(sampleout, "Sample Output"))
        probtitle = self.xhtml_escape(probtitle)
        shortname = self.xhtml_escape(shortname)
        content = self.xhtml_escape(content)
        inputfmt = self.xhtml_escape(inputfmt)
        outputfmt = self.xhtml_escape(outputfmt)
        samplein = self.xhtml_escape(samplein)
        sampleout = self.xhtml_escape(sampleout)
        if error:
            title = self._("Add Problem")
            self.render("backstage/problem_add.html", locals())
            return
        probtitle = escape(probtitle)
        md = escape(self.markdown.convert(content))
        shortname = escape(shortname)
        content = escape(content)
        inputfmt = escape(inputfmt)
        outputfmt = escape(outputfmt)
        samplein = escape(samplein)
        sampleout = escape(sampleout)
        sql = """INSERT INTO `problem` (`title`, `shortname`, `content`, `content_html`, \
                 `inputfmt`, `outputfmt`, `samplein`, `sampleout`, `create`) \
                 VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', UTC_TIMESTAMP())""" \
                 % (probtitle, shortname, content, md, inputfmt, outputfmt, samplein, sampleout)
        pid = self.db.execute(sql)
        self.redirect('/problem/%d' % pid)
