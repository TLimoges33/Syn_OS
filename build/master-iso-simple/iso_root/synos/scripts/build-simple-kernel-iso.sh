#!/bin/bash

# Syn_OS Simplified Kernel ISO Builder
# Uses bootloader crate for proper kernel handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build/simple-kernel-iso"
KERNEL_DIR="${PROJECT_ROOT}/src/kernel"
ISO_ROOT="${BUILD_DIR}/iso_root"
BUILD_DATE=$(date +%Y%m%d-%H%M%S)
ISO_FILENAME="synos-kernel-${BUILD_DATE}.iso"

echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║              SYN_OS SIMPLIFIED KERNEL ISO                    ║${NC}"
echo -e "${PURPLE}║          AI-Powered Cybersecurity Education OS              ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}║  🧠 Consciousness Integration  🔒 Neural Security           ║${NC}"
echo -e "${PURPLE}║  🎓 Educational Framework     ⚡ High Performance           ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

echo -e "${BLUE}[INFO]${NC} Building simplified Syn_OS kernel ISO..."
echo -e "${BLUE}[INFO]${NC} Target: ${ISO_FILENAME}"
echo -e "${BLUE}[INFO]${NC} Build directory: ${BUILD_DIR}"

# Clean and create build directories
echo -e "${CYAN}[1/6]${NC} Setting up build environment"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR" "$ISO_ROOT/boot/grub"

# Build kernel using bootloader crate
echo -e "${CYAN}[2/6]${NC} Building Rust kernel with bootloader"
cd "$KERNEL_DIR"

# Install bootimage if not present
if ! command -v cargo-bootimage &> /dev/null; then
    echo -e "${YELLOW}Installing bootimage...${NC}"
    cargo install bootimage
fi

# Add rust-src component
rustup component add rust-src --toolchain nightly 2>/dev/null || true

# Build bootable kernel image
echo -e "${BLUE}Building bootable kernel image...${NC}"
cargo bootimage --release --target x86_64-unknown-none

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Kernel build failed!"
    exit 1
fi

# Find the bootable kernel image
KERNEL_IMAGE=$(find "$PROJECT_ROOT/target" -name "*.bin" -path "*/x86_64-unknown-none/release/*" | head -1)

if [ -z "$KERNEL_IMAGE" ]; then
    echo -e "${RED}[ERROR]${NC} Could not find bootable kernel image"
    find "$PROJECT_ROOT/target" -name "*.bin" -type f | head -5
    exit 1
fi

echo -e "${GREEN}✅ Found bootable kernel: $KERNEL_IMAGE${NC}"

# Copy kernel to ISO
echo -e "${CYAN}[3/6]${NC} Creating ISO structure"
cp "$KERNEL_IMAGE" "$ISO_ROOT/boot/kernel.bin"

# Create GRUB configuration
echo -e "${CYAN}[4/6]${NC} Creating GRUB configuration"
cat > "$ISO_ROOT/boot/grub/grub.cfg" << 'EOF'
# Syn_OS GRUB Configuration
# AI-Consciousness Integrated Kernel Boot Menu

set timeout=10
set default=0

# Set theme colors
set color_normal=light-cyan/black
set color_highlight=white/blue

menuentry "🧠 Syn_OS - AI Consciousness Kernel" {
    echo "🧠 Loading Syn_OS AI Consciousness Kernel..."
    echo "🔒 Initializing Neural Security Framework..."
    echo "🎓 Starting Educational Cybersecurity Platform..."
    multiboot2 /boot/kernel.bin
    boot
}

menuentry "🧠 Syn_OS - Debug Mode" {
    echo "🔧 Loading Syn_OS in Debug Mode..."
    echo "🧠 Consciousness Engine: Debug Level Logging"
    echo "🔍 Enhanced Diagnostic Information"
    multiboot2 /boot/kernel.bin debug
    boot
}

menuentry "🧠 Syn_OS - Safe Mode" {
    echo "🛡️  Loading Syn_OS in Safe Mode..."
    echo "🧠 Consciousness Engine: Minimal Configuration"
    echo "🔒 Security Framework: Basic Protection"
    multiboot2 /boot/kernel.bin safe
    boot
}

