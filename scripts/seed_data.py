"""
OSINT 100X ULTIMATE — Seed Test Data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.search import SearchLog
from app.models.payment import Payment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_data():
    app = create_app()
    with app.app_context():
        # Create test user
        test_user = User.query.filter_by(user_id='test@example.com').first()
        if not test_user:
            test_user = User(
                user_id='test@example.com',
                password=generate_password_hash('Test1234'),
                full_name='Test User',
                referral_code='TEST123',
                tier='premium'
            )
            db.session.add(test_user)
            db.session.commit()
        
        # Create search logs
        queries = ['919494850232', 'john@gmail.com', '@testuser', 'example.com']
        for i in range(10):
            log = SearchLog(
                user_id=test_user.id,
                query=random.choice(queries),
                query_type='phone',
                result_count=random.randint(1, 10),
                response_time=random.randint(100, 1000),
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            db.session.add(log)
        
        # Create payment
        payment = Payment(
            user_id=test_user.id,
            amount=99,
            tier='premium',
            transaction_id='TXN' + str(random.randint(100000, 999999)),
            status='approved',
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add(payment)
        
        db.session.commit()
        print("✅ Test data seeded successfully")
        print(f"👤 Test user: test@example.com / Test1234")

if __name__ == '__main__':
    seed_data()
