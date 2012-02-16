# -*- coding: utf-8 -*-

import uuid
import binascii
from judge.utils import escape

class BaseDBObject(object):
    def __repr__(self):
        result = ", \n".join(["'%s': '%s'" % (attr, getattr(self, attr)) for attr in dir(self) if attr[0] != '_' and not callable(getattr(self, attr)) ])
        return "<{%s}>" % result
    def __getitem__(self, name):
        return getattr(self, name)
    def _init_row(self, row):
        if row:
            keys = row.keys()
            for key in keys:
                setattr(self, key, row[key])
    def e(self, name):
        if self[name]:
            return escape(self[name])
        return ""

class Member(BaseDBObject):
    username = ""
    username_lower = ""
    password = ""
    email = ""
    website = ""
    tagline = ""
    bio = ""
    create = None
    admin = 0
    lang = 1

class MemberDBMixin(object):
    def _new_member_by_row(self, row):
        member = Member()
        member._init_row(row)
        return member
    def select_member_by_id(self, mid):
        sql = """SELECT * FROM `member` WHERE `id` = '%d'""" % int(mid)
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_username(self, username):
        sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' LIMIT 1""" % (escape(username.lower()))
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_usr_pwd(self, usr, pwd):
        sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' AND `password` = '%s' LIMIT 1""" % (escape(usr.lower()), escape(pwd))
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_email(self, email):
        sql = """SELECT * FROM `member` WHERE `email` = '%s' LIMIT 1""" % (escape(email.lower()))
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def insert_member(self, member):
        member.username_lower = member.username.lower()
        member.id = self.db.execute("""INSERT INTO `member` (`username`, `username_lower`, `password`, `email`, `gravatar_link`, `create`, `website`, `tagline`, `bio`, `admin`, `lang`)
                                       VALUES (%s, %s, %s, %s, %s, UTC_TIMESTAMP(), %s, %s, %s, %s, %s)""", \
                                    member.username, member.username_lower, member.password, member.email, \
                                    member.gravatar_link, member.website, member.tagline, member.bio, \
                                    member.admin, member.lang)
    def update_member(self, member):
        self.db.execute("""UPDATE `member`
                           SET `password` = %s, 
                               `email` = %s, 
                               `gravatar_link` = %s, 
                               `website` = %s, 
                               `tagline` = %s, 
                               `bio` = %s, 
                               `admin` = %s, 
                               `lang` = %s
                           WHERE `id` = %s""", member.password, member.email, member.gravatar_link, \
                                               member.website, member.tagline, member.bio, \
                                               member.admin, member.lang, member.id)

class Auth(BaseDBObject):
    uid = 0
    secret = ""
    create = None

class AuthDBMixin(object):
    def _new_auth_by_row(self, row):
        if row:
            auth = Auth()
            auth._init_row(row)
            return [auth]
        return []
    def select_auth_by_uid(self, uid):
        sql = """SELECT * FROM `auth` WHERE `uid` = '%d'""" % int(uid)
        rows = self.db.query(sql)
        result = []
        for row in rows:
            result.extend(self._new_auth_by_row(row))
        return result
    def select_auth_by_secret(self, secret):
        sql = """SELECT * FROM `auth` WHERE `secret` = '%s' LIMIT 1""" % escape(secret)
        result = self._new_auth_by_row(self.db.get(sql))
        if result:
            return result[0]
        return None
    def create_auth(self, uid):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `auth` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                 % (int(uid), random)
        self.db.execute(sql)
        auth = Auth()
        auth.uid = uid
        auth.secret = random
        return auth
    def delete_auth_by_uid(self, uid):
        sql = """DELETE FROM `auth` WHERE `uid` = '%d'""" % int(uid)
        self.db.execute(sql)
    def delete_auth_by_secret(self, secret):
        sql = """DELETE FROM `auth` WHERE `secret` = '%s'""" % (escape(secret))
        self.db.execute(sql)

