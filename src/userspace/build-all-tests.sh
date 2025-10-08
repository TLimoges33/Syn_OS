#!/bin/bash
# Build all SynOS userspace test programs
# These are freestanding binaries for SynOS kernel execution

set -e

echo "🔧 Building SynOS Userspace Integration Tests"
echo "=============================================="
echo ""

# Ensure we have the target installed
echo "📦 Ensuring x86_64-unknown-none target is available..."
rustup target add x86_64-unknown-none

echo ""
echo "🏗️  Building libtsynos userspace library..."
cargo build --package libtsynos
echo "✅ Library built successfully"

echo ""
echo "🧪 Building test binaries..."
echo ""

tests=(
    "test_core_syscalls"
    "test_network_syscalls"
    "test_security_syscalls"
    "test_ai_syscalls"
    "test_advanced_syscalls"
    "test_integration_full"
)

for test in "${tests[@]}"; do
    echo "   Building ${test}..."
    cargo build --package synos-userspace-tests \
        --bin "${test}" \
        --target x86_64-unknown-none \
        --quiet
    echo "   ✅ ${test} built"
done

echo ""
echo "=============================================="
echo "✨ Build Complete!"
echo ""
echo "📁 Test binaries location:"
echo "   target/x86_64-unknown-none/debug/"
echo ""
echo "📊 Built binaries:"
ls -lh ../../target/x86_64-unknown-none/debug/test_* 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
echo ""
echo "🚀 Next steps:"
echo "   - Load binaries into SynOS kernel userspace"
echo "   - Execute tests to validate syscall implementation"
echo "   - Review integration test results"
echo ""
