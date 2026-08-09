"""
OSINT 100X ULTIMATE — Custom Exceptions
"""

class OSINTException(Exception):
    """Base exception for OSINT application"""
    pass

class AuthenticationError(OSINTException):
    """Authentication related errors"""
    pass

class AuthorizationError(OSINTException):
    """Authorization related errors"""
    pass

class RateLimitError(OSINTException):
    """Rate limit exceeded"""
    pass

class APIServiceError(OSINTException):
    """API service errors"""
    pass

class DatabaseError(OSINTException):
    """Database related errors"""
    pass

class ValidationError(OSINTException):
    """Input validation errors"""
    pass

class PaymentError(OSINTException):
    """Payment related errors"""
    pass

class SearchLimitError(OSINTException):
    """Search limit exceeded"""
    pass
