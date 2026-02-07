from pydantic import Field
from typing import Literal, List, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from rowdybottypiper.actions.forms.base import FormAction
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import smooth_scroll_to_element, random_pause


class SubmitFormAction(FormAction):
    """Fill multiple form fields and submit"""
    
    type: Literal["SubmitFormAction"] = "SubmitFormAction"
    
    form_fields: List[Tuple[str, str, str]]  # (selector, value, field_type)
    submit_selector: str
    success_indicator: Optional[str] = None
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        by_type = self._get_by_type()
        
        # Fill each field
        for selector, value, field_type in self.form_fields:
            try:
                self._fill_field(driver, selector, value, field_type)
            except Exception as e:
                return False
        
        # Submit the form
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by_type, self.submit_selector))
            )
            
            smooth_scroll_to_element(driver, submit_button)
            random_pause(lower=0.5, upper=self.wait_upper)
            
            submit_button.click()
            random_pause(lower=2.0, upper=self.wait_upper)
            
            # Verify submission if success indicator provided
            if self.success_indicator:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.success_indicator))
                    )
                except:
                    return False
            
            # Store form submission in context
            context.set('form_submitted', True)
            context.set('form_data', {selector: value for selector, value, _ in self.form_fields})
            
            return True
        
        except Exception as e:
            return False