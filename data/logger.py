import logging
import os
from datetime import datetime

def get_logger(name="AppLogger"):
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Create a unique log file for today
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join("logs", f"app_{date_str}.log")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding duplicate handlers if get_logger is called multiple times
    if not logger.handlers:
        # File handler (writes everything to the log file)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler (prints warnings and errors to the terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatting
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger