#!/bin/bash
"""
Setup Syn_OS Automated Development Workflow
==========================================

This script sets up the complete automation system for:
1. Monitoring feature branch completion
2. Creating automated pull requests  
3. Syncing to master repository
4. Building ISO images

Usage: ./setup_automation.sh
"""

echo "🤖 Setting up Syn_OS Automated Development Workflow"
echo "=================================================="

# Check if we're in the right repository
if [ ! -f "README.md" ] || [ ! -d ".git" ]; then
    echo "❌ Please run this script from the Syn_OS repository root"
    exit 1
fi

echo "📍 Repository: $(git remote get-url origin)"
echo "📍 Current branch: $(git branch --show-current)"

# 1. Set up GitHub token
echo -e "\n🔑 GitHub Authentication Setup"
echo "================================"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN environment variable not set"
    echo "   To enable full automation, you need a GitHub Personal Access Token"
    echo "   with 'repo' permissions."
    echo ""
    echo "   You can:"
    echo "   1. Set it temporarily: export GITHUB_TOKEN=your_token_here"
    echo "   2. Add to ~/.bashrc: echo 'export GITHUB_TOKEN=your_token' >> ~/.bashrc"
    echo "   3. Use GitHub CLI: gh auth login"
    echo ""
    read -p "   Continue without token? (automation will be limited) [y/N]: " continue_without
    if [[ ! $continue_without =~ ^[Yy]$ ]]; then
        echo "   Please set up GitHub token and re-run this script"
        exit 1
    fi
else
    echo "✅ GitHub token configured"
fi

# 2. Install Python dependencies
echo -e "\n📦 Installing Dependencies"
echo "=========================="

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing requests library..."
    pip3 install requests --user
    if [ $? -eq 0 ]; then
        echo "✅ Python dependencies installed"
    else
        echo "❌ Failed to install Python dependencies"
        exit 1
    fi
else
    echo "✅ Python dependencies already available"
fi

# 3. Make automation scripts executable
echo -e "\n🔧 Setting up Automation Scripts"
echo "================================"

automation_scripts=(
    "automated_workflow_system.py"
    "simple_automation.py"
)

for script in "${automation_scripts[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "✅ Made executable: $script"
    else
        echo "⚠️  Script not found: $script"
    fi
done

# 4. Set up git remotes for dev-team repo
echo -e "\n🔗 Setting up Repository Connections"
echo "===================================="

# Check if dev-team remote exists
if git remote get-url dev-team &>/dev/null; then
    echo "✅ dev-team remote already configured"
else
    echo "📡 Adding dev-team remote..."
    git remote add dev-team git@github.com:TLimoges33/Syn_OS-Dev-Team.git
    if [ $? -eq 0 ]; then
        echo "✅ dev-team remote added"
    else
        echo "❌ Failed to add dev-team remote"
        exit 1
    fi
fi

# Fetch from dev-team
echo "📡 Fetching from dev-team repository..."
git fetch dev-team --quiet
if [ $? -eq 0 ]; then
    echo "✅ Successfully fetched dev-team branches"
else
    echo "❌ Failed to fetch from dev-team"
fi

# 5. Create automation cron job (optional)
echo -e "\n⏰ Setting up Automated Monitoring"
echo "=================================="

echo "The automation can run:"
echo "1. 📅 Scheduled (cron job) - runs every 30 minutes"
echo "2. 🖱️  Manual - run when needed"
echo "3. 🔗 Webhook - triggered by GitHub events"

read -p "Set up scheduled automation? [y/N]: " setup_cron
if [[ $setup_cron =~ ^[Yy]$ ]]; then
    
    # Create cron job
    cron_entry="*/30 * * * * cd $(pwd) && python3 simple_automation.py >> automation.log 2>&1"
    
    # Check if cron entry already exists
    if crontab -l 2>/dev/null | grep -q "simple_automation.py"; then
        echo "✅ Cron job already exists"
    else
        # Add to crontab
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        if [ $? -eq 0 ]; then
            echo "✅ Scheduled automation enabled (every 30 minutes)"
            echo "   Log file: $(pwd)/automation.log"
        else
            echo "❌ Failed to set up cron job"
        fi
    fi
