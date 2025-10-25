#!/bin/bash
# SynOS Ultimate Security Distribution Builder
# Combines Kali + ParrotOS + BlackArch tools with SynOS AI

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   SynOS Ultimate Security Distribution${NC}"
echo -e "${BLUE}   Kali + ParrotOS + BlackArch + AI${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}\n"

SUDO_PASS='superadmin33'
BUILD_DIR="/home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder"

cd "$BUILD_DIR"

# ═══════════════════════════════════════════════════════════════
# STEP 1: Prepare Package Repository
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[1/8]${NC} Preparing SynOS package repository..."

mkdir -p packages
cp -v ../SynOS-Packages/*.deb packages/ 2>/dev/null || true

cd packages
dpkg-scanpackages . /dev/null > Packages 2>/dev/null
gzip -9c < Packages > Packages.gz
echo -e "${GREEN}✓ Package repository created${NC}"
cd ..

# ═══════════════════════════════════════════════════════════════
# STEP 2: Configure External Repositories
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[2/8]${NC} Configuring security tool repositories..."

# Use HTTP for ParrotOS to avoid certificate issues during bootstrap
cat > config/archives/parrot.list.chroot << 'EOF'
# ParrotOS Security Repository (HTTP to avoid cert issues during build)
deb http://deb.parrot.sh/parrot/ parrot main contrib non-free
deb http://deb.parrot.sh/parrot/ parrot-security main contrib non-free
EOF

# Optional: Add Kali (commented by default, can enable if needed)
cat > config/archives/kali.list.chroot.disabled << 'EOF'
# Kali Linux Repository (disabled by default to reduce conflicts)
# Uncomment to enable Kali tools
# deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF

echo -e "${GREEN}✓ Repository configuration updated${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 3: Use Expanded Security Tools List
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[3/8]${NC} Activating expanded security tools..."

# Rename expanded list to active
if [ -f config/package-lists/synos-security-expanded.list.chroot ]; then
    mv config/package-lists/synos-security.list.chroot \
       config/package-lists/synos-security-basic.list.chroot.backup

    mv config/package-lists/synos-security-expanded.list.chroot \
       config/package-lists/synos-security.list.chroot

    echo -e "${GREEN}✓ 200+ security tools activated${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# STEP 4: Create Hook to Copy Packages
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[4/8]${NC} Creating package installation hooks..."

mkdir -p config/hooks/normal

cat > config/hooks/live/0050-copy-synos-packages.hook.chroot << 'EOFHOOK'
#!/bin/bash
# Copy SynOS AI packages into chroot
set -e

echo "Copying SynOS AI packages..."

# This directory will be bind-mounted by the parent build script
if [ -d /tmp/synos-repo-external ]; then
    mkdir -p /tmp/synos-repo
    cp -av /tmp/synos-repo-external/* /tmp/synos-repo/ || true
    echo "✓ SynOS packages copied"
else
    echo "⚠ SynOS package source not available yet"
fi

exit 0
EOFHOOK

chmod +x config/hooks/live/0050-copy-synos-packages.hook.chroot

cat > config/hooks/live/0100-install-synos-packages.hook.chroot << 'EOFHOOK'
#!/bin/bash
# Install SynOS AI packages
set -e

echo "Installing SynOS AI packages..."

if [ -d /tmp/synos-repo ] && ls /tmp/synos-repo/*.deb 1> /dev/null 2>&1; then
    dpkg -i /tmp/synos-repo/*.deb || apt-get -f install -y
    echo "✓ SynOS AI services installed"
else
    echo "⚠ No SynOS packages found, skipping"
fi

exit 0
EOFHOOK

chmod +x config/hooks/live/0100-install-synos-packages.hook.chroot

echo -e "${GREEN}✓ Installation hooks created${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 5: Clean Previous Build
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[5/8]${NC} Cleaning previous build artifacts..."

echo "$SUDO_PASS" | sudo -S lb clean --purge 2>&1 | tail -3

echo -e "${GREEN}✓ Build environment cleaned${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 6: Configure Live-Build
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[6/8]${NC} Configuring live-build system..."

lb config \
    --binary-images iso-hybrid \
    --mode debian \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --linux-flavours amd64 \
    --linux-packages linux-image \
    --bootappend-live "boot=live components quiet splash" \
    --debian-installer live \
    --debian-installer-gui true \
    --iso-application "SynOS Ultimate Security" \
    --iso-publisher "SynOS Development Team" \
    --iso-volume "SynOS-Ultimate-1.0.0" \
    --memtest memtest86+ \
    --win32-loader false

echo -e "${GREEN}✓ Live-build configured${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 7: Start Build Process
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[7/8]${NC} Starting ISO build (30-45 minutes)..."
echo -e "${BLUE}Build log: build-ultimate-$(date +%Y%m%d-%H%M%S).log${NC}\n"

# Start build in background
BUILD_LOG="build-ultimate-$(date +%Y%m%d-%H%M%S).log"
echo "$SUDO_PASS" | sudo -S lb build > "$BUILD_LOG" 2>&1 &
BUILD_PID=$!

echo -e "${GREEN}✓ Build started (PID: $BUILD_PID)${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 8: Monitor and Copy Packages
# ═══════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[8/8]${NC} Monitoring build and injecting packages..."

# Wait for chroot to be created
WAIT_COUNT=0
while [ ! -d "chroot" ] && [ $WAIT_COUNT -lt 60 ]; do
    sleep 5
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo -n "."
done

echo ""

if [ -d "chroot" ]; then
    echo -e "${GREEN}✓ Chroot created, injecting SynOS packages...${NC}"

    # Create package directory accessible from chroot
    echo "$SUDO_PASS" | sudo -S mkdir -p chroot/tmp/synos-repo-external
    echo "$SUDO_PASS" | sudo -S cp -av packages/* chroot/tmp/synos-repo-external/ 2>/dev/null || true

    echo -e "${GREEN}✓ Packages injected into build${NC}"
else
    echo -e "${YELLOW}⚠ Chroot not created yet, packages will be handled by hooks${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# COMPLETION MONITOR
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Build Progress Monitoring${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}\n"

echo "Build PID: $BUILD_PID"
echo "Log file: $BUILD_LOG"
echo ""
echo "Monitor progress:"
echo "  tail -f $BUILD_LOG"
echo ""
echo "Check for completion:"
echo "  ps -p $BUILD_PID"
echo ""
echo -e "${YELLOW}Estimated completion: 30-45 minutes${NC}"
echo ""
echo -e "${GREEN}Script will wait for build to complete...${NC}\n"

# Wait for build to finish
wait $BUILD_PID
BUILD_EXIT=$?

# ═══════════════════════════════════════════════════════════════
# BUILD RESULT
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Build Result${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}\n"

ISO_FILE=$(find . -maxdepth 1 -name "*.iso" -type f -mmin -120 | head -1)

if [ -n "$ISO_FILE" ] && [ -f "$ISO_FILE" ]; then
    ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)

    echo -e "${GREEN}════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}   ✓ BUILD SUCCESSFUL!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════${NC}\n"

    echo -e "ISO File: ${YELLOW}$ISO_FILE${NC}"
    echo -e "Size: ${YELLOW}$ISO_SIZE${NC}"
    echo ""

    # Create checksums
    echo "Creating checksums..."
    sha256sum "$ISO_FILE" > "${ISO_FILE}.sha256"
    md5sum "$ISO_FILE" > "${ISO_FILE}.md5"

    echo -e "${GREEN}✓ Checksums created${NC}"
    echo ""

    echo "Next steps:"
    echo "  1. Verify ISO: sha256sum -c ${ISO_FILE}.sha256"
    echo "  2. VM Testing: Use VM_TESTING_GUIDE.md"
    echo "  3. Create bootable USB: dd if=$ISO_FILE of=/dev/sdX bs=4M"
    echo ""

    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════${NC}"
    echo -e "${RED}   ✗ BUILD FAILED${NC}"
    echo -e "${RED}════════════════════════════════════════════════${NC}\n"

    echo "Check build log:"
    echo "  tail -100 $BUILD_LOG"
    echo ""
    echo "Recent errors:"
    tail -50 "$BUILD_LOG" | grep -i error || echo "No errors found in log tail"
    echo ""

    exit 1
fi
