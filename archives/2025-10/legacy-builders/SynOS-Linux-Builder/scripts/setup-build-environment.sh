#!/bin/bash

# SynOS Linux Distribution Build Environment Setup
# This script installs all required tools for building SynOS Linux

set -euo pipefail

echo "🚀 Setting up SynOS Linux build environment..."

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Install live-build and related tools
echo "🛠️ Installing live-build tools..."
sudo apt install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    dosfstools \
    e2fsprogs \
    parted \
    gdisk

# Install package building tools
echo "📦 Installing package building tools..."
sudo apt install -y \
    devscripts \
    debhelper \
    dh-make \
    reprepro \
    dpkg-dev \
    fakeroot \
    lintian

# Install development tools
echo "🔧 Installing development tools..."
sudo apt install -y \
    git \
    build-essential \
    python3-dev \
    python3-pip \
    nodejs \
    npm \
    curl \
    wget

# Install additional utilities
echo "🔧 Installing additional utilities..."
sudo apt install -y \
    rsync \
    tar \
    gzip \
    unzip \
    p7zip-full \
    tree \
    jq

# Verify installations
echo "✅ Verifying installations..."
echo "Live-build version: $(lb --version 2>/dev/null || echo 'Not found')"
echo "Debootstrap version: $(debootstrap --version 2>/dev/null || echo 'Not found')"
echo "Squashfs-tools: $(mksquashfs -version 2>/dev/null | head -1 || echo 'Not found')"

echo "🎉 Build environment setup complete!"
echo "📍 Next: Run './build-synos-base.sh' to create base configuration"