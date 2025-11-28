"""
Web Automation Bot Framework with Advanced Logging
A flexible framework for building stateful web automation bots with comprehensive logging.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.actions.action import Action
from rowdybottypiper.logging.structured_logger import StructuredLogger
from rowdybottypiper.logging.metrics import BotMetrics
import random
import os


class Bot:
    """Base bot class for web automation with comprehensive logging"""
    
    def __init__(
        self,
        name: str,
        chrome_driver_path: Optional[str] = None,
        headless: bool = False,
        chrome_options: Optional[Options] = None,
        correlation_id: Optional[str] = None,
        debug: Optional[bool] = False
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
        
        # SlackClient specific variables, auto-detect, if found, lazy load inc
        slack_token = os.getenv('RRP_SLACK_BOT_TOKEN')
        slack_channel = os.getenv('RRP_SLACK_CHANNEL')

        if slack_token and slack_channel:
            try:
                from rowdybottypiper.utils.slackbot import SlackClient
                self.slack = SlackClient(
                    logger=self.logger,
                    token=slack_token,
                    channel=slack_channel
                )
                self.logger.info("Slack integration enabled")
            except Exception as e:
                self.logger.warning(f"Slack integration failed to initialize: {str(e)}")
                self.slack=None
        else:
            self.slack=None
            self.logger.info("Slack integration disabled (RRP_SLACK_BOT_TOKEN' and 'RRP_SLACK_CHANNEL' env vars not detected)")

        # S3Uploader specific variables, auto-detect, if found, lazy load
        s3_secret_key = os.getenv('RRP_S3_SECRET_KEY')
        s3_access_key = os.getenv('RRP_S3_ACCESS_KEY')
        s3_bucket_name = os.getenv('RRP_S3_BUCKET_NAME')
        s3_region = os.getenv('RRP_S3_REGION')
        s3_endpoint = os.getenv('RRP_S3_ENDPOINT')

        if s3_secret_key and s3_access_key and s3_bucket_name:
            try:
                from rowdybottypiper.utils.s3_uploader import S3Uploader
                self.s3_uploader = S3Uploader(
                    logger=self.logger,
                    bucket_name=s3_bucket_name,
                    region_name=s3_region,
                    endpoint_url=s3_endpoint,
                    access_key=s3_access_key,
                    secret_key=s3_secret_key
                )
                self.logger.info("S3 uploader enabled")
            except Exception as e:
                self.logger.warning(f"S3 uploader failed to initialize: {str(e)}")
                self.s3_uploader = None
        else:
            self.s3_uploader = None
            self.logger.info("S3 uploader disabled (RRP_S3_SECRET_KEY, RRP_S3_ACCESS_KEY, and RRP_S3_BUCKET_NAME env vars not detected)")

        # SCPClient specific variables, auto-detect, if found, lazy load
        scp_hostname = os.getenv('RRP_SCP_HOSTNAME')
        scp_username = os.getenv('RRP_SCP_USERNAME')
        scp_private_key = os.getenv('RRP_SCP_PRIVATEKEY')
        scp_public_key = os.getenv('RRP_SCP_PUBLICKEY')
        scp_port = int(os.getenv('RRP_SCP_PORT', '22'))

        if scp_hostname and scp_username and scp_private_key and scp_public_key:
            try:
                from rowdybottypiper.utils.scp_client import SCPClient
                self.scp_client = SCPClient(
                    logger=self.logger,
                    hostname=scp_hostname,
                    username=scp_username,
                    password=None,
                    key_filename=scp_private_key,
                    port=scp_port
                )
                self.logger.info("SCP client enabled")
            except Exception as e:
                self.logger.warning(f"SCP client failed to initialize: {str(e)}")
                self.scp_client = None
        else:
            self.scp_client = None
            self.logger.info("SCP client disabled (RRP_SCP_HOSTNAME, RRP_SCP_USERNAME, RRP_SCP_PRIVATEKEY, and RRP_SCP_PUBLICKEY env vars not detected)")

    def notify_slack(self, title: str, message: str, file_path: Optional[str] = None):
        if not self.slack:
            self.logger.debug("Slack not configured, no message sent.")
            return False
        return self.slack.send_message(title=title, message=message, file_path=file_path)
    
    def upload_to_s3(self, file_path: str, s3_folder: str = '', s3_filename: Optional[str] = None, make_public: bool = False) -> bool:
        """Upload a file to S3 if S3 uploader is configured"""
        if not self.s3_uploader:
            self.logger.debug("S3 uploader not configured, file not uploaded.")
            return False
        return self.s3_uploader.upload_file(file_path, s3_folder, s3_filename, make_public)
    
    def scp_upload(self, local_path: str, remote_path: str, create_remote_dirs: bool = True) -> bool:
        """Upload a file via SCP if SCP client is configured"""
        if not self.scp_client:
            self.logger.debug("SCP client not configured, file not uploaded.")
            return False
        return self.scp_client.upload_file(local_path, remote_path, create_remote_dirs)
    
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
            
            # Set random window size to mimic human behavior
            self.driver.set_window_size(random.randint(1201,1599), random.randint(801,899))
            self.driver.implicitly_wait(10)

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