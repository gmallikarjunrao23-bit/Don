"""
OSINT 100X ULTIMATE — Logging Middleware
"""

import time
import logging
from flask import request
from functools import wraps

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    """Request/response logging middleware"""
    
    @staticmethod
    def log_request(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            start_time = time.time()
            
            # Log request
            logger.info(f"→ {request.method} {request.path} from {request.remote_addr}")
            
            response = f(*args, **kwargs)
            
            # Log response
            duration = int((time.time() - start_time) * 1000)
            logger.info(f"← {request.method} {request.path} → {response.status_code} ({duration}ms)")
            
            return response
        return decorated
