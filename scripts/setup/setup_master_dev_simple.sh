#!/bin/bash

echo "🎯 Setting up Master Dev Codespace in Dev-Team Repository"
echo "========================================================"

# Wait for system to be ready
sleep 5

# Set error handling
set -e

# Make scripts executable
chmod +x master_dev_dashboard.py 2>/dev/null || true
chmod +x .devcontainer/setup-master-dev.sh 2>/dev/null || true

# Configure git for master dev environment
git config --global user.name "Master Dev Codespace" || true
git config --global user.email "master-dev@syn-os.dev" || true
git config --global pull.rebase false || true
git config --global init.defaultBranch main || true

# Ensure Python dependencies are available
echo "📦 Installing Python dependencies..."
pip install --user requests python-dateutil || true

# Install Claude Desktop if not already present
echo "🤖 Installing Claude Desktop..."
if ! command -v claude &> /dev/null; then
    echo "Setting up Claude Desktop installation..."
    # Copy the Claude installer to temp location
    cp install-claude.sh /tmp/install-claude.sh || true
    chmod +x /tmp/install-claude.sh || true
    
    # Run the Claude installer
    bash /tmp/install-claude.sh || echo "⚠️  Claude Desktop installation requires manual setup - use 'setup-claude' command"
else
    echo "✅ Claude Desktop already installed"
fi

# Set up GitHub CLI authentication if available
if command -v gh &> /dev/null; then
    echo "🔑 Checking GitHub CLI authentication..."
    if gh auth status >/dev/null 2>&1; then
        echo "✅ GitHub CLI already authenticated"
        export GITHUB_TOKEN=$(gh auth token)
        echo "export GITHUB_TOKEN=\$(gh auth token)" >> ~/.bashrc || true
    else
        echo "⚠️  Run 'gh auth login' to enable full automation features"
    fi
else
    echo "⚠️  GitHub CLI not available"
fi

# Fetch all branches safely
echo "📡 Fetching all branches..."
git fetch origin --all || git fetch origin || true

# Set up helpful aliases
echo "🔧 Setting up master dev aliases..."
cat >> ~/.bashrc << 'EOF' || true

# Master Dev Codespace Aliases
alias dashboard='python3 dashboard_stable.py'
alias teams='python3 dashboard_stable.py teams'
alias recovery='bash fix_codespace_issues.sh all'
alias help='python3 dashboard_stable.py help'
alias claude='bash claude-launcher.sh'
alias setup-claude='bash /tmp/install-claude.sh'

echo "🎯 Master Dev Codespace Ready!"
echo "Commands available:"
echo "  dashboard  - Open stable master development dashboard"
echo "  teams      - List all team feature branches"
echo "  recovery   - Fix codespace issues"
echo "  claude     - Launch Claude Desktop (with VNC support)"
echo "  help       - Show all commands"
EOF

# Source the new configuration safely
source ~/.bashrc || true

# Create a status file to indicate successful setup
touch /tmp/master_dev_setup_complete

echo ""
echo "✅ Master Dev Codespace Setup Complete!"
echo "🎯 Run 'dashboard' to start monitoring all development teams"
echo "🔧 If you see any extension issues, reload the window: Ctrl+Shift+P → 'Developer: Reload Window'"
