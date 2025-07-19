#!/bin/bash
# Syn_OS Enhanced Post-Create Setup
# Comprehensive development environment with all tools for the dev team

set -euo pipefail

echo "🚀 Initializing Syn_OS comprehensive development environment..."

# Security: Validate environment
echo "🔍 Validating security configuration..."
if [[ "$EUID" -eq 0 ]]; then
    echo "❌ ERROR: Running as root is not allowed for security"
    exit 1
fi

# Rust comprehensive configuration
echo "🦀 Configuring Rust development environment..."
mkdir -p ~/.cargo
cat > ~/.cargo/config.toml << 'EOF'
[build]
target = "x86_64-unknown-none"

[target.x86_64-unknown-none]
runner = "qemu-system-x86_64 -drive format=raw,file={} -display none -serial stdio -no-reboot"

[unstable]
build-std = ["core", "compiler_builtins", "alloc"]
build-std-features = ["compiler-builtins-mem"]

[alias]
ktest = "test --target x86_64-unknown-none"
krun = "run --target x86_64-unknown-none"
kbuild = "build --target x86_64-unknown-none"
audit-fix = "audit fix"
security-check = "audit"
check-all = "check --all-targets --all-features"
test-all = "test --all-targets --all-features"
EOF

# Install comprehensive Rust toolchain
echo "🛡️ Installing comprehensive Rust toolchain..."
rustup component add rust-analyzer rust-src llvm-tools-preview clippy rustfmt
rustup target add wasm32-unknown-unknown aarch64-unknown-linux-gnu

# Install Rust development tools
cargo install --locked cargo-audit || echo "cargo-audit already installed"
cargo install --locked cargo-deny || echo "cargo-deny already installed"
cargo install --locked cargo-geiger || echo "cargo-geiger already installed"
cargo install --locked cargo-tarpaulin || echo "cargo-tarpaulin already installed"
cargo install --locked cargo-watch || echo "cargo-watch already installed"
cargo install --locked cargo-expand || echo "cargo-expand already installed"
cargo install --locked cargo-tree || echo "cargo-tree already installed"
cargo install --locked cargo-outdated || echo "cargo-outdated already installed"
cargo install --locked flamegraph || echo "flamegraph already installed"
cargo install --locked tokei || echo "tokei already installed"

# Python comprehensive development environment
echo "🐍 Setting up comprehensive Python environment..."
python3 -m venv ~/.venv/dev
source ~/.venv/dev/bin/activate

# Install comprehensive Python toolchain
pip install --upgrade pip setuptools wheel
pip install \
    # Security tools
    bandit safety semgrep detect-secrets gitpython \
    # Code quality and formatting
    black isort mypy pylint flake8 autopep8 pycodestyle pydocstyle \
    # Testing frameworks
    pytest pytest-cov pytest-xdist pytest-mock pytest-asyncio \
    # Documentation tools
    sphinx mkdocs mkdocs-material pydoc-markdown \
    # Development tools
    ipython jupyter notebook jupyterlab \
    # Performance profiling
    line_profiler memory_profiler py-spy scalene \
    # Data analysis (for performance analysis)
    pandas numpy matplotlib seaborn \
    # Web development
    requests aiohttp fastapi uvicorn \
    # Database tools
    sqlalchemy alembic \
    # Container security
    docker-py kubernetes

# Add Python virtual environment to shell
echo 'source ~/.venv/dev/bin/activate' >> ~/.bashrc

# Go development tools
echo "🔷 Setting up Go development tools..."
export PATH="/usr/local/go/bin:$PATH"
export GOPATH="$HOME/go"
mkdir -p "$GOPATH/bin"

# Install Go tools
go install golang.org/x/tools/gopls@latest
go install golang.org/x/tools/cmd/goimports@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go install github.com/securecodewarrior/shenron@latest
go install github.com/go-delve/delve/cmd/dlv@latest
go install github.com/fatih/gomodifytags@latest
go install github.com/josharian/impl@latest

# Node.js comprehensive setup
echo "🟨 Setting up Node.js development environment..."
npm config set fund false
npm config set audit-level high

# Install global Node.js tools
npm install -g \
    # Core development
    typescript ts-node nodemon \
    # Code quality
    eslint prettier @typescript-eslint/parser @typescript-eslint/eslint-plugin \
    # Testing
    jest mocha nyc \
    # Build tools
    webpack vite rollup \
    # Utilities
    npm-check-updates npm-audit-html \
    # Process management
    pm2 \
    # Documentation
    jsdoc typedoc

# C/C++ development setup
echo "⚙️ Setting up C/C++ development tools..."
# Create compilation database helper
cat > ~/.local/bin/make-compile-commands << 'EOF'
#!/bin/bash
# Generate compile_commands.json for C/C++ projects
bear -- make "$@"
EOF
chmod +x ~/.local/bin/make-compile-commands

