# OpenAI Proxy Configuration
# Copy this file to config.py and modify as needed

# Server Configuration
SERVER_HOST = "0.0.0.0"  # Bind to all interfaces
SERVER_PORT = 8080       # Default port

# Target Configuration
OPENAI_API_BASE = "https://api.openai.com"

# Timeout Configuration (in seconds)
CLIENT_TIMEOUT_TOTAL = 300    # 5 minutes total timeout
CLIENT_TIMEOUT_CONNECT = 30   # 30 seconds connection timeout

# Connection Pool Configuration
CONNECTOR_LIMIT = 100         # Total connection pool size
CONNECTOR_LIMIT_PER_HOST = 30 # Connections per host
CONNECTOR_KEEPALIVE_TIMEOUT = 30  # Keep-alive timeout

# CORS Configuration
CORS_ALLOW_ORIGIN = "*"
CORS_ALLOW_METHODS = "GET, POST, PUT, DELETE, OPTIONS"
CORS_ALLOW_HEADERS = "*"
CORS_MAX_AGE = "86400"

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE = "proxy.log"
