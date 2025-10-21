#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# SynOS v1.0 - Quick Setup Script
# ═══════════════════════════════════════════════════════════════════════════
#
# This script automates the entire setup process:
# 1. Downloads ParrotOS base ISO
# 2. Verifies all SynOS components
# 3. Runs the remaster build
#
# Usage: sudo ./quick-build-synos.sh
# ═══════════════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[⚠]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root: sudo ./quick-build-synos.sh"
fi

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           SynOS v1.0 - Quick Build Setup                     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORK_DIR="$PROJECT_ROOT/build/parrot-remaster"

log "Project root: $PROJECT_ROOT"

# Step 1: Install dependencies
echo ""
warn "Installing build dependencies..."
apt-get update
apt-get install -y \
    squashfs-tools \
    xorriso \
    genisoimage \
    rsync \
    isolinux \
    syslinux-utils \
    wget \
    curl

log "Dependencies installed!"

# Step 2: Create working directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Step 3: Locate or use existing ParrotOS ISO
echo ""
warn "Looking for ParrotOS ISO..."

# Check common locations for existing ISO
PARROT_ISO=""
if [ -f "$HOME/Downloads/Parrot-security-6.4_amd64.iso" ]; then
    PARROT_ISO="$HOME/Downloads/Parrot-security-6.4_amd64.iso"
    log "Found ParrotOS 6.4 ISO in ~/Downloads"
elif [ -f "$WORK_DIR/Parrot-security-6.4_amd64.iso" ]; then
    PARROT_ISO="$WORK_DIR/Parrot-security-6.4_amd64.iso"
    log "Found ParrotOS 6.4 ISO in work directory"
elif [ -f "$WORK_DIR/Parrot-security-5.3_amd64.iso" ]; then
    PARROT_ISO="$WORK_DIR/Parrot-security-5.3_amd64.iso"
    log "Found ParrotOS 5.3 ISO in work directory"
else
    # Try to download if not found
    PARROT_VERSION="6.4"
    PARROT_ISO_NAME="Parrot-security-${PARROT_VERSION}_amd64.iso"
    PARROT_URL="https://deb.parrot.sh/parrot/iso/${PARROT_VERSION}/${PARROT_ISO_NAME}"

    warn "No existing ISO found. Attempting to download ParrotOS ${PARROT_VERSION}..."
    warn "Download URL: $PARROT_URL"

    if wget -c "$PARROT_URL" -O "$WORK_DIR/$PARROT_ISO_NAME"; then
        PARROT_ISO="$WORK_DIR/$PARROT_ISO_NAME"
        log "ParrotOS ISO downloaded successfully!"
    else
        error "Failed to download ParrotOS ISO. Please manually download from https://www.parrotsec.org/download/ and place in $WORK_DIR/"
    fi
fi

# Verify we have an ISO
if [ ! -f "$PARROT_ISO" ]; then
    error "No ParrotOS ISO found! Please download manually from https://www.parrotsec.org/download/"
fi

log "Using ParrotOS ISO: $PARROT_ISO"

# Step 4: Verify SynOS components
echo ""
warn "Verifying SynOS custom components..."

check_component() {
    if [ ! -e "$1" ]; then
        warn "Missing: $1"
        return 1
    else
        log "Found: $(basename "$1")"
        return 0
    fi
}

MISSING=0

# Source Rust environment if available
if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
elif [ -f "/home/$SUDO_USER/.cargo/env" ]; then
    source "/home/$SUDO_USER/.cargo/env"
fi

# Add cargo to PATH if not already there
if [ -d "/home/$SUDO_USER/.cargo/bin" ] && [[ ":$PATH:" != *":/home/$SUDO_USER/.cargo/bin:"* ]]; then
    export PATH="/home/$SUDO_USER/.cargo/bin:$PATH"
fi

# Check kernel
if ! check_component "$PROJECT_ROOT/src/kernel/target/x86_64-unknown-none/release/kernel"; then
    warn "Building Rust kernel..."
    cd "$PROJECT_ROOT/src/kernel"
    cargo +nightly build --release --bin kernel --features kernel-binary
    MISSING=1
fi

# ALFRED component doesn't exist - skipping
# The AI functionality is provided by other components:
# - core/ai (library)
# - src/ai-engine
# - src/ai-runtime

# Check DEBs
if [ ! -f "$PROJECT_ROOT/linux-distribution/SynOS-Packages/synos-ai-daemon_1.0.0_amd64.deb" ]; then
    warn "SynOS DEBs not found (optional - will be built during remaster if needed)"
fi

# Check consciousness framework (optional)
if [ -d "$PROJECT_ROOT/src/consciousness-framework" ]; then
    log "Found: consciousness-framework"
else
    warn "consciousness-framework not found (optional component)"
fi

# Check AI daemon (optional)
if [ -f "$PROJECT_ROOT/src/ai-engine/ai-daemon.py" ]; then
    log "Found: ai-daemon.py"
elif [ -f "$PROJECT_ROOT/ai-daemon.py" ]; then
    log "Found: ai-daemon.py (root)"
else
    warn "ai-daemon.py not found (optional component)"
fi

if [ $MISSING -eq 1 ]; then
    log "All required components built successfully!"
else
    log "All required components verified!"
fi

# Step 5: Run the remaster build
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Starting SynOS Remaster Build...${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

cd "$PROJECT_ROOT"
"$PROJECT_ROOT/scripts/02-build/build-synos-from-parrot.sh" "$PARROT_ISO"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 QUICK BUILD COMPLETE! 🎉                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Your SynOS ISO is ready!${NC}"
echo ""
echo "Next steps:"
echo "  1. Test in VM: See docs/03-build/PARROT-REMASTER-GUIDE.md"
echo "  2. Create USB: See the guide for dd commands"
echo "  3. Boot and enjoy your custom SynOS!"
echo ""
