#!/bin/bash

# 🚀 SynOS Development Environment Setup Script
# Sets up the complete development environment for SynOS v1.0

set -e

echo "🚀 Setting up SynOS v1.0 Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in SynOS directory
if [[ ! -f "SynOS-Focused.code-workspace" ]]; then
    print_error "Please run this script from the SynOS root directory"
    exit 1
fi

print_status "Setting up development environment for SynOS v1.0..."

# 1. Install system dependencies
print_status "Installing system dependencies..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y \
        build-essential \
        curl \
        git \
        python3 \
        python3-pip \
        python3-venv \
        nodejs \
        npm \
        docker.io \
        docker-compose \
        qemu-system-x86 \
        nasm \
        grub-pc-bin \
        xorriso \
        mtools
    print_success "System dependencies installed"
elif command -v dnf &> /dev/null; then
    sudo dnf install -y \
        gcc \
        make \
        curl \
        git \
        python3 \
        python3-pip \
        nodejs \
        npm \
        docker \
        docker-compose \
        qemu-system-x86 \
        nasm \
        grub2-tools \
        xorriso \
        mtools
    print_success "System dependencies installed"
else
    print_warning "Unsupported package manager. Please install dependencies manually."
fi

# 2. Install Rust if not present
if ! command -v rustc &> /dev/null; then
    print_status "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    print_success "Rust installed"
else
    print_status "Rust already installed"
fi

# 3. Install Rust targets for kernel development
print_status "Installing Rust targets for kernel development..."
rustup target add x86_64-unknown-none
rustup component add rust-src
rustup component add llvm-tools-preview
print_success "Rust targets installed"

# 4. Set up Python virtual environment
print_status "Setting up Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    print_success "Python virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip

# Install Python dependencies
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
fi

# Install additional development tools
pip install \
    black \
    flake8 \
    pylint \
    pytest \
    mypy \
    bandit \
    safety

print_success "Python environment configured"

# 5. Install local Claude if available via npm
print_status "Checking for local Claude installation..."
if command -v npm &> /dev/null; then
    # Check if Claude CLI is available
    if npm list -g @anthropic/claude 2>/dev/null; then
        print_success "Claude CLI already installed"
    else
        print_status "Installing Claude development tools..."
        # Note: This is a placeholder - adjust based on actual Claude local installation
        npm install -g @anthropic/claude 2>/dev/null || print_warning "Claude CLI not available via npm"
    fi
fi

# 6. Set up Git hooks
print_status "Setting up Git hooks..."
mkdir -p .git/hooks

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for SynOS

echo "🔍 Running pre-commit checks..."

# Format Rust code
cargo fmt --all

# Check Rust code
cargo check --target x86_64-unknown-none

# Format Python code
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
    find . -name "*.py" -not -path "./venv/*" -not -path "./target/*" | xargs black
fi

echo "✅ Pre-commit checks completed"
EOF

chmod +x .git/hooks/pre-commit
print_success "Git hooks configured"

# 7. Configure Docker (if available)
if command -v docker &> /dev/null; then
    print_status "Configuring Docker for development..."
    
    # Add user to docker group if not already
    if ! groups | grep -q docker; then
        sudo usermod -aG docker $USER
        print_warning "Added user to docker group. Please log out and log back in."
    fi
    
    # Test Docker
    if docker ps &> /dev/null; then
        print_success "Docker configured and running"
    else
        print_warning "Docker not running. Please start Docker service."
    fi
fi

# 8. Set up development database (if needed)
print_status "Setting up development services..."
if [[ -f "docker/docker-compose.yml" ]]; then
    cd docker
    docker-compose up -d nats postgres redis 2>/dev/null || print_warning "Could not start development services"
    cd ..
    print_success "Development services started"
fi

# 9. Build initial kernel
print_status "Building initial kernel..."
if make kernel 2>/dev/null; then
    print_success "Kernel built successfully"
else
    print_warning "Kernel build failed. Check dependencies."
fi

# 10. Create helpful aliases
print_status "Creating development aliases..."
cat > .synos-aliases << 'EOF'
# SynOS Development Aliases
alias synos-build='make kernel'
alias synos-test='make test'
alias synos-format='make format'
alias synos-audit='python3 scripts/a_plus_security_audit.py'
alias synos-consciousness='python3 core/consciousness/consciousness_bridge.py'
alias synos-iso='./scripts/build-simple-kernel-iso.sh'
alias synos-dev='source venv/bin/activate'
alias synos-clean='make clean && docker system prune -f'
alias synos-status='git status && docker ps && ls -la build/'
EOF

print_success "Development aliases created (source .synos-aliases to use)"

# 11. Final validation
print_status "Validating development environment..."

# Check Rust
if rustc --version &> /dev/null; then
    print_success "✅ Rust: $(rustc --version)"
else
    print_error "❌ Rust not working"
fi

# Check Python
if python3 --version &> /dev/null; then
    print_success "✅ Python: $(python3 --version)"
else
    print_error "❌ Python not working"
fi

# Check Node.js
if node --version &> /dev/null; then
    print_success "✅ Node.js: $(node --version)"
else
    print_warning "⚠️  Node.js not available"
fi

# Check Docker
if docker --version &> /dev/null; then
    print_success "✅ Docker: $(docker --version)"
else
    print_warning "⚠️  Docker not available"
fi

print_success "🎉 SynOS Development Environment Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Source the aliases: source .synos-aliases"
echo "2. Activate Python environment: source venv/bin/activate"
echo "3. Open VS Code: code SynOS-Focused.code-workspace"
echo "4. Run initial build: make kernel"
echo "5. Run tests: make test"
echo ""
echo "🔧 Available Commands:"
echo "  synos-build     - Build kernel"
echo "  synos-test      - Run tests"
echo "  synos-format    - Format code"
echo "  synos-audit     - Security audit"
echo "  synos-iso       - Build ISO"
echo ""
echo "Happy coding! 🚀"
