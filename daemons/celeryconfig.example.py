# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: celeryconfig.py
# CREATED: 02:26:56 17/03/2012
# MODIFIED: 02:58:41 17/03/2012

CELERY_RESULT_BACKEND = "amqp"
CELERYD_CONCURRENCY = 1
BROKER_URL = "amqp://guest:guest@localhost:5672/"

CELERY_IMPORTS = ("tasks", )
