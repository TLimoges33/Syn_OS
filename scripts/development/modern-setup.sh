#!/bin/bash
# Syn_OS Modern Development Environment Setup
# Optimized for security-first development without external dependencies
# Version: 2025.08

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly LOG_FILE="$PROJECT_ROOT/logs/dev-setup.log"

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

step() {
    ((SETUP_STEPS++))
    local step_name="$1"
    echo -e "\n${PURPLE}🔧 Step $SETUP_STEPS: $step_name${NC}"
}

step_success() {
    ((COMPLETED_STEPS++))
    success "Step $SETUP_STEPS completed successfully"
}

# Main setup function
main() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║               Syn_OS Modern Development Environment              ║${NC}"
    echo -e "${PURPLE}║                     Clean & Optimized Setup                     ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log "Starting modern development environment setup"
    log "Project root: $PROJECT_ROOT"
    
    # Environment validation
    step "Environment Validation"
    validate_environment
    step_success
    
    # Clean previous installations
    step "Environment Cleanup"
    cleanup_environment
    step_success
    
    # Core tools installation
    step "Core Development Tools"
    install_core_tools
    step_success
    
    # Language environments
    step "Programming Languages"
    setup_language_environments
    step_success
    
    # Security tools
    step "Security Tools"
    install_security_tools
    step_success
    
    # Development services
    step "Development Services"
    setup_development_services
    step_success
    
    # Project configuration
    step "Project Configuration"
    configure_project
    step_success
    
    # IDE setup
    step "IDE Configuration"
    configure_ide
    step_success
    
    # Environment verification
    step "Verification"
    verify_environment
    step_success
    
    # Final report
    generate_report
}

# Environment validation
validate_environment() {
    log "Validating system requirements..."
    
    # Check OS
    if [[ "$(uname)" != "Linux" ]]; then
        error "This setup is optimized for Linux environments"
        exit 1
    fi
    
    # Check resources
    local memory_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $memory_gb -lt 8 ]]; then
        warn "Memory: ${memory_gb}GB (8GB+ recommended)"
    else
        log "Memory: ${memory_gb}GB ✓"
    fi
    
    # Check disk space
    local disk_gb=$(df "$PROJECT_ROOT" | awk 'NR==2{print int($4/1024/1024)}')
    if [[ $disk_gb -lt 20 ]]; then
        warn "Disk space: ${disk_gb}GB (20GB+ recommended)"
    else
        log "Disk space: ${disk_gb}GB ✓"
    fi
    
    # Check internet
    if curl -s --max-time 10 https://github.com > /dev/null; then
        log "Internet connectivity ✓"
    else
        error "No internet connectivity"
        exit 1
    fi
}

