#!/bin/bash

# ==================================================================
# 🚀 Laptop Development Environment Memory Optimization Suite
# ==================================================================
# Optimizes VS Code, system settings, and development tools for
# heavy-duty development on memory-constrained laptops
# ==================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "======================================"
echo "🚀 Laptop Dev Environment Optimizer"
echo "======================================"
echo "Optimizing for heavy-duty development..."
echo ""

# 1. VS Code Performance Configuration
optimize_vscode() {
    log_info "Optimizing VS Code settings for memory efficiency..."
    
    # Create VS Code settings directory if it doesn't exist
    mkdir -p ~/.config/Code/User
    
    # Create optimized settings.json
    cat > ~/.config/Code/User/settings.json << 'EOF'
{
    // ============================================
    // 🚀 MEMORY & PERFORMANCE OPTIMIZATIONS
    // ============================================
    
    // Disable telemetry and data collection
    "telemetry.telemetryLevel": "off",
    "telemetry.enableCrashReporter": false,
    "telemetry.enableTelemetry": false,
    
    // Disable automatic updates and background tasks
    "update.mode": "none",
    "extensions.autoCheckUpdates": false,
    "extensions.autoUpdate": false,
    
    // Memory management
    "typescript.disableAutomaticTypeAcquisition": true,
    "typescript.suggest.autoImports": false,
    "typescript.validate.enable": false,
    "javascript.validate.enable": false,
    
    // Editor optimizations
    "editor.minimap.enabled": false,
    "editor.suggest.snippetsPreventQuickSuggestions": false,
    "editor.suggest.localityBonus": true,
    "editor.semanticHighlighting.enabled": false,
    "editor.bracketPairColorization.enabled": false,
    "editor.guides.bracketPairs": false,
    
    // File watching optimizations
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/node_modules/**": true,
        "**/build/**": true,
        "**/target/**": true,
        "**/.cargo/**": true,
        "**/tmp/**": true,
        "**/.tmp/**": true,
        "**/temp/**": true
    },
    
    // Search optimizations
    "search.exclude": {
        "**/node_modules": true,
        "**/build": true,
        "**/target": true,
        "**/.cargo": true,
        "**/tmp": true,
        "**/.tmp": true,
        "**/temp": true,
        "**/*.iso": true,
        "**/*.img": true
    },
    
    // Git optimizations
    "git.enabled": true,
    "git.autoRepositoryDetection": false,
    "git.decorations.enabled": false,
    "git.autoStash": false,
    "scm.diffDecorations": "none",
    
    // Terminal optimizations
    "terminal.integrated.rendererType": "dom",
    "terminal.integrated.gpuAcceleration": "off",
    
    // Language server optimizations
    "rust-analyzer.checkOnSave.command": "check",
    "rust-analyzer.cargo.loadOutDirsFromCheck": false,
    "rust-analyzer.procMacro.enable": false,
    "rust-analyzer.lens.enable": false,
    
    // C/C++ optimizations
    "C_Cpp.intelliSenseEngine": "Tag Parser",
    "C_Cpp.autocomplete": "Disabled",
    "C_Cpp.errorSquiggles": "Disabled",
    
    // Python optimizations
    "python.analysis.autoImportCompletions": false,
    "python.analysis.indexing": false,
    "python.languageServer": "None",
    
    // Workspace optimizations
    "workbench.enableExperiments": false,
    "workbench.tips.enabled": false,
    "workbench.startupEditor": "none",
    "workbench.tree.renderIndentGuides": "none",
    
    // Extension optimizations
    "extensions.ignoreRecommendations": true,
    "workbench.extensions.ignoreRecommendations": true,
    
    // Performance monitoring
    "window.titleBarStyle": "custom",
    "window.menuBarVisibility": "compact"
}
EOF
    
    log_success "VS Code settings optimized for memory efficiency"
}

# 2. System Memory Optimizations
optimize_system() {
    log_info "Applying system-level memory optimizations..."
    
    # Create swap file if none exists (essential for memory-constrained systems)
    if [ ! -f /swapfile ]; then
        log_info "Creating 4GB swap file for memory overflow protection..."
        sudo fallocate -l 4G /swapfile 2>/dev/null || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        
        # Make swap permanent
        if ! grep -q "/swapfile" /etc/fstab; then
            echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        fi
        log_success "4GB swap file created and activated"
    else
        log_info "Swap file already exists"
    fi
    
    # Optimize swappiness for development workloads
    echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-dev-optimization.conf
    echo 'vm.dirty_ratio=15' | sudo tee -a /etc/sysctl.d/99-dev-optimization.conf
    echo 'vm.dirty_background_ratio=5' | sudo tee -a /etc/sysctl.d/99-dev-optimization.conf
    sudo sysctl -p /etc/sysctl.d/99-dev-optimization.conf
    
    log_success "System memory parameters optimized"
}

