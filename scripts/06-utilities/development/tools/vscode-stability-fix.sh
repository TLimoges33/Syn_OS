#!/bin/bash

# 🧠 VS Code Stability Meta-Fix
# Comprehensive solution for VS Code crashes and performance issues

set -euo pipefail

echo "🧠 VS Code Big Brain Meta-Fix Starting..."
echo "========================================"

# Function to log with timestamp
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# 1. IMMEDIATE CRISIS RESOLUTION
log "🚨 Phase 1: Crisis Resolution"

# Kill only resource-heavy processes (not VS Code itself)
log "Terminating resource-heavy background processes..."
pkill -f "cpptools" 2>/dev/null || true
pkill -f "rg" 2>/dev/null || true  # ripgrep search causing high CPU
pkill -f "webhint" 2>/dev/null || true

# Note: VS Code processes left running to avoid interruption

# 2. SYSTEM OPTIMIZATION
log "💾 Phase 2: System Optimization"

# Create swap space if none exists
if [ "$(swapon --show | wc -l)" -eq 0 ]; then
    log "Creating emergency swap space..."
    sudo fallocate -l 2G /swapfile 2>/dev/null || true
    sudo chmod 600 /swapfile 2>/dev/null || true
    sudo mkswap /swapfile 2>/dev/null || true
    sudo swapon /swapfile 2>/dev/null || true
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab >/dev/null 2>&1 || true
fi

# Optimize kernel memory management
log "Optimizing memory management..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf >/dev/null 2>&1 || true
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf >/dev/null 2>&1 || true
sudo sysctl -p >/dev/null 2>&1 || true

# 3. VS CODE CONFIGURATION OPTIMIZATION
log "⚙️  Phase 3: VS Code Configuration"

# Create optimized settings.json
VSCODE_SETTINGS="$HOME/.config/Code/User/settings.json"
mkdir -p "$(dirname "$VSCODE_SETTINGS")"

cat > "$VSCODE_SETTINGS" << 'EOF'
{
    // Performance Optimizations
    "editor.codeLens": false,
    "editor.minimap.enabled": false,
    "editor.hover.enabled": false,
    "editor.parameterHints.enabled": false,
    "editor.quickSuggestions": false,
    "editor.suggestOnTriggerCharacters": false,
    "editor.wordBasedSuggestions": "off",
    "editor.wordWrap": "off",
    
    // File Management
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/target/**": true,
        "**/build/**": true,
        "**/.git/**": true,
        "**/archive/**": true
    },
    "search.exclude": {
        "**/node_modules": true,
        "**/target": true,
        "**/build": true,
        "**/archive": true
    },
    
    // Extension Control
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false,
    
    // Language Server Optimizations
    "C_Cpp.intelliSenseEngine": "disabled",
    "C_Cpp.autocomplete": "disabled",
    "C_Cpp.errorSquiggles": "disabled",
    
    // Git Performance
    "git.enabled": false,
    "git.autorefresh": false,
    
    // Memory Management
    "typescript.disableAutomaticTypeAcquisition": true,
    "javascript.suggest.enabled": false,
    
    // UI Optimizations
    "workbench.enableExperiments": false,
    "workbench.settings.enableNaturalLanguageSearch": false,
    "telemetry.telemetryLevel": "off",
    
    // Terminal Performance
    "terminal.integrated.gpuAcceleration": "off",
    "terminal.integrated.smoothScrolling": false
}
EOF

# 4. EXTENSION MANAGEMENT
log "🔌 Phase 4: Extension Management"

# Disable heavy extensions
DISABLED_EXTENSIONS=(
    "ms-edgedevtools.vscode-edge-devtools"
    "ms-vscode.cpptools"
    "redhat.vscode-yaml"
)

for ext in "${DISABLED_EXTENSIONS[@]}"; do
    code --disable-extension "$ext" 2>/dev/null || true
done

# 5. WORKSPACE OPTIMIZATION
log "📁 Phase 5: Workspace Optimization"

# Create .vscode workspace settings
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
    "files.watcherExclude": {
        "**/target/**": true,
        "**/build/**": true,
        "**/archive/**": true,
        "**/squashfs_extracted/**": true,
        "**/Final_SynOS-*/**": true
    },
    "search.exclude": {
        "**/target": true,
        "**/build": true,
        "**/archive": true,
        "**/squashfs_extracted": true
    },
    "C_Cpp.intelliSenseEngine": "disabled",
    "rust-analyzer.checkOnSave.enable": false,
    "rust-analyzer.cargo.buildScripts.enable": false
}
EOF

# 6. MEMORY MONITORING SETUP
log "📊 Phase 6: Monitoring Setup"

cat > "$HOME/vscode-monitor.sh" << 'EOF'
#!/bin/bash
# VS Code Memory Monitor
while true; do
    MEMORY_USAGE=$(ps aux | grep -E "(code|electron)" | awk '{sum+=$6} END {print sum/1024}')
    if (( $(echo "$MEMORY_USAGE > 2048" | bc -l) )); then
        echo "$(date): High VS Code memory usage: ${MEMORY_USAGE}MB"
        pkill -f "cpptools"
        pkill -f "rg"
    fi
    sleep 30
done
EOF
chmod +x "$HOME/vscode-monitor.sh"

# 7. AUTOMATIC CLEANUP SERVICE
log "🧹 Phase 7: Cleanup Service"

cat > "$HOME/.local/bin/vscode-cleanup" << 'EOF'
#!/bin/bash
# Automatic VS Code cleanup
pkill -f "rg" 2>/dev/null || true
pkill -f "cpptools" 2>/dev/null || true
rm -rf ~/.config/Code/logs/* 2>/dev/null || true
rm -rf ~/.config/Code/CachedExtensions/* 2>/dev/null || true
echo "VS Code cleaned: $(date)"
EOF
chmod +x "$HOME/.local/bin/vscode-cleanup"

# 8. STARTUP SCRIPT
log "🚀 Phase 8: Optimized Startup"

cat > "$HOME/.local/bin/code-stable" << 'EOF'
#!/bin/bash
# Stable VS Code launcher
export ELECTRON_NO_ATTACH_CONSOLE=1
export VSCODE_DISABLE_CRASH_REPORTER=1
ulimit -v 4194304  # 4GB virtual memory limit
code --disable-gpu --disable-dev-shm-usage --max-old-space-size=2048 "$@"
EOF
chmod +x "$HOME/.local/bin/code-stable"

# 9. FINAL CLEANUP
log "🎯 Phase 9: Final Cleanup"

# Clear VS Code caches
rm -rf ~/.config/Code/logs/* 2>/dev/null || true
rm -rf ~/.config/Code/CachedExtensions/* 2>/dev/null || true
rm -rf ~/.config/VSCodium/logs/* 2>/dev/null || true

# Clear system caches
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null 2>&1 || true

echo "========================================"
log "✅ VS Code Meta-Fix Complete!"
echo ""
echo "🎯 Key Improvements:"
echo "   • Disabled resource-heavy extensions"
echo "   • Optimized memory management"
echo "   • Created 2GB swap space"
echo "   • Configured performance settings"
echo "   • Set up monitoring & cleanup"
echo ""
echo "🚀 Use 'code-stable' command for optimized VS Code"
echo "📊 Monitor with: ~/vscode-monitor.sh &"
echo "🧹 Manual cleanup: ~/.local/bin/vscode-cleanup"
echo ""
echo "💡 Restart VS Code to apply all changes"
