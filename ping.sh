#/usr/sbin/env bash
: <<'DESCRIPTION'

Rackspace Cloud Monitoring Plug-In
This is a plugin to monitor ICMP response times of hosts accessible by the server

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<zoltan.ver@gmail.com> wrote this file.  As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

Usage:
- Place plug-in in folder /usr/lib/rackspace-monitoring-agent/plugins
- Ensure that it is executable
  chmod +x ping.sh
- Configure Custom Plugin type check in Rackspace Intelligence
  Specify only the script's name and the required parameter(s), e.g.:
  ping.sh 192.168.0.1
- Configure an Alert (optional, see example below)

This plugin returns 4 metrics:
  - minimum, average, maximum: statistics returned by the GNU ping utility
    in the format "round-trip min/avg/max/stddev = 9.429/35.460/79.698/27.657 ms"
  - lost_packets : the percentage of the packets lost out of the number of probes
    sent (specifiied by ping_count or the -c command paramter)

Example alert:

--- start copying after this line ---

if (metric['average'] >= 15.0) {
    return new AlarmStatus(CRITICAL, 'Average round-trip takes #{average}ms');
}
if (metric['lost_packets'] >= 30) {
    return new AlarmStatus(CRITICAL, 'Packet loss is #{lost_packets}%');
}
if (metric['legacy_state'] != "ok") {
    return new AlarmStatus(WARNING, 'Error: #{legacy_state}');
}
return new AlarmStatus(OK, 'All good');

--- stop copying before this line ---

DESCRIPTION

target_host="$1"
ping_count=5
ping_stats=$(ping -q -w 30 -n -c ${ping_count} ${target_host} 2>&1 | tail -2)
min_ping="$(echo ${ping_stats} | sed -e "s#.\+= \([.0-9]\+\).\+#\\1#g")"
avg_ping="$(echo ${ping_stats} | cut -d'/' -f5)"
max_ping="$(echo ${ping_stats} | cut -d'/' -f6)"
loss_percent="$(echo ${ping_stats} | sed -e "s#.\+ \([0-9]\+\)%.\+#\1#")"

if [ -n "$(echo "${avg_ping}" | grep "^[.0-9]\+$" -)" ]
    then
        echo "status ok"
        echo "metric minimum double ${min_ping} milliseconds"
        echo "metric average double ${avg_ping} milliseconds"
        echo "metric maximum double ${max_ping} milliseconds"
        echo "metric lost_packets int32 ${loss_percent} percent"
    else
        echo "status error: ping probe fail"
	exit 1
fi
