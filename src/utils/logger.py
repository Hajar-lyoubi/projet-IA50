import logging
import sys
from pathlib import Path

def setup_logger(name: str = "cvrptw_solver", log_file: str = "solver.log", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with console and file handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.hasHandlers():
        return logger
        
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except IOError:
        print(f"Warning: Could not create log file {log_file}")
        
    return logger

# Global logger instance
logger = setup_logger()
