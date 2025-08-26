#!/bin/bash
# Syn_OS Complete Development Environment Setup
# Master setup script for GitHub Codespaces

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
WORKSPACE_ROOT="/workspace"
LOG_FILE="$WORKSPACE_ROOT/logs/setup.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging functions
log() {
    local message="$1"
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $message" | tee -a "$LOG_FILE"
}

error() {
    local message="$1"
    echo -e "${RED}[ERROR]${NC} $message" | tee -a "$LOG_FILE" >&2
}

success() {
    local message="$1"
    echo -e "${GREEN}[SUCCESS]${NC} $message" | tee -a "$LOG_FILE"
}

warn() {
    local message="$1"
    echo -e "${YELLOW}[WARNING]${NC} $message" | tee -a "$LOG_FILE"
}

info() {
    local message="$1"
    echo -e "${CYAN}[INFO]${NC} $message" | tee -a "$LOG_FILE"
}

# Progress tracking
SETUP_STEPS=0
COMPLETED_STEPS=0
FAILED_STEPS=0

step() {
    ((SETUP_STEPS++))
    local step_name="$1"
    echo -e "\n${PURPLE}🔧 Step $SETUP_STEPS: $step_name${NC}" | tee -a "$LOG_FILE"
}

step_success() {
    ((COMPLETED_STEPS++))
    success "Step $SETUP_STEPS completed successfully"
}

step_failed() {
    ((FAILED_STEPS++))
    error "Step $SETUP_STEPS failed"
}

# Main setup function
main() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                  Syn_OS Development Environment Setup                       ║${NC}"
    echo -e "${PURPLE}║                          Version 2025.01                                    ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log "Starting Syn_OS development environment setup"
    log "Workspace: $WORKSPACE_ROOT"
    log "Script location: $SCRIPT_DIR"
    echo ""
    
    # Environment validation
    step "Environment Validation"
    validate_environment
    step_success
    
    # System preparation
    step "System Preparation"
    prepare_system
    step_success
    
    # Core tools installation
    step "Core Development Tools"
    install_core_tools
    step_success
    
    # Language environments
    step "Programming Language Environments"
    setup_language_environments
    step_success
    
    # Security tools
    step "Security Tools Installation"
    install_security_tools
    step_success
    
    # Development services
    step "Development Services Setup"
    setup_development_services
    step_success
    
    # Workspace configuration
    step "Workspace Configuration"
    configure_workspace
    step_success
    
    # VS Code configuration
    step "VS Code Environment"
    configure_vscode
    step_success
    
    # Project initialization
    step "Project Initialization"
    initialize_project
    step_success
    
    # Health verification
    step "Environment Verification"
    verify_environment
    step_success
    
    # Final report
    generate_setup_report
}

# Validation function
validate_environment() {
    log "Validating environment prerequisites..."
    
    # Check if running in correct environment
    if [[ ! "$PWD" == "$WORKSPACE_ROOT"* ]]; then
        warn "Not running in expected workspace directory"
    fi
    
    # Check available resources
    local memory_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$memory_gb" -lt 8 ]; then
        warn "Low memory detected (${memory_gb}GB). Minimum 8GB recommended."
    else
        log "Memory: ${memory_gb}GB (sufficient)"
    fi
    
    local disk_gb=$(df / | awk 'NR==2{print int($4/1024/1024)}')
    if [ "$disk_gb" -lt 20 ]; then
        warn "Low disk space (${disk_gb}GB available)"
    else
        log "Disk space: ${disk_gb}GB available"
    fi
    
    # Check internet connectivity
    if curl -s --max-time 10 https://google.com > /dev/null; then
        log "Internet connectivity: OK"
    else
        error "No internet connectivity detected"
        return 1
    fi
}

# System preparation
prepare_system() {
    log "Preparing system for development..."
    
    # Update package lists
    sudo apt-get update -qq || warn "Package update failed"
    
    # Create necessary directories
    mkdir -p "$WORKSPACE_ROOT"/{logs,build,tmp,config/{local,production}}
    mkdir -p ~/.local/bin
    mkdir -p ~/.config
    
    # Set up permissions
    sudo chown -R "$USER:$USER" "$WORKSPACE_ROOT"
    
    log "System preparation completed"
}

# Core tools installation
install_core_tools() {
    log "Installing core development tools..."
    
    # Essential build tools
    sudo apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        pkg-config \
        curl \
        wget \
        git \
        git-lfs \
        unzip \
        jq \
        tree \
        htop || warn "Some packages failed to install"
    
    log "Core tools installation completed"
}

