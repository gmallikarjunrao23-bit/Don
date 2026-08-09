"""
OSINT 100X ULTIMATE — Validators
"""

import re

def validate_email(email):
    """Validate email address"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_password(password):
    """Validate password strength"""
    if not password or len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

def validate_name(name):
    """Validate full name"""
    if not name or len(name.strip()) < 2:
        return False
    return True

def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return False
    cleaned = re.sub(r'[\s\-()]', '', phone)
    return bool(re.match(r'^\+?[0-9]{7,15}$', cleaned))

def validate_query(query):
    """Validate search query"""
    if not query:
        return False
    query = query.strip()
    if len(query) < 2 or len(query) > 200:
        return False
    return True
