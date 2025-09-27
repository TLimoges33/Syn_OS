#!/bin/bash
# SynapticOS Linux Distribution Builder
# Builds a custom Linux distribution based on ParrotOS with AI consciousness integration

set -e

# Configuration
SYNOS_VERSION="1.0.0-alpha"
BUILD_DIR="/tmp/synos-build"
ISO_NAME="SynapticOS-Linux-${SYNOS_VERSION}-$(date +%Y%m%d)"
BASE_ISO="parrot-security-6.4-amd64.iso"
WORKSPACE_ROOT="$(dirname "$(readlink -f "$0")")/.."

echo "🚀 Building SynapticOS Linux Distribution v${SYNOS_VERSION}"
echo "📂 Workspace: ${WORKSPACE_ROOT}"
echo "🏗️ Build directory: ${BUILD_DIR}"

# Prerequisites check
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    local missing_tools=()
    
    command -v debootstrap >/dev/null || missing_tools+=("debootstrap")
    command -v live-build >/dev/null || missing_tools+=("live-build")
    command -v squashfs-tools >/dev/null || missing_tools+=("squashfs-tools")
    command -v genisoimage >/dev/null || missing_tools+=("genisoimage")
    command -v cargo >/dev/null || missing_tools+=("cargo")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo "❌ Missing required tools: ${missing_tools[*]}"
        echo "📦 Install with: sudo apt install ${missing_tools[*]}"
        exit 1
    fi
    
    echo "✅ All prerequisites satisfied"
}

# Build AI Engine and components
build_synos_components() {
    echo "🤖 Building SynapticOS AI components..."
    
    cd "${WORKSPACE_ROOT}"
    
    # Build AI Engine
    echo "🧠 Building AI Engine..."
    cargo build --release --manifest-path src/ai-engine/Cargo.toml
    
    # Build core components
    echo "🛡️ Building security framework..."
    cargo build --release --manifest-path core/security/Cargo.toml
    
    # Build kernel modules
    echo "🔧 Building kernel components..."
    cargo build --release --manifest-path src/kernel/Cargo.toml --target x86_64-unknown-none
    
    echo "✅ SynapticOS components built successfully"
}

# Create build environment
setup_build_environment() {
    echo "🏗️ Setting up build environment..."
    
    # Clean previous build
    sudo rm -rf "${BUILD_DIR}"
    mkdir -p "${BUILD_DIR}"/{rootfs,iso,packages}
    
    # Create package directory structure
    mkdir -p "${BUILD_DIR}/packages/synos"
    
    echo "✅ Build environment ready"
}

# Extract ParrotOS base system
extract_parrot_base() {
    echo "🔓 Extracting ParrotOS base system..."
    
    if [ ! -f "${BASE_ISO}" ]; then
        echo "❌ ParrotOS ISO not found: ${BASE_ISO}"
        echo "📥 Please download ParrotOS 6.4 Security Edition"
        exit 1
    fi
    
    # Mount ISO and extract squashfs
    sudo mkdir -p /mnt/parrot-iso
    sudo mount -o loop "${BASE_ISO}" /mnt/parrot-iso
    
    # Extract filesystem
    sudo unsquashfs -d "${BUILD_DIR}/rootfs" /mnt/parrot-iso/live/filesystem.squashfs
    
    # Unmount ISO
    sudo umount /mnt/parrot-iso
    sudo rmdir /mnt/parrot-iso
    
    echo "✅ ParrotOS base system extracted"
}

