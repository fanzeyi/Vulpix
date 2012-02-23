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
    id = 0
    username = ""
    username_lower = ""
    password = ""
    email = ""
    website = ""
    tagline = ""
    bio = ""
    gravatar_link = ""
    create = None
    admin = 0
    lang = 1

class MemberDBMixin(object):
    def _new_member_by_row(self, row):
        member = Member()
        member._init_row(row)
        return member
    def select_member_by_id(self, mid):
        result = self.db.get("""SELECT * FROM `member` WHERE `id` = %s""", int(mid))
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_username(self, username):
        result = self.db.get("""SELECT * FROM `member` WHERE `username_lower` = %s LIMIT 1""", username.lower())
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_usr_pwd(self, usr, pwd):
        result = self.db.get("""SELECT * FROM `member` WHERE `username_lower` = %s AND `password` = %s LIMIT 1""", usr.lower(), pwd)
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_email(self, email):
        result = self.db.get("""SELECT * FROM `member` WHERE `email` = %s LIMIT 1""", email.lower())
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
        rows = self.db.query("""SELECT * FROM `auth` WHERE `uid` = %s""", int(uid))
        result = []
        for row in rows:
            result.extend(self._new_auth_by_row(row))
        return result
    def select_auth_by_secret(self, secret):
        result = self.db.get("""SELECT * FROM `auth` WHERE `secret` = %s LIMIT 1""", secret)
        if result:
            auth = Auth()
            auth._init_row(result)
            return auth
        return None
    def create_auth(self, uid):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        self.db.execute("""INSERT INTO `auth` (`uid`, `secret`, `create`) VALUES (%s, %s, UTC_TIMESTAMP())""" \
                        , int(uid), random)
        auth = Auth()
        auth.uid = uid
        auth.secret = random
        return auth
    def delete_auth_by_uid(self, uid):
        self.db.execute("""DELETE FROM `auth` WHERE `uid` = %s""", int(uid))
    def delete_auth_by_secret(self, secret):
        self.db.execute("""DELETE FROM `auth` WHERE `secret` = %s""", secret)

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
        result = []
        rows = self.db.query("""SELECT * FROM `reset_mail` WHERE `uid` = %s""", int(uid))
        for row in rows:
            result.extend(self._new_reset_mail_by_row(row))
        return result
    def select_reset_mail_last_by_uid(self, uid):
        result = self.db.get("""SELECT * FROM `reset_mail` WHERE `uid` = %s ORDER BY `create` DESC LIMIT 1""", int(uid))
        if result:
            reset_mail = ResetMail()
            reset_mail._init_row(result)
            return reset_mail
        return None
    def select_reset_mail_by_secret(self, secret):
        result = self.db.get("""SELECT * FROM `reset_mail` WHERE `secret` = %s LIMIT 1""", secret)
        if result:
            reset_mail = ResetMail()
            reset_mail._init_row(result)
            return reset_mail
        return None
    def create_reset_mail(self, uid):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        self.db.execute("""INSERT INTO `reset_mail` (`uid`, `secret`, `create`) VALUES (%s, %s, UTC_TIMESTAMP())""" \
                        , int(uid), random)
        reset_mail = ResetMail()
        reset_mail.uid = uid
        reset_mail.secret = random
        return reset_mail
    def delete_reset_mail_by_secret(self, secret):
        self.db.execute("""DELETE FROM `reset_mail` WHERE `secret` = %s""", secret)

class Problem(BaseDBObject):
    id = 0
    title = ""
    shortname = ""
    content = ""
    timelimit = 1000
    memlimit = 128
    testpointnum = 0
    invisible = 0
    tags = ""
    create = None

class ProblemTag(BaseDBObject):
    problem_id = 0
    tagname = ""