# Language environments setup
setup_language_environments() {
    log "Setting up programming language environments..."
    
    # Rust installation
    setup_rust_environment
    
    # Python installation
    setup_python_environment
    
    # Go installation
    setup_go_environment
    
    # Node.js installation
    setup_nodejs_environment
    
    # C/C++ tools
    setup_cpp_environment
    
    log "Language environments setup completed"
}

setup_rust_environment() {
    log "Setting up Rust development environment..."
    
    if ! command -v rustc &> /dev/null; then
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
        source ~/.cargo/env
    fi
    
    # Add targets and components
    rustup target add x86_64-unknown-none i686-unknown-none || warn "Failed to add some Rust targets"
    rustup component add rust-src llvm-tools-preview clippy rustfmt || warn "Failed to add some Rust components"
    
    # Install useful cargo tools
    local cargo_tools=("cargo-audit" "cargo-watch" "cargo-expand" "bootimage" "flamegraph")
    for tool in "${cargo_tools[@]}"; do
        cargo install --locked "$tool" || warn "Failed to install $tool"
    done
    
    log "Rust environment setup completed"
}

setup_python_environment() {
    log "Setting up Python development environment..."
    
    # Install Python development packages
    sudo apt-get install -y python3-dev python3-pip python3-venv || warn "Python installation issues"
    
    # Create virtual environment
    python3 -m venv "$WORKSPACE_ROOT/.venv"
    source "$WORKSPACE_ROOT/.venv/bin/activate"
    
    # Upgrade pip and install development tools
    pip install --upgrade pip setuptools wheel
    
    # Install essential Python packages
    pip install \
        black pylint mypy bandit safety \
        pytest pytest-cov pytest-xdist \
        numpy scipy scikit-learn \
        fastapi uvicorn aiohttp requests \
        jupyterlab notebook || warn "Some Python packages failed to install"
    
    log "Python environment setup completed"
}

setup_go_environment() {
    log "Setting up Go development environment..."
    
    # Install Go
    sudo apt-get install -y golang-go || warn "Go installation failed"
    
    # Install Go tools
    if command -v go &> /dev/null; then
        go install golang.org/x/tools/gopls@latest || warn "Failed to install gopls"
        go install golang.org/x/tools/cmd/goimports@latest || warn "Failed to install goimports"
        go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest || warn "Failed to install golangci-lint"
    fi
    
    log "Go environment setup completed"
}

setup_nodejs_environment() {
    log "Setting up Node.js development environment..."
    
    # Install Node.js
    sudo apt-get install -y nodejs npm || warn "Node.js installation failed"
    
    # Install global packages
    if command -v npm &> /dev/null; then
        npm install -g \
            typescript \
            eslint \
            prettier \
            create-react-app \
            vite || warn "Some npm packages failed to install"
    fi
    
    log "Node.js environment setup completed"
}

setup_cpp_environment() {
    log "Setting up C/C++ development environment..."
    
    sudo apt-get install -y \
        llvm clang clang-tools \
        gdb lldb valgrind \
        cppcheck \
        nasm binutils || warn "C/C++ tools installation issues"
    
    log "C/C++ environment setup completed"
}

# Security tools installation
install_security_tools() {
    log "Installing security analysis tools..."
    
    # Install Trivy
    wget -qO- https://github.com/aquasecurity/trivy/releases/latest/download/trivy_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/').tar.gz | tar -xzC /tmp
    sudo mv /tmp/trivy /usr/local/bin/
    
    # Install other security tools
    sudo apt-get install -y \
        nmap \
        tcpdump \
        wireshark-common \
        chkrootkit || warn "Some security tools failed to install"
    
    log "Security tools installation completed"
}

# Development services setup
setup_development_services() {
    log "Setting up development services..."
    
    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        sudo apt-get install -y docker.io docker-compose || warn "Docker installation failed"
        sudo usermod -aG docker "$USER"
    fi
    
    # Install QEMU for kernel development
    sudo apt-get install -y qemu-system-x86 qemu-utils || warn "QEMU installation failed"
    
    log "Development services setup completed"
}

