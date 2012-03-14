# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/db/__init__.py
# CREATED: 02:01:23 08/03/2012
# MODIFIED: 02:39:32 15/03/2012
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
    ''' DELETE '''
    def delete_auth_by_secret(self, secret):
        self.db.execute("""DELETE FROM `auth` WHERE `secret` = %s""", secret)
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
    pass

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

class ProblemDBMixin(BaseDBMixin):
    pass

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
    pass
