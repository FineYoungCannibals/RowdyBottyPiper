"""
Web Automation Bot Framework with Advanced Logging
A flexible framework for building stateful web automation bots with comprehensive logging.
"""


import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from bot_framework.core.context import BotContext
from bot_framework.actions.action import Action
from bot_framework.logging.structured_logger import StructuredLogger
from bot_framework.logging.metrics import BotMetrics

class Bot:
    """Base bot class for web automation with comprehensive logging"""
    
    def __init__(
        self,
        name: str,
        chrome_driver_path: Optional[str] = None,
        headless: bool = False,
        chrome_options: Optional[Options] = None,
        correlation_id: Optional[str] = None,
        debug: bool = False
    ):
        self.debug = debug
        self.name = name
        self.chrome_driver_path = chrome_driver_path
        self.headless = headless
        self.chrome_options = chrome_options or Options()
        self.driver: Optional[webdriver.Chrome] = None
        self.context = BotContext()
        self.actions: List[Action] = []
        
        # Initialize structured logging
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.logger = StructuredLogger(f"Bot.{name}", self.correlation_id)
        self.metrics = BotMetrics(name, self.correlation_id)
        
        # Configure default Chrome options
        if headless:
            self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
    
    def add_action(self, action: Action) -> 'Bot':
        """Add an action to the bot's workflow (chainable)"""
        action.set_logger(self.logger)
        self.actions.append(action)
        return self
    
    def setup_driver(self):
        """Initialize the Chrome driver"""
        try:
            self.logger.info(
                "Initializing Chrome driver",
                headless=self.headless,
                custom_driver=self.chrome_driver_path is not None
            )
            
            if self.chrome_driver_path:
                service = Service(executable_path=self.chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            else:
                self.driver = webdriver.Chrome(options=self.chrome_options)
            
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.critical(
                "Failed to initialize Chrome driver",
                error=str(e)
            )
            raise
    def list_actions(self) -> List[str]:
        self.logger.debug(f"Listing all actions in the bot workflow - execution at {str(datetime.now().strftime('%s'))}")
        self.logger.debug([action.name for action in self.actions])
    
    def teardown_driver(self):
        """Close the Chrome driver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Chrome driver closed successfully")
            except Exception as e:
                self.logger.error(
                    "Error closing Chrome driver",
                    error=str(e)
                )
    
    def run(self) -> bool:
        """Execute the complete bot workflow"""
        self.logger.info(
            f"Starting bot execution",
            bot_name=self.name,
            total_actions=len(self.actions)
        )
        self.metrics.start()
        
        try:
            # Setup
            self.setup_driver()
            if self.debug:
                self.logger.info("Debug mode is ON")
                self.list_actions()
            # Execute all actions in sequence
            for i, action in enumerate(self.actions):
                self.logger.info(
                    f"Executing action {i+1}/{len(self.actions)}",
                    action_name=action.name,
                    action_index=i
                )
                
                success = action.run(self.driver, self.context)
                self.metrics.add_action_metrics(action.metrics)
                
                if not success:
                    self.logger.error(
                        f"Bot stopped due to action failure",
                        failed_action=action.name,
                        action_index=i
                    )
                    self.metrics.end(False)
                    self.metrics.log_summary(self.logger)
                    return False
            
            self.logger.info(
                f"Bot completed all actions successfully",
                total_actions=len(self.actions)
            )
            if self.debug:
                self.logger.debug("Final Bot Context", context=self.context.data)
                self.logger.debug("Final Bot Metrics", metrics=self.metrics.to_dict())
                self.logger.debug("Bot Completed at ", completion_time=str(datetime.now().strftime('%s')))

            self.metrics.end(True)
            self.metrics.log_summary(self.logger)
            return True
            
        except Exception as e:
            self.logger.critical(
                f"Bot encountered unexpected error",
                error=str(e)
            )
            self.metrics.end(False)
            self.metrics.log_summary(self.logger)
            return False
        
        finally:
            # Cleanup
            self.teardown_driver()
    
    def get_session_cookies(self) -> Dict[str, str]:
        """Extract cookies from Selenium session"""
        if not self.driver:
            return {}
        
        cookies = {}
        for cookie in self.driver.get_cookies():
            cookies[cookie['name']] = cookie['value']
        return cookies
    
    def create_requests_session(self) -> requests.Session:
        """Create a requests session with cookies from Selenium"""
        session = requests.Session()
        cookies = self.get_session_cookies()
        for name, value in cookies.items():
            session.cookies.set(name, value)
        return session