#!/bin/bash

# varnish4.sh
# Rackspace Cloud Monitoring Plugin to collect metrics from varnishstat.
#
# Copyright (c) 2013, Rob Szumski <rob@robszumski.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# check if service is running
SERVICE=varnish
VARNISHSTAT=/usr/bin/varnishstat
VARNISHADM=/usr/bin/varnishadm
HITSNAME=MAIN.cache_hit
MISSESNAME=MAIN.cache_miss

if P=$(pgrep $SERVICE | wc -l)
then
    echo "status success"
else
    echo "status down"
fi

# output number of processes
echo "metric processes int32 $P"

# calculate hit rate
# cache_hit/(cache_hit + cache_miss)
hits=$($VARNISHSTAT -1 -f $HITSNAME | awk '{print $2}')
misses=$($VARNISHSTAT -1 -f $MISSESNAME | awk '{print $2}')
hit_rate=$(echo "scale=8;($hits/($hits + $misses))" | bc | awk '{printf "%f", $1*100}')
echo "metric hit_rate double" $hit_rate

# calculate # of healthy backends
healthy=$($VARNISHADM backend.list | grep -c "Healthy")
echo "metric healthy_backends int32" $healthy

[ ! -z $1 ] && $VARNISHSTAT -1 -f $1 | awk ' { print "metric " $1 " gauge " $2 } '