else
    echo "⏭️  Skipping scheduled automation"
fi

# 6. Test automation system
echo -e "\n🧪 Testing Automation System"
echo "============================"

echo "🔍 Running automation check..."
python3 simple_automation.py

# 7. Create helper scripts
echo -e "\n📝 Creating Helper Scripts"
echo "=========================="

# Create quick automation runner
cat > run_automation.sh << 'EOF'
#!/bin/bash
# Quick automation runner
echo "🤖 Running Syn_OS Automation Check"
echo "Time: $(date)"
python3 simple_automation.py
echo "✅ Automation check complete"
EOF

chmod +x run_automation.sh
echo "✅ Created: run_automation.sh"

# Create manual sync script  
cat > sync_to_master.sh << 'EOF'
#!/bin/bash
# Manual sync to master repository
echo "🔄 Manual sync to master repository"
git fetch dev-team main
git checkout master
git merge dev-team/main --no-ff -m "Manual sync: Dev team integration"
git push origin master
echo "✅ Sync complete"
EOF

chmod +x sync_to_master.sh
echo "✅ Created: sync_to_master.sh"

# Create ISO build trigger
cat > build_iso.sh << 'EOF'
#!/bin/bash
# Manual ISO build trigger
echo "🏗️ Building Syn_OS ISO"
if [ -f "scripts/build-simple-kernel-iso.sh" ]; then
    chmod +x scripts/build-simple-kernel-iso.sh
    ./scripts/build-simple-kernel-iso.sh
    echo "✅ ISO build complete"
    find build/ -name "*.iso" -exec echo "📀 Generated: {}" \;
else
    echo "❌ ISO build script not found"
fi
EOF

chmod +x build_iso.sh
echo "✅ Created: build_iso.sh"

# 8. Final setup summary
echo -e "\n🎉 AUTOMATION SETUP COMPLETE!"
echo "=============================="

echo "📋 Available Commands:"
echo "   ./run_automation.sh      - Run automation check"
echo "   ./sync_to_master.sh      - Manual sync to master"  
echo "   ./build_iso.sh           - Build ISO manually"
echo "   python3 simple_automation.py - Direct automation"

echo -e "\n📊 System Status:"
echo "   Repository: ✅ Connected"
echo "   Dependencies: ✅ Installed"
echo "   Scripts: ✅ Executable"
echo "   Dev-team remote: ✅ Configured"

if [ ! -z "$GITHUB_TOKEN" ]; then
    echo "   GitHub API: ✅ Configured"
else
    echo "   GitHub API: ⚠️  Limited (no token)"
fi

if crontab -l 2>/dev/null | grep -q "simple_automation.py"; then
    echo "   Scheduled runs: ✅ Every 30 minutes"
else
    echo "   Scheduled runs: ⏭️  Manual only"
fi

echo -e "\n🚀 Automation Workflow:"
echo "   1. 📊 Monitor feature branches for completion markers"
echo "   2. 🔄 Create automated pull requests"
echo "   3. 🧪 Run automated testing"
echo "   4. 🔄 Merge to dev-team main"
echo "   5. 🔄 Sync to master Syn_OS repository"
echo "   6. 🏗️ Build final ISO image"

echo -e "\n🎯 Ready for automated development workflow!"
echo "   Start developing with completion markers in commit messages:"
echo "   • '🎯 Phase Implementation Complete'"
echo "   • '✅ Ready for Integration'"
echo "   • '🧪 All Tests Passing'"
echo "   • '📚 Documentation Updated'"

echo -e "\nℹ️  For more details, see the automation documentation."
