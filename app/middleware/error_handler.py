"""
OSINT 100X ULTIMATE — Error Handler Middleware
"""

import logging
import traceback
from flask import request, jsonify, render_template

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """Global error handler"""
    
    @staticmethod
    def handle_exception(e):
        """Handle any uncaught exception"""
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        
        if request.is_json:
            return jsonify({
                'error': 'An unexpected error occurred',
                'details': str(e) if app.debug else None
            }), 500
        
        return render_template('error.html', 
                             error='500', 
                             description='An unexpected error occurred'), 500
