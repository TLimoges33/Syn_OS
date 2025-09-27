# Syn OS Scripts Directory

This directory contains organized scripts for various aspects of the Syn OS project. Scripts are categorized by functionality for easier navigation and maintenance.

## Directory Structure

### 📁 `core/`

Core system scripts and main tools:

- `claude` - Main Claude CLI executable
- `claude-cli.py` - Claude CLI Python implementation
- `claude-dev-functions.sh` - Development functions for Claude integration
- `claude-mcp-env.sh` - Claude MCP environment setup
- `add-claude-to-path.sh` - Adds Claude to system PATH
- `complete-service-integration.sh` - Complete service integration script

### 📁 `setup/`

Initial setup and configuration scripts:

- `setup-api-key.sh` - Configure API keys
- `setup-claude-cli.sh` - Set up Claude CLI
- `setup-claude-mcp.sh` - Set up Claude MCP server
- `setup-claude.sh` - General Claude setup
- `setup-dev-environment.sh` - Development environment setup
- `team-onboarding-setup.sh` - Team member onboarding
- `switch-mcp.sh` - Switch between MCP configurations

### 📁 `ebpf/`

Extended Berkeley Packet Filter (eBPF) related scripts:

- `ebpf-comprehensive-test.sh` - Comprehensive eBPF testing
- `ebpf-dashboard.sh` - eBPF monitoring dashboard
- `ebpf-realtime-monitor.sh` - Real-time eBPF monitoring
- `ebpf-stress-test.sh` - eBPF stress testing

### 📁 `merge/`

Git merge and branch management scripts:

- `automate-pr-merge.sh` - Automated pull request merging
- `simple-merge-branches.sh` - Simple branch merging
- `optimize-branches.sh` - Branch optimization

### 📁 `optimization/`

System and code optimization scripts:

- `optimize-workspace.sh` - Workspace optimization
- `comprehensive-architecture-optimization.sh` - Architecture optimization

### 📁 `backup/`

Backup and recovery scripts:

- `create-safety-backup.sh` - Create system safety backups

### 📁 `audit/`

Code and security audit scripts:

- `comprehensive-architecture-audit.py` - Architecture auditing
- `comprehensive-codebase-audit.sh` - Codebase auditing
- `team-codespace-audit.sh` - Team codespace auditing

### 📁 `documentation/`

Documentation management scripts:

- `organize-documentation.sh` - Organize project documentation

### 📁 `build/`

Build and compilation scripts:

- `build-master-iso-v1.0.sh` - Build master ISO v1.0
- `build-simple-iso.sh` - Build simple ISO
- `test-kernel-build.sh` - Test kernel builds

### 📁 `repo/`

Repository management and synchronization scripts:

- `auto-consolidate-repository.sh` - Auto-consolidate repository
- `complete-repository-consolidation.sh` - Complete repository consolidation
- `synos-repo-sync.sh` - Syn OS repository synchronization

### 📁 `maintenance/`

System maintenance and cleanup scripts:

- `workspace-cleanup.sh` - Clean up workspace
- `fix-vscode-terminal.sh` - Fix VS Code terminal issues

### 📁 Existing Specialized Directories

- `development/` - Development-specific tools and scripts
- `monitoring/` - System monitoring scripts
- `security-automation/` - Security automation tools
- `setup/` - Setup and configuration utilities
- `systemd/` - Systemd service management

## Usage Guidelines

1. **Before running any script**, ensure you understand what it does by reading its comments or documentation
2. **Make scripts executable** if needed: `chmod +x script-name.sh`
3. **Run from appropriate directory** - some scripts expect to be run from specific locations
4. **Check dependencies** - ensure required tools and packages are installed

## Common Workflows

### Initial Setup

```bash
# Set up development environment
./setup/setup-dev-environment.sh

# Configure Claude CLI
./setup/setup-claude-cli.sh

# Set up API keys
./setup/setup-api-key.sh
```

### Development Workflow

```bash
# Optimize workspace
./optimization/optimize-workspace.sh

# Create backup before major changes
./backup/create-safety-backup.sh

# Run audits
./audit/comprehensive-codebase-audit.sh
```

### Build and Test

```bash
# Test kernel build
./build/test-kernel-build.sh

# Run eBPF tests
./ebpf/ebpf-comprehensive-test.sh

# Build ISO
./build/build-master-iso-v1.0.sh
```

## Maintenance

- Scripts should be reviewed and updated regularly
- Dead or obsolete scripts should be removed or moved to an archive
- New scripts should follow the naming convention and be placed in appropriate directories
- Update this README when adding new categories or scripts

## Contributing

When adding new scripts:

1. Choose the appropriate category directory
2. Use descriptive names with appropriate extensions
3. Add execute permissions (`chmod +x`)
4. Include proper documentation/comments in the script
5. Update this README if creating new categories

---

_Last updated: September 12, 2025_
