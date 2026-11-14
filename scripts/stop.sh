#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
PORT=8090
PID_FILE="$DIR/gateway.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping Ekhtizaly Core (PID $PID)..."
        kill -15 $PID 2>/dev/null || kill -9 $PID 2>/dev/null
    fi
    rm -f "$PID_FILE"
fi

# Fallback check on port
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Cleaning up lingering process on port $PORT..."
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null || true
fi

echo "Ekhtizaly Core stopped successfully."
