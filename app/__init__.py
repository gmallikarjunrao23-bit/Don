from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import os
import logging
import requests
import re
import hashlib
import random
from functools import wraps

# ============================================================
# APP INIT
# ============================================================

app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/osint.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
limiter = Limiter(app, key_func=get_remote_address)

# ============================================================
# MODELS
# ============================================================

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    tier = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    total_searches = db.Column(db.Integer, default=0)
    searches_today = db.Column(db.Integer, default=0)
    last_search_date = db.Column(db.DateTime)
    premium_expiry = db.Column(db.DateTime)
    referral_code = db.Column(db.String(20), unique=True)
    searches = db.relationship('SearchLog', backref='user', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')

    def get_tier_info(self):
        tiers = {
            'free': {'name': 'Free', 'searches': 3, 'price': 0, 'color': '#6b7280', 'badge': '🆓'},
            'premium': {'name': 'Premium', 'searches': 100, 'price': 99, 'color': '#7c3aed', 'badge': '👑'},
            'pro': {'name': 'Pro', 'searches': -1, 'price': 299, 'color': '#06b6d4', 'badge': '⚡'},
            'enterprise': {'name': 'Enterprise', 'searches': -1, 'price': 999, 'color': '#10b981', 'badge': '🏢'}
        }
        return tiers.get(self.tier, tiers['free'])

    def can_search(self):
        limit = self.get_tier_info()['searches']
        return limit == -1 or self.searches_today < limit

class SearchLog(db.Model):
    __tablename__ = 'search_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query = db.Column(db.String(200), nullable=False)
    query_type = db.Column(db.String(20))
    result_count = db.Column(db.Integer, default=0)
    response_time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer)
    tier = db.Column(db.String(20))
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)

# ============================================================
# HELPERS
# ============================================================

def detect_type(query):
    if re.match(r'^\+?[0-9\s\-()]{7,20}$', query):
        return "phone"
    elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return "email"
    elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return "domain"
    else:
        return "username"

def get_emoji(field):
    f = field.lower()
    if 'phone' in f or 'mobile' in f: return '📱'
    if 'email' in f: return '✉️'
    if 'name' in f: return '📛'
    if 'address' in f or 'adres' in f: return '📍'
    if 'passport' in f or 'aadhar' in f or 'id' in f: return '🛂'
    if 'region' in f or 'state' in f: return '🗺️'
    if 'father' in f or 'mother' in f: return '👨'
    if 'username' in f: return '👤'
    if 'url' in f or 'link' in f: return '🔗'
    return '📌'

def get_platform_emoji(title):
    title_lower = title.lower()
    emoji_map = {
        'facebook': '📘', 'instagram': '📸', 'twitter': '🐦', 'linkedin': '💼',
        'github': '🐙', 'google': '🔴', 'microsoft': '🟦', 'apple': '🍎',
        'amazon': '🛒', 'netflix': '🎬', 'spotify': '🎵', 'youtube': '▶️',
        'reddit': '🤖', 'discord': '💬', 'telegram': '✈️', 'whatsapp': '💚'
    }
    for key, emoji in emoji_map.items():
        if key in title_lower:
            return emoji
    return '📢'

def process_api_data(raw_data):
    processed = []
    total_records = 0
    if not raw_data:
        return {'sources': [], 'total': 0}
    if 'data' in raw_data and isinstance(raw_data['data'], dict):
        raw_data = raw_data['data']
    for key, src in raw_data.items():
        if not src:
            continue
        title = src.get('title', key.replace('_', ' ').title())
        desc = src.get('description', '')
        records = src.get('records', [])
        if not records:
            records = src.get('record s', []) or src.get('record', [])
        platform_emoji = get_platform_emoji(title)
        pr = []
        for rec in records:
            if isinstance(rec, dict):
                fields = [{'key': k, 'value': str(v), 'emoji': get_emoji(k)} for k, v in rec.items() if v and str(v).strip()]
                if fields:
                    pr.append(fields)
                    total_records += len(fields)
            else:
                pr.append([{'key': 'data', 'value': str(rec), 'emoji': '📌'}])
                total_records += 1
        processed.append({
            'title': title,
            'description': desc[:500] + '...' if len(desc) > 500 else desc,
            'records': pr,
            'platform_emoji': platform_emoji
        })
    return {'sources': processed, 'total': total_records, 'total_sources': len(processed)}

def format_search_output(query, processed, response_time, api_owner=None, api_channel=None):
    output = {
        'success': True,
        'query': query,
        'type': detect_type(query),
        'response_time': response_time,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_sources': processed['total_sources'],
        'total_records': processed['total'],
        'sources': []
    }
    if api_owner:
        output['api_owner'] = api_owner
    if api_channel:
        output['api_channel'] = api_channel
    for src in processed['sources']:
        source_data = {
            'title': src['title'],
            'description': src['description'],
            'platform_emoji': src['platform_emoji'],
            'fields': [{'label': f['key'], 'value': f['value'], 'emoji': f['emoji']} for record in src['records'] for f in record]
        }
        output['sources'].append(source_data)
    return output

