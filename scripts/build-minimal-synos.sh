#!/bin/bash
# Minimal SynOS Linux Build - Focus on working ISO first

set -e

echo "🚀 Building Minimal SynOS Linux Distribution..."

# Configuration
ISO_NAME="synos-linux-minimal-$(date +%Y%m%d-%H%M%S)-amd64.iso"
BUILD_DIR="/home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder"

cd "$BUILD_DIR"

# Clean previous build
echo "🧹 Cleaning previous builds..."
sudo lb clean --purge

# Simple configuration without custom packages for now
echo "⚙️ Configuring minimal live-build..."
sudo lb config \
    --binary-images iso-hybrid \
    --mode debian \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --linux-flavours amd64 \
    --bootappend-live "boot=live components quiet splash" \
    --iso-application "SynOS Linux" \
    --iso-publisher "SynOS Development Team" \
    --iso-volume "SynOS Linux 1.0.0" \
    --memtest memtest86+

# Build the ISO
echo "🏗️ Building SynOS ISO..."
sudo lb build

# Check for ISO
if [ -f live-image-amd64.hybrid.iso ]; then
    mv live-image-amd64.hybrid.iso "$ISO_NAME"
    sha256sum "$ISO_NAME" > "${ISO_NAME}.sha256"

    echo "🎉 SUCCESS! SynOS Linux ISO created!"
    echo "📁 File: $ISO_NAME"
    echo "📏 Size: $(du -h "$ISO_NAME" | cut -f1)"
    echo "🔐 SHA256: $(cat "${ISO_NAME}.sha256" | cut -d' ' -f1)"

    # File validation
    file "$ISO_NAME"

else
    echo "❌ ERROR: ISO file not found!"
    echo "Checking for alternative ISO names..."
    find . -maxdepth 1 -name "*.iso" -ls
fi

echo "✅ Build process completed!"