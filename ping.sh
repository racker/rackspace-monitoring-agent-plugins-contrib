#/usr/sbin/env bash

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
