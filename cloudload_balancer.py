#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to provide cloud load balancer

Requirement:
pyrax - https://github.com/rackspace/pyrax

Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import argparse
import pyrax

USAGE_STATS = [
    {'key': 'incoming', 'ref': 'incomingTransfer', 'unit': 'int'},
    {'key': 'incoming_ssl', 'ref': 'incomingTransferSsl', 'unit': 'int'},
    {'key': 'outgoing', 'ref': 'outgoingTransfer', 'unit': 'int'},
    {'key': 'outgoing_ssl', 'ref': 'outgoingTransferSsl', 'unit': 'int'}
]


STATS = [
    {'key': 'connect_timeout', 'ref': 'connectTimeOut', 'unit': 'int'},
    {'key': 'connect_error', 'ref': 'connectError', 'unit': 'int'},
    {'key': 'connect_failure', 'ref': 'connectFailure', 'unit': 'int'},
    {'key': 'data_timed_out', 'ref': 'dataTimedOut', 'unit': 'int'},
    {'key': 'keep_alive_timed_out', 'ref': 'keepAliveTimedOut', 'unit': 'int'},
    {'key': 'max_conns', 'ref': 'maxConn', 'unit': 'int'}
]


def check_usage(instance_id, region):
    pyrax.settings.set('identity_type', 'rackspace')
    pyrax.set_credential_file(
        os.path.expanduser("~/.rackspace_cloud_credentials"),
        region=region)

    clb = pyrax.cloud_loadbalancers

    try:
        instance = clb.get(instance_id)
        print 'status ok'
    except pyrax.exceptions.NotFound:
        print 'status err Unable to find instance', instance_id
        return

    mgr = instance.manager
    status = instance.status
    nodes = instance.nodes
    name = instance.name.lower().replace('-', '_')
    usage = mgr.get_usage(instance)
    usage = usage['loadBalancerUsageRecords'][-1]

    if status == 'ACTIVE':
        print 'metric %s.status float 100.0' % (name)
    else:
        print 'metric %s.status float 0.0' % (name)

    for stat in USAGE_STATS:
        print 'metric %s.%s %s %s' % \
            (name, stat['key'], stat['unit'], usage[stat['ref']])

    online_nodes = 0
    offline_nodes = 0
    draining_nodes = 0
    total_nodes = len(nodes)

    for node in nodes:
        if node.status == 'ONLINE' and node.condition == 'ENABLED':
            online_nodes = online_nodes + 1
        if node.status == 'OFFLINE' or node.condition == 'DISABLED':
            offline_nodes = offline_nodes + 1
        if node.status == 'DRAINING' or node.condition == 'DRAINING':
            draining_nodes = draining_nodes + 1

    print 'metric %s.total_nodes int %s' % (name, total_nodes)
    print 'metric %s.online_nodes int %s' % (name, online_nodes)
    print 'metric %s.offline_nodes int %s' % (name, offline_nodes)
    print 'metric %s.draining_nodes int %s' % (name, draining_nodes)

    stats = mgr.get_stats(instance)
    for stat in STATS:
        print 'metric %s.%s %s %s' % \
            (name, stat['key'], stat['unit'], stats[stat['ref']])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("instance", help="Cloud Load Balancer instance id")
    parser.add_argument("region", help="Cloud region, e.g. DFW or ORD")
    args = parser.parse_args()
    check_usage(args.instance, args.region.upper())
