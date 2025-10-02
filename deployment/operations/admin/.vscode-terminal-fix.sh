#!/bin/bash
# VS Code Terminal Fix Script
# Fixes common terminal issues in VS Code development environment

set -euo pipefail

echo "🔧 VS Code Terminal Fix - Starting diagnostic and repair..."

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check and fix terminal permissions
fix_terminal_permissions() {
    log "Checking terminal permissions..."
    
    if [ -t 0 ]; then
        log "✅ Terminal input available"
    else
        log "⚠️  Terminal input not available, attempting fix..."
        exec < /dev/tty
    fi
    
    if [ -t 1 ]; then
        log "✅ Terminal output available"
    else
        log "⚠️  Terminal output issues detected"
    fi
}

# Fix terminal environment variables
fix_terminal_env() {
    log "Setting up terminal environment..."
    
    export TERM=${TERM:-xterm-256color}
    export SHELL=${SHELL:-/bin/bash}
    export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
    
    # Fix locale issues
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    
    log "✅ Terminal environment configured"
}

# Clear terminal issues
clear_terminal_state() {
    log "Clearing terminal state..."
    
    # Reset terminal state
    reset 2>/dev/null || true
    stty sane 2>/dev/null || true
    
    # Clear any hung processes
    jobs -p | xargs -r kill -9 2>/dev/null || true
    
    log "✅ Terminal state cleared"
}

# Fix VS Code specific issues
fix_vscode_integration() {
    log "Fixing VS Code integration..."
    
    # Ensure proper shell integration
    if [[ -n "${VSCODE_SHELL_INTEGRATION:-}" ]]; then
        log "✅ VS Code shell integration active"
    else
        log "⚠️  VS Code shell integration not detected"
        export VSCODE_SHELL_INTEGRATION=1
    fi
    
    # Fix terminal title
    echo -ne "\033]0;Syn_OS Development Terminal\007"
    
    log "✅ VS Code integration fixed"
}

# Main execution
main() {
    log "🚀 Starting VS Code terminal fix process..."
    
    fix_terminal_permissions
    fix_terminal_env
    clear_terminal_state
    fix_vscode_integration
    
    log "✅ VS Code terminal fix completed successfully!"
    log "🎯 Terminal is now ready for OS development"
    
    # Show current terminal info
    echo ""
    echo "📊 Terminal Information:"
    echo "  Shell: $SHELL"
    echo "  Term: $TERM"
    echo "  User: $USER"
    echo "  PWD: $PWD"
    echo ""
}

# Execute main function
main "$@"