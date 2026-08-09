"""
OSINT 100X ULTIMATE — API Service
"""

import requests
import time
import logging
from flask import current_app
from app import cache
from app.exceptions import APIServiceError

logger = logging.getLogger(__name__)

class APIService:
    """Service for interacting with Leak API"""
    
    @staticmethod
    def search(query, retry_count=0):
        """Search query in leak database with retry logic"""
        
        api_url = current_app.config.get('API_URL')
        api_key = current_app.config.get('API_KEY')
        timeout = current_app.config.get('API_TIMEOUT', 30)
        max_retries = current_app.config.get('API_RETRIES', 3)
        retry_delay = current_app.config.get('API_RETRY_DELAY', 2)
        
        # Check cache
        cache_key = f"api:{query}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"📦 Cache hit: {query}")
            return cached
        
        try:
            start_time = time.time()
            
            response = requests.get(
                api_url,
                params={'key': api_key, 'number': query},
                timeout=timeout,
                headers={
                    'User-Agent': f'OSINT-100X/1.0 ({current_app.config.get("SITE_NAME")})',
                    'Accept': 'application/json'
                }
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 429:
                if retry_count < max_retries:
                    time.sleep(retry_delay * (retry_count + 1))
                    return APIService.search(query, retry_count + 1)
                return {'error': 'Rate limit exceeded', 'status': 429}
            
            if response.status_code != 200:
                error_msg = f'API Error: {response.status_code}'
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    error_msg = response.text[:200] if response.text else error_msg
                return {'error': error_msg, 'status': response.status_code}
            
            result = response.json()
            
            # Cache successful results
            cache.set(cache_key, result, timeout=3600)
            
            return {
                'data': result,
                'response_time': response_time,
                'status': response.status_code
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout for {query}")
            if retry_count < max_retries:
                time.sleep(retry_delay)
                return APIService.search(query, retry_count + 1)
            return {'error': 'Request timeout', 'status': 504}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {query}")
            if retry_count < max_retries:
                time.sleep(retry_delay)
                return APIService.search(query, retry_count + 1)
            return {'error': 'Connection error', 'status': 503}
        except Exception as e:
            logger.error(f"API error: {e}")
            if retry_count < max_retries:
                time.sleep(retry_delay)
                return APIService.search(query, retry_count + 1)
            return {'error': str(e), 'status': 500}
