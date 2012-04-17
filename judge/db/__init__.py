# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/db/__init__.py
# CREATED: 02:01:23 08/03/2012
# MODIFIED: 23:04:42 17/04/2012
# DESCRIPTION: Database Table Object

import uuid
import binascii

class BaseDBObject(object):
    ''' Base Table Object '''
    def __repr__(self):
        ''' for debug '''
        result = ", \n".join(["'%s': '%s'" % (attr, getattr(self, attr)) for attr in dir(self) if attr[0] != '_' and not callable(getattr(self, attr)) ])
        return "<{%s}>" % result
    def _init_row(self, row):
        keys = row.keys()
        for key in keys:
            setattr(self, key, row[key])

class BaseDBMixin(object):
    ''' Base Database Mixin '''
    def _new_object_by_row(self, Obj, row):
        obj = Obj()
        obj._init_row(row)
        return obj

'''
'' ===================================
''            Member Table 
'' ===================================
'''

class Member(BaseDBObject):
    '''User data table'''
    __tablename__ = "member"
    id = 0
    username = ""
    username_lower = ""
    passowrd = ""
    email = ""
    website = ""
    tagline = ""
    bio = ""
    gravatar_link = ""
    create = None
    admin = 0
    lang = 1

class Auth(BaseDBObject):
    '''User auth table'''
    __tablename__ = "auth"
    member_id = 0 
    secret = ""
    create = None

class ResetMail(BaseDBObject):
    '''User reset mail table'''
    __tablename__ = "reset_mail"
    member_id = 0
    secret = ""
    create = None

class MemberDBMixin(BaseDBMixin):
    ''' New Data Model '''
    def _new_member(self, row):
        member = Member()
        member._init_row(row)
        return member
    ''' COUNT '''
    def count_member(self):
        count = self.db.get("""SELECT COUNT(*) FROM `member`""")
        return count["COUNT(*)"]
    def count_accepted_by_member_id(self, member_id):
        count = self.db.get("""SELECT COUNT(*) FROM `submit` WHERE `status` = 1 AND `member_id` = %s""", member_id)
        return count["COUNT(*)"]
    def count_submit_by_member_id(self, member_id):
        count = self.db.get("""SELECT COUNT(*) FROM `submit` WHERE `member_id` = %s""", member_id)
        return count["COUNT(*)"]
    ''' SELECT '''
    def select_member_by_username_lower(self, username_lower):
        row = self.db.get("""SELECT * FROM `member` WHERE `username_lower` = %s LIMIT 1""", username_lower)
        if row:
            return self._new_member(row)
        return None
    def select_member_by_email(self, email):
        row = self.db.get("""SELECT * FROM `member` WHERE `email` = %s LIMIT 1""", email)
        if row:
            return self._new_member(row)
        return None
    def select_member_by_usr_pwd(self, usr, pwd):
        row = self.db.get("""SELECT * FROM `member` WHERE `username` = %s AND `password` = %s LIMIT 1""", usr, pwd)
        if row:
            return self._new_member(row)
        return None
    def select_member_order_by_id(self, count = 10, start = 0):
        rows = self.db.query("""SELECT * FROM `member` ORDER BY `id` LIMIT %s, %s""", int(start), int(count))
        result = []
        for row in rows:
            result.append(self._new_member(row))
        return result
    ''' INSERT '''
    def insert_member(self, member):
        member.id = self.db.execute("""INSERT INTO `member` (`username`, `username_lower`, `password`, `email`, 
                                                             `gravatar_link`, `create`, `website`, `tagline`, `bio`, 
                                                             `admin`, `lang`)
                                              VALUES (%s, %s, %s, %s, %s, UTC_TIMESTAMP(), %s, %s, %s, %s, %s)""", \
                                    member.username, member.username_lower, member.passowrd, member.email, member.gravatar_link, \
                                    member.website, member.tagline, member.bio, member.admin, member.lang)
    def insert_auth(self, member_id, random):
        self.db.execute("""INSERT INTO `auth` (`member_id`, `secret`, `create`) VALUES (%s, %s, UTC_TIMESTAMP())""", \
                        member_id, random)
        auth = Auth()
        auth.member_id = member_id
        auth.secret = random
        return auth
    ''' UPDATE '''
    def update_member(self, member):
        self.db.execute("""UPDATE `member`
                           SET `email` = %s, 
                               `gravatar_link` = %s, 
                               `website` = %s, 
                               `tagline` = %s, 
                               `bio` = %s, 
                               `lang` = %s
                           WHERE `id` = %s""", member.email, member.gravatar_link, \
                                               member.website, member.tagline, member.bio, \
                                               member.lang, member.id)
    def update_member_password(self, member):
        self.db.execute("""UPDATE `member` SET `password` = %s WHERE `id` = %s""", member.password, member.id)
    ''' DELETE '''
    def delete_auth_by_secret(self, secret):
        self.db.execute("""DELETE FROM `auth` WHERE `secret` = %s""", secret)
    def delete_auth_by_member_id(self, member_id):
        self.db.execute("""DELETE FROM `auth` WHERE `member_id` = %s""", member_id)
    ''' OTHER '''
    def create_auth(self, member_id):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        return self.insert_auth(member_id, random)


