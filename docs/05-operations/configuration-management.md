# SynOS Configuration Management

## Overview

SynOS uses a centralized configuration management approach with one authoritative configuration file per functional area. This document outlines the configuration structure and best practices.

## Configuration Hierarchy

### 1. Development Environment

- **File**: `.vscode/settings.json`
- **Purpose**: IDE configuration, language server settings
- **Scope**: Development experience

### 2. Build System

- **File**: `.cargo/config.toml`
- **Purpose**: Rust compiler settings, build profiles, targets
- **Scope**: All Rust builds

### 3. Core System

- **File**: `config/core/syn_os_config.yaml`
- **Purpose**: Main system configuration
- **Scope**: Runtime system behavior

### 4. Security

- **File**: `config/security/zero_trust.yaml`
- **Purpose**: Security policies and zero-trust configuration
- **File**: `core/security/audit/security_config.json`
- **Purpose**: Security orchestrator settings
- **Scope**: Security subsystem

### 5. Testing

- **File**: `tests/phase-reports/test_config.json`
- **Purpose**: Test suite configuration and parameters
- **Scope**: Test execution

### 6. Infrastructure

- **File**: `config/core/prometheus.yml` - Monitoring
- **File**: `config/core/nats_subjects.yaml` - Messaging
- **File**: `config/core/logging.yml` - Logging
- **Scope**: Infrastructure services

## Configuration Principles

### 1. Single Source of Truth

Each configuration aspect has exactly one authoritative file. No duplicates or conflicts.

### 2. Environment-Specific Overrides

Use environment variables or command-line arguments for environment-specific settings rather than multiple config files.

### 3. Validation

All configuration files are validated for syntax and logical consistency.

### 4. Documentation

Each configuration file includes inline documentation explaining its purpose and critical settings.

## Best Practices

### 1. Avoid Configuration Drift

- Use the `scripts/maintenance/config-cleanup.sh` script regularly
- Review the `config/CONFIG_INVENTORY.md` for changes

### 2. Version Control

- All configuration files are version controlled
- Use meaningful commit messages for configuration changes

### 3. Testing

- Configuration changes should be tested in development environments first
- Use the validation scripts before committing changes

### 4. Security

- Sensitive values use environment variables or secure vaults
- No secrets in configuration files

## Maintenance Commands

```bash
# Validate all configurations
./scripts/maintenance/config-cleanup.sh

# Check for configuration conflicts
grep -r "rust-analyzer.checkOnSave" config/ .vscode/

# Validate specific file types
find . -name "*.json" -exec python3 -m json.tool {} \; > /dev/null
find . -name "*.yaml" -exec python3 -c "import yaml; yaml.safe_load(open('{}'))" \; 2>/dev/null
```

## Troubleshooting

### Common Issues

1. **Duplicate configurations**: Use the cleanup script to identify and resolve
2. **Invalid JSON/YAML**: Use validation commands to check syntax
3. **Environment conflicts**: Ensure environment variables don't override critical settings

### Recovery

If configuration becomes corrupted:

1. Check git history for last known good configuration
2. Use backup files if available (though these should be cleaned up regularly)
3. Refer to this documentation to rebuild from scratch
