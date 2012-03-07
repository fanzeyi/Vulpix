# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/db/__init__.py
# CREATED: 02:01:23 08/03/2012
# MODIFIED: 02:29:52 08/03/2012
# DESCRIPTION: Database Table Object

from judge.base import BaseDBMixin
from judge.base import BaseDBObject

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
    pass

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