'''
'' ===================================
''            Forum Table 
'' ===================================
'''

class Node(BaseDBObject):
    '''Forum node table'''
    __tablename__ = "node"
    id = 0
    name = ""
    description = ""
    link = ""

class Topic(BaseDBObject):
    '''Forum topic table'''
    __tablename__ = "topic"
    id = 0
    title = ""
    content = ""
    node_id = 0
    member_id = 0
    create = None
    last_reply = None

class Reply(BaseDBObject):
    '''Forum topic reply table'''
    __tablename__ = "reply"
    id = 0
    content = ""
    member_id = 0
    topic_id = 0
    create = None

class ForumDBMixin(BaseDBMixin):
    def _new_node(row):
        node = Node()
        node._init_row(row)
        return node
    '''COUNT'''
    '''SELECT'''
    def select_node_by_id(self, node_id):
        row = self.db.get("""SELECT * FROM `node` WHERE `id` = %s""", int(node_id))
        if row:
            return self._new_node(row)
        return None
    '''INSERT'''
    def insert_node(self, node):
        node.id = self.db.execute("""INSERT INTO `node` (`name`, `link`, `description`) 
                                     VALUES (%s, %s, %s)""", node.name, node.link, node.description)
    '''UPDATE'''
    def update_node(self, node):
        self.db.execute("""UPDATE `node` SET `name` = %s, 
                                             `link` = %s, 
                                             `description` = %s, 
                                         WHERE `node`.`id` = %s""", node.name, node.link, node.description, node.id)
    '''DELETE'''

'''
'' ===================================
''             Note Table 
'' ===================================
'''

class Note(BaseDBObject):
    '''Note data table'''
    __tablename__ = "note"
    id = 0
    title = ""
    content = ""
    member_id = 0
    create = None

class RelatedProblem(BaseDBObject):
    '''Note related problem table'''
    __tablename__ = "related_problem"
    problem_id = 0
    note_id = 0

class NoteDBMixin(BaseDBMixin):
    pass

'''
'' ===================================
''           Problem Table 
'' ===================================
'''

class Problem(BaseDBObject):
    '''Problem table'''
    __tablename__ = "problem"
    id = 0
    title = ""
    shortname = ""
    content = ""
    timelimit = 0
    memlimit = 0
    testpoint = 0
    invisible = 0
    create = None

class ProblemTag(BaseDBObject):
    '''Problem tag table'''
    __tablename__ = "problem_tag"
    problem_id = 0
    tagname = ""

class Submit(BaseDBObject):
    '''Submit table'''
    __tablename__ = "submit"
    id = 0
    problem_id = 0
    member_id = 0
    code = ""
    status = 0
    testpoint = 0
    testpoint_time = ""
    testpoint_memory = ""
    score = 0
    costtime = 0
    costmemory = 0
    timestamp = ""
    lang = 0
    msg = ""
    user_agent = 0
    ip = 0
    create = 0