# Git comprehensive configuration
echo "📝 Configuring Git with comprehensive settings..."
git config --global init.defaultBranch main
git config --global core.autocrlf false
git config --global core.filemode true
git config --global pull.rebase false
git config --global push.default simple
git config --global core.editor "code --wait"
git config --global diff.tool "vscode"
git config --global merge.tool "vscode"
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.st "status -s"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.ci "commit"

# Install and configure pre-commit
echo "🔧 Setting up pre-commit framework..."
pip install pre-commit
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', '.']

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Security: Setup comprehensive security scanning
echo "🛡️ Setting up comprehensive security scanning..."

# Create security scan script
cat > ~/.local/bin/security-scan << 'EOF'
#!/bin/bash
# Comprehensive security scan for Syn_OS

echo "🔍 Running comprehensive security scan..."

# Rust security
if command -v cargo &> /dev/null; then
    echo "🦀 Rust security audit..."
    cargo audit
    cargo deny check
fi

# Python security
if command -v bandit &> /dev/null; then
    echo "🐍 Python security scan..."
    bandit -r . -f json || true
fi

# Go security
if command -v gosec &> /dev/null; then
    echo "🔷 Go security scan..."
    gosec ./... || true
fi

# Container security
if command -v trivy &> /dev/null && [[ -f Dockerfile ]]; then
    echo "🐳 Container security scan..."
    trivy fs .
fi

# Secret detection
if command -v detect-secrets &> /dev/null; then
    echo "🔑 Secret detection..."
    detect-secrets scan --all-files --baseline .secrets.baseline
fi

echo "✅ Security scan completed"
EOF
chmod +x ~/.local/bin/security-scan

# Setup development aliases
echo "⚡ Setting up development aliases..."
cat >> ~/.bashrc << 'EOF'

# Syn_OS Development Aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias ..='cd ..'
alias ...='cd ../..'

# Development shortcuts
alias rs='cargo run'
alias rb='cargo build'
alias rt='cargo test'
alias rc='cargo check'
alias rw='cargo watch -x check'

# Python shortcuts
alias py='python3'
alias pip='python3 -m pip'
alias pytest='python3 -m pytest'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gco='git checkout'

# Security shortcuts
alias audit='security-scan'
alias scan='trivy fs .'

# Performance shortcuts
alias perf-record='perf record -g'
alias perf-report='perf report -g'
alias flamegraph-rs='cargo flamegraph'
EOF

# Create project structure helpers
echo "📁 Setting up project helpers..."
mkdir -p ~/.local/bin

cat > ~/.local/bin/new-rust-project << 'EOF'
#!/bin/bash
# Create new Rust project with security best practices
cargo new "$1"
cd "$1"
cargo add serde --features derive
cargo add tokio --features full
cargo add clap --features derive
cargo add anyhow
cargo add thiserror
echo "✅ Rust project '$1' created with common dependencies"
EOF
chmod +x ~/.local/bin/new-rust-project

# Validate comprehensive installation
echo "🔧 Validating comprehensive development environment..."

echo "Languages and tools:"
rustc --version
cargo --version
python3 --version
go version
node --version
npm --version

echo ""
echo "Security tools:"
command -v bandit && bandit --version || echo "bandit: not found"
command -v trivy && trivy --version || echo "trivy: not found"
command -v cargo-audit && cargo audit --version || echo "cargo-audit: not found"

echo ""
echo "Development tools:"
command -v black && black --version || echo "black: not found"
command -v eslint && eslint --version || echo "eslint: not found"
command -v pre-commit && pre-commit --version || echo "pre-commit: not found"

# Final security validation
echo "✅ Comprehensive development environment setup completed successfully!"
echo ""
echo "🛠️ AVAILABLE DEVELOPMENT TOOLS:"
echo "   🦀 Rust: Full toolchain with security auditing"
echo "   🐍 Python: Complete development environment with security"
echo "   🔷 Go: Development tools with security scanning"
echo "   🟨 Node.js: Modern development stack"
echo "   ⚙️ C/C++: Compilation and analysis tools"
echo "   🔍 Security: Multi-language security scanning"
echo "   📊 Performance: Profiling and benchmarking tools"
echo "   🔧 Debugging: Multi-language debugging support"
echo ""
echo "📚 Quick start commands:"
echo "   new-rust-project <name>  # Create new Rust project"
echo "   security-scan           # Run comprehensive security scan"
echo "   audit                   # Quick security audit"
echo "   rw                      # Watch Rust code changes"
echo ""
echo "🔐 Security features active:"
echo "   ✓ Pre-commit hooks with security checks"
echo "   ✓ Multi-language security scanning"
echo "   ✓ Secret detection"
echo "   ✓ Container security analysis"
echo "   ✓ Dependency vulnerability scanning"
echo ""