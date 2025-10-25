#!/bin/bash
set -e

echo "🚀 Building Complete SynOS Linux Distribution..."

# Configuration
SYNOS_VERSION="1.0.0"
BUILD_DATE=$(date +%Y%m%d)
ISO_NAME="synos-linux-${SYNOS_VERSION}-${BUILD_DATE}-amd64.iso"
BUILD_DIR="$(pwd)"
PACKAGES_DIR="${BUILD_DIR}/packages"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

# Check if we're root
if [ "$EUID" -eq 0 ]; then
    error "Do not run this script as root! Use regular user with sudo access."
    exit 1
fi

# Check prerequisites
log "🔍 Checking prerequisites..."

MISSING_TOOLS=""
for tool in lb debootstrap xorriso; do
    if ! command -v "$tool" > /dev/null; then
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    fi
done

if [ -n "$MISSING_TOOLS" ]; then
    error "Missing required tools:$MISSING_TOOLS"
    log "Install with: sudo apt update && sudo apt install live-build xorriso"
    exit 1
fi

success "All prerequisites satisfied"

# Clean previous builds
log "🧹 Cleaning previous builds..."
if [ -d .build ]; then
    echo "superadmin33" | sudo -S lb clean || true
fi

# Set up local package repository if AI package exists
if [ -f "${PACKAGES_DIR}/synos-ai-engine_1.0.0_amd64.deb" ]; then
    log "📦 Setting up local package repository..."
    mkdir -p config/packages.chroot
    cp "${PACKAGES_DIR}/synos-ai-engine_1.0.0_amd64.deb" config/packages.chroot/
    success "SynOS AI Engine package added"
else
    warn "SynOS AI Engine package not found - will be skipped in this build"
fi

# Create local repository for custom packages
log "📚 Creating local APT repository..."
mkdir -p custom-repo
if [ -f "${PACKAGES_DIR}/synos-ai-engine_1.0.0_amd64.deb" ]; then
    cp "${PACKAGES_DIR}"/*.deb custom-repo/ 2>/dev/null || true
    cd custom-repo
    dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
    cd ..

    # Add custom repository to sources
    mkdir -p config/archives
    cat > config/archives/synos-local.list.chroot << 'EOF'
# SynOS Local Repository
deb [trusted=yes] file:///tmp/synos-repo ./
EOF

    # Copy repository to includes
    mkdir -p config/includes.chroot/tmp/synos-repo
    cp -r custom-repo/* config/includes.chroot/tmp/synos-repo/
fi

# Configure live-build
log "⚙️  Configuring live-build..."
echo "superadmin33" | sudo -S lb config \
    --binary-images iso-hybrid \
    --mode debian \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --linux-flavours amd64 \
    --linux-packages linux-image \
    --bootappend-live "boot=live components quiet splash" \
    --debian-installer live \
    --debian-installer-gui true \
    --iso-application "SynOS Linux" \
    --iso-publisher "SynOS Development Team" \
    --iso-volume "SynOS Linux ${SYNOS_VERSION}" \
    --memtest memtest86+ \
    --win32-loader false

# Update binary config with SynOS branding
cat >> config/binary << EOF

# SynOS specific configuration
LB_ISO_APPLICATION="SynOS Linux - AI-Conscious Operating System"
LB_ISO_PUBLISHER="SynOS Development Team <dev@synos.ai>"
LB_ISO_VOLUME="SynOS-Linux-${SYNOS_VERSION}"
EOF

log "🏗️  Starting SynOS build process..."

# Build stages with progress tracking
stages=(
    "bootstrap:🌱 Bootstrapping base system"
    "chroot:📦 Installing packages and configuring system"
    "binary:💿 Creating bootable ISO image"
)

for stage_info in "${stages[@]}"; do
    stage="${stage_info%:*}"
    desc="${stage_info#*:}"

    log "$desc..."

    start_time=$(date +%s)

    if echo "superadmin33" | sudo -S lb build 2>&1 | tee "build-${stage}.log"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        success "${desc} completed in ${duration}s"
    else
        error "${desc} failed! Check build-${stage}.log for details"
        exit 1
    fi

    # Break after each major milestone to show progress
    case "$stage" in
        "bootstrap")
            log "📊 Bootstrap complete - base Debian system ready"
            ;;
        "chroot")
            log "📊 Package installation complete - system configured"
            ;;
        "binary")
            log "📊 ISO creation complete!"
            break
            ;;
    esac
done

# Check if ISO was created
if [ -f live-image-amd64.hybrid.iso ]; then
    # Rename to SynOS branded name
    mv live-image-amd64.hybrid.iso "$ISO_NAME"

    # Calculate SHA256
    sha256sum "$ISO_NAME" > "${ISO_NAME}.sha256"

    # Get file size
    ISO_SIZE=$(du -h "$ISO_NAME" | cut -f1)

    success "🎉 SynOS Linux ISO build complete!"
    echo
    log "📊 Build Summary:"
    log "   📁 File: ${BLUE}${ISO_NAME}${NC}"
    log "   📏 Size: ${GREEN}${ISO_SIZE}${NC}"
    log "   🔐 SHA256: $(cat "${ISO_NAME}.sha256" | cut -d' ' -f1)"
    log "   📅 Built: $(date)"
    echo
    log "🔍 Quick validation:"
    file "$ISO_NAME"
    echo
    log "🚀 To test the ISO:"
    log "   VirtualBox: Create VM with 4GB RAM, boot from ${ISO_NAME}"
    log "   QEMU: qemu-system-x86_64 -m 4G -cdrom ${ISO_NAME} -boot d"
    log "   Physical: Write to USB with dd or balenaEtcher"
    echo
    success "SynOS Linux build completed successfully! 🎊"

else
    error "ISO file not found! Build may have failed."
    log "Check the build logs for errors:"
    ls -la build-*.log 2>/dev/null || true
    exit 1
fi