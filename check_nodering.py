#! /usr/bin/python

from subprocess import check_output
import sys
import argparse

parser = argparse.ArgumentParser(description='Run nodetool to check for inconsistent state')
parser.add_argument('-p', '--port', dest='portforcassandra',
                    default='9080', help='port that cassandra is running on')
parser.add_argument('-t', '--tool', dest='pathtonodetool',
                    default='/opt/cassandra/bin/',
                    help='path to nodetool executable (ex /opt/cassandra/bin)')
parser.add_argument('-o', '--host', dest='cassandrahost',
                    default='localhost', help='host cassandra is running on.')

args = parser.parse_args()

nodetooloutput = check_output([args.pathtonodetool + '/nodetool', '-h',
                               args.cassandrahost, '-p', args.portforcassandra, 'ring'])

if nodetooloutput.find('?') >= 0:
  print 'status critical nodering not consistent, find out which nodes have the "?" status'
  sys.exit(2)
else:
  print 'status ok nodering consistent'.exit(0)
