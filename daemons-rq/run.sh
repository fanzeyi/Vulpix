#!/bin/bash
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: run.sh
# CREATED: 02:25:51 09/06/2012
# MODIFIED: 18:17:17 09/06/2012

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

if [ "$(ps -A | grep redis-server | wc -l)" == "0" ]; then
    echo "Redis Server is not running!" 1>&2
    exit 1
fi

rqworker judge 2>&1 >> judge.log &
python2 daemons.py 2>&1 >> daemons.log &
