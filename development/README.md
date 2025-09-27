# SynOS Development Environment

A comprehensive development environment for SynOS (Synthetic Operating System) featuring secure MCP (Model Context Protocol) servers, testing infrastructure, and development tools.

## Overview

This development environment provides the essential tools and infrastructure needed for SynOS development, including:

- **Secure Shell MCP Server**: Execute shell commands with security controls and audit logging
- **Test Simple MCP Server**: Comprehensive testing framework for system validation and performance benchmarking
- **Testing Infrastructure**: Complete test suite with unit, integration, and performance tests
- **Development Tools**: Modern Python tooling with linting, formatting, and type checking

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Virtual environment (recommended)
- Git

### Installation

1. **Clone the repository and navigate to development directory**:

   ```bash
   cd development
   ```

2. **Create and activate virtual environment**:

   ```bash
   python3 -m venv mcp_env
   source mcp_env/bin/activate  # Linux/macOS
   # or
   mcp_env\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

### Running MCP Servers

#### Shell MCP Server

```bash
# Start the secure shell execution server
python -m mcp_servers.shell_mcp_server

# Or use the installed script
synos-shell-mcp
```

#### Test MCP Server

```bash
# Start the testing and validation server
python -m mcp_servers.test_simple_mcp_server

# Or use the installed script
synos-test-mcp
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_servers --cov=mcp

# Run specific test categories
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m "not slow"  # Exclude slow tests

# Run with verbose output
pytest -v
```

## Architecture

### MCP Servers

#### Shell MCP Server (`shell_mcp_server.py`)

- **Purpose**: Secure shell command execution with security controls
- **Features**:
  - Command validation and sanitization
  - Security restriction enforcement
  - Audit logging for all operations
  - Timeout controls for long-running commands
  - Async execution with proper resource management

#### Test Simple MCP Server (`test_simple_mcp_server.py`)

- **Purpose**: Comprehensive testing framework for system validation
- **Features**:
  - Connectivity testing
  - Performance benchmarking
  - System validation
  - JSON data validation
  - Stress testing capabilities
  - Metrics collection and analysis

### Security Features

- **Command Restriction**: Dangerous commands are automatically blocked
- **Input Validation**: All inputs are validated for safety and correctness
- **Audit Logging**: Security events and violations are logged
- **Timeout Controls**: Commands have configurable timeout limits
- **Resource Management**: Proper cleanup and resource management

## Development Workflow

### Setting Up Development Environment

1. **Environment Variables**:

   ```bash
   export SYNOS_DEV_MODE=true
   export SYNOS_LOG_LEVEL=DEBUG
   export MCP_SERVER_HOST=localhost
   export MCP_SERVER_PORT=8000
   ```

2. **Development Dependencies**:
   ```bash
   pip install -e ".[dev]"  # Install with development dependencies
   ```

### Code Quality Tools

#### Formatting and Linting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy mcp_servers/ mcp/
```

#### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Testing Guidelines

#### Test Structure

- `tests/conftest.py`: Test configuration and fixtures
- `tests/test_shell_mcp_server.py`: Shell server unit tests
- `tests/test_test_simple_mcp_server.py`: Test server unit tests
- `tests/test_integration.py`: Integration and performance tests

#### Writing Tests

- Use async/await for asynchronous tests
- Include both positive and negative test cases
- Test security restrictions and error handling
- Use fixtures for common test setup
- Follow naming conventions: `test_<functionality>`

## Configuration

### Project Configuration (`pyproject.toml`)

The project uses modern Python packaging with comprehensive tool configuration:

- **Build System**: setuptools with wheel support
- **Dependencies**: Managed through project dependencies and optional extras
- **Tool Configuration**: Black, isort, mypy, pytest, and coverage settings
- **Scripts**: Entry points for MCP servers

### Environment Configuration

Environment variables can be configured in `.env` file:

```env
SYNOS_DEV_MODE=true
SYNOS_LOG_LEVEL=DEBUG
SYNOS_SECURITY_LEVEL=high
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
```

## API Reference

### Shell MCP Server Tools

#### `execute_shell_command`

Execute shell commands with security controls.

**Parameters**:

- `command` (string): The shell command to execute

**Returns**:

- JSON object with execution results, including stdout, stderr, exit code, and security status

#### `list_safe_commands`

Get a list of safe commands that can be executed.

**Returns**:

- JSON array of safe command examples

### Test MCP Server Tools

#### `run_connectivity_test`

Perform basic connectivity and system checks.

**Returns**:

- JSON object with test results and system information

#### `run_performance_test`

Execute performance benchmarking tests.

**Returns**:

- JSON object with performance metrics including operations per second and response times

#### `run_system_validation`

Validate system configuration and capabilities.

**Returns**:

- JSON object with system validation results and configuration details

#### `run_stress_test`

Execute stress testing with configurable parameters.

**Parameters**:

- `iterations` (integer): Number of test iterations to run

**Returns**:

- JSON object with stress test results and performance statistics

#### `validate_json_data`

Validate and parse JSON data.

**Parameters**:

- `json_data` (string): JSON string to validate

**Returns**:

- JSON object with validation results and parsed data

## Security Considerations

### Command Execution Security

- All shell commands are validated against a whitelist of safe patterns
- Dangerous commands (file system modifications, privilege escalation) are blocked
- Commands have timeout limits to prevent resource exhaustion
- All command executions are logged for audit purposes

### Input Validation

- All inputs are sanitized and validated
- JSON inputs are parsed safely with error handling
- Command length limits prevent buffer overflow attacks
- Binary data and control characters are rejected

### Audit and Monitoring

- Security violations are logged with detailed context
- Performance metrics are collected for monitoring
- System resource usage is tracked
- Failed operations are recorded for analysis

## Troubleshooting

### Common Issues

#### MCP Server Won't Start

- Check Python version (3.9+ required)
- Verify all dependencies are installed
- Check for port conflicts
- Review log files for error details

#### Command Execution Fails

- Verify command is in the safe command list
- Check command syntax and parameters
- Review security restrictions
- Check timeout settings

#### Test Failures

- Ensure test environment is properly configured
- Check for required system permissions
- Verify network connectivity for integration tests
- Review test logs for specific error details

### Debugging Tips

1. **Enable Debug Logging**:

   ```bash
   export SYNOS_LOG_LEVEL=DEBUG
   ```

2. **Run Tests with Verbose Output**:

   ```bash
   pytest -v -s
   ```

3. **Check System Resources**:
   ```bash
   # Monitor system performance during tests
   htop
   # Or use the built-in system validation
   python -c "from mcp_servers.test_simple_mcp_server import TestRunner; import asyncio; runner = TestRunner(); asyncio.run(runner.run_system_validation())"
   ```

## Contributing

### Development Process

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Run the full test suite
5. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new functionality
- Maintain security best practices

### Testing Requirements

- All new code must have test coverage
- Security features require specific security tests
- Performance changes need performance tests
- Integration features need integration tests

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For support, issues, or questions:

- Create an issue in the GitHub repository
- Check the troubleshooting section
- Review the test logs for diagnostic information
- Consult the API reference for usage details
