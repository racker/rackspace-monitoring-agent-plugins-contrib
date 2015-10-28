#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: $0 <host> <port>"
  exit 100
fi

HOST=$1
PORT=$2

EXPIRATION_DATE=$(echo ""|openssl s_client -connect $HOST:$PORT 2>/dev/null | openssl x509 -noout -enddate | sed 's/^not.*\=//')

REMAINING_SECONDS=$(( $(date -u -d"$EXPIRATION_DATE" +%s) - $(date +%s) ))

echo "metric cert_end_in int ${REMAINING_SECONDS}"
