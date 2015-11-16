#!/usr/bin/python
#
# Rackspace Cloud Monitoring Plugin to read Galera metrics.
#
# Copyright (c) 2015, Javier Ayala <jayala@rackspace.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# USAGE;
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins, make executable
# and run like this:
#
# galera.py [OPTIONS]
#
# OPTIONS
#   -f PATH   Pass in the MySQL CNF file containing credentials (defaults to
#             /root/.raxmon.cnf). This should be a basic MySQL Options file
#             with a "[raxmon]" group containing at a minimum
#             the 'user' and 'password' options, and optionally the 'host',
#             'port', or 'unix_socket' options.
#
# Requires: Python 2.7+, mysql.connector, argparse, iniparse
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# Example 1:
# if (metric['wsrep_ready'] != 'ON') {
#   return new AlarmStatus(CRITICAL, 'Galera not ready on this node!');
# }
#
# return new AlarmStatus(OK, 'Galera Cluster OK');
#
# Example 2 (assuming a 3 node cluster):
# if (metric['wsrep_cluster_size'] < 2) {
#   return new AlarmStatus(CRITICAL, 'Galera Quorum Lost!');
# }
# if (metric['wsrep_cluster_size'] < 3) {
#   return new AlarmStatus(WARNING, 'Galera Node Dropped.');
# }
#
# return new AlarmStatus(OK, 'Galera Cluster OK');
#
#
import sys
import argparse
import mysql.connector
from iniparse import INIConfig
from iniparse.config import Undefined as iniparseUndefType

stats_to_inspect = {
    'wsrep_apply_window': 'double',
    'wsrep_causal_reads': 'int',
    'wsrep_cert_deps_distance': 'double',
    'wsrep_cert_interval': 'double',
    'wsrep_cluster_size': 'int',
    'wsrep_cluster_status': 'string',
    'wsrep_commit_window': 'double',
    'wsrep_flow_control_paused': 'double',
    'wsrep_gcache_pool_size': 'int64',
    'wsrep_local_bf_aborts': 'int',
    'wsrep_local_cert_failures': 'int',
    'wsrep_local_commits': 'int',
    'wsrep_local_recv_queue': 'int',
    'wsrep_local_replays': 'int',
    'wsrep_local_state': 'int',
    'wsrep_local_state_comment': 'string',
    'wsrep_protocol_version': 'int',
    'wsrep_ready': 'string',
    'wsrep_received': 'int',
    'wsrep_received_bytes': 'int64',
    'wsrep_repl_data_bytes': 'int64',
    'wsrep_repl_keys': 'int32',
    'wsrep_repl_keys_bytes': 'int32',
    'wsrep_repl_other_bytes': 'int32',
    'wsrep_replicated': 'int',
    'wsrep_replicated_bytes': 'int64',
}
"""
    stats_to_inspect: Contains a dictionary comprised of the stats that are
    gathered as a key, and their data types as a value.
"""

stats_units = {
    'wsrep_flow_control_paused': 'seconds',
    'wsrep_gcache_pool_size': 'bytes',
    'wsrep_received_bytes': 'bytes',
    'wsrep_repl_data_bytes': 'bytes',
    'wsrep_repl_keys_bytes': 'bytes',
    'wsrep_repl_other_bytes': 'bytes',
    'wsrep_replicated_bytes': 'bytes',
}
"""
    stat_units: Contains a dictionary comprised of the stats that have unit
    names as a key, and the unit names as a value.
"""


def parse_cfg(cfg):
    """
    Parses a MySQL config file looking for connection info for this plugin
    and returns a dict containing the parsed connection information.

    Args:
        cfg(str): String containing the path to the config file

    Returns:
        dict
    """
    mysqlcfg = {}
    try:
        cfgdata = INIConfig(open(cfg))
    except IOError as ioe:
        print "status err I/O error({0}): {1} {2}".format(ioe.errno,
                                                          ioe.strerror,
                                                          cfg)
        sys.exit(1)
    except Exception as e:
        raise
    for key in ['user', 'password', 'unix_socket', 'host', 'port']:
        try:
            if cfgdata.raxmon[key] != iniparseUndefType:
                mysqlcfg[key] = cfgdata.raxmon[key]
        except KeyError:
            pass
    return mysqlcfg


def list2dict(in_list):
    """
    Takes a row passed to it containing a key and a value and returns it as a
    dict.

    Args:
        in_list(list): list containing a key and value as a list, not a hash

    Returns:
        dict
    """
    if len(in_list) == 2:
        return {in_list[0]: in_list[1]}


def status2dict(raw_status):
    """
    Takes the status information retrieved from MySQL and returns it as a dict.

    Args:
        raw_status(list): Raw status response rows from the MySQL query

    Returns:
        dict
    """
    newdict = {}
    for row in raw_status:
        if row[0] in stats_to_inspect.iterkeys():
            newdict.update(list2dict(row))

    return newdict


def print_stats(stats):
    """
    Prints the stats information in a format that Rackspace Cloud Monitoring
    can consume.

    Args:
        stats(dict): dict containing the stat names and values
    """
    for key, val in stats.iteritems():
        if key in stats_units.iterkeys():
            print "metric %s %s %s %s" % (key, stats_to_inspect[key], val,
                                          stats_units[key])
        else:
            print "metric %s %s %s" % (key, stats_to_inspect[key], val)


def obtain_stats(args):
    """
    Connects to MySQL and retrieves the stats for Galera.

    Returns:
        dict of stats
    """
    cnx_setup = parse_cfg(args.config_file)
    try:
        cnx = mysql.connector.connect(**cnx_setup)
    except mysql.connector.ProgrammingError as e:
        print "status err Can't connect to MySQL({0}): {1}".format(e.errno,
                                                                   e.msg)
        sys.exit(2)

    cursor = cnx.cursor()

    status_query = ("SHOW STATUS LIKE %s")
    wsrep_query = ("wsrep%",)

    cursor.execute(status_query, (wsrep_query))
    result = status2dict(cursor.fetchall())
    cursor.close()
    cnx.close()
    return result


def main():
    parsedesc = 'Gather Galera stats for Rackspace Cloud Monitoring'
    default_cnf = '/root/.raxmon.cnf'
    parser = argparse.ArgumentParser(description=parsedesc)
    parser.add_argument('-f', '--config-file', default=default_cnf)
    args = parser.parse_args()
    try:
        final_stats = obtain_stats(args)
    except Exception as e:
        print "status Warning unhandled error executing script %s" % e
    print "status ok succeeded in obtaining galera metrics"
    print_stats(final_stats)


if __name__ == "__main__":
    main()
