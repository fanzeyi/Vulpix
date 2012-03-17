# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: config.py
# CREATED: 02:35:44 18/03/2012
# MODIFIED: 03:05:45 18/03/2012

import rsa

COMPILE_DIR  = ""
TESTDATA_DIR = ""
DAEMON_PORT = 8889

RSA_PRIVKEY_PATH = ""
RSA_PRIVKEY = ""

with open(RSA_PRIVKEY_PATH, "r") as rsafp:
    RSA_PRIVKEY = rsa.PrivateKey.load_pkcs1(rsafp.read())
