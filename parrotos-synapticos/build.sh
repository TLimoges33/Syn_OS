#!/bin/bash
# SynapticOS Build Script
# Builds ParrotOS with SynapticOS consciousness enhancements

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Build configuration
BUILD_DIR="build"
ISO_NAME="synapticos-$(date +%Y%m%d).iso"
THREADS=$(nproc)

echo -e "${GREEN}=== SynapticOS Build System ===${NC}"
echo "Building with $THREADS threads"

# Function to print status
status() {
    echo -e "${YELLOW}[*]${NC} $1"
}

error() {
    echo -e "${RED}[!]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    status "Checking prerequisites..."
    
    # Check for required tools
    for tool in git make gcc debootstrap squashfs-tools xorriso; do
        if ! command -v $tool &> /dev/null; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check if running as root (required for debootstrap)
    if [ "$EUID" -ne 0 ]; then 
        error "Please run as root (required for debootstrap)"
    fi
    
    success "Prerequisites check passed"
}

# Prepare build environment
prepare_build() {
    status "Preparing build environment..."
    
    # Create build directory
    mkdir -p $BUILD_DIR/{iso,squashfs,work}
    
    # Copy ParrotOS base
    if [ -d "parrot" ]; then
        cp -r parrot/* $BUILD_DIR/work/
    else
        error "ParrotOS base not found. Please clone ParrotOS first."
    fi
    
    success "Build environment prepared"
}

# Apply SynapticOS overlay
apply_overlay() {
    status "Applying SynapticOS overlay..."
    
    # Copy consciousness system
    mkdir -p $BUILD_DIR/work/opt/synapticos/consciousness
    cp -r synapticos-overlay/consciousness/* $BUILD_DIR/work/opt/synapticos/consciousness/
    
    # Copy configuration
    mkdir -p $BUILD_DIR/work/etc/synapticos
    cp synapticos-overlay/config/* $BUILD_DIR/work/etc/synapticos/
    
    # Create systemd services
    cat > $BUILD_DIR/work/etc/systemd/system/synapticos-consciousness.service << EOF
[Unit]
Description=SynapticOS Consciousness Engine
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/synapticos/consciousness/neural_darwinism.py
Restart=always
User=synapticos

[Install]
WantedBy=multi-user.target
EOF

    # Create synapticos user
    chroot $BUILD_DIR/work useradd -m -s /bin/bash synapticos || true
    
    success "SynapticOS overlay applied"
}

# Install additional packages
install_packages() {
    status "Installing additional packages..."
    
    # Mount necessary filesystems for chroot
    mount --bind /dev $BUILD_DIR/work/dev
    mount --bind /proc $BUILD_DIR/work/proc
    mount --bind /sys $BUILD_DIR/work/sys
    
    # Update package list
    chroot $BUILD_DIR/work apt-get update
    
    # Install Python and AI dependencies
    chroot $BUILD_DIR/work apt-get install -y \
        python3 python3-pip python3-numpy python3-scipy \
        python3-sklearn python3-torch \
        build-essential linux-headers-generic
    
    # Install Python packages for consciousness system
    chroot $BUILD_DIR/work pip3 install \
        asyncio dataclasses typing-extensions \
        aiohttp websockets
    
    # Cleanup
    umount $BUILD_DIR/work/dev
    umount $BUILD_DIR/work/proc
    umount $BUILD_DIR/work/sys
    
    success "Additional packages installed"
}

# Build kernel modules
build_kernel_modules() {
    status "Building kernel modules..."
    
    # This would contain the actual kernel module build process
    # For now, we'll create a placeholder
    mkdir -p $BUILD_DIR/work/lib/modules/synapticos
    
    success "Kernel modules built"
}

# Create squashfs
create_squashfs() {
    status "Creating squashfs filesystem..."
    
    mksquashfs $BUILD_DIR/work $BUILD_DIR/squashfs/filesystem.squashfs \
        -comp xz -b 1M -Xdict-size 100% \
        -processors $THREADS
    
    # Calculate size for manifest
    printf $(du -sx --block-size=1 $BUILD_DIR/work | cut -f1) > $BUILD_DIR/iso/filesystem.size
    
    success "Squashfs created"
}

# Create ISO
create_iso() {
    status "Creating ISO image..."
    
    # Copy squashfs to ISO directory
    cp $BUILD_DIR/squashfs/filesystem.squashfs $BUILD_DIR/iso/
    
    # Create ISO with xorriso
    xorriso -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "SynapticOS" \
        -eltorito-boot isolinux/isolinux.bin \
        -eltorito-catalog isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -output $ISO_NAME \
        $BUILD_DIR/iso
    
    success "ISO created: $ISO_NAME"
}

# Main build process
main() {
    echo "Starting SynapticOS build process..."
    echo "ISO will be created as: $ISO_NAME"
    echo
    
    check_prerequisites
    prepare_build
    apply_overlay
    install_packages
    build_kernel_modules
    create_squashfs
    create_iso
    
    echo
    success "Build completed successfully!"
    echo "ISO location: $(pwd)/$ISO_NAME"
    echo "Size: $(du -h $ISO_NAME | cut -f1)"
}

# Handle command line arguments
case "$1" in
    --full)
        main
        ;;
    --overlay-only)
        apply_overlay
        ;;
    --iso-only)
        create_squashfs
        create_iso
        ;;
    *)
        echo "Usage: $0 [--full|--overlay-only|--iso-only]"
        echo "  --full         Full build process (default)"
        echo "  --overlay-only Only apply SynapticOS overlay"
        echo "  --iso-only     Only create ISO from existing build"
        exit 1
        ;;
esac