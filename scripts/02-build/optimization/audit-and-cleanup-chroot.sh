#!/usr/bin/env bash
################################################################################
# SynOS Chroot Audit & Cleanup Script
# Analyzes and cleans up bloat before ISO rebuild
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot}"
PROJECT_ROOT="/home/diablorain/Syn_OS"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; }
section() { echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"; echo -e "${BLUE}║${NC} $*"; echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}\n"; }

################################################################################
# AUDIT CURRENT STATE
################################################################################

audit_chroot() {
    section "Chroot Audit Report"

    log "Current chroot size: $(du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)"
    echo ""

    echo "=== TOP 15 SPACE CONSUMERS ==="
    du -sh "$CHROOT_DIR"/* 2>/dev/null | sort -hr | head -15
    echo ""

    echo "=== PYTHON PACKAGES (Top 15) ==="
    if [ -d "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages" ]; then
        du -sh "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages"/* 2>/dev/null | sort -hr | head -15
    fi
    echo ""

    echo "=== INSTALLED TOOLS VERIFICATION ==="
    log "Security tool categories: $(ls "$CHROOT_DIR/usr/share/desktop-directories/" 2>/dev/null | grep -c synos || echo 0)"
    log "Security tool launchers: $(find "$CHROOT_DIR/usr/share/applications" -name "synos-*.desktop" 2>/dev/null | wc -l)"
    log "GitHub repos in /opt/tools: $(ls -1 "$CHROOT_DIR/opt/tools/github/" 2>/dev/null | wc -l)"
    log "GitHub repos in /opt/github-repos: $(ls -1 "$CHROOT_DIR/opt/github-repos/" 2>/dev/null | wc -l)"

    # Check for demo
    if [ -f "$CHROOT_DIR/usr/local/bin/synos-demo" ]; then
        log "Demo app: INSTALLED ✓"
    else
        warn "Demo app: NOT FOUND"
    fi

    # Check for branding
    if [ -d "$CHROOT_DIR/boot/grub/themes/synos" ]; then
        log "GRUB theme: INSTALLED ✓"
    else
        warn "GRUB theme: NOT FOUND"
    fi

    if [ -d "$CHROOT_DIR/usr/share/plymouth/themes/synos" ]; then
        log "Plymouth theme: INSTALLED ✓"
    else
        warn "Plymouth theme: NOT FOUND"
    fi
    echo ""

    echo "=== PACKAGE CACHE ==="
    if [ -d "$CHROOT_DIR/var/cache/apt/archives" ]; then
        log "APT cache size: $(du -sh "$CHROOT_DIR/var/cache/apt/archives" 2>/dev/null | cut -f1)"
    fi
    if [ -d "$CHROOT_DIR/root/.cache/pip" ]; then
        warn "PIP cache size: $(du -sh "$CHROOT_DIR/root/.cache/pip" 2>/dev/null | cut -f1) ⚠️  BLOAT!"
    fi
    echo ""
}

################################################################################
# IDENTIFY BLOAT
################################################################################

identify_bloat() {
    section "Bloat Analysis"

    echo "=== MAJOR BLOAT SOURCES ==="
    echo ""

    # NVIDIA packages (4.1GB)
    local nvidia_size=$(du -sh "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/nvidia" 2>/dev/null | cut -f1 || echo "0")
    warn "NVIDIA CUDA packages: $nvidia_size"
    echo "    - These are GPU acceleration libraries for PyTorch"
    echo "    - Useful for AI but HUGE and only work with NVIDIA GPUs"
    echo "    - RECOMMENDATION: Remove for general ISO, keep for AI-focused build"
    echo ""

    # PyTorch (1.7GB)
    local torch_size=$(du -sh "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch" 2>/dev/null | cut -f1 || echo "0")
    warn "PyTorch framework: $torch_size"
    echo "    - Deep learning framework"
    echo "    - RECOMMENDATION: Keep if AI features are important"
    echo ""

    # Triton (541MB)
    local triton_size=$(du -sh "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/triton" 2>/dev/null | cut -f1 || echo "0")
    warn "Triton compiler: $triton_size"
    echo "    - GPU programming language for PyTorch"
    echo "    - RECOMMENDATION: Remove with NVIDIA packages"
    echo ""

    # SecLists duplicates (2.5GB x 2 = 5GB total!)
    warn "SecLists DUPLICATED in two locations (5GB total!):"
    echo "    - /opt/tools/github/SecLists: $(du -sh "$CHROOT_DIR/opt/tools/github/SecLists" 2>/dev/null | cut -f1 || echo "N/A")"
    echo "    - /opt/github-repos/SecLists: $(du -sh "$CHROOT_DIR/opt/github-repos/SecLists" 2>/dev/null | cut -f1 || echo "N/A")"
    echo "    - RECOMMENDATION: Remove one copy (keep /opt/github-repos)"
    echo ""

    # Other duplicates
    warn "Multiple tools DUPLICATED in /opt/tools AND /opt/github-repos:"
    for tool in BloodHound impacket Responder CrackMapExec nuclei-templates PEASS-ng PayloadsAllTheThings LinEnum; do
        if [ -d "$CHROOT_DIR/opt/tools/github/$tool" ] && [ -d "$CHROOT_DIR/opt/github-repos/$tool" ]; then
            local size1=$(du -sh "$CHROOT_DIR/opt/tools/github/$tool" 2>/dev/null | cut -f1 || echo "?")
            local size2=$(du -sh "$CHROOT_DIR/opt/github-repos/$tool" 2>/dev/null | cut -f1 || echo "?")
            echo "    - $tool: $size1 + $size2"
        fi
    done
    echo "    - RECOMMENDATION: Remove /opt/tools/github completely (keep /opt/github-repos)"
    echo ""

    # LibreOffice
    local libreoffice_size=$(du -sh "$CHROOT_DIR/usr/lib/libreoffice" 2>/dev/null | cut -f1 || echo "0")
    if [ "$libreoffice_size" != "0" ]; then
        warn "LibreOffice: $libreoffice_size"
        echo "    - Full office suite"
        echo "    - RECOMMENDATION: Remove if not needed for security work"
        echo ""
    fi

    echo "=== ESTIMATED SAVINGS ==="
    echo "  • Remove NVIDIA packages: ~4.1GB"
    echo "  • Remove Triton: ~541MB"
    echo "  • Remove /opt/tools/github (duplicates): ~3.4GB"
    echo "  • Remove PIP cache (/root/.cache/pip): ~3.9GB"
    echo "  • Clean APT package cache: ~100-500MB"
    echo "  • Remove LibreOffice (optional): ~251MB"
    echo "  • Keep PyTorch for AI features: 0GB saved"
    echo ""
    echo "  TOTAL POTENTIAL SAVINGS: ~12-13GB"
    echo "  RESULT: ~12GB final size (compressed to ~4-5GB ISO)"
    echo ""
}

################################################################################
# CLEANUP OPTIONS
################################################################################

cleanup_aggressive() {
    section "Aggressive Cleanup (Remove NVIDIA + Duplicates + Caches)"

    log "Removing NVIDIA CUDA packages (4.1GB)..."
    rm -rf "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/nvidia" 2>/dev/null || true

    log "Removing Triton compiler (541MB)..."
    rm -rf "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/triton" 2>/dev/null || true

    log "Removing duplicate GitHub repos from /opt/tools (3.4GB)..."
    rm -rf "$CHROOT_DIR/opt/tools" 2>/dev/null || true

    log "Cleaning PIP cache (3.9GB)..."
    rm -rf "$CHROOT_DIR/root/.cache/pip" 2>/dev/null || true

    log "Cleaning APT package cache..."
    rm -rf "$CHROOT_DIR/var/cache/apt/archives"/*.deb 2>/dev/null || true

    log "Cleaning logs..."
    find "$CHROOT_DIR/var/log" -type f -name "*.log" -exec truncate -s 0 {} \; 2>/dev/null || true
    find "$CHROOT_DIR/var/log" -type f -name "*.gz" -delete 2>/dev/null || true

    log "Cleaning temporary files..."
    rm -rf "$CHROOT_DIR/tmp"/* 2>/dev/null || true
    rm -rf "$CHROOT_DIR/var/tmp"/* 2>/dev/null || true

    log "New size: $(du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)"
}

cleanup_moderate() {
    section "Moderate Cleanup (Remove Duplicates + Caches)"

    log "Removing duplicate GitHub repos from /opt/tools (3.4GB)..."
    rm -rf "$CHROOT_DIR/opt/tools" 2>/dev/null || true

    log "Cleaning PIP cache (3.9GB)..."
    rm -rf "$CHROOT_DIR/root/.cache/pip" 2>/dev/null || true

    log "Cleaning APT package cache..."
    rm -rf "$CHROOT_DIR/var/cache/apt/archives"/*.deb 2>/dev/null || true

    log "Cleaning logs..."
    find "$CHROOT_DIR/var/log" -type f -name "*.log" -exec truncate -s 0 {} \; 2>/dev/null || true
    find "$CHROOT_DIR/var/log" -type f -name "*.gz" -delete 2>/dev/null || true

    log "Cleaning temporary files..."
    rm -rf "$CHROOT_DIR/tmp"/* 2>/dev/null || true
    rm -rf "$CHROOT_DIR/var/tmp"/* 2>/dev/null || true

    log "New size: $(du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)"
}

cleanup_minimal() {
    section "Minimal Cleanup (Caches Only)"

    log "Cleaning PIP cache (3.9GB)..."
    rm -rf "$CHROOT_DIR/root/.cache/pip" 2>/dev/null || true

    log "Cleaning APT package cache..."
    rm -rf "$CHROOT_DIR/var/cache/apt/archives"/*.deb 2>/dev/null || true

    log "Cleaning logs..."
    find "$CHROOT_DIR/var/log" -type f -name "*.log" -exec truncate -s 0 {} \; 2>/dev/null || true
    find "$CHROOT_DIR/var/log" -type f -name "*.gz" -delete 2>/dev/null || true

    log "Cleaning temporary files..."
    rm -rf "$CHROOT_DIR/tmp"/* 2>/dev/null || true
    rm -rf "$CHROOT_DIR/var/tmp"/* 2>/dev/null || true

    log "New size: $(du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)"
}

################################################################################
# MAIN
################################################################################

if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root"
    exit 1
fi

if [ ! -d "$CHROOT_DIR" ]; then
    error "Chroot directory not found: $CHROOT_DIR"
    exit 1
fi

# Always run audit first
audit_chroot
identify_bloat

# Ask what to do
echo ""
echo "=== CLEANUP OPTIONS ==="
echo ""
echo "  1) AGGRESSIVE - Remove NVIDIA, Triton, duplicates, caches (~12GB saved, ~13GB final)"
echo "     Best for: General security ISO without GPU AI features"
echo "     Keeps: PyTorch, transformers, all tools, menu, branding"
echo ""
echo "  2) MODERATE - Remove duplicates + caches (~7.5GB saved, ~17GB final)"
echo "     Best for: Keep ALL AI features, remove wasteful duplicates"
echo "     Keeps: NVIDIA, PyTorch, transformers, all tools"
echo ""
echo "  3) MINIMAL - Clean caches only (~4GB saved, ~21GB final)"
echo "     Best for: Keep EVERYTHING, just clean temporary files"
echo "     Warning: Large ISO (~7-8GB compressed)"
echo ""
echo "  4) AUDIT ONLY - Just show report, don't clean anything"
echo ""
read -p "Choose cleanup level (1-4): " choice

case "$choice" in
    1)
        cleanup_aggressive
        ;;
    2)
        cleanup_moderate
        ;;
    3)
        cleanup_minimal
        ;;
    4)
        log "Audit complete. No cleanup performed."
        ;;
    *)
        error "Invalid choice"
        exit 1
        ;;
esac

section "Cleanup Complete!"
log "Final chroot size: $(du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)"
log "Ready for ISO rebuild with Phase 6"
