#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin for elasticsearch cluster health
and node stats.

There are some questionable choices in modules (urllib2 vs requests,
optparse vs argparse). These questions can be answered by considering
compatability issues with older python versions like what we find stock
on Red Hat Enterprise Linux systems.

This plugin provides various groups of metrics.
* cluster-health gives an overview of the cluster status
* stats-store gives local node metrics about storing
* stats-index gives local node metrics about indexing
* stats-get gives local node metrics about gets
* stats-search gives local node metrics about searches
* stats-docs gives local node metrics about docs

Examples:
$ ./elasticsearch.py --stats-docs
$ ./elasticsearch.py -H http://localhost:9200 --cluster-health

This means you can call this plugin for up to 6 different checks for
various metrics groups about your elasticsearch cluster.

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


STATUS_OK = "status Elasticsearch returned a response"


def bug_out(why):
    '''Something went wrong. Tell the agent what, then die.'''

    print "status", why
    exit(1)


def call_to_cluster(host, path):
    '''Call a given path to the cluster and return JSON.'''

    try:
        r = urllib2.urlopen('{h}{p}'.format(h=host, p=path))
    except (urllib2.URLError, ValueError) as e:
        bug_out(e)

    try:
        response = json.loads(r.read())
    except Exception as e:  # improve this...
        bug_out(e)

    return response


def get_stats(host, keyname):
    '''Return a dict of stats from /_cluster/nodes/_local/stats.
    Keyname can be one of: docs, search, indexing, store, get'''

    h = call_to_cluster(host, '/_cluster/nodes/_local/stats')

    node_name = h['nodes'].keys()[0]
    stats = h['nodes'][node_name]['indices'][keyname]

    return stats


def cluster_health(option, opt, value, parser):
    '''Print metrics about /_cluster/health.'''

    h = call_to_cluster(parser.values.host, '/_cluster/health')

    print STATUS_OK
    print "metric status string", h['status']
    print "metric number_of_nodes uint32", h['number_of_nodes']
    print "metric unassigned_shards uint32", h['unassigned_shards']
    print "metric timed_out string", h['timed_out']
    print "metric active_primary_shards uint32", h['active_primary_shards']
    print "metric cluster_name string", h['cluster_name']
    print "metric relocating_shards uint32", h['relocating_shards']
    print "metric active_shards uint32", h['active_shards']
    print "metric initializing_shards uint32", h['initializing_shards']
    print "metric number_of_data_nodes uint32", h['number_of_data_nodes']


def stats_store(option, opt, value, parser):
    '''Print store metrics from /_cluster/nodes/_local/stats.'''

    s = get_stats(parser.values.host, 'store')

    print STATUS_OK
    print "metric size_in_bytes uint64", s['size_in_bytes']
    print "metric throttle_time_in_millis uint32", s['throttle_time_in_millis']


def stats_indexing(option, opt, value, parser):
    '''Print indexing metrics from /_cluster/nodes/_local/stats.'''

    s = get_stats(parser.values.host, 'indexing')

    print STATUS_OK
    print "metric delete_time_in_millis uint32", s['delete_time_in_millis']
    print "metric delete_total uint64", s['delete_total']
    print "metric delete_current uint32", s['delete_current']
    print "metric index_time_in_millis uint32", s['index_time_in_millis']
    print "metric index_total uint64", s['index_total']
    print "metric index_current uint32", s['index_current']


def stats_get(option, opt, value, parser):
    '''Print GET metrics from /_cluster/nodes/_local/stats.'''

    s = get_stats(parser.values.host, 'get')

    print STATUS_OK
    print "metric missing_total uint32", s['missing_total']
    print "metric exists_total uint32", s['exists_total']
    print "metric current uint32", s['current']
    print "metric time_in_millis uint32", s['time_in_millis']
    print "metric missing_time_in_millis", s['missing_time_in_millis']
    print "metric exists_time_in_millis", s['exists_time_in_millis']
    print "metric total uint32", s['total']


def stats_search(option, opt, value, parser):
    '''Print search metrics from /_cluster/nodes/_local/stats.'''

    s = get_stats(parser.values.host, 'search')

    print STATUS_OK
    print "metric query_total uint64", s['query_total']
    print "metric fetch_time_in_millis uint32", s['fetch_time_in_millis']
    print "metric fetch_total uint64", s['fetch_total']
    print "metric query_time_in_millis uint32", s['query_time_in_millis']
    print "metric open_contexts uint32", s['open_contexts']
    print "metric fetch_current uint32", s['fetch_current']
    print "metric query_current uint32", s['query_current']


def stats_docs(option, opt, value, parser):
    '''Print doc metrics from /_cluster/nodes/_local/stats.'''

    s = get_stats(parser.values.host, 'docs')

    print STATUS_OK
    print "metric count uint64", s['count']
    print "metric deleted uint32", s['deleted']


if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-H", "--host",
                      action="store", type="string", dest="host",
                      default="http://localhost:9200")

    mg = OptionGroup(parser, "Possible Metric Groups")
    mg.add_option("--cluster-health", action="callback",
                  callback=cluster_health)
    mg.add_option("--stats-store", action="callback",
                  callback=stats_store)
    mg.add_option("--stats-indexing", action="callback",
                  callback=stats_indexing)
    mg.add_option("--stats-get", action="callback",
                  callback=stats_get)
    mg.add_option("--stats-search", action="callback",
                  callback=stats_search)
    mg.add_option("--stats-docs", action="callback",
                  callback=stats_docs)

    parser.add_option_group(mg)
    (options, args) = parser.parse_args()
