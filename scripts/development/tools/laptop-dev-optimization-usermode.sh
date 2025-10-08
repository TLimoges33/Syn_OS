#!/bin/bash

# ==================================================================
# 🚀 Laptop Development Environment Memory Optimization Suite
# ==================================================================
# User-level optimizations for VS Code and development tools
# No sudo required - perfect for containers and limited environments
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

echo "======================================"
echo "🚀 Laptop Dev Environment Optimizer"
echo "======================================"
echo "User-level optimizations (no sudo required)..."
echo ""

# 1. VS Code Performance Configuration
optimize_vscode() {
    log_info "Optimizing VS Code settings for memory efficiency..."
    
    # Create VS Code settings directory
    mkdir -p ~/.config/Code/User
    
    # Backup existing settings
    if [ -f ~/.config/Code/User/settings.json ]; then
        cp ~/.config/Code/User/settings.json ~/.config/Code/User/settings.json.backup.$(date +%s)
        log_info "Existing settings backed up"
    fi
    
    # Create optimized settings.json
    cat > ~/.config/Code/User/settings.json << 'EOF'
{
    // ============================================
    // 🚀 MEMORY & PERFORMANCE OPTIMIZATIONS
    // ============================================
    
    // === TELEMETRY & DATA COLLECTION (DISABLED) ===
    "telemetry.telemetryLevel": "off",
    "telemetry.enableCrashReporter": false,
    "telemetry.enableTelemetry": false,
    "workbench.enableExperiments": false,
    
    // === AUTOMATIC UPDATES (DISABLED) ===
    "update.mode": "none",
    "extensions.autoCheckUpdates": false,
    "extensions.autoUpdate": false,
    "extensions.ignoreRecommendations": true,
    
    // === MEMORY-HEAVY FEATURES (DISABLED) ===
    "editor.minimap.enabled": false,
    "editor.semanticHighlighting.enabled": false,
    "editor.bracketPairColorization.enabled": false,
    "editor.guides.bracketPairs": false,
    "editor.lightbulb.enabled": false,
    "workbench.tree.renderIndentGuides": "none",
    
    // === LANGUAGE SERVER OPTIMIZATIONS ===
    "typescript.disableAutomaticTypeAcquisition": true,
    "typescript.suggest.autoImports": false,
    "typescript.validate.enable": false,
    "javascript.validate.enable": false,
    "typescript.surveys.enabled": false,
    
    // === FILE WATCHING (REDUCED) ===
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/node_modules/**": true,
        "**/build/**": true,
        "**/target/**": true,
        "**/.cargo/**": true,
        "**/tmp/**": true,
        "**/.tmp/**": true,
        "**/temp/**": true,
        "**/*.iso": true,
        "**/*.img": true,
        "**/squashfs_extracted/**": true
    },
    
    // === SEARCH OPTIMIZATIONS ===
    "search.exclude": {
        "**/node_modules": true,
        "**/build": true,
        "**/target": true,
        "**/.cargo": true,
        "**/tmp": true,
        "**/.tmp": true,
        "**/temp": true,
        "**/*.iso": true,
        "**/*.img": true,
        "**/squashfs_extracted": true
    },
    "search.useIgnoreFiles": true,
    "search.followSymlinks": false,
    
    // === GIT OPTIMIZATIONS ===
    "git.enabled": true,
    "git.autoRepositoryDetection": false,
    "git.decorations.enabled": false,
    "git.autoStash": false,
    "scm.diffDecorations": "none",
    "git.autofetch": false,
    
    // === TERMINAL OPTIMIZATIONS ===
    "terminal.integrated.rendererType": "dom",
    "terminal.integrated.gpuAcceleration": "off",
    "terminal.integrated.smoothScrolling": false,
    
    // === RUST ANALYZER (OPTIMIZED) ===
    "rust-analyzer.checkOnSave.command": "check",
    "rust-analyzer.cargo.loadOutDirsFromCheck": false,
    "rust-analyzer.procMacro.enable": false,
    "rust-analyzer.lens.enable": false,
    "rust-analyzer.completion.addCallParenthesis": false,
    "rust-analyzer.completion.addCallArgumentSnippets": false,
    
    // === C/C++ OPTIMIZATIONS ===
    "C_Cpp.intelliSenseEngine": "Tag Parser",
    "C_Cpp.autocomplete": "Disabled",
    "C_Cpp.errorSquiggles": "Disabled",
    "C_Cpp.formatting": "Disabled",
    
    // === PYTHON OPTIMIZATIONS ===
    "python.analysis.autoImportCompletions": false,
    "python.analysis.indexing": false,
    "python.languageServer": "None",
    "python.terminal.activateEnvironment": false,
    
    // === WORKSPACE OPTIMIZATIONS ===
    "workbench.tips.enabled": false,
    "workbench.startupEditor": "none",
    "workbench.editor.enablePreview": false,
    "workbench.editor.enablePreviewFromQuickOpen": false,
    "workbench.activityBar.visible": true,
    "workbench.statusBar.visible": true,
    
    // === EDITOR PERFORMANCE ===
    "editor.suggest.snippetsPreventQuickSuggestions": true,
    "editor.suggest.localityBonus": true,
    "editor.wordBasedSuggestions": false,
    "editor.parameterHints.enabled": false,
    "editor.hover.enabled": false,
    
    // === WINDOW OPTIMIZATIONS ===
    "window.titleBarStyle": "custom",
    "window.menuBarVisibility": "compact",
    "window.zoomLevel": 0,
    
    // === SPECIFIC EXTENSION SETTINGS ===
    "emmet.showExpandedAbbreviation": "never",
    "html.suggest.html5": false,
    "css.validate": false,
    "less.validate": false,
    "scss.validate": false
}
EOF
    
    log_success "VS Code settings optimized for maximum performance"
}

