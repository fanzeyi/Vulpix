# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/db/__init__.py
# CREATED: 02:01:23 08/03/2012
# MODIFIED: 20:41:50 18/04/2012
# DESCRIPTION: Database Table Object

import uuid
import binascii
import datetime
from sqlalchemy import desc
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

from judge.db.models import *

'''
'' ===================================
''            Member Table 
'' ===================================
'''

class MemberDBMixin(object):
    ''' COUNT '''
    def count_member(self):
        return self.db.query(Member).count()
    def count_accepted_by_member_id(self, member_id):
        return self.db.query(Submit).filter_by(member_id = member_id).filter_by(status = 1).count()
    def count_submit_by_member_id(self, member_id):
        return self.db.query(Submit).filter_by(member_id = member_id).count()
    ''' SELECT '''
    def select_member_by_id(self, member_id):
        return self.db.query(Member).get(member_id)
    def select_member_by_username_lower(self, username_lower):
        return self.db.query(Member).filter_by(username_lower = username_lower).one()
    def select_member_by_email(self, email):
        return self.db.query(Member).filter_by(email = email).one()
    def select_member_by_usr_pwd(self, usr, pwd):
        return self.db.query(Member).filter_by(username_lower = usr.lower()).filter_by(password = pwd).one()
    def select_member_order_by_id(self, count = 10, start = 0):
        return self.db.query(Member).order_by(Member.id).offset(start).limit(count).all()
    ''' INSERT '''
    def insert_member(self, member):
        member.create = datetime.datetime.now()
        self.db.add(member)
        self.db.commit()
    def insert_auth(self, member_id, random):
        auth = Auth()
        auth.member_id = member_id
        auth.secret = random
        auth.create = datetime.datetime.now()
        self.db.add(auth)
        self.db.commit()
        return auth
    ''' UPDATE '''
    def update_member(self, member):
        db_member = self.select_member_by_id(member.id)
        db_member.email = member.email
        db_member.website = member.website
        db_member.tagline = member.tagline
        db_member.bio = member.bio
        db_member.gravatar_link = member.gravatar_link
        db_member.lang = member.lang
        self.db.commit()
    def update_member_password(self, member):
        db_member = self.select_member_by_id(member.id)
        db_member.password = member.password
    ''' DELETE '''
    def delete_auth_by_secret(self, secret):
        self.db.query(Auth).filter_by(secret = secret).delete()
    def delete_auth_by_member_id(self, member_id):
        self.db.query(Auth).filter_by(member_id = member_id).delete()
    ''' OTHER '''
    def create_auth(self, member_id):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        return self.insert_auth(member_id, random)


'''
'' ===================================
''            Forum Table 
'' ===================================
'''

class ForumDBMixin(object):
    '''COUNT'''
    def count_reply_by_topic_id(self, topic_id):
        return self.db.query(Reply).filter_by(topic_id = topic_id).count()
    '''SELECT'''
    def select_latest_node(self, count = 20):
        return self.db.query(Node).order_by(desc(Node.id)).limit(count).all()
    def select_node_by_id(self, node_id):
        return self.db.query(Node).get(node_id)
    def select_node_by_link(self, link):
        return self.db.query(Node).filter_by(link = link).one()
    def select_topic_by_id(self, topic_id):
        return self.db.query(Topic).get(topic_id)
    def select_topic_by_node_id(self, node_id, start = 0, count = 10):
        return self.db.query(Topic).filter_by(node_id = node_id).order_by(desc(Topic.last_reply)).offset(start).limit(count).all()
    def select_reply_by_topic_id(self, topic_id):
        return self.db.query(Reply).filter_by(topic_id = topic_id).all()
    def select_lates_topic(self, start = 0, count = 10):
        return self.db.query(Topic).order_by(desc(Topic.last_reply)).offset(start).limit(count).all()
    '''INSERT'''
    def insert_node(self, node):
        self.db.add(node)
        self.db.commit()
    def insert_topic(self, topic):
        # a bug here.. todo
        topic.create = datetime.datetime.now()
        topic.last_reply = datetime.datetime.now()
        self.db.add(topic)
        self.db.commit()
    '''UPDATE'''
    def update_node(self, node):
        db_node = self.select_node_by_id(node.id)
        db_node.name = node.name
        db_node.link = node.link
        db_node.description = node.description
        self.db.commit()
    def update_topic(self, topic):
        db_topic = self.select_topic_by_id(topic.id)
        db_topic.title   = topic.title
        db_topic.content = topic.content
    '''DELETE'''

'''
'' ===================================
''             Note Table 
'' ===================================
'''

class NoteDBMixin(object):
    pass

'''
'' ===================================
''           Problem Table 
'' ===================================
'''

