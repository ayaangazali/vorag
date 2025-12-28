#!/bin/bash
# VoRAG Backend Startup Script
# Kills any existing process on port 8000 and starts the backend

echo "🔍 Checking for processes on port 8000..."

# Kill any process using port 8000
PID=$(lsof -ti:8000)
if [ ! -z "$PID" ]; then
    echo "⚠️  Killing existing process (PID: $PID) on port 8000..."
    kill -9 $PID
    sleep 1
fi

echo "🚀 Starting VoRAG Backend..."

# Get the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

# Run the backend
python3 main.py
