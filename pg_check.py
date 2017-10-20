#!/usr/bin/env python
#
# Simple PostgeSQL status check for Rackspace Cloud Monitoring
#
# (C)2014 Christopher Coffey <christopher.coffey@rackspace.com>
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
# Usage:
# Place file in the /usr/lib/rackspace-monitoring-agent/plugins/ directory
#
# No need to define specific custom alert criteria, Status ok is only acceptable
# response, All other responses trigger alert (default responses expected).
#
# SAMPLE monitoring-postgresql.yaml monitoring file to be placed in
# /etc/rackspace-monitoring-agent.conf.d/
# --------------------------------
# type: agent.plugin
# label: postgresql status
# period: 300
# timeout: 30
# details:
#   file: pg_check.py
#

import sys
import os

stat = os.popen('pg_isready')
report = stat.read()

if report.find("accepting connections") != -1:
    print "status ok"
    sys.exit(0)
else:
    print "status error"
    sys.exit(1)
