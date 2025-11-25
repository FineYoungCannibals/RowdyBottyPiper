from bot_framework.core.action import Action, ActionStatus
from bot_framework.core.context import BotContext
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from typing import Optional


class LoginAction(Action):
    """Example login action"""
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        username_selector: str,
        password_selector: str,
        submit_selector: str,
        success_indicator: Optional[str] = None,
        wait_time: int = 2
    ):
        super().__init__("Login")
        self.url = url
        self.username = username
        self.password = password
        self.username_selector = username_selector
        self.password_selector = password_selector
        self.submit_selector = submit_selector
        self.success_indicator = success_indicator
        self.wait_time = wait_time
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        from selenium.webdriver.common.by import By
        
        # Navigate to login page
        driver.get(self.url)
        if self.logger:
            self.logger.info("Navigated to login page", url=self.url)
        time.sleep(self.wait_time)
        
        # Fill in credentials
        username_field = driver.find_element(By.CSS_SELECTOR, self.username_selector)
        username_field.send_keys(self.username)
        
        password_field = driver.find_element(By.CSS_SELECTOR, self.password_selector)
        password_field.send_keys(self.password)
        
        if self.logger:
            self.logger.info("Credentials entered")
        
        # Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, self.submit_selector)
        submit_button.click()
        
        # Wait for page load
        time.sleep(self.wait_time)
        
        # Verify success
        if self.success_indicator:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.success_indicator))
                )
                if self.logger:
                    self.logger.info("Login verified successfully")
            except TimeoutException:
                if self.logger:
                    self.logger.error("Login verification failed - success indicator not found")
                return False
        
        # Store login state
        context.set('logged_in', True)
        context.session_active = True
        
        return True