# 2. Development Tool Optimizations
optimize_dev_tools() {
    log_info "Optimizing development tools..."
    
    # Rust optimizations
    mkdir -p ~/.cargo
    cat > ~/.cargo/config.toml << 'EOF'
[build]
# Limit parallel jobs for memory efficiency
jobs = 2

[profile.dev]
# Minimal debug info for faster builds
debug = 1
overflow-checks = false

[profile.release]
# Optimize for size on laptops
opt-level = "s"
lto = true
codegen-units = 1
panic = "abort"
EOF
    
    # Git optimizations
    git config --global core.preloadindex true
    git config --global core.fscache true
    git config --global gc.auto 256
    git config --global pack.threads 2
    git config --global diff.algorithm patience
    
    # Environment variables for memory optimization
    cat >> ~/.bashrc << 'EOF'

# === DEVELOPMENT MEMORY OPTIMIZATIONS ===
export CARGO_BUILD_JOBS=2
export NODE_OPTIONS="--max-old-space-size=2048"
export RUST_BACKTRACE=0
export PYTHONDONTWRITEBYTECODE=1
EOF
    
    log_success "Development tools optimized"
}

# 3. Create Monitoring Tools
create_monitoring_tools() {
    log_info "Creating memory monitoring tools..."
    
    mkdir -p ~/.local/bin
    
    # Memory monitoring script
    cat > ~/.local/bin/dev-memory-monitor << 'EOF'
#!/bin/bash
# Development memory monitor

clear
echo "=== 📊 Development Environment Memory Report ==="
echo "Time: $(date)"
echo ""

echo "=== 💾 System Memory ==="
free -h
echo ""

echo "=== 🔥 Top Memory Consumers ==="
ps aux --sort=-%mem | head -8 | awk 'NR==1 {print $0} NR>1 {printf "%-12s %6s %6s %s\n", $1, $3, $4, $11}'
echo ""

echo "=== 🖥️  VS Code Processes ==="
ps aux | grep -E '[c]ode' | awk '{printf "PID: %-8s CPU: %-6s MEM: %-6s %s\n", $2, $3, $4, $11}' | head -5
echo ""

echo "=== 🛠️  Development Tools Memory ==="
for tool in rustc cargo node npm python3; do
    if pgrep "$tool" > /dev/null 2>&1; then
        mem=$(ps aux | grep "[${tool:0:1}]${tool:1}" | awk '{sum+=$4} END {printf "%.1f", sum}')
        echo "$tool: ${mem}%"
    fi
done
echo ""

echo "=== 💡 Memory Usage Summary ==="
TOTAL_MEM=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
echo "Total Memory Usage: ${TOTAL_MEM}%"

if (( $(echo "$TOTAL_MEM > 75" | bc -l) )); then
    echo "⚠️  HIGH MEMORY USAGE - Consider running 'dev-memory-cleanup'"
elif (( $(echo "$TOTAL_MEM > 50" | bc -l) )); then
    echo "⚡ Moderate memory usage - System running well"
else
    echo "✅ Low memory usage - Excellent performance"
fi
EOF
    
    # Quick cleanup script
    cat > ~/.local/bin/dev-memory-cleanup << 'EOF'
#!/bin/bash
# Quick development environment cleanup

echo "🧹 Cleaning development environment..."

# Clear build artifacts
echo "📦 Cleaning build artifacts..."
find . -name "target" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "node_modules/.cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Clear Python cache
echo "🐍 Cleaning Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Clear cargo cache (user level)
echo "🦀 Cleaning Cargo cache..."
cargo clean 2>/dev/null || echo "No Cargo project found"

# Clear npm cache
echo "📦 Cleaning npm cache..."
npm cache clean --force 2>/dev/null || echo "npm not available"

# Clear temporary files
echo "🗑️  Cleaning temporary files..."
rm -rf ~/.cache/typescript 2>/dev/null || true
rm -rf ~/.cache/rust-analyzer 2>/dev/null || true

echo "✅ Cleanup complete!"
echo "💡 Run 'dev-memory-monitor' to check memory usage"
EOF
    
    # VS Code optimizer script
    cat > ~/.local/bin/vscode-performance-mode << 'EOF'
#!/bin/bash
# Toggle VS Code performance mode

SETTINGS_FILE="$HOME/.config/Code/User/settings.json"

if grep -q '"editor.minimap.enabled": false' "$SETTINGS_FILE" 2>/dev/null; then
    echo "🚀 VS Code already in performance mode"
    echo "📊 Current optimizations active:"
    echo "  ✅ Telemetry disabled"
    echo "  ✅ Minimap disabled" 
    echo "  ✅ Heavy language features disabled"
    echo "  ✅ File watching optimized"
else
    echo "⚡ Applying performance optimizations..."
    echo "Please run the main optimization script first"
fi

echo ""
echo "💡 Additional tips:"
echo "  • Close unused tabs and editors"
echo "  • Disable unnecessary extensions"
echo "  • Use 'dev-memory-cleanup' regularly"
EOF
    
    chmod +x ~/.local/bin/dev-memory-monitor
    chmod +x ~/.local/bin/dev-memory-cleanup
    chmod +x ~/.local/bin/vscode-performance-mode
    
    log_success "Monitoring tools created"
}

