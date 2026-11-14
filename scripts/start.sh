#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT=8090
PID_FILE="$DIR/gateway.pid"

# Kill existing process on port 8090 if running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Port $PORT is already in use. Stopping existing instance..."
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null || true
    sleep 1
fi

echo "Starting Ekhtizaly Autonomous Core v2.0 on port $PORT..."
export PYTHONPATH="$DIR"

PYTHON_BIN="$DIR/venv/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

setsid "$PYTHON_BIN" -m uvicorn gateway.service_api:app --host 0.0.0.0 --port $PORT --workers 1 > "$DIR/gateway.log" 2>&1 < /dev/null &
NEW_PID=$!
sleep 2
echo $NEW_PID > "$PID_FILE"
echo "Ekhtizaly Core running with PID $NEW_PID."
echo "API Docs: http://127.0.0.1:$PORT/docs"
echo "Status:   http://127.0.0.1:$PORT/api/status"