class ResetMail(BaseDBObject):
    uid = 0
    secret = ""
    create = None

class ResetMailDBMixin(object):
    def _new_reset_mail_by_row(self, row):
        if row:
            auth = Auth()
            auth._init_row(row)
            return [auth]
        return []
    def select_reset_mail_by_uid(self, uid):
        sql = """SELECT * FROM `reset_mail` WHERE `uid` = '%d'""" % int(uid)
        result = []
        rows = self.db.query(sql)
        for row in rows:
            result.extend(self._new_reset_mail_by_row(row))
        return result
    def select_reset_mail_last_by_uid(self, uid):
        sql = """SELECT * FROM `reset_mail` WHERE `uid` = '%d' ORDER BY `create` DESC LIMIT 1""" % int(uid)
        auth = self._new_reset_mail_by_row(self.db.get(sql))
        if auth:
            return auth[0]
        return None
    def select_reset_mail_by_secret(self, secret):
        sql = """SELECT * FROM `reset_mail` WHERE `secret` = '%s' LIMIT 1""" % escape(secret)
        result = self._new_reset_mail_by_row(self.db.get(sql))
        if result:
            return result[0]
        return None
    def create_reset_mail(self, uid):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `reset_mail` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                % (int(uid), random)
        self.db.execute(sql)
        reset_mail = ResetMail()
        reset_mail.uid = uid
        reset_mail.secret = random
        return reset_mail
    def delete_reset_mail_by_secret(self, secret):
        sql = """DELETE FROM `reset_mail` WHERE `secret` = '%s'""" % (escape(secret))
        self.db.execute(sql)

class Problem(BaseDBObject):
    id = 0
    title = ""
    shortname = ""
    content = ""
    content_html = ""
    inputfmt = ""
    outputfmt = ""
    samplein = ""
    sampleout = ""
    timelimit = 1000
    memlimit = 128
    tags = ""
    create = None

class ProblemDBMixin(object):
    def _new_problem_by_row(self, row):
        if row:
            problem = Problem()
            problem._init_row(row)
            return [problem]
        return []
    def insert_problem(self, problem):
        pid = self.db.execute("""INSERT INTO `problem` (`title`, `shortname`, `content`, `content_html`, \
                                 `inputfmt`, `outputfmt`, `samplein`, `sampleout`, `timelimit`, `memlimit`, `create`) \
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())""" \
                              , problem.title, problem.shortname, problem.content, problem.content_html, \
                              problem.inputfmt, problem.outputfmt, problem.samplein, problem.sampleout, \
                              int(problem.timelimit), int(problem.memlimit))
        problem.id = pid
    def update_problem(self, problem):
        self.db.execute("""UPDATE `problem` SET `title` = %s, \
                                                `shortname` = %s, \
                                                `content` = %s, \
                                                `content_html` = %s, \
                                                `inputfmt` = %s, \
                                                `outputfmt` = %s, \
                                                `samplein` = %s, \
                                                `sampleout` = %s, \
                                                `timelimit` = %s, \
                                                `memlimit` = %s \
                                            WHERE `id` = %s""", \
                           problem.title, problem.shortname, problem.content, problem.content_html, \
                           problem.inputfmt, problem.outputfmt, problem.samplein, problem.sampleout, \
                           int(problem.timelimit), int(problem.memlimit), problem.id)
    def count_problem(self):
        count = self.db.get("""SELECT COUNT(*) FROM `problem`""")
        return count["COUNT(*)"]
    def select_problem_by_id(self, pid):
        sql = """SELECT * FROM `problem` WHERE `id` = '%d' LIMIT 1""" % int(pid)
        query = self.db.get(sql)
        if query:
            problem = Problem()
            problem._init_row(query)
            return problem
        return None
    def select_problem_order_by_id(self, nums, start = 0):
        sql = """SELECT * FROM `problem` LIMIT %d, %d""" % (start, nums)
        result = []
        rows = self.db.query(sql)
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result
    def select_problem_by_create(self, nums):
        sql = """SELECT * FROM `problem` ORDER BY `id` DESC LIMIT %d""" % nums
        result = []
        rows = self.db.query(sql)
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result