class ProblemDBMixin(BaseDBMixin):
    ''' New Data Model '''
    def _new_problem(self, row):
        problem = Problem()
        problem._init_row(row)
        return problem
    def _new_problem_tag(self, row):
        problem_tag = ProblemTag()
        problem_tag._init_row(row)
        return problem_tag
    def _new_submit(self, row):
        submit = Submit()
        submit._init_row(row)
        return submit
    ''' COUNT '''
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
        count = self.db.get("""SELECT COUNT(*) FROM `problem_tag` 
                               LEFT JOIN `problem` ON `problem_tag`.`problem_id` = `problem`.`id`
                               WHERE `tagname` = %s AND `problem`.`invisible` = 0""", tagname)
        return count["COUNT(*)"]
    def count_submit(self):
        count = self.db.get("""SELECT COUNT(*) FROM `submit`""")
        return count["COUNT(*)"]
    ''' SELECT '''
    def select_problem_by_id(self, id):
        row = self.db.get("""SELECT * FROM `problem` WHERE `id` = %s LIMIT 1""", id)
        if row:
            return self._new_problem(row)
        return None
    def select_problem_tag_by_problem_id(self, problem_id):
        rows = self.db.query("""SELECT * FROM `problem_tag` WHERE `problem_id` = %s""", problem_id)
        result = []
        for row in rows:
            result.append(self._new_problem_tag(row))
        return result
    def select_problem_order_by_id(self, count = 10, start = 0):
        rows = self.db.query("""SELECT * FROM `problem` LIMIT %s, %s""", int(start), int(count))
        result = []
        for row in rows:
            result.append(self._new_problem(row))
        return result
    def select_visible_problem_order_by_id(self, count = 10, start = 0):
        rows = self.db.query("""SELECT * FROM `problem` WHERE `invisible` = 0 LIMIT %s, %s""", int(start), int(count))
        result = []
        for row in rows:
            result.append(self._new_problem(row))
        return result
    def select_latest_visible_problem_order_by_id(self, count = 10):
        rows = self.db.query("""SELECT * FROM `problem` WHERE `invisible` = 0 ORDER BY `id` DESC LIMIT %s""", int(count))
        result = []
        for row in rows:
            result.append(self._new_problem(row))
        return result
    def select_last_submit_by_problem_id_member_id(self, problem_id):
        row = self.db.get("""SELECT * FROM `submit` WHERE `problem_id` = %s AND `member_id` = %s ORDER BY `id` DESC LIMIT 1""", \
                          problem_id, self.current_user.id)
        if row:
            return self._new_submit(row)
        return None
    def select_submit_by_id(self, sid):
        row = self.db.get("""SELECT `submit`.*, `member`.`username`, `problem`.`title` FROM `submit` 
                             LEFT JOIN `member` ON `submit`.`member_id` = `member`.`id`
                             LEFT JOIN `problem` ON `submit`.`problem_id` = `problem`.`id`
                             WHERE `submit`.`id` = %s LIMIT 1""", int(sid))
        if row:
            return self._new_submit(row)
        return None
    def select_submit_order_by_id(self, count = 10, start = 0):
        rows = self.db.query("""SELECT `submit`.*, `member`.`username`, `problem`.`title` FROM `submit` 
                                LEFT JOIN `member` ON `submit`.`member_id` = `member`.`id`
                                LEFT JOIN `problem` ON `submit`.`problem_id` = `problem`.`id`
                                ORDER BY `submit`.`id` DESC LIMIT %s, %s""", int(start), int(count))
        result = []
        for row in rows:
            result.append(self._new_submit(row))
        return result
    def select_submit_by_member_id(self, member_id, count = 10):
        rows = self.db.query("""SELECT `submit`.*, `problem`.`title` FROM `submit` 
                                LEFT JOIN `member` ON `submit`.`member_id` = `member`.`id`
                                LEFT JOIN `problem` ON `submit`.`problem_id` = `problem`.`id`
                                WHERE `submit`.`member_id` = %s
                                ORDER BY `submit`.`id` DESC LIMIT %s""", int(member_id), int(count))
        result = []
        for row in rows:
            result.append(self._new_submit(row))
        return result
    def select_problem_by_tagname(self, tagname, count = 10, start = 0):
        rows = self.db.query("""SELECT `problem_tag`.*, `problem`.* FROM `problem_tag` 
                                LEFT JOIN `problem` ON `problem_tag`.`problem_id` = `problem`.`id`
                                WHERE `problem_tag`.`tagname` = %s AND `problem`.`invisible` = 0 
                                ORDER BY `problem`.`id` ASC
                                LIMIT %s, %s""", tagname, int(start), int(count))
        result = []
        for row in rows:
            result.append(self._new_problem(row))
        return result
    def select_visible_problem_by_tagname(self, tagname, count = 10, start = 0):
        rows = self.db.query("""SELECT `problem_tag`.*, `problem`.* FROM `problem_tag` 
                                LEFT JOIN `problem` ON `problem_tag`.`problem_id` = `problem`.`id`
                                WHERE `problem_tag`.`tagname` = %s 
                                ORDER BY `problem`.`id` ASC
                                LIMIT %s, %s""", tagname, int(start), int(count))
        result = []
        for row in rows:
            result.append(self._new_problem(row))
        return result
    ''' INSERT '''
    def insert_problem(self, problem):
        problem.id = self.db.execute("""INSERT INTO `problem` (`title`, `shortname`, `content`, \
                                     `timelimit`, `memlimit`, `testpoint`, `invisible`, `create`) \
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())""" \
                                     , problem.title, problem.shortname, problem.content, \
                                     int(problem.timelimit), int(problem.memlimit), int(problem.testpoint), int(problem.invisible))
    def insert_problem_tag(self, tagname, problem_id):
        self.db.execute("""INSERT INTO `problem_tag` (`tagname`, `problem_id`) VAlUES (%s, %s)""", tagname, int(problem_id))
    def insert_submit(self, submit):
        submit.id = self.db.execute("""INSERT INTO `submit` (`problem_id`, `member_id`, `code`, `timestamp`,
                                                            `lang`, `user_agent`, `ip`, `create`)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())""", \
                                    submit.problem_id, submit.member_id, submit.code, submit.timestamp, \
                                    submit.lang, submit.user_agent, submit.ip)
    ''' UPDATE '''
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
    ''' DELETE '''
    def delete_problem_tag_by_problem_id(self, problem_id):
        self.db.execute("""DELETE FROM `problem_tag` WHERE `problem_id` = %s""", int(problem_id))
    ''' OTHER '''

