"""
Utility functions for the HEX Automation Hub

This module provides common utility functions used across all automation modules,
including configuration loading, logging setup, and signal handling.

Functions:
    load_config: Load configuration from JSON file
    setup_logging: Set up logging based on configuration
    graceful_shutdown: Handle graceful shutdown signals
    setup_signal_handlers: Set up signal handlers for graceful shutdown
    get_current_timestamp: Get current timestamp in ISO format
    format_error_message: Format error message for logging/notification
    validate_config: Validate configuration structure
    create_data_directory: Create data directory if it doesn't exist

Example:
    config = load_config('config.json')
    logger = setup_logging(config)
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import signal
import sys
from datetime import datetime

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {str(e)}")

def setup_logging(config: Dict[str, Any]):
    """Set up logging based on configuration"""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'app.log')
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def graceful_shutdown(signum, frame):
    """Handle graceful shutdown signals"""
    print(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def format_error_message(error: Exception) -> str:
    """Format error message for logging/notification"""
    return f"{type(error).__name__}: {str(error)}"

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure"""
    required_sections = ['web_scraper', 'api', 'browser', 'rpa', 'social_bots']
    
    for section in required_sections:
        if section not in config:
            return False
    
    return True

def create_data_directory(path: str) -> bool:
    """Create data directory if it doesn't exist"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory: {str(e)}")
        return False