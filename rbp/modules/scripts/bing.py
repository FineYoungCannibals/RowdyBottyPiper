from seleniumbase import SB                                                                                                                 
import uuid
import random
import string
from pathlib import Path


filename = Path(__file__).stem

def generate_random_lowercase_string():
    length = random.randint(8,12)
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string

def handle_progress_callback(progress_callback):
    if progress_callback:
        return progress_callback(1)

def handle_filedownload_callback(on_file_downloaded, fpath):
    if on_file_downloaded:
        return on_file_downloaded(fpath)
    

def run(config, progress_callback=None, file_download_callback=None):
    with SB(uc=True, browser='brave') as sb:  # uc=True enables undetected mode
        # 1. Navigate to login page
        #@rbp_progbar_counter
        print("1. Navigating to login page...")
        sb.open("https://www.bing.com")
        handle_progress_callback(progress_callback)
        sb.sleep(5)

        #@rbp_progbar_counter
        print("2. Taking Screenshot")
        fname = f"rbpss_{filename}_{str(uuid.uuid4())[-6:]}.png"
        download_path = Path.home() / 'Downloads' / fname 
        sb.save_screenshot(fname, folder=Path.home() / 'Downloads') 
        handle_filedownload_callback(file_download_callback, download_path)
        print("file download callback done")
        sb.sleep(5)
        handle_progress_callback(progress_callback)
        print("\n✓ Workflow completed successfully!")
        return "Success"