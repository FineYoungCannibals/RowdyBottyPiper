from abc import abstractmethod
from pydantic import Field
from typing import Literal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import smooth_scroll_to_element, random_pause


class ClickableAction(Action):
    """Base class for actions that click elements"""
    
    selector: str
    by: Literal["CSS_SELECTOR", "XPATH", "ID", "CLASS_NAME", "NAME", "LINK_TEXT", "PARTIAL_LINK_TEXT"] = "CSS_SELECTOR"
    scroll_to_element: bool = True
    
    def _get_by_type(self):
        """Convert string to Selenium By type"""
        by_map = {
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "XPATH": By.XPATH,
            "ID": By.ID,
            "CLASS_NAME": By.CLASS_NAME,
            "NAME": By.NAME,
            "LINK_TEXT": By.LINK_TEXT,
            "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT
        }
        return by_map.get(self.by.upper(), By.CSS_SELECTOR)
    
    def _find_and_click_element(self, driver: webdriver.Chrome) -> WebElement:
        """Find element, optionally scroll to it, and click"""
        by_type = self._get_by_type()
        
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((by_type, self.selector))
        )
        
        if self.scroll_to_element:
            smooth_scroll_to_element(driver, element)
            random_pause(lower=0.3, upper=self.wait_upper)
        
        element.click()
        random_pause(lower=0.5, upper=self.wait_upper)
        
        return element
    
    @abstractmethod
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        pass