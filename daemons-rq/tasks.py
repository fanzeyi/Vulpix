# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: tasks.py
# CREATED: 02:27:12 17/03/2012
# MODIFIED: 02:20:05 09/06/2012

import os
import MySQLdb
import subprocess
from time import sleep
from MySQLdb import escape_string

from config import COMPILE_DIR
from config import TESTDATA_DIR
from config import CARETAKER_PATH

from config import MYSQL_DB
from config import MYSQL_HOST
from config import MYSQL_PORT
from config import MYSQL_USER
from config import MYSQL_PASS

STATUS_DICT = {
    "A" : 1, 
    "W" : 2, 
    "T" : 3, 
    "M" : 4, 
    "R" : 5, 
    "C" : 6, 
    "N" : 7, 
}
_e = lambda a: escape_string(str(a))

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
        code.write(query['code'].encode("utf-8"))
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

def _get_input_file(tp, shortname):
    with open(os.path.join(TESTDATA_DIR, shortname, shortname + str(tp+1) + ".in")) as input_data_p:
        input_data = input_data_p.read()
    with open(os.path.join(COMPILE_DIR, shortname + ".in"), "w") as input_data_p:
        input_data_p.write(input_data)

def _run(result, query, tp):
    shortname = query["shortname"]
    os.chdir(COMPILE_DIR)
    cmd = " ".join([CARETAKER_PATH, "--input=%s.in" % query["shortname"], \
                                    "--output=%s.out" % query["shortname"], \
                                    "--time=%s" % str(query["timelimit"]), \
                                    "--memory=%s" % str(query["memlimit"] * 1024), \
                                    "a.out"])
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutput,erroutput) = proc.communicate()
    testresult = ""
    wexit = 0
    time = 0
    memory = 0
    if proc.returncode:
        if proc.returncode == 251:
            testresult = "T" 
        elif proc.returncode == 252:
            testresult = "M"
        elif proc.returncode == 253:
            testresult = "R"
    else:
        wexit, time, memory = stdoutput.split("\n")[-2].split(" ")
        wexit = int(wexit)
        time = int(time)
        memory = int(memory)
        if wexit != 0:
            testresult = "W"
        else:
            # cmp output
            with open(os.path.join(TESTDATA_DIR, shortname, shortname + str(tp+1) + ".ans")) as answer_fp:
                answer = answer_fp.read()
            try:
                with open(os.path.join(COMPILE_DIR, shortname + ".out")) as prg_answer_fp:
                    prg_answer = prg_answer_fp.read()
            except IOError:
                testresult = "N"
            else:
                if _compare(answer, prg_answer):
                    testresult = "A"
                    result["score"] = result["score"] + 10
                else:
                    testresult = "W"
    result["testpoint"].append((testresult, time, memory))

def _compare(fout, fans):
    out = [line.strip() for line in fout if line.strip()]
    ans = [line.strip() for line in fans if line.strip()]
    return ans == out

def _get_status(testpoint):
    for tp in testpoint:
        if tp != "A":
            return STATUS_DICT[tp]
    return STATUS_DICT["A"]

def _return_result(result, query):
    # connect to server
    conn = MySQLdb.connect(host = MYSQL_HOST, user = MYSQL_USER, passwd = MYSQL_PASS, db = MYSQL_DB)
    cur = conn.cursor()
    testpoint = ""
    timecost = ""
    memorycost = ""
    totaltime = 0
    totalmemory = 0
    if result["compilesucc"] == 0:
        status = 6
    else:
        # update 
        testpoint = []
        timecost = []
        memorycost = []
        totaltime = 0
        totalmemory = 0
        for tp in result["testpoint"]:
            testpoint.append(tp[0])
            timecost.append(str(tp[1]))
            memorycost.append(str(tp[2]))
            totaltime = totaltime + tp[1]
            totalmemory = totalmemory + tp[2]
        testpoint = "".join(testpoint)
        timecost = ",".join(timecost)
        memorycost = ",".join(memorycost)
        status = _get_status(testpoint)
    cur.execute("""UPDATE `submit` SET `status` = %s, 
                                       `testpoint` = %s, 
                                       `testpoint_time` = %s, 
                                       `testpoint_memory` = %s, 
                                       `score` = %s, 
                                       `costtime` = %s, 
                                       `costmemory` = %s, 
                                       `msg` = %s 
                                   WHERE `id` = %s """, (_e(status), _e(testpoint), _e(timecost), _e(memorycost), \
                                                        _e(result["score"]), _e(totaltime), _e(totalmemory), \
                                                        _e(result["msg"]), _e(query["id"])))
    conn.commit()
    cur.close()

'''

Query String Format:

id - Required. Submit id.
code - Required. Code file content.
lang - Required. Code language. ( 1 - Pascal, 2 - C, 3 - C++ )
filename - Required. Code file filename.
shortname - Required. Problem shortname.
timelimit - Required. Problem time limit. (MB)
memlimit - Required. Problem memory limit.(ms)
testpoint - Required. Problem testpoint number.
sign - Signature.
time - For signature.

'''

def judge(query):
    result = {}
    _compile(result, query)
    if result["compilesucc"] == 0:
        result["score"] = 0
        _return_result(result, query)
    result["testpoint"] = []
    result["score"] = 0
    if result["compilesucc"]:
        for tp in range(query["testpoint"]):
            _get_input_file(tp, query["shortname"])
            _run(result, query, tp)
    _return_result(result, query)
    return 0

