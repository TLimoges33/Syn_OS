#!/bin/bash
# SynOS Phase 2 Week 4 Build Script

set -e

echo "🚀 Building SynOS Phase 2 Week 4 Components..."

# Build custom bootloader
echo "Building SynBoot bootloader..."
cd core/bootloader
make clean
make

# Build consciousness scheduler kernel module
echo "Building consciousness scheduler..."
cd ../kernel
make -C /lib/modules/$(uname -r)/build M=$PWD modules

# Build neural memory manager
echo "Building neural memory manager..."
cd memory
make -C /lib/modules/$(uname -r)/build M=$PWD modules

echo "✅ Phase 2 Week 4 build complete!"
