#!/usr/bin/env python3

import sys
import colorama

from src.banner import print_banner
from src.cli_parser import ArgumentParser
from src.logger import get_logger
from src.workflow_executor import WorkflowExecutor
from src.path_utils import get_log_file


class ReconApplication:
    """Main application controller"""

    def __init__(self):
        """Initialize the application"""
        colorama.init(autoreset=True)
        print_banner()

        self.args = ArgumentParser.parse_args()
        self.logger = get_logger(
            path=str(get_log_file()), verbose_level=self.args.verbose
        )
        self.executor = WorkflowExecutor(self.logger)

    def run(self):
        """Execute the workflow"""
        try:
            self.executor.execute(self.args)
        except KeyboardInterrupt:
            self.logger.print_console("\n\nWorkflow interrupted by user....", "YELLOW")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Fatal error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    app = ReconApplication()
    app.run()
