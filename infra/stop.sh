#!/usr/bin/env bash
# Stop hackathon infrastructure started with ./start.sh -d
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/infra.pid"

if [[ ! -f "$PID_FILE" ]]; then
    echo "No PID file found — services may not be running."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "Process $PID is not running. Cleaning up stale PID file."
    rm -f "$PID_FILE"
    exit 1
fi

echo "Stopping infrastructure (pid $PID)..."
kill -TERM "$PID"

# Wait for it to exit
for i in $(seq 1 10); do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "Stopped."
        exit 0
    fi
    sleep 1
done

echo "Still running after 10s, sending SIGKILL..."
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo "Killed."
