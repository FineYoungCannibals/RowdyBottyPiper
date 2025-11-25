from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ClickAction(Action):
    """Click an element"""
    def __init__(self, selector: str, by: str = "CSS_SELECTOR"):
        super().__init__("Click")
        self.selector = selector
        self.by = by
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        from selenium.webdriver.common.by import By
        
        by_map = {
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "XPATH": By.XPATH,
            "ID": By.ID,
            "CLASS_NAME": By.CLASS_NAME
        }
        
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((by_map[self.by], self.selector))
        )
        element.click()
        if self.logger:
            self.logger.info("Element clicked", selector=self.selector)
        self.make_random_wait()
        return True