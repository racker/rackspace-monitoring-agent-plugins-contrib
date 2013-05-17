#!/usr/bin/env ruby
#
# example.rb
#  - A ruby example of a Rackspace Cloud Montioring Agent plugin

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
  puts "status Your new plugin is reporting metrics!"
  @metrics.each do |name,v|
    puts "#{name} #{v[:type]} #{v[:value]}"
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
  o.banner = "Usage: check_agent_public.rb [options]"
  o.on('-o', '--my-option OPTION', 'Set OPTION to be a valid option') do |s| 
    options[:option] = s 
  end
  o.on_tail('-h', '--help', 'Show this message') { puts o; exit }
  o.parse!(args)
end

# Error handling by option/input validation and begin;rescue;end is reccomended
if false
  fail "I checked to make sure this would succeed, and it didn't"
end

# Gather metrics using your own code here.
# Call metric(name,type,value) for every metric you want to record.

# Faking metrics for this example
metric("example","int64",40895)
metric("fake_http_code","string","500")

output_success
