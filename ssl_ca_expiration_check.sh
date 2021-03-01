#!/bin/bash

# This check was written in response to the poorly communicated expiration
# of the 2016 PEM file required to make SSL-encrypted connections to Rackspace
# cloud databases, including MySQL and Redis (from Object Rocket).  This blew
# up on us in February 2021 when the 2016 PEM file was replaced with the 2021
# PEM file.
#
# The idea here is that we want to be able to get alerted about 4-6 weeks before
# the CA cert expires again, which will be in 5+ years and we won't remember
# it without an alert.  Then we can proactively reach out to Rackspace, maybe
# accept the new cert for 2026 before they switch over and not experience
# downtime.
#
# See:
# https://docs.objectrocket.com/redis_stunnel.html
# http://ssl.rackspaceclouddb.com/rackspace-ca-2021.pem
#

if [ $# -ne 1 ]; then
  echo "Usage: $0 </path/to/ca/certificate.pem>"
  exit 100
fi

CA_FILE=$1
NOW=$(TZ=UTC date '+%s')

CMD="openssl x509 -noout -in $CA_FILE -dates"
NOT_BEFORE=$($CMD | grep notBefore | sed 's/^not.*\=//')
NOT_AFTER=$($CMD | grep notAfter | sed 's/^not.*\=//')

NOT_BEFORE_AT=$(TZ=UTC date '+%s' --date "$NOT_BEFORE")
NOT_AFTER_AT=$(TZ=UTC date '+%s' --date "$NOT_AFTER")
NOT_BEFORE_LOCAL=$(date --date "$NOT_BEFORE")
NOT_AFTER_LOCAL=$(date --date "$NOT_AFTER")
NOT_BEFORE_IN=$(( $NOT_BEFORE_AT - $NOW ))
NOT_AFTER_IN=$(( $NOT_AFTER_AT - $NOW ))

echo "metric not_before string $NOT_BEFORE"
echo "metric not_before_local string $NOT_BEFORE_LOCAL"
echo "metric not_before_at uint64 $NOT_BEFORE_AT"
echo "metric not_before_in int32 $NOT_BEFORE_IN"
echo "metric now uint64 $NOW"
echo "metric not_after string $NOT_AFTER"
echo "metric not_after_local string $NOT_AFTER_LOCAL"
echo "metric not_after_at uint64 $NOT_AFTER_AT"
echo "metric not_after_in int32 $NOT_AFTER_IN"
exit 0
