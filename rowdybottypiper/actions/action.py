from abc import ABC, abstractmethod
import time
from typing import Optional
from rowdybottypiper.logging.structured_logger import StructuredLogger
from rowdybottypiper.logging.metrics import ActionMetrics
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.actions.action_status import ActionStatus
import random
from selenium import webdriver

class Action(ABC):
    """Base class for bot actions with enhanced logging"""
    def __init__(self, name: str, retry_count: int = 3, retry_delay: int = 2, wait_lower: float = 0.1, wait_upper: float = 4.0):
        self.name = name
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.logger: Optional[StructuredLogger] = None
        self.metrics = ActionMetrics(name)
        self.wait_lower = wait_lower
        self.wait_upper = wait_upper
    
    def make_random_wait(self):
        """Wait for a random duration to mimic human behavior"""
        time.sleep(random.uniform(self.wait_lower,self.wait_upper))
        return
    
    def set_logger(self, logger: StructuredLogger):
        """Set the structured logger"""
        self.logger = logger
    
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
                
                if self.logger:
                    self.logger.info(
                        f"Starting action '{self.name}'",
                        action=self.name,
                        attempt=attempt + 1,
                        max_attempts=self.retry_count
                    )
                
                success = self.execute(driver, context)
                
                if success:
                    self.metrics.end(ActionStatus.SUCCESS)
                    if self.logger:
                        self.logger.info(
                            f"Action '{self.name}' completed successfully",
                            action=self.name,
                            duration=self.metrics.duration,
                            attempts=self.metrics.attempts
                        )
                    return True
                else:
                    if attempt < self.retry_count - 1:
                        self.metrics.end(ActionStatus.RETRYING, "Action returned False")
                        if self.logger:
                            self.logger.warning(
                                f"Action '{self.name}' returned False, retrying",
                                action=self.name,
                                attempt=attempt + 1
                            )
                    else:
                        self.metrics.end(ActionStatus.FAILED, "Action returned False after all retries")
                        
            except Exception as e:
                error_msg = str(e)
                if attempt < self.retry_count - 1:
                    self.metrics.end(ActionStatus.RETRYING, error_msg)
                    if self.logger:
                        self.logger.warning(
                            f"Action '{self.name}' failed, retrying",
                            action=self.name,
                            attempt=attempt + 1,
                            error=error_msg,
                            retry_delay=self.retry_delay
                        )
                    time.sleep(self.retry_delay)
                else:
                    self.metrics.end(ActionStatus.FAILED, error_msg)
                    if self.logger:
                        self.logger.error(
                            f"Action '{self.name}' failed after all retries",
                            action=self.name,
                            attempts=self.retry_count,
                            error=error_msg
                        )
        
        return False
