#!/bin/bash
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: runner.sh
# CREATED: 23:39:04 03/04/2012
# MODIFIED: 16:44:37 05/04/2012

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

python2 main.py 8080 >> main.log 2>&1 &
echo "Web Server is running: " $!
python2 daemons/daemons.py >> daemons.log 2>&1 &
echo "Judge Server is running: " $!
cd daemons && celeryd -l info -I tasks >> celery.log 2>&1 &
echo "Celery Server is running: " $!
