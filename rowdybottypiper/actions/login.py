from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.validators import validate_url
from rowdybottypiper.utils.realistic import slow_typing, random_pause
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
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
        success_indicator: Optional[str] = None
    ):
        super().__init__("Login")
        self.url = validate_url(url)
        self.username = username
        self.password = password
        self.username_selector = username_selector
        self.password_selector = password_selector
        self.submit_selector = submit_selector
        self.success_indicator = success_indicator
    
    
            
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        from selenium.webdriver.common.by import By
        
        # Navigate to login page
        driver.get(self.url)
        if self.logger:
            self.logger.info("Navigated to login page", url=self.url)
        random_pause()
        
        # Fill in credentials
        username_field = driver.find_element(By.CSS_SELECTOR, self.username_selector)
        slow_typing(username_field, self.username)
        password_field = driver.find_element(By.CSS_SELECTOR, self.password_selector)
        slow_typing(password_field,self.password)
        
        if self.logger:
            self.logger.info("Credentials entered")
        
        # Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, self.submit_selector)
        submit_button.click()
        
        # Wait for page load
        random_pause()
        
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

