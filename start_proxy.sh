#!/bin/bash

# OpenAI Proxy Server Startup Script
# Usage: ./start_proxy.sh [--port PORT] [--host HOST] [--client CLIENT_IP]
# Options:
#   --port PORT        Port to run the server on (default: 8080)
#   --host HOST        Host to bind the server to (default: 0.0.0.0)
#   --client CLIENT_IP Only allow connections from this specific IP address
#   --help             Show this help message

# Default configuration
DEFAULT_PORT=8080
DEFAULT_HOST="0.0.0.0"
DEFAULT_CLIENT_IP=""

# Parse command line arguments first (before any other processing)
PORT=$DEFAULT_PORT
HOST=$DEFAULT_HOST
CLIENT_IP=$DEFAULT_CLIENT_IP

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --client)
            CLIENT_IP="$2"
            shift 2
            ;;
        --help)
            echo "OpenAI Proxy Server Startup Script"
            echo "Usage: $0 [--port PORT] [--host HOST] [--client CLIENT_IP]"
            echo ""
            echo "Options:"
            echo "  --port PORT        Port to run the server on (default: $DEFAULT_PORT)"
            echo "  --host HOST        Host to bind the server to (default: $DEFAULT_HOST)"
            echo "  --client CLIENT_IP Only allow connections from this specific IP address"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Use all defaults"
            echo "  $0 --port 3001                       # Custom port"
            echo "  $0 --client 192.168.1.100            # IP restriction only"
            echo "  $0 --port 8080 --client 10.0.0.50    # Custom port with IP restriction"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

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

echo ""
echo -e "${GREEN}Starting proxy server...${NC}"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Target: https://api.openai.com"
if [ -n "$CLIENT_IP" ]; then
    echo "Allowed client IP: $CLIENT_IP"
else
    echo "Allowed client IP: All IPs (no restriction)"
fi
echo ""
echo -e "${YELLOW}Your Vite config should use: http://<this-server-ip>:$PORT${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================="

# Start the proxy server with or without client IP restriction
if [ -n "$CLIENT_IP" ]; then
    python3 proxy_server.py --host "$HOST" --port "$PORT" --client "$CLIENT_IP"
else
    python3 proxy_server.py --host "$HOST" --port "$PORT"
fi
