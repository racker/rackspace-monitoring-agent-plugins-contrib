#!/usr/bin/env python2.7
"""
Copyright 2014 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
----

Rackspace Cloud Monitoring Plugin for Cloud Queues 

Retrieves Stats for number of unclaimed(free), claimed, and total messages in a given queue.
Useful for triggering Autoscale webhooks based on number os messages in a Cloud Queue.

Requires:
pyrax - https://github.com/rackspace/pyrax

Usage:
Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins

Setup a CLoud Monitoring Check of type agent.plugin to run
python ./cloud-queues.py <queueName>

Eg.
python ./cloud-queues.py myQueue

The following is an example 'criteria' for a Rackspace Monitoring Alarm:

if (metric['queue.free'] >= 100) {
 return new AlarmStatus(CRITICAL, 'over 100 msgs unclaimed msgs'
if (metric['queue.free'] >= '50') {
 return new AlarmStatus(WARNING, 'more than 60 unclaimed msgs');
}
return new AlarmStatus(OK, 'Less than 50 unclaimed msgs');

Please note that you will need to adjust the thresholds based on what works for you.

Available metrics are 
queue.claimed
queue.total
queue.free

"""
import os
import argparse
import pyrax

def get_queue_stats(queueName):
    
    pyrax.settings.set('identity_type', 'rackspace')
    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))

    try:
        cq = pyrax.queues
    except pyrax.exceptions.PyraxException:
        print 'status err Unable to get queue', queueName
        return

    try:
        stats = cq.get_stats(queueName)
        print 'status success'
    except pyrax.exceptions.NotFound:
        print 'status err Unable to get queue stats', queueName
        return
   
    for key,value in stats.items():
        if type(value) is int:
            print 'metric queue.%s int %s' % (key, value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("queueName", help="Cloud Queue name")
    args = parser.parse_args()
    get_queue_stats(args.queueName)

    
