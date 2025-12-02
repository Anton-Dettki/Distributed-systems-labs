#!/bin/bash

# Script to start 4 servers in 4 different terminals
# Each server has ID 0-3 and ports 10000-10003

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f "bin/activate" ]; then
    VENV_ACTIVATE="source bin/activate && "
else
    VENV_ACTIVATE=""
fi

# Start server 0
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ${VENV_ACTIVATE}python3 SendToCoordinatorAndBackToServers_Main.py 0\""

# Start server 1
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ${VENV_ACTIVATE}python3 SendToCoordinatorAndBackToServers_Main.py 1\""

# Start server 2
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ${VENV_ACTIVATE}python3 SendToCoordinatorAndBackToServers_Main.py 2\""

# Start server 3
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ${VENV_ACTIVATE}python3 SendToCoordinatorAndBackToServers_Main.py 3\""

echo "Started 4 servers in separate terminals:"
echo "  Server 0 on port 10000"
echo "  Server 1 on port 10001"
echo "  Server 2 on port 10002"
echo "  Server 3 on port 10003"

