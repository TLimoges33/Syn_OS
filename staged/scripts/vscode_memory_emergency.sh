#!/bin/bash
# VS Code Memory Emergency Optimizer
# For immediate memory relief on older hardware

echo "🚨 VS Code Memory Emergency Optimizer"
echo "====================================="

# Check current memory usage
echo "📊 Current Memory Status:"
free -h
echo ""

echo "📊 VS Code Memory Usage:"
VSCODE_MEMORY=$(ps aux | grep -E '[Cc]ode' | grep -v grep | awk '{sum+=$6} END {print sum/1024}')
echo "Total VS Code Memory: ${VSCODE_MEMORY} MB"
echo ""

if (( $(echo "$VSCODE_MEMORY > 3000" | bc -l) )); then
    echo "⚠️  WARNING: VS Code using > 3GB RAM - Emergency optimization needed!"
    
    # Kill memory-heavy language servers
    echo "🔄 Stopping memory-heavy language servers..."
    pkill -f "pylance" 2>/dev/null || true
    pkill -f "rust-analyzer" 2>/dev/null || true  
    pkill -f "cpptools" 2>/dev/null || true
    pkill -f "intellicode" 2>/dev/null || true
    
    sleep 2
    
    # Check memory after cleanup
    NEW_MEMORY=$(ps aux | grep -E '[Cc]ode' | grep -v grep | awk '{sum+=$6} END {print sum/1024}')
    SAVED=$(echo "$VSCODE_MEMORY - $NEW_MEMORY" | bc -l)
    echo "💾 Memory saved: ${SAVED} MB"
    echo "📊 New VS Code memory usage: ${NEW_MEMORY} MB"
    
else
    echo "✅ VS Code memory usage is acceptable (< 3GB)"
fi

echo ""
echo "🔧 Applying emergency VS Code settings..."

# Create emergency memory settings
cat > /tmp/emergency_vscode_settings.json << 'EOF'
{
    // Emergency memory settings - overrides existing config
    "workbench.editor.limit.enabled": true,
    "workbench.editor.limit.value": 3,
    "workbench.editor.closeEmptyGroups": true,
    
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false,
    "extensions.ignoreRecommendations": true,
    
    "editor.quickSuggestions": {
        "other": false,
        "comments": false,
        "strings": false
    },
    "editor.suggest.enabled": false,
    "editor.inlineSuggest.enabled": false,
    "editor.hover.enabled": false,
    "editor.lightbulb.enabled": "off",
    "editor.codeLens": false,
    "editor.minimap.enabled": false,
    
    "python.analysis.autoImportCompletions": false,
    "python.analysis.typeCheckingMode": "off",
    "python.linting.enabled": false,
    
    "rust-analyzer.checkOnSave.enable": false,
    "rust-analyzer.inlayHints.enable": false,
    "rust-analyzer.lens.enable": false,
    
    "C_Cpp.intelliSenseEngine": "disabled",
    "C_Cpp.intelliSenseMemoryLimit": 1024,
    
    "terminal.integrated.scrollback": 500,
    "terminal.integrated.enablePersistentSessions": false,
    
    "files.maxMemoryForLargeFilesMB": 256,
    "search.maxResults": 1000,
    
    "telemetry.telemetryLevel": "off",
    "workbench.enableExperiments": false,
    "workbench.reduce.motion": "on"
}
EOF

echo "💾 Emergency settings created in /tmp/emergency_vscode_settings.json"
echo "📋 To apply: Copy contents to your .vscode/settings.json"
echo ""

echo "🔧 Additional optimizations you can apply:"
echo "1. Restart VS Code: Ctrl+Shift+P -> 'Developer: Reload Window'"
echo "2. Close unused editor tabs"
echo "3. Disable extensions you don't need right now"
echo "4. Set environment variable: export NODE_OPTIONS='--max-old-space-size=2048'"
echo ""

echo "📊 Final memory check:"
free -h

echo ""
echo "✅ Emergency optimization complete!"
