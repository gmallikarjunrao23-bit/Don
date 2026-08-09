"""
OSINT 100X ULTIMATE — Reset Database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def reset_db():
    app = create_app()
    with app.app_context():
        confirm = input("⚠️ This will delete all data. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cancelled")
            return
        
        db.drop_all()
        db.create_all()
        print("✅ Database reset successfully")

if __name__ == '__main__':
    reset_db()
