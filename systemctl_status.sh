#!/bin/bash

# List of status codes:
# https://www.freedesktop.org/software/systemd/man/systemctl.html#is-system-running

STATE=$(systemctl is-system-running)
echo "status ok"
echo "metric systemctl_status string $STATE"

: <<EOF
# Example Alarm:
if (metric['systemctl_status'] != "running") {
  return new AlarmStatus(CRITICAL, 'SystemCTL status is #{systemctl_status}!');
}
return new AlarmStatus(OK, 'SystemCTL status is #{systemctl_status}');
EOF
