from rowdybottypiper.actions.action import Action
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import smooth_scroll_to_element, random_pause
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from typing import Optional, Callable
import os
import time
import glob


class DownloadAction(Action):
    """Click a download link/button and wait for download to complete"""
    
    def __init__(
        self,
        selector: str,
        by: str = "CSS_SELECTOR",
        download_dir: Optional[str] = None,
        expected_filename: Optional[str] = None,
        timeout: int = 60,
        scroll_to_element: bool = True,
        verify_download: bool = True,
        wait_time: Optional[float] = 5.0,
        **kwargs
    ):
        """
        Initialize DownloadAction
        
        Args:
            selector: CSS selector (or other) for download button/link
            by: Selector type (CSS_SELECTOR, XPATH, ID, etc.)
            download_dir: Directory where files are downloaded (defaults to Chrome's download dir)
            expected_filename: Expected filename to verify (can use wildcards like '*.pdf')
            timeout: Seconds to wait for download to complete
            scroll_to_element: Whether to scroll to download button before clicking
            verify_download: Whether to verify file was downloaded successfully
            **kwargs: Additional Action parameters
        """
        super().__init__("Download", **kwargs)
        self.selector = selector
        self.by = by
        self.download_dir = download_dir or self._get_default_download_dir()
        self.expected_filename = expected_filename
        self.timeout = timeout
        self.scroll_to_element = scroll_to_element
        self.verify_download = verify_download
        self.wait_time = wait_time
    
    def _get_default_download_dir(self) -> str:
        """Get the default Chrome download directory"""
        # This will be overridden if Chrome options specify a download dir
        if os.name == 'nt':  # Windows
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        else:  # Linux/Mac
            return os.path.join(os.path.expanduser('~'), 'Downloads')
    
    def _get_by_type(self, by: str):
        """Convert string to Selenium By type"""
        by_map = {
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "XPATH": By.XPATH,
            "ID": By.ID,
            "CLASS_NAME": By.CLASS_NAME,
            "NAME": By.NAME,
            "LINK_TEXT": By.LINK_TEXT,
            "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT
        }
        return by_map.get(by.upper(), By.CSS_SELECTOR)
    
    def _get_download_files_before(self) -> set:
        """Get list of files in download directory before download"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            return set()
        
        files = set(os.listdir(self.download_dir))
        if self.logger:
            self.logger.debug(f"Files before download", count=len(files))
        return files
    
    def _wait_for_download_complete(self, files_before: set) -> Optional[str]:
        """
        Wait for download to complete and return the downloaded filename
        
        Args:
            files_before: Set of files that existed before download started
            
        Returns:
            Downloaded filename if found, None otherwise
        """
        if self.logger:
            self.logger.info("Waiting for download to complete", timeout=self.timeout)
        
        start_time = time.time()
        downloaded_file = None
        
        while time.time() - start_time < self.timeout:
            # Check for .crdownload or .tmp files (download in progress)
            temp_files = glob.glob(os.path.join(self.download_dir, '*.crdownload')) + \
                        glob.glob(os.path.join(self.download_dir, '*.tmp'))
            
            if temp_files:
                if self.logger:
                    self.logger.debug("Download in progress", temp_files=len(temp_files))
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
                        if self.logger:
                            self.logger.info("Download completed", filename=downloaded_file)
                        return downloaded_file
                    else:
                        if self.logger:
                            self.logger.debug(
                                "New file found but doesn't match expected",
                                found=downloaded_file,
                                expected=self.expected_filename
                            )
                else:
                    # No expected filename, just return the new file
                    if self.logger:
                        self.logger.info("Download completed", filename=downloaded_file)
                    return downloaded_file
            
            time.sleep(1)
        
        if self.logger:
            self.logger.error("Download timeout", timeout=self.timeout)
        return None
    
    def _get_file_size(self, filename: str) -> int:
        """Get file size in bytes"""
        filepath = os.path.join(self.download_dir, filename)
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        by_type = self._get_by_type(self.by)
        
        try:
            if self.logger:
                self.logger.info("Starting download", selector=self.selector)
            
            # Get files before download
            files_before = self._get_download_files_before()
            
            # Find download button/link
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by_type, self.selector))
            )
            
            # Scroll to element if enabled
            if self.scroll_to_element:
                smooth_scroll_to_element(driver, element)
                random_pause(lower=0.3, upper=self.wait_time)
            
            # Click to start download
            element.click()
            
            if self.logger:
                self.logger.info("Download triggered")
            
            # Small pause after clicking
            random_pause(lower=1.0, upper=self.wait_time)
            
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
                    
                    if self.logger:
                        self.logger.info(
                            "Download verified",
                            filename=downloaded_file,
                            size_mb=round(file_size / (1024 * 1024), 2)
                        )
                    
                    return True
                else:
                    if self.logger:
                        self.logger.error("Download verification failed")
                    return False
            else:
                # Not verifying, just assume success
                if self.logger:
                    self.logger.info("Download triggered (verification disabled)")
                return True
        
        except Exception as e:
            if self.logger:
                self.logger.error("Download failed", error=str(e))
            return False


class DownloadMultipleAction(Action):
    """Download multiple files in sequence"""
    
    def __init__(
        self,
        selectors: list,
        by: str = "CSS_SELECTOR",
        download_dir: Optional[str] = None,
        timeout: int = 60,
        wait_time: Optional[float] = 5.0,
        **kwargs
    ):
        """
        Initialize DownloadMultipleAction
        
        Args:
            selectors: List of CSS selectors for download buttons/links
            by: Selector type
            download_dir: Directory where files are downloaded
            timeout: Seconds to wait for each download
            pause_between_downloads: (min, max) seconds to pause between downloads
            **kwargs: Additional Action parameters
        """
        super().__init__("DownloadMultiple", **kwargs)
        self.selectors = selectors
        self.by = by
        self.download_dir = download_dir or self._get_default_download_dir()
        self.timeout = timeout
        self.pause_between_downloads = (2.0,wait_time)
    
    def _get_default_download_dir(self) -> str:
        """Get the default Chrome download directory"""
        if os.name == 'nt':  # Windows
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        else:
            return os.path.join(os.path.expanduser('~'), 'Downloads')
    
    def execute(self, driver: webdriver.Chrome, context: BotContext) -> bool:
        downloaded_files = []
        
        if self.logger:
            self.logger.info("Starting multiple downloads", count=len(self.selectors))
        
        for i, selector in enumerate(self.selectors):
            if self.logger:
                self.logger.info(f"Downloading file {i+1}/{len(self.selectors)}")
            
            # Create a single download action
            download_action = DownloadAction(
                selector=selector,
                by=self.by,
                download_dir=self.download_dir,
                timeout=self.timeout,
                verify_download=True
            )
            download_action.set_logger(self.logger)
            
            # Execute download
            success = download_action.execute(driver, context)
            
            if success:
                # Get download info from context
                download_info = context.get('last_download')
                if download_info:
                    downloaded_files.append(download_info)
            else:
                if self.logger:
                    self.logger.warning(f"Failed to download file {i+1}")
            
            # Pause between downloads (except after last one)
            if i < len(self.selectors) - 1:
                random_pause(
                    lower=self.pause_between_downloads[0],
                    upper=self.pause_between_downloads[1]
                )
        
        # Store all downloads in context
        context.set('downloads', downloaded_files)
        context.set('download_count', len(downloaded_files))
        
        if self.logger:
            self.logger.info(
                "Multiple downloads completed",
                successful=len(downloaded_files),
                total=len(self.selectors)
            )
        
        return len(downloaded_files) > 0