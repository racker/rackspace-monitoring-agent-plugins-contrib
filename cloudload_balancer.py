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

STATS = [
    {'key': 'incoming', 'ref': 'incomingTransfer', 'unit': 'int'},
    {'key': 'incoming_ssl', 'ref': 'incomingTransferSsl', 'unit': 'int'},
    {'key': 'outgoing', 'ref': 'outgoingTransfer', 'unit': 'int'},
    {'key': 'outgoing_ssl', 'ref': 'outgoingTransferSsl', 'unit': 'int'}
]


def check_usage(region):
    pyrax.settings.set('identity_type', 'rackspace')
    pyrax.set_credential_file(
        os.path.expanduser("~/.rackspace_cloud_credentials"),
        region=region)

    clb = pyrax.cloud_loadbalancers

    print 'status ok'

    for instance in clb.list():
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

        for stat in STATS:
            print 'metric %s.%s %s %s' % \
                (name, stat['key'], stat['unit'], usage[stat['ref']])

        online_nodes = 0
        offline_nodes = 0
        draining_nodes = 0
        total_nodes = len(nodes)

        for node in nodes:
            if node.status == 'ONLINE':
                online_nodes = online_nodes + 1
            elif node.status == 'OFFLINE':
                offline_nodes = offline_nodes + 1
            elif node.status == 'DRAINING':
                draining_nodes = draining_nodes + 1

        print 'metric %s.total_nodes int %s' % (name, total_nodes)
        print 'metric %s.online_nodes int %s' % (name, online_nodes)
        print 'metric %s.offline_nodes int %s' % (name, offline_nodes)
        print 'metric %s.draining_nodes int %s' % (name, draining_nodes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("region", help="Cloud region, e.g. DFW or ORD")
    args = parser.parse_args()
    check_usage(args.region.upper())
