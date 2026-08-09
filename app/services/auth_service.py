"""
OSINT 100X ULTIMATE — Auth Service
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from datetime import datetime
from flask import request, session
from app import db
from app.models.user import User
from app.models.audit import AuditLog
from app.utils.helpers import generate_referral_code
from app.utils.validators import validate_email, validate_password, validate_name
from app.exceptions import ValidationError, AuthenticationError

class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def register_user(email, password, full_name):
        """Register a new user with validation"""
        
        # Validate inputs
        if not validate_email(email):
            return {'success': False, 'error': 'Invalid email address'}
        
        if not validate_password(password):
            return {'success': False, 'error': 'Password must be at least 8 characters with letters and numbers'}
        
        if not validate_name(full_name):
            return {'success': False, 'error': 'Please enter a valid name'}
        
        # Check if user already exists
        existing = User.query.filter_by(user_id=email).first()
        if existing:
            return {'success': False, 'error': 'Email already registered'}
        
        # Create new user
        hashed_password = generate_password_hash(password)
        ref_code = generate_referral_code()
        
        user = User(
            user_id=email,
            password=hashed_password,
            full_name=full_name,
            referral_code=ref_code,
            last_ip=request.remote_addr,
            last_user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action='register',
            resource='user',
            resource_id=user.user_id,
            details=f"User registered: {user.full_name}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit)
        db.session.commit()
        
        return {'success': True, 'user': user}
    
    @staticmethod
    def login_user(email, password):
        """Login a user with validation"""
        
        user = User.query.filter_by(user_id=email).first()
        if not user:
            return {'success': False, 'error': 'Invalid credentials'}
        
        if not check_password_hash(user.password, password):
            return {'success': False, 'error': 'Invalid credentials'}
        
        if not user.is_active:
            return {'success': False, 'error': 'Account is disabled'}
        
        user.last_login = datetime.utcnow()
        user.last_ip = request.remote_addr
        user.last_user_agent = request.headers.get('User-Agent', '')
        db.session.commit()
        
        login_user(user, remember=True)
        session['user_id'] = user.user_id
        session['user_name'] = user.full_name
        session['is_admin'] = user.is_admin
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action='login',
            resource='user',
            resource_id=user.user_id,
            details=f"User logged in: {user.full_name}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit)
        db.session.commit()
        
        return {'success': True, 'user': user}
    
    @staticmethod
    def logout_user():
        """Logout a user"""
        user = User.query.filter_by(user_id=session.get('user_id')).first()
        if user:
            audit = AuditLog(
                user_id=user.id,
                action='logout',
                resource='user',
                resource_id=user.user_id,
                details=f"User logged out: {user.full_name}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(audit)
            db.session.commit()
        
        logout_user()
        session.clear()
        return {'success': True}
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(user_id=email).first()