class ProblemDBMixin(object):
    def _new_problem_by_row(self, row):
        if row:
            problem = Problem()
            problem._init_row(row)
            return [problem]
        return []
    def insert_problem_tag(self, tagname, problem_id):
        self.db.execute("""INSERT INTO `problem_tag` (`tagname`, `problem_id`) VAlUES (%s, %s)""", tagname, int(problem_id))
    def insert_problem(self, problem):
        problem.id = self.db.execute("""INSERT INTO `problem` (`title`, `shortname`, `content`, \
                                     `timelimit`, `memlimit`, `testpoint`, `invisible`, `create`) \
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())""" \
                                     , problem.title, problem.shortname, problem.content, \
                                     int(problem.timelimit), int(problem.memlimit), int(problem.testpoint), int(problem.invisible))
    def delete_problem_tag_by_problem_id(self, problem_id):
        self.db.execute("""DELETE FROM `problem_tag` WHERE `problem_id` = %s""", int(problem_id))
    def update_problem(self, problem):
        self.db.execute("""UPDATE `problem` SET `title` = %s, 
                                                `shortname` = %s, 
                                                `content` = %s, 
                                                `timelimit` = %s, 
                                                `memlimit` = %s, 
                                                `testpoint` = %s, 
                                                `invisible` = %s
                                            WHERE `id` = %s""", \
                           problem.title, problem.shortname, problem.content, \
                           int(problem.timelimit), int(problem.memlimit), int(problem.testpoint), int(problem.invisible), \
                           problem.id)
    def count_problem(self):
        count = self.db.get("""SELECT COUNT(*) FROM `problem`""")
        return count["COUNT(*)"]
    def count_visible_problem(self):
        count = self.db.get("""SELECT COUNT(*) FROM `problem` WHERE `invisible` = 0""")
        return count["COUNT(*)"]
    def count_problem_by_tagname(self, tagname):
        count = self.db.get("""SELECT COUNT(*) FROM `problem_tag` WHERE `tagname` = %s""", tagname)
        return count["COUNT(*)"]
    def count_visible_problem_by_tagname(self, tagname):
        count = self.db.get("""SELECT COUNT(*), `problem`.* FROM `problem_tag` 
                               LEFT JOIN `problem` ON `problem_tag`.`problem_id` = `problem`.`id`
                               WHERE `tagname` = %s AND `problem`.`invisible` = 0""", tagname)
        return count["COUNT(*)"]
    def select_problem_tag_by_pid(self, pid):
        query = self.db.query("""SELECT * FROM `problem_tag` WHERE `problem_id` = %s""", pid)
        result = []
        if query:
            for row in query:
                result.append(row['tagname'])
        return result
    def select_problem_by_id(self, pid):
        query = self.db.get("""SELECT * FROM `problem` WHERE `id` = %s LIMIT 1""" , int(pid))
        if query:
            problem = Problem()
            problem._init_row(query)
            return problem
        return None
    def select_problem_order_by_id(self, nums = 10, start = 0):
        rows = self.db.query("""SELECT * FROM `problem` LIMIT %s, %s""", int(start), int(nums))
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result
    def select_problem_order_by_id_visible(self, nums = 10, start = 0):
        rows = self.db.query("""SELECT * FROM `problem` WHERE `invisible` = 0 LIMIT %s, %s""", int(start), int(nums))
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result
    def select_problem_by_create(self, nums = 10):
        rows = self.db.query("""SELECT * FROM `problem` ORDER BY `id` DESC LIMIT %s""", nums)
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result
    def select_problem_by_tagname(self, tagname, start = 0, nums = 10):
        rows = self.db.query("""SELECT `problem_tag`.*, `problem`.* 
                                FROM `problem_tag`
                                LEFT JOIN `problem` ON `problem_tag`.`problem_id` = `problem`.`id`
                                WHERE `tagname` = %s LIMIT %s, %s""", tagname, int(start), int(nums))
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result
    def select_visible_problem_by_tagname(self, tagname, start = 0, nums = 10):
        rows = self.db.query("""SELECT `problem_tag`.*, `problem`.* 
                                FROM `problem_tag`
                                LEFT JOIN `problem` ON `problem_tag`.`problem_id` = `problem`.`id`
                                WHERE `tagname` = %s AND `problem`.`invisible` = 0
                                LIMIT %s, %s""", tagname, int(start), int(nums))
        result = []
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

