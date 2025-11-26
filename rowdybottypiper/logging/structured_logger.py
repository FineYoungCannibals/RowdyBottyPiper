from enum import Enum
import logging
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
        
class StructuredLogger:
    """Enhanced logger with structured output for distributed systems"""
    
    def __init__(self, name: str, correlation_id: Optional[str] = None):
        self.name = name
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.logger = logging.getLogger(name)
        
    def _create_log_entry(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create structured log entry"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self.correlation_id,
            "logger_name": self.name,
            "level": level,
            "message": message
        }
        if extra:
            entry.update(extra)
        return entry
    
    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal logging method"""
        log_entry = self._create_log_entry(level, message, extra)
        log_message = json.dumps(log_entry)
        
        # Use standard logger
        log_method = getattr(self.logger, level.lower())
        log_method(log_message)
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, kwargs)
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log("CRITICAL", message, kwargs)

