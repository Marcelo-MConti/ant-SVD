#!/bin/sh
#
# Generates memory usage reports for ant-SVD.
#
# At first, we tried using Heaptrack, but we found no easy
# way to isolate the memory usage for the SVD step only.
#
# This script uses a trace hook built into the program
# to start tracing it only after any unrelated buffers
# have been deallocated, but before the SVD procedure
# starts, and traces it until it returns.
#
# The values in the log output are measured in kB.
#
# Usage: ./scripts/gen_mem_usage_report.sh <ARGS TO ANT-SVD>...

set -e

FIFO=$(mktemp -u)
LOG=$(mktemp -u)

mkfifo "$FIFO"

trap -- 'rm -f "$FIFO" "$LOG"' EXIT 

PYTHON=$(command -v python3 python | head -n 1)

"$PYTHON" -m src.ant_svd -x "$@" > "$FIFO" &
PYPID=$!

echo "$PYPID"

grep -m 1 -- ':::' < "$FIFO" && (
    while [ -d /proc/$PYPID ]; do
        awk '/Private/{ sum += $2 } END { print sum }' /proc/$PYPID/smaps
        sleep 0.01
    done > "$LOG"
)

baseline=$(head -n 1 "$LOG")
at_start=1

while read -r measurement; do
    # Last line may be empty
    [ -z "$measurement" ] && break
    
    [ $measurement -ne $baseline ] && unset at_start
    [ -z "$at_start" ] && echo "$((measurement - baseline))"
done < "$LOG" > mem.$PYPID.log
