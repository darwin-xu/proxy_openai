#!/bin/bash

# OpenAI Proxy Server Startup Script

# Default configuration
DEFAULT_PORT=8080
DEFAULT_HOST="0.0.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}OpenAI Proxy Server Setup${NC}"
echo "================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}Dependencies installed successfully${NC}"
fi

# Get port from command line argument or use default
PORT=${1:-$DEFAULT_PORT}
HOST=${2:-$DEFAULT_HOST}

echo ""
echo -e "${GREEN}Starting proxy server...${NC}"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Target: https://api.openai.com"
echo ""
echo -e "${YELLOW}Your Vite config should use: http://<this-server-ip>:$PORT${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================="

# Start the proxy server
python3 proxy_server.py --host "$HOST" --port "$PORT"
