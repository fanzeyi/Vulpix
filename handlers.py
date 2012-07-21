# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: handlers.py
# CREATED: 01:41:06 08/03/2012
# MODIFIED: 20:28:26 18/04/2012
# DESCRIPTION: URL Route

from api import *
from home import *
from lang import *
from forum import *
from member import *
from problem import *
from contest import *
from backstage import *

'''
'' Handler 命名规范： [动宾结构 / 名词] + Handler
'''

handlers = [
    (r'/', HomeHandler), 
    (r'/signin', SigninHandler), 
    (r'/signup', SignupHandler), 
    (r'/signout', SignoutHandler), 
    (r'/settings', SettingsHandler), 
    (r'/settings/changepass', ChangePasswordHandler), 
    (r'/member', ListMemberHandler), 
    (r'/member/(.*)', MemberHandler), 
    (r'/lang/(.*)', SetLanguageHandler), 
    (r'/problem', ListProblemHandler), 
    (r'/problem/([\d]*)', ViewProblemHandler), 
    (r'/tag/(.*)', ViewTagHandler), 
    (r'/submit', ListSubmitHandler), 
    (r'/submit/(.*)', ViewSubmitHandler), 
    (r'/backstage/problem/add', AddProblemHandler), 
    (r'/backstage/contest/add', AddContestHandler), 
    (r'/backstage/node/add', AddNodeHandler), 
    (r'/backstage/judger', ManageJudgerHandler), 
    (r'/backstage/judger/add', AddJudgerHandler), 
    (r'/contest', ListContestHandlder), 
    (r'/contest/([\d]*)', ViewContestHandler), 
    (r'/go/(.*)', ViewNodeHandler), 
    (r'/t/([\d]*)', ViewTopicHandler), 
    (r'/new/(.*)', CreateTopicHandler), 
    (r'/forum', ViewForumHandler), 
    (r'/test', TestHandler), 
    (r'/api/problem/get/([\d]*)', GetProblemHandler), 
]
