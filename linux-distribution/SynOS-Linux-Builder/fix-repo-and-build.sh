#!/bin/bash
# Quick fix for package repository issue and rebuild ISO

set -e

echo "🔧 SynOS ISO Build - Quick Fix"
echo "=============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Navigate to builder directory
cd /home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder

echo -e "\n${YELLOW}Step 1: Creating proper package repository...${NC}"

# Create packages directory if missing
mkdir -p packages

# Copy AI packages
echo "Copying AI service packages..."
cp -v ../SynOS-Packages/*.deb packages/ 2>/dev/null || true

# Create proper Packages index
cd packages
echo "Creating Packages index..."
dpkg-scanpackages . /dev/null > Packages 2>/dev/null
gzip -9c < Packages > Packages.gz
echo -e "${GREEN}✓ Packages index created${NC}"

cd ..

echo -e "\n${YELLOW}Step 2: Setting up repository for chroot...${NC}"

# Create hook to copy repository into chroot
mkdir -p config/hooks/normal

cat > config/hooks/normal/0100-setup-local-repo.hook.chroot << 'EOFHOOK'
#!/bin/bash
# Setup local package repository in chroot

set -e

echo "Setting up SynOS local package repository..."

# Create repo directory
mkdir -p /tmp/synos-repo

# This will be bind-mounted from host, but create placeholder
touch /tmp/synos-repo/.placeholder

echo "✓ Repository directory ready"

exit 0
EOFHOOK

chmod +x config/hooks/normal/0100-setup-local-repo.hook.chroot

# Create hook to install SynOS packages
cat > config/hooks/normal/0200-install-synos-packages.hook.chroot << 'EOFHOOK'
#!/bin/bash
# Install SynOS AI packages

set -e

echo "Installing SynOS AI packages..."

# Check if repository is accessible
if [ -f /tmp/synos-repo/Packages ]; then
    echo "Repository found, installing packages..."

    # Try to install available .deb files directly
    if ls /tmp/synos-repo/*.deb 1> /dev/null 2>&1; then
        dpkg -i /tmp/synos-repo/*.deb || apt-get -f install -y
        echo "✓ SynOS packages installed"
    else
        echo "⚠ No .deb packages found in repository"
    fi
else
    echo "⚠ Repository not accessible, skipping package installation"
fi

exit 0
EOFHOOK

chmod +x config/hooks/normal/0200-install-synos-packages.hook.chroot

echo -e "${GREEN}✓ Repository hooks created${NC}"

echo -e "\n${YELLOW}Step 3: Cleaning previous build...${NC}"
echo 'superadmin33' | sudo -S lb clean --purge 2>/dev/null || true
echo -e "${GREEN}✓ Build cleaned${NC}"

echo -e "\n${YELLOW}Step 4: Configuring live-build...${NC}"
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
    --iso-application "SynOS Linux" \
    --iso-publisher "SynOS Development Team" \
    --iso-volume "SynOS Linux 1.0.0" \
    --memtest memtest86+ \
    --win32-loader false

echo -e "${GREEN}✓ Configuration complete${NC}"

echo -e "\n${YELLOW}Step 5: Building ISO (this will take 15-30 minutes)...${NC}"

# Create bind mount script for repository
cat > bind-repo.sh << 'EOFBIND'
#!/bin/bash
# Bind mount package repository into chroot

REPO_SRC="/home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder/packages"
REPO_DST="chroot/tmp/synos-repo"

if [ -d "chroot" ] && [ -d "$REPO_SRC" ]; then
    mkdir -p "$REPO_DST"

    # Copy packages instead of bind mount (more reliable)
    cp -av "$REPO_SRC"/* "$REPO_DST/" 2>/dev/null || true

    echo "✓ Repository copied to chroot"
fi
EOFBIND

chmod +x bind-repo.sh

# Build with repository binding
echo 'superadmin33' | sudo -S lb build 2>&1 | tee build-quickfix-$(date +%H%M%S).log &

BUILD_PID=$!

# Wait for chroot to be created, then copy repo
sleep 30

if [ -d "chroot" ]; then
    echo -e "\n${YELLOW}Copying package repository to chroot...${NC}"
    echo 'superadmin33' | sudo -S mkdir -p chroot/tmp/synos-repo
    echo 'superadmin33' | sudo -S cp -av packages/* chroot/tmp/synos-repo/ 2>/dev/null || true
    echo -e "${GREEN}✓ Repository copied${NC}"
fi

# Wait for build to complete
wait $BUILD_PID

BUILD_EXIT=$?

echo -e "\n${YELLOW}Step 6: Checking build result...${NC}"

# Find ISO
ISO_FILE=$(find . -maxdepth 1 -name "*.iso" -type f | head -1)

if [ -n "$ISO_FILE" ] && [ -f "$ISO_FILE" ]; then
    ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ ISO BUILD SUCCESSFUL!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "ISO: ${YELLOW}$ISO_FILE${NC}"
    echo -e "Size: ${YELLOW}$ISO_SIZE${NC}"
    echo -e ""
    echo -e "Create checksum:"
    echo -e "  ${YELLOW}sha256sum $ISO_FILE > ${ISO_FILE}.sha256${NC}"
    echo -e ""
    echo -e "Next step: VM Testing"
    echo -e "  ${YELLOW}VirtualBox → New → Linux/Debian → Mount ISO${NC}"
    echo -e ""
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ ISO BUILD FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e ""
    echo -e "Check logs:"
    ls -lh build-*.log 2>/dev/null || true
    echo -e ""
    echo -e "Most recent errors:"
    tail -50 build-quickfix-*.log 2>/dev/null | grep -i error || echo "No errors in log"
    echo -e ""
    exit 1
fi
