# -*- coding: utf-8 -*-

import functools
from tornado.web import HTTPError
from tornado.web import authenticated

from judge import Problem
from judge import ProblemDBMixin
from judge.base import BaseHandler
from judge.utils import escape

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

class AddProblemHandler(BaseHandler, ProblemDBMixin):
    @backstage
    def get(self):
        title = self._("Add Problem")
        pid = self.get_argument("pid", default = 0)
        problem = None
        if pid:
            problem = self.select_problem_by_id(pid)
        self.render("backstage/problem_add.html", locals())
    @backstage
    def post(self):
        probtitle = self.get_argument('probtitle', default = None)
        shortname = self.get_argument('shortname', default = None)
        timelimit = self.get_argument('timelimit', default = 1000)
        memlimit = self.get_argument('memlimit', default = 1000)
        content = self.get_argument('content', default = None)
        inputfmt = self.get_argument('inputfmt', default = '')
        outputfmt = self.get_argument('outputfmt', default = '')
        samplein = self.get_argument('samplein', default = '')
        sampleout = self.get_argument('sampleout', default = '')
        pid = self.get_argument('pid', default = 0)
        print pid
        problem = Problem()
        error = []
        error.extend(self._check_text_value(probtitle, "Title", True))
        error.extend(self._check_text_value(shortname, "Short Name", True))
        error.extend(self._check_text_value(content, "Content", True))
        error.extend(self._check_text_value(inputfmt, "Input Format"))
        error.extend(self._check_text_value(outputfmt, "Output Format"))
        error.extend(self._check_text_value(samplein, "Sample Input"))
        error.extend(self._check_text_value(sampleout, "Sample Output"))
        problem.id = int(pid)
        problem.title = self.xhtml_escape(probtitle)
        problem.shortname = self.xhtml_escape(shortname)
        problem.timelimit = self.xhtml_escape(timelimit)
        problem.memlimit = self.xhtml_escape(memlimit)
        problem.content = self.xhtml_escape(content)
        problem.inputfmt = self.xhtml_escape(inputfmt)
        problem.outputfmt = self.xhtml_escape(outputfmt)
        problem.samplein = self.xhtml_escape(samplein)
        problem.sampleout = self.xhtml_escape(sampleout)
        if error:
            title = self._("Add Problem")
            self.render("backstage/problem_add.html", locals())
            return
        problem.content_html = self.markdown.convert(content)
        if problem.id:
            self.update_problem(problem)
        else:
            self.insert_problem(problem)
        self.redirect('/problem/%d' % problem.id)
