"""
Path utilities for absolute path management
Ensures all paths are absolute for pipx compatibility
"""

from pathlib import Path
import os
import sys


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.
    Works regardless of where the script is run from.

    Returns:
        Path object pointing to project root
    """
    # Get the directory where this module is located (src/)
    src_dir = Path(__file__).resolve().parent
    # Go up one level to get project root
    project_root = src_dir.parent
    return project_root


def get_logs_dir() -> Path:
    """
    Get the absolute path to the logs directory.

    Returns:
        Path object pointing to logs directory
    """
    return get_project_root() / "logs"


def get_config_dir() -> Path:
    """
    Get the absolute path to the config directory.

    Returns:
        Path object pointing to config directory
    """
    return get_project_root() / "config"


def get_log_file(filename: str = "RunnerScript.log") -> Path:
    """
    Get the absolute path to a log file.

    Args:
        filename: Name of the log file

    Returns:
        Path object pointing to the log file
    """
    return get_logs_dir() / filename


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists, creating parent directories as needed.

    Args:
        path: Path object to create
    """
    path.mkdir(parents=True, exist_ok=True)
