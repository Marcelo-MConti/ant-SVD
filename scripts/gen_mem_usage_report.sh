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

mkfifo "$FIFO"

trap -- 'rm -f "$FIFO"' EXIT 

PYTHON=$(command -v python3 python | head -n 1)

"$PYTHON" -m src.ant_svd -x "$@" > "$FIFO" &
PYPID=$!

LOG=mem.$PYPID.log

echo "PID: $PYPID"

grep -m 1 -- ':::' < "$FIFO" && (
    cat < "$FIFO" >/dev/null &
    kill -USR1 $PYPID

    while [ -d /proc/$PYPID ]; do
        awk '/Private/{ sum += $2 } END { print sum }' /proc/$PYPID/smaps || break
        sleep 0.01
    done > "$LOG"

    wait
)

sed -i '/^$/d' "$LOG"

min=$(sort -h < "$LOG" | head -n 1)
max=$(sort -h < "$LOG" | tail -n 1)

echo "MIN: $min kB"
echo "MAX: $max kB"

echo "PEAK MEM USAGE: $((max - min)) kB"
