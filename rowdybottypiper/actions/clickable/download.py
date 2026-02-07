from pydantic import Field
from typing import Literal, Optional
from selenium import webdriver
import os
import time
import glob

from rowdybottypiper.actions.clickable.base import ClickableAction
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import random_pause


class DownloadAction(ClickableAction):
    """Click a download link/button and wait for download to complete"""
    
    type: Literal["DownloadAction"] = "DownloadAction"
    
    download_dir: str 
    expected_filename: Optional[str] = None
    timeout: int = Field(default=180, ge=1)
    verify_download: bool = True
    
    def model_post_init(self, __context):
        """Set up download dir after initialization"""
        super().model_post_init(__context)
        if self.download_dir is None:
            self.download_dir = self._get_default_download_dir()
    
    def _get_default_download_dir(self) -> str:
        """Get the default Chrome download directory"""
        if os.name == 'nt':  # Windows
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        else:  # Linux/Mac
            return os.path.join(os.path.expanduser('~'), 'Downloads')
    
    def _get_download_files_before(self) -> set:
        """Get list of files in download directory before download"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            return set()
        
        files = set(os.listdir(self.download_dir))
        return files
    
    def _wait_for_download_complete(self, files_before: set) -> Optional[str]:
        """
        Wait for download to complete and return the downloaded filename
        
        Args:
            files_before: Set of files that existed before download started
            
        Returns:
            Downloaded filename if found, None otherwise
        """
        start_time = time.time()
        downloaded_file = None
        
        while time.time() - start_time < self.timeout:
            # Check for .crdownload or .tmp files (download in progress)
            temp_files = glob.glob(os.path.join(self.download_dir, '*.crdownload')) + \
                        glob.glob(os.path.join(self.download_dir, '*.tmp'))
            
            if temp_files:
                time.sleep(1)
                continue
            
            # Get current files
            files_after = set(os.listdir(self.download_dir))
            new_files = files_after - files_before
            
            if new_files:
                downloaded_file = list(new_files)[0]
                
                # If expected filename is specified, verify it matches
                if self.expected_filename:
                    import fnmatch
                    if fnmatch.fnmatch(downloaded_file, self.expected_filename):
                        return downloaded_file
                else:
                    # No expected filename, just return the new file
                    return downloaded_file
            
            time.sleep(1)
        
        return None
    
    def _get_file_size(self, filename: str) -> int:
        """Get file size in bytes"""
        filepath = os.path.join(self.download_dir, filename)
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        try:
            # Get files before download
            files_before = self._get_download_files_before()
            
            # Click to start download (uses inherited _find_and_click_element)
            self._find_and_click_element(driver)
            
            # Small pause after clicking
            random_pause(self.wait_lower, self.wait_upper)
            
            # Wait for download to complete if verification is enabled
            if self.verify_download:
                downloaded_file = self._wait_for_download_complete(files_before)
                
                if downloaded_file:
                    filepath = os.path.join(self.download_dir, downloaded_file)
                    file_size = self._get_file_size(downloaded_file)
                    
                    # Store download info in context
                    context.set('last_download', {
                        'filename': downloaded_file,
                        'filepath': filepath,
                        'size_bytes': file_size,
                        'download_dir': self.download_dir
                    })
                    
                    return True
                else:
                    return False
            else:
                # Not verifying, just assume success
                return True
        
        except Exception as e:
            return False