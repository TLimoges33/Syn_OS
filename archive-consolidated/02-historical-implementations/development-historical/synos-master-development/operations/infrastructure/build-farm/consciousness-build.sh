#!/bin/bash
# SynOS Consciousness-Integrated Build System

set -euo pipefail

CONSCIOUSNESS_TARGET="0.942"
PERFORMANCE_TARGET="3.0"

echo "🧠 Starting consciousness-integrated build..."

# Build consciousness system first
echo "🔧 Building Neural Darwinism consciousness..."
cd core/consciousness
python -m pip install -e .
if ! python -c "from core.agent_ecosystem.neural_darwinism import NeuralDarwinismEngine; print('✅ Consciousness system ready')"; then
    echo "❌ Consciousness system build failed"
    exit 1
fi

# Build kernel with consciousness integration
echo "⚡ Building consciousness-integrated kernel..."
cd ../kernel
cargo build --release --features consciousness-integration
if ! cargo test --release --features consciousness-integration; then
    echo "❌ Kernel build failed"
    exit 1
fi

# Build security tools with consciousness enhancement
echo "🛡️ Building enhanced security tools..."
cd ../security-tools
./build-enhanced-tools.sh --consciousness-mode=production --performance-target=$PERFORMANCE_TARGET

# Build educational platform
echo "🎓 Building SCADI educational platform..."
cd ../educational-platform
python -m pip install -e .
python -m pytest tests/ --educational-validation=production

# Validate overall integration
echo "🔍 Validating consciousness integration..."
if ! ./validate-consciousness-fitness.sh --target=$CONSCIOUSNESS_TARGET; then
    echo "❌ Consciousness fitness validation failed"
    exit 1
fi

echo "✅ Consciousness-integrated build complete!"
