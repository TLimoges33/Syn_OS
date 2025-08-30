#!/bin/bash
# Codespace-specific setup and troubleshooting script
# Fixes common issues and optimizes environment

set -euo pipefail

echo "🚀 Syn_OS Codespace Environment Setup"
echo "======================================"

# Environment detection
echo "🔍 Environment Detection:"
echo "  User: $(whoami)"
echo "  Home: $HOME"
echo "  PWD: $(pwd)"
echo "  Workspace: ${GITHUB_WORKSPACE:-'Not set'}"
echo "  Codespace: ${CODESPACE_NAME:-'Not detected'}"

# Fix permissions and paths
echo ""
echo "🔧 Fixing Permissions and Paths..."

# Ensure proper ownership
sudo chown -R $(whoami):$(whoami) . 2>/dev/null || echo "Ownership fix skipped"

# Create essential directories with proper permissions
mkdir -p ~/.local/bin ~/.cargo ~/.config
chmod 755 ~/.local/bin ~/.cargo ~/.config

# Add local bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# Fix Cargo configuration for codespace
echo ""
echo "📦 Optimizing Cargo for Codespace..."

# Create optimized Cargo config
cat > ~/.cargo/config.toml << 'EOF'
[build]
jobs = 2
target-dir = "/tmp/cargo-target"

[cargo-new]
vcs = "none"

[net]
retry = 10
git-fetch-with-cli = true

[alias]
quick = "check --bins --lib"
ktest = "test --target x86_64-unknown-none"
krun = "run --target x86_64-unknown-none"
kbuild = "build --target x86_64-unknown-none"
EOF

# Create improved development commands
echo ""
echo "🛠️ Creating Development Commands..."

# Improved new-rust-project
cat > ~/.local/bin/new-rust-project << 'EOF'
#!/bin/bash
# Codespace-optimized Rust project creation

if [[ -z "$1" ]]; then
    echo "Usage: new-rust-project <project-name>"
    exit 1
fi

echo "🦀 Creating Rust project: $1"
echo "📁 Location: $(pwd)/$1"

# Set target directory to avoid conflicts
export CARGO_TARGET_DIR="/tmp/cargo-target-$1"
mkdir -p "$CARGO_TARGET_DIR"

# Create project
cargo new "$1" --vcs none
cd "$1"

echo "✅ Project '$1' created successfully"
echo "📁 Directory: $(pwd)"
echo "🔧 Run 'cargo check' to verify setup"
EOF

# Improved rw command
cat > ~/.local/bin/rw << 'EOF'
#!/bin/bash
# Rust watch with codespace optimization

if [[ ! -f "Cargo.toml" ]]; then
    echo "❌ Error: Not in a Rust project directory"
    echo "💡 Run this command from a directory with Cargo.toml"
    echo "🔧 Or create a project first: new-rust-project my-project"
    exit 1
fi

if ! command -v cargo-watch &> /dev/null; then
    echo "Installing cargo-watch..."
    export CARGO_TARGET_DIR="/tmp/cargo-install"
    cargo install cargo-watch --quiet
fi

echo "🦀 Starting Rust watch mode..."
echo "📁 Project: $(basename $(pwd))"

export CARGO_TARGET_DIR="/tmp/cargo-target-$(basename $(pwd))"
mkdir -p "$CARGO_TARGET_DIR"

cargo watch -x "check --bins --lib"
EOF

# Security scan command
cat > ~/.local/bin/security-scan << 'EOF'
#!/bin/bash
# Comprehensive security scan

echo "🔍 Running security scan..."

# Rust security
if [[ -f "Cargo.toml" ]]; then
    echo "🦀 Rust security audit..."
    if command -v cargo-audit &> /dev/null; then
        cargo audit || echo "Audit completed with warnings"
    else
        echo "Installing cargo-audit..."
        cargo install cargo-audit --quiet
        cargo audit || echo "Audit completed with warnings"  
    fi
fi

# Python security
if command -v python3 &> /dev/null; then
    echo "🐍 Python security scan..."
    find . -name "*.py" -not -path "./.venv/*" | head -10 | xargs -r grep -l -E "(password|secret|key|token)" 2>/dev/null || echo "No Python secrets detected"
fi

# Git secrets
echo "🔑 Checking for secrets..."
git diff --cached --name-only 2>/dev/null | xargs -r grep -l -E "(password|secret|key|token|credential)" 2>/dev/null || echo "No secrets detected in staged files"

echo "✅ Security scan completed"
EOF

# Environment validation
cat > ~/.local/bin/validate-env << 'EOF'
#!/bin/bash
# Quick environment validation

echo "🔍 Environment Validation"
echo "========================"

echo "Languages:"
echo "  Rust: $(rustc --version 2>/dev/null || echo 'Not available')"
echo "  Python: $(python3 --version 2>/dev/null || echo 'Not available')" 
echo "  Node: $(node --version 2>/dev/null || echo 'Not available')"
echo "  Go: $(go version 2>/dev/null || echo 'Not available')"

echo ""
echo "Development Tools:"
echo "  Cargo: $(cargo --version 2>/dev/null || echo 'Not available')"
echo "  Git: $(git --version 2>/dev/null || echo 'Not available')"
echo "  VS Code: $(code --version 2>/dev/null | head -1 || echo 'Not available')"

echo ""
echo "Custom Commands:"
echo "  new-rust-project: $(command -v new-rust-project &>/dev/null && echo 'Available' || echo 'Not available')"
echo "  security-scan: $(command -v security-scan &>/dev/null && echo 'Available' || echo 'Not available')"
echo "  rw: $(command -v rw &>/dev/null && echo 'Available' || echo 'Not available')"

echo ""
echo "Path: $PATH"
EOF

# Make all scripts executable
chmod +x ~/.local/bin/*

# Create development aliases
cat >> ~/.bashrc << 'EOF'

# Syn_OS Development Aliases
alias rs='cargo run'
alias rb='cargo build'
alias rt='cargo test'
alias rc='cargo quick'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias audit='security-scan'
alias validate='validate-env'
alias ll='ls -alF'
alias la='ls -A'
alias ..='cd ..'
alias ...='cd ../..'

# Cargo optimization
export CARGO_TARGET_DIR="/tmp/cargo-target"
export CARGO_NET_RETRY=10

EOF

echo ""
echo "✅ Codespace setup completed!"
echo ""
echo "🛠️ Available commands:"
echo "  new-rust-project <name>  # Create new Rust project"
echo "  security-scan           # Run security analysis"
echo "  rw                      # Rust watch mode"
echo "  validate-env            # Check environment"
echo ""
echo "🔧 To activate:"
echo "  source ~/.bashrc        # Load new environment"
echo ""
echo "🚀 Try: new-rust-project hello-world"