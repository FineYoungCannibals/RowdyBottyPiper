from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from selenium import webdriver
from rowdybottypiper.utils.validators import validate_url
from rowdybottypiper.utils.realistic import random_pause
from typing import Optional
# Example Action Implementations

class NavigateAction(Action):
    """Navigate to a URL"""
    def __init__(self, url: str, wait_time: Optional[float] = 2.0):
        super().__init__("Navigate")
        self.url = validate_url(url)
        self.wait_time = wait_time
        
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        driver.get(self.url)
        if self.logger:
            self.logger.info("Navigation completed", url=self.url)
        context.set('current_url', driver.current_url)
        random_pause(0.2,self.wait_time)
        return True