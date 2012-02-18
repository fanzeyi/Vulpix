# -*- coding: utf-8 -*- 

import os
import time
import base64
import requests

from tornado.web import HTTPError
from tornado.web import authenticated

from judge import Submit
from judge import Problem
from judge import SubmitDBMixin
from judge import ProblemDBMixin
from judge import RelatedProblemDBMixin
from judge.base import BaseHandler

class ProblemHandler(BaseHandler, ProblemDBMixin, RelatedProblemDBMixin, SubmitDBMixin):
    @staticmethod
    def _array_encode(arr):
        sa = []
        for k in arr:
            sa.append(base64.b64encode(str(k)))
            sa.append(base64.b64encode(str(arr[k])))
        s = "?".join(sa)
        return base64.b64encode(s)
    @staticmethod
    def _array_decode(s):
        arr = {}
        s = base64.b64decode(s)
        sa = s.split("?")
        for k, v in zip(sa[::2], sa[1::2]):
            arr[base64.b64decode(k)] = base64.b64decode(v)
        return arr
    @staticmethod
    def _set_status(submit, status):
        if submit.status == None:
            submit.status = status
    def _send_request(self, data):
        self.require_setting("judger")
        req = requests.post(self.settings['judger'], { 'query' : self._array_encode(data)})
        return self._array_decode(req.content[8:])
    def get(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if problem:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Problem'), '/problem'))
            breadcrumb.append((problem.title, '/problem/%d' % problem.id))
            title = self._("Problem") + u" › " + problem.title
            related_note = self.select_related_problem_by_pid(problem.id)
            self.render("problem.html", locals())
        else:
            raise HTTPError(404)
    @authenticated
    def post(self, pid):
        try:
            pid = int(pid)
        except ValueError:
            raise HTTPError(404)
        problem = self.select_problem_by_id(pid)
        if not problem:
            raise HTTPError(404)
        lang = self.get_argument("lang", default = 0)
        error = []
        try:
            codefile = self.request.files['codefile'][0]
        except KeyError:
            error.append(self._('Please Choose Your Code File'))
        else:
            filename, fileext = os.path.splitext(codefile.filename)
            if fileext not in ['.c', '.cc', '.cpp', '.cxx', '.pas']:
                error.append(self._('File Type Error!'))
            else:
                if lang not in ['1', '2', '3']:
                    error.append(self._('Error Code Language Select'))
                else:
                    # query grader status
                    result = self._send_request({'action' : 'state'})
                    if result['state'] != 'free':
                        error.append(self._("No Free Judger!"))
        if error:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Problem'), '/problem'))
            breadcrumb.append((problem.title, '/problem/%d' % problem.id))
            title = self._("Problem") + u" › " + problem.title
            related_note = self.select_related_problem_by_pid(problem.id)
            self.render("problem.html", locals())
            return
        code_dir = os.path.join(self.settings['code_save_path'], str(self.current_user.id))
        if not os.path.exists(code_dir):
            os.mkdir(code_dir)
        timestamp = int(time.time())
        code_file_path = os.path.join(code_dir, '%s%s.%d' % (problem.shortname, fileext, timestamp))
        with open(code_file_path, 'w') as codefp:
            codefp.write(codefile.body)
        submit = Submit()
        submit.member_id = self.current_user.id
        submit.problem_id = problem.id
        submit.lang = lang
        submit.user_agent = self.request.headers['User-Agent']
        submit.ip = self.request.remote_ip
        submit.timestamp = timestamp
        self.insert_submit(submit)
        self.redirect("/submit")
        self._send_request({'action' : 'lock'})
        result = self._send_request({'action' : 'compile', \
                                     'pname' : problem.shortname, \
                                     'language' : int(lang) - 1, \
                                     'uid'  : self.current_user.id, \
                                     'code'  : codefile.body, \
                                     'src'  : '%s%s' % (problem.shortname, fileext)})
        if result['compilesucc'] != '1':
            # Compile error
            submit.status = 6
            submit.msg = result['msg']
            self.update_submit(submit)
            self._send_request({'action' : 'unlock', 'uid' : submit.member_id})
            return
        submit.status = None
        for i in range(problem.testpoint):
            result = self._send_request({'action' : 'grade', \
                                         'pname'  : problem.shortname, \
                                         'memorylimit' : problem.memlimit, \
                                         'plugin' : 1, \
                                         'grade' : i + 1, 
                                         'timelimit' : problem.timelimit, \
                                         'uid' : self.current_user.id})
            submit.costtime += int(float(result['rtime']))
            submit.costmemory += int(float(result['memory']))
            if result['timeout']:
                self._set_status(submit, 3)
                submit.testpoint = submit.testpoint + "T"
            elif result['memoryout']:
                self._set_status(submit, 4)
                submit.testpoint = submit.testpoint + "M"
            elif result['runerr']:
                self._set_status(submit, 5)
                submit.testpoint = submit.testpoint + "E"
            elif result['noreport']:
                self._set_status(submit, 2)
                submit.testpoint = submit.testpoint + "R"
            elif str(result['score']) != '0':
                self._set_status(submit, 2)
                submit.testpoint = submit.testpoint + "W"
            else:
                submit.score += int(float(result['score']))
                submit.testpoint = submit.testpoint + "A"
        self._set_status(submit, 1)
        submit.score = submit.score * 10
        self.update_submit(submit)
        self._send_request({'action' : 'unlock', 'uid' : submit.member_id})

class ProblemListHandler(BaseHandler, ProblemDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        problems = self.select_problem_order_by_id(20, start)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Problem'), '/problem'))
        title = self._("Problem")
        self.render("problem_list.html", locals())

class SubmitListHandler(BaseHandler, SubmitDBMixin):
    def get(self):
        start = self.get_argument("start", default = 0)
        submits = self.select_submit_desc(start = start)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Submit'), '/submit'))
        title = self._("Submit")
        self.render("submit.html", locals())
