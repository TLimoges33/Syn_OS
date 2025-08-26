#!/bin/bash

echo "🎯 Setting up Master Dev Codespace Environment"
echo "=============================================="

# Set proper permissions
chmod +x master_dev_dashboard.py
chmod +x setup_automation.sh
chmod +x run_automation.sh
chmod +x sync_to_master.sh
chmod +x build_iso.sh
chmod +x simple_automation.py
chmod +x automated_workflow_system.py

# Configure git for all teams monitoring
echo "🔧 Configuring Git for multi-team monitoring..."
git config --global user.name "Master Dev Codespace"
git config --global user.email "master-dev@syn-os.dev"
git config --global pull.rebase false
git config --global init.defaultBranch main

# Add master repository as remote (if not already added)
echo "🔗 Setting up repository remotes..."
if ! git remote get-url master >/dev/null 2>&1; then
    git remote add master https://github.com/TLimoges33/Syn_OS.git
    echo "✅ Added master repository remote"
else
    echo "✅ Master repository remote already configured"
fi

# Fetch all branches from both repositories
echo "📡 Fetching all branches..."
git fetch origin
git fetch master 2>/dev/null || echo "⚠️  Master remote fetch failed - continuing with dev-team only"

# Create local tracking branches for all feature branches
echo "🌿 Setting up local tracking branches..."
FEATURE_BRANCHES=(
    "feature/consciousness-kernel"
    "feature/security-framework"
    "feature/education-platform"
    "feature/performance-optimization"
    "feature/enterprise-integration"
    "feature/quantum-computing"
    "feature/documentation-system"
    "feature/testing-framework"
    "feature/iso-building"
    "feature/monitoring-observability"
)

for branch in "${FEATURE_BRANCHES[@]}"; do
    if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        git checkout -b "$branch" "origin/$branch" 2>/dev/null || git checkout "$branch"
        echo "✅ Set up tracking for $branch"
    else
        echo "⚠️  Branch $branch not found on remote"
    fi
done

# Return to main branch
git checkout main

# Install Python dependencies for automation
echo "📦 Installing Python dependencies..."
pip3 install requests python-dateutil --quiet

# Set up GitHub CLI authentication (if not already done)
echo "🔑 Checking GitHub CLI authentication..."
if gh auth status >/dev/null 2>&1; then
    echo "✅ GitHub CLI already authenticated"
    export GITHUB_TOKEN=$(gh auth token)
    echo "export GITHUB_TOKEN=$(gh auth token)" >> ~/.bashrc
else
    echo "⚠️  GitHub CLI not authenticated - some features may be limited"
    echo "   Run 'gh auth login' to enable full automation features"
fi

# Create useful aliases
echo "🔧 Setting up helpful aliases..."
cat >> ~/.bashrc << 'EOF'

# Syn_OS Master Dev Aliases
alias dashboard='python3 /workspaces/Syn_OS-Dev-Team/master_dev_dashboard.py'
alias automation='python3 /workspaces/Syn_OS-Dev-Team/simple_automation.py'
alias checkall='./run_automation.sh'
alias syncmaster='./sync_to_master.sh'
alias buildiso='./build_iso.sh'
alias teams='git branch -a | grep feature/'

# Quick team switching
alias consciousness='git checkout feature/consciousness-kernel'
alias security='git checkout feature/security-framework'
alias education='git checkout feature/education-platform'
alias performance='git checkout feature/performance-optimization'
alias enterprise='git checkout feature/enterprise-integration'
alias quantum='git checkout feature/quantum-computing'
alias documentation='git checkout feature/documentation-system'
alias qa='git checkout feature/testing-framework'
alias build='git checkout feature/iso-building'
alias devops='git checkout feature/monitoring-observability'

echo "🎯 Master Dev Codespace Ready!"
echo "Available commands:"
echo "  dashboard    - Open master dev dashboard"
echo "  automation   - Run automation check"
echo "  checkall     - Check all team branches"
echo "  syncmaster   - Sync to master repository"
echo "  buildiso     - Build ISO"
echo "  teams        - List all feature branches"
echo ""
echo "Quick team switching:"
echo "  consciousness, security, education, performance, enterprise"
echo "  quantum, documentation, qa, build, devops"
EOF

# Create welcome message
cat > /workspaces/Syn_OS-Dev-Team/MASTER_DEV_WELCOME.md << 'EOF'
# 🎯 Welcome to Master Dev Codespace!

You're now in the **central command center** for all Syn_OS development teams.

## 🚀 Quick Start

```bash
dashboard       # Open comprehensive team dashboard
automation      # Run automation check for ready branches
checkall        # Quick status check of all teams
teams           # List all feature branches
```

## 🌿 Team Switching

```bash
consciousness   # Switch to Consciousness team branch
security        # Switch to Security team branch
education       # Switch to Education team branch
performance     # Switch to Performance team branch
enterprise      # Switch to Enterprise team branch
quantum         # Switch to Quantum team branch
documentation   # Switch to Documentation team branch
qa              # Switch to QA team branch
build           # Switch to Build team branch
devops          # Switch to DevOps team branch
```

## 🔄 Pull from Any Team

```bash
git checkout feature/consciousness-kernel
git pull origin feature/consciousness-kernel
```

## 🤖 Automation Control

```bash
syncmaster      # Sync dev-team main to master repository
buildiso        # Build ISO from current state
```

## 📊 Master Dashboard Features

- 📋 **Real-time status** of all 10 development teams
- 🔍 **Completion marker detection** for automation readiness  
- 📈 **Commit tracking** and branch synchronization status
- 🚀 **One-click automation** triggers
- 🔄 **Cross-team collaboration** tools

**Your development superpower awaits!** 🌟
EOF

echo ""
echo "🎉 MASTER DEV CODESPACE SETUP COMPLETE!"
echo "========================================"
echo ""
echo "🎯 You now have full control over all development teams"
echo "📊 Use 'dashboard' to see comprehensive team status"
echo "🔄 Use 'automation' to process ready branches"
echo "🌿 Use team aliases to switch between branches quickly"
echo ""
echo "📋 Available Teams:"
echo "   • Consciousness    • Security      • Education"
echo "   • Performance      • Enterprise    • Quantum"
echo "   • Documentation    • QA            • Build"
echo "   • DevOps"
echo ""
echo "🚀 Ready to coordinate all development activities!"

# Source the new aliases
source ~/.bashrc
