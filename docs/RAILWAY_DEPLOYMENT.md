# Railway Deployment Guide

## Health Check Configuration

### 1. Health Check Server Implementation
The health check server is implemented in `twitter_api_bot.py` using Python's built-in `http.server`:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        # Suppress logging to avoid cluttering the logs
        pass

def start_healthcheck(port=8080):
    """Start health check server"""
    server = HTTPServer(('', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True  # This ensures the thread will be killed when main program exits
    thread.start()
    logger.info(f"Health check server started on port {port}")
```

### 2. Railway Configuration
In `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python twitter_api_bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. Procfile Configuration
In `Procfile`:
```
web: python twitter_api_bot.py
```

### 4. Implementation Details

1. **Threading**: The health check server runs in a separate daemon thread to avoid blocking the main bot process.

2. **Port Configuration**: Uses port 8080 by default, which is standard for Railway web services.

3. **Minimal Response**: Returns a simple "OK" response to keep the payload small and response time fast.

4. **Error Suppression**: Suppresses default HTTP server logging to avoid cluttering the application logs.

### 5. How It Works

1. When the bot starts, it launches a lightweight HTTP server in a separate thread
2. Railway periodically sends GET requests to the root path ('/')
3. The server responds with a 200 OK status and "OK" message
4. If Railway receives this response, it considers the service healthy
5. If no response or error response, Railway will attempt to restart the service

### 6. Troubleshooting

If health checks are failing:

1. Check if the bot process is running
2. Verify the health check server is started (look for "Health check server started" in logs)
3. Ensure port 8080 is not blocked or in use
4. Check Railway's service logs for any error messages

### 7. Best Practices

1. Keep the health check endpoint lightweight
2. Use daemon threads to ensure clean shutdown
3. Suppress unnecessary logging
4. Handle basic error cases
5. Use appropriate timeouts
