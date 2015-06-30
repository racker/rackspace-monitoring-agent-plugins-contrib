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
            metrics['checkInDuration'] = int(float(line.split()[6]))

    metrics['timeSinceCheckIn'] = int(
        datetime.now().strftime('%s')) - int(
        sorted(clientRuns)[-1].strftime('%s')
    )

    metrics['processesAmount'] = 0
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        match = re.search(
            'chef-client',
            open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        )
        if match:
            metrics['processesAmount'] += 1

    if metrics['timeSinceCheckIn'] > 86400:
        print "status Critcal node has not checked in for {0} seconds".format(
            metrics['timeSinceCheckIn']
        )
    elif metrics['timeSinceCheckIn'] > 3600:
        print "status Warning node has not checked in for {0} seconds".format(
            metrics['timeSinceCheckIn']
        )
    else:
        print "status OK node checked in {0} seconds ago".format(
            metrics['timeSinceCheckIn']
        )
    return metrics


logfile = '/var/log/chef/client.log'
metrics = {'timeSinceCheckIn': 0, 'checkInDuration': 0, 'processesAmount': 0}

try:
    metrics = PopulateMetrics(logfile)

# Anything OS related with file handling should warn and exit
except IOError as err:
    print "status Warning there was an error handling {0}".format(err)

# Handle the log regex not returning a poplated array
except IndexError:
    print "status OK node has not generated a parsable log"

except:
    print "status Warning unhandled error executing script"

# Always print out metrics to allow REACH to report metrics
finally:
    print "metric timeSinceCheckIn int32", metrics['timeSinceCheckIn']
    print "metric checkInDuration int32",  metrics['checkInDuration']
    print "metric numberOfClients int32",  metrics['processesAmount']
