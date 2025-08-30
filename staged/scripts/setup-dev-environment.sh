#!/bin/bash

# SynOS Development Environment Setup
# Configures git save system and development aliases
# Author: SynOS Development Team
# Version: 1.0

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up SynOS Development Environment...${NC}"

# Get the repository root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT_DIR="$REPO_ROOT/scripts"

# Ensure scripts directory exists
mkdir -p "$SCRIPT_DIR"

# Create save command symlinks
echo -e "${BLUE}Creating save command shortcuts...${NC}"

# Create convenient save commands
cat > "$SCRIPT_DIR/save" << 'EOF'
#!/bin/bash
# Quick save shortcut - routes to git-save-system.sh
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
exec "$SCRIPT_DIR/git-save-system.sh" "$@"
EOF

cat > "$SCRIPT_DIR/save-dev" << 'EOF'
#!/bin/bash
# Dev save shortcut
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
exec "$SCRIPT_DIR/git-save-system.sh" dev
EOF

cat > "$SCRIPT_DIR/save-prod" << 'EOF'
#!/bin/bash
# Production save shortcut
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
exec "$SCRIPT_DIR/git-save-system.sh" production
EOF

cat > "$SCRIPT_DIR/git-status-check" << 'EOF'
#!/bin/bash
# Status check shortcut
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
exec "$SCRIPT_DIR/git-save-system.sh" status
EOF

# Make all scripts executable
chmod +x "$SCRIPT_DIR"/{save,save-dev,save-prod,git-status-check,git-save-system.sh}

# Create bash aliases file
echo -e "${BLUE}Creating bash aliases...${NC}"

cat > "$REPO_ROOT/.synos-aliases" << EOF
# SynOS Development Aliases
# Source this file in your .bashrc or .zshrc

# Navigation aliases
alias synos='cd "$REPO_ROOT"'
alias scripts='cd "$REPO_ROOT/scripts"'
alias docs='cd "$REPO_ROOT/docs"'
alias src='cd "$REPO_ROOT/src"'

# Git save system aliases
alias save='$SCRIPT_DIR/save'
alias save-dev='$SCRIPT_DIR/save-dev'
alias save-prod='$SCRIPT_DIR/save-prod'
alias git-check='$SCRIPT_DIR/git-status-check'

# Development workflow aliases
alias build-kernel='cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-syn_os'
alias build-security='cargo build --manifest-path=src/security/Cargo.toml'
alias test-all='make test'
alias security-audit='python3 scripts/a_plus_security_audit.py'
alias validate-env='./scripts/validate-environment.sh'

# Docker aliases
alias docker-up='docker-compose -f docker-compose.yml up -d'
alias docker-down='docker-compose -f docker-compose.yml down'
alias docker-rebuild='docker-compose -f docker-compose.yml up -d --build'

# Quick status checks
alias gs='git status'
alias gb='git branch -v'
alias gl='git log --oneline -10'
alias gd='git diff'

# Safety aliases (prevent accidental operations)
alias git-force-push='echo "Use save-dev or save-prod instead for safe operations"'
alias git-reset-hard='echo "Use git-save-system.sh for safe operations with backups"'

echo "SynOS Development Environment loaded!"
echo "Available commands:"
echo "  save          - Interactive save system"
echo "  save-dev      - Save development work (dev-team-main -> main)"
echo "  save-prod     - Save to production (main -> master)"
echo "  git-check     - Comprehensive status check"
echo "  build-kernel  - Build kernel components"
echo "  test-all      - Run all tests"
echo "  docker-up     - Start development containers"
EOF

# Create environment variables file
cat > "$REPO_ROOT/.synos-env" << EOF
# SynOS Environment Variables
export SYNOS_ROOT="$REPO_ROOT"
export SYNOS_SCRIPTS="$SCRIPT_DIR"
export SYNOS_LOGS="$REPO_ROOT/logs"
export SYNOS_BACKUPS="$REPO_ROOT/.git-backups"

# Development settings
export RUST_BACKTRACE=1
export CARGO_TARGET_DIR="$REPO_ROOT/target"

# Add scripts to PATH
export PATH="$SCRIPT_DIR:\$PATH"
EOF

echo -e "${BLUE}Creating development profile...${NC}"

# Create comprehensive development profile
cat > "$REPO_ROOT/.synos-profile" << 'EOF'
#!/bin/bash
# SynOS Development Profile
# Complete development environment setup

# Source environment variables
if [ -f "$SYNOS_ROOT/.synos-env" ]; then
    source "$SYNOS_ROOT/.synos-env"
fi

