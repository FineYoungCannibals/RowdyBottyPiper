from typing import Literal
from selenium import webdriver

from rowdybottypiper.actions.clickable.base import ClickableAction
from rowdybottypiper.core.context import BotContext


class ClickAction(ClickableAction):
    """Simple click action"""
    
    type: Literal["ClickAction"] = "ClickAction"
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        self._find_and_click_element(driver)
        return True