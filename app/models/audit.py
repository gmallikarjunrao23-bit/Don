"""
OSINT 100X ULTIMATE — AuditLog Model
"""

from datetime import datetime
from app import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(50))
    resource_id = db.Column(db.String(50))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'
