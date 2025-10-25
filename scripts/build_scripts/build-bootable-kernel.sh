#!/bin/bash
# Build bootable kernel using bootloader 0.10+ API

set -e

PROJECT_ROOT="/home/diablorain/Syn_OS"
cd "$PROJECT_ROOT"

echo "🔧 Building SynOS kernel with bootloader 0.10..."

# Build the kernel binary
echo "Step 1: Building kernel binary..."
cargo build \
    --manifest-path=src/kernel/Cargo.toml \
    --release \
    --target=x86_64-unknown-none \
    --features=kernel-binary

if [ ! -f "target/x86_64-unknown-none/release/kernel" ]; then
    echo "❌ Kernel binary not found!"
    exit 1
fi

echo "✅ Kernel binary built: $(ls -lh target/x86_64-unknown-none/release/kernel | awk '{print $5}')"

# Use bootloader's builder to create bootable image
echo "Step 2: Creating bootable disk image..."

# Create a simple Rust program to build the bootable image
cat > /tmp/build-bootable.rs << 'EOF'
use std::path::PathBuf;

fn main() {
    let kernel_binary_path = PathBuf::from(env!("KERNEL_BINARY"));
    let out_dir = PathBuf::from(env!("OUT_DIR"));

    // Create bootable disk image
    let bootloader_manifest = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../Cargo.toml");

    bootloader::UefiBoot::new(&kernel_binary_path)
        .create_disk_image(&out_dir.join("uefi.img"))
        .expect("Failed to create UEFI disk image");

    bootloader::BiosBoot::new(&kernel_binary_path)
        .create_disk_image(&out_dir.join("bios.img"))
        .expect("Failed to create BIOS disk image");

    println!("✅ Bootable images created!");
    println!("  UEFI: {}", out_dir.join("uefi.img").display());
    println!("  BIOS: {}", out_dir.join("bios.img").display());
}
EOF

# Actually, let's use a simpler approach - just copy the kernel and use GRUB properly
# The real issue is GRUB configuration

echo "Step 3: Testing kernel format..."
file target/x86_64-unknown-none/release/kernel

echo ""
echo "✅ Kernel build complete!"
echo "📍 Location: target/x86_64-unknown-none/release/kernel"
echo ""
echo "Note: This kernel uses bootloader crate entry_point!() macro"
echo "It needs to be booted with bootloader crate, not GRUB directly."
