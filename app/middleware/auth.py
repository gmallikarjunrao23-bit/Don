"""
OSINT 100X ULTIMATE — Auth Middleware
"""

from flask import request, session, jsonify
from functools import wraps

class AuthMiddleware:
    """Authentication middleware"""
    
    @staticmethod
    def validate_session():
        """Validate user session"""
        if 'user_id' in session:
            return True
        return False
    
    @staticmethod
    def require_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not AuthMiddleware.validate_session():
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated
