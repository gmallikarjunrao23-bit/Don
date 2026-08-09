"""
OSINT 100X ULTIMATE — Custom Logger
"""

import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured logging for better debugging"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler with JSON format
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
    
    def info(self, message, **kwargs):
        self.logger.info(self._format(message, **kwargs))
    
    def error(self, message, **kwargs):
        self.logger.error(self._format(message, **kwargs))
    
    def warning(self, message, **kwargs):
        self.logger.warning(self._format(message, **kwargs))
    
    def debug(self, message, **kwargs):
        self.logger.debug(self._format(message, **kwargs))
    
    def _format(self, message, **kwargs):
        if kwargs:
            return f"{message} | {json.dumps(kwargs)}"
        return message

# Global logger instance
logger = StructuredLogger('osint')
