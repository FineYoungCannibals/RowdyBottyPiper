from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import smooth_scroll_to_element, random_pause, slow_typing

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from typing import Optional, List, Tuple


class SubmitFormAction(Action):
    """Click an element"""
    def __init__(
            self, 
            form_fields: List[Tuple[str,str,str]],
            submit_selector: str,
            by: str = "CSS_SELECTOR",
            success_indicator: Optional[str] = None,
            **kwargs
    ):
        super().__init__("SubmitForm")
        self.form_fields = form_fields
        self.selector = submit_selector
        self.by = by
        self.success_indicator = success_indicator
    
    def _get_by_type(self, by: str):
        """Convert string to Selenium By type"""
        by_map = {
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "XPATH": By.XPATH,
            "ID": By.ID,
            "CLASS_NAME": By.CLASS_NAME,
            "NAME": By.NAME,
            "TAG_NAME": By.TAG_NAME
        }
        return by_map.get(by.upper(), By.CSS_SELECTOR)

    def _fill_text_field(self, driver: webdriver.Chrome, element, value: str):
        """Fill a text input or textarea"""
        element.clear()
        random_pause(lower=0.2, upper=0.5)
        slow_typing(element, value)
        if self.logger:
            self.logger.debug("Filled text field", value_length=len(value))
    
    def _fill_select_field(self, element, value: str):
        """Fill a dropdown/select field"""
        select = Select(element)
        # Try by visible text first
        try:
            select.select_by_visible_text(value)
            if self.logger:
                self.logger.debug("Selected by visible text", value=value)
        except:
            # Try by value
            try:
                select.select_by_value(value)
                if self.logger:
                    self.logger.debug("Selected by value", value=value)
            except:
                # Try by index as last resort
                try:
                    select.select_by_index(int(value))
                    if self.logger:
                        self.logger.debug("Selected by index", index=value)
                except Exception as e:
                    if self.logger:
                        self.logger.error("Failed to select option", value=value, error=str(e))
                    raise

    def _fill_checkbox_field(self, element, value: str):
        """Check or uncheck a checkbox"""
        should_check = value.lower() in ['true', '1', 'yes', 'checked']
        is_checked = element.is_selected()
        
        if should_check != is_checked:
            element.click()
            if self.logger:
                self.logger.debug("Toggled checkbox", checked=should_check)
    
    def _fill_radio_field(self, element, value: str):
        """Select a radio button"""
        if not element.is_selected():
            element.click()
            if self.logger:
                self.logger.debug("Selected radio button")
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        by_type = self._get_by_type(self.by)
        
        if self.logger:
            self.logger.info("Starting form submission", total_fields=len(self.form_fields))
        
        # Fill each field
        for i, (selector, value, field_type) in enumerate(self.form_fields):
            try:
                if self.logger:
                    self.logger.debug(
                        f"Processing field {i+1}/{len(self.form_fields)}",
                        selector=selector,
                        field_type=field_type
                    )
                
                # Wait for field to be present
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by_type, selector))
                )
                
                # Scroll to field if enabled
                if self.scroll_to_fields:
                    smooth_scroll_to_element(driver, element)
                    random_pause(lower=0.3, upper=0.7)
                
                # Fill field based on type
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
                    if self.logger:
                        self.logger.warning(f"Unknown field type: {field_type}, treating as text")
                    self._fill_text_field(driver, element, value)
                
                # Random pause between fields
                random_pause(lower=0.5, upper=1.5)
            
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Failed to fill field {i+1}",
                        selector=selector,
                        error=str(e)
                    )
                return False
        
        if self.logger:
            self.logger.info("All fields filled, submitting form")
        
        # Submit the form
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by_type, self.submit_selector))
            )
            
            smooth_scroll_to_element(driver, submit_button)
            random_pause(lower=0.5, upper=1.2)
            
            submit_button.click()
            
            if self.logger:
                self.logger.info("Form submitted successfully")
            
            # Wait for page to respond
            random_pause(lower=2.0, upper=4.0)
            
            # Verify submission if success indicator provided
            if self.success_indicator:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.success_indicator))
                    )
                    if self.logger:
                        self.logger.info("Form submission verified")
                except:
                    if self.logger:
                        self.logger.warning("Success indicator not found")
                    return False
            
            # Store form submission in context
            context.set('form_submitted', True)
            context.set('form_data', {selector: value for selector, value, _ in self.form_fields})
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error("Failed to submit form", error=str(e))
            return False