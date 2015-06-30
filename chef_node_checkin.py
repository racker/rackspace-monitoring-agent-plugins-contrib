#!/usr/bin/python
import re
from datetime import datetime, timedelta
import time
import os


def PopulateMetrics(log):
    clientRuns = []
    response = []
    logFile = open(log, 'r')
    for line in logFile:
        match = re.search('INFO: Chef Run complete in', line)
        if match:
            date = re.split('-|T|\+|\:', (line.split()[0])[1:][:-1])
            clientRuns.append(datetime(int(date[0]), int(date[1]), int(
                date[2]), int(date[3]), int(date[4]), int(date[5]), 0))
            checkInDuration = int(float(line.split()[6]))

    timeSinceCheckIn = int(
        datetime.now().strftime('%s')) - int(sorted(clientRuns)[-1].strftime('%s'))

    processesAmount = 0
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        match = re.search(
            'chef-client', open(os.path.join('/proc', pid, 'cmdline'), 'rb').read())
        if match:
            processesAmount += 1

    if timeSinceCheckIn > 86400:
        print "status Critcal node has not checked in for {0} seconds".format(timeSinceCheckIn)
    elif timeSinceCheckIn > 3600:
        print "status Warning node has not checked in for {0} seconds".format(timeSinceCheckIn)
    else:
        print "status OK node checked in {0} seconds ago".format(timeSinceCheckIn)


logfile = '/var/log/chef/client.log'

checkInDuration = 0
processesAmount = 0
timeSinceCheckIn = 0

try:
    PopulateMetrics(logfile)

# Anything OS related with file handling should warn and exit
except IOError as err:
    print "status Warning there was an error handling {0}".format(logfile)

# Handle the log regex not returning a poplated array meaning an
except IndexError:
    print "status OK node has not generated a parsable log"

except:
    print "status Warning unhandled error executing script"

# Print out even zero values to allow for REACH to show exported metrics
finally:
    print "metric timeSinceCheckIn int32", timeSinceCheckIn
    print "metric checkInDuration int32", checkInDuration
    print "metric numberOfClients int32", processesAmount
