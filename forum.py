# -*- coding: utf-8 -*-

from tornado.web import authenticated

from judge import Reply
from judge import Topic
from judge import NodeDBMixin
from judge import ReplyDBMixin
from judge import TopicDBMixin
from judge.base import BaseHandler

class ForumIndexHandler(BaseHandler, TopicDBMixin, NodeDBMixin):
    def get(self):
        topics = self.select_topic_by_last_reply()
        nodes = self.select_nodes()
        title = self._("Forum")
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Forum'), '/forum'))
        self.render("forum.html", locals())

class ForumNodeHandler(BaseHandler, NodeDBMixin, TopicDBMixin):
    def get(self, link):
        node = self.select_node_by_link(link)
        if node:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Forum'), '/forum'))
            breadcrumb.append((node.name, '/forum/go/%s' % node.link))
            topics = self.select_topic_by_node(node.id)
            title = node.name
            self.render("node.html", locals())
        else:
            raise HTTPError(404)

class TopicCreateHandler(BaseHandler, NodeDBMixin, TopicDBMixin):
    @authenticated
    def get(self, link):
        node = self.select_node_by_link(link)
        tid = self.get_argument("tid", default = 0)
        if node:
            topic = None
            if tid:
                topic = self.select_topic_by_id(tid)
                if not topic:
                    raise HTTPError(404)
                if topic and not self.current_user.admin:
                    raise HTTPError(404)
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Forum'), '/forum'))
            breadcrumb.append((node.name, '/forum/go/%s' % node.link))
            breadcrumb.append((self._('Create Topic'), '/forum/new/%s' % node.link))
            title = self._("Create Topic")
            if topic:
                title = self._("Edit Topic")
            self.render("topic_create.html", locals())
        else:
            raise HTTPError(404)
    @authenticated
    def post(self, link):
        node = self.select_node_by_link(link)
        tid = self.get_argument("tid", default = 0)
        if node:
            if tid:
                topic = self.select_topic_by_id(tid)
                if not topic:
                    raise HTTPError(404)
                if topic and not self.current_user.admin:
                    raise HTTPError(404)
            title = self.get_argument("title", default = None)
            content = self.get_argument("content", default = None)
            topic = Topic()
            error = []
            error.extend(self._check_text_value(title, "Title", True, max = 200))
            error.extend(self._check_text_value(content, "Content", True, max = 4000))
            topic.title = self.xhtml_escape(title)
            topic.content = self.xhtml_escape(content)
            topic.id = tid
            if error:
                breadcrumb = []
                breadcrumb.append((self._('Home'), '/'))
                breadcrumb.append((self._('Forum'), '/forum'))
                breadcrumb.append((node.name, '/forum/go/%s' % node.link))
                breadcrumb.append((self._('Create Topic'), '/forum/new/%s' % node.link))
                title = self._("Create Topic")
                if topic:
                    title = self._("Edit Topic")
                self.render("topic_create.html", locals())
                return
            topic.node_id = node.id
            topic.member_id = self.current_user.id
            if topic.id:
                self.update_topic(topic)
            else:
                self.insert_topic(topic)
            self.redirect("/forum/t/%d" % topic.id)
        else:
            raise HTTPError(404)

class TopicHandler(BaseHandler, TopicDBMixin, NodeDBMixin, ReplyDBMixin):
    def get(self, tid):
        try:
            tid = int(tid)
        except ValueError:
            raise HTTPError(404)
        topic = self.select_topic_by_id(tid)
        node = self.select_node_by_id(topic.node_id)
        replies = self.select_reply_by_topic_id(tid)
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self._('Forum'), '/forum'))
        breadcrumb.append((node.name, '/forum/go/%s' % node.link))
        breadcrumb.append((topic.title, '/forum/t/%s' % topic.id))
        title = topic.title
        self.render("topic.html", locals())
    @authenticated
    def post(self, tid):
        try:
            tid = int(tid)
        except ValueError:
            raise HTTPError(404)
        content = self.get_argument('content', default = None)
        error = []
        reply = Reply()
        error.extend(self._check_text_value(content, self._('Reply'), True, max = 3000))
        reply.content = self.xhtml_escape(content)
        if error:
            topic = self.select_topic_by_id(tid)
            node = self.select_node_by_id(topic.node_id)
            replies = self.select_reply_by_topic_id(tid)
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self._('Forum'), '/forum'))
            breadcrumb.append((node.name, '/forum/go/%s' % node.link))
            breadcrumb.append((topic.title, '/forum/t/%s' % topic.id))
            title = topic.title
            self.render("topic.html", locals())
            return
        reply.member_id = self.current_user.id
        reply.topic_id = tid
        self.insert_reply(reply)
        self.update_topic_last_reply(tid)
        self.redirect('/forum/t/%d' % tid)
