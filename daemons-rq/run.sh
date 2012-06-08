#!/bin/bash
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: run.sh
# CREATED: 02:25:51 09/06/2012
# MODIFIED: 02:31:16 09/06/2012


rqworker judge 2>&1 >> judge.log &
python2 daemons.py 2>&1 >> daemons.log &
