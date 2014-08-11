#! /usr/bin/env python

import socket
import httplib
import xml.etree.ElementTree

from pprint import pprint

def solr_ok(uri="localhost:8983"):
    try:
      c = httplib.HTTPConnection(uri)
      c.request("GET", "/solr/admin/ping")
      r = c.getresponse()
    except socket.error:
      return False
    if r.status == 200:
      return True
    else:
      return False


def solrstats(uri="localhost:8983"):
  solr_stats = {}
  try:
    c = httplib.HTTPConnection(uri)
    c.request("GET", "/solr/admin/system")
    r = c.getresponse()
    if r.status == 200:
     xmldoc = xml.etree.ElementTree.fromstring(r.read())
     uptime_elements = xmldoc.findall(".//*[@name='upTimeMS']")
    if len(uptime_elements) > 0:
      solr_stats['upTimeMS'] = uptime_elements[0].text
    else:
      pass
  except socket.error:
    pass

  try:
    c = httplib.HTTPConnection(uri)
    c.request("GET", "/solr/admin/luke")
    r = c.getresponse()
    if r.status == 200:
      xmldoc = xml.etree.ElementTree.fromstring(r.read())
      luke_elements = xmldoc.findall(".//*[@name='numDocs']")
    if len(luke_elements) > 0:
      solr_stats['numDocs'] = luke_elements[0].text
    else:
      pass
  except socket.error:
    pass

  return solr_stats


if __name__ == '__main__':
    if solr_ok():
        print "status OK solr responded to solr.PingRequestHandler query"
    else:
        print "status Critical solr failed to respond, or reported an error"

    solr_stats = solrstats()
    for stat in solr_stats.keys():
      print 'metric %s int64 %s' % (stat, solr_stats[stat])

