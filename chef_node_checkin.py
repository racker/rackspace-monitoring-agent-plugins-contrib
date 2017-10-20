#!/usr/bin/python
from datetime import datetime
import os


def PopulateMetrics(log):
    clientRuns = []
    logFile = open(log, 'r')
    for line in logFile:
        if 'INFO: Chef Run complete in' in line:
            date = line[1:11].split('-')
            time = line[12:20].split(':')
            clientRuns.append(datetime(int(date[0]), int(date[1]), int(
                date[2]), int(time[0]), int(time[1]), int(time[2]), 0))
            metrics['checkInDuration'] = int(float(line.split()[6]))

    metrics['timeSinceCheckIn'] = int(
        datetime.now().strftime('%s')) - int(
        sorted(clientRuns)[-1].strftime('%s')
    )

    metrics['processesAmount'] = 0
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        if 'chef-client' in open(os.path.join('/proc', pid, 'cmdline'), 'rb').read():
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
    print "status Warning {0}".format(err)

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
