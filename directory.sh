#!/bin/sh
#
# Custom check for a directory presence and size (in Mbytes)
#
# if (metric['size'] < 0) {
#   return new AlarmStatus(CRITICAL, 'Directory #{dir} check failed - no such directory?');
# }
# if (metric['size'] > 500) {
#   return new AlarmStatus(WARNING, 'Directory #{dir} is #{size} Mbytes');
# }
# if (metric['size'] > 1000) {
#   return new AlarmStatus(CRITICAL, 'Directory #{dir} is #{size} Mbytes');
# }
#

if [ $# -ne 1 ]; then
    echo "Usage: $0 DIRECTORY"
    exit 100
fi

DIR=$1

size=-1
if [ ! -d $DIR ]; then
    status="err No such directory $DIR"
else
    status="ok directory $DIR found"
    size=`du -sm $DIR 2>/dev/null | awk '{print $1}'`
    if [ "X$size" = "X" ]; then
	size=-1
    fi
fi    
echo "status $status"
echo "metric dir string $DIR"
echo "metric size int $size"
