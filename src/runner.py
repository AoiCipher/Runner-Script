"""
Workflow execution engine
Handles command execution from configuration
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.logger import get_logger


class WorkflowRunner:
    """Script execution workflow stages and tasks"""

    def __init__(self, config: Dict[str, Any], output_dir: str, verbose: int = 0):
        """
        Initialize workflow runner

        Args:
            config: Configuration dictionary
            output_dir: Output directory path
            verbose: Verbose level (0=default, 1=silent, 2=detailed)
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        # Create log path within output directory: {output_dir}/log/RunnerScript.log
        log_path = self.output_dir / "log" / "RunnerScript.log"
        self.logger = get_logger(path=str(log_path), verbose_level=verbose)
        self.variables = config.get("variables", {})
        self.config_settings = config.get("script_config", {})

    def execute(self) -> None:
        """Execute the complete workflow with dependency handling"""
        stages = self.config.get("stages", [])

        if not stages:
            self.logger.warning("No stages defined in configuration")
            return

        completed_stages: Set[str] = set()
        total_stages = len(stages)

        for idx, stage in enumerate(stages, 1):
            stage_name = stage.get("name", "unknown")

            # Check dependencies
            depends_on = stage.get("depends_on", [])
            if depends_on:
                missing_deps = [
                    dep for dep in depends_on if dep not in completed_stages
                ]
                if missing_deps:
                    self.logger.warning(
                        f"Skipping stage '{stage_name}': unmet dependencies {missing_deps}"
                    )
                    continue

            stage_success = self._execute_stage(stage, idx, total_stages)
            if not stage_success:
                # Stage failed and stop_on_failure is enabled
                if self.config_settings.get("stop_on_failure", False):
                    self.logger.error(
                        f"Workflow stopped due to stage failure: {stage_name}"
                    )
                    return
            completed_stages.add(stage_name)

    def _execute_stage(
        self, stage: Dict[str, Any], stage_num: int, total_stages: int
    ) -> bool:
        """
        Execute a single workflow stage

        Args:
            stage: Stage configuration
            stage_num: Current stage number
            total_stages: Total number of stages

        Returns:
            True if stage completed successfully, False if it failed and stop_on_failure is set
        """
        stage_name = stage.get("name", "unknown")
        self.logger.info(f"[{stage_num}/{total_stages}] Executing stage: {stage_name}")

        tasks = stage.get("tasks", [])
        is_parallel = stage.get("parallel", False)

        if is_parallel:
            return self._execute_tasks_parallel(tasks)
        else:
            return self._execute_tasks_sequential(tasks)

    def _execute_tasks_sequential(self, tasks: List[Dict[str, Any]]) -> bool:
        """
        Execute tasks sequentially

        Args:
            tasks: List of task configurations

        Returns:
            True if all tasks succeeded, False if any failed and stop_on_failure is set
        """
        for task_idx, task in enumerate(tasks, 1):
            task_success = self._execute_task_with_retry(task, task_idx, len(tasks))
            if not task_success:
                # Task failed - check if we should stop
                if self.config_settings.get("stop_on_failure", False):
                    return False
        return True

    def _execute_tasks_parallel(self, tasks: List[Dict[str, Any]]) -> bool:
        """
        Execute tasks in parallel using ThreadPoolExecutor

        Args:
            tasks: List of task configurations

        Returns:
            True if all tasks succeeded, False if any failed and stop_on_failure is set
        """

        if self.config_settings.get("thread_count") == 0:
            max_workers = len(tasks)
        else:
            max_workers = self.config_settings.get("thread_count", 4)

        self.logger.info(f"  Executing {len(tasks)} tasks in parallel")
        self.logger.debug(
            f"  Parallel execution enabled - using up to {max_workers} threads"
        )
        self.logger.warning(
            "  If your tool is CPU-heavy, consider setting 'parallel' to false for better performance, and if your tool requires internet access, it may slow down your internet due to multiple requests being made simultaneously."
        )

        failed_tasks = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(
                    self._execute_task_with_retry, task, idx + 1, len(tasks)
                ): task
                for idx, task in enumerate(tasks)
            }

            # Wait for all tasks to complete
            for future in as_completed(future_to_task):
                try:
                    task_success = future.result()
                    if not task_success:
                        failed_tasks.append(
                            future_to_task[future].get("name", "unknown")
                        )
                except Exception as e:
                    self.logger.error(f"Task execution failed: {str(e)}")
                    failed_tasks.append(future_to_task[future].get("name", "unknown"))

        # Check if we should stop due to failures
        if failed_tasks and self.config_settings.get("stop_on_failure", False):
            return False

        return True

    def _execute_task_with_retry(
        self, task: Dict[str, Any], task_num: int, total_tasks: int
    ) -> bool:
        """
        Execute a task with retry logic based on failure policy

        Args:
            task: Task configuration
            task_num: Current task number
            total_tasks: Total tasks in stage

        Returns:
            True if task succeeded, False if it failed
        """
        task_name = task.get("name", "unknown")

        # Failure handling policy logic:
        # 1. If continue_on_failure=true: Skip failed task, don't retry, continue
        # 2. If stop_on_failure=true AND retry_failed_tasks=true: Retry on failure
        # 3. If stop_on_failure=true AND retry_failed_tasks=false: Stop on failure, no retry

        continue_on_failure = self.config_settings.get("continue_on_failure", False)
        stop_on_failure = self.config_settings.get("stop_on_failure", False)
        retry_failed_tasks = self.config_settings.get("retry_failed_tasks", False)
        retry_count = self.config_settings.get("retry", 1)

        # If continue_on_failure is enabled, just execute once (no retries)
        if continue_on_failure:
            return self._execute_task(task, task_num, total_tasks)

        # If stop_on_failure and retry_failed_tasks are both enabled, retry on failure
        if stop_on_failure and retry_failed_tasks and retry_count > 1:
            for attempt in range(1, retry_count + 1):
                self.logger.info(
                    f"  [{task_num}/{total_tasks}] {task_name} - Attempt {attempt}/{retry_count}"
                )
                task_success = self._execute_task(task, task_num, total_tasks)
                if task_success:
                    return True
                else:
                    if attempt < retry_count:
                        self.logger.warning(
                            f"  [{task_num}/{total_tasks}] {task_name} failed on attempt {attempt}, retrying..."
                        )
            return False

        # Default: Just execute once
        return self._execute_task(task, task_num, total_tasks)

    def _execute_task(
        self, task: Dict[str, Any], task_num: int, total_tasks: int
    ) -> bool:
        """
        Execute a single task (no retry logic here)

        Args:
            task: Task configuration
            task_num: Current task number
            total_tasks: Total tasks in stage

        Returns:
            True if task succeeded, False if it failed
        """
        task_name = task.get("name", "unknown")
        command = task.get("command", "").strip()

        if not command:
            self.logger.warning(
                f"  [{task_num}/{total_tasks}] {task_name}: No command defined"
            )
            return False

        # Substitute variables in command
        command = self._substitute_variables(command)

        self.logger.info(f"  [{task_num}/{total_tasks}] {task_name}")
        self.logger.debug(f"  Command: {command}")

        try:
            # Determine whether to capture output based on verbose level
            capture_output = self.verbose != 2

            if (
                self.config_settings.get("timeout", 3600) == -1
            ):  # if -1 is set, disable timeout
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(self.output_dir),
                    capture_output=capture_output,
                    text=True,
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(self.output_dir),
                    capture_output=capture_output,
                    text=True,
                    timeout=self.config_settings.get("timeout", 3600),
                )

            if result.returncode == 0:
                self.logger.success(f"  ✓ {task_name} completed")
                return True
            else:
                self.logger.warning(
                    f"  ⚠ {task_name} finished with code {result.returncode}"
                )
                if result.stderr:
                    self.logger.debug(f"  Error: {result.stderr[:500]}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(
                f"  ✗ {task_name} timed out (exceeded {self.config_settings.get('timeout', 3600)}s)"
            )
            return False
        except Exception as e:
            self.logger.error(f"  ✗ {task_name} failed: {str(e)}")
            return False

    def _substitute_variables(self, command: str) -> str:
        """
        Replace variable placeholders in command

        Args:
            command: Command string with {var} placeholders

        Returns:
            Command with variables substituted
        """
        for var_name, var_value in self.variables.items():
            placeholder = f"{{{var_name}}}"
            command = command.replace(placeholder, str(var_value))

        return command