class Note(BaseDBObject):
    id = 0
    title = ""
    content = ""
    member_id = 0
    create = ""
    link_problem = ""

class NoteDBMixin(object):
    def _new_problem_by_row(self, row):
        if row:
            note = Note()
            note._init_row(row)
            note.link_problem = note.link_problem.split(", ") if note.link_problem else None
            return [note]
        return []
    def select_note_by_id(self, nid):
        sql = """SELECT * FROM `note` WHERE `id` = '%d' LIMIT 1""" % int(nid)
        query = self.db.get(sql)
        if query:
            note = Note()
            note._init_row(query)
            note.link_problem = note.link_problem.split(", ") if note.link_problem else None
            return note
        return None
    def select_note_by_mid(self, mid, start = 0, count = 10):
        sql = """SELECT * FROM `note` WHERE `member_id` = '%d' ORDER BY `id` DESC LIMIT %d, %d""" \
                 % (int(mid), int(start), int(count))
        query = self.db.query(sql)
        result = []
        if query:
            for row in query:
                result.extend(self._new_problem_by_row(row))
        return result
    def insert_note(self, note):
        nid = self.db.execute("""INSERT INTO `note` (`title`, `content`, `member_id`, `create`, `link_problem`) \
                                 VALUES (%s, %s, %s, UTC_TIMESTAMP(), %s)""" \
                                 , note.title, note.content, int(note.member_id), ", ".join(note.link_problem))
        note.id = nid
    def update_note(self, note):
        sql = """UPDATE `note` SET `title` = '%s', \
                                   `content` = '%s' \
                               WHERE `id` = '%d'""" \
                 % (note.title, note.content, note.id)
        self.db.execute(sql)
    def delete_note_by_nid(self, nid):
        sql = """DELETE FROM `note` WHERE `id` = '%d'""" % int(nid)
        self.db.execute(sql)

class Node(BaseDBObject):
    id = 0
    name = ""
    description = ""
    link = ""

class NodeDBMixin(object):
    def _new_topic_by_row(self, row):
        if row:
            node = Node()
            node._init_row(row)
            return [node]
        return []
    def count_node(self):
        count = self.db.get("""SELECT COUNT(*) FROM `node`""")
        return count["COUNT(*)"]
    def select_nodes(self, start = 0, num = 100):
        rows = self.db.query("""SELECT * FROM `node` LIMIT %s, %s""", start, num)
        result = []
        for row in rows:
            result.extend(self._new_topic_by_row(row))
        return result
    def select_node_by_link(self, link):
        result = self.db.get("""SELECT * FROM `node` WHERE `link` = %s LIMIT 1""", link)
        if result:
            node = Node()
            node._init_row(result)
            return node
        return None
    def select_node_by_id(self, nid):
        result = self.db.get("""SELECT * FROM `node` WHERE `id` = %s LIMIT 1""", nid)
        node = None
        if result:
            node = Node()
            node._init_row(result)
            return node
        return None
    def update_node(self, node):
        self.db.execute("""UPDATE `node` SET `name` = %s, \
                                             `description` = %s, \
                                             `link` = %s \
                                         WHERE `id` = %s""", \
                        node.name, node.description, node.link, node.id)
    def insert_node(self, node):
        node.id = self.db.execute("""INSERT INTO `node` (`name`, `description`, `link`) \
                                     VALUES (%s, %s, %s)""", \
                                     node.name, node.description, node.link)
    def delete_node(self, nid):
        self.db.execute("""DELETE FROM `node` WHERE `id` = %s""", nid)

class Topic(BaseDBObject):
    id = 0
    title = ""
    content = ""
    node_id = 0
    member_id = 0
    create = None
    last_reply = None

