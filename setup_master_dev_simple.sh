#!/bin/bash

echo "🎯 Setting up Master Dev Codespace in Dev-Team Repository"
echo "========================================================"

# Make scripts executable
chmod +x master_dev_dashboard.py
chmod +x .devcontainer/setup-master-dev.sh

# Configure git for master dev environment
git config --global user.name "Master Dev Codespace"
git config --global user.email "master-dev@syn-os.dev"
git config --global pull.rebase false

# Set up GitHub CLI authentication if available
if command -v gh &> /dev/null; then
    if gh auth status >/dev/null 2>&1; then
        echo "✅ GitHub CLI already authenticated"
        export GITHUB_TOKEN=$(gh auth token)
        echo "export GITHUB_TOKEN=\$(gh auth token)" >> ~/.bashrc
    else
        echo "⚠️  Run 'gh auth login' to enable full automation features"
    fi
fi

# Fetch all branches
echo "📡 Fetching all branches..."
git fetch origin

# Set up helpful aliases
echo "🔧 Setting up master dev aliases..."
cat >> ~/.bashrc << 'EOF'

# Master Dev Codespace Aliases
alias dashboard='python3 master_dev_dashboard.py'
alias teams='git branch -r | grep feature/'

echo "🎯 Master Dev Codespace Ready!"
echo "Commands available:"
echo "  dashboard  - Open master development dashboard"
echo "  teams      - List all team feature branches"
EOF

# Source the new configuration
source ~/.bashrc

echo ""
echo "✅ Master Dev Codespace Setup Complete!"
echo "Run 'dashboard' to start monitoring all development teams"
