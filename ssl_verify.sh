#!/bin/bash

# Verifies that a given remote host / port has a valid SSL certificate.
#
# Usage:
#   ssl_verify.sh HOST PORT
#
# This is really written to make sure that using SSL for cloud databases
# will work. See:
# * https://docs.rackspace.com/docs/cloud-databases/v1/general-api-info/using-ssl/
# * http://ssl.rackspaceclouddb.com/rackspace-ca-2021.pem
#
# On Ubuntu machines, this means that the CA file(s) in
# `/etc/ssl/certs/ca-certificates.crt` should be able to validate the SSL
# certificate.
#
# In order to setup the `rackspace-ca-2021.pem` file, you should
# place the `rackspace-ca-2021.pem` file in this folder
# `/usr/local/share/ca-certificates` and rename it to end in `.crt`. Then
# run `/usr/sbin/update-ca-certificates`

if [ $# -ne 1 ] && [ $# -ne 2 ] && [ $# -ne 3 ]; then
  echo "Usage: $0 <ip> [port] [ca_file]"
  exit 100
fi

HOST=$1

if [ $# -eq 2 ] || [ $# -eq 3 ]; then
  PORT=$2
else
  PORT=443
fi

if [ $# -eq 3 ]; then
  CA_FILE=$3
  RESULT=`echo | openssl s_client -connect $HOST:$PORT 2>/dev/null | openssl x509 | openssl verify -CAfile $CA_FILE 2>/dev/null | awk '{ gsub("stdin: ", "") ; print $0 }'`
else
  CA_FILE=''
  RESULT=`echo | openssl s_client -connect $HOST:$PORT 2>/dev/null | openssl x509 | openssl verify 2>/dev/null | awk '{ gsub("stdin: ", "") ; print $0 }'`
fi

echo "metric result string ${RESULT:-Error: No data}";
echo "metric host string ${HOST:-Error: No data}";
echo "metric port uint32 ${PORT:-Error: No data}";
echo "metric ca_file string ${CA_FILE:-Error: No data}";
exit 0
