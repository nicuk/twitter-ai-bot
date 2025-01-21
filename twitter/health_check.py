"""Health check server for Railway deployment"""

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

def start_healthcheck(port=8080):
    """Start health check server"""
    try:
        server = HTTPServer(('', port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        logger.info(f"Health check server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start health check server: {e}")
        # Don't fail the whole bot if health check fails
        pass
