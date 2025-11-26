import logging
# Logging Configuration Helper

def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = False,
    log_file_path: str = "bot_execution.log",
    json_format: bool = True
):
    """
    Configure logging for the framework
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file
        log_file_path: Path to log file
        json_format: Whether to use JSON format (recommended for K8s)
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        logger.addHandler(file_handler)