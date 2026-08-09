"""
OSINT 100X ULTIMATE — Helper Functions
"""

import re
import hashlib
import random
from datetime import datetime

def detect_type(query):
    """Detect query type: phone, email, domain, or username"""
    query = query.strip()
    if re.match(r'^\+?[0-9\s\-()]{7,20}$', query):
        return "phone"
    elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return "email"
    elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return "domain"
    else:
        return "username"

def get_emoji(field):
    """Get emoji for field type"""
    f = field.lower()
    if 'phone' in f or 'mobile' in f:
        return '📱'
    if 'email' in f:
        return '✉️'
    if 'name' in f:
        return '📛'
    if 'address' in f or 'adres' in f:
        return '📍'
    if 'passport' in f or 'aadhar' in f or 'id' in f:
        return '🛂'
    if 'region' in f or 'state' in f:
        return '🗺️'
    if 'father' in f or 'mother' in f:
        return '👨'
    if 'username' in f:
        return '👤'
    if 'url' in f or 'link' in f:
        return '🔗'
    return '📌'

def get_platform_emoji(title):
    """Get platform-specific emoji"""
    title_lower = title.lower()
    emoji_map = {
        'facebook': '📘', 'instagram': '📸', 'twitter': '🐦', 'linkedin': '💼',
        'github': '🐙', 'google': '🔴', 'microsoft': '🟦', 'apple': '🍎',
        'amazon': '🛒', 'netflix': '🎬', 'spotify': '🎵', 'youtube': '▶️',
        'reddit': '🤖', 'discord': '💬', 'telegram': '✈️', 'whatsapp': '💚',
        'signal': '🔵', 'tiktok': '🎵', 'snapchat': '👻', 'pinterest': '📌',
        'vimeo': '🎥', 'flickr': '📷', 'imgur': '🖼️', 'deviantart': '🎨',
        'medium': '📝', 'substack': '📧', 'quora': '❓', 'stackoverflow': '📚',
        'gitlab': '🦊', 'bitbucket': '🔷', 'docker': '🐳', 'heroku': '⚡',
        'netlify': '🚀', 'vercel': '▲', 'cloudflare': '☁️'
    }
    for key, emoji in emoji_map.items():
        if key in title_lower:
            return emoji
    return '📢'

def process_api_data(raw_data):
    """Process raw API data into structured format"""
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
                fields = []
                for k, v in rec.items():
                    if v and str(v).strip():
                        fields.append({
                            'key': k,
                            'value': str(v),
                            'emoji': get_emoji(k)
                        })
                if fields:
                    pr.append(fields)
                    total_records += len(fields)
            else:
                pr.append([{
                    'key': 'data',
                    'value': str(rec),
                    'emoji': '📌'
                }])
                total_records += 1
        
        processed.append({
            'title': title,
            'description': desc[:500] + '...' if len(desc) > 500 else desc,
            'records': pr,
            'platform_emoji': platform_emoji
        })
    
    return {
        'sources': processed,
        'total': total_records,
        'total_sources': len(processed)
    }

def format_search_output(query, processed, response_time, api_owner=None, api_channel=None):
    """Format search results for API response"""
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
            'fields': []
        }
        for record in src['records']:
            for field in record:
                source_data['fields'].append({
                    'label': field['key'],
                    'value': field['value'],
                    'emoji': field['emoji']
                })
        output['sources'].append(source_data)
    
    return output

def generate_cache_key(query):
    """Generate cache key for a query"""
    return hashlib.md5(f"{query}".encode()).hexdigest()

def generate_referral_code():
    """Generate unique referral code"""
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
