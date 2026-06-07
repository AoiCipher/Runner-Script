"""Command-line argument parsing for RunnerScript"""

import argparse
from src.banner import BannerHelpAction


class ArgumentParser:
    """Handle command-line argument parsing"""

    @staticmethod
    def create_parser():
        """Create and configure the argument parser"""
        parser = argparse.ArgumentParser(
            description="RunnerScript - Professional Script Execution Automation, for chaining multiple tools in a Hacking workflow.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False,
            epilog="""
Examples:
    python rs.py -cl
    python rs.py -cc ./my_config.yaml
    python rs.py -uc 1
    python Rs.py -p myproject
    python Rs.py -p myproject -c ./config.yaml -v 2
    python Rs.py -p myproject -o /custom/output/path -v 1
    python rs.py -p myproject -ch config1.yaml config2.yaml -o custompth
            """,
        )
        
        ArgumentParser._add_arguments(parser)
        return parser

    @staticmethod
    def _add_arguments(parser):
        """Add arguments to the parser"""
        parser.add_argument(
            "-h",
            "--help",
            action=BannerHelpAction,
            help="Show this help message with banner",
        )
        parser.add_argument(
            "-p",
            "--project",
            type=str,
            required=False,
            help="Project name for output directory (required unless using -cl, -uc, or -cc)",
        )
        parser.add_argument(
            "-c",
            "--config",
            type=str,
            default="config/default-config.yaml",
            help="Path to configuration file",
        )
        parser.add_argument(
            "-o", "--output", type=str, help="Custom output directory path"
        )
        parser.add_argument(
            "-S",
            "--silent",
            action="store_true",
            help="Silent mode (no console output)",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            type=int,
            nargs="?",
            const=2,
            default=1,
            choices=[0, 1, 2],
            help="Verbose level: 0 = silent, 1 = default (same as no flag), 2 = detailed (script output to console)",
        )
        parser.add_argument("--version", action="version", version="RunnerScript 1.0.0")
        parser.add_argument(
            "-cc",
            "--copy-config",
            type=str,
            metavar="FILE",
            help="Copy a config file to RunnerScript config folder (e.g., -cc ./my_config.yaml)",
        )
        parser.add_argument(
            "-cl",
            "--config-list",
            action="store_true",
            help="List all your config file in RunnerScript config folder",
        )
        parser.add_argument(
            "-uc",
            "--use-config",
            type=str,
            help="Use a config file from RunnerScript config folder by specifying the Config number, example: -uc 1",
        )
        parser.add_argument(
            "-cf", "--config-info", type=str, help="Show information of the config"
        )
        parser.add_argument(
            "-ch",
            "--chain",
            type=str,
            nargs="+",
            metavar="CONFIG",
            help="Chain multiple config files to run sequentially (e.g., -ch config1.yaml config2.yaml)",
        )

    @staticmethod
    def parse_args():
        """Parse command-line arguments"""
        parser = ArgumentParser.create_parser()
        return parser.parse_args()
