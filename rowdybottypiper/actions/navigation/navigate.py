from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from selenium import webdriver
from rowdybottypiper.utils.realistic import random_pause
from typing import Literal
from pydantic import Field, field_validator
# Example Action Implementations

class NavigateAction(Action):
    """Navigate to a URL"""
    type: Literal["NavigateAction"] = "NavigateAction"
    url: str
    save_dom: bool = False

    @field_validator('url')
    @classmethod
    def validate_url_field(cls, v):
        from rowdybottypiper.utils.validators import validate_url
        return validate_url(v)
        
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        driver.get(self.url)
        context.set('current_url', driver.current_url)
        random_pause(self.wait_lower,self.wait_upper)

        if self.save_dom:
            dom_html = driver.page_source
            key = f"{self.name}_dom"
            context.set(key, dom_html)
        return True