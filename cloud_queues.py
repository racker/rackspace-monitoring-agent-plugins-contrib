#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to provide cloud load balancer

Requirement:
pyrax - https://github.com/rackspace/pyrax

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

Use:
python ./cloud-queues.py <queueName> <region>

Eg.
python ./cloud-queues.py myQueue lon

"""
import os
import argparse
import pyrax
from pprint import pprint

def get_queue_stats(queueName, region):
    
    pyrax.settings.set('identity_type', 'rackspace')
    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"), region=region)

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
        print 'metric queue.%s int %s' % (key, value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("queueName", help="Cloud Queue name")
    parser.add_argument("region", help="Cloud region, e.g. DFW, ORD or LON")
    args = parser.parse_args()
    get_queue_stats(args.queueName, args.region.upper())

    
