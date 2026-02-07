from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import random_pause
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from typing import Optional, Literal
import time


class AlertAction(Action):
    """Handle JavaScript alerts, confirms, and prompts"""
    
    def __init__(
        self,
        action: Literal["accept", "dismiss", "get_text", "send_keys"] = "accept",
        text_to_send: Optional[str] = None,
        expected_text: Optional[str] = None,
        timeout: int = 10,
        wait_for_alert: bool = True,
        store_text_in_context: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AlertAction
        
        Args:
            action: What to do with the alert
                - 'accept': Click OK/Accept
                - 'dismiss': Click Cancel/Dismiss
                - 'get_text': Just get the alert text
                - 'send_keys': Send text to prompt (then accept)
            text_to_send: Text to send if action is 'send_keys'
            expected_text: Optional text to verify alert contains
            timeout: Seconds to wait for alert to appear
            wait_for_alert: If True, wait for alert. If False, check immediately
            store_text_in_context: Context key to store alert text
            **kwargs: Additional Action parameters
        """
        super().__init__("Alert", **kwargs)
        self.action = action
        self.text_to_send = text_to_send
        self.expected_text = expected_text
        self.timeout = timeout
        self.wait_for_alert = wait_for_alert
        self.store_text_in_context = store_text_in_context
    
    def _wait_for_alert(self, driver: webdriver.Chrome) -> bool:
        """Wait for an alert to be present"""
        try:
            WebDriverWait(driver, self.timeout).until(
                lambda d: d.switch_to.alert
            )
            return True
        except TimeoutException:
            return False
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        try:
            # Wait for alert if specified
            if self.wait_for_alert:
                alert_present = self._wait_for_alert(driver)
                
                if not alert_present:
                    return False
            
            # Small pause before interacting
            random_pause(lower=0.5, upper=4.0)
            
            # Switch to alert
            alert = driver.switch_to.alert
            alert_text = alert.text
            
            # Store alert text in context if requested
            if self.store_text_in_context:
                context.set(self.store_text_in_context, alert_text)
            
            # Verify expected text if provided
            if self.expected_text:
                if self.expected_text not in alert_text:
                    return False
            
            # Perform action
            if self.action == "accept":
                alert.accept()
            
            elif self.action == "dismiss":
                alert.dismiss()
            
            elif self.action == "send_keys":
                if self.text_to_send:
                    alert.send_keys(self.text_to_send)
                    random_pause(lower=0.2, upper=0.5)
                    alert.accept()
                else:
                    return False
            
            elif self.action == "get_text":
                # Don't accept or dismiss, just return
                return True
            
            # Pause after handling alert
            random_pause(lower=0.5, upper=1.0)
            
            # Store that alert was handled
            context.set('last_alert_handled', {
                'text': alert_text,
                'action': self.action
            })
            
            return True
        
        except NoAlertPresentException as e:
            print(f'{str(e)}')
            return False
        
        except Exception as e:
            print(f'{str(e)}')
            return False