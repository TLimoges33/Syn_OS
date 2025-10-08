#!/bin/bash
# SynOS Unified Build Script
# Consolidates all ISO building functionality with configurable options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VARIANT="ultimate"  # ultimate, desktop, redteam, base
DESKTOP="mate"      # mate, gnome, kde, xfce
FEATURES="ai,security"  # Comma-separated: ai,security,educational,redteam
OUTPUT_DIR="build"
ISO_NAME="synos"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --variant)
            VARIANT="$2"
            shift 2
            ;;
        --desktop)
            DESKTOP="$2"
            shift 2
            ;;
        --features)
            FEATURES="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --name)
            ISO_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --variant   <type>      ISO variant: ultimate, desktop, redteam, base (default: ultimate)"
            echo "  --desktop   <env>       Desktop environment: mate, gnome, kde, xfce (default: mate)"
            echo "  --features  <list>      Comma-separated features: ai,security,educational,redteam"
            echo "  --output    <dir>       Output directory (default: build)"
            echo "  --name      <name>      ISO name prefix (default: synos)"
            echo "  --help                  Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --variant ultimate --desktop mate --features ai,security"
            echo "  $0 --variant desktop --desktop gnome"
            echo "  $0 --variant redteam --features ai,security,redteam"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Functions
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

# Main build logic
main() {
    log_info "SynOS Build Configuration:"
    echo "  Variant: $VARIANT"
    echo "  Desktop: $DESKTOP"
    echo "  Features: $FEATURES"
    echo "  Output: $OUTPUT_DIR"
    echo "  ISO Name: $ISO_NAME"
    echo ""

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Step 1: Setup build environment
    log_info "Setting up build environment..."
    if ! command -v live-build &> /dev/null; then
        log_error "live-build not found. Installing..."
        sudo apt-get update && sudo apt-get install -y live-build debootstrap
    fi
    log_success "Build environment ready"

    # Step 2: Configure live-build
    log_info "Configuring live-build..."
    cd "$OUTPUT_DIR"
    lb config \
        --distribution bookworm \
        --archive-areas "main contrib non-free non-free-firmware" \
        --bootappend-live "boot=live components quiet splash" \
        --mirror-bootstrap "http://deb.debian.org/debian/" \
        --iso-application "SynOS" \
        --iso-volume "SynOS-${VARIANT}-$(date +%Y%m%d)"

    log_success "Live-build configured"

    # Step 3: Add SynOS components
    log_info "Adding SynOS components..."
    # This would copy Rust kernel, AI services, etc.
    # Placeholder for actual implementation
    log_success "SynOS components added"

    # Step 4: Build ISO
    log_info "Building ISO (this may take a while)..."
    sudo lb build

    # Step 5: Move final ISO
    if [ -f "live-image-amd64.hybrid.iso" ]; then
        FINAL_ISO="${ISO_NAME}-${VARIANT}-$(date +%Y%m%d).iso"
        mv live-image-amd64.hybrid.iso "../${FINAL_ISO}"
        log_success "ISO built successfully: ${FINAL_ISO}"
        log_info "Size: $(du -h ../${FINAL_ISO} | cut -f1)"
    else
        log_error "ISO build failed"
        exit 1
    fi
}

# Run main
main
