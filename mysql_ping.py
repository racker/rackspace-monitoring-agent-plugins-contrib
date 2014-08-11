#!/usr/bin/env python
"""
Rackspace Cloud Monitoring Alert to verify MySQL server is running on system

does a 'mysqladmin ping' to determine if service is running
returns Status OK if service is alive, else Status ERROR.

NOTE: must have a /root/.my.cnf file with access to mysql

"""
import sys
import os

stat = os.popen('mysqladmin --defaults-file=/root/.my.cnf ping')
report = stat.read()

if report =="mysqld is alive\n":
    print "status ok ok"
    sys.exit(0)
else:
    print "status error"
    sys.exit(1)
