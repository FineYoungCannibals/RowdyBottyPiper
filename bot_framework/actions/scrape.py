from bot_framework.actions.action import Action
from bot_framework.core.context import BotContext
from typing import Optional
import time

class ScrapeAction(Action):
    """Scrape data from current page"""
    def __init__(self, selector: str, context_key: str, attribute: Optional[str] = None, wait_time: int = 2):
        super().__init__("Scrape")
        self.selector = selector
        self.context_key = context_key
        self.attribute = attribute
        self.wait_time = wait_time
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        from selenium.webdriver.common.by import By
        
        elements = driver.find_elements(By.CSS_SELECTOR, self.selector)
        
        if not elements:
            if self.logger:
                self.logger.warning("No elements found", selector=self.selector)
            return False
        
        if self.attribute:
            data = [elem.get_attribute(self.attribute) for elem in elements]
        else:
            data = [elem.text for elem in elements]
        
        time.sleep(self.wait_time)
        context.set(self.context_key, data)
        if self.logger:
            self.logger.info(
                "Data scraped successfully",
                selector=self.selector,
                items_count=len(data),
                context_key=self.context_key
            )
        return True