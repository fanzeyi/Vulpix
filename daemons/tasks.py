# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: tasks.py
# CREATED: 02:27:12 17/03/2012
# MODIFIED: 03:02:01 18/03/2012

import os
import subprocess
from time import sleep
from celery.task import task

from config import COMPILE_DIR
from config import TESTDATA_DIR

def _clean(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            os.remove(os.path.join(root, name))

def _compile_cmd(lang, filename):
    lang = int(lang)
    if lang == 1:
        return "fpc %s -So -XS -v0 -O1 -o\"a.out\"" % filename
    elif lang == 2:
        return "gcc %s -lm -w -static -o a.out" % filename
    elif lang == 3:
        return "g++ %s -lm -static -o a.out" % filename

def _compile(result, query):
    _clean(COMPILE_DIR)
    os.chdir(COMPILE_DIR)
    with open(COMPILE_DIR + query['filename'], "w+") as code:
        code.write(query['code'])
    cmd = " ".join(["timeout 30", _compile_cmd(query['lang'], query['filename'])])
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutput,erroutput) = proc.communicate()
    result['msg'] = "".join(["STDOUT:\n--------\n", stdoutput, "\n--------\nSTDERR\n--------\n", erroutput])
    result['cmd'] = cmd
    if proc.returncode != 0:
        result["compilesucc"] = 0
    else:
        result["compilesucc"] = 1
    return result

def _run(result, query):
    pass

'''

Query String Format:

code - Required. Code file content.
lang - Required. Code language. ( 1 - Pascal, 2 - C, 3 - C++ )
filename - Required. Code file filename.
shortname - Required. Problem shortname.
timelimit - Required. Problem time limit. (MB)
memlimit - Required. Problem memory limit.(ms)

'''

@task
def judge(query):
    result = {}
    _compile(result, query)
    return 0
