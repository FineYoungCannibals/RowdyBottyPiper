from pydantic import Field, field_validator
from typing import Literal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from rowdybottypiper.actions.forms.base import FormAction
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.validators import validate_url
from rowdybottypiper.utils.realistic import slow_typing, random_pause


class LoginAction(FormAction):
    """Complete login workflow with navigation, submission, and verification"""
    
    type: Literal["LoginAction"] = "LoginAction"
    
    # Navigation
    url: str
    
    # Credentials
    username: str
    password: str
    
    # Selectors
    username_selector: str
    password_selector: str
    submit_selector: str
    success_indicator: str
    
    # Login-specific behavior
    retry_with_refresh: bool = True
    verification_timeout: int = Field(default=30, ge=1)
    
    @field_validator('url')
    @classmethod
    def validate_url_field(cls, v):
        return validate_url(v)
    
    def _verify_login(self, driver: webdriver.Chrome) -> bool:
        """Verify login was successful by checking for success indicator"""
        try:
            WebDriverWait(driver, self.verification_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.success_indicator))
            )
            return True
        except TimeoutException:
            return False
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        # Navigate to login page
        driver.get(self.url)
        random_pause(lower=self.wait_lower, upper=self.wait_upper)
        
        # Fill username
        username_field = driver.find_element(By.CSS_SELECTOR, self.username_selector)
        slow_typing(username_field, self.username)
        random_pause(lower=0.5, upper=self.wait_upper)
        
        # Fill password
        password_field = driver.find_element(By.CSS_SELECTOR, self.password_selector)
        slow_typing(password_field, self.password)
        random_pause(lower=0.3, upper=self.wait_upper)
        
        # Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, self.submit_selector)
        submit_button.click()
        
        # First verification attempt
        login_verified = self._verify_login(driver)
        
        # Retry with refresh if enabled and first attempt failed
        if not login_verified and self.retry_with_refresh:
            driver.refresh()
            random_pause(lower=2.0, upper=self.wait_upper)
            login_verified = self._verify_login(driver)
        
        if not login_verified:
            return False
        
        # Store session state in context
        context.set('logged_in', True)
        context.session_active = True
        
        return True