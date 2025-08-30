#!/bin/bash

# SynapticOS Complete Distribution Builder
# Combines ParrotOS base with consciousness-integrated services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                SYNAPTICOS DISTRIBUTION BUILDER              ║${NC}"
echo -e "${PURPLE}║        Complete Linux Distribution with Consciousness        ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}║  🧠 Neural Darwinism Engine  🔒 ParrotOS Security Tools    ║${NC}"
echo -e "${PURPLE}║  🎓 Educational Platform     ⚡ Real-time AI Integration    ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INTEGRATION_DIR="${PROJECT_ROOT}/parrotos-integration"
BASE_DIR="${INTEGRATION_DIR}/base"
OVERLAY_DIR="${INTEGRATION_DIR}/overlay"
BUILD_DIR="${INTEGRATION_DIR}/build"
ISO_ROOT="${BUILD_DIR}/iso_root"
SQUASHFS_ROOT="${BUILD_DIR}/squashfs_root"

BUILD_DATE=$(date +%Y%m%d-%H%M%S)
ISO_FILENAME="SynapticOS-v1.0-consciousness-${BUILD_DATE}.iso"

echo -e "${BLUE}[INFO]${NC} Building SynapticOS complete distribution..."
echo -e "${BLUE}[INFO]${NC} Target ISO: ${ISO_FILENAME}"
echo -e "${BLUE}[INFO]${NC} Build directory: ${BUILD_DIR}"

# Check prerequisites
echo -e "${CYAN}[1/10]${NC} Checking prerequisites"
if [ ! -d "${BASE_DIR}/iso_contents" ]; then
    echo -e "${RED}[ERROR]${NC} ParrotOS base not found. Run setup-parrotos-integration.sh first"
    exit 1
fi

# Required packages for ISO building
REQUIRED_PACKAGES="squashfs-tools xorriso isolinux syslinux-utils"
for pkg in $REQUIRED_PACKAGES; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        echo -e "${YELLOW}[INSTALL]${NC} Installing required package: $pkg"
        sudo apt-get update && sudo apt-get install -y $pkg
    fi
done

# Clean and create build directories
echo -e "${CYAN}[2/10]${NC} Setting up build environment"
sudo rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR" "$ISO_ROOT" "$SQUASHFS_ROOT"

