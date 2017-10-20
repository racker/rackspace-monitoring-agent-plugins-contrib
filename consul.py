#!/usr/bin/env python
#
# Script to return status and metrics for Consul
#
# Justin Phelps <justin.phelps@rackspace.com>
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Example alarm criteria:
#
# if (metric['node_count'] < 5) {
#   return new AlarmStatus(WARNING, 'Node Count is below 5.');
# }
#
# if (metric['node_count'] < 3) {
#   return new AlarmStatus(CRITICAL, 'Node Count is below 3.');
# }
#
# return new AlarmStatus(OK, 'Node Count is within range.');
#

import psutil
import json
import urllib2

def check_process_name(name):
    """Returns status of given process."""
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['name'])
        except psutil.NoSuchProcess:
            pass
        else:
            if pinfo['name'] == name:
                return 'status ok consul is running'
    return 'status error consul is not running'

def consul_http2json(url):
    """Returns data from the HTTP interface as a dict."""
    try:
        response = urllib2.urlopen(url)
    except urllib2.URLError:
        pass
    else:
        html = response.read()
        data = json.loads(html)
        return data

def consul_agent_type():
    """Returns the type of agent that is running."""
    try:
        agent_info = consul_http2json("http://localhost:8500/v1/agent/self?pretty=1")
        agent_type = agent_info['Config']['Server']
    except:
        return 'metric agent_type string unknown'
    else:
        if agent_type is True:
            return 'metric agent_type string server'
        else:
            return 'metric agent_type string client'

def consul_node_count():
    """Returns the number of consul nodes running as seen by this specific node."""
    try:
        nodes = consul_http2json("http://localhost:8500/v1/catalog/nodes?pretty=1")
        count = len(nodes)
    except:
        return 'metric node_count string unknown'
    else:
        return 'metric node_count int32 {0} nodes'.format(count)

def main():
    status = check_process_name("consul")
    print(status)
    agent_type = consul_agent_type()
    print(agent_type)
    node_count = consul_node_count()
    print(node_count)

if __name__ == '__main__':
    main()
