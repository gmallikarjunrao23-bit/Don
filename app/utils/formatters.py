"""
OSINT 100X ULTIMATE — Premium Formatters
"""

from datetime import datetime

class PremiumFormatter:
    """Premium output formatter"""
    
    @staticmethod
    def format_source(source):
        """Format a single source"""
        return {
            'title': source.get('title', 'Unknown'),
            'description': source.get('description', '')[:500],
            'records': source.get('records', []),
            'count': len(source.get('records', []))
        }
    
    @staticmethod
    def format_record(record):
        """Format a single record"""
        if isinstance(record, dict):
            return {
                'fields': [
                    {'key': k, 'value': v} 
                    for k, v in record.items() 
                    if v and str(v).strip()
                ]
            }
        return {'value': str(record)}
    
    @staticmethod
    def format_timestamp(dt):
        """Format datetime"""
        if not dt:
            return 'N/A'
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def get_tier_badge(tier):
        """Get tier badge HTML"""
        badges = {
            'free': '🆓 Free',
            'premium': '👑 Premium',
            'pro': '⚡ Pro',
            'enterprise': '🏢 Enterprise'
        }
        return badges.get(tier, '🆓 Free')
    
    @staticmethod
    def get_tier_color(tier):
        """Get tier color"""
        colors = {
            'free': '#6b7280',
            'premium': '#7c3aed',
            'pro': '#06b6d4',
            'enterprise': '#10b981'
        }
        return colors.get(tier, '#6b7280')