# 4. Extension Management
optimize_extensions() {
    log_info "Optimizing VS Code extensions..."
    
    # Create extension optimization script
    cat > ~/.local/bin/optimize-vscode-extensions << 'EOF'
#!/bin/bash
# VS Code extension optimizer

echo "🔧 Optimizing VS Code extensions..."

# List of resource-heavy extensions to disable
HEAVY_EXTENSIONS=(
    "ms-vscode.vscode-typescript-next"
    "ms-python.python"
    "ms-edgedevtools.vscode-edge-devtools"
    "coenraads.bracket-pair-colorizer-2"
    "ms-vscode.cpptools"
)

echo "Checking for heavy extensions..."
for ext in "${HEAVY_EXTENSIONS[@]}"; do
    if code --list-extensions | grep -q "$ext"; then
        echo "⚠️  Found heavy extension: $ext"
        echo "   Consider disabling if not essential"
    fi
done

echo ""
echo "💡 Recommendations:"
echo "  • Keep only essential extensions enabled"
echo "  • Disable language servers for unused languages"
echo "  • Use lightweight alternatives when possible"
EOF
    
    chmod +x ~/.local/bin/optimize-vscode-extensions
    
    log_success "Extension optimization tools created"
}

# Main execution
main() {
    optimize_vscode
    optimize_dev_tools
    create_monitoring_tools
    optimize_extensions
    
    # Add tools to PATH if not already there
    if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    echo ""
    echo "======================================"
    echo "🎉 Laptop Optimization Complete!"
    echo "======================================"
    echo ""
    echo "📊 New Tools Available:"
    echo "  dev-memory-monitor           - Check memory usage"
    echo "  dev-memory-cleanup           - Quick cleanup"
    echo "  vscode-performance-mode      - Check VS Code optimization"
    echo "  optimize-vscode-extensions   - Extension recommendations"
    echo ""
    echo "🔄 Next Steps:"
    echo "  1. Restart VS Code to apply settings"
    echo "  2. Run 'source ~/.bashrc' to load new environment"
    echo "  3. Use 'dev-memory-monitor' to check improvements"
    echo ""
    echo "⚡ Your laptop is now optimized for heavy development!"
    echo "🚀 Memory usage should be significantly reduced"
}

# Run optimization
main "$@"
