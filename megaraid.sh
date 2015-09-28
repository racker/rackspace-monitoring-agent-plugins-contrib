#!/bin/bash
# Rackspace Cloud Monitoring Plug-In
# megaraid plugin to query SMART status of drives attached to LSI megaraid or
# DELL PERC {3,700} raid controllers.
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <simon.vetter@runbox.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return
# ----------------------------------------------------------------------------
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# This plugin returns 5 metrics:
#   - failed    : the number of drives in failed state,
#   - prefail   : the number of drives in prefail state,
#   - unknown   : the number of drives for which the smart state could not
#                 be determined,
#   - ok        : the number of drives in OK state,
#   - report    : a string reporting the drive id, vendor, serial number
#                 as well as the smart state for non-ok drives.
#                 e.g. /dev/bus/0 -d megaraid,4 SEAGATE 6SL28GNF FAILED \
#                      ^controller & drive ids  ^vendor ^serial# ^state
#                 ( HARDWARE IMPENDING FAILURE GENERAL HARD DRIVE FAILURE [asc=5d, ascq=10] )
#                   ^SMART health status for this drive
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['failed'] != 0) {
#  return new AlarmStatus(CRITICAL, '#{failed} failed drive(s): #{report}');
# }
#
# if (metric['prefail'] != 0) {
#  return new AlarmStatus(WARNING, '#{prefail} prefail drive(s): #{report}');
# }
#
# if (metric['unknown'] != 0) {
#  return new AlarmStatus(WARNING, '#{unknown} unknown drive(s): #{report}');
# }
#
# return new AlarmStatus(OK, '#{ok} drive(s) OK');
#
# Things to keep in mind:
#   - this plugin needs a fairly recent version of smartmontools (tested OK with 6.2)
#     (apt-get install smartmontools) but does NOT need megacli.
#   - on big and loaded arrays, the plugin can take more than 10s (default agent plugin
#     timeout) to complete. Some disks are slower than others, not surprisingly.
#   - as of now, this plugin only checks individual drives and not the status of the
#     array as seen by the controller. I'd add it, but it seems hard to extract without
#     megacli which I'm trying to stay away from. If you know of a way, please let me
#     know.
#
#
SMARTCTL=$(which smartctl)

OK_CNT=0
PREFAIL_CNT=0
FAILED_CNT=0
UNKNOWN_CNT=0
REPORT=""

# discover all drives
DEVLIST=$(${SMARTCTL} --scan 2>/dev/null)
if [ $? -ne 0 ]
then
  echo status failed to perform drive discovery
  exit 1
fi

while read DEV
do
  STAT=$(${SMARTCTL} ${DEV} --info --health 2>/dev/null)
  STATRC=$?
  SHS=$(echo "${STAT}" | grep -i 'smart health status:' | cut -d':' -f2)
  DRIVE_ID=$(echo "${STAT}" | grep -iE '(vendor:|serial number:)' | cut -d':' -f2 | xargs)

  # Bit 3: SMART status check returned "DISK FAILING".
  if [ $((${STATRC} & (2**3))) -ne 0 ]; then
    ((FAILED_CNT++))
    REPORT="${REPORT} ${DEV} ${DRIVE_ID} FAILED (${SHS} ) "
  # Bit 4: We found prefail Attributes <= threshold.
  # Bit 5: SMART  status check returned "DISK OK" but we found that some (usage or prefail)
  # attributes have been <= threshold at some time in the past.
  elif [ $((${STATRC} & (2**4) | ${STATRC} & (2**5))) -ne 0 ]; then
    ((PREFAIL_CNT++))
    REPORT="${REPORT} ${DEV} ${DRIVE_ID} PREFAIL (${SHS} ) "
  # Anything else (drive open failed, smart command failed, etc.) maps to unknown to me
  elif [ ${STATRC} -ne 0 ]; then
    ((UNKNOWN_CNT++))
    REPORT="${REPORT} ${DEV} ${DRIVE_ID} UNKNOWN (${SHS} ) "
  else
    ((OK_CNT++))
  fi
# only care for /dev/bus devices. /dev/sd* are logical disks
# and do not respond to any SMART command.
done < <(echo "${DEVLIST}" | grep /dev/bus/ | cut -d'#' -f1)

if [ "z${REPORT}" == "z" ]; then
  REPORT="all drives OK"
fi

echo "status smart status retrieved"
echo "metric failed uint32 ${FAILED_CNT}"
echo "metric prefail uint32 ${PREFAIL_CNT}"
echo "metric unknown uint32 ${UNKNOWN_CNT}"
echo "metric ok uint32 ${OK_CNT}"
echo "metric report string ${REPORT}"

exit 0
