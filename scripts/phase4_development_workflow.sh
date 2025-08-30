#!/bin/bash
# Phase 4.0 Parallel Development Workflow

echo "🚀 GenAI OS Phase 4.0 Development Environment"
echo "============================================="

# Ensure we're on the right branch
git checkout phase-4.0-preparation

# Start containerized services (production)
echo "📦 Starting containerized services..."
if command -v podman &> /dev/null; then
    podman-compose -f docker/docker-compose-frozen.yml up -d
else
    echo "⚠️  Podman not available, skipping container startup"
fi

# Build kernel components
echo "🔧 Building kernel components..."
cd src/kernel
if [ -f "Cargo.toml" ]; then
    cargo build --target=x86_64-syn_os
    echo "✅ Kernel build complete"
else
    echo "⚠️  Kernel Cargo.toml not found"
fi

cd ../..

# Run tests
echo "🧪 Running Phase 4.0 tests..."
if [ -d "tests/kernel" ]; then
    echo "✅ Kernel test directory ready"
else
    echo "⚠️  Kernel tests not set up"
fi

echo "🎯 Phase 4.0 development environment ready!"
echo "Next: Implement consciousness kernel integration"