class NoteDBMixin(object):
    def _new_problem_by_row(self, row):
        if row:
            note = Note()
            note._init_row(row)
            return [note]
        return []
    def select_note_by_id(self, nid):
        query = self.db.get("""SELECT * FROM `note` WHERE `id` = %s LIMIT 1""", int(nid))
        if query:
            note = Note()
            note._init_row(query)
            return note
        return None
    def select_note_by_mid(self, mid, start = 0, count = 10):
        query = self.db.query("""SELECT * FROM `note` WHERE `member_id` = %s ORDER BY `id` DESC LIMIT %s, %s""" \
                              , int(mid), int(start), int(count))
        result = []
        if query:
            for row in query:
                result.extend(self._new_problem_by_row(row))
        return result
    def insert_note(self, note):
        note.id = self.db.execute("""INSERT INTO `note` (`title`, `content`, `member_id`, `create`)
                                     VALUES (%s, %s, %s, UTC_TIMESTAMP())""" \
                                  , note.title, note.content, int(note.member_id))
    def update_note(self, note):
        self.db.execute("""UPDATE `note` SET `title`   = %s, 
                                             `content` = %s
                                         WHERE `id` = %s""" \
                        , note.title, note.content, note.id)
    def delete_note_by_nid(self, nid):
        self.db.execute("""DELETE FROM `note` WHERE `id` = %s""", int(nid))

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


class RelatedProblem(BaseDBObject):
    pid = 0
    nid = 0

class RelatedProblemDBMixin(object):
    def _new_related_problem_by_row(self, row):
        if row:
            related_problem = RelatedProblem()
            related_problem._init_row(row)
            return [related_problem]
        return []
    def select_related_problem_by_pid(self, pid, start = 0, max = 5):
        rows = self.db.query("""SELECT `related_problem`.*, `note`.`title`, `note`.`content`, `note`.`member_id`, `member`.`username`
                                FROM `related_problem` 
                                LEFT JOIN `note` ON `related_problem`.`nid` = `note`.`id`
                                LEFT JOIN `member` ON `note`.`member_id` = `member`.`id`
                                WHERE `pid` = %s LIMIT %s, %s""", pid, start, max)
        result = []
        for row in rows:
            result.extend(self._new_related_problem_by_row(row))
        return result
    def select_related_problem_by_nid(self, nid, start = 0, max = 20):
        rows = self.db.query("""SELECT `related_problem`.*, `problem`.`title`
                                FROM `related_problem`
                                LEFT JOIN `problem` ON `related_problem`.`pid` = `problem`.`id`
                                WHERE `nid` = %s LIMIT %s, %s""", nid, start, max)
        result = []
        for row in rows:
            result.extend(self._new_related_problem_by_row(row))
        return result
    def insert_related_problem(self, related_problem):
        self.db.execute("""INSERT INTO `related_problem` (`pid`, `nid`) VALUES (%s, %s)""", \
                        related_problem.pid, related_problem.nid)
    def delete_related_problem_by_nid(self, nid):
        self.db.execute("""DELETE FROM `related_problem` WHERE `nid` = %s""", nid)
    def delete_related_problem_by_pid(self, pid):
        self.db.execute("""DELETE FROM `related_problem` WHERE `pid` = %s""", pid)

class Submit(BaseDBObject):
    id = ""
    problem_id = 0
    member_id = 0
    status = 0 # Pending = 0, Accepted = 1, Wrong Answer = 2, Time Limit Exceeded = 3, Memory Limit Exceeded = 4, Runtime Error = 5, Compile Error = 6
    testpoint = ""
    score = 0
    costtime = 0   # ms
    costmemory = 0 # kb
    timestamp = None
    lang = 0 # 
    user_agent = ""
    ip = ""
    create = None

class SubmitDBMixin(object):
    def _new_submit_by_row(self, row):
        if row:
            submit = Submit()
            submit._init_row(row)
            return [submit]
        return []
    def select_submit_desc(self, start = 0, max = 20):
        rows = self.db.query("""SELECT `submit`.*, `problem`.`title`, `member`.`username`
                                FROM `submit` 
                                LEFT JOIN `member` ON `submit`.`member_id` = `member`.`id`
                                LEFT JOIN `problem` ON `submit`.`problem_id` = `problem`.`id`
                                ORDER BY `id` DESC LIMIT %s, %s""", start, max)
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_submit_by_row(row))
        return result
    def select_submit_by_member_id_desc(self, mid, start = 0, max = 20):
        rows = self.db.query("""SELECT * FROM `submit` WHERE `member_id` = %s ORDER BY `id` DESC LIMIT %s, %s""", mid, start, max)
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_submit_by_row(row))
        return result
    def select_submit_by_problem_id_desc(self, pid, start = 0, max = 20):
        rows = self.db.query("""SELECT * FROM `submit` WHERE `problem_id` = %s ORDER BY `id` DESC LIMIT %s, %s""", pid, start, max)
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_submit_by_row(row))
        return result

