#!/bin/bash
# ============================================================================
# SynOS v1.0 Linux ISO Build Configuration
# ============================================================================
# Optimized for fast, reliable Linux distribution builds
# Date: September 24, 2025
# ============================================================================

echo "🚀 SYNOS V1.0 LINUX ISO BUILD OPTIMIZATION"
echo "=========================================="
echo ""

# Build Environment Configuration
export SYNOS_BUILD_MODE="iso"
export RUST_BACKTRACE=1
export CARGO_TARGET_DIR="$(pwd)/target"

# Memory Optimization
export CARGO_BUILD_JOBS=2  # Limit parallel jobs to conserve memory
export RUSTFLAGS="-C link-arg=-Wl,--compress-debug-sections=zlib"

# Feature Selection for Linux ISO
export SYNOS_FEATURES="lightweight,linux-integration"

echo "✅ Environment configured for v1.0 ISO build"
echo "Features: $SYNOS_FEATURES"
echo "Build jobs limited to: $CARGO_BUILD_JOBS"
echo ""
