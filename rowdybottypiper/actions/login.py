from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.validators import validate_url
from rowdybottypiper.utils.realistic import slow_typing, random_pause
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Optional


class LoginAction(Action):
    """Login action with optional retry mechanism and page refresh fallback"""
    
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        username_selector: str,
        password_selector: str,
        submit_selector: str,
        success_indicator: str,
        retry_with_refresh: bool = True,
        verification_timeout: int = 30,
        **kwargs
    ):
        """
        Initialize LoginAction
        
        Args:
            url: Login page URL
            username: Username/email to login with
            password: Password to login with
            username_selector: CSS selector for username field
            password_selector: CSS selector for password field
            submit_selector: CSS selector for submit button
            success_indicator: CSS selector that appears after successful login
            retry_with_refresh: If True, refresh page and retry if login verification fails
            verification_timeout: Seconds to wait for success indicator
            **kwargs: Additional Action parameters (wait_lower, wait_upper, retry_count, etc.)
        """
        super().__init__("Login", **kwargs)
        self.url = validate_url(url)
        self.username = username
        self.password = password
        self.username_selector = username_selector
        self.password_selector = password_selector
        self.submit_selector = submit_selector
        self.success_indicator = success_indicator
        self.retry_with_refresh = retry_with_refresh
        self.verification_timeout = verification_timeout
    
    def _wait_for_element(self, driver: webdriver.Chrome, by, selector, timeout=30):
        """Wait for an element to be present"""
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    
    def _verify_login(self, driver: webdriver.Chrome) -> bool:
        """
        Verify login was successful by checking for success indicator
        
        Returns:
            True if login verified, False otherwise
        """
        try:
            if self.logger:
                self.logger.info("Waiting for login verification", timeout=self.verification_timeout)
            
            self._wait_for_element(
                driver,
                By.CSS_SELECTOR,
                self.success_indicator,
                timeout=self.verification_timeout
            )
            
            if self.logger:
                self.logger.info("Login verified successfully")
            return True
        
        except TimeoutException:
            if self.logger:
                self.logger.warning("Login verification timeout - success indicator not found")
            return False
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        # Navigate to login page
        driver.get(self.url)
        if self.logger:
            self.logger.info("Navigated to login page", url=self.url)
        random_pause()
        
        # Fill in credentials
        username_field = driver.find_element(By.CSS_SELECTOR, self.username_selector)
        slow_typing(username_field, self.username)
        
        random_pause(lower=0.5, upper=1.5)  # Pause between fields
        
        password_field = driver.find_element(By.CSS_SELECTOR, self.password_selector)
        slow_typing(password_field, self.password)
        
        if self.logger:
            self.logger.info("Credentials entered")
        
        random_pause(lower=0.3, upper=0.8)  # Pause before submit
        
        # Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, self.submit_selector)
        submit_button.click()
        
        if self.logger:
            self.logger.info("Login form submitted")
        
        # First verification attempt
        login_verified = self._verify_login(driver)
        
        # If first attempt failed and retry is enabled, refresh and try again
        if not login_verified and self.retry_with_refresh:
            if self.logger:
                self.logger.info("Attempting login verification with page refresh")
            
            driver.refresh()
            random_pause(lower=2.0, upper=4.0)  # Wait for refresh
            
            # Second verification attempt
            login_verified = self._verify_login(driver)
            
            if login_verified:
                if self.logger:
                    self.logger.info("Login verified successfully after refresh")
            else:
                if self.logger:
                    self.logger.error("Login verification failed after refresh")
                return False
        
        elif not login_verified:
            # Retry disabled and verification failed
            if self.logger:
                self.logger.error("Login verification failed (retry_with_refresh=False)")
            return False
        
        # Store login state
        context.set('logged_in', True)
        context.session_active = True
        
        if self.logger:
            self.logger.info("Login completed successfully")
        
        return True