class ProblemDBMixin(object):
    ''' COUNT '''
    def count_problem(self):
        return self.db.query(Problem).count()
    def count_visible_problem(self):
        return self.db.query(Problem).filter_by(invisible = 0).count()
    def count_problem_by_tagname(self, tagname):
        return self.db.query(ProblemTag).filter_by(tagname = tagname).count()
    def count_visible_problem_by_tagname(self, tagname):
        return self.db.query(ProblemTag).filter_by(tagname = tagname).join(Problem).filter_by(invisible = 0).count()
    def count_submit(self):
        return self.db.query(Submit).count()
    ''' SELECT '''
    def select_problem_by_id(self, id):
        return self.db.query(Problem).get(id)
    def select_problem_tag_by_problem_id(self, problem_id):
        return self.db.query(ProblemTag).filter_by(problem_id = problem_id).all()
    def select_problem_order_by_id(self, count = 10, start = 0):
        return self.db.query(Problem).offset(start).limit(count).all()
    def select_visible_problem_order_by_id(self, count = 10, start = 0):
        return self.db.query(Problem).filter_by(invisible = 0).offset(start).limit(count).all()
    def select_latest_visible_problem_order_by_id(self, count = 10):
        return self.db.query(Problem).filter_by(invisible = 0).order_by(desc(Problem.id)).limit(count).all()
    def select_last_submit_by_problem_id_member_id(self, problem_id):
        return self.db.query(Submit).filter_by(problem_id = problem_id).filter_by(member_id = self.current_user.id).order_by(desc(Submit.id)).limit(1).one()
    def select_submit_by_id(self, sid):
        return self.db.query(Submit).get(sid)
    def select_submit_order_by_id(self, count = 10, start = 0):
        return self.db.query(Submit).order_by(desc(Submit.id)).offset(start).limit(count).all()
    def select_submit_by_member_id(self, member_id, count = 10):
        return self.db.query(Submit).filter_by(member_id = member_id).order_by(desc(Submit.id)).limit(count).all()
    def select_problem_by_tagname(self, tagname, count = 10, start = 0):
        return self.db.query(ProblemTag).filter_by(tagname = tagname).join(Problem).order_by(Problem.id).offset(start).limit(count)
    def select_visible_problem_by_tagname(self, tagname, count = 10, start = 0):
        return self.db.query(ProblemTag).filter_by(tagname = tagname).join(Problem).filter_by(invisible = 0).order_by(Problem.id).offset(start).limit(count)
    ''' INSERT '''
    def insert_problem(self, problem):
        problem.create = datetime.datetime.now()
        self.db.add(problem)
        self.db.commit()
    def insert_problem_tag(self, tagname, problem_id):
        problem_tag = ProblemTag()
        problem_tag.tagname = tagname
        problem_tag.problem_id = problem_id
        self.db.add(problem_tag)
        self.db.commit()
    def insert_submit(self, submit):
        submit.create = datetime.datetime.now()
        self.db.add(submit)
        self.db.commit()
    ''' UPDATE '''
    def update_problem(self, problem):
        db_problem = self.select_problem_by_id(problem.id)
        db_problem.title = problem.title
        db_problem.shortname = problem.shortname
        db_problem.content   = problem.content
        db_problem.timelimit = problem.timelimit
        db_problem.memlimit  = problem.memlimit
        db_problem.testpoint = problem.testpoint
        db_problem.invisible = problem.invisible
        self.db.commit()
    ''' DELETE '''
    def delete_problem_tag_by_problem_id(self, problem_id):
        self.db.query(ProblemTag).filter_by(problem_id = problem_id).delete()
    ''' OTHER '''

'''
'' ===================================
''          Contest Table 
'' ===================================
'''

class ContestDBMixin(object):
    ''' COUNT '''
    def count_contest(self):
        return self.db.query(Contest).count()
    def count_visible_contest(self):
        return self.db.query(Contest).filter_by(invisible = 0).count()
    ''' SELECT '''
    def select_contest_by_id(self, contest_id):
        return self.db.query(Contest).get(contest_id)
    def select_contest_problem_by_contest_id(self, contest_id):
        return self.db.query(ContestProblem).filter_by(contest_id = contest_id).all()
    def select_contest_submit_by_contest_id_problem_id_user_id(self, contest_id, problem_id):
        return self.db.query(ContestSubmit).filter_by(contest_id = contest_id).filter_by(problem_id = problem_id).filter_by(member_id = self.current_user.id).one()
    def select_contest(self, start = 0, count = 20):
        return self.db.query(Contest).order_by(desc(Contest.id)).offset(start).limit(count).all()
    def select_visible_contest(self, start = 0, count = 20):
        return self.db.query(Contest).filter_by(invisible = 0).order_by(desc(Contest.id)).offset(start).limit(count).all()
    ''' INSERT '''
    def insert_contest(self, contest):
        contest.create = datetime.datetime.now()
        self.db.add(contest)
        self.db.commit()
    def insert_contest_problem(self, contest_id, problem_id):
        contest_problem = ContestProblem()
        contest_problem.contest_id = contest_id
        contest_problem.problem_id = problem_id
        self.db.add(contest_problem)
        self.db.commit()
    ''' UPDATE '''
    def update_contest(self, contest):
        db_contest = self.select_contest_by_id(contest_id)
        db_contest.title       = contest.title
        db_contest.description = contest.description
        db_contest.start_time  = contest.start_time
        db_contest.end_time    = contest.end_time
        db_contest.invisible   = contest.invisible
        self.db.commit()
    ''' DELETE '''
    def delete_contest_problem_by_contest_id(self, contest_id):
        self.db.query(ContestProblem).filter_by(contest_id = contest_id).delete()
    ''' OTHER '''

class JudgerDBMixin(object):
    ''' SELECT '''
    def select_judgers(self):
        return self.db.query(Judger).all()
    def select_judger_by_id(self, judger_id):
        return self.db.query(Judger).get(judger_id)
    def select_judger_by_queue(self):
        return self.db.query(Judger).order_by(Judger.queue_num, Judger.priority).one()
    ''' INSERT '''
    def insert_judger(self, judger):
        judger.create = datetime.datetime.now()
        self.db.add(judger)
        self.commit()
    ''' UPDATE '''
    def update_judger(self, judger):
        db_judger = self.select_judger_by_id(judger.id)
        db_judger.name        = judger.name
        db_judger.description = judger.description
        db_judger.path        = judger.path
        db_judger.priority    = judger.priority
        db_judger.pubkey      = judger.pubkey
        self.db.commit()
    def update_judger_count(self, judger):
        db_judger = self.select_judger_by_id(Judger.id)
        db_judger.queue_num = 0
        self.db.commit()
