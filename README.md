# RunnerScript

A professional workflow automation tool designed for chaining and orchestrating multiple tools in sophisticated, multi-stage execution pipelines. RunnerScript enables seamless tool orchestration for ANY workflow—whether security reconnaissance, data processing, CI/CD pipelines, or custom automation—through YAML-based configuration files.

## Overview

RunnerScript is a powerful, flexible automation framework that allows developers and engineers to define, manage, and execute complex multi-stage workflows. It handles parallel task execution, sequential dependencies, tool chaining, and comprehensive logging with support for project-based output organization. While security reconnaissance is a primary use case, RunnerScript can orchestrate ANY workflow requiring multiple tools to be chained together with controlled execution order and dependencies.

## Features

- **YAML-Based Configuration**: Define complex multi-tool workflows using simple, readable YAML files
- **Flexible Stage Design**: Create stages for ANY type of workflow—reconnaissance, data processing, automation, CI/CD, etc.
- **Parallel & Sequential Execution**: Run multiple tasks simultaneously within a stage OR sequentially, as needed
- **Dependency Management**: Control task execution order with `depends_on` relationships between stages
- **Tool Chaining**: Chain multiple commands together, pass data between tools, and build complex workflows
- **Multiple Tool Integration**: Execute any command-line tool, script, or custom application
- **Project Organization**: Automatic output directory management per project
- **Comprehensive Logging**: Detailed logs with configurable verbosity levels
- **Configuration Management**: Manage, list, and copy predefined configurations
- **Chained Execution**: Execute multiple configuration files in sequence with shared output
- **Timeout Control**: Global timeout settings for workflow execution
- **Colored Console Output**: Enhanced readability with color-coded output

## Installation

### Requirements

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/AoiCipher/Runner-Script
cd Runner-Script
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the main script executable (Linux/macOS):
```bash
chmod +x rs.py
```

## Usage

### Basic Syntax

```bash
python rs.py [OPTIONS]
```

### Command Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--project` | `-p` | STRING | Project name for output directory |
| `--config` | `-c` | PATH | Path to configuration YAML file |
| `--output` | `-o` | PATH | Custom output directory path |
| `--verbose` | `-v` | INT | Verbosity level (0=default, 1=silent, 2=detailed) |
| `--use-config` | `-uc` | INT | Use predefined configuration by ID |
| `--config-list` | `-cl` | FLAG | List all available configurations |
| `--copy-config` | `-cc` | PATH | Copy configuration file to RunnerScript |
| `--config-info` | `-ci` | INT | Display detailed configuration information |
| `--chain` | `-ch` | PATHS | Chain multiple configuration files in sequence |
| `--help` | `-h` | FLAG | Show help message and banner |

### Usage Examples

#### Run a workflow with custom configuration
```bash
python rs.py -p myproject -c ./config.yaml
```

#### List available configurations
```bash
python rs.py -cl
```

#### Use predefined configuration
```bash
python rs.py -p myproject -uc 1
```

#### Run with verbose output
```bash
python rs.py -p myproject -c ./config.yaml -v 2
```

#### Chain multiple configurations (execute sequentially with shared output)
```bash
python rs.py -p myproject -ch recon.yaml analysis.yaml reporting.yaml
```

#### Chain configs for different workflow types
```bash
python rs.py -p data-pipeline -ch extract.yaml transform.yaml load.yaml
```

#### Custom output directory
```bash
python rs.py -p myproject -c ./config.yaml -o /custom/output/path
```

#### Get info about a configuration
```bash
python rs.py -ci 1
```

## Project Structure

```
RunnerScript/
├── rs.py                      # Main application entry point
├── README.md                  # Project documentation
├── workflow.md                # Workflow configuration guide
├── requirements.txt           # Python dependencies
├── config/
│   └── default-config.yaml   # Default reconnaissance workflow template
└── src/
    ├── banner.py             # ASCII banner and help action
    ├── cli_parser.py         # Command-line argument parsing
    ├── config.py             # Configuration management
    ├── logger.py             # Logging and output formatting
    ├── runner.py             # Workflow execution engine
    └── workflow_executor.py   # Workflow orchestration
```

## Configuration

RunnerScript uses YAML files to define workflows. A configuration file contains:

- **Metadata**: Name, description, version, author
- **Variables**: Input parameters that can be substituted into commands (e.g., `{domain}`, `{input_file}`, custom variables)
- **Script Config**: Global settings like timeout, retry behavior, and checkpoints
- **Stages**: Sequential or parallel task execution blocks that define your workflow logic

### Basic Configuration Structure

```yaml
name: Workflow Name
description: Workflow description
version: 1.0.0
author: Your Name

variables:
  domain: example.com

script_config:
  timeout: 3600

stages:
  - name: stage_name
    parallel: true
    tasks:
      - name: task_name
        command: command_to_execute
```

For detailed information on creating custom YAML configurations, refer to [workflow.md](workflow.md).

## Output Organization

RunnerScript automatically creates organized output directories:

```
projects/
├── myproject/
│   ├── logs/
│   │   └── execution.log
│   ├── output/
│   │   ├── stage1_output.txt
│   │   ├── stage2_output.txt
│   │   └── ...
│   └── metadata.json
```

Each project gets its own directory with:
- **logs/**: Execution logs and debug information
- **output/**: Command output and results
- **metadata.json**: Workflow execution metadata

## Logging

RunnerScript provides three verbosity levels:

- **Level 0** (Default): Standard output with important information
- **Level 1** (Silent): Minimal output, errors only
- **Level 2** (Detailed): Complete execution details and debug information

Enable detailed logging:
```bash
python rs.py -p myproject -c ./config.yaml -v 2
```

## Variables

RunnerScript supports variables that are substituted into commands during task execution. You can define any variable in the `variables` section:

- `{domain}`: Target domain (commonly used in reconnaissance workflows)
- Custom variables: Define any variable you need for your workflow

Variables are substituted into commands during task execution. Examples:
```yaml
variables:
  domain: target.com

tasks:
  - name: subdomain_enumeration
    command: subfinder -d {domain} -o subs.txt
```

Future versions will support additional variables.

## Troubleshooting

### Configuration File Not Found
Ensure the path to your YAML configuration file is correct and relative to your current working directory.

### Project Name Required
Use the `-p` or `--project` flag to specify your project name, unless using configuration-only operations (`-cl`, `-uc`, `-cc`).

### Timeout Issues
Adjust the `timeout` value in your YAML configuration's `script_config` section. Use `-1` for no timeout.

### Permission Denied
On Linux/macOS, ensure the script has execution permissions:
```bash
chmod +x rs.py
```

## Contributing

Contributions are welcome! Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is provided as-is for authorized security testing purposes only.

## Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Last Updated**: 2026-06-06