'''
'' ===================================
''          Contest Table 
'' ===================================
'''

class Contest(BaseDBObject):
    '''Contest data table'''
    __tablename__ = "contest"
    id = 0
    title = ""
    description = ""
    start_time = None
    end_time = None
    invisible = 0
    create = None

class ContestProblem(BaseDBObject):
    '''Contest problem table'''
    __tablename__ = "contest_problem"
    contest_id = 0
    problem_id = 0

class ContestSubmit(BaseDBObject):
    '''Contest submit table'''
    __tablename__ = "contest_submit"
    contest_id = 0
    problem_id = 0
    member_id = 0
    status = 0
    testpoint = ""
    score = 0
    costtime = 0
    costmemory = 0
    timestamp = ""
    lang = 0
    msg = ""
    user_agent = 0
    ip = 0
    create = 0

class ContestDBMixin(BaseDBMixin):
    ''' New Data Model '''
    def _new_contest(self, row):
        contest = Contest()
        contest._init_row(row)
        return contest
    def _new_contest_problem(self, row):
        contest_problem = ContestProblem()
        contest_problem._init_row(row)
        return contest_problem
    def _new_contest_submit(self, row):
        contest_submit = ContestSubmit()
        contest_submit._init_row(row)
        return contest_submit
    ''' COUNT '''
    def count_contest(self):
        row = self.db.get("""SELECT COUNT(*) FROM `contest`""")
        return row["COUNT(*)"]
    def count_visible_contest(self):
        row = self.db.get("""SELECT COUNT(*) FROM `contest` WHERE invisible = 0""")
        return row["COUNT(*)"]
    ''' SELECT '''
    def select_contest_by_id(self, contest_id):
        row = self.db.get("""SELECT * FROM `contest` WHERE `id` = %s""", contest_id)
        if row:
            return self._new_contest(row)
        return None
    def select_contest_problem_by_contest_id(self, contest_id):
        rows = self.db.query("""SELECT *, `problem`.* FROM `contest_problem`
                                LEFT JOIN `problem` ON `contest_problem`.`problem_id` = `problem`.`id`
                                WHERE `contest_id` = %s""", contest_id)
        result = []
        for row in rows:
            result.append(self._new_contest_problem(row))
        return result
    def select_contest_submit_by_contest_id_problem_id_user_id(self, contest_id, problem_id):
        row = self.db.get("""SELECT * FROM `contest_submit` WHERE `contest_id` = %s AND `problem_id` = %s AND `member_id` = %s""", \
                          contest_id, problem_id, self.current_user.id)
        if row:
            return self._new_contest_submit(row)
        return None
    def select_contest(self, start = 0, count = 20):
        rows = self.db.query("""SELECT * FROM `contest` ORDER BY `id` DESC LIMIT %s, %s""", start, count)
        result = []
        for row in rows:
            result.append(self._new_contest(row))
        return result
    def select_visible_contest(self, start = 0, count = 20):
        rows = self.db.query("""SELECT * FROM `contest` WHERE `invisible` = 0 ORDER BY `id` DESC LIMIT %s, %s""", start, count)
        result = []
        for row in rows:
            result.append(self._new_contest(row))
        return result
    ''' INSERT '''
    def insert_contest(self, contest):
        contest.id = self.db.execute("""INSERT INTO `contest` (`title`, `description`, `start_time`, 
                                                               `end_time`, `invisible`, `create`)
                                               VALUES (%s, %s, %s, %s, %s, UTC_TIMESTAMP())""", \
                                     contest.title, contest.description, contest.start_time, contest.end_time, \
                                     contest.invisible)
    def insert_contest_problem(self, contest_id, problem_id):
        self.db.execute("""INSERT INTO `contest_problem` (`contest_id`, `problem_id`) VALUES (%s, %s)""", int(contest_id), int(problem_id))
    ''' UPDATE '''
    def update_contest(self, contest):
        self.db.execute("""UPDATE `contest` SET `title` = %s, 
                                                `description` = %s, 
                                                `start_time` = %s, 
                                                `end_time` = %s, 
                                                `invisible` = %s
                                            WHERE `id` = %s""" \
                        , contest.title, contest.description, contest.start_time, contest.end_time, \
                        contest.invisible, contest.id)
    ''' DELETE '''
    def delete_contest_problem_by_contest_id(self, contest_id):
        self.db.execute("""DELETE FROM `contest_problem` WHERE `contest_id` = %s""", contest_id)
    ''' OTHER '''