menuentry "🔄 Reboot" {
    echo "🔄 Rebooting system..."
    reboot
}

menuentry "⚡ Shutdown" {
    echo "⚡ Shutting down system..."
    halt
}
EOF

# Create consciousness integration files
echo -e "${CYAN}[5/6]${NC} Adding consciousness integration"
mkdir -p "$ISO_ROOT/opt/synos"
cp -r "$PROJECT_ROOT/src/consciousness_v2" "$ISO_ROOT/opt/synos/" 2>/dev/null || true

# Create startup script
cat > "$ISO_ROOT/opt/synos/consciousness-info.txt" << 'EOF'
Syn_OS Consciousness Engine Integration
======================================

🧠 AI Consciousness Features:
- Neural Darwinism Processing
- Real-time Threat Analysis
- Educational Content Adaptation
- Personalized Learning Paths
- Advanced Security Monitoring

🔒 Security Framework:
- Zero-Trust Architecture
- Behavioral Anomaly Detection
- Automated Incident Response
- Threat Intelligence Integration
- Educational Security Scenarios

🎓 Educational Platform:
- Interactive Cybersecurity Labs
- Hands-on Penetration Testing
- Real-world Attack Simulations
- Skill Assessment and Tracking
- Consciousness-Enhanced Learning

This kernel demonstrates the integration of AI consciousness
with operating system security and educational frameworks.
EOF

# Create bootable ISO
echo -e "${CYAN}[6/6]${NC} Creating bootable ISO"
cd "$BUILD_DIR"

grub-mkrescue -o "$ISO_FILENAME" "$ISO_ROOT/" \
    --compress=xz \
    --verbose

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} ISO creation failed!"
    exit 1
fi

# Calculate checksums
sha256sum "$ISO_FILENAME" > "${ISO_FILENAME}.sha256"
md5sum "$ISO_FILENAME" > "${ISO_FILENAME}.md5"

# Get ISO size
ISO_SIZE=$(du -h "$ISO_FILENAME" | cut -f1)

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                     BUILD SUCCESSFUL! 🎉                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ Syn_OS Kernel ISO created successfully!${NC}"
echo -e "${BLUE}📀 ISO File:${NC} ${BUILD_DIR}/${ISO_FILENAME}"
echo -e "${BLUE}📏 ISO Size:${NC} ${ISO_SIZE}"
echo -e "${BLUE}🔐 SHA256:${NC} $(cat "${ISO_FILENAME}.sha256" | cut -d' ' -f1)"

echo ""
echo -e "${CYAN}🚀 Next Steps:${NC}"
echo "1. Test ISO: qemu-system-x86_64 -cdrom ${BUILD_DIR}/${ISO_FILENAME} -m 512M"
echo "2. Write to USB: dd if=${BUILD_DIR}/${ISO_FILENAME} of=/dev/sdX bs=4M status=progress"
echo "3. Boot and explore AI consciousness kernel features"
echo ""

echo -e "${YELLOW}🧠 Consciousness Features:${NC}"
echo "- AI-integrated kernel with neural security"
echo "- Educational cybersecurity platform"
echo "- Real-time threat detection and response"
echo "- Personalized learning adaptation"
echo ""

# Offer to test immediately
echo -e "${YELLOW}Would you like to test the ISO in QEMU now? (y/N)${NC}"
read -r -n 1 response
echo ""
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}Starting QEMU test...${NC}"
    qemu-system-x86_64 \
        -cdrom "$ISO_FILENAME" \
        -m 512M \
        -display curses \
        -serial stdio \
        -no-reboot \
        -no-shutdown \
        -boot d \
        -cpu qemu64 \
        -smp 2 \
        -enable-kvm 2>/dev/null || \
    qemu-system-x86_64 \
        -cdrom "$ISO_FILENAME" \
        -m 512M \
        -display curses \
        -serial stdio \
        -no-reboot \
        -no-shutdown \
        -boot d \
        -cpu qemu64 \
        -smp 2
fi

echo -e "${GREEN}🎉 Syn_OS Kernel ISO build completed successfully!${NC}"