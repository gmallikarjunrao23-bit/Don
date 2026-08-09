"""
OSINT 100X ULTIMATE — Configuration
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/osint.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
    }
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))
    CACHE_KEY_PREFIX = 'osint_'
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '10 per minute')
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_HEADERS_ENABLED = True
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', 'csrf-secret-key')
    
    # API
    API_URL = os.getenv('API_URL', 'https://sahil-33rd.onrender.com/api/leakpro')
    API_KEY = os.getenv('API_KEY', 'SAHILS')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    API_RETRIES = int(os.getenv('API_RETRIES', 3))
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', 2))
    
    # Branding
    SITE_NAME = os.getenv('SITE_NAME', 'OSINT 100X')
    DEVELOPER = os.getenv('DEVELOPER', '@DEVILHASHJ')
    VERSION = os.getenv('VERSION', '100X ULTIMATE')
    
    # UPI
    UPI_ID = os.getenv('UPI_ID', '9866583926@axl')
    BANK_NAME = os.getenv('BANK_NAME', 'Union Bank Of India')
    
    # Tiers
    TIERS = {
        'free': {
            'name': 'Free',
            'searches': 3,
            'price': 0,
            'color': '#6b7280',
            'badge': '🆓',
            'description': 'Basic access with limited searches'
        },
        'premium': {
            'name': 'Premium',
            'searches': 100,
            'price': 99,
            'color': '#7c3aed',
            'badge': '👑',
            'description': '100 searches per day'
        },
        'pro': {
            'name': 'Pro',
            'searches': -1,
            'price': 299,
            'color': '#06b6d4',
            'badge': '⚡',
            'description': 'Unlimited searches'
        },
        'enterprise': {
            'name': 'Enterprise',
            'searches': -1,
            'price': 999,
            'color': '#10b981',
            'badge': '🏢',
            'description': 'Full access + priority support'
        }
    }
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
