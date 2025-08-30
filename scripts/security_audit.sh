#!/bin/bash
# Run all security audits for SynapticOS
set -e

# Python: safety
if [ -f requirements.txt ]; then
  echo "[Python] Running safety..."
  pip install --quiet safety
  safety check || true
fi

# Python: bandit
if [ -d src/ ]; then
  echo "[Python] Running bandit..."
  pip install --quiet bandit
  bandit -r src/ || true
fi

# Rust: cargo-audit
if [ -f Cargo.toml ] || [ -f src/Cargo.toml ]; then
  echo "[Rust] Running cargo-audit..."
  cargo install --quiet cargo-audit || true
  (cd src && cargo audit) || true
fi

# Node: npm audit
if [ -f package.json ]; then
  echo "[Node] Running npm audit..."
  npm install --quiet
  npm audit || true
fi

# Semgrep (universal)
echo "[Universal] Running semgrep..."
pip install --quiet semgrep
semgrep scan --config=auto || true

# Trivy (container/image scan)
if command -v trivy >/dev/null 2>&1; then
  echo "[Container] Running trivy filesystem scan..."
  trivy fs . || true
fi