class Judger(BaseDBObject):
    '''Contest problem table'''
    __tablename__ = "judge"
    id = 0
    name = ""
    description = ""
    path = "" # support HTTP protocol
    priority = 0
    queue_num = 0
    pubkey = ""
    create = None

class JudgerDBMixin(BaseDBMixin):
    ''' New Data Model '''
    def _new_judger(self, row):
        judger = Judger()
        judger._init_row(row)
        return judger
    ''' SELECT '''
    def select_judgers(self):
        rows = self.db.query("""SELECT * FROM `judger`""")
        result = []
        for row in rows:
            result.append(self._new_judger(row))
        return result
    def select_judger_by_id(self, juder_id):
        row = self.db.get("""SELECT * FROM `judger` WHERE `id` = %s""", juder_id)
        if row:
            return self._new_judger(row)
        return None
    def select_judger_by_queue(self):
        row = self.db.get("""SELECT * FROM `judger` ORDER BY `queue_num`, `priority` LIMIT 1""")
        if row:
            return self._new_judger(row)
        return None
    ''' INSERT '''
    def insert_judger(self, judger):
        judger.id = self.db.execute("""INSERT INTO `judger` (`name`, `description`, `path`, \
                                                             `priority`, `queue_num`, `pubkey`, `create`)
                                              VALUES (%s, %s, %s, %s, 0, %s, UTC_TIMESTAMP())""", \
                                    judger.name, judger.description, judger.path, judger.priority, judger.pubkey)
    ''' UPDATE '''
    def update_judger(self, judger):
        self.db.execute("""UPDATE `judger` SET `name` = %s, 
                                               `description` = %s, 
                                               `path` = %s, 
                                               `priority` = %s,
                                               `pubkey` = %s
                                           WHERE `id` = %s""", \
                           judger.name, judger.description, judger.path, judger.priority, judger.pubkey, judger.id)
    def update_judger_count(self, judger):
        self.db.execute("""UPDATE `judger` SET `queue_num` = 0 WHERE `id` = %s""", judger.id)
