#!/usr/bin/python
import re
from datetime import datetime, timedelta
import time
import os
import sys

if os.stat('/var/log/chef/client.log').st_size == 0:
    print "status OK node has not generated a client log"
    print "metric timeSinceCheckIn int32 0"
    print "metric checkInDuration int32 0"
    print "metric numberOfClients int32 0"
    sys.exit(0)

logFile = open('/var/log/chef/client.log', 'r')

clientRuns = []
response   = []

for line in logFile:
    match = re.search('INFO: Chef Run complete in', line)
    if match:
        date = re.split('-|T|\+|\:',(line.split()[0])[1:][:-1])
        clientRuns.append(datetime(int(date[0]),int(date[1]),int(date[2]),int(date[3]),int(date[4]), int(date[5]), 0))
        checkInDuration = int(float(line.split()[6]))


timeSinceCheckIn = int(datetime.now().strftime('%s')) - int(sorted(clientRuns)[-1].strftime('%s'))

processesAmount = 0

pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

for pid in pids:
  match = re.search('chef-client', open(os.path.join('/proc', pid, 'cmdline'), 'rb').read())
  if match:
    processesAmount += 1

if timeSinceCheckIn > 86400:
	print "status Critical node has not checked in for", timeSinceCheckIn, "seconds"
elif timeSinceCheckIn > 3600:
    print "status Warning node has not checked in for", timeSinceCheckIn, "seconds"
else:
	print "status OK node checked in", timeSinceCheckIn, "seconds ago"

print "metric timeSinceCheckIn int32", timeSinceCheckIn

print "metric checkInDuration int32", checkInDuration

print "metric numberOfClients int32", processesAmount