# Source aliases
if [ -f "$SYNOS_ROOT/.synos-aliases" ]; then
    source "$SYNOS_ROOT/.synos-aliases"
fi

# Git configuration for SynOS development
git config --local user.name "${GIT_USER_NAME:-SynOS Developer}"
git config --local user.email "${GIT_USER_EMAIL:-dev@synos.local}"

# Set up git hooks path
git config --local core.hooksPath "$SYNOS_SCRIPTS/git-hooks"

# Create git hooks directory if it doesn't exist
mkdir -p "$SYNOS_SCRIPTS/git-hooks"

# Development environment status
echo "=================================================="
echo "🚀 SynOS Development Environment Active"
echo "=================================================="
echo "Repository: $SYNOS_ROOT"
echo "Current Branch: $(git branch --show-current)"
echo "Git Status: $(git status --porcelain | wc -l) modified files"
echo ""
echo "Quick Commands:"
echo "  save-dev    - Save development work safely"
echo "  save-prod   - Promote to production"
echo "  git-check   - Full repository status"
echo "  test-all    - Run comprehensive tests"
echo "=================================================="
EOF

chmod +x "$REPO_ROOT/.synos-profile"

echo -e "${BLUE}Creating git hooks...${NC}"

# Create git hooks directory
mkdir -p "$SCRIPT_DIR/git-hooks"

# Pre-commit hook
cat > "$SCRIPT_DIR/git-hooks/pre-commit" << 'EOF'
#!/bin/bash
# SynOS Pre-commit Hook
# Runs basic checks before allowing commits

set -e

echo "🔍 Running pre-commit checks..."

# Check for large files
if git diff --cached --name-only | xargs -I {} find {} -size +50M 2>/dev/null | grep -q .; then
    echo "❌ Large files detected (>50MB). Use Git LFS or .gitignore"
    exit 1
fi

# Check for sensitive files
if git diff --cached --name-only | grep -E '\.(key|pem|p12|pfx)$'; then
    echo "❌ Sensitive files detected. Add to .gitignore"
    exit 1
fi

# Check for TODO/FIXME in staged files
if git diff --cached | grep -E '(TODO|FIXME|XXX).*CRITICAL'; then
    echo "⚠️  Critical TODO/FIXME found in staged changes"
    echo "Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Pre-commit checks passed"
EOF

# Pre-push hook
cat > "$SCRIPT_DIR/git-hooks/pre-push" << 'EOF'
#!/bin/bash
# SynOS Pre-push Hook
# Recommends using save system for pushes

echo "🚀 Push detected!"
echo "💡 Consider using the SynOS save system for safer operations:"
echo "   save-dev    - For development work"
echo "   save-prod   - For production releases"
echo ""
echo "Continue with manual push? (y/N)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Push cancelled. Use save-dev or save-prod for guided workflow."
    exit 1
fi
EOF

