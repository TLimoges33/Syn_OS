#!/bin/bash

# Install live-build for SynOS Linux Distribution Builder
# Run this script with: ./install-livebuild.sh

set -e

echo "🚀 Installing live-build for SynOS Linux Distribution Builder..."

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Install live-build
echo "🛠️ Installing live-build..."
sudo apt install -y live-build

# Verify installation
echo "✅ Verifying installation..."
if command -v lb &>/dev/null; then
    echo "Live-build version: $(lb --version)"
    echo ""
    echo "🎉 Live-build successfully installed!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Run: ./verify-setup.sh"
    echo "2. Run: ./build-synos-linux.sh"
    echo "3. Select option 1 (Quick Test Build) for first test"
else
    echo "❌ Installation failed - lb command not found"
    exit 1
fi