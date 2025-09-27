# SynOS Configuration Inventory

This document tracks all authoritative configuration files in the SynOS project.

## VS Code Configuration
- **Location**: `.vscode/settings.json`
- **Purpose**: VS Code IDE settings, rust-analyzer configuration
- **Status**: Active ✅

## Rust/Cargo Configuration
- **Location**: `.cargo/config.toml`
- **Purpose**: Consolidated Cargo build configuration (performance + security)
- **Status**: Active ✅
- **Removed**: `.cargo/config-security.toml` (merged into main config)

## Core System Configuration
- **Location**: `config/core/syn_os_config.yaml`
- **Purpose**: Main SynOS system configuration
- **Status**: Active ✅

## Development Environment
- **Location**: `config/core/dev-environment.yaml`
- **Purpose**: Development tools and IDE settings
- **Status**: Active ✅

## Security Configuration
- **Location**: `core/security/audit/security_config.json`
- **Purpose**: Security orchestrator configuration
- **Status**: Active ✅

- **Location**: `config/security/zero_trust.yaml`
- **Purpose**: Zero trust security model configuration
- **Status**: Active ✅

## Testing Configuration
- **Location**: `tests/phase-reports/test_config.json`
- **Purpose**: Test suite configuration
- **Status**: Active ✅

## Formatting Configuration
- **Location**: `config/formatting/rustfmt.toml`
- **Purpose**: Rust code formatting rules
- **Status**: Active ✅

## Logging Configuration
- **Location**: `config/core/logging.yml`
- **Purpose**: System logging configuration
- **Status**: Active ✅

## Monitoring Configuration
- **Location**: `config/core/prometheus.yml`
- **Purpose**: Prometheus monitoring configuration
- **Status**: Active ✅

## Network Configuration
- **Location**: `config/core/nats_subjects.yaml`
- **Purpose**: NATS messaging subjects configuration
- **Status**: Active ✅

## Deployment Configuration
- **Location**: `config/docker/docker-compose.test.yml`
- **Purpose**: Docker container orchestration for testing
- **Status**: Active ✅

## Service Configuration
- **Location**: `config/security-tools/services.yaml`
- **Purpose**: Security tools and services configuration
- **Status**: Active ✅

## Removed/Consolidated Files
- `.vscode/settings.json.backup` - Removed ❌
- `.cargo/config-security.toml` - Merged into main config ❌

## Archive Directory
All files in the `archive/` directory are considered historical and do not affect the active codebase.
