#!/bin/bash

echo "🔧 Codespace Recovery & Extension Fix"
echo "===================================="

# Function to restart extension host
restart_extensions() {
    echo "🔄 Restarting extension host..."
    pkill -f "extensionHost" 2>/dev/null || true
    sleep 2
    echo "✅ Extension host restart initiated"
}

# Function to clear VS Code cache
clear_vscode_cache() {
    echo "🧹 Clearing VS Code cache..."
    rm -rf ~/.vscode-server/data/User/workspaceStorage/* 2>/dev/null || true
    rm -rf ~/.vscode-server/data/logs/* 2>/dev/null || true
    rm -rf /tmp/vscode-* 2>/dev/null || true
    echo "✅ VS Code cache cleared"
}

# Function to fix permissions
fix_permissions() {
    echo "🔑 Fixing file permissions..."
    chmod +x master_dev_dashboard.py 2>/dev/null || true
    chmod +x setup_master_dev_simple.sh 2>/dev/null || true
    chmod +x .devcontainer/*.sh 2>/dev/null || true
    echo "✅ Permissions fixed"
}

# Function to reinstall key extensions
reinstall_extensions() {
    echo "🔄 Reinstalling key extensions..."
    code --install-extension ms-python.python --force 2>/dev/null || true
    code --install-extension GitHub.copilot --force 2>/dev/null || true
    code --install-extension eamodio.gitlens --force 2>/dev/null || true
    echo "✅ Key extensions reinstalled"
}

# Main recovery process
echo "🚨 Starting Codespace Recovery Process..."

case "${1:-all}" in
    "extensions")
        restart_extensions
        reinstall_extensions
        ;;
    "cache")
        clear_vscode_cache
        ;;
    "permissions")
        fix_permissions
        ;;
    "all")
        fix_permissions
        clear_vscode_cache
        restart_extensions
        reinstall_extensions
        ;;
    *)
        echo "Usage: $0 [extensions|cache|permissions|all]"
        exit 1
        ;;
esac

echo ""
echo "🎯 Recovery Complete!"
echo "📋 Next Steps:"
echo "1. Reload the window: Ctrl+Shift+P → 'Developer: Reload Window'"
echo "2. If issues persist, try: Ctrl+Shift+P → 'Codespaces: Rebuild Container'"
echo "3. Run 'dashboard' to test functionality"

# Create recovery completion marker
touch /tmp/codespace_recovery_complete
echo "✅ Recovery marker created"
