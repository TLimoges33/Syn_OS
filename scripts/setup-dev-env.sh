#!/bin/bash
# SynapticOS Development Environment Setup
# This script installs all necessary tools for OS development

set -e

echo "🚀 Setting up SynapticOS Development Environment..."

# Update system (skip if repositories have issues)
echo "📦 Updating system packages..."
sudo apt update || echo "Warning: Some repositories failed to update, continuing..."

# Install essential OS development tools (fixed package names)
echo "🔧 Installing core development tools..."
sudo apt install -y \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    libssl-dev \
    libudev-dev \
    llvm \
    clang \
    lld \
    gdb \
    valgrind \
    strace \
    ltrace \
    bsdextrautils \
    binutils \
    nasm \
    qemu-system \
    qemu-utils || echo "Some packages may not be available on this system"

# Install Rust with additional targets for OS development
echo "🦀 Installing Rust with OS development targets..."
if ! command -v rustc &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    echo 'source ~/.cargo/env' >> ~/.bashrc
fi

# Add Rust to current session
export PATH="$HOME/.cargo/bin:$PATH"

# Install Rust targets and components
rustup target add x86_64-unknown-none || echo "Rust target installation may require manual setup"
rustup target add i686-unknown-none || echo "32-bit target may not be available"
rustup component add rust-src || echo "Rust source component may need manual installation"
rustup component add llvm-tools-preview || echo "LLVM tools may need manual installation"

# Install Python tools for system analysis
echo "🐍 Installing Python development tools..."
pip3 install --user --break-system-packages \
    capstone \
    keystone-engine \
    requests \
    pyyaml || echo "Some Python packages may need manual installation"

# Install Go tools for security tooling
echo "🔷 Installing Go development tools..."
if command -v go &> /dev/null; then
    go version
    echo "Go tools installation would go here"
else
    echo "Go not found, skipping Go-specific tools"
fi

# Install monitoring and debugging tools
echo "📊 Installing monitoring tools..."
sudo apt install -y \
    htop \
    iotop \
    tcpdump \
    linux-tools-common || echo "Some monitoring tools may not be available"

# Setup project structure
echo "📁 Creating SynapticOS project structure..."
mkdir -p src/{security,consciousness,kernel,frontend}
mkdir -p {tools,tests,scripts/build,scripts/deploy}

echo "✅ SynapticOS Development Environment setup complete!"
echo ""
echo "🔧 Manual setup still needed:"
echo "1. Configure QEMU for OS testing: qemu-system-x86_64 --version"
echo "2. Verify Rust installation: cargo --version"
echo "3. Set up additional security tools as needed"
echo ""
echo "📝 Next steps:"
echo "1. Run: source ~/.bashrc"
echo "2. Test Rust: rustc --version"
echo "3. Start developing your first kernel module"
