"""
Helper utilities for the financial toolkit.
"""

import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from dotenv import load_dotenv


def setup_logging(level: str = "INFO", log_file: str = None):
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path to save logs
    """
    logger.remove()  # Remove default handler
    
    # Console handler
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # File handler
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level=level,
            rotation="10 MB"
        )
    
    logger.info(f"Logging initialized at {level} level")


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dictionary with configuration values
    """
    # Load .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded configuration from .env file")
    
    config = {
        'alpha_vantage_api_key': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'polygon_api_key': os.getenv('POLYGON_API_KEY'),
        'default_cache_dir': os.getenv('DEFAULT_CACHE_DIR', './cache'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    }
    
    return config


def ensure_dir(directory: str) -> Path:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
    
    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path
