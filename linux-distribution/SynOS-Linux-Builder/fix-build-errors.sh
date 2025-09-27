#!/bin/bash

# SynOS Build Error Fix Script
# Fixes common build issues and directory problems

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"

echo "🔧 Fixing common build issues..."

# Fix directory permissions and ownership
if [[ -d "$BUILD_DIR" ]]; then
    echo "📁 Fixing directory permissions..."
    sudo chown -R $USER:$USER "$BUILD_DIR"
    chmod -R 755 "$BUILD_DIR"
fi

# Ensure all critical directories exist
echo "📁 Creating missing directories..."
mkdir -p "$BUILD_DIR/config/includes.chroot/etc"
mkdir -p "$BUILD_DIR/config/includes.chroot/opt/synos"
mkdir -p "$BUILD_DIR/config/includes.chroot/usr/bin"
mkdir -p "$BUILD_DIR/config/includes.chroot/usr/lib/synos"
mkdir -p "$BUILD_DIR/config/includes.chroot/home/user"
mkdir -p "$BUILD_DIR/config/hooks/live"
mkdir -p "$BUILD_DIR/config/package-lists"
mkdir -p "$BUILD_DIR/logs"

# Fix live-build specific issues
echo "🛠️ Fixing live-build configuration..."
cd "$BUILD_DIR"

# Clean any partial builds
if [[ -f ".build" ]]; then
    echo "🧹 Cleaning partial build..."
    sudo lb clean --purge || true
fi

# Fix hostname file
if [[ ! -f "config/includes.chroot/etc/hostname" ]]; then
    echo "🏷️ Creating hostname file..."
    echo "synos-linux" > config/includes.chroot/etc/hostname
fi

# Fix hosts file
if [[ ! -f "config/includes.chroot/etc/hosts" ]]; then
    echo "🌐 Creating hosts file..."
    cat > config/includes.chroot/etc/hosts << 'EOF'
127.0.0.1   localhost
127.0.1.1   synos-linux
::1         localhost ip6-localhost ip6-loopback
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
EOF
fi

# Ensure package lists exist
touch config/package-lists/synos-base.list.chroot
touch config/package-lists/synos-security.list.chroot

echo "✅ Build environment fixed!"
echo "Ready to run: sudo ./build-redteam-iso.sh"