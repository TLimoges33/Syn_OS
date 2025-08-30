#!/bin/bash
# Fix Cargo file locking and permission issues in codespace

set -euo pipefail

echo "🔧 Fixing Cargo and development environment issues..."

# Fix Cargo registry and cache permissions
echo "📦 Fixing Cargo permissions..."
if [[ -d ~/.cargo ]]; then
    chmod -R 755 ~/.cargo || true
    rm -rf ~/.cargo/registry/cache/* 2>/dev/null || true
    rm -rf ~/.cargo/registry/index/* 2>/dev/null || true
fi

# Create clean cargo cache
mkdir -p ~/.cargo/registry/{cache,index,src}
mkdir -p ~/.cargo/git/{cache,checkouts,db}

# Set proper environment for container
export CARGO_HOME="$HOME/.cargo"
export CARGO_TARGET_DIR="$HOME/.cargo/target"
export CARGO_NET_RETRY=10
export CARGO_NET_GIT_FETCH_WITH_CLI=true

# Create optimized Cargo config
mkdir -p ~/.cargo
cat > ~/.cargo/config.toml << 'EOF'
[build]
jobs = 4
target-dir = "/tmp/cargo-target"

[cargo-new]
vcs = "none"

[net]
retry = 10
git-fetch-with-cli = true
offline = false

[registry]
default = "crates-io"

[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "/opt/rust/cargo/registry/src"

[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[alias]
ktest = "test --target x86_64-unknown-none"
krun = "run --target x86_64-unknown-none" 
kbuild = "build --target x86_64-unknown-none"
audit-fix = "audit fix"
security-check = "audit"
quick-check = "check --bins --lib"
EOF

# Fix file system sync issues
sync

echo "✅ Cargo environment fixed"
echo "🔧 Optimized for codespace development"