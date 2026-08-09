"""
OSINT 100X ULTIMATE — Payment Model
"""

from datetime import datetime
from app import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer)
    tier = db.Column(db.String(20))
    transaction_id = db.Column(db.String(100), unique=True)
    screenshot_url = db.Column(db.String(500))
    upi_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    admin_notes = db.Column(db.Text)
    admin_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'
