"""
Custom logging module with verbose level handling
Provides prettier output when verbose is disabled
"""

import sys
from pathlib import Path
from typing import Optional

import colorama
from loguru import logger as loguru_logger

from src.path_utils import get_logs_dir, ensure_directory


class VerboseLogger:
    """
    Handles logging with different verbose levels:
    - 0: Silent mode (no output)
    - 1: Normal mode (console and file logging at INFO level)
    - 2: Detailed mode (console and file logging at DEBUG level)
    """

    def __init__(self, path: str, verbose_level: int = 0):
        """
        Initialize logger with verbose level

        Args:
            path: Path to the log file
            verbose_level: 0 (silent), 1 (normal), 2 (detailed)
        """
        self.path = path
        self.verbose_level = verbose_level
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging based on verbose level"""
        # Remove default loguru handler
        loguru_logger.remove()

        # Use the path parameter if provided, otherwise default to logs
        if isinstance(self.path, str):
            log_path = Path(self.path)
        else:
            log_path = get_logs_dir() / "RunnerScript.log"

        # Ensure parent directory exists
        if log_path.suffix:  # If it's a file path
            log_dir = log_path.parent
        else:  # If it's a directory path
            log_dir = log_path
            log_path = log_path / "RunnerScript.log"

        ensure_directory(log_dir)

        if self.verbose_level == 0:
            # Silent mode: no console output, minimal file logging
            loguru_logger.add(
                log_path,
                rotation="10 MB",
                retention="7 days",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                level="WARNING",
            )
        elif self.verbose_level == 1:
            # Normal mode: console output (INFO) and file logging
            loguru_logger.add(
                sys.stderr,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
                level="INFO",
            )
            loguru_logger.add(
                log_path,
                rotation="10 MB",
                retention="7 days",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                level="INFO",
            )
        elif self.verbose_level == 2:
            # Detailed: full output to both stderr and file
            loguru_logger.add(
                sys.stderr,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
                level="DEBUG",
            )
            loguru_logger.add(
                log_path,
                rotation="10 MB",
                retention="7 days",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                level="DEBUG",
            )

    def info(self, message: str):
        """Log info message"""
        loguru_logger.info(message)

    def debug(self, message: str):
        """Log debug message"""
        loguru_logger.debug(message)

    def warning(self, message: str):
        """Log warning message"""
        loguru_logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        loguru_logger.error(message)

    def success(self, message: str):
        """Log success message"""
        loguru_logger.success(message)

    def print_console(self, message: str, color: str = "WHITE"):
        """
        Print directly to console (prettier output)

        Args:
            message: Message to print
            color: Colorama color (CYAN, GREEN, YELLOW, RED, etc.)
        """
        if self.verbose_level == 0:
            return
        color_attr = getattr(colorama.Fore, color, colorama.Fore.WHITE)
        print(color_attr + message)


def get_logger(path: str, verbose_level: int = 0) -> VerboseLogger:
    """
    Factory function to get a logger instance

    Args:
        path: Path to the log file
        verbose_level: 0 (silent), 1 (normal), 2 (detailed)

    Returns:
        VerboseLogger instance
    """
    return VerboseLogger(path=path, verbose_level=verbose_level)
