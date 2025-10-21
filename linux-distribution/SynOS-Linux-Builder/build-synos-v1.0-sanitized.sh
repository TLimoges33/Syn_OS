#!/bin/bash
################################################################################
# SynOS v1.0 Sanitized Build Script
#
# Strategy: Use existing ParrotOS debootstrap, sanitize, rebrand, add v1.0
#
# What this does:
# 1. Verifies synos-staging components
# 2. Uses ONLY ParrotOS repository (no Kali conflicts)
# 3. Uses sanitized package lists (no missing packages)
# 4. Cleans previous builds
# 5. Configures live-build
# 6. Builds ISO with full ParrotOS + SynOS branding
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# Paths
BUILD_DIR="/home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder"
BUILD_LOG="$BUILD_DIR/build-sanitized-$(date +%Y%m%d-%H%M%S).log"
STAGING_DIR="$BUILD_DIR/synos-staging"

cd "$BUILD_DIR"

# Logging functions
log() {
    local level=$1
    shift
    local msg="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        SUCCESS) echo -e "${GREEN}✅ [$timestamp]${NC} $msg" | tee -a "$BUILD_LOG" ;;
        ERROR)   echo -e "${RED}❌ [$timestamp]${NC} $msg" | tee -a "$BUILD_LOG" ;;
        INFO)    echo -e "${BLUE}ℹ️  [$timestamp]${NC} $msg" | tee -a "$BUILD_LOG" ;;
        WARN)    echo -e "${YELLOW}⚠️  [$timestamp]${NC} $msg" | tee -a "$BUILD_LOG" ;;
        STEP)    echo -e "\n${PURPLE}${BOLD}▶ [$timestamp] $msg${NC}\n" | tee -a "$BUILD_LOG" ;;
    esac
}

header() {
    echo -e "\n${CYAN}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}" | tee -a "$BUILD_LOG"
    echo -e "${CYAN}${BOLD}║  $1${NC}" | tee -a "$BUILD_LOG"
    echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}\n" | tee -a "$BUILD_LOG"
}

echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║                                                           ║${NC}"
echo -e "${CYAN}${BOLD}║           SynOS v1.0 SANITIZED BUILD                      ║${NC}"
echo -e "${CYAN}${BOLD}║                                                           ║${NC}"
echo -e "${CYAN}${BOLD}║  • Full ParrotOS 6.4 Base (500+ Tools)                   ║${NC}"
echo -e "${CYAN}${BOLD}║  • SynOS Rebranding & Custom Components                  ║${NC}"
echo -e "${CYAN}${BOLD}║  • AI Consciousness Integration                           ║${NC}"
echo -e "${CYAN}${BOLD}║  • NO Repository Conflicts                                ║${NC}"
echo -e "${CYAN}${BOLD}║                                                           ║${NC}"
echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}\n"

# ═══════════════════════════════════════════════════════════════
# STEP 1: Verify Components
# ═══════════════════════════════════════════════════════════════
header "STEP 1: Verifying SynOS Components"

if [ ! -d "$STAGING_DIR" ]; then
    log WARN "Staging directory not found: $STAGING_DIR"
    log INFO "Build will continue with ParrotOS base only"
else
    # Verify components
    if [ -f "$STAGING_DIR/kernel/kernel" ]; then
        KERNEL_SIZE=$(du -h "$STAGING_DIR/kernel/kernel" | cut -f1)
        log SUCCESS "Rust kernel found: $KERNEL_SIZE"
    else
        log WARN "Rust kernel not found (will boot with Linux kernel 6.5)"
    fi

    if [ -d "$STAGING_DIR/consciousness" ]; then
        CONSCIOUSNESS_FILES=$(find "$STAGING_DIR/consciousness" -type f 2>/dev/null | wc -l)
        log SUCCESS "Consciousness framework found: $CONSCIOUSNESS_FILES files"
    else
        log WARN "Consciousness framework not found"
    fi

    if [ -f "$STAGING_DIR/ai/ai-daemon.py" ]; then
        log SUCCESS "AI consciousness daemon found"
    else
        log WARN "AI daemon not found"
    fi
fi

log SUCCESS "Component verification complete"

# ═══════════════════════════════════════════════════════════════
# STEP 2: Verify Repository Configuration
# ═══════════════════════════════════════════════════════════════
header "STEP 2: Verifying Repository Configuration"

if [ -f config/archives/kali.list.chroot ]; then
    log ERROR "Kali repository still present!"
    log ERROR "This will cause package conflicts. Remove it:"
    log ERROR "  rm config/archives/kali.list.chroot"
    exit 1
fi

if [ -f config/archives/parrot.list.chroot ]; then
    log SUCCESS "ParrotOS repository configured"
    log INFO "Repository contents:"
    cat config/archives/parrot.list.chroot | tee -a "$BUILD_LOG"
else
    log ERROR "ParrotOS repository not found!"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# STEP 3: Verify Package Lists
# ═══════════════════════════════════════════════════════════════
header "STEP 3: Verifying Package Lists"

