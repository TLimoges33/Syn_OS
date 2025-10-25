#!/bin/bash
#
# Fix Cargo Warnings Script
# Automatically fixes unused imports, dead code, and other warnings
#

set -e

PROJECT_ROOT="/home/diablorain/Syn_OS"
cd "$PROJECT_ROOT"

echo "════════════════════════════════════════════════════════════════"
echo "  CARGO FIX - Automatic Warning Resolution"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Add cargo to PATH
export PATH="/home/diablorain/.cargo/bin:$PATH"

echo "📋 Running cargo fix on workspace (excluding kernel)..."
echo ""

# Run cargo fix on all projects except kernel
cargo fix --workspace --allow-dirty --allow-staged --exclude syn-kernel || {
    echo "⚠️  Some fixes may have failed, but continuing..."
}

echo ""
echo "✅ Cargo fix completed!"
echo ""
echo "📊 Checking remaining warnings..."
cargo check --workspace --exclude syn-kernel 2>&1 | grep -E "warning:|error:" | head -20 || {
    echo "✅ No warnings found!"
}

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  DONE - You can now run the build script"
echo "════════════════════════════════════════════════════════════════"