# Clean environment from previous setups
cleanup_environment() {
    log "Cleaning up previous development environment..."
    
    # Remove old Claude/Kilo artifacts
    find "$PROJECT_ROOT" -name ".claude*" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -name ".kilocode*" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*claude*" -name "*.json" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*kilo*" -name "*.json" -delete 2>/dev/null || true
    
    # Clean temporary files
    find "$PROJECT_ROOT" -name "*.tmp" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.log" -not -path "*/logs/*" -delete 2>/dev/null || true
    
    log "Environment cleanup completed"
}

# Install core development tools
install_core_tools() {
    log "Installing essential development tools..."
    
    # Update package lists
    sudo apt-get update -qq
    
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
        zip \
        jq \
        tree \
        htop \
        iotop \
        time \
        ca-certificates \
        gnupg \
        lsb-release
    
    # Performance monitoring tools
    if ! command -v hyperfine &> /dev/null; then
        wget -qO- https://github.com/sharkdp/hyperfine/releases/latest/download/hyperfine_1.18.0_amd64.deb -O /tmp/hyperfine.deb
        sudo dpkg -i /tmp/hyperfine.deb || sudo apt-get install -f -y
        rm -f /tmp/hyperfine.deb
    fi
    
    log "Core tools installation completed"
}

# Setup programming language environments
setup_language_environments() {
    log "Setting up programming language environments..."
    
    setup_rust_environment
    setup_python_environment
    setup_cpp_environment
    setup_go_environment
    
    log "Language environments setup completed"
}

setup_rust_environment() {
    log "Setting up Rust development environment..."
    
    # Install Rust if not present
    if ! command -v rustc &> /dev/null; then
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
        source ~/.cargo/env
    fi
    
    # Update Rust
    rustup update stable
    
    # Add essential targets
    rustup target add x86_64-unknown-none i686-unknown-none
    
    # Add essential components
    rustup component add rust-src llvm-tools-preview clippy rustfmt
    
    # Install useful cargo tools
    local cargo_tools=(
        "cargo-audit"     # Security auditing
        "cargo-watch"     # File watching
        "cargo-expand"    # Macro expansion
        "bootimage"       # Bootable image creation
        "cargo-nextest"   # Better testing
        "cargo-deny"      # Dependency management
    )
    
    for tool in "${cargo_tools[@]}"; do
        if ! cargo install --list | grep -q "^$tool v"; then
            cargo install --locked "$tool" || warn "Failed to install $tool"
        fi
    done
    
    log "Rust environment configured"
}

setup_python_environment() {
    log "Setting up Python development environment..."
    
    # Install Python development packages
    sudo apt-get install -y python3-dev python3-pip python3-venv python3-wheel
    
    # Create virtual environment in project
    if [[ ! -d "$PROJECT_ROOT/.venv" ]]; then
        python3 -m venv "$PROJECT_ROOT/.venv"
    fi
    
    # Activate and upgrade
    source "$PROJECT_ROOT/.venv/bin/activate"
    pip install --upgrade pip setuptools wheel
    
    # Install development tools
    pip install \
        black \
        pylint \
        mypy \
        bandit \
        safety \
        pytest \
        pytest-cov \
        pytest-xdist \
        pre-commit
    
    # Install project dependencies if requirements files exist
    if [[ -f "$PROJECT_ROOT/config/dependencies/requirements-security.txt" ]]; then
        pip install -r "$PROJECT_ROOT/config/dependencies/requirements-security.txt"
    fi
    
    if [[ -f "$PROJECT_ROOT/config/dependencies/requirements-testing.txt" ]]; then
        pip install -r "$PROJECT_ROOT/config/dependencies/requirements-testing.txt"
    fi
    
    log "Python environment configured"
}

setup_cpp_environment() {
    log "Setting up C/C++ development environment..."
    
    sudo apt-get install -y \
        llvm \
        clang \
        clang-tools \
        gdb \
        lldb \
        valgrind \
        cppcheck \
        nasm \
        binutils
    
    log "C/C++ environment configured"
}

setup_go_environment() {
    log "Setting up Go development environment..."
    
    # Install Go
    sudo apt-get install -y golang-go
    
    # Install Go tools
    if command -v go &> /dev/null; then
        go install golang.org/x/tools/gopls@latest
        go install golang.org/x/tools/cmd/goimports@latest
        go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
    fi
    
    log "Go environment configured"
}

# Install security tools
install_security_tools() {
    log "Installing security analysis tools..."
    
    # Install Trivy
    if ! command -v trivy &> /dev/null; then
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    fi
    
    # Install other security tools
    sudo apt-get install -y \
        nmap \
        tcpdump \
        wireshark-common \
        chkrootkit \
        rkhunter
    
    log "Security tools installed"
}

# Setup development services
setup_development_services() {
    log "Setting up development services..."
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo usermod -aG docker "$USER"
    fi
    
    # Install QEMU for kernel development
    sudo apt-get install -y qemu-system-x86 qemu-utils
    
    log "Development services configured"
}

# Configure project settings
configure_project() {
    log "Configuring project environment..."
    
    # Create development environment file
    cat > "$PROJECT_ROOT/config/development/.env" << 'EOF'
# Syn_OS Development Environment
SYN_OS_DEV_MODE=true
RUST_BACKTRACE=1
CARGO_TERM_COLOR=always
LOG_LEVEL=debug
ENVIRONMENT=development

# Development paths
PATH_ADDITIONS=$HOME/.cargo/bin:$HOME/.local/bin

# Security settings
SECURITY_ENABLED=true
AUDIT_LOGGING=true

# Performance settings
RUST_TEST_THREADS=4
CARGO_BUILD_JOBS=4
EOF
    
    # Configure shell environment
    if ! grep -q "Syn_OS Development Environment" ~/.bashrc; then
        cat >> ~/.bashrc << 'EOF'

# Syn_OS Development Environment
if [ -f ~/Syn_OS/config/development/.env ]; then
    set -a
    source ~/Syn_OS/config/development/.env
    set +a
fi

# Rust environment
if [ -f ~/.cargo/env ]; then
    source ~/.cargo/env
fi

# Python virtual environment
if [ -f ~/Syn_OS/.venv/bin/activate ]; then
    source ~/Syn_OS/.venv/bin/activate
fi

# Development aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias cb='cargo build'
alias ct='cargo test'
alias cr='cargo run'
alias cf='cargo fmt'
alias cc='cargo clippy'
alias ca='cargo audit'
alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline'
alias health='scripts/monitoring/healthcheck.sh'
alias syn-build='cargo build --target x86_64-unknown-none'
alias syn-test='cargo test --workspace'
alias syn-run='cargo run --target x86_64-unknown-none'
EOF
    fi
    
    # Setup Git hooks
    if [[ -d "$PROJECT_ROOT/.git" ]]; then
        mkdir -p "$PROJECT_ROOT/.git/hooks"
        
        # Pre-commit hook
        cat > "$PROJECT_ROOT/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Syn_OS pre-commit hook
set -e

echo "Running pre-commit checks..."

# Check if we're in a Rust project
if [ -f Cargo.toml ]; then
    echo "Formatting Rust code..."
    cargo fmt --all -- --check || {
        echo "Code formatting issues found. Run 'cargo fmt --all' to fix."
        exit 1
    }
    
    echo "Running Clippy..."
    cargo clippy -- -D warnings || {
        echo "Clippy found issues. Please fix them."
        exit 1
    }
fi

# Check Python code if present
if [ -d src ] && find src -name "*.py" | grep -q .; then
    if command -v black &> /dev/null; then
        echo "Checking Python formatting..."
        black --check src/ || {
            echo "Python formatting issues found. Run 'black src/' to fix."
            exit 1
        }
    fi
fi

echo "Pre-commit checks passed!"
EOF
        chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"
    fi
    
    log "Project configuration completed"
}

# Configure IDE settings
configure_ide() {
    log "Configuring IDE settings..."
    
    mkdir -p "$PROJECT_ROOT/.vscode"
    
    # VS Code settings
    cat > "$PROJECT_ROOT/.vscode/settings.json" << 'EOF'
{
    "rust-analyzer.cargo.features": "all",
    "rust-analyzer.check.command": "clippy",
    "rust-analyzer.cargo.loadOutDirsFromCheck": true,
    "rust-analyzer.procMacro.enable": true,
    "rust-analyzer.experimental.procAttrMacros": true,
    
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.typeCheckingMode": "basic",
    
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true,
        "source.organizeImports": true
    },
    
    "files.watcherExclude": {
        "**/target/**": true,
        "**/.venv/**": true,
        "**/node_modules/**": true,
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true
    },
    
    "search.exclude": {
        "**/target": true,
        "**/.venv": true,
        "**/node_modules": true
    },
    
    "C_Cpp.clang_format_style": "Google",
    "C_Cpp.intelliSenseEngine": "Tag Parser",
    
    "security.workspace.trust.enabled": false,
    "telemetry.enableCrashReporter": false,
    "telemetry.enableTelemetry": false,
    
    "git.enableSmartCommit": true,
    "git.confirmSync": false,
    
    "terminal.integrated.defaultProfile.linux": "bash"
}
EOF
    
    # VS Code launch configuration
    cat > "$PROJECT_ROOT/.vscode/launch.json" << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Rust",
            "type": "lldb",
            "request": "launch",
            "program": "${workspaceFolder}/target/debug/${workspaceFolderBasename}",
            "args": [],
            "cwd": "${workspaceFolder}",
            "sourceLanguages": ["rust"]
        },
        {
            "name": "Debug Kernel",
            "type": "lldb",
            "request": "launch",
            "program": "${workspaceFolder}/target/x86_64-unknown-none/debug/syn_os",
            "args": [],
            "cwd": "${workspaceFolder}",
            "sourceLanguages": ["rust"]
        }
    ]
}
EOF
    
    log "IDE configuration completed"
}

