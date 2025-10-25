#!/bin/bash

# SynOS Directory Structure Initialization
# Ensures all required directories exist before build

set -euo pipefail

BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/build"

echo "📁 Creating required directory structure..."

# Create all necessary directories
mkdir -p "$BUILD_DIR"/{config,logs,kernel-modules,stages,releases}
mkdir -p "$BUILD_DIR/config"/{includes.chroot,hooks,package-lists,archives}
mkdir -p "$BUILD_DIR/config/includes.chroot"/{etc,opt,usr,home,var}
mkdir -p "$BUILD_DIR/config/includes.chroot/opt"/{synos,packages}
mkdir -p "$BUILD_DIR/config/includes.chroot/opt/synos"/{bin,lib,share,data,src,consciousness,education,themes,tools}
mkdir -p "$BUILD_DIR/config/includes.chroot/usr"/{bin,lib,share,local}
mkdir -p "$BUILD_DIR/config/includes.chroot/usr/lib"/{synos,systemd}
mkdir -p "$BUILD_DIR/config/includes.chroot/usr/share"/{synos,applications,pixmaps}
mkdir -p "$BUILD_DIR/config/includes.chroot/etc"/{synos,systemd,init.d}
mkdir -p "$BUILD_DIR/config/includes.chroot/etc/systemd"/{system,user}
mkdir -p "$BUILD_DIR/config/includes.chroot/home"/{user,synos}
mkdir -p "$BUILD_DIR/config/includes.chroot/var"/{log,lib}
mkdir -p "$BUILD_DIR/config/includes.chroot/var/log"/synos
mkdir -p "$BUILD_DIR/config/includes.chroot/var/lib"/synos
mkdir -p "$BUILD_DIR/config/hooks"/{live,binary,source}
mkdir -p "$BUILD_DIR/config/package-lists"

echo "✅ Directory structure created successfully"

# Set proper permissions
chmod -R 755 "$BUILD_DIR/config/includes.chroot"
chmod -R 755 "$BUILD_DIR/config/hooks"

echo "✅ Permissions set correctly"
echo "📁 Build environment ready!"