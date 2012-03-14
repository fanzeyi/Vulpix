# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: handlers.py
# CREATED: 01:41:06 08/03/2012
# MODIFIED: 02:52:56 15/03/2012
# DESCRIPTION: URL Route

from home import *
from lang import *
from member import *
from backstage import *

'''
'' Handler 命名规范： [动宾结构 / 名词] + Handler
'''

handlers = [
    (r'/', HomeHandler), 
    (r'/signin', SigninHandler), 
    (r'/signup', SignupHandler), 
    (r'/signout', SignoutHandler), 
    (r'/lang/(.*)', SetLanguageHandler), 
    (r'/backstage/problem/add', AddProblemHandler), 
]