# Verify environment
verify_environment() {
    log "Verifying development environment..."
    
    local verification_passed=true
    
    # Check essential tools
    local tools=("rustc" "python3" "git" "docker" "clang")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            local version
            case "$tool" in
                rustc) version=$(rustc --version | cut -d' ' -f2) ;;
                python3) version=$(python3 --version | cut -d' ' -f2) ;;
                git) version=$(git --version | cut -d' ' -f3) ;;
                docker) version=$(docker --version | cut -d' ' -f3 | tr -d ',') ;;
                clang) version=$(clang --version | head -n1 | cut -d' ' -f3) ;;
            esac
            log "$tool: $version ✓"
        else
            error "$tool: Not found ✗"
            verification_passed=false
        fi
    done
    
    # Test Rust environment
    if command -v cargo &> /dev/null; then
        if cargo check &> /tmp/cargo_check.log; then
            log "Rust project: Valid ✓"
        else
            warn "Rust project: Issues detected (see /tmp/cargo_check.log)"
        fi
    fi
    
    # Test Python environment
    if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
        log "Python virtual environment: Available ✓"
    else
        warn "Python virtual environment: Not found"
    fi
    
    # Test security tools
    if command -v trivy &> /dev/null && command -v cargo-audit &> /dev/null; then
        log "Security tools: Available ✓"
    else
        warn "Security tools: Incomplete installation"
    fi
    
    if [[ "$verification_passed" == true ]]; then
        success "Environment verification passed"
    else
        warn "Environment verification completed with warnings"
    fi
}

