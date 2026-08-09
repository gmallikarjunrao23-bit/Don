"""
OSINT 100X ULTIMATE — Create Admin User
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admin():
    app = create_app()
    with app.app_context():
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        name = input("Enter admin name: ").strip()
        
        existing = User.query.filter_by(user_id=email).first()
        if existing:
            print(f"❌ User {email} already exists")
            return
        
        admin = User(
            user_id=email,
            password=generate_password_hash(password),
            full_name=name,
            is_admin=True,
            tier='enterprise',
            referral_code='ADMIN999'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin created: {email} / {password}")

if __name__ == '__main__':
    create_admin()
