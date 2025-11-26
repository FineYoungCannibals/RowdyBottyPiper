from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from typing import Optional
from selenium import webdriver
from rowdybottypiper.utils.realistic import random_pause, smooth_scroll_to_element
# similuates readings through page content

class Peruse(Action):
    """ Simulate reading through page content """

    def __init__(self, selector: str, context_key: str, attribute: Optional[str] = None):
        super().__init__("Peruse")
        self.selector = selector
        self.context_key = context_key
        self.attribute = attribute
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        from selenium.webdriver.common.by import By
        
        elements = driver.find_elements(By.CSS_SELECTOR, self.selector)
        
        if not elements:
            if self.logger:
                self.logger.warning("No elements found", selector=self.selector)
            return False
        
        for i, elem in enumerate(elements):
            if self.logger:
                self.logger.info(
                    "Perusing element",
                    selector=self.selector,
                    index=i+1,
                    total=len(elements)
                )
            smooth_scroll_to_element(driver, elem)
            random_pause()
        
        if self.logger:
            self.logger.info(
                "Perusing completed",
                selector=self.selector,
                items_count=len(elements),
                context_key=self.context_key
            )

        random_pause()
        return True