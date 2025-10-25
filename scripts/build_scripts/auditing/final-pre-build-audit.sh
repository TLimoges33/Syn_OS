#!/usr/bin/env bash
################################################################################
# SynOS Final Pre-Build Audit & Verification
# Comprehensive check before ISO creation
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; }
info() { echo -e "${BLUE}[i]${NC} $*"; }

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       SynOS Final Pre-Build Audit & Verification         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

################################################################################
# SIZE CHECK
################################################################################

echo "=== FILESYSTEM SIZE ==="
CHROOT_SIZE=$(sudo du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)
log "Current chroot size: $CHROOT_SIZE"
echo ""

################################################################################
# SECURITY TOOLS VERIFICATION
################################################################################

echo "=== SECURITY TOOLS VERIFICATION ==="

# Check tool categories
CATEGORIES=$(sudo find "$CHROOT_DIR/usr/share/desktop-directories/" -name "synos-*.directory" 2>/dev/null | wc -l)
log "Tool categories: $CATEGORIES"

# Check tool launchers
LAUNCHERS=$(sudo find "$CHROOT_DIR/usr/share/applications/" -name "synos-*.desktop" 2>/dev/null | wc -l)
log "Tool launchers: $LAUNCHERS"

# List categories
info "Categories found:"
sudo ls "$CHROOT_DIR/usr/share/desktop-directories/" 2>/dev/null | grep synos | sed 's/.directory//' | sed 's/synos-/  - /'

echo ""

################################################################################
# GITHUB REPOS VERIFICATION
################################################################################

echo "=== GITHUB REPOSITORIES ==="

if [ -d "$CHROOT_DIR/opt/github-repos" ]; then
    REPO_COUNT=$(sudo ls -1 "$CHROOT_DIR/opt/github-repos/" 2>/dev/null | wc -l)
    log "GitHub repos: $REPO_COUNT"
    info "Repositories:"
    sudo ls -1 "$CHROOT_DIR/opt/github-repos/" 2>/dev/null | while read repo; do
        SIZE=$(sudo du -sh "$CHROOT_DIR/opt/github-repos/$repo" 2>/dev/null | cut -f1)
        echo "  - $repo ($SIZE)"
    done
else
    warn "No GitHub repos found"
fi

# Check for duplicates
if [ -d "$CHROOT_DIR/opt/tools" ]; then
    warn "DUPLICATE: /opt/tools directory still exists!"
    sudo du -sh "$CHROOT_DIR/opt/tools" 2>/dev/null
else
    log "No duplicate /opt/tools directory"
fi

echo ""

################################################################################
# AI/ML PACKAGES VERIFICATION
################################################################################

echo "=== AI/ML PACKAGES ==="

if [ -d "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages" ]; then
    info "Checking Python packages..."

    # Check for bloat
    if [ -d "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/nvidia" ]; then
        error "BLOAT: NVIDIA packages still present!"
        sudo du -sh "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/nvidia" 2>/dev/null
    else
        log "NVIDIA packages removed ✓"
    fi

    if [ -d "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/triton" ]; then
        error "BLOAT: Triton still present!"
        sudo du -sh "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/triton" 2>/dev/null
    else
        log "Triton removed ✓"
    fi

    # Check for essential packages
    info "Essential AI packages:"
    for pkg in torch transformers pandas numpy scikit-learn langchain; do
        if [ -d "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/$pkg" ]; then
            SIZE=$(sudo du -sh "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/$pkg" 2>/dev/null | cut -f1)
            echo "  - $pkg: $SIZE ✓"
        else
            echo "  - $pkg: MISSING ✗"
        fi
    done
fi

echo ""

################################################################################
# BRANDING VERIFICATION
################################################################################

echo "=== BRANDING & CONFIGURATION ==="

# GRUB theme
if [ -d "$CHROOT_DIR/boot/grub/themes/synos" ]; then
    log "GRUB theme installed ✓"
else
    warn "GRUB theme missing"
fi

# Plymouth theme
if [ -d "$CHROOT_DIR/usr/share/plymouth/themes/synos" ]; then
    log "Plymouth theme installed ✓"
else
    warn "Plymouth theme missing"
fi

# Demo app
if [ -f "$CHROOT_DIR/usr/local/bin/synos-demo" ]; then
    log "Demo app installed ✓"
else
    warn "Demo app missing"
fi

echo ""

################################################################################
# CACHE & BLOAT CHECK
################################################################################

echo "=== CACHE & BLOAT CHECK ==="

# PIP cache
if [ -d "$CHROOT_DIR/root/.cache/pip" ]; then
    CACHE_SIZE=$(sudo du -sh "$CHROOT_DIR/root/.cache/pip" 2>/dev/null | cut -f1)
    error "BLOAT: PIP cache present: $CACHE_SIZE"
