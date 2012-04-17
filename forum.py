# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: forum.py
# CREATED: 22:39:44 17/04/2012
# MODIFIED: 04:06:41 18/04/2012

from tornado.web import HTTPError
from tornado.web import authenticated

from judge.db import Node
from judge.db import Topic
from judge.db import ForumDBMixin
from judge.base import BaseHandler

class ViewNodeHandler(BaseHandler, ForumDBMixin):
    def get(self, link):
        node = self.select_node_by_link(link.lower())
        if not node:
            raise HTTPError(404)
        start = self.get_argument("start", default = 0)
        try:
            start = int(start)
        except ValueError:
            start = 0
        topics = self.select_topic_by_node_id(node.id, start = 0)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Forum'), '/forum'))
        breadcrumb.append((node.name, '/go/%s' % node.link))
        title = node.name
        self.render("topic_list.html", locals())

class CreateTopicHandler(BaseHandler, ForumDBMixin):
    @authenticated
    def get(self, link):
        node = self.select_node_by_link(link.lower())
        if not node:
            raise HTTPError(404)
        if self.current_user.admin:
            tid = self.get_argument("tid", default = 0)
            try:
                tid = int(tid)
            except ValueError:
                raise HTTPError(404)
            topic = self.select_topic_by_id(tid)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Forum'), '/forum'))
        breadcrumb.append((node.name, '/go/%s' % node.link))
        breadcrumb.append((self._("Create Topic"), '/new/%s' % node.link))
        title = self._("Create Topic")
        self.render("topic_create.html", locals())
    @authenticated
    def post(self, link):
        node = self.select_node_by_link(link.lower())
        if not node:
            raise HTTPError(404)
        title = self.get_argument("title", default = "")
        content = self.get_argument("content", default = "")
        error = []
        topic = Topic()
        if self.current_user.admin:
            tid = self.get_argument("tid", default = 0)
            try:
                tid = int(tid)
            except ValueError:
                raise HTTPError(404)
            topic.id = tid
        error.extend(self.check_text_value(title, self._("Topic Title"), required = True, max = 255))
        error.extend(self.check_text_value(content, self._("Topic Content"), required = True, min = 5, max = 100000))
        topic.title = self.xhtml_escape(title)
        topic.content = self.xhtml_escape(content)
        if error:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Forum'), '/forum'))
            breadcrumb.append((node.name, '/go/%s' % node.link))
            breadcrumb.append((self._("Create Topic"), '/new/%s' % node.link))
            title = self._("Create Topic")
            self.render("topic_create.html", locals())
            return
        topic.node_id = node.id
        topic.member_id = self.current_user.id
        if topic.id:
            self.update_topic(topic)
        else:
            self.insert_topic(topic)
        self.redirect("/t/%s" % topic.id)

__all__ = ["ViewNodeHandler", "CreateTopicHandler"]
