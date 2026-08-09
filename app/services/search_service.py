"""
OSINT 100X ULTIMATE — Search Service
"""

from datetime import datetime
from flask import current_app, request
from app import db
from app.models.user import User
from app.models.search import SearchLog
from app.models.audit import AuditLog
from app.services.api_service import APIService
from app.utils.helpers import process_api_data, format_search_output, detect_type
from app.exceptions import SearchLimitError, APIServiceError

class SearchService:
    """Service for search operations"""
    
    @staticmethod
    def execute_search(user, query):
        """Execute a search query with full validation"""
        
        # Validate user
        if not user:
            return {'error': 'User not found', 'status': 401}
        
        # Check search limits
        if not user.can_search():
            tier_info = user.get_tier_info()
            return {
                'error': f'Daily limit reached ({tier_info["searches"]}). Upgrade to continue.',
                'limit_reached': True,
                'status': 403
            }
        
        # Validate query
        if not query or len(query.strip()) < 2:
            return {'error': 'Query too short. Minimum 2 characters.', 'status': 400}
        
        if len(query.strip()) > 200:
            return {'error': 'Query too long. Maximum 200 characters.', 'status': 400}
        
        query = query.strip()
        
        # Call API
        result = APIService.search(query)
        
        if 'error' in result:
            # Log error
            SearchService._log_search(user, query, 0, 0, result.get('status', 500), result.get('error'))
            return {'error': result['error'], 'status': result.get('status', 500)}
        
        api_data = result['data']
        response_time = result['response_time']
        
        # Process data
        raw_data = api_data.get('data', {})
        processed = process_api_data(raw_data)
        
        # Update user limits
        user.searches_today += 1
        user.total_searches += 1
        user.last_search_date = datetime.utcnow()
        db.session.commit()
        
        # Log search
        SearchService._log_search(
            user, 
            query, 
            processed['total'], 
            response_time, 
            200, 
            None
        )
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action='search',
            resource='leak_database',
            resource_id=query,
            details=f"Found {processed['total']} records in {response_time}ms",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit)
        db.session.commit()
        
        # Format output
        output = format_search_output(
            query,
            processed,
            response_time,
            api_data.get('owner'),
            api_data.get('channel')
        )
        
        # Add user tier info
        output['tier'] = user.tier
        output['remaining_searches'] = user.get_remaining_searches()
        output['total_searches'] = user.total_searches
        
        return output
    
    @staticmethod
    def _log_search(user, query, result_count, response_time, status, error):
        """Log search to database"""
        log = SearchLog(
            user_id=user.id,
            query=query,
            query_type=detect_type(query),
            result_count=result_count,
            response_time=response_time,
            api_status=status,
            error_message=error,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    
    @staticmethod
    def get_user_history(user, limit=50):
        """Get user's search history"""
        return SearchLog.query.filter_by(user_id=user.id)\
            .order_by(SearchLog.created_at.desc())\
            .limit(limit).all()
