import random
import time
from typing import Optional
import string


async def sim_alpha_fat_finger(inchar):
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

async def sim_num_fat_finger(inchar):
    return random.choice([str(abs(int(inchar)-1))[-1],str(abs(int(inchar)+1))[-1]])

async def slow_typing(element, text, error_chance=0.06, delay_range=(0.2,0.5),error_delay=(0.1,0.5)):
    print(f"typing: {text}")
    for char in text:
        print(f"typing {char}")
        if random.random()<error_chance:
            print(f"typo trigger")
            if char.isalpha():
                await element.send_keys(sim_alpha_fat_finger(char))
                time.sleep(random.uniform(*error_delay))
                await element.send_keys('\b')
                time.sleep(random.uniform(*delay_range))
            elif char.isdigit():
                await element.send_keys(sim_num_fat_finger(char))
                time.sleep(random.uniform(*error_delay))
                await element.send_keys('\b')
                time.sleep(random.uniform(*delay_range))
            else:
                continue
        await element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

async def random_pause(lower: float = 0.2, upper: float = 4.0):
    """
    Simple random pause utility
    
    Args:
        lower: Minimum wait time (seconds)
        upper: Maximum wait time (seconds)
    """
    time.sleep(random.uniform(lower, upper))