class TopicDBMixin(object):
    def _new_topic_by_row(self, row):
        if row:
            topic = Topic()
            topic._init_row(row)
            return [topic]
        return []
    def count_topic(self):
        count = self.db.get("""SELECT COUNT(*) FROM `topic`""")
        return count["COUNT(*)"]
    def select_topic_by_node(self, node, start = 0, num = 15):
        rows = self.db.query("""SELECT `topic`. * , `member`.`username`, `member`.`gravatar_link` , `node`.`name` , `node`.`link`
                                FROM `topic`
                                LEFT JOIN `member` ON `topic`.`member_id` = `member`.`id`
                                LEFT JOIN `node` ON `topic`.`node_id` = `node`.`id`
                                WHERE `node_id` = %s
                                ORDER BY `create` DESC
                                LIMIT %s, %s""", node, start, num)
        result = []
        for row in rows:
            result.extend(self._new_topic_by_row(row))
        return result
    def select_topic_by_id(self, topic_id):
        result = self.db.get("""SELECT `topic`.*, `member`.`username`, `member`.`gravatar_link`, `member`.`tagline`
                                FROM `topic` 
                                LEFT JOIN `member` ON `topic`.`member_id` = `member`.`id`
                                WHERE `topic`.`id` = %s
                                LIMIT 1""", topic_id)
        topic = Topic()
        if result:
            topic._init_row(result)
            return topic
        return None
    def select_topic_by_last_reply(self, start = 0, num = 20):
        rows = self.db.query("""SELECT `topic`.*, `member`.`username`, `member`.`gravatar_link`, `node`.`name`
                                FROM `topic`
                                LEFT JOIN `member` ON `topic`.`member_id` = `member`.`id`
                                LEFT JOIN `node` ON `topic`.`node_id` = `node`.`id`
                                ORDER BY `topic`.`last_reply` DESC LIMIT %s, %s""", start, num)
        result = []
        for row in rows:
            result.extend(self._new_topic_by_row(row))
        return result
    def update_topic(self, topic):
        self.db.execute("""UPDATE `topic` SET `title` = %s, \
                                              `content` = %s, \
                                          WHERE `id` = %s""", \
                           topic.title, topic.content, topic.id)
    def update_topic_last_reply(self, tid):
        self.db.execute("""UPDATE `topic` SET `last_reply` = UTC_TIMESTAMP() WHERE `id` = %s""", tid)
    def insert_topic(self, topic):
        topic.id = self.db.execute("""INSERT INTO `topic` (`title`, `content`, `node_id`, `member_id`, `create`, `last_reply`) \
                                                   VALUES (%s, %s, %s, %s, UTC_TIMESTAMP(), UTC_TIMESTAMP())""", \
                                                   topic.title, topic.content, topic.node_id, topic.member_id)
    def delete_topic(self, tid):
        self.db.execute("""DELETE FROM `topic` WHERE `id` = %s""", tid)

class Reply(BaseDBObject):
    id = ""
    content = ""
    member_id = ""
    topic_id = ""
    create = None

class ReplyDBMixin(object):
    def _new_reply_by_row(self, row):
        if row:
            reply = Reply()
            reply._init_row(row)
            return [reply]
        return []
    def select_reply_by_topic_id(self, tid, start = 0, count = 100):
        rows = self.db.query("""SELECT `reply`.*, `member`.`gravatar_link`, `member`.`username`
                                FROM `reply`
                                LEFT JOIN `member` ON `reply`.`member_id` = `member`.`id`
                                WHERE `reply`.`topic_id` = %s LIMIT %s,%s""", tid, start, count)
        result = []
        for row in rows:
            result.extend(self._new_reply_by_row(row))
        return result
    def insert_reply(self, reply):
        self.db.execute("""INSERT INTO `reply` (`content`, `member_id`, `topic_id`, `create`)
                                  VALUES (%s, %s, %s, UTC_TIMESTAMP())""", reply.content, reply.member_id, reply.topic_id)

