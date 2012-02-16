# -*- coding: utf-8 -*- 

from tornado.web import HTTPError

from judge import Problem
from judge import NodeDBMixin
from judge import TopicDBMixin
from judge import ProblemDBMixin
from judge.base import BaseHandler

class HomeHandler(BaseHandler, ProblemDBMixin, TopicDBMixin, NodeDBMixin):
    def get(self):
        if self.current_user:
            title = self._("Home")
            breadcrumb = []
            breadcrumb.append((self._("Home"), '/'))
            newest_problem = self.select_problem_by_create(5)
            topics = self.select_topic_by_last_reply(num = 5)
            problem_count = self.count_problem()
            node_count = self.count_node()
            topic_count = self.count_topic()
            self.render('home.html', locals())
        else:
            self.render('index.html', locals())
