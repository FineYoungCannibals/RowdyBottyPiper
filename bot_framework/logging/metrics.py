from typing import Any, Dict, List, Optional
from enum import Enum
import time
from datetime import datetime
from bot_framework.logging.structured_logger import StructuredLogger
from bot_framework.core.action import ActionStatus




class ActionMetrics:
    """Metrics for action execution"""
    
    def __init__(self, action_name: str):
        self.action_name = action_name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.attempts = 0
        self.status = ActionStatus.SKIPPED
        self.error_message: Optional[str] = None
    
    def start(self):
        """Mark action start"""
        self.start_time = time.time()
        self.attempts += 1
    
    def end(self, status: ActionStatus, error_message: Optional[str] = None):
        """Mark action end"""
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.status = status
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "action_name": self.action_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": round(self.duration, 3) if self.duration else None,
            "attempts": self.attempts,
            "status": self.status.value,
            "error_message": self.error_message
        }


class BotMetrics:
    """Metrics for entire bot execution"""
    
    def __init__(self, bot_name: str, correlation_id: str):
        self.bot_name = bot_name
        self.correlation_id = correlation_id
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.total_actions = 0
        self.successful_actions = 0
        self.failed_actions = 0
        self.action_metrics: List[ActionMetrics] = []
        self.overall_success = False
    
    def start(self):
        """Mark bot start"""
        self.start_time = time.time()
    
    def end(self, success: bool):
        """Mark bot end"""
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.overall_success = success
    
    def add_action_metrics(self, metrics: ActionMetrics):
        """Add action metrics"""
        self.action_metrics.append(metrics)
        self.total_actions += 1
        if metrics.status == ActionStatus.SUCCESS:
            self.successful_actions += 1
        elif metrics.status == ActionStatus.FAILED:
            self.failed_actions += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "bot_name": self.bot_name,
            "correlation_id": self.correlation_id,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration_seconds": round(self.duration, 3) if self.duration else None,
            "overall_success": self.overall_success,
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "success_rate": round(self.successful_actions / self.total_actions * 100, 2) if self.total_actions > 0 else 0,
            "actions": [m.to_dict() for m in self.action_metrics]
        }
    
    def log_summary(self, logger: StructuredLogger):
        """Log execution summary"""
        logger.info(
            "Bot execution completed",
            metrics=self.to_dict()
        )
