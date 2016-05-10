#!/usr/bin/env ruby
## Rackspace Cloud Monitoring Plug-In
## CMAN nodes check
#
# Author: James Turnbull
# Copyright (c) 2012 James Turnbull <james@lovedthanlost.net>
#
# MIT License:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['NODE_STATUS'] == 'X') {
#   return new AlarmStatus(CRITICAL, 'Host is not a member of the cluster!');
# }
#
# if (metric['NODE_STATUS'] < 'd') {
#   return new AlarmStatus(CRITICAL, 'Host is disallowed from cluster!');
# }
#
# return new AlarmStatus(OK, 'Host is a member of the cluster.');
#

# If the plugin fails in any way, print why and exit nonzero.
def fail(status="Unknown failure")
  puts "status #{status}"
  exit 1
end

# Store metrics in a hash and don't print them until we've completed
def metric(name,type,value)
  @metrics[name] = {
    :type => type,
    :value => value
  }
end

# Once the script has succeeded without errors, print metrics lines.
def output_success
  puts "status Cman node status for #{@hostname}"
  @metrics.each do |name,v|
    puts "metric #{name} #{v[:type]} #{v[:value]}"
  end
end

begin
  require 'optparse'
rescue
  fail "Failed to load required ruby gems!"
end

@metrics = {}
options = {}

args = ARGV.dup

OptionParser.new do |o|
  o.banner = "Usage: #{$0} [options]"
  o.on('-h', '--hostname HOSTNAME', 'Check status of node lid option') do |h| 
    options[:host] = h 
  end
  o.on_tail('-h', '--help', 'Show this message') { puts o; exit }
  o.parse!(args)
end

@hostname = options[:host] || `hostname -s`.chomp

begin
  node_status = `cman_tool nodes -n #{@hostname} -F type`
  metric("node_status","string","#{node_status}")
rescue => e
  fail "Problem running cman_tool plugin: #{e.message}"
end

output_success
