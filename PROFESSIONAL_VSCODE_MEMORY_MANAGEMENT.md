# Professional VS Code Memory Management for Older Hardware

## Current Status: VS Code using 5.3GB RAM (Critical!)

Your VS Code is consuming excessive memory. Here are professional techniques used by developers on resource-constrained systems:

## 🚨 Immediate Actions (Emergency)

### 1. Kill Heavy Language Servers
```bash
pkill -f "pylance"        # Python language server
pkill -f "rust-analyzer"  # Rust language server  
pkill -f "cpptools"       # C++ IntelliSense
pkill -f "intellicode"    # AI-assisted coding
```

### 2. Restart VS Code with Memory Limits
```bash
code --max-memory=2048 --disable-gpu --no-sandbox
```

## 🔧 Professional Configuration Techniques

### 1. Environment Variables (Add to ~/.bashrc)
```bash
# Limit Node.js memory for VS Code extensions
export NODE_OPTIONS="--max-old-space-size=2048"

# Reduce Electron memory overhead
export ELECTRON_DISABLE_SECURITY_WARNINGS=true
export ELECTRON_NO_ATTACH_CONSOLE=true
```

### 2. Advanced VS Code Settings

#### Memory-Critical Settings:
```json
{
    // Limit open editors aggressively
    "workbench.editor.limit.enabled": true,
    "workbench.editor.limit.value": 3,
    "workbench.editor.closeEmptyGroups": true,
    
    // Disable all IntelliSense and suggestions
    "editor.quickSuggestions": false,
    "editor.suggest.enabled": false,
    "editor.inlineSuggest.enabled": false,
    "editor.hover.enabled": false,
    "editor.codeLens": false,
    "editor.minimap.enabled": false,
    
    // Language server memory limits
    "C_Cpp.intelliSenseMemoryLimit": 1024,
    "rust-analyzer.checkOnSave.enable": false,
    "python.analysis.typeCheckingMode": "off",
    
    // File system optimizations
    "files.maxMemoryForLargeFilesMB": 256,
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/target/**": true,
        "**/build/**": true,
        "**/.git/**": true,
        "**/venv*/**": true,
        "**/__pycache__/**": true,
        "**/logs/**": true
    }
}
```

### 3. Extension Management Strategy

#### Disable High-Memory Extensions:
- ✋ GitHub Copilot (300-500MB)
- ✋ GitLens (200-300MB)  
- ✋ IntelliCode (100-200MB)
- ✋ Auto Rename Tag
- ✋ Bracket Pair Colorizer
- ✋ Path Intellisense

#### Keep Only Essential:
- ✅ Language syntax highlighting
- ✅ Basic formatting (if needed)
- ✅ Minimal theme

### 4. System-Level Optimizations

#### Linux/Unix Systems:
```bash
# Reduce system swappiness (as root)
echo 'vm.swappiness=10' >> /etc/sysctl.conf
sysctl vm.swappiness=10

# Clear system caches
sync && echo 3 > /proc/sys/vm/drop_caches
```

#### VS Code Cache Cleanup:
```bash
# Clear workspace cache
rm -rf ~/.config/Code/User/workspaceStorage/*

# Clear extension cache  
rm -rf ~/.config/Code/logs/*
```

## 📊 Memory Monitoring Tools

### Real-time VS Code Memory Usage:
```bash
# Monitor VS Code memory in real-time
watch -n 2 'ps aux | grep -E "[Cc]ode" | grep -v grep | awk "{sum+=\$6} END {print \"VS Code Total: \" sum/1024 \" MB\"}"'
```

### Memory Usage Breakdown:
```bash
# Detailed process breakdown
ps aux | grep -E '[Cc]ode' | grep -v grep | sort -k6 -nr | head -10
```

## 🎯 Professional Workflow Adaptations

### 1. Project Organization
- **One project per window**: Don't use multi-root workspaces
- **Modular development**: Work on one component at a time
- **External tools**: Use separate terminals for builds/tests

### 2. Editor Discipline
- **Close unused tabs immediately**
- **Use file explorer instead of keeping files open**
- **Reload window instead of restarting VS Code**

### 3. Development Workflow
```bash
# Use external terminal for heavy operations
tmux new-session -d 'cargo build'  # Instead of VS Code terminal

# Use lightweight editors for large files
vim large_file.txt  # Instead of opening in VS Code

# Batch editing workflow
code file1.rs  # Edit and close
code file2.rs  # Edit and close
# Instead of keeping all files open
```

## 📈 Performance Benchmarks

### Memory Usage Targets:
- **Critical**: > 4GB (immediate action needed)
- **High**: 2-4GB (optimization recommended)  
- **Acceptable**: 1-2GB (normal for development)
- **Optimal**: < 1GB (lightweight configuration)

### Expected Savings:
- Disabling language servers: 1-2GB
- Limiting editors: 200-500MB
- Disabling suggestions: 300-800MB
- Extension cleanup: 500MB-1GB

## 🚨 Emergency Recovery Script

Use the provided script when VS Code becomes unresponsive:
```bash
./scripts/vscode_memory_emergency.sh
```

## 💡 Pro Tips from Senior Developers

1. **Use VS Code for editing, terminal for everything else**
2. **Keep project dependencies external** (don't rely on VS Code for builds)
3. **Use git from command line** (disable Git decorations in VS Code)
4. **Profile your extensions** regularly
5. **Consider alternative editors** for specific tasks (vim for config files, etc.)

## 📋 Quick Reference Commands

```bash
# Current VS Code memory usage
ps aux | grep -E '[Cc]ode' | awk '{sum+=$6} END {print sum/1024 " MB"}'

# Kill all VS Code processes (emergency)
pkill -f code

# Start VS Code with memory limit
code --max-memory=2048 --disable-gpu

# Clear VS Code cache
rm -rf ~/.config/Code/{logs,CachedData}/*
```

These techniques can reduce VS Code memory usage from 5GB+ down to 1-2GB while maintaining essential development functionality.
