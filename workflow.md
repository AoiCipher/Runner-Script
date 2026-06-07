# Workflow Configuration Guide

This document provides comprehensive instructions for creating and customizing YAML workflow configurations for RunnerScript. While the examples use security reconnaissance, RunnerScript is a **general-purpose tool-chaining framework** suitable for any workflow requiring orchestration of multiple tools and scripts.

## Table of Contents

1. [Overview](#overview)
2. [YAML Structure](#yaml-structure)
3. [Metadata Section](#metadata-section)
4. [Variables Section](#variables-section)
5. [Script Config Section](#script-config-section)
6. [Stages Section](#stages-section)
7. [Creating Custom YAML](#creating-custom-yaml)
8. [Examples](#examples)
9. [Best Practices](#best-practices)

## Overview

A RunnerScript workflow configuration is a YAML file that defines:
- **What** tasks to execute (commands, scripts, tools)
- **When** to execute them (sequential or parallel)
- **How** to manage them (timeouts, dependencies, retries)
- **With what** input data (variables and parameters)

The YAML format is human-readable and easy to maintain, making it ideal for documenting complex workflows. Use RunnerScript for:
- **Security workflows**: Reconnaissance, vulnerability scanning, penetration testing
- **Data pipelines**: ETL processes, data transformation, aggregation
- **CI/CD automation**: Build chains, testing pipelines, deployment workflows
- **Custom orchestration**: Any workflow requiring tool chaining and controlled execution

## YAML Structure

A complete RunnerScript YAML configuration follows this structure:

```yaml
# Metadata
name: Workflow Name
description: Detailed description
version: 1.0.0
author: Your Name

# Variables (inputs)
variables:
  domain: example.com

# Global configuration
script_config:
  timeout: 3600

# Task execution definition
stages:
  - name: stage_name
    parallel: true
    tasks:
      - name: task_name
        command: command_to_execute
```

## Metadata Section

The metadata section provides information about your workflow:

```yaml
name: Reconnaissance Workflow
description: A comprehensive reconnaissance workflow for security assessment
version: 1.0.0
author: Security Team
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Name of the workflow |
| `description` | String | Yes | Detailed description of what the workflow does |
| `version` | String | Yes | Semantic version number (e.g., 1.0.0) |
| `author` | String | Yes | Author or team name |

## Variables Section

Variables are input parameters used throughout your workflow configuration. They are referenced using curly braces `{variable_name}` and are substituted during task execution. Define ANY variables your workflow needs.

### Common Variables

**`{domain}`** - The target domain (reconnaissance workflows)
- Type: String
- Example: `{domain}` becomes `example.com`

**Custom variables** - Define any variables for your workflow:
- `{input_file}` - Input file path (data processing workflows)
- `{database_url}` - Database connection string
- `{api_key}` - API credentials
- `{output_format}` - Output format specification
- Any other parameter your tools need

### Variable Declaration

```yaml
variables:
  domain: example.com
  input_file: /path/to/data.csv
  output_format: json
  database_url: postgresql://localhost/mydb
```

### Using Variables in Commands

Variables are substituted into command strings. They work with ANY command or tool:

```yaml
tasks:
  - name: subdomain_enumeration
    command: subfinder -d {domain} -o subs.txt
    # Executes as: subfinder -d example.com -o subs.txt
```

### Future Variable Support

The following variables are planned for future releases:
- `{subdomain_list}` - List of discovered subdomains
- `{ip_list}` - List of resolved IP addresses
- `{url_list}` - List of discovered URLs
- `{output_dir}` - Current project output directory

## Script Config Section

The `script_config` section contains global configuration for workflow execution:

```yaml
script_config:
  timeout: 3600
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout` | Integer | 3600 | Maximum execution time in seconds. Use `-1` for no timeout |

### Timeout Behavior

- **Positive value** (e.g., 3600): Workflow terminates after specified seconds
- **Negative value** (-1): No timeout limit
- **Not specified**: Defaults to 3600 seconds (1 hour)

### Example Configurations

One hour timeout:
```yaml
script_config:
  timeout: 3600
```

No timeout:
```yaml
script_config:
  timeout: -1
```

Six hours:
```yaml
script_config:
  timeout: 21600
```

## Stages Section

The `stages` section defines the execution workflow as a list of stages. Each stage represents a logical step in your process and contains tasks that can run in parallel or sequentially. Stages can be used to organize ANY workflow:

**Reconnaissance workflow stages**: enumeration → analysis → reporting  
**Data pipeline stages**: extraction → transformation → validation → loading  
**CI/CD pipeline stages**: build → test → deploy → verify  
**Custom automation**: any logical sequence of tool-chaining operations

### Stage Definition

```yaml
stages:
  - name: stage_name
    parallel: true
    depends_on:
      - previous_stage
    tasks:
      - name: task_name
        command: command_to_execute
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Unique stage identifier |
| `parallel` | Boolean | No | Execute all tasks in parallel (default: false) |
| `depends_on` | List | No | List of stage names that must complete first |
| `tasks` | List | Yes | List of tasks to execute in this stage |

### Parallel Execution

When `parallel: true`, all tasks in the stage execute simultaneously. Use this when tasks are independent and can safely run at the same time:

```yaml
- name: data_extraction
  parallel: true
  tasks:
    - name: extract_from_api
      command: python extract_api.py -o api_data.json
    - name: extract_from_database
      command: python extract_db.py -o db_data.json
    - name: extract_from_files
      command: python extract_files.py -o file_data.json
    # All three execute at the same time
```

Alternatively, for security reconnaissance:
```yaml
- name: subdomain_enumeration
  parallel: true
  tasks:
    - name: subfinder
      command: subfinder -d {domain} -o subfinder.txt
    - name: sublist3r
      command: sublist3r -d {domain} -o sublist3r.txt
    # All enumeration tools run simultaneously
```

### Sequential Execution

When `parallel: false` or not specified, tasks execute one after another. Use this when tasks have dependencies or must process results in order:

```yaml
- name: data_processing
  parallel: false
  tasks:
    - name: merge_inputs
      command: cat input1.json input2.json > combined.json
    - name: validate_data
      command: python validate.py combined.json
    - name: transform_data
      command: python transform.py combined.json > output.json
    # Executed sequentially - each waits for the previous
```

Or for reconnaissance workflow:
```yaml
- name: merge_results
  parallel: false
  tasks:
    - name: merge_subdomains
      command: cat subfinder.txt sublist3r.txt | sort -u > merged.txt
    - name: count_results
      command: wc -l merged.txt
    # Executed sequentially
```

### Stage Dependencies

Use `depends_on` to control stage execution order. This allows you to chain stages together where later stages depend on outputs from earlier stages:

```yaml
stages:
  - name: extraction
    tasks:
      - name: extract_data
        command: python extract.py

  - name: transformation
    depends_on:
      - extraction
    tasks:
      - name: transform_data
        command: python transform.py

  - name: validation
    depends_on:
      - transformation
    tasks:
      - name: validate_data
        command: python validate.py

  - name: loading
    depends_on:
      - validation
    tasks:
      - name: load_data
        command: python load.py
```

In this example:
1. `extraction` runs first
2. `transformation` waits for `extraction` to complete
3. `validation` waits for `transformation` to complete
4. `loading` waits for `validation` to complete

This pattern works for ANY workflow type:
- **Data pipelines**: extraction → transformation → validation → loading
- **Security workflows**: reconnaissance → analysis → reporting → cleanup
- **Build systems**: prepare → build → test → deploy → verify
- **Custom automation**: any sequence of dependent stages

### Task Definition

Each task within a stage contains:

```yaml
- name: task_identifier
  command: command_to_execute
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Unique task identifier within the stage |
| `command` | String | Yes | Shell command or script to execute |

The `command` field can be:
- A single-line command
- A multi-line command using YAML's `>` syntax for folding
- A pipe-separated command chain

#### Single-line Command
```yaml
- name: simple_task
  command: echo "Hello, World!"
```

#### Multi-line Command (Folded)
```yaml
- name: complex_task
  command: >
    httpx -l hosts.txt -sc -title -tech-detect -cdn
    -ip -cl -location -silent -o output.txt
```

#### Piped Commands
```yaml
- name: piped_task
  command: cat data.txt | grep "pattern" | sort -u > results.txt
```

## Creating Custom YAML

### Step-by-Step Guide

#### 1. Create a New File

Create a new YAML file with a descriptive name for your workflow:
```bash
# For security reconnaissance
touch security_recon.yaml

# For data processing
touch data_pipeline.yaml

# For CI/CD automation
touch build_deploy.yaml
```

#### 2. Add Metadata

Start with the metadata section. Choose a name and description that reflects your workflow:
```yaml
# Example 1: Security Reconnaissance
name: Domain Reconnaissance Workflow
description: Comprehensive domain reconnaissance and vulnerability scanning
version: 1.0.0
author: Your Name

# Example 2: Data Processing Pipeline
name: ETL Data Pipeline
description: Extract, transform, and load customer data
version: 1.0.0
author: Your Name

# Example 3: CI/CD Build Pipeline
name: Application Build and Deploy
description: Build, test, and deploy application to production
version: 1.0.0
author: Your Name
```

#### 3. Define Variables

Add variables for your specific workflow. These can be ANY parameters your workflow needs:
```yaml
# Security workflow
variables:
  domain: target.com
  output_dir: /results

# Data processing workflow
variables:
  input_file: /data/customers.csv
  database_url: postgresql://localhost/mydb
  batch_size: 1000

# CI/CD workflow
variables:
  app_name: myapp
  version: 1.0.0
  environment: production
```

#### 4. Configure Script Settings

Set the timeout and other global configurations:
```yaml
script_config:
  timeout: 3600  # 1 hour
  stop_on_failure: true
  retry_failed_tasks: true
  retry: 3
```

#### 5. Define Stages and Tasks

Add stages that organize your workflow into logical steps. Use ANY command-line tool or script:

**Example 1: Security Reconnaissance**
```yaml
stages:
  - name: information_gathering
    parallel: true
    tasks:
      - name: whois
        command: whois {domain}
      - name: dns_info
        command: nslookup {domain}
      - name: http_check
        command: httpx -u {domain} -title
```

**Example 2: Data Processing**
```yaml
stages:
  - name: extraction
    tasks:
      - name: extract_from_csv
        command: python extract.py --input {input_file} --format csv
  
  - name: transformation
    depends_on:
      - extraction
    tasks:
      - name: clean_data
        command: python clean.py extracted_data.csv
      - name: transform_data
        command: python transform.py cleaned_data.csv
  
  - name: loading
    depends_on:
      - transformation
    tasks:
      - name: load_to_db
        command: python load.py {database_url} transformed_data.csv
```

**Example 3: CI/CD Pipeline**
```yaml
stages:
  - name: build
    tasks:
      - name: compile
        command: mvn clean build -DappVersion={version}
      - name: unit_tests
        command: mvn test
  
  - name: deploy
    depends_on:
      - build
    tasks:
      - name: docker_build
        command: docker build -t {app_name}:{version} .
      - name: push_image
        command: docker push {app_name}:{version}
      - name: deploy_to_k8s
        command: kubectl set image deployment/{app_name} {app_name}={app_name}:{version} --record
```

#### 6. Validate Your Configuration

Test your configuration file:
```bash
python rs.py -p test -c ./your_workflow.yaml -v 2
```

### File Format Requirements

- **File extension**: `.yaml` or `.yml`
- **Encoding**: UTF-8
- **Indentation**: 2 spaces (spaces, not tabs)
- **Syntax**: Valid YAML format

### Common Mistakes to Avoid

1. **Incorrect indentation**: Use 2 spaces consistently
   ```yaml
   # WRONG - mixed indentation
   stages:
     - name: stage1
        tasks:  # 3 spaces instead of 2
   ```

2. **Unquoted special characters**: Quote strings with special characters
   ```yaml
   # WRONG
   command: echo "test" > output.txt
   
   # CORRECT
   command: 'echo "test" > output.txt'
   # or
   command: echo \"test\" > output.txt
   ```

3. **Invalid variable names**: Use only alphanumeric characters and underscores
   ```yaml
   # WRONG
   variables:
     my-domain: example.com  # hyphens not supported
   
   # CORRECT
   variables:
     my_domain: example.com
   ```

4. **Missing required fields**: Ensure all required fields are present
   ```yaml
   # WRONG - missing author
   name: My Workflow
   description: A workflow
   version: 1.0.0
   
   # CORRECT
   name: My Workflow
   description: A workflow
   version: 1.0.0
   author: Your Name
   ```

## Examples

### Example 1: Security Reconnaissance Workflow

```yaml
name: DNS Reconnaissance
description: Simple DNS information gathering workflow
version: 1.0.0
author: Security Team

variables:
  domain: example.com

script_config:
  timeout: 300

stages:
  - name: dns_lookup
    parallel: true
    tasks:
      - name: nslookup
        command: nslookup {domain}
      - name: dig
        command: dig {domain}
      - name: whois
        command: whois {domain}
```

### Example 2: Data Processing Pipeline

```yaml
name: Customer Data ETL Pipeline
description: Extract, transform, and load customer data from multiple sources
version: 1.0.0
author: Data Team

variables:
  input_dir: /data/raw
  output_dir: /data/processed
  database_url: postgresql://localhost/analytics
  batch_size: 5000

script_config:
  timeout: 7200
  stop_on_failure: true
  retry_failed_tasks: true
  retry: 3

stages:
  - name: extraction
    parallel: true
    tasks:
      - name: extract_csv
        command: python extract.py --source csv --input {input_dir}/customers.csv --output extracted_csv.json
      - name: extract_database
        command: python extract.py --source postgres --connection {database_url} --output extracted_db.json
      - name: extract_api
        command: python extract.py --source api --endpoint https://api.example.com/customers --output extracted_api.json

  - name: transformation
    depends_on:
      - extraction
    parallel: true
    tasks:
      - name: clean_data
        command: python clean.py extracted_*.json --output cleaned_data.json
      - name: validate_schema
        command: python validate.py cleaned_data.json --schema customer_schema.json

  - name: aggregation
    depends_on:
      - transformation
    tasks:
      - name: merge_sources
        command: python merge.py cleaned_data.json --batch-size {batch_size} --output merged_data.json
      - name: deduplicate
        command: python deduplicate.py merged_data.json --output deduped_data.json

  - name: loading
    depends_on:
      - aggregation
    tasks:
      - name: load_to_warehouse
        command: python load.py {database_url} deduped_data.json --table customers
      - name: generate_report
        command: python report.py {database_url} --output {output_dir}/load_report.html
```

### Example 3: CI/CD Build and Deploy Pipeline

```yaml
name: Application Build and Deploy Pipeline
description: Build, test, and deploy application across environments
version: 1.0.0
author: DevOps Team

variables:
  app_name: myapp
  version: 1.0.0
  docker_registry: docker.io/mycompany
  k8s_namespace: production

script_config:
  timeout: 3600
  stop_on_failure: true
  continue_on_failure: false

stages:
  - name: build
    parallel: false
    tasks:
      - name: install_dependencies
        command: npm install
      - name: run_unit_tests
        command: npm run test
      - name: run_linter
        command: npm run lint

  - name: package
    depends_on:
      - build
    tasks:
      - name: build_docker_image
        command: docker build -t {docker_registry}/{app_name}:{version} .
      - name: scan_image
        command: trivy image --severity HIGH,CRITICAL {docker_registry}/{app_name}:{version}

  - name: push
    depends_on:
      - package
    tasks:
      - name: push_to_registry
        command: docker push {docker_registry}/{app_name}:{version}

  - name: deploy
    depends_on:
      - push
    tasks:
      - name: update_k8s_deployment
        command: kubectl set image deployment/{app_name} {app_name}={docker_registry}/{app_name}:{version} -n {k8s_namespace}
      - name: verify_rollout
        command: kubectl rollout status deployment/{app_name} -n {k8s_namespace}

  - name: smoke_tests
    depends_on:
      - deploy
    tasks:
      - name: run_health_checks
        command: curl http://{app_name}.example.com/health
      - name: verify_api_endpoints
        command: python smoke_tests.py --host {app_name}.example.com
```

### Example 4: Multi-Stage Security Reconnaissance

```yaml
name: Multi-Stage Reconnaissance
description: Comprehensive reconnaissance with tool chaining
version: 1.0.0
author: Security Team

variables:
  domain: example.com

script_config:
  timeout: 7200

stages:
  - name: subdomain_discovery
    parallel: true
    tasks:
      - name: subfinder
        command: subfinder -d {domain} -o subs.txt

  - name: resolve_subdomains
    depends_on:
      - subdomain_discovery
    tasks:
      - name: dns_resolution
        command: dnsx -l subs.txt -o resolved.txt

  - name: host_discovery
    depends_on:
      - resolve_subdomains
    tasks:
      - name: httpx
        command: httpx -l resolved.txt -o hosts.txt
```

### Example 5: Results Processing and Reporting

```yaml
name: Results Processing Workflow
description: Aggregate, process, and report on collected data
version: 1.0.0
author: Analysis Team

variables:
  domain: example.com

script_config:
  timeout: 1800

stages:
  - name: data_collection
    parallel: true
    tasks:
      - name: gather_subdomains
        command: >
          subfinder -d {domain} |
          tee subs.txt | wc -l
      - name: gather_ips
        command: >
          dig +short {domain} |
          tee ips.txt | sort -u

  - name: consolidate
    depends_on:
      - data_collection
    tasks:
      - name: merge_results
        command: >
          cat subs.txt ips.txt |
          sort -u | tee all-results.txt
      - name: generate_summary
        command: python generate_report.py all-results.txt
```

## Best Practices

### 1. Use Descriptive Names for Clarity

Use clear, descriptive names for stages and tasks that reflect your workflow type:

```yaml
# GOOD - Security Workflow
- name: subdomain_enumeration_tools
  tasks:
    - name: subfinder_enumeration
      command: subfinder -d {domain}

# GOOD - Data Pipeline
- name: data_extraction_phase
  tasks:
    - name: extract_from_csv
      command: python extract.py --source csv

# AVOID - Non-descriptive names
- name: stage1
  tasks:
    - name: task1
      command: some_command
```

### 2. Organize Related Tasks into Stages

Group related tasks within stages to create logical workflow steps:

```yaml
# Security workflow example
stages:
  - name: passive_enumeration
    parallel: true
    tasks:
      - name: whois_lookup
        command: whois {domain}
      - name: dns_records
        command: dig {domain}

  - name: active_enumeration
    depends_on:
      - passive_enumeration
    tasks:
      - name: port_scan
        command: nmap {domain}
```

### 3. Use Dependencies for Complex Workflows

Leverage `depends_on` to create multi-stage workflows where later stages use output from earlier stages:

```yaml
stages:
  - name: initial_phase
    tasks:
      - name: prepare_data
        command: python prepare.py

  - name: processing_phase
    depends_on:
      - initial_phase
    tasks:
      - name: process_data
        command: python process.py prepared_data.json

  - name: final_phase
    depends_on:
      - processing_phase
    tasks:
      - name: finalize_data
        command: python finalize.py processed_data.json
```

### 4. Add Comments for Complex Sections

Use YAML comments to explain important workflow logic:

```yaml
# Parallel tasks - these tools can run simultaneously
- name: reconnaissance_phase
  parallel: true
  tasks:
    # Multiple enumeration tools
    - name: tool1
      command: command1
    # Another enumeration tool
    - name: tool2
      command: command2

# Sequential processing - each task depends on previous results
- name: processing_phase
  parallel: false
  tasks:
    - name: merge_results
      command: cat results1 results2 > merged.txt
```

### 5. Set Appropriate Timeouts

Set realistic timeouts based on expected execution duration:

```yaml
script_config:
  timeout: 300      # 5 minutes - for quick checks
  timeout: 3600     # 1 hour - standard workflow
  timeout: 7200     # 2 hours - long-running pipeline
  timeout: -1       # No timeout - for indefinite processes
```

### 6. Test Before Large-Scale Deployment

Always test configurations locally with verbose output first:

```bash
python rs.py -p test -c ./new_workflow.yaml -v 2
```

### 7. Version Your Configurations

Update version numbers when making changes to track workflow evolution:

```yaml
version: 1.0.0  # Initial release
version: 1.1.0  # Added new stage or tool
version: 2.0.0  # Major refactor or workflow redesign
```

### 8. Document Complex Workflows

Add descriptive metadata for your workflows:

```yaml
name: Multi-Stage Processing Workflow
description: |
  Comprehensive workflow designed for processing large datasets.
  Includes extraction from multiple sources, transformation,
  validation, and loading into data warehouse.
  Estimated runtime: 2-4 hours depending on data volume.
version: 1.0.0
author: Data Team
```

### 9. Use Variables for Reusability

Parameterize your workflows with variables to make them reusable across different targets or inputs:

```yaml
variables:
  domain: example.com          # For security workflows
  input_file: /path/to/data    # For data processing
  output_dir: /results         # Common to all workflows
  database_url: postgres://... # For any workflow

# Use variables in commands
tasks:
  - name: process_data
    command: python process.py --input {input_file} --output {output_dir}
```

### 10. Use Parallel Execution for Independent Tasks

When tasks don't depend on each other's output, run them in parallel to reduce overall execution time:

```yaml
- name: independent_tasks
  parallel: true  # Run all simultaneously
  tasks:
    - name: task_a
      command: tool_a
    - name: task_b
      command: tool_b
    - name: task_c
      command: tool_c
```

## Troubleshooting

### Workflow Won't Start

1. Verify YAML syntax is valid (check indentation)
2. Ensure all required fields are present
3. Verify variable syntax: `{domain}` not `{domain` or `domain}`

### Variables Not Substituting

1. Check variable names match exactly (case-sensitive)
2. Ensure variables are defined in the `variables` section
3. Verify variable usage syntax: `{variable_name}`

### Stages Not Executing in Order

1. Review `depends_on` declarations
2. Ensure stage names match exactly between `depends_on` and stage definition
3. Check for circular dependencies

### Commands Failing to Execute

1. Test commands manually in the terminal first
2. Verify tool is installed and in PATH
3. Check command syntax and quotation
4. Use `-v 2` for detailed error messages

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-06-06  
**Supported Variables**: `{domain}`
