#!/bin/bash
# Run a full security audit in Codespace
set -euo pipefail

echo "[Codespace Security Audit] Running security-scan..."
security-scan
echo "[Codespace Security Audit] Running bandit on Python..."
bandit -r . || true
echo "[Codespace Security Audit] Running cargo-audit on Rust..."
cargo audit || true
echo "[Codespace Security Audit] Running npm audit (if package.json exists)..."
if [ -f package.json ]; then npm audit || true; fi
echo "[Codespace Security Audit] Complete."
