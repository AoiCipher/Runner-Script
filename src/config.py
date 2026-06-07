"""
Configuration management module
Handles YAML configuration loading and directory operations
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import os
import sys
import yaml

from src.logger import get_logger
from src.path_utils import (
    get_project_root,
    get_config_dir,
    get_log_file,
    ensure_directory,
)


class ConfigManager:
    """Manages configuration file loading and validation"""

    @staticmethod
    def load(config_file: str, verbose: int = 0) -> Dict[str, Any]:
        """
        Load configuration from YAML file

        Args:
            config_file: Path to configuration file
            verbose: Verbose level (0=default, 1=silent, 2=detailed)

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        logger = get_logger(
            path=str(get_log_file()),
            verbose_level=verbose,
        )
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            logger.debug(f"Configuration loaded from {config_file}")

            return config or {}

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML config: {str(e)}")

    @staticmethod
    def validate(config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure

        Args:
            config: Configuration dictionary

        Returns:
            True if valid, raises exception otherwise
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        if "stages" not in config or not isinstance(config["stages"], list):
            raise ValueError("Configuration must contain 'stages' list")

        return True

    def config_info(self, config_id: str, verbose: int = 0) -> None:
        """Display detailed information about a specific config file

        Args:
            config_id: Configuration ID number (as string)
            verbose: Verbose level (0=default, 1=silent, 2=detailed)
        """
        if verbose == 0:
            print("This command does not require the -v --verbose flag!")
            return
        logger = get_logger(path=str(get_log_file()), verbose_level=verbose)
        try:
            config_path = self.use_config(config_id=config_id, verbose=verbose)
            data = self.load(config_file=config_path)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return

        # Extract config information
        name = data.get("name", "Unknown")
        description = data.get("description", "No description")
        version = data.get("version", "Unknown")
        author = data.get("author", "Unknown")
        variables = data.get("variables", {})
        stages = data.get("stages", [])
        script_config = data.get("script_config", {})

        # Display formatted config information
        logger.print_console("\n" + "=" * 70, "CYAN")
        logger.print_console(f"  CONFIG: {name}", "GREEN")
        logger.print_console("=" * 70, "CYAN")

        logger.info(f"Version:     {version}")
        logger.info(f"Author:      {author}")
        logger.info(f"Description: {description}")

        logger.print_console("\n📋 Script Configuration:", "CYAN")
        for key, value in script_config.items():
            logger.info(f"  • {key}: {value}")

        if variables:
            logger.print_console("\n🔧 Variables:", "CYAN")
            for var_name, var_value in variables.items():
                logger.info(f"  • {var_name}: {var_value}")

        if stages:
            logger.print_console("\n📊 Stages:", "CYAN")
            for idx, stage in enumerate(stages, 1):
                stage_name = stage.get("name", "Unknown")
                task_count = len(stage.get("tasks", []))
                logger.info(f"  [{idx}] {stage_name} ({task_count} tasks)")

        logger.print_console("\n" + "=" * 70, "CYAN")
        logger.print_console(f"Total Stages: {len(stages)}", "GREEN")
        logger.print_console("=" * 70 + "\n", "CYAN")

    @staticmethod
    def copy_config(config_path: str, verbose: int = 0):
        """Copy a config file to the config directory

        Args:
            config_path: Path to source config file
            verbose: Verbose level (0=default, 1=silent, 2=detailed)
        """
        logger = get_logger(path=str(get_log_file()), verbose_level=verbose)
        if not os.path.isfile(config_path):
            logger.error(f"Config file not found: {config_path}")
            sys.exit(1)

        destination_dir = get_config_dir()
        ensure_directory(destination_dir)
        destination_path = destination_dir / os.path.basename(config_path)

        try:
            logger.info(f"Copying {config_path} to {destination_dir}")
            with open(config_path, "r") as src_file:
                content = src_file.read()
            with open(destination_path, "w") as dst_file:
                dst_file.write(content)
            logger.info(f"Config file copied to: {destination_path}")
        except Exception as e:
            logger.error(f"Failed to copy config file: {str(e)}")
            sys.exit(1)

    @staticmethod
    def config_list(verbose: int = 0) -> str:
        """List all available config files

        Args:
            verbose: Verbose level (0=default, 1=silent, 2=detailed)
        """
        logger = get_logger(path=str(get_log_file()), verbose_level=verbose)
        config_dir = get_config_dir()
        if not config_dir.is_dir():
            logger.error(f"Config directory not found: {config_dir}")
            sys.exit(1)

        config_files = sorted(
            [f for f in config_dir.iterdir() if f.is_file() and f.suffix == ".yaml"]
        )
        if not config_files:
            logger.info("No config files found in the config directory.")
        else:
            logger.print_console("Available config files:", "CYAN")
            for idx, cfg in enumerate(config_files, 1):
                logger.info(f"  [{idx}] {cfg}")

    @staticmethod
    def use_config(config_id: int, verbose: int = 0) -> str:
        """Select a config file by ID number

        Args:
            config_id: Configuration ID number to select
            verbose: Verbose level (0=default, 1=silent, 2=detailed)

        Returns:
            Path to selected config file
        """
        logger = get_logger(path=str(get_log_file()), verbose_level=verbose)
        config_dir = get_config_dir()
        if not config_dir.is_dir():
            logger.error(f"Config directory not found: {config_dir}")
            sys.exit(1)

        config_files = sorted(
            [f for f in config_dir.iterdir() if f.is_file() and f.suffix == ".yaml"]
        )

        try:
            config_index = int(config_id) - 1
            if config_index < 0 or config_index >= len(config_files):
                logger.error(
                    f"Invalid config number: {config_id}. Available configs: 1-{len(config_files)}"
                )
                sys.exit(1)
            selected_config = config_files[config_index]
            logger.info(f"config: [{config_id}] {selected_config}")
            return os.path.join(config_dir, selected_config)
        except ValueError:
            logger.error(f"Invalid config number format: {config_id}")
            sys.exit(1)


class DirectoryManager:
    """Manages output directory creation and structure"""

    @staticmethod
    def create_directory(
        output_path: Optional[str], project_name: str, verbose: int = 0
    ) -> str:
        """
        Create and return the output directory path

        Args:
            output_path: Custom base path (uses CWD if None)
            project_name: Project name for subdirectory
            verbose: Verbose level (0=default, 1=silent, 2=detailed)

        Returns:
            Absolute path to output directory
        """
        logger = get_logger(path=str(get_log_file()), verbose_level=verbose)
        base_path = Path(output_path) if output_path else Path.cwd()
        output_dir = (
            base_path / f"{project_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            logger.debug(f"Output directory: {output_dir.absolute()}")

            return str(output_dir.absolute())

        except OSError as e:
            logger.error(f"Failed to create directory: {str(e)}")
            raise

    @staticmethod
    def ensure_subdirectories(base_dir: str, subdirs: Optional[list] = None) -> None:
        """Create standard subdirectories

        Args:
            base_dir: Base output directory
            subdirs: List of subdirectory names (default: standard set)
        """
        if subdirs is None:
            subdirs = ["results", "logs", "reports", "artifacts"]

        for subdir in subdirs:
            subdir_path = Path(base_dir) / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
