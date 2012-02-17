# -*- coding: utf-8 -*-

import functools
from tornado.web import HTTPError
from tornado.web import authenticated

from judge import Node
from judge import Problem
from judge import NodeDBMixin
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
        testpoint = self.get_argument('testpoint', default = None)
        content = self.get_argument('content', default = None)
        inputfmt = self.get_argument('inputfmt', default = '')
        outputfmt = self.get_argument('outputfmt', default = '')
        samplein = self.get_argument('samplein', default = '')
        sampleout = self.get_argument('sampleout', default = '')
        pid = self.get_argument('pid', default = 0)
        print pid
        problem = Problem()
        error = []
        error.extend(self._check_text_value(probtitle, self._("Title"), True))
        error.extend(self._check_text_value(shortname, self._("Short Name"), True))
        error.extend(self._check_text_value(content, self._("Content"), True))
        error.extend(self._check_text_value(testpoint, self._("Test Point"), True))
        error.extend(self._check_text_value(inputfmt, self._("Input Format")))
        error.extend(self._check_text_value(outputfmt, self._("Output Format")))
        error.extend(self._check_text_value(samplein, self._("Sample Input")))
        error.extend(self._check_text_value(sampleout, self._("Sample Output")))
        problem.id = int(pid)
        problem.title = self.xhtml_escape(probtitle)
        problem.shortname = self.xhtml_escape(shortname)
        problem.timelimit = self.xhtml_escape(timelimit)
        problem.memlimit = self.xhtml_escape(memlimit)
        problem.testpoint = self.xhtml_escape(testpoint)
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

class CreateNodeHandler(BaseHandler, NodeDBMixin):
    @backstage
    def get(self):
        title = self._("Add Node")
        nid = self.get_argument('nid', default = 0)
        node = None
        if nid:
            node = self.select_node_by_id(nid)
            title = self._("Edit Node")
        self.render("backstage/node_create.html", locals())
    @backstage
    def post(self):
        nid = self.get_argument("nid", default = 0)
        name = self.get_argument("name", default = None)
        description = self.get_argument("description", default = None)
        link = self.get_argument("link", default = None)
        node = Node()
        error = []
        error.extend(self._check_text_value(name, self._("Node Name"), True, max = 50))
        error.extend(self._check_text_value(description, self._("Node Description"), True, max = 2000))
        error.extend(self._check_text_value(link, self._("Node Link"), True, max = 30))
        node.id = int(nid)
        node.name = self.xhtml_escape(name)
        node.description = self.xhtml_escape(description)
        node.link = self.xhtml_escape(link)
        if error:
            title = self._("Add Node")
            if node.id:
                title = self._("Edit Node")
            self.render("backstage/node_create.html", locals())
            return
        if node.id:
            self.update_node(node)
        else:
            self.insert_node(node)
        self.redirect("/forum/go/%s" % node.link)
