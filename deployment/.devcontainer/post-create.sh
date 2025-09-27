#!/bin/bash

# ==================================================================
# SynOS Codespace Post-Create Script
# ==================================================================
# Runs after the codespace is created and VS Code is ready
# ==================================================================

set -euo pipefail

echo "🔧 Running post-create setup for SynOS..."

# Verify Rust installation
echo "📋 Verifying Rust installation..."
rustc --version
cargo --version

# Check if we're in a git repository
if [ -d ".git" ]; then
    echo "📦 Setting up git repository..."
    
    # Add safe directory (security measure for codespaces)
    git config --global --add safe.directory "$(pwd)"
    
    # Show current branch and remote info
    echo "Current branch: $(git branch --show-current)"
    echo "Remotes configured:"
    git remote -v
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  Warning: There are uncommitted changes in the repository"
        echo "Run 'git status' to see what has changed"
    else
        echo "✅ Repository is clean"
    fi
else
    echo "⚠️  Not in a git repository"
fi

# Run memory optimization setup if available
if [ -f "scripts/laptop-dev-optimization-usermode.sh" ]; then
    echo "🚀 Running VS Code memory optimizations..."
    bash scripts/laptop-dev-optimization-usermode.sh
else
    echo "💡 Memory optimization script not found, using default settings"
fi

# Set up development aliases
echo "🔧 Setting up development aliases..."
cat >> ~/.bashrc << 'EOF'

# SynOS Development Aliases
alias ll='exa -la'
alias ls='exa'
alias cat='bat'
alias find='fd'
alias grep='rg'
alias cargo-check='cargo check --all-targets --all-features'
alias cargo-test='cargo test --all-targets --all-features'
alias cargo-clean-all='cargo clean && rm -rf ~/.cargo/registry/cache'
alias dev-status='free -h && echo "" && ps aux --sort=-%cpu | head -10'

# Git aliases for workflow
alias gst='git status'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gps='git push'
alias gpl='git pull'
alias gcm='git commit -m'
alias gaa='git add .'

# SynOS specific
alias synos-build='cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none'
alias synos-test='cargo test --workspace'
alias synos-security='python3 scripts/a_plus_security_audit.py'
EOF

# Install development monitoring tools if not already present
if [ -f "scripts/laptop-dev-optimization-usermode.sh" ]; then
    echo "📊 Development monitoring tools available:"
    echo "  - dev-memory-monitor: Check memory usage"
    echo "  - dev-memory-cleanup: Clean build artifacts"
    echo "  - vscode-performance-mode: Check VS Code optimization"
fi

# Install Claude Code and 10x development tools
echo "🤖 Installing Claude Code and 10x development tools..."
npm install -g @anthropic-ai/claude-code || echo "Claude Code installation attempted"
npm install -g typescript ts-node nodemon concurrently || echo "Dev tools installation attempted"

# Setup MCP (Model Context Protocol) access for AI tools
echo "🔐 Setting up MCP access for AI tools..."
if [ -f ".devcontainer/setup-mcp-access.sh" ]; then
    chmod +x .devcontainer/setup-mcp-access.sh
    bash .devcontainer/setup-mcp-access.sh
else
    echo "⚠️ MCP setup script not found, manual configuration may be needed"
fi

# Install Rust 10x tools
echo "🦀 Installing Rust 10x development tools..."
cargo install cargo-watch cargo-edit cargo-expand || echo "Rust tools installation attempted"

# Check available resources
echo ""
echo "📊 Codespace Resources:"
echo "CPU: $(nproc) cores"
echo "Memory: $(free -h | grep Mem | awk '{print $2}') total"
echo "Disk: $(df -h / | tail -1 | awk '{print $4}') available"

echo ""
echo "🎉 SynOS development environment ready!"
echo ""
echo "💡 Quick start commands:"
echo "  cargo check              - Check code without building"
echo "  cargo test                - Run all tests"
echo "  synos-build              - Build SynOS kernel"
echo "  dev-status               - Check system resource usage"
echo "  git status               - Check repository status"
echo ""
echo "📚 See docs/development/ for comprehensive guides"
