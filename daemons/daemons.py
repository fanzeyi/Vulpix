# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: daemons.py
# CREATED: 02:48:06 18/03/2012
# MODIFIED: 02:59:28 18/03/2012

import rsa
import simplejson

import tornado.web
import tornado.ioloop
from tornado.web import HTTPError

from tasks import judge
from config import DAEMON_PORT
from config import RSA_PRIVKEY

REQURED_ARGS = ["code", "lang", "filename", "shortname", "timelimit", "memlimit"]

class ReceiveQueryHandler(tornado.web.RequestHandler):
    def post(self):
        query = self.get_argument("query", default = None)
        if not query:
            raise HTTPError(404)
        try:
            query = rsa.decrypt(query, RSA_PRIVKEY)
        except:
            raise HTTPError(404)
        query = simplejson.loads(query)
        for key in REQURED_ARGS:
            if key not in query.keys():
                raise HTTPError(404)
        judge.delay(query)
        
application = tornado.web.Application([
    (r"/", ReceiveQueryHandler),
])

if __name__ == "__main__":
    application.listen(int(DAEMON_PORT))
    tornado.ioloop.IOLoop.instance().start()
