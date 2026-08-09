"""
OSINT 100X ULTIMATE — SearchLog Model
"""

from datetime import datetime
from app import db

class SearchLog(db.Model):
    __tablename__ = 'search_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query = db.Column(db.String(200), nullable=False)
    query_type = db.Column(db.String(20))
    result_count = db.Column(db.Integer, default=0)
    response_time = db.Column(db.Integer)
    api_status = db.Column(db.Integer)
    error_message = db.Column(db.String(500))
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchLog {self.query}>'
