"""
OSINT 100X ULTIMATE — Rate Limit Middleware
"""

import time
from flask import request, jsonify
from functools import wraps

class RateLimitMiddleware:
    """IP-based rate limiting middleware"""
    
    _requests = {}
    _limit = 10
    _window = 60
    
    @classmethod
    def check_limit(cls, key=None):
        """Check if request is within rate limit"""
        ip = key or request.remote_addr
        now = time.time()
        
        if ip not in cls._requests:
            cls._requests[ip] = []
        
        # Clean old requests
        cls._requests[ip] = [t for t in cls._requests[ip] if now - t < cls._window]
        
        if len(cls._requests[ip]) >= cls._limit:
            return False
        
        cls._requests[ip].append(now)
        return True
    
    @classmethod
    def limit(cls, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not cls.check_limit():
                if request.is_json:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                return 'Rate limit exceeded', 429
            return f(*args, **kwargs)
        return decorated
