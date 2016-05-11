#/usr/sbin/env bash

target_host="$1"
ping_count=5
ping_stats=$(ping -q -w 30 -n -c ${ping_count} ${target_host} | tail -1)
min_ping="$(echo ${ping_stats} | sed -e "s#.\+= \([.0-9]\+\).\+#\\1#g")"
avg_ping="$(echo ${ping_stats} | cut -d'/' -f5)"
max_ping="$(echo ${ping_stats} | cut -d'/' -f6)"

if [ -n "$(echo "${avg_ping}" | grep "^[.0-9]\+$" -)" ]
    then
        echo "status ok"
        echo "metric time_connect double ${avg_ping} milliseconds"
    else
        echo "status error: ping probe fail"
        exit 1
fi
