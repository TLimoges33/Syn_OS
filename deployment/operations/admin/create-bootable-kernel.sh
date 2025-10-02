#!/bin/bash

# Script to create a bootable kernel image from our ELF kernel
# This bridges the gap between our Rust bootloader-based kernel and traditional bootloaders

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KERNEL_PATH="$PROJECT_ROOT/target/x86_64-unknown-none/debug/kernel"
OUTPUT_PATH="$PROJECT_ROOT/target/x86_64-unknown-none/debug/synos-kernel.bin"

log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo "✅ $1"
}

log_error() {
    echo "❌ $1" >&2
}

if [[ ! -f "$KERNEL_PATH" ]]; then
    log_error "Kernel not found at $KERNEL_PATH"
    log_info "Run: cargo build --package syn-kernel-v2 --target x86_64-unknown-none"
    exit 1
fi

log_info "Creating bootable kernel image..."

# For now, let's create a simple kernel wrapper that can be loaded by ISOLINUX
# This is a temporary solution while we debug the bootloader chain

# Option 1: Direct ELF kernel (may work with some bootloaders)
cp "$KERNEL_PATH" "$OUTPUT_PATH"

log_success "Bootable kernel created at $OUTPUT_PATH"
log_info "Size: $(stat -c%s "$OUTPUT_PATH" | numfmt --to=iec-i)"

# Verify the kernel format
file "$OUTPUT_PATH"

log_info "To test: Use this kernel in place of vmlinuz in ISO build"