chmod +x "$SCRIPT_DIR/git-hooks"/*

echo -e "${BLUE}Creating VS Code integration...${NC}"

# Update VS Code settings for the save system
VSCODE_DIR="$REPO_ROOT/.vscode"
mkdir -p "$VSCODE_DIR"

# Add tasks for the save system
if [ -f "$VSCODE_DIR/tasks.json" ]; then
    # Backup existing tasks
    cp "$VSCODE_DIR/tasks.json" "$VSCODE_DIR/tasks.json.backup"
fi

cat > "$VSCODE_DIR/tasks-save-system.json" << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "SynOS: Save Development Work",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/save-dev",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared",
                "showReuseMessage": true,
                "clear": false
            },
            "problemMatcher": []
        },
        {
            "label": "SynOS: Save to Production",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/save-prod",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared",
                "showReuseMessage": true,
                "clear": false
            },
            "problemMatcher": []
        },
        {
            "label": "SynOS: Check Repository Status",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/git-status-check",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared",
                "showReuseMessage": true,
                "clear": false
            },
            "problemMatcher": []
        },
        {
            "label": "SynOS: Interactive Save",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/save",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "shared",
                "showReuseMessage": true,
                "clear": false
            },
            "problemMatcher": []
        }
    ]
}
EOF

# Create keybindings for save system
cat > "$VSCODE_DIR/keybindings-save-system.json" << 'EOF'
[
    {
        "key": "ctrl+shift+s",
        "command": "workbench.action.tasks.runTask",
        "args": "SynOS: Save Development Work"
    },
    {
        "key": "ctrl+shift+alt+s",
        "command": "workbench.action.tasks.runTask",
        "args": "SynOS: Save to Production"
    },
    {
        "key": "ctrl+shift+g",
        "command": "workbench.action.tasks.runTask",
        "args": "SynOS: Check Repository Status"
    }
]
EOF

echo -e "${YELLOW}Creating devcontainer integration...${NC}"

# Update devcontainer configuration
DEVCONTAINER_DIR="$REPO_ROOT/.devcontainer"
mkdir -p "$DEVCONTAINER_DIR"

# Create postCreateCommand script for devcontainer
cat > "$DEVCONTAINER_DIR/setup-save-system.sh" << 'EOF'
#!/bin/bash
# Devcontainer setup for SynOS save system

echo "🚀 Setting up SynOS development environment in devcontainer..."

# Source the development profile
if [ -f "/workspaces/Syn_OS/.synos-profile" ]; then
    source "/workspaces/Syn_OS/.synos-profile"
fi

# Add to bashrc for persistent sessions
if ! grep -q "synos-profile" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# SynOS Development Environment" >> ~/.bashrc
    echo 'if [ -f "/workspaces/Syn_OS/.synos-profile" ]; then' >> ~/.bashrc
    echo '    source "/workspaces/Syn_OS/.synos-profile"' >> ~/.bashrc
    echo 'fi' >> ~/.bashrc
fi

# Set up git configuration
git config --global --add safe.directory /workspaces/Syn_OS

# Install additional development tools
echo "📦 Installing additional development tools..."
sudo apt-get update
sudo apt-get install -y tree htop ncdu jq

echo "✅ SynOS development environment setup complete!"
echo ""
echo "🚀 Quick start:"
echo "  save-dev    - Save your development work"
echo "  save-prod   - Promote to production"
echo "  git-check   - Check repository status"
echo ""
EOF

chmod +x "$DEVCONTAINER_DIR/setup-save-system.sh"

# Create documentation
echo -e "${BLUE}Creating documentation...${NC}"

cat > "$REPO_ROOT/docs/GIT_SAVE_SYSTEM.md" << 'EOF'
# SynOS Git Save System

## Overview

The SynOS Git Save System provides a comprehensive, safe, and automated workflow for managing git operations across the development lifecycle. It replaces manual git commands with intelligent automation that includes testing, validation, and safety checks.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   dev-team-main │───▶│      main       │───▶│     master      │
│   (development) │    │   (staging)     │    │  (production)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       │                        │                        │
       ▼                        ▼                        ▼
   save-dev                 [testing]               save-prod
```

## Commands

### Primary Commands

- **`save-dev`** - Save development work from dev-team-main to main
- **`save-prod`** - Promote main to master for production release
- **`git-check`** - Comprehensive repository status check
- **`save`** - Interactive save system with options

### Workflow

#### Development Workflow (save-dev)
1. **Validation**: Ensures you're on dev-team-main branch
2. **Backup**: Creates automatic backup of current state
3. **Stashing**: Safely stashes uncommitted changes
4. **Testing**: Runs comprehensive test suite
5. **Environment Check**: Validates development environment
6. **Commit**: Commits changes with interactive message prompt
7. **Push**: Safely pushes dev-team-main to remote
8. **Merge**: Merges dev-team-main into main
9. **Testing**: Re-runs tests on main branch
10. **Push**: Pushes main to remote
11. **Cleanup**: Returns to dev-team-main branch

#### Production Workflow (save-prod)
1. **Validation**: Ensures you're on main branch
2. **Backup**: Creates automatic backup
3. **Testing**: Runs comprehensive test suite
4. **Environment Check**: Extended validation for production
5. **Merge**: Merges main into master
6. **Final Testing**: Runs tests on master
7. **Push**: Pushes master to remote
8. **Tagging**: Creates timestamped release tag
9. **Cleanup**: Returns to main branch

## Safety Features

### Automatic Backups
- Creates compressed backups before major operations
- Stored in `.git-backups/` directory
- Timestamped for easy identification

### Test Integration
- Rust: `cargo test --workspace`
- Python: `pytest tests/`
- Make: `make test`
- Security: Custom security audit scripts

### Conflict Prevention
- Force-with-lease pushes prevent overwrites
- Branch validation before operations
- Automatic stashing and restoration
- Merge conflict detection and rollback

### Error Recovery
- Automatic rollback on test failures
- Git tag backups for major operations
- Detailed logging of all operations
- Stash preservation during errors

## Configuration

### Environment Variables
```bash
export SYNOS_ROOT="/path/to/repository"
export SYNOS_SCRIPTS="/path/to/scripts"
export SYNOS_LOGS="/path/to/logs"
export SYNOS_BACKUPS="/path/to/.git-backups"
```

### Git Configuration
```bash
# Set up git hooks
git config --local core.hooksPath "$SYNOS_SCRIPTS/git-hooks"

# Configure user info
git config --local user.name "Your Name"
git config --local user.email "your.email@domain.com"
```

## VS Code Integration

### Tasks
- **Ctrl+Shift+S**: Save Development Work
- **Ctrl+Shift+Alt+S**: Save to Production
- **Ctrl+Shift+G**: Check Repository Status

### Command Palette
- "SynOS: Save Development Work"
- "SynOS: Save to Production"
- "SynOS: Check Repository Status"
- "SynOS: Interactive Save"

## DevContainer Integration

The save system is automatically configured in GitHub Codespaces and devcontainers:

1. **Automatic Setup**: Runs during container creation
2. **Profile Loading**: Adds aliases and environment to shell
3. **Git Configuration**: Sets up safe directories and hooks
4. **Tool Installation**: Installs additional development tools

## Troubleshooting

### Common Issues

#### "Not in a git repository"
- Ensure you're in the SynOS repository directory
- Run `git status` to verify git repository

#### "Tests failed on main"
- Check test output for specific failures
- Fix issues and run `save-dev` again
- Tests are run automatically as safety check

#### "Merge conflict detected"
- System automatically aborts merge and returns to original branch
- Manually resolve conflicts and try again
- Use `git-check` to review repository status

#### "Remote may have been updated"
- Someone else pushed changes to remote
- Run `git fetch` and review changes
- Merge or rebase as appropriate

### Recovery

#### Restore from Backup
```bash
# List available backups
ls -la .git-backups/

# Extract backup (example)
tar -xzf .git-backups/backup_dev-team-main_2025-08-27_14-30-15.tar.gz
```

#### Emergency Reset
```bash
# Find backup tags
git tag | grep backup-pre-merge

# Reset to backup tag
git reset --hard backup-pre-merge-20250827-143015
```

## Logs and Monitoring

### Log Files
- **Location**: `logs/git-save-system.log`
- **Format**: Timestamped entries with operation details
- **Rotation**: Manual cleanup recommended

### Status Monitoring
```bash
# Quick status
git-check

# Detailed branch comparison
git log --graph --oneline --all

# Remote synchronization status
git fetch --dry-run
```

## Best Practices

### Daily Workflow
1. Start day: `git-check` to review status
2. Development: Work on dev-team-main
3. Save work: `save-dev` regularly
4. End day: `git-check` to verify clean state

### Release Workflow
1. Complete features on dev-team-main
2. Use `save-dev` to promote to main
3. Test thoroughly on main branch
4. Use `save-prod` to release to master
5. Verify release with `git-check`

### Emergency Procedures
1. Always check `git-check` before major operations
2. Create manual backup if unsure: `git tag emergency-backup-$(date +%s)`
3. Use system backups in `.git-backups/` for recovery
4. Contact team before force operations

## Advanced Usage

### Custom Test Integration
Add custom tests by modifying `git-save-system.sh`:
```bash
# Add to run_tests() function
if [ -f "$REPO_ROOT/custom-tests.sh" ]; then
    bash "$REPO_ROOT/custom-tests.sh"
fi
```

### Custom Validation
Add custom validation by modifying `validate_environment()`:
```bash
# Check custom requirements
if ! command -v custom-tool > /dev/null; then
    return 1
fi
```

### Hooks Customization
Modify git hooks in `scripts/git-hooks/`:
- `pre-commit`: Runs before each commit
- `pre-push`: Runs before each push

## Support

For issues or questions:
1. Check logs: `tail -f logs/git-save-system.log`
2. Run status check: `git-check`
3. Review this documentation
4. Contact development team
EOF

echo -e "${GREEN}✅ SynOS Development Environment Setup Complete!${NC}"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo "1. Source the development profile:"
echo "   source .synos-profile"
echo ""
echo "2. Available commands:"
echo "   save-dev     - Save development work safely"
echo "   save-prod    - Promote to production"
echo "   git-check    - Check repository status"
echo ""
echo -e "${BLUE}VS Code Integration:${NC}"
echo "   Ctrl+Shift+S       - Save Development Work"
echo "   Ctrl+Shift+Alt+S   - Save to Production"
echo "   Ctrl+Shift+G       - Check Repository Status"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "   docs/GIT_SAVE_SYSTEM.md - Complete guide"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test the system: save-dev"
echo "2. Review documentation: docs/GIT_SAVE_SYSTEM.md"
echo "3. Customize for your workflow"
