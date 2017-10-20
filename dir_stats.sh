#!/bin/bash
#
# Gather stats on the directory size, number of files and oldest file name

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e
TARGET="${1}"

if [ "z" = "z${TARGET}" ]
then
  echo "status err missing target argument"
  exit 1
fi

if [ ! -d ${TARGET} ]
then
  echo "status err ${TARGET} does not exist or is not a directory"
  exit 1
fi

SIZE="$(du -sm ${TARGET} | awk '{print $1}')"
NB_FILES="$(find ${TARGET} -type f | wc -l)"
if [ ${NB_FILES} -gt 0 ]
then
  OLDEST_FILE_STAT="$(find ${TARGET} -type f -printf "%T@ %p\n" | sort -n | head -n1)"
  OLDEST_FILE_NAME="$(echo ${OLDEST_FILE_STAT} | cut -d ' ' -f2)"
  OLDEST_FILE_MTIME="$(echo ${OLDEST_FILE_STAT} | cut -d ' ' -f1 | cut -d '.' -f1)"
  OLDEST_FILE_AGE=$((`date +%s`-${OLDEST_FILE_MTIME}))
else
  OLDEST_FILE_NAME='no_files'
  OLDEST_FILE_AGE=0
fi

echo "status ok target uses ${SIZE} MB in ${NB_FILES} files"
echo "metric total_size uint64 ${SIZE} megabytes"
echo "metric total_files uint64 ${NB_FILES} files"
echo "metric oldest_file_name string ${OLDEST_FILE_NAME}"
echo "metric oldest_file_age uint64 ${OLDEST_FILE_AGE} seconds"
