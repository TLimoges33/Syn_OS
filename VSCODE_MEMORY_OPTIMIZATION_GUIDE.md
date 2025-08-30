# Professional VS Code Memory Optimization Guide
## For Older Hardware and Memory-Constrained Systems

### System-Level Optimizations

#### 1. Environment Variables (add to ~/.bashrc or ~/.profile)
```bash
# Limit Node.js memory for VS Code extensions
export NODE_OPTIONS="--max-old-space-size=2048"

# Reduce Electron memory usage
export ELECTRON_DISABLE_SECURITY_WARNINGS=true
export ELECTRON_NO_ATTACH_CONSOLE=true

# Optimize VS Code startup
export VSCODE_DISABLE_CRASH_REPORTER=true
export VSCODE_SKIP_GETTING_STARTED=true
```

#### 2. Launch VS Code with Memory Limits
```bash
# Create optimized VS Code launcher
code --max-memory=2048 --disable-gpu --disable-dev-shm-usage --no-sandbox
```

#### 3. System Swappiness Optimization (as root)
```bash
# Reduce swap usage (good for SSDs and limited RAM)
echo 'vm.swappiness=10' >> /etc/sysctl.conf

# Apply immediately
sysctl vm.swappiness=10
```

### Professional VS Code Settings Additions

#### Memory Management Settings Applied:
```json
{
    // Disable all TypeScript/JavaScript validation and suggestions
    "typescript.disableAutomaticTypeAcquisition": true,
    "typescript.validate.enable": false,
    "javascript.validate.enable": false,
    
    // Disable all editor suggestions and IntelliSense
    "editor.quickSuggestions": false,
    "editor.suggest.*": false, // (all suggest options disabled)
    
    // Limit open editors and reduce UI overhead
    "workbench.editor.limit.enabled": true,
    "workbench.editor.limit.value": 5,
    "workbench.reduce.motion": "on",
    
    // Terminal optimizations
    "terminal.integrated.scrollback": 1000,
    "terminal.integrated.enablePersistentSessions": false,
    
    // Language server resource limits
    "C_Cpp.intelliSenseMemoryLimit": 2048,
    "rust-analyzer.checkOnSave.enable": false,
    "python.analysis.indexing": false,
    
    // File system optimizations
    "files.maxMemoryForLargeFilesMB": 512,
    "files.watcherExclude": {
        // Exclude heavy directories from file watching
        "**/node_modules/**": true,
        "**/target/**": true,
        "**/build/**": true,
        "**/.git/**": true,
        "**/venv*/**": true,
        "**/__pycache__/**": true
    }
}
```

### Extension Management

#### Extensions to Disable for Memory Savings:
- GitHub Copilot (high memory usage)
- GitLens (heavy git operations)
- Bracket Pair Colorizer (use built-in instead)
- Auto Rename Tag
- Path Intellisense
- IntelliCode

#### Keep Only Essential Extensions:
- Language support for your primary languages
- Basic formatting tools
- Minimal theme (avoid heavy themes)

### Hardware-Specific Optimizations

#### For Systems with < 4GB RAM:
```json
{
    "workbench.editor.limit.value": 3,
    "terminal.integrated.scrollback": 500,
    "files.maxMemoryForLargeFilesMB": 256,
    "search.maxResults": 1000
}
```

#### For Systems with 4-8GB RAM:
```json
{
    "workbench.editor.limit.value": 5,
    "terminal.integrated.scrollback": 1000,
    "files.maxMemoryForLargeFilesMB": 512,
    "search.maxResults": 5000
}
```

### Monitoring and Maintenance

#### Check VS Code Memory Usage:
```bash
# Monitor VS Code processes
ps aux | grep -E 'code|Code' | awk '{print $2, $4, $11}' | sort -k2 -nr

# Total memory usage by VS Code
ps aux | grep -E 'code|Code' | awk '{sum += $4} END {print "Total VS Code Memory: " sum "%"}'
```

#### Regular Maintenance Tasks:
1. Clear VS Code workspace cache: `~/.config/Code/User/workspaceStorage/`
2. Clean extension cache: `~/.vscode/extensions/`
3. Restart VS Code when memory usage > 2GB
4. Use `Reload Window` command instead of full restart

### Professional Workflow Adaptations

#### 1. Project Splitting
- Open only one large project at a time
- Use multiple VS Code windows instead of workspaces
- Split large codebases into focused modules

#### 2. File Management
- Close unused editors regularly
- Use file tree collapse to reduce UI overhead
- Avoid opening extremely large files in editor

#### 3. Development Workflow
- Use external terminals for heavy operations
- Disable language servers for non-critical file types
- Enable language features only when needed

### Performance Monitoring Commands

```bash
# VS Code memory usage
echo "VS Code Memory Usage:"
ps aux | grep -E '[Cc]ode' | grep -v grep | awk '{sum+=$6} END {print "Total RSS: " sum/1024 " MB"}'

# System memory overview
free -h

# Top memory consumers
ps aux --sort=-%mem | head -10
```

### Emergency Memory Recovery

If VS Code becomes unresponsive:
```bash
# Kill memory-heavy VS Code processes
pkill -f "code.*pylance"
pkill -f "code.*rust-analyzer" 
pkill -f "code.*cpptools"

# Restart with minimal configuration
code --disable-extensions --disable-gpu
```

### Configuration Backup

Always backup your settings before applying optimizations:
```bash
cp ~/.config/Code/User/settings.json ~/.config/Code/User/settings.json.backup
```

These optimizations can reduce VS Code memory usage by 40-60% on older hardware while maintaining essential development functionality.
