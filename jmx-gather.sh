#!/bin/sh
#
# Rackspace Cloud Monitoring Plug-In
# Gathers JMX MBean attribute values from a specified ObjectName via a remote JMX RMI endpoint.
#
# (c) 2017 Geoff Bourne <geoff.bourne@rackspace.com>
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# It accepts three or more arguments:
# * host:port of the JMX RMI endpoint to access, such as "localhost:9080"
# * the MBean's ObjectName, such as "java.lang:type=Memory"
# * an attribute name of the MBean, such as "HeapMemoryUsage"
# * an attribute name...
#
# Returns a metric for each attribute that was found. Metrics are hardcoded to be typed as "gauge" since their
# originating type can vary and is dictated by the MBean accessed.
# NOTE:
# * if the MBean was not found, the status is reported "ok" with no metrics reported
# * if an attribute is not found on the given MBean that attribute's metric line is simply omitted

# Cleanup and setup our JavaScript code to run through Java's jrunscript
trap "rm -f /tmp/gather-mbean-$$.js" EXIT INT QUIT TSTP

cat > /tmp/gather-mbean-$$.js <<END
if (arguments.length < 3) {
  print("status err script requires hostPort objectName attribute...");
  exit(1);
}

var hostPort = arguments[0];
var objectName = arguments[1];
var attribute = arguments[2];

var u = new javax.management.remote.JMXServiceURL("service:jmx:rmi:///jndi/rmi://" + hostPort + "/jmxrmi");

var conn;

try {
conn = javax.management.remote.JMXConnectorFactory.connect(u);
} catch (e) {
  print("status err failed to connect to "+hostPort);
  exit(2);
}

var serverConn = conn.getMBeanServerConnection();

var name = new javax.management.ObjectName(objectName);

print("status ok retrieved JMX metrics");
for (i = 2; i < arguments.length; ++i) {
  var attribute = arguments[i];
  try {
    var value = serverConn.getAttribute(name, attribute);

    print("metric " + attribute + " gauge "+ value);
  } catch (e) {
    // attribute not found, no output
  }
}
END

# ...and run it
jrunscript -l js -f /tmp/gather-mbean-$$.js "$@"