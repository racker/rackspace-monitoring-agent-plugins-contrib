#!/usr/bin/env python
#
#
# usage: content_check.py [-h] [--timeout TIMEOUT] url pattern
#
# Rackspace Monitoring plugin to check a URL for a regular expression. Useful if
# the URL you need to check is not publicly accessible, but can be reached by
# another entity. Returns the metric 'found' with a value of 'yes' or 'no'.
#
# positional arguments:
#   url                url to check
#   pattern            regex to check for
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --timeout TIMEOUT  timeout in seconds (default 5)
#
#
# content_check.py - Rackspace Cloud Monitoring plugin
# Copyright (C) 2015  Carl George
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Rackspace Monitoring plugin to check a URL for a regular expression.  Useful
if the URL you need to check is not publicly accessible, but can be reached by
another entity.  Returns the metric 'found' with a value of 'yes' or 'no'.
"""


from __future__ import print_function

import argparse
import re

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('url', help='url to check')
parser.add_argument('pattern', help='regex to check for')
parser.add_argument('--timeout', type=int, default=5, help='timeout in seconds (default 5)')
args = parser.parse_args()

if not args.url.startswith('http'):
    args.url = 'http://{0}'.format(args.url)

try:
    request = urlopen(args.url, timeout=args.timeout)
    page = request.read().decode('utf-8')
except HTTPError as e:
    raise SystemExit('{0} {1} ({2})'.format(e.code, e.reason, args.url))

m = re.search(args.pattern, page)

if m:
    print('status ok\nmetric found string yes')
else:
    print('status err\nmetric found string no')