class Contest(BaseDBObject):
    id = ""
    title = ""
    description = ""
    start_time = None
    end_time = None
    invisible = 0 # 0 - visible   1 - invisible
    create = None

class ContestProblem(BaseDBObject):
    cid = 0
    pid = 0

class ContestSubmit(BaseDBObject):
    id = ""
    contest_id = 0
    problem_id = 0
    member_id = 0
    status = 0 # Pending = 0, Accepted = 1, Wrong Answer = 2, Time Limit Exceeded = 3, Memory Limit Exceeded = 4, Runtime Error = 5, Compile Error = 6
    testpoint = ""
    score = 0
    costtime = 0   # ms
    costmemory = 0 # kb
    lang = 0 # 
    timestamp = None
    msg = ""
    user_agent = ""
    ip = ""
    create = None

class ContestDBMixin(object):
    def _new_contest_by_row(self, row):
        if row:
            contest = Contest()
            contest._init_row(row)
            return [contest]
        return []
    def _new_contest_problem_by_row(self, row):
        if row:
            contest_problem = ContestProblem()
            contest_problem._init_row(row)
            return [contest_problem]
        return []
    def _new_contest_submit_by_row(self, row):
        if row:
            contest_submit = ContestSubmit()
            contest_submit._init_row(row)
            return [contest_submit]
        return []
    def insert_contest(self, contest):
        contest.id = self.db.execute("""INSERT INTO `contest` (`title`, `description`, `start_time`, 
                                                               `end_time`, `invisible`, `create`)
                                               VALUES (%s, %s, %s, %s, %s, UTC_TIMESTAMP())""", \
                                     contest.title, contest.description, contest.start_time, contest.end_time, \
                                     contest.invisible)
    def insert_contest_problem(self, cid, pid):
        self.db.execute("""INSERT INTO `contest_problem` (`cid`, `pid`) VALUES (%s, %s)""", int(cid), int(pid))
    def update_contest(self, contest):
        self.db.execute("""UPDATE `contest` SET `title` = %s, 
                                                `description` = %s, 
                                                `start_time` = %s, 
                                                `end_time` = %s, 
                                                `invisible` = %s
                                            WHERE `id` = %s""" \
                        , contest.title, contest.description, contest.start_time, contest.end_time, \
                        contest.invisible, contest.id)
    def delete_contest_problem_by_cid(self, cid):
        self.db.execute("""DELETE FROM `contest_problem` WHERE `cid` = %s""", cid)
    def select_contest(self, start = 0, max = 20):
        rows = self.db.query("""SELECT * FROM `contest` LIMIT %s, %s""", start, max)
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_contest_by_row(row))
        return result
    def select_contest_visible(self, start = 0, max = 20):
        rows = self.db.query("""SELECT * FROM `contest` WHERE `invisible` = 0 LIMIT %s, %s""", start, max)
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_contest_by_row(row))
        return result
    def select_contest_by_id(self, cid):
        row = self.db.get("""SELECT * FROM `contest` WHERE `id` = %s""", cid)
        if row:
            contest = Contest()
            contest._init_row(row)
            return contest
        return None
    def select_contest_problem_by_cid(self, cid):
        rows = self.db.query("""SELECT `contest_problem`.*, `problem`.`title`
                                FROM `contest_problem`
                                LEFT JOIN `problem` ON `contest_problem`.`pid` = `problem`.`id`
                                WHERE `cid` = %s""", cid)
        result = []
        if rows:
            for row in rows:
                result.extend(self._new_contest_problem_by_row(row))
        return result
    def select_contest_submit_by_cid_and_uid(self, cid, uid):
        rows = self.db.query("""SELECT `contest_problem`.*, `problem`.`title`, `problem`.`shortname`
                                FROM `contest_problem`
                                LEFT JOIN `problem` ON `contest_problem`.`pid` = `problem`.`id`
                                WHERE `cid` = %s""", cid)
        result = []
        if rows:
            for row in rows:
                contest_problem = self._new_contest_problem_by_row(row) 
                query = self.db.get("""SELECT * FROM `contest_submit` WHERE `member_id` = %s AND `problem_id` = %s ORDER BY `id` DESC LIMIT 1""", uid, contest_problem[0].pid)
                contest_problem[0].submit = ContestSubmit()
                contest_problem[0].submit._init_row(query)
                result.extend(contest_problem)
        return result