# ============================================================
# AUTH DECORATOR
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user_obj = User.query.filter_by(user_id=session['user_id']).first()
        if user_obj:
            user = {'email': user_obj.user_id, 'name': user_obj.full_name, 'tier': user_obj.tier}
    history = []
    if user:
        logs = SearchLog.query.filter_by(user_id=user_obj.id).order_by(SearchLog.created_at.desc()).limit(10).all()
        history = [{'query': l.query, 'type': detect_type(l.query), 'records': l.result_count, 'timestamp': l.created_at.strftime('%Y-%m-%d %H:%M:%S') if l.created_at else ''} for l in logs]
    return render_template('index.html', user=user, history=history, developer='@DEVILHASHJ', version='100X ULTIMATE')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        if not email or '@' not in email:
            flash('Please enter a valid email', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        if not full_name:
            flash('Please enter your full name', 'error')
            return render_template('register.html')
        if User.query.filter_by(user_id=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        hashed = generate_password_hash(password)
        ref_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
        new_user = User(user_id=email, password=hashed, full_name=full_name, referral_code=ref_code)
        db.session.add(new_user)
        db.session.commit()
        flash('✅ Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(user_id=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['user_name'] = user.full_name
            session['is_admin'] = user.is_admin
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome back, {user.full_name}! 👋', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user_obj = User.query.filter_by(user_id=session['user_id']).first()
    if not user_obj:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    total_searches = SearchLog.query.filter_by(user_id=user_obj.id).count()
    today = datetime.utcnow().date()
    today_searches = SearchLog.query.filter(SearchLog.user_id == user_obj.id, SearchLog.created_at >= today).count()
    user = {'email': user_obj.user_id, 'name': user_obj.full_name, 'tier': user_obj.tier, 'created_at': user_obj.created_at}
    return render_template('profile.html', user=user, total_searches=total_searches, today_searches=today_searches, developer='@DEVILHASHJ')

@app.route('/search', methods=['POST'])
@login_required
def search():
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({'error': 'Invalid query'}), 400
    query = data['query'].strip()
    if len(query) < 2 or len(query) > 200:
        return jsonify({'error': 'Query must be 2-200 characters'}), 400
    user_obj = User.query.filter_by(user_id=session['user_id']).first()
    if not user_obj:
        return jsonify({'error': 'User not found'}), 401
    if not user_obj.can_search():
        tier_info = user_obj.get_tier_info()
        return jsonify({'error': f'Daily limit reached ({tier_info["searches"]}). Upgrade to continue.', 'limit_reached': True}), 403
    # Call API
    API_URL = os.getenv('API_URL', 'https://sahil-33rd.onrender.com/api/leakpro')
    API_KEY = os.getenv('API_KEY', 'SAHILS')
    try:
        start = datetime.utcnow()
        resp = requests.get(API_URL, params={'key': API_KEY, 'number': query}, timeout=30)
        response_time = int((datetime.utcnow() - start).total_seconds() * 1000)
        if resp.status_code != 200:
            return jsonify({'error': f'API Error: {resp.status_code}'}), 500
        result = resp.json()
        raw_data = result.get('data', {})
        processed = process_api_data(raw_data)
        # Update user
        user_obj.searches_today += 1
        user_obj.total_searches += 1
        user_obj.last_search_date = datetime.utcnow()
        db.session.commit()
        # Log search
        log = SearchLog(user_id=user_obj.id, query=query, query_type=detect_type(query), result_count=processed['total'], response_time=response_time)
        db.session.add(log)
        db.session.commit()
        output = format_search_output(query, processed, response_time, result.get('owner'), result.get('channel'))
        output['remaining'] = user_obj.get_tier_info()['searches'] - user_obj.searches_today if user_obj.get_tier_info()['searches'] != -1 else '∞'
        output['tier'] = user_obj.tier
        return jsonify(output)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
@login_required
def history():
    user_obj = User.query.filter_by(user_id=session['user_id']).first()
    if not user_obj:
        return jsonify({'error': 'User not found'}), 401
    logs = SearchLog.query.filter_by(user_id=user_obj.id).order_by(SearchLog.created_at.desc()).limit(50).all()
    history = [{'query': l.query, 'type': detect_type(l.query), 'records': l.result_count, 'timestamp': l.created_at.strftime('%Y-%m-%d %H:%M:%S') if l.created_at else ''} for l in logs]
    return jsonify({'history': history})

@app.route('/clear_history', methods=['POST'])
@login_required
def clear_history():
    user_obj = User.query.filter_by(user_id=session['user_id']).first()
    if user_obj:
        SearchLog.query.filter_by(user_id=user_obj.id).delete()
        db.session.commit()
    return jsonify({'success': True})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': '100X ULTIMATE'})

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='404', description='Page not found'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error='500', description='Internal server error'), 500

# ============================================================
# CREATE TABLES
# ============================================================

with app.app_context():
    db.create_all()

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