# Generate setup report
generate_report() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                        Setup Complete                           ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log "Modern Development Environment Setup Summary:"
    log "✓ Completed steps: $COMPLETED_STEPS/$SETUP_STEPS"
    log "✓ Claude/Kilo dependencies removed"
    log "✓ Modern toolchain configured"
    log "✓ Security tools installed"
    log "✓ IDE optimized"
    
    echo ""
    echo -e "${GREEN}🎉 Syn_OS development environment ready!${NC}"
    echo ""
    echo -e "Quick start commands:"
    echo -e "  ${BLUE}syn-build${NC}     - Build the kernel"
    echo -e "  ${BLUE}syn-test${NC}      - Run tests"
    echo -e "  ${BLUE}syn-run${NC}       - Run in QEMU"
    echo -e "  ${BLUE}health${NC}        - Check environment health"
    echo ""
    echo -e "Documentation:"
    echo -e "  ${BLUE}docs/guides/QUICK_START.md${NC}      - Getting started"
    echo -e "  ${BLUE}config/development/dev-environment.yaml${NC} - Environment config"
    echo ""
    
    # Create setup completion marker
    echo "Setup completed: $(date)" > "$PROJECT_ROOT/.dev-setup-complete"
    echo "Version: 2025.08" >> "$PROJECT_ROOT/.dev-setup-complete"
    echo "Clean environment: true" >> "$PROJECT_ROOT/.dev-setup-complete"
}

# Error handling
trap 'error "Setup interrupted"; exit 1' INT TERM

# Change to project root
cd "$PROJECT_ROOT"

# Run main setup
main "$@"