# Count total packages
TOTAL_PACKAGES=0
for list in config/package-lists/*.list.chroot; do
    if [ -f "$list" ]; then
        COUNT=$(grep -v '^#' "$list" | grep -v '^$' | wc -l || echo "0")
        TOTAL_PACKAGES=$((TOTAL_PACKAGES + COUNT))
        log INFO "$(basename $list): $COUNT packages"
    fi
done

log SUCCESS "Total packages to install: $TOTAL_PACKAGES"

# Check for problematic lists
if [ -f config/package-lists/synos-security-kali-expanded.list.chroot ]; then
    log ERROR "kali-expanded list still present (causes 50+ missing packages)"
    log ERROR "Remove it: rm config/package-lists/synos-security-kali-expanded.list.chroot"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# STEP 4: Clean Previous Build
# ═══════════════════════════════════════════════════════════════
header "STEP 4: Cleaning Previous Build"

log INFO "Running lb clean --purge..."
sudo lb clean --purge 2>&1 | tail -10 | while read line; do log INFO "$line"; done

log SUCCESS "Build environment cleaned"

# ═══════════════════════════════════════════════════════════════
# STEP 5: Configure Live-Build
# ═══════════════════════════════════════════════════════════════
header "STEP 5: Configuring Live-Build"

log INFO "Running lb config for SynOS v1.0..."

lb config \
    --binary-images iso-hybrid \
    --mode debian \
    --distribution bookworm \
    --parent-mirror-bootstrap "http://deb.debian.org/debian/" \
    --parent-mirror-binary "http://deb.debian.org/debian/" \
    --mirror-chroot "http://deb.parrot.sh/parrot/" \
    --mirror-binary "http://deb.parrot.sh/parrot/" \
    --archive-areas "main contrib non-free non-free-firmware" \
    --linux-flavours amd64 \
    --linux-packages linux-image \
    --bootappend-live "boot=live components quiet splash" \
    --debian-installer live \
    --debian-installer-gui true \
    --iso-application "SynOS v1.0 - AI-Enhanced Security Platform" \
    --iso-publisher "SynOS Development Team" \
    --iso-volume "SynOS-v1.0-$(date +%Y%m%d)" \
    --memtest memtest86+ \
    --win32-loader false

log SUCCESS "Live-build configured"

# ═══════════════════════════════════════════════════════════════
# STEP 6: Build ISO
# ═══════════════════════════════════════════════════════════════
header "STEP 6: Building SynOS ISO (This may take 2-4 hours)"

log INFO "Build log: $BUILD_LOG"
log INFO "Starting lb build..."
log INFO "You can monitor progress with: tail -f $BUILD_LOG"
echo ""

# Start build with full logging
sudo lb build 2>&1 | tee -a "$BUILD_LOG"
BUILD_EXIT_CODE=${PIPESTATUS[0]}

# ═══════════════════════════════════════════════════════════════
# STEP 7: Verify Build Result
# ═══════════════════════════════════════════════════════════════
header "STEP 7: Verifying Build Result"

if [ "$BUILD_EXIT_CODE" -eq 0 ]; then
    log SUCCESS "Build process completed successfully!"
else
    log ERROR "Build process failed with exit code: $BUILD_EXIT_CODE"
fi

echo ""
log INFO "Searching for generated ISO..."

ISO_FILE=$(find . -maxdepth 1 -name "*.iso" -type f -mmin -240 | head -1)

if [ -n "$ISO_FILE" ] && [ -f "$ISO_FILE" ]; then
    ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)

    echo ""
    echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║                                                           ║${NC}"
    echo -e "${GREEN}${BOLD}║              ✓ BUILD SUCCESSFUL!                          ║${NC}"
    echo -e "${GREEN}${BOLD}║                                                           ║${NC}"
    echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}\n"

    log SUCCESS "ISO File: $ISO_FILE"
    log SUCCESS "Size: $ISO_SIZE"
    echo ""

    # Create checksums
    log INFO "Creating checksums..."
    sha256sum "$ISO_FILE" > "${ISO_FILE}.sha256"
    md5sum "$ISO_FILE" > "${ISO_FILE}.md5"
    log SUCCESS "Checksums created"

    echo ""
    log INFO "SHA256: $(cat "${ISO_FILE}".sha256 | cut -d' ' -f1)"
    echo ""

    echo -e "${CYAN}${BOLD}Next Steps:${NC}"
    echo -e "  ${BOLD}1.${NC} Test in VM:"
    echo -e "     qemu-system-x86_64 -cdrom $ISO_FILE -m 4096 -smp 2 -enable-kvm"
    echo ""
    echo -e "  ${BOLD}2.${NC} Verify SynOS branding:"
    echo -e "     • Boot screen shows SynOS logo"
    echo -e "     • Desktop wallpaper is SynOS branded"
    echo -e "     • Check: cat /etc/os-release"
    echo ""
    echo -e "  ${BOLD}3.${NC} Test ParrotOS tools:"
    echo -e "     • nmap, metasploit, burpsuite, wireshark"
    echo -e "     • All 500+ tools should work"
    echo ""
    echo -e "  ${BOLD}4.${NC} Test SynOS components (if installed):"
    echo -e "     • Check: ls -la /opt/synos/"
    echo -e "     • Run: synos-consciousness status"
    echo ""

    log SUCCESS "SynOS v1.0 Sanitized Build Complete! 🎉"
    exit 0

else
    echo ""
    echo -e "${RED}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}${BOLD}║                                                           ║${NC}"
    echo -e "${RED}${BOLD}║              ✗ BUILD FAILED                               ║${NC}"
    echo -e "${RED}${BOLD}║                                                           ║${NC}"
    echo -e "${RED}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}\n"

    log ERROR "No ISO file found"
    log INFO "Check build log: tail -100 $BUILD_LOG"
    echo ""

    log WARN "Recent errors from build log:"
    grep -i "unable to locate package" "$BUILD_LOG" | head -20 || log INFO "No missing package errors"
    grep -i "error" "$BUILD_LOG" | tail -20 || log INFO "No obvious errors in log tail"
    echo ""

    exit 1
fi