else
    log "PIP cache cleaned ✓"
fi

# Root cache
if [ -d "$CHROOT_DIR/root/.cache" ]; then
    ROOT_CACHE=$(sudo du -sh "$CHROOT_DIR/root/.cache" 2>/dev/null | cut -f1)
    if [ "$ROOT_CACHE" != "0" ] && [ "$ROOT_CACHE" != "4.0K" ]; then
        warn "Root cache: $ROOT_CACHE"
    else
        log "Root cache minimal ✓"
    fi
fi

# APT cache
APT_CACHE=$(sudo find "$CHROOT_DIR/var/cache/apt/archives/" -name "*.deb" 2>/dev/null | wc -l)
if [ "$APT_CACHE" -gt 0 ]; then
    warn "APT cache has $APT_CACHE .deb files"
else
    log "APT cache cleaned ✓"
fi

# Logs
LOG_SIZE=$(sudo du -sh "$CHROOT_DIR/var/log" 2>/dev/null | cut -f1)
info "Log directory: $LOG_SIZE"

echo ""

################################################################################
# SYSTEM PACKAGES VERIFICATION
################################################################################

echo "=== SYSTEM PACKAGES ==="

info "Desktop environments:"
for de in mate-desktop-environment kde-plasma-desktop xfce4 cinnamon-desktop-environment; do
    if sudo chroot "$CHROOT_DIR" dpkg -l | grep -q "^ii.*$de" 2>/dev/null; then
        echo "  - $de ✓"
    fi
done

info "Browsers:"
for browser in chromium firefox-esr; do
    if sudo chroot "$CHROOT_DIR" dpkg -l | grep -q "^ii.*$browser" 2>/dev/null; then
        echo "  - $browser ✓"
    fi
done

info "Security tools (sample):"
for tool in nmap metasploit-framework burpsuite wireshark; do
    if sudo chroot "$CHROOT_DIR" dpkg -l | grep -q "^ii.*$tool" 2>/dev/null; then
        echo "  - $tool ✓"
    elif sudo chroot "$CHROOT_DIR" which $tool &>/dev/null; then
        echo "  - $tool ✓ (binary)"
    fi
done

echo ""

################################################################################
# FILE COUNT & STRUCTURE
################################################################################

echo "=== FILESYSTEM STATISTICS ==="

TOTAL_FILES=$(sudo find "$CHROOT_DIR" -type f 2>/dev/null | wc -l)
TOTAL_DIRS=$(sudo find "$CHROOT_DIR" -type d 2>/dev/null | wc -l)
TOTAL_LINKS=$(sudo find "$CHROOT_DIR" -type l 2>/dev/null | wc -l)

info "Total files: $TOTAL_FILES"
info "Total directories: $TOTAL_DIRS"
info "Total symlinks: $TOTAL_LINKS"

echo ""

################################################################################
# LARGE FILES CHECK
################################################################################

echo "=== LARGE FILES (>100MB) ==="
sudo find "$CHROOT_DIR" -type f -size +100M 2>/dev/null -exec ls -lh {} \; | \
    awk '{print $5, $9}' | \
    sed "s|$CHROOT_DIR||" | \
    head -10

echo ""

################################################################################
# FINAL RECOMMENDATIONS
################################################################################

echo "=== FINAL RECOMMENDATIONS ==="

ISSUES=0

# Check for bloat
if [ -d "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/nvidia" ]; then
    error "Remove NVIDIA packages before building"
    ((ISSUES++))
fi

if [ -d "$CHROOT_DIR/root/.cache/pip" ]; then
    error "Clean PIP cache before building"
    ((ISSUES++))
fi

if [ -d "$CHROOT_DIR/opt/tools" ]; then
    error "Remove duplicate /opt/tools directory"
    ((ISSUES++))
fi

if [ "$ISSUES" -eq 0 ]; then
    log "Filesystem ready for ISO build! ✓"
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                  ✓ PRE-BUILD AUDIT PASSED                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Final size: $CHROOT_SIZE"
    echo "Expected ISO: ~5-5.5GB compressed"
    echo ""
    echo "Ready to build ISO with:"
    echo "  sudo /home/diablorain/Syn_OS/scripts/build/enhance-phase6-iso-rebuild.sh \\"
    echo "      /home/diablorain/Syn_OS/build/synos-v1.0/work/chroot"
    exit 0
else
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              ⚠ ISSUES FOUND: $ISSUES                           ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Run cleanup again:"
    echo "  sudo /home/diablorain/Syn_OS/scripts/build/audit-and-cleanup-chroot.sh \\"
    echo "      /home/diablorain/Syn_OS/build/synos-v1.0/work/chroot"
    exit 1
fi
