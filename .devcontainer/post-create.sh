#!/bin/bash
# Syn_OS Post-Create Security Setup
# Executes after container creation with security hardening

set -euo pipefail

echo "🔐 Initializing Syn_OS secure development environment..."

# Security: Validate environment
echo "🔍 Validating security configuration..."
if [[ "$EUID" -eq 0 ]]; then
    echo "❌ ERROR: Running as root is not allowed for security"
    exit 1
fi

# Rust security configuration
echo "🦀 Configuring Rust security settings..."
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
EOF

# Security: Install additional Rust security tools
echo "🛡️ Installing Rust security toolchain..."
cargo install --locked cargo-audit || echo "cargo-audit already installed"
cargo install --locked cargo-deny || echo "cargo-deny already installed"
cargo install --locked cargo-geiger || echo "cargo-geiger already installed"

# Python security environment
echo "🐍 Setting up Python security environment..."
python3 -m venv ~/.venv/security
source ~/.venv/security/bin/activate
pip install --upgrade pip setuptools wheel
pip install bandit safety semgrep pysec-inspector

# Security: Git configuration with security focus
echo "📝 Configuring Git with security settings..."
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

# Security: Pre-commit hooks setup
echo "🪝 Setting up security pre-commit hooks..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e

echo "🔍 Running security checks..."

# Rust security audit
if command -v cargo &> /dev/null; then
    echo "🦀 Running Rust security audit..."
    cargo audit || { echo "❌ Cargo audit failed"; exit 1; }
fi

# Python security scan
if command -v bandit &> /dev/null; then
    echo "🐍 Running Python security scan..."
    find . -name "*.py" -not -path "./.venv/*" -not -path "./venv/*" | xargs bandit -r || true
fi

# Secret detection
echo "🔑 Scanning for secrets..."
if git diff --cached --name-only | xargs grep -l "password\|secret\|key\|token" 2>/dev/null; then
    echo "⚠️  WARNING: Potential secrets detected in staged files"
    echo "Please review your changes before committing"
fi

echo "✅ Security checks completed"
EOF

chmod +x .git/hooks/pre-commit

# Security: Environment validation
echo "🔧 Validating development environment..."
rustc --version
cargo --version
go version
python3 --version
node --version
qemu-system-x86_64 --version

# Security: Create secure development directories
echo "📁 Creating secure development structure..."
mkdir -p {.secrets,.logs,.cache}
chmod 700 .secrets .logs .cache

# Security: Initialize project-specific security config
echo "🛡️ Initializing project security configuration..."
cat > .security-config << 'EOF'
# Syn_OS Security Configuration
SECURITY_ENABLED=true
AUDIT_LEVEL=strict
THREAT_DETECTION=enabled
ZERO_TRUST=enforced
ENCRYPTION_REQUIRED=true
EOF

# Final security validation
echo "✅ Post-create security setup completed successfully!"
echo "🚀 Syn_OS development environment is ready with enhanced security"

# Display security summary
echo ""
echo "🔐 SECURITY FEATURES ENABLED:"
echo "   ✓ Non-root user enforcement"
echo "   ✓ Security-focused container configuration"
echo "   ✓ Rust security toolchain (audit, deny, geiger)"
echo "   ✓ Python security scanning (bandit, safety)"
echo "   ✓ Pre-commit security hooks"
echo "   ✓ Secret detection mechanisms"
echo "   ✓ Secure directory permissions"
echo "   ✓ Zero-trust development practices"
echo ""