from abc import abstractmethod
from pydantic import Field
from typing import Literal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import smooth_scroll_to_element, random_pause, slow_typing


class FormAction(Action):
    """Base class for form-related actions"""
    
    by: Literal["CSS_SELECTOR", "XPATH", "ID", "CLASS_NAME", "NAME", "TAG_NAME"] = "CSS_SELECTOR"
    scroll_to_fields: bool = False
    
    def _get_by_type(self):
        """Convert string to Selenium By type"""
        by_map = {
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "XPATH": By.XPATH,
            "ID": By.ID,
            "CLASS_NAME": By.CLASS_NAME,
            "NAME": By.NAME,
            "TAG_NAME": By.TAG_NAME
        }
        return by_map.get(self.by.upper(), By.CSS_SELECTOR)
    
    def _fill_text_field(self, driver: webdriver.Chrome, element, value: str):
        """Fill a text input or textarea"""
        element.clear()
        random_pause(lower=0.2, upper=self.wait_upper)
        slow_typing(element, value)
    
    def _fill_select_field(self, element, value: str):
        """Fill a dropdown/select field"""
        select = Select(element)
        # Try by visible text first
        try:
            select.select_by_visible_text(value)
        except:
            # Try by value
            try:
                select.select_by_value(value)
            except:
                # Try by index as last resort
                try:
                    select.select_by_index(int(value))
                except Exception as e:
                    raise
    
    def _fill_checkbox_field(self, element, value: str):
        """Check or uncheck a checkbox"""
        should_check = value.lower() in ['true', '1', 'yes', 'checked']
        is_checked = element.is_selected()
        
        if should_check != is_checked:
            element.click()
    
    def _fill_radio_field(self, element, value: str):
        """Select a radio button"""
        if not element.is_selected():
            element.click()
    
    def _fill_field(self, driver: webdriver.Chrome, selector: str, value: str, field_type: str):
        """Generic field filler - routes to specific methods"""
        by_type = self._get_by_type()
        
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by_type, selector))
        )
        
        if self.scroll_to_fields:
            smooth_scroll_to_element(driver, element)
            random_pause(lower=0.3, upper=self.wait_upper)
        
        field_type_lower = field_type.lower()
        
        if field_type_lower in ['text', 'input', 'textarea', 'email', 'password', 'number']:
            self._fill_text_field(driver, element, value)
        elif field_type_lower == 'select':
            self._fill_select_field(element, value)
        elif field_type_lower == 'checkbox':
            self._fill_checkbox_field(element, value)
        elif field_type_lower == 'radio':
            self._fill_radio_field(element, value)
        else:
            # Default to text field
            self._fill_text_field(driver, element, value)
        
        random_pause(lower=0.5, upper=self.wait_upper)
    
    @abstractmethod
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        pass