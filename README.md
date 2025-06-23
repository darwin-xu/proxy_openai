# OpenAI API Proxy Server

This is a Python-based HTTP proxy server that forwards requests from your local development environment to the OpenAI API. It's designed to work around network connectivity issues where your lab environment cannot directly reach OpenAI's servers.

## Features

- **Async HTTP Proxy**: High-performance asynchronous proxy using aiohttp
- **Full Request Forwarding**: Preserves all headers, request body, and HTTP methods
- **CORS Support**: Handles browser CORS preflight requests automatically
- **Client IP Restriction**: Optional restriction to allow connections only from specific IP addresses
- **Logging**: Comprehensive logging to both console and file
- **Error Handling**: Robust error handling with meaningful error messages
- **Configurable**: Command-line arguments and environment variable support

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Start the Proxy Server

**Option A: Using the startup script (recommended)**
```bash
# Basic usage
./start_proxy.sh [port] [host] [client_ip]

# Examples
./start_proxy.sh                    # Default: port 8080, host 0.0.0.0, no IP restriction
./start_proxy.sh 3001               # Port 3001, host 0.0.0.0, no IP restriction  
./start_proxy.sh 8080 127.0.0.1     # Port 8080, host 127.0.0.1, no IP restriction
./start_proxy.sh 8080 0.0.0.0 192.168.1.100  # Port 8080, host 0.0.0.0, only allow 192.168.1.100
```

**Option B: Direct Python execution**
```bash
# Basic usage
python3 proxy_server.py --port 8080 --host 0.0.0.0

# With client IP restriction
python3 proxy_server.py --port 8080 --host 0.0.0.0 --client 192.168.1.100
```

### 3. Configure Your Vite Client

Update your `client/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  // ... other config
  server: {
    proxy: {
      '/openai': {
        target: 'http://<your-vps-ip>:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/openai/, ''),
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('proxy error', err);
          });
        }
      }
    }
  }
})
```

### 4. Update Your Client Code

Modify your client-side OpenAI API calls to use the proxy:

```javascript
// Before
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  // ... options
});

// After
const response = await fetch('/openai/v1/chat/completions', {
  // ... options
});
```

## Configuration

### Command Line Arguments

- `--port`: Port to run the server on (default: 8080)
- `--host`: Host to bind the server to (default: 0.0.0.0)
- `--client`: Only allow connections from this specific client IP address (optional)
- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Environment Variables

- `PROXY_PORT`: Port to run the proxy server on
- `PROXY_HOST`: Host to bind the server to

### Examples

```bash
# Run on port 3001
python3 proxy_server.py --port 3001

# Run on localhost only
python3 proxy_server.py --host 127.0.0.1

# Restrict to specific client IP
python3 proxy_server.py --client 192.168.1.50

# Combine multiple options
python3 proxy_server.py --port 3001 --host 127.0.0.1 --client 10.0.0.25

# Using environment variables
PROXY_PORT=3001 PROXY_HOST=127.0.0.1 python3 proxy_server.py
```

## How It Works

1. **Request Reception**: The proxy server receives HTTP requests from your Vite dev server
2. **Header Processing**: Removes hop-by-hop headers and preserves application headers
3. **Request Forwarding**: Forwards the request to `https://api.openai.com` with the original path, method, headers, and body
4. **Response Processing**: Receives the OpenAI response and adds necessary CORS headers
5. **Response Forwarding**: Sends the response back to your client

## Request Flow

```
[Your Browser/App] 
    ↓ (HTTP request to /openai/*)
[Vite Dev Server] 
    ↓ (proxies to VPS)
[VPS Proxy Server] 
    ↓ (forwards to https://api.openai.com/*)
[OpenAI API]
    ↓ (response)
[VPS Proxy Server] 
    ↓ (adds CORS headers)
[Vite Dev Server] 
    ↓ (returns response)
[Your Browser/App]
```

## Logging

The proxy server logs to both:
- **Console**: Real-time request/response information
- **File**: `proxy.log` for persistent logging

Log levels:
- `INFO`: Request/response summaries
- `DEBUG`: Detailed header information (enable with logging config)
- `ERROR`: Error conditions and failures

## Security Considerations

- This proxy forwards all requests to OpenAI without authentication checks
- Ensure your VPS firewall only allows connections from trusted sources
- Consider adding API key validation if needed
- The proxy runs on all interfaces (0.0.0.0) by default - restrict if needed

## Security Features

### Client IP Restriction

The proxy server supports restricting access to specific client IP addresses using the `--client` parameter:

```bash
# Only allow connections from 192.168.1.100
python3 proxy_server.py --client 192.168.1.100
```

**How it works:**
- The server checks the client IP from the request headers and connection
- Supports `X-Forwarded-For` header for reverse proxy setups
- Supports `X-Real-IP` header for nginx configurations
- Falls back to the direct connection IP if no proxy headers are present
- Blocks all requests from non-matching IPs with a 403 Forbidden response

**Use cases:**
- Restrict proxy access to specific development machines
- Secure the proxy when deployed on a public server
- Prevent unauthorized usage of your OpenAI API key through the proxy

**Example with reverse proxy:**
```bash
# If using nginx with X-Real-IP header
python3 proxy_server.py --client 203.0.113.45
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if the proxy server is running
   - Verify the port and host configuration
   - Check firewall settings on your VPS

2. **CORS Errors**
   - The proxy automatically handles CORS headers
   - Ensure your Vite proxy configuration has `changeOrigin: true`

3. **Timeout Errors**
   - The proxy has a 5-minute timeout for requests
   - Check network connectivity between VPS and OpenAI

4. **SSL/TLS Issues**
   - The proxy uses HTTPS to connect to OpenAI
   - Ensure your VPS has updated CA certificates

### Debug Mode

To enable debug logging, modify the logging level in `proxy_server.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    # ... rest of config
)
```

## Requirements

- Python 3.7+
- aiohttp >= 3.8.0
- Network connectivity from VPS to api.openai.com

## License

This proxy server is provided as-is for development purposes.
