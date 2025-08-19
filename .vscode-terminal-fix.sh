# VS Code Terminal Configuration Fix
# This file ensures NVM and other tools are available in VS Code terminals

# Check if running in VS Code terminal and NVM isn't loaded
if [[ $TERM_PROGRAM == "vscode" ]] && [[ -z "$NVM_DIR" ]]; then
    # Load NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    
    # Load cargo/rust environment
    [ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
    
    echo "🔧 Loaded development environment for VS Code terminal"
fi
