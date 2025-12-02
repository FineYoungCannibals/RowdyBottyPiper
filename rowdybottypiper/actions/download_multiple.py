from rowdybottypiper.actions.action import Action
from rowdybottypiper.actions.download import DownloadAction
from rowdybottypiper.core.context import BotContext
from rowdybottypiper.utils.realistic import random_pause
from selenium import webdriver
from typing import Optional
import os

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