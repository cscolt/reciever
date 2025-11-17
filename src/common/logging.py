#!/usr/bin/env python3
"""
Centralized logging configuration for Desktop Casting Receiver
"""

import logging
import sys
from typing import Optional
from .config import LoggingConfig


def setup_logging(config: Optional[LoggingConfig] = None):
    """
    Setup logging with the provided configuration

    Args:
        config: LoggingConfig instance. If None, uses default settings.
    """
    if config is None:
        config = LoggingConfig()

    # Convert string level to logging constant
    level = getattr(logging, config.level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(config.format)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if specified
    if config.file:
        try:
            file_handler = logging.FileHandler(config.file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            logging.info(f"Logging to file: {config.file}")
        except Exception as e:
            logging.error(f"Failed to setup file logging: {e}")

    logging.info(f"Logging configured at {config.level} level")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
