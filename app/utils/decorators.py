"""
OSINT 100X ULTIMATE — Custom Decorators
"""

from functools import wraps
from flask import request, jsonify, session, flash, redirect, url_for, current_app
from app import limiter, cache
import time

rate_limit_store = {}
RATE_LIMIT = 10

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('auth.login'))
        if not session.get('is_admin', False):
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

def rate_limit_check(f):
    """Simple IP-based rate limiting"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method != 'POST':
            return f(*args, **kwargs)
        
        ip = request.remote_addr
        now = time.time()
        
        if ip in rate_limit_store:
            requests_list = [t for t in rate_limit_store[ip] if now - t < 60]
            if len(requests_list) >= RATE_LIMIT:
                return jsonify({'error': 'Rate limit exceeded. Please wait.'}), 429
            rate_limit_store[ip] = requests_list
        else:
            rate_limit_store[ip] = []
        
        rate_limit_store[ip].append(now)
        return f(*args, **kwargs)
    return decorated

def cache_response(timeout=3600):
    """Cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method != 'POST':
                return f(*args, **kwargs)
            
            data = request.get_json()
            if not data:
                return f(*args, **kwargs)
            
            query = data.get('query', '').strip()
            if not query:
                return f(*args, **kwargs)
            
            cache_key = f"{f.__name__}:{query}"
            cached = cache.get(cache_key)
            if cached:
                return jsonify(cached)
            
            result = f(*args, **kwargs)
            if result.status_code == 200:
                try:
                    cache.set(cache_key, result.get_json(), timeout=timeout)
                except:
                    pass
            
            return result
        return decorated
    return decorator

def log_request(f):
    """Log all requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_app.logger.info(f"📝 {request.method} {request.path} from {request.remote_addr}")
        return f(*args, **kwargs)
    return decorated

def handle_errors(f):
    """Global error handling for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error in {f.__name__}: {e}")
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('main.index'))
    return decorated
