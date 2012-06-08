# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: daemons.py
# CREATED: 02:48:06 18/03/2012
# MODIFIED: 02:23:16 09/06/2012

import time
import hashlib
import logging
import simplejson as json
from rq import Queue
from rq import use_connection
from operator import itemgetter

import tornado.web
import tornado.ioloop
import tornado.options
from tornado.web import HTTPError

tornado.options.parse_command_line()

from tasks import judge
from config import SALT
from config import DAEMON_PORT

REQURED_ARGS = ["code", "lang", "filename", "shortname", "timelimit", "memlimit", "testpoint", "sign", "time"]
use_connection()

class ReceiveQueryHandler(tornado.web.RequestHandler):
    def post(self):
        query = self.get_argument("query", default = None)
        if not query:
            logging.error("Invalid Post Query.")
            raise HTTPError(404)
        query = json.loads(query)
        for key in REQURED_ARGS:
            if key not in query.keys():
                logging.error("Require key %s is missing" % key)
                raise HTTPError(404)
        query_sign = query["sign"]
        query.pop("sign")
        now = time.time()
        if abs(now - query["time"]) > 300:
            logging.error("Time is invalid!")
            raise HTTPError(404)
        query = dict(sorted(query.iteritems(), key=itemgetter(1)))
        sign = hashlib.sha1(json.dumps(query) + SALT).hexdigest()
        if not sign == query_sign:
            logging.error("Signature is invalid")
            raise HTTPError(404)
        q = Queue('judge')
        q.enqueue(judge, query)
        
application = tornado.web.Application([
    (r"/", ReceiveQueryHandler),
])

if __name__ == "__main__":
    application.listen(int(DAEMON_PORT))
    tornado.ioloop.IOLoop.instance().start()