# Workspace configuration
configure_workspace() {
    log "Configuring workspace settings..."
    
    # Create environment configuration
    cat > "$WORKSPACE_ROOT/config/local/.env" << 'EOF'
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
    
    # Configure shell environment
    cat >> ~/.bashrc << 'EOF'

# Syn_OS Development Environment
source /workspace/config/local/.env
export PATH="$HOME/.local/bin:$PATH"

# Rust environment
if [ -f ~/.cargo/env ]; then
    source ~/.cargo/env
fi

# Python virtual environment
if [ -f /workspace/.venv/bin/activate ]; then
    source /workspace/.venv/bin/activate
fi

# Development aliases
alias ll='ls -alF'
alias cb='cargo build'
alias ct='cargo test'
alias cr='cargo run'
alias gs='git status'
alias health='healthcheck.sh'
EOF
    
    log "Workspace configuration completed"
}

# VS Code configuration
configure_vscode() {
    log "Configuring VS Code environment..."
    
    mkdir -p "$WORKSPACE_ROOT/.vscode"
    
    # Create VS Code settings
    cat > "$WORKSPACE_ROOT/.vscode/settings.json" << 'EOF'
{
    "rust-analyzer.cargo.features": "all",
    "rust-analyzer.check.command": "clippy",
    "python.defaultInterpreterPath": "/workspace/.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true,
        "source.organizeImports": true
    },
    "files.watcherExclude": {
        "**/target/**": true,
        "**/.venv/**": true,
        "**/node_modules/**": true
    }
}
EOF
    
    log "VS Code configuration completed"
}

# Project initialization
initialize_project() {
    log "Initializing project structure..."
    
    # Ensure Git is configured
    if ! git config user.name &> /dev/null; then
        git config --global user.name "Syn_OS Developer"
        git config --global user.email "developer@synapticos.dev"
    fi
    
    # Initialize Git hooks if not present
    if [ -d .git ] && [ ! -f .git/hooks/pre-commit ]; then
        log "Setting up Git hooks..."
        # Add basic pre-commit hook for code formatting
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Syn_OS pre-commit hook
set -e

echo "Running pre-commit checks..."

# Format Rust code
if command -v cargo &> /dev/null; then
    cargo fmt --all
fi

# Format Python code
if command -v black &> /dev/null && [ -d src ]; then
    black src/
fi

echo "Pre-commit checks completed"
EOF
        chmod +x .git/hooks/pre-commit
    fi
    
    log "Project initialization completed"
}

# Environment verification
verify_environment() {
    log "Verifying environment setup..."
    
    # Run health check if available
    if [ -f ~/.local/bin/healthcheck.sh ]; then
        chmod +x ~/.local/bin/healthcheck.sh
        if ~/.local/bin/healthcheck.sh > /tmp/health_check_result.log 2>&1; then
            log "Health check passed"
        else
            warn "Health check had issues. See /tmp/health_check_result.log"
        fi
    fi
    
    # Basic tool verification
    local tools=("rustc" "python3" "go" "node" "docker" "git")
    local verified=0
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            ((verified++))
            log "$tool: OK"
        else
            warn "$tool: Not found"
        fi
    done
    
    log "Verified $verified/${#tools[@]} essential tools"
}

# Setup report generation
generate_setup_report() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                           Setup Report                                       ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log "Setup Summary:"
    log "Total steps: $SETUP_STEPS"
    log "Completed: $COMPLETED_STEPS"
    log "Failed: $FAILED_STEPS"
    
    if [ $FAILED_STEPS -eq 0 ]; then
        echo -e "${GREEN}🎉 Syn_OS development environment setup completed successfully!${NC}"
        echo ""
        echo -e "Next steps:"
        echo -e "1. Run ${BLUE}healthcheck.sh${NC} for detailed environment verification"
        echo -e "2. Run ${BLUE}syn-welcome${NC} to see the welcome message"
        echo -e "3. Start developing with ${BLUE}syn-dev build${NC}"
        echo ""
        echo -e "Documentation available at: ${BLUE}CODESPACE_DEVELOPMENT_GUIDE.md${NC}"
    else
        echo -e "${YELLOW}⚠️  Setup completed with $FAILED_STEPS issues${NC}"
        echo -e "Check the log file for details: ${BLUE}$LOG_FILE${NC}"
    fi
    
    # Create setup completion marker
    echo "$(date): Setup completed with $COMPLETED_STEPS/$SETUP_STEPS steps successful" > "$WORKSPACE_ROOT/.setup-completed"
    
    echo ""
    log "Setup process completed"
}

# Error handling
trap 'error "Setup interrupted"; exit 1' INT TERM

# Change to workspace directory
cd "$WORKSPACE_ROOT" 2>/dev/null || {
    warn "Could not change to workspace directory, using current directory"
    WORKSPACE_ROOT="$(pwd)"
}

# Run main setup
main "$@"
