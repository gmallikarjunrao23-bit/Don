"""
OSINT 100X ULTIMATE — Application Factory
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# EXTENSIONS
# ============================================================

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cache = Cache()

# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app(config_class=None):
    """Create and configure the Flask application"""
    
    app = Flask(__name__, instance_relative_config=True)
    
    if config_class:
        app.config.from_object(config_class)
    else:
        env = os.getenv('FLASK_ENV', 'production')
        if env == 'development':
            app.config.from_object('app.config.DevelopmentConfig')
        elif env == 'testing':
            app.config.from_object('app.config.TestingConfig')
        else:
            app.config.from_object('app.config.ProductionConfig')
    
    os.makedirs(app.instance_path, exist_ok=True)
    
    setup_logging(app)
    register_error_handlers(app)
    init_extensions(app)
    register_blueprints(app)
    
    with app.app_context():
        db.create_all()
    
    app.logger.info("🚀 OSINT 100X ULTIMATE started")
    return app

# ============================================================
# SETUP LOGGING
# ============================================================

def setup_logging(app):
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

# ============================================================
# INIT EXTENSIONS
# ============================================================

def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    migrate.init_app(app, db)
    cache.init_app(app)
    
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

# ============================================================
# REGISTER BLUEPRINTS
# ============================================================

def register_blueprints(app):
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.search import search_bp
    from app.blueprints.profile import profile_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.billing import billing_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(billing_bp, url_prefix='/billing')

# ============================================================
# REGISTER ERROR HANDLERS
# ============================================================

def register_error_handlers(app):
    
    @app.errorhandler(404)
    def not_found(e):
        app.logger.warning(f"404: {request.path}")
        return render_template('error.html', error='404', description='Page not found'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning(f"403: {request.path}")
        return render_template('error.html', error='403', description='Access forbidden'), 403
    
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"500: {e}")
        return render_template('error.html', error='500', description='Internal server error'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}")
        return render_template('error.html', error='500', description='An unexpected error occurred'), 500

# ============================================================
# IMPORT FOR ROUTES
# ============================================================

from flask import request
from datetime import datetime
