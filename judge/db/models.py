# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/db/models.py
# CREATED: 23:40:55 17/04/2012
# MODIFIED: 00:29:45 18/04/2012

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def init_db(engine):
    Base.metadata.create_all(bind=engine)

class Member(Base):
    __tablename__ = "member"
    id = Column(Integer, primary_key = True)
    username = Column(String)
    username_lower = Column(String)
    password = Column(String)
    email = Column(String)
    website = Column(String)
    tagline = Column(String)
    bio = Column(String)
    gravatar_link = Column(String)
    create = Column(DateTime)
    admin = Column(Integer)
    lang = Column(Integer)

class Auth(Base):
    __tablename__ = "auth"
    id = Column(Integer, primary_key = True)
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("member")
    secret = Column(String)
    create = Column(DateTime)

class ResetMail(Base):
    __tablename__ = "reset_mail"
    id = Column(Integer, primary_key = True)
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("member")
    secret = Column(String)
    create = Column(DateTime)

class Node(Base):
    __tablename__ = "node"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    link = Column(String)
    description = Column(String)

class Topic(Base):
    __tablename__ = "topic"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    content = Column(String)
    node_id = Column(Integer, ForeignKey("node.id"))
    node = relation("node")
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("member")
    create = Column(DateTime)
    last_reply = Column(DateTime)

class Reply(Base):
    __tablename__ = "reply"
    id = Column(Integer, primary_key = True)
    content = Column(String)
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("member")
    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relation("topic")
    create = Column(DateTime)

class Note(Base):
    __tablename__ = "note"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    content = Column(String)
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("member")
    create = Column(DateTime)

class RelatedProblem(Base):
    __tablename__ = "related_problem"
    id = Column(Integer, primary_key = True)
    problem_id = Column(Integer, ForeignKey("problem.id"))
    problem = relation("problem")
    note_id = Column(Integer, ForeignKey("note.id"))
    note = relation("note")

class Problem(Base):
    __tablename__ = "problem"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    shortname = Column(String)
    content = Column(String)
    timelimit = Column(Integer)
    memlimit = Column(Integer)
    testpoint = Column(Integer)
    invisible = Column(Boolean)
    create = Column(DateTime)

class ProblemTag(Base):
    __tablename__ = "problem_tag"
    id = Column(Integer, primary_key = True)
    problem_id = Column(Integer, ForeignKey("problem.id"))
    problem = relation("problem")
    tagname = Column(String)

class Submit(Base):
    __tablename__ = "submit"
    id = Column(Integer, primary_key = True)
    problem_id = Column(Integer, ForeignKey("problem.id"))
    problem = relation("problem")
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("member")
    code = Column(String)
    status = Column(Integer)
    testpoint = Column(String)
    testpoint_time = Column(String)
    testpoint_memory = Column(String)
    score = Column(Integer)
    costtime = Column(Integer)
    costmemory = Column(Integer)
    timestamp = Column(String)
    lang = Column(Integer)
    msg = Column(String)
    user_agent = Column(String)
    ip = Column(String)
    create = Column(DateTime)

class Contest(Base):
    __tablename__ = "contest"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    invisible = Column(Boolean)
    create = Column(DateTime)

class ContestProblem(Base):
    __tablename__ = "contest_problem"
    id = Column(Integer, primary_key = True)
    contest_id = Column(Integer, ForeignKey("contest.id"))
    contest = relation("contest")
    problem_id = Column(Integer, ForeignKey("problem.id"))
    problem = relation("problem")

class ContestSubmit(Base):
    __tablename__ = "contest_submit"
    id = Column(Integer, primary_key = True)
    contest_id = Column(Integer, ForeignKey("contest.id"))
    contest = relation("contest")
    problem_id = Column(Integer, ForeignKey("problem.id"))
    problem = relation("problem")
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("member")
    code = Column(String)
    status = Column(Integer)
    testpoint = Column(String)
    testpoint_time = Column(String)
    testpoint_memory = Column(String)
    score = Column(Integer)
    costtime = Column(Integer)
    costmemory = Column(Integer)
    timestamp = Column(String)
    lang = Column(Integer)
    msg = Column(String)
    user_agent = Column(String)
    ip = Column(String)
    create = Column(DateTime)

class Judger(Base):
    __tablename__ = "judger"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    description = Column(String)
    path = Column(String)
    priority = Column(Integer)
    queue_num = Column(Integer)
    pubkey = Column(String)
    create = Column(DateTime)