# Install SynapticOS components
install_synos_components() {
    echo "🤖 Installing SynapticOS components..."
    
    # Create SynOS directories
    sudo mkdir -p "${BUILD_DIR}/rootfs"/{usr/bin,usr/share/synos,etc/synos,var/lib/synos}
    
    # Install AI Engine binary
    sudo cp "${WORKSPACE_ROOT}/target/release/synaptic-ai-engine" "${BUILD_DIR}/rootfs/usr/bin/synos-ai-engine"
    sudo chmod +x "${BUILD_DIR}/rootfs/usr/bin/synos-ai-engine"
    
    # Install systemd services
    sudo mkdir -p "${BUILD_DIR}/rootfs/etc/systemd/system"
    sudo cp "${WORKSPACE_ROOT}/configs/systemd"/*.service "${BUILD_DIR}/rootfs/etc/systemd/system/"
    
    # Install configuration files
    sudo cp -r "${WORKSPACE_ROOT}/configs/runtime"/* "${BUILD_DIR}/rootfs/etc/synos/"
    
    # Create synos user
    sudo chroot "${BUILD_DIR}/rootfs" /bin/bash -c "
        useradd -r -s /bin/false -d /var/lib/synos synos
        chown -R synos:synos /var/lib/synos
    "
    
    echo "✅ SynapticOS components installed"
}

# Customize branding and desktop
customize_branding() {
    echo "🎨 Customizing SynapticOS branding..."
    
    # Update OS release info
    sudo tee "${BUILD_DIR}/rootfs/etc/os-release" > /dev/null << EOF
NAME="SynapticOS Linux"
VERSION="${SYNOS_VERSION}"
ID=synapticos
ID_LIKE=debian
PRETTY_NAME="SynapticOS Linux ${SYNOS_VERSION}"
VERSION_ID="${SYNOS_VERSION}"
HOME_URL="https://github.com/Syn_OS-Dev-Team/Syn_OS"
SUPPORT_URL="https://github.com/Syn_OS-Dev-Team/Syn_OS/issues"
BUG_REPORT_URL="https://github.com/Syn_OS-Dev-Team/Syn_OS/issues"
EOF
    
    # Update hostname
    echo "synapticos" | sudo tee "${BUILD_DIR}/rootfs/etc/hostname" > /dev/null
    
    # Customize MATE desktop
    # TODO: Add custom themes, wallpapers, and desktop configurations
    
    echo "✅ Branding customization complete"
}

# Generate ISO image
generate_iso() {
    echo "💿 Generating SynapticOS Linux ISO..."
    
    # Create squashfs
    sudo mksquashfs "${BUILD_DIR}/rootfs" "${BUILD_DIR}/iso/live/filesystem.squashfs" -comp xz
    
    # Copy boot files (this is simplified - real implementation needs proper boot setup)
    sudo mkdir -p "${BUILD_DIR}/iso"/{live,isolinux}
    
    # Generate ISO
    sudo genisoimage \
        -r -V "SynapticOS Linux ${SYNOS_VERSION}" \
        -cache-inodes -J -l \
        -b isolinux/isolinux.bin \
        -c isolinux/boot.cat \
        -no-emul-boot -boot-load-size 4 \
        -boot-info-table \
        -o "${ISO_NAME}.iso" \
        "${BUILD_DIR}/iso"
    
    # Generate checksums
    sha256sum "${ISO_NAME}.iso" > "${ISO_NAME}.iso.sha256"
    md5sum "${ISO_NAME}.iso" > "${ISO_NAME}.iso.md5"
    
    echo "✅ ISO generated: ${ISO_NAME}.iso"
    echo "📊 Size: $(du -h "${ISO_NAME}.iso" | cut -f1)"
}

# Cleanup
cleanup() {
    echo "🧹 Cleaning up build environment..."
    sudo rm -rf "${BUILD_DIR}"
    echo "✅ Cleanup complete"
}

# Main execution
main() {
    echo "🎯 Starting SynapticOS Linux Distribution build process..."
    
    check_prerequisites
    build_synos_components
    setup_build_environment
    extract_parrot_base
    install_synos_components
    customize_branding
    generate_iso
    cleanup
    
    echo "🎉 SynapticOS Linux Distribution build complete!"
    echo "📀 ISO: ${ISO_NAME}.iso"
    echo "🔒 SHA256: ${ISO_NAME}.iso.sha256"
    echo "🔒 MD5: ${ISO_NAME}.iso.md5"
}

# Execute main function
main "$@"
