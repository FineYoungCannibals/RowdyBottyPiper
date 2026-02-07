from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict
import time
from typing import Optional
from rowdybottypiper.logging.structured_logger import StructuredLogger
from rowdybottypiper.logging.metrics import ActionMetrics
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.actions.action_status import ActionStatus
from selenium import webdriver

class Action(BaseModel, ABC):
    """Base class for bot actions with enhanced logging"""
    name: str
    retry_count: int = Field(default=3, ge=1)
    retry_delay: int = Field(default=2, ge=0)
    wait_lower: float = Field(default=1.1, ge=0)
    wait_upper: float = Field(default=10.0, ge=0)

    def model_post_init(self, __context):
        """CAlled after pydantic initialization"""
        self.metrics = ActionMetrics(self.name)
    
    @abstractmethod
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        """
        Execute the action
        Returns True if successful, False otherwise
        """
        pass
    
    def run(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        """Run action with retry logic and metrics"""
        for attempt in range(self.retry_count):
            try:
                self.metrics.start()
                success = self.execute(driver, context)
                if success:
                    self.metrics.end(ActionStatus.SUCCESS)
                    return True
                else:
                    if attempt < self.retry_count - 1:
                        self.metrics.end(ActionStatus.RETRYING, "Action returned False")
                    else:
                        self.metrics.end(ActionStatus.FAILED, "Action returned False after all retries")
            except Exception as e:
                error_msg = str(e)
                if attempt < self.retry_count - 1:
                    self.metrics.end(ActionStatus.RETRYING, error_msg)
                    time.sleep(self.retry_delay)
                else:
                    self.metrics.end(ActionStatus.FAILED, error_msg)
        return False