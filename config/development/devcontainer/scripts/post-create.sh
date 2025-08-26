#!/bin/bash
# Syn_OS Development Environment Post-Create Setup
# Runs after container is created to configure development environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Syn_OS Development Environment Setup${NC}"
echo -e "${BLUE}=======================================${NC}"

# Function to print status
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Ensure we're in the workspace directory
cd /workspace

log "Setting up Git configuration..."
if [ ! -f ~/.gitconfig ]; then
    git config --global init.defaultBranch main
    git config --global core.editor "code --wait"
    git config --global pull.rebase false
    git config --global push.autoSetupRemote true
    success "Git configuration completed"
else
    log "Git already configured"
fi

log "Creating development directories..."
mkdir -p ~/.local/bin
mkdir -p ~/.config
mkdir -p /workspace/.vscode
mkdir -p /workspace/build
mkdir -p /workspace/logs
mkdir -p /workspace/tmp
success "Development directories created"

log "Setting up Rust development environment..."
if [ -f ~/.cargo/env ]; then
    source ~/.cargo/env
    
    # Ensure required targets are installed
    rustup target add x86_64-unknown-none || warn "Failed to install x86_64-unknown-none target"
    rustup target add i686-unknown-none || warn "Failed to install i686-unknown-none target"
    
    # Install additional useful tools if not present
    cargo install --locked cargo-watch 2>/dev/null || warn "cargo-watch already installed or failed to install"
    cargo install --locked cargo-expand 2>/dev/null || warn "cargo-expand already installed or failed to install"
    
    success "Rust environment setup completed"
else
    error "Rust not properly installed"
fi

log "Setting up Python virtual environment..."
if command -v python3 &> /dev/null; then
    python3 -m venv /workspace/.venv || warn "Failed to create virtual environment"
    if [ -f /workspace/.venv/bin/activate ]; then
        source /workspace/.venv/bin/activate
        pip install --upgrade pip setuptools wheel
        
        # Install development requirements if they exist
        if [ -f requirements-dev.txt ]; then
            pip install -r requirements-dev.txt || warn "Failed to install some Python dependencies"
        fi
        
        success "Python virtual environment setup completed"
    fi
else
    error "Python3 not available"
fi

log "Configuring VS Code workspace settings..."
cat > /workspace/.vscode/settings.json << 'EOF'
{
    "rust-analyzer.cargo.features": "all",
    "rust-analyzer.check.command": "clippy",
    "rust-analyzer.check.extraArgs": ["--all-targets"],
    "python.defaultInterpreterPath": "/workspace/.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "go.toolsManagement.autoUpdate": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true,
        "source.organizeImports": true
    },
    "files.watcherExclude": {
        "**/target/**": true,
        "**/.venv/**": true,
        "**/node_modules/**": true,
        "**/build/**": true
    },
    "terminal.integrated.env.linux": {
        "RUST_BACKTRACE": "1",
        "CARGO_TERM_COLOR": "always"
    }
}
EOF
success "VS Code workspace settings configured"

log "Setting up workspace-specific tools..."
# Create useful aliases
cat >> ~/.bashrc << 'EOF'

# Syn_OS Development Aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Rust aliases
alias cb='cargo build'
alias ct='cargo test'
alias cc='cargo check'
alias cr='cargo run'
alias cw='cargo watch -x check -x test -x run'

# Python aliases
alias py='python3'
alias piv='python3 -m venv'
alias pia='source .venv/bin/activate'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'
alias gd='git diff'

# Syn_OS specific
alias health='healthcheck.sh'
alias syros-build='cargo build --workspace'
alias syros-test='cargo test --workspace'
alias syros-run='cargo run --bin syn-kernel'

EOF

log "Setting up development scripts..."
# Create quick development script
cat > ~/.local/bin/syn-dev << 'EOF'
#!/bin/bash
# Syn_OS Quick Development Helper

case "$1" in
    "health")
        healthcheck.sh
        ;;
    "build")
        echo "Building Syn_OS workspace..."
        cargo build --workspace
        ;;
    "test")
        echo "Running Syn_OS tests..."
        cargo test --workspace
        ;;
    "run")
        echo "Running Syn_OS kernel..."
        cargo run --bin syn-kernel
        ;;
    "clean")
        echo "Cleaning build artifacts..."
        cargo clean
        rm -rf build/* logs/* tmp/*
        ;;
    "setup")
        echo "Setting up development environment..."
        rustup update
        cargo update
        pip install --upgrade pip
        ;;
    *)
        echo "Syn_OS Development Helper"
        echo "Usage: syn-dev [health|build|test|run|clean|setup]"
        echo ""
        echo "Commands:"
        echo "  health  - Run environment health check"
        echo "  build   - Build the entire workspace"
        echo "  test    - Run all tests"
        echo "  run     - Run the kernel"
        echo "  clean   - Clean build artifacts"
        echo "  setup   - Update development tools"
        ;;
esac
EOF

chmod +x ~/.local/bin/syn-dev
success "Development scripts installed"

log "Setting up service configurations..."
# Create local configuration directory
mkdir -p /workspace/config/local

# Create environment file
cat > /workspace/config/local/.env << 'EOF'
# Syn_OS Development Environment Configuration
SYNAPTICOS_ENV=development
RUST_BACKTRACE=1
CARGO_TERM_COLOR=always
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=dev-token
NATS_URL=nats://localhost:4222
REDIS_URL=redis://localhost:6379
LOG_LEVEL=debug
EOF
success "Service configurations created"

log "Setting up Docker development environment..."
if command -v docker &> /dev/null; then
    # Pull commonly used images
    docker pull nats:latest &
    docker pull redis:alpine &
    docker pull postgres:14-alpine &
    wait
    success "Docker development images pulled"
else
    warn "Docker not available, skipping image pulls"
fi

log "Configuring shell environment..."
# Source environment in bashrc
echo "source /workspace/config/local/.env" >> ~/.bashrc
echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc

# Set up completion
if [ -f ~/.cargo/env ]; then
    echo "source ~/.cargo/env" >> ~/.bashrc
fi

log "Running initial health check..."
if healthcheck.sh > /tmp/healthcheck.log 2>&1; then
    success "Health check passed"
else
    warn "Health check had issues. Check /tmp/healthcheck.log for details"
fi

log "Creating welcome message..."
cat > ~/.local/bin/syn-welcome << 'EOF'
#!/bin/bash
echo -e "\033[0;34m"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                          Syn_OS Development Environment                      ║"
echo "║                     AI-Enhanced Cybersecurity Operating System              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "\033[0m"
echo ""
echo "Welcome to the Syn_OS development environment!"
echo ""
echo "Quick start commands:"
echo "  syn-dev health  - Check environment health"
echo "  syn-dev build   - Build the entire project"
echo "  syn-dev test    - Run all tests"
echo "  syn-dev run     - Run the kernel"
echo ""
echo "Development directories:"
echo "  /workspace/src/          - Source code"
echo "  /workspace/docs/         - Documentation"
echo "  /workspace/tests/        - Test suites"
echo "  /workspace/build/        - Build artifacts"
echo ""
echo "For more information, see README.md or run 'syn-dev' without arguments."
echo ""
EOF

chmod +x ~/.local/bin/syn-welcome
echo "syn-welcome" >> ~/.bashrc

success "Post-create setup completed successfully!"
log "Development environment is ready for Syn_OS development"
echo ""
