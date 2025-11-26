import random
import time
from typing import Optional
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
import string


def sim_alpha_fat_finger(inchar):
    neighbors = {
        "q":["w", "a"],
        "w":["e","d","s","q"],
        "a":["s","z"],
        "f":["g","d"],
        "j":["h","k"],
        "c":["v"],
        "n":["m"],
        "i":["u","o"],
        "s":["d","a"],
        "r":["t"],
        "e":["w","r"],
        "o":["i","p","l"],
        "z":["x","s"],
        "t":["r","g"],
        "y":["u","t"],
        "u":["i","y"],
        "p":["o","l"],
        "d":['f','s','c'],
        "g":['f'],
        "h":['g','j'],
        "k":['j'],
        "l":['k'],
        "m":['n'],
        "b":['v'],
        "x":['z','c'],
        "v":['c','b']
    }
    if neighbors.get(str(inchar).lower()):
        if str(inchar).isupper():
            return random.choice(neighbors[str(inchar).lower()]).upper()
        return random.choice(neighbors[inchar])
    else:
        if str(inchar).isupper():
            return random.choice(string.ascii_uppercase)
        return random.choice(string.ascii_lowercase)

def sim_num_fat_finger(inchar):
    return random.choice([str(abs(int(inchar)-1))[-1],str(abs(int(inchar)+1))[-1]])

def slow_typing(element, text, error_chance=0.06, delay_range=(0.4,1.5),error_delay=(0.3,0.8)):
    print(f"typing: {text}")
    for char in text:
        print(f"typing {char}")
        if random.random()<error_chance:
            print(f"typo trigger")
            if char.isalpha():
                element.send_keys(sim_alpha_fat_finger(char))
                time.sleep(random.uniform(*error_delay))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(*delay_range))
            elif char.isdigit():
                element.send_keys(sim_num_fat_finger(char))
                time.sleep(random.uniform(*error_delay))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(*delay_range))
            else:
                continue
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

def random_mouse_movement(driver, element: WebElement):
    """Simulate random mouse movement to an element to mimic human behavior"""
    from selenium.webdriver.common.action_chains import ActionChains
    
    actions = ActionChains(driver)
    # Move to element with some randomness
    actions.move_to_element_with_offset(
        element, 
        random.randint(-5, 5),  # Random x offset
        random.randint(-5, 5)   # Random y offset
    ).perform()
    time.sleep(random.uniform(0.1, 0.3))

def random_pause(lower: float = 0.2, upper: float = 4.0):
    """
    Simple random pause utility
    
    Args:
        lower: Minimum wait time (seconds)
        upper: Maximum wait time (seconds)
    """
    time.sleep(random.uniform(lower, upper))

def smooth_scroll_to_element(driver, element, step_range=(70, 120)):
    def get_step(numrange,negative=False):
        stepvalue = random.randint(*numrange)
        if negative:    
            return stepvalue*-1
        return stepvalue
    
    def get_window_y(driver):
        return driver.execute_script("return window.scrollY;")
    
    element_y = element.location['y']
    element_height = element.size['height']
    viewport_height = driver.execute_script("return window.innerHeight")
    viewport_halfway = viewport_height/2
    optimal_element_view_top = viewport_halfway-200
    optimal_element_view_bottom = viewport_halfway+200
    # Adjust scrolling until the element is centered in the viewport
    while True:
        window_y = get_window_y(driver)
        if element_y + element_height < window_y+optimal_element_view_top or element_y > window_y + optimal_element_view_bottom:
            # Scroll the page slightly
            driver.execute_script(f"window.scrollBy(0, {get_step(step_range)});")
        else:
            break
        time.sleep(random.uniform(0.02, 0.08))