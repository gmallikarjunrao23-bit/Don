"""
OSINT 100X ULTIMATE — Analytics Service
"""

from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.search import SearchLog
from app.models.payment import Payment
from app.models.audit import AuditLog
from sqlalchemy import func

class AnalyticsService:
    """Service for dashboard analytics"""
    
    @staticmethod
    def get_dashboard_stats():
        """Get all dashboard statistics"""
        
        # User stats
        total_users = User.query.count()
        active_users = User.query.filter(User.is_active == True).count()
        premium_users = User.query.filter(User.tier != 'free').count()
        new_users_today = User.query.filter(
            User.created_at >= datetime.utcnow().date()
        ).count()
        
        # Search stats
        total_searches = SearchLog.query.count()
        searches_today = SearchLog.query.filter(
            SearchLog.created_at >= datetime.utcnow().date()
        ).count()
        total_records = db.session.query(func.sum(SearchLog.result_count)).scalar() or 0
        
        # Payment stats
        total_revenue = db.session.query(func.sum(Payment.amount))\
            .filter(Payment.status == 'approved').scalar() or 0
        pending_payments = Payment.query.filter_by(status='pending').count()
        total_payments = Payment.query.count()
        
        # Recent activity
        recent_logs = SearchLog.query\
            .order_by(SearchLog.created_at.desc())\
            .limit(10).all()
        
        # Daily trends (last 7 days)
        daily_trends = []
        for i in range(7):
            date = datetime.utcnow().date() - timedelta(days=i)
            count = SearchLog.query.filter(
                SearchLog.created_at >= date,
                SearchLog.created_at < date + timedelta(days=1)
            ).count()
            daily_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'searches': count
            })
        
        return {
            'users': {
                'total': total_users,
                'active': active_users,
                'premium': premium_users,
                'new_today': new_users_today
            },
            'searches': {
                'total': total_searches,
                'today': searches_today,
                'total_records': total_records
            },
            'payments': {
                'total': total_payments,
                'pending': pending_payments,
                'revenue': total_revenue
            },
            'daily_trends': daily_trends,
            'recent_activity': recent_logs
        }
    
    @staticmethod
    def get_user_analytics(user):
        """Get analytics for a specific user"""
        
        total_searches = SearchLog.query.filter_by(user_id=user.id).count()
        today = datetime.utcnow().date()
        today_searches = SearchLog.query.filter(
            SearchLog.user_id == user.id,
            SearchLog.created_at >= today
        ).count()
        
        total_payments = Payment.query.filter_by(user_id=user.id).count()
        pending_payments = Payment.query.filter_by(
            user_id=user.id,
            status='pending'
        ).count()
        
        total_records = db.session.query(func.sum(SearchLog.result_count))\
            .filter(SearchLog.user_id == user.id).scalar() or 0
        
        recent_searches = SearchLog.query\
            .filter_by(user_id=user.id)\
            .order_by(SearchLog.created_at.desc())\
            .limit(5).all()
        
        return {
            'total_searches': total_searches,
            'today_searches': today_searches,
            'total_records': total_records,
            'total_payments': total_payments,
            'pending_payments': pending_payments,
            'recent_searches': recent_searches,
            'tier': user.tier,
            'remaining_searches': user.get_remaining_searches()
          }
