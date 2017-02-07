#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin for etcd node stats.

Example:
$ ./etcd.py --url http://localhost:4001

Example alarm criteria:

if (metric['state'] != 'follower' && metric['state'] != 'leader') {
  return new AlarmStatus(CRITICAL, 'Node is neither leader nor follower.');
}

if (metric['state'] == 'follower') {
  return new AlarmStatus(OK, 'Node is following #{leader}.');
}

if (metric['state'] == 'leader') {
  return new AlarmStatus(OK, 'Node is leading the cluster.');
}

Copyright 2014 Simon Vetter <simon.vetter@runbox.com>

Based on Victor Watkins' elasticsearch plugin:
Copyright 2013 Victor Watkins <vic.watkins@rackspace.com>

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
import urllib2
import json

from sys import exit
from optparse import OptionParser, OptionGroup


STATUS_OK = "status etcd returned a response"


def bug_out(why):
    '''Something went wrong. Tell the agent what, then die.'''

    print "status", why
    exit(1)


def call_to_server(url, path):
    '''Call a given path to the server and return JSON.'''

    try:
        r = urllib2.urlopen('{u}{p}'.format(u=url, p=path))
    except (urllib2.URLError, ValueError) as e:
        bug_out(e)

    try:
        response = json.loads(r.read())
    except Exception as e:  # improve this...
        bug_out(e)

    return response


def get_stats(url):
    '''Return a dict of stats from /v2/stats/self'''

    s = call_to_server(url, '/v2/stats/self')

    print STATUS_OK
    if not s['state']:
        s['state'] = 'leader'
    print "metric state string", s.get('state', 'unknown')
    print "metric leader string", s['leaderInfo']['leader']
    print "metric recvAppendRequestCnt uint64", s['recvAppendRequestCnt']
    print "metric sendAppendRequestCnt uint64", s['sendAppendRequestCnt']

    exit(0)


if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("--url",
                      action="store", type="string", dest="url",
                      default="http://localhost:4001")

    (options, args) = parser.parse_args()
    get_stats(parser.values.url);
