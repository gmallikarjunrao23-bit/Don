"""
OSINT 100X ULTIMATE — User Model
"""

from flask_login import UserMixin
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    tier = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    total_searches = db.Column(db.Integer, default=0)
    searches_today = db.Column(db.Integer, default=0)
    last_search_date = db.Column(db.DateTime)
    premium_expiry = db.Column(db.DateTime)
    referral_code = db.Column(db.String(20), unique=True)
    referred_by = db.Column(db.String(100))
    last_ip = db.Column(db.String(50))
    last_user_agent = db.Column(db.String(200))
    
    # Relationships
    searches = db.relationship('SearchLog', backref='user', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    audits = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def get_tier_info(self):
        from app.config import Config
        return Config.TIERS.get(self.tier, Config.TIERS['free'])
    
    def can_search(self):
        tier_info = self.get_tier_info()
        limit = tier_info['searches']
        if limit == -1:
            return True
        if self.searches_today >= limit:
            return False
        return True
    
    def get_remaining_searches(self):
        tier_info = self.get_tier_info()
        limit = tier_info['searches']
        if limit == -1:
            return float('inf')
        remaining = limit - self.searches_today
        return max(0, remaining)
    
    def is_premium(self):
        return self.tier in ['premium', 'pro', 'enterprise']
    
    def has_premium_expired(self):
        if not self.premium_expiry:
            return False
        return self.premium_expiry < datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.user_id}>'
