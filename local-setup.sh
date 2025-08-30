#!/bin/bash
# Local setup script for immediate development
# Creates the essential commands locally

set -euo pipefail

echo "🔧 Setting up local development commands..."

# Create local bin directory
mkdir -p ~/.local/bin

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create new-rust-project command
cat > ~/.local/bin/new-rust-project << 'EOF'
#!/bin/bash
# Create new Rust project with security best practices
if [[ -z "$1" ]]; then
    echo "Usage: new-rust-project <project-name>"
    exit 1
fi

echo "🦀 Creating Rust project: $1"
echo "📁 Current directory: $(pwd)"

# Use CARGO_TARGET_DIR to avoid file conflicts
export CARGO_TARGET_DIR="/tmp/cargo-target-$USER"
mkdir -p "$CARGO_TARGET_DIR"

cargo new "$1" --vcs none
cd "$1"

# Add common dependencies with retry and file sync
echo "Adding dependencies with file sync..."
sync
sleep 1
cargo add serde --features derive --offline=false || echo "serde dependency may need manual addition"
sync
sleep 1  
cargo add anyhow --offline=false || echo "anyhow dependency may need manual addition"
sync
sleep 1
cargo add thiserror --offline=false || echo "thiserror dependency may need manual addition"

# Create basic security configuration
cat > deny.toml << 'EOD'
[graph]
targets = []

[licenses]
allow = ["MIT", "Apache-2.0", "BSD-3-Clause"]

[bans]
multiple-versions = "warn"
wildcards = "allow"

[advisories]
version = 2
yanked = "deny"
EOD

echo "✅ Rust project '$1' created with security configuration"
echo "📁 Directory: $(pwd)"
echo "🔧 Run 'cargo run' to test"
EOF

# Create security-scan command
cat > ~/.local/bin/security-scan << 'EOF'
#!/bin/bash
# Local security scan script

echo "🔍 Running local security scan..."

# Rust security
if command -v cargo &> /dev/null && [[ -f Cargo.toml ]]; then
    echo "🦀 Rust security audit..."
    if command -v cargo-audit &> /dev/null; then
        cargo audit
    else
        echo "Installing cargo-audit..."
        cargo install cargo-audit
        cargo audit
    fi
    
    if command -v cargo-deny &> /dev/null; then
        cargo deny check
    else
        echo "Installing cargo-deny..."  
        cargo install cargo-deny
        cargo deny check
    fi
fi

# Python security
if command -v python3 &> /dev/null; then
    echo "🐍 Python security scan..."
    if command -v bandit &> /dev/null; then
        find . -name "*.py" -not -path "./.venv/*" | xargs bandit -r || true
    else
        echo "Install bandit: pip install bandit"
    fi
fi

# Git secrets check
echo "🔑 Checking for potential secrets..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    git diff --cached --name-only | xargs grep -l -E "(password|secret|key|token|credential)" 2>/dev/null || echo "No secrets detected"
else
    grep -r -E "(password|secret|key|token|credential)" --include="*.rs" --include="*.py" . || echo "No secrets detected"
fi

echo "✅ Security scan completed"
EOF

# Create rw (rust watch) command
cat > ~/.local/bin/rw << 'EOF'
#!/bin/bash
# Rust watch command with codespace optimization

if ! command -v cargo-watch &> /dev/null; then
    echo "Installing cargo-watch..."
    export CARGO_TARGET_DIR="/tmp/cargo-target-install"
    cargo install cargo-watch
fi

# Check if we're in a Rust project
if [[ ! -f "Cargo.toml" ]]; then
    echo "❌ Error: Not in a Rust project directory"
    echo "💡 Run this command from a directory with Cargo.toml"
    echo "🔧 Or create a project first: new-rust-project my-project"
    exit 1
fi

echo "🦀 Starting Rust watch mode..."
echo "📁 Project: $(pwd)"
export CARGO_TARGET_DIR="/tmp/cargo-target-$(basename $(pwd))"
mkdir -p "$CARGO_TARGET_DIR"
cargo watch -x "check --bins --lib" -x "test --lib"
EOF

# Create development aliases script
cat > ~/.local/bin/setup-aliases << 'EOF'
#!/bin/bash
# Setup development aliases

cat >> ~/.bashrc << 'ALIASES'

# Syn_OS Development Aliases
alias rs='cargo run'
alias rb='cargo build'
alias rt='cargo test'
alias rc='cargo check'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias audit='security-scan'
alias ll='ls -alF'
alias la='ls -A'
alias ..='cd ..'
alias ...='cd ../..'

ALIASES

echo "✅ Development aliases added to ~/.bashrc"
echo "Run 'source ~/.bashrc' or restart terminal to use aliases"
EOF

# Make all scripts executable
chmod +x ~/.local/bin/new-rust-project
chmod +x ~/.local/bin/security-scan
chmod +x ~/.local/bin/rw
chmod +x ~/.local/bin/setup-aliases

echo "✅ Local development commands created!"
echo ""
echo "🛠️ Available commands:"
echo "   new-rust-project <name>  # Create new Rust project"
echo "   security-scan           # Run security analysis"
echo "   rw                      # Rust watch mode"
echo "   setup-aliases           # Add development aliases"
echo ""
echo "🔧 To activate:"
echo "   source ~/.bashrc        # Load new PATH"
echo "   setup-aliases           # Add convenient aliases"
echo ""
echo "🚀 Try: new-rust-project test-project"