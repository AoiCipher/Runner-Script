"""Workflow execution and orchestration"""

import os
import sys
from src.config import ConfigManager, DirectoryManager
from src.runner import WorkflowRunner


class WorkflowExecutor:
    """Handle workflow execution and configuration management"""

    def __init__(self, logger):
        """Initialize the executor with a logger"""
        self.logger = logger
        self.config_manager = ConfigManager()

    def handle_config_operations(self, args):
        """Handle configuration-only operations (copy, list, info)"""
        if args.copy_config:
            return self.config_manager.copy_config(
                config_path=args.copy_config, verbose=args.verbose
            )

        if args.config_list:
            return self.config_manager.config_list(args.verbose)

        if args.config_info:
            self.config_manager.config_info(
                config_id=args.config_info, verbose=args.verbose
            )
            return

    def validate_project_requirement(self, args):
        """Validate that project argument is provided when required"""
        if not (args.copy_config or args.config_list or args.config_info or args.chain):
            if not args.project:
                self.logger.error("Error: -p/--project is required for this operation.")
                self.logger.info(
                    "Use -h for help or use -cl, -uc, or -cc for special commands that don't require -p"
                )
                sys.exit(1)

    def run_chained_configs(self, args):
        """Execute multiple chained configuration files"""
        if not args.project:
            self.logger.error("Error: -p/--project is required when chaining configs.")
            sys.exit(1)

        # Create output directory once for all configs
        output_dir = DirectoryManager.create_directory(
            args.output, args.project, args.verbose
        )
        self.logger.info(f"Project: {args.project}")
        self.logger.info(f"Output directory: {output_dir}")
        self.logger.print_console(
            f"\nRunning {len(args.chain)} chained configs...", "CYAN"
        )

        for idx, config_file in enumerate(args.chain, 1):
            if not os.path.exists(config_file):
                self.logger.error(f"Configuration file not found: {config_file}")
                sys.exit(1)

            self.logger.print_console(
                f"\n[{idx}/{len(args.chain)}] Running config: {config_file}",
                "CYAN",
            )
            config = self.config_manager.load(config_file, args.verbose)

            # Execute workflow with same output directory
            runner = WorkflowRunner(config, output_dir, args.verbose)
            runner.execute()

        self.logger.print_console(
            "\nAll chained configs completed successfully. Check logs and output directory for results.",
            "GREEN",
        )

    def run_single_workflow(self, args):
        """Execute a single workflow with the given configuration"""
        # Load configuration
        if not os.path.exists(args.config):
            self.logger.error(f"Configuration file not found: {args.config}")
            sys.exit(1)

        if args.use_config:
            config = self.config_manager.use_config(
                config_id=args.use_config, verbose=args.verbose
            )
            config = self.config_manager.load(config, args.verbose)
        else:
            config = self.config_manager.load(args.config, args.verbose)

        # Create output directory
        output_dir = DirectoryManager.create_directory(
            args.output, args.project, args.verbose
        )

        self.logger.info(f"Project: {args.project}")
        self.logger.info(f"Output directory: {output_dir}")

        # Execute workflow
        runner = WorkflowRunner(config, output_dir, args.verbose)
        runner.execute()

        self.logger.print_console(
            "\nEnd of script execution workflow. Check logs and output directory for results.",
            "GREEN",
        )

    def execute(self, args):
        """Main execution logic - routes to appropriate handler"""
        # Handle config-only operations
        if args.copy_config or args.config_list or args.config_info:
            return self.handle_config_operations(args)

        # Validate project requirement for other operations
        self.validate_project_requirement(args)

        # Handle chaining multiple configs
        if args.chain:
            return self.run_chained_configs(args)

        # Default: run single workflow
        return self.run_single_workflow(args)
