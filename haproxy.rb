#!/usr/bin/env ruby
## Rackspace Cloud Monitoring Plug-In
## HAProxy Stats
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <lo@petalphile.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return
# ----------------------------------------------------------------------------
#
# haproxy.rb
#  - Takes HAProxy stats and grabs connections, rate, and check time
#    for every listener and every backend server, and prints it using
#    Rackspace Cloud Montioring metric lines
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['connections'] == 0) {
#   return new AlarmStatus(CRITICAL, 'No connections to your HAProxy!
#
# if (metric['connections'] < '10') {
#   return new AlarmStatus(WARNING, 'Less than 10 connections to your HAProxy!');
# }
#
# return new AlarmStatus(OK, 'HAProxy connections normal');
#
# Please note that you will need to adjust the thresholds based on workload.
# Also, there are other metrics this plugin reports you may find useful, but
# the metricnames for these will vary based on your HAProxy cluster name.
#

def fail(status="Unknown failure")
  puts "status #{status}"
  exit 1
end

def metric(name,type,value)
  @metrics[name] = {
    :type => type,
    :value => value
  }
end

def output_success
  puts "status HAProxy is running and reporting metrics"
  @metrics.each do |name,v|
    puts "metric #{name} #{v[:type]} #{v[:value]}"
  end
end

begin
  require 'optparse'
  require 'socket'
rescue
  fail "Failed to load required ruby gems"
end

@metrics = {}
options = {}

args = ARGV.dup

OptionParser.new do |o|
  o.banner = "Usage: #{$0} [options]"
  o.on('-s', '--stats-socket SOCKET', 'Specify the HAProxy stats socket') do |s|
    options[:sock] = s
  end
  o.on_tail('-h', '--help', 'Show this message') { puts o; exit }
  o.parse!(args)
end

fail "You must specify the haproxy stats socket" if options[:sock].nil?

pid = `pidof haproxy`.chomp.to_i || fail("HAProxy is not running")

# get global frontend stats
begin
  ctl=UNIXSocket.new(options[:sock])
  ctl.puts "show info"

  while (line = ctl.gets) do
    if (line =~ /^CurrConns:/)
      line = line.split(":")
      metric("connections","int", line[1].to_i)
    end
    if (line =~ /^ConnRate:/)
      line = line.split(":")
      metric("connection_rate","int", line[1].to_i)
    end
  end
  ctl.close
rescue
  fail "Problem reading global stats from #{options[:sock]}"
end

# get per-backend stats
# note that the current maximum number of metrics a plugin can submit is 30.
# if you have a lot of backends, you'll need to remove a metric or two in
# the list below.
begin
  ctl=UNIXSocket.new(options[:sock])
  ctl.puts "show stat"

  while (line = ctl.gets) do
    if (line =~ /^[^#]\w+/)
      line = line.split(",")
      host = "#{line[0]}_#{line[1]}".gsub('-', '_').gsub('.', '_')
      metric("#{host}_request_rate","int",line[47].to_i)
      metric("#{host}_total_requests","gauge",line[49].to_i)
      metric("#{host}_health_check_duration","int",line[35].to_i)
      metric("#{host}_current_queue","int",line[3].to_i)
    end
  end
  ctl.close
rescue
  fail "Problem reading backend stats from #{options[:sock]}"
end

output_success