# Copy ParrotOS base
echo -e "${CYAN}[3/10]${NC} Copying ParrotOS base system"
cp -r "${BASE_DIR}/iso_contents"/* "$ISO_ROOT/"

# Extract existing squashfs for modification
echo -e "${CYAN}[4/10]${NC} Extracting ParrotOS filesystem"
if [ -f "$ISO_ROOT/live/filesystem.squashfs" ]; then
    sudo unsquashfs -d "$SQUASHFS_ROOT" "$ISO_ROOT/live/filesystem.squashfs"
    echo -e "${GREEN}[SUCCESS]${NC} ParrotOS filesystem extracted"
else
    echo -e "${RED}[ERROR]${NC} ParrotOS squashfs not found"
    exit 1
fi

# Install our consciousness services
echo -e "${CYAN}[5/10]${NC} Installing SynapticOS consciousness services"

# Create SynapticOS directory structure in chroot
sudo mkdir -p "$SQUASHFS_ROOT/opt/synapticos"
sudo cp -r "$OVERLAY_DIR/services" "$SQUASHFS_ROOT/opt/synapticos/"

# Install systemd services
echo -e "${YELLOW}[INSTALL]${NC} Installing systemd services"
sudo cp "$OVERLAY_DIR"/systemd-services/*.service "$SQUASHFS_ROOT/etc/systemd/system/"
sudo cp "$OVERLAY_DIR"/systemd-services/*.target "$SQUASHFS_ROOT/etc/systemd/system/"

# Install desktop integration
echo -e "${YELLOW}[INSTALL]${NC} Installing desktop integration"
sudo mkdir -p "$SQUASHFS_ROOT/usr/share/applications"
sudo cp "$OVERLAY_DIR"/desktop-integration/applications/*.desktop "$SQUASHFS_ROOT/usr/share/applications/"

# Create SynapticOS user and configurations
echo -e "${CYAN}[6/10]${NC} Configuring SynapticOS environment"

# Create SynapticOS user in chroot
sudo chroot "$SQUASHFS_ROOT" /bin/bash -c "
    # Create synapticos user
    useradd -m -s /bin/bash -G sudo,docker synapticos
    echo 'synapticos:consciousness123' | chpasswd
    
    # Create consciousness data directories
    mkdir -p /home/synapticos/.synapticos/{consciousness,education,ctf,news,context}
    chown -R synapticos:synapticos /home/synapticos/.synapticos
    
    # Set up consciousness auto-start
    mkdir -p /home/synapticos/.config/autostart
    cp /opt/synapticos/desktop-integration/autostart/* /home/synapticos/.config/autostart/ 2>/dev/null || true
    chown -R synapticos:synapticos /home/synapticos/.config
"

# Install additional packages
echo -e "${CYAN}[7/10]${NC} Installing additional packages for consciousness"
PACKAGES_TO_INSTALL="python3-fastapi python3-uvicorn python3-aiohttp python3-docker python3-feedparser python3-beautifulsoup4 python3-dev python3-pip redis-server postgresql-client chromium-browser"

sudo chroot "$SQUASHFS_ROOT" /bin/bash -c "
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y $PACKAGES_TO_INSTALL
    
    # Install Python packages for consciousness services
    pip3 install spacy scikit-learn networkx numpy pydantic PyYAML
    python3 -m spacy download en_core_web_sm
    
    # Enable SynapticOS services
    systemctl enable synapticos-consciousness-bridge.service
    systemctl enable synapticos-educational-platform.service
    systemctl enable synapticos-ctf-platform.service
    systemctl enable synapticos-news-intelligence.service
    systemctl enable synapticos-context-engine.service
    systemctl enable synapticos-stack.target
    
    # Clean up
    apt-get clean
    rm -rf /var/lib/apt/lists/*
"

# Create SynapticOS branding
echo -e "${CYAN}[8/10]${NC} Applying SynapticOS branding"

# Create custom issue file
sudo tee "$SQUASHFS_ROOT/etc/issue" > /dev/null << 'EOF'

███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ████████╗██╗ ██████╗ ██████╗ ███████╗
██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗╚══██╔══╝██║██╔════╝██╔═══██╗██╔════╝
███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝   ██║   ██║██║     ██║   ██║███████╗
╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝    ██║   ██║██║     ██║   ██║╚════██║
███████║   ██║   ██║ ╚████║██║  ██║██║        ██║   ██║╚██████╗╚██████╔╝███████║
╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝

🧠 Consciousness-Integrated Cybersecurity Education & Operations Platform
🔒 Built on ParrotOS Security Foundation with Neural Darwinism AI Engine
🎓 Real-time Adaptive Learning with Advanced Threat Intelligence

Version: 1.0-consciousness    Build: BUILDDATE
Login: synapticos / consciousness123

SynapticOS \n \l

EOF

# Update version info
sudo sed -i "s/BUILDDATE/$BUILD_DATE/g" "$SQUASHFS_ROOT/etc/issue"

# Create custom MOTD
sudo tee "$SQUASHFS_ROOT/etc/motd" > /dev/null << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    Welcome to SynapticOS                     ║
║          Consciousness-Integrated Security Platform          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🧠 Consciousness Services:                                  ║
║     • Consciousness Dashboard: http://localhost:8000        ║
║     • Educational Platform:   http://localhost:8001         ║
║     • CTF Platform:          http://localhost:8086         ║
║     • News Intelligence:     http://localhost:8087         ║
║                                                              ║
║  🔧 Service Management:                                      ║
║     • View status: systemctl status synapticos-stack.target ║
║     • Start all:   systemctl start synapticos-stack.target  ║
║     • Stop all:    systemctl stop synapticos-stack.target   ║
║                                                              ║
║  📚 Learning Resources:                                      ║
║     • /opt/synapticos/ - Service configurations             ║
║     • ~/.synapticos/   - User consciousness data            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF

# Rebuild squashfs with consciousness integration
echo -e "${CYAN}[9/10]${NC} Building consciousness-integrated filesystem"
sudo rm -f "$ISO_ROOT/live/filesystem.squashfs"
sudo mksquashfs "$SQUASHFS_ROOT" "$ISO_ROOT/live/filesystem.squashfs" \
    -comp xz -e boot -wildcards

# Create final ISO
echo -e "${CYAN}[10/10]${NC} Creating SynapticOS distribution ISO"

# Update isolinux configuration for SynapticOS
sudo tee "$ISO_ROOT/isolinux/isolinux.cfg" > /dev/null << 'EOF'
default live
label live
  menu label ^SynapticOS Live (Consciousness Mode)
  kernel /live/vmlinuz
  append initrd=/live/initrd.img boot=live components splash quiet username=synapticos hostname=synapticos
label install
  menu label ^Install SynapticOS
  kernel /live/vmlinuz
  append initrd=/live/initrd.img boot=live components splash quiet username=synapticos hostname=synapticos live-installer
label memtest
  menu label ^Memory Test
  kernel /live/memtest
EOF

# Build the final ISO
cd "$BUILD_DIR"
sudo xorriso -as mkisofs \
    -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
    -c isolinux/boot.cat \
    -b isolinux/isolinux.bin \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -eltorito-alt-boot \
    -e boot/grub/efi.img \
    -no-emul-boot \
    -isohybrid-gpt-basdat \
    -volid "SynapticOS" \
    -o "$ISO_FILENAME" \
    "$ISO_ROOT"

# Calculate checksums
echo -e "${CYAN}[VERIFY]${NC} Calculating checksums"
cd "$BUILD_DIR"
sha256sum "$ISO_FILENAME" > "${ISO_FILENAME}.sha256"
md5sum "$ISO_FILENAME" > "${ISO_FILENAME}.md5"

# Build completion
echo
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}         SYNAPTICOS DISTRIBUTION BUILD COMPLETE                 ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo
echo -e "${BLUE}📀 ISO File:${NC} ${BUILD_DIR}/${ISO_FILENAME}"
echo -e "${BLUE}📊 Size:${NC} $(du -h "${BUILD_DIR}/${ISO_FILENAME}" | cut -f1)"
echo -e "${BLUE}🔐 SHA256:${NC} $(cat "${BUILD_DIR}/${ISO_FILENAME}.sha256" | cut -d' ' -f1)"
echo -e "${BLUE}🔐 MD5:${NC} $(cat "${BUILD_DIR}/${ISO_FILENAME}.md5" | cut -d' ' -f1)"
echo
echo -e "${YELLOW}🚀 Ready for deployment!${NC}"
echo -e "  • Boot from USB/DVD for live environment"
echo -e "  • Default login: synapticos / consciousness123"
echo -e "  • Consciousness services auto-start on boot"
echo -e "  • Access dashboard at http://localhost:8000"
echo
echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. Test in virtual machine"
echo -e "  2. Validate consciousness integration"
echo -e "  3. Test educational platform functionality"
echo -e "  4. Deploy to target hardware"
echo
echo -e "${GREEN}🎯 SynapticOS Distribution Ready!${NC}"