# 3. Development Tool Optimizations
optimize_dev_tools() {
    log_info "Optimizing development tools for memory efficiency..."
    
    # Rust optimizations
    mkdir -p ~/.cargo
    cat > ~/.cargo/config.toml << 'EOF'
[build]
# Use fewer parallel jobs to reduce memory usage
jobs = 2

[profile.dev]
# Reduce debug info for faster compilation and less memory
debug = 1
overflow-checks = false

[profile.release]
# Optimize for size over speed on laptops
opt-level = "s"
lto = true
codegen-units = 1
EOF
    
    # Git optimizations for large repositories
    git config --global core.preloadindex true
    git config --global core.fscache true
    git config --global gc.auto 256
    git config --global pack.threads 2
    
    log_success "Development tools optimized"
}

# 4. Browser Memory Management
optimize_browsers() {
    log_info "Setting up browser memory management..."
    
    # Create script to manage browser memory
    cat > ~/.local/bin/browser-memory-guard << 'EOF'
#!/bin/bash
# Browser memory guard - kills resource-heavy browser processes

MEMORY_THRESHOLD=80  # Kill processes if memory usage > 80%

while true; do
    MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    
    if [ "$MEMORY_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
        # Kill heavy browser processes
        pkill -f "chrome.*--type=renderer" 2>/dev/null || true
        pkill -f "firefox.*content" 2>/dev/null || true
        echo "$(date): Memory at ${MEMORY_USAGE}% - cleaned browser processes"
    fi
    
    sleep 30
done
EOF
    
    chmod +x ~/.local/bin/browser-memory-guard
    log_success "Browser memory guard installed"
}

# 5. Development Environment Monitoring
create_monitoring_tools() {
    log_info "Creating development environment monitoring tools..."
    
    # Memory monitoring script
    cat > ~/.local/bin/dev-memory-monitor << 'EOF'
#!/bin/bash
# Development memory monitor - tracks resource usage

echo "=== Development Environment Memory Report ==="
echo "Date: $(date)"
echo ""

echo "=== System Memory ==="
free -h
echo ""

echo "=== Top Memory Consumers ==="
ps aux --sort=-%mem | head -10
echo ""

echo "=== VS Code Processes ==="
ps aux | grep -E 'code|vscodium' | grep -v grep | awk '{printf "%-8s %-6s %-6s %s\n", $2, $3, $4, $11}'
echo ""

echo "=== Development Tool Memory Usage ==="
for tool in rustc cargo node npm python3 git; do
    if pgrep "$tool" > /dev/null; then
        echo "$tool: $(ps aux | grep "$tool" | grep -v grep | awk '{sum+=$4} END {printf "%.1f%%\n", sum}')"
    fi
done
EOF
    
    chmod +x ~/.local/bin/dev-memory-monitor
    
    # Quick memory cleanup script
    cat > ~/.local/bin/dev-memory-cleanup << 'EOF'
#!/bin/bash
# Quick development environment memory cleanup

echo "🧹 Cleaning development environment memory..."

# Clear system caches
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

# Clean cargo cache
cargo clean 2>/dev/null || true

# Clean npm cache
npm cache clean --force 2>/dev/null || true

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Clean build artifacts
rm -rf build/ target/ node_modules/.cache/ 2>/dev/null || true

echo "✅ Memory cleanup complete"
EOF
    
    chmod +x ~/.local/bin/dev-memory-cleanup
    
    log_success "Monitoring tools created in ~/.local/bin/"
}

# 6. VS Code Extension Management
manage_vscode_extensions() {
    log_info "Managing VS Code extensions for optimal performance..."
    
    # Disable resource-heavy extensions
    HEAVY_EXTENSIONS=(
        "bracket-pair-colorizer"
        "auto-rename-tag"
        "path-intellisense"
        "vscode-icons"
        "material-icon-theme"
    )
    
    for ext in "${HEAVY_EXTENSIONS[@]}"; do
        code --disable-extension "$ext" 2>/dev/null || true
    done
    
    log_success "Heavy extensions disabled"
}

# Main execution
main() {
    log_info "Starting laptop development environment optimization..."
    
    optimize_vscode
    optimize_system
    optimize_dev_tools
    optimize_browsers
    create_monitoring_tools
    manage_vscode_extensions
    
    echo ""
    echo "======================================"
    echo "🎉 Optimization Complete!"
    echo "======================================"
    echo ""
    echo "📊 New Tools Available:"
    echo "  dev-memory-monitor    - Check memory usage"
    echo "  dev-memory-cleanup    - Quick memory cleanup"
    echo "  browser-memory-guard  - Background browser management"
    echo ""
    echo "🔄 Recommended Actions:"
    echo "  1. Restart VS Code to apply settings"
    echo "  2. Run 'dev-memory-monitor' to check current usage"
    echo "  3. Use 'dev-memory-cleanup' when memory gets tight"
    echo ""
    echo "⚡ Your laptop is now optimized for heavy development!"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
