from bot_framework.core.action import Action, ActionStatus
from bot_framework.core.context import BotContext
import time
from typing import Optional

class LogoutAction(Action):
    """Example logout action"""
    def __init__(self, logout_url: Optional[str] = None, logout_selector: Optional[str] = None):
        super().__init__("Logout")
        self.logout_url = logout_url
        self.logout_selector = logout_selector
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        from selenium.webdriver.common.by import By
        
        if self.logout_url:
            driver.get(self.logout_url)
            if self.logger:
                self.logger.info("Navigated to logout URL", url=self.logout_url)
        elif self.logout_selector:
            logout_button = driver.find_element(By.CSS_SELECTOR, self.logout_selector)
            logout_button.click()
            if self.logger:
                self.logger.info("Clicked logout button", selector=self.logout_selector)
        
        time.sleep(2)
        context.set('logged_in', False)
        context.session_active = False
        return True