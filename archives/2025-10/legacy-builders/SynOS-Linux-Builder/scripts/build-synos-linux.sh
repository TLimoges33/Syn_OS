#!/bin/bash

# SynOS Linux Distribution Master Builder
# Complete build process for SynOS Linux distribution

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BUILD_DIR="$PROJECT_ROOT/build"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    local timestamp=$(date '+%H:%M:%S')

    case $status in
        "success") echo -e "${GREEN}✅ [$timestamp]${NC} $message" ;;
        "error") echo -e "${RED}❌ [$timestamp]${NC} $message" ;;
        "info") echo -e "${BLUE}ℹ️  [$timestamp]${NC} $message" ;;
        "warning") echo -e "${YELLOW}⚠️  [$timestamp]${NC} $message" ;;
        "header") echo -e "${CYAN}🚀 $message${NC}" ;;
        "section") echo -e "${PURPLE}🔧 [$timestamp]${NC} $message" ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    print_status "section" "Checking prerequisites..."

    # Check if running as regular user (not root)
    if [[ $EUID -eq 0 ]]; then
        print_status "error" "Do not run this script as root. Live-build will use sudo when needed."
        exit 1
    fi

    # Check for required commands
    local missing_tools=()

    if ! command -v lb &>/dev/null; then
        missing_tools+=("live-build")
    fi

    if ! command -v debootstrap &>/dev/null; then
        missing_tools+=("debootstrap")
    fi

    if ! command -v mksquashfs &>/dev/null; then
        missing_tools+=("squashfs-tools")
    fi

    if ! command -v xorriso &>/dev/null; then
        missing_tools+=("xorriso")
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        print_status "warning" "Missing tools: ${missing_tools[*]}"
        print_status "info" "Run: $SCRIPTS_DIR/setup-build-environment.sh"
        return 1
    fi

    print_status "success" "All prerequisites satisfied"
    return 0
}

# Function to display build options
show_build_options() {
    echo ""
    print_status "header" "SynOS Linux Distribution Builder"
    print_status "header" "Select build configuration:"
    echo ""
    echo "1) 🚀 Quick Test Build (Minimal, ~2GB, 30 min)"
    echo "   - Basic Debian + MATE + SynOS AI"
    echo "   - Essential security tools only"
    echo "   - Good for testing and development"
    echo ""
    echo "2) 🎯 Standard Build (Balanced, ~4GB, 60 min)"
    echo "   - Full desktop environment"
    echo "   - 50+ security tools"
    echo "   - Complete educational framework"
    echo ""
    echo "3) 🏆 Full Build (Complete, ~6GB, 90 min)"
    echo "   - All ParrotOS security tools"
    echo "   - Complete AI consciousness"
    echo "   - All branding and customizations"
    echo ""
    echo "4) 🔧 Custom Configuration"
    echo "   - Manual configuration selection"
    echo ""
    echo "5) 📋 Show Current Configuration"
    echo ""
    echo "6) 🧹 Clean Build Environment"
    echo ""
    echo "0) Exit"
    echo ""
}

# Function for quick test build
quick_test_build() {
    print_status "section" "Configuring Quick Test Build..."

    # Run base configuration
    $SCRIPTS_DIR/build-synos-base.sh

    cd "$BUILD_DIR"

    # Modify package lists for minimal build
    cat > config/package-lists/synos-security.list.chroot << 'EOF'
# Minimal Security Tools for Testing
nmap
wireshark-qt
curl
wget
netcat-traditional
openssh-client
EOF

    # Remove heavy packages
    echo "" > config/package-lists/synos-heavy.list.chroot

    print_status "success" "Quick test build configured"
}

# Function for standard build
standard_build() {
    print_status "section" "Configuring Standard Build..."

    # Run all configuration scripts
    $SCRIPTS_DIR/build-synos-base.sh
    $SCRIPTS_DIR/copy-synos-components.sh
    $SCRIPTS_DIR/create-branding-assets.sh

    print_status "success" "Standard build configured"
}

# Function for full build
full_build() {
    print_status "section" "Configuring Full Build..."

    # Run all configuration scripts
    $SCRIPTS_DIR/build-synos-base.sh
    $SCRIPTS_DIR/copy-synos-components.sh
    $SCRIPTS_DIR/create-branding-assets.sh

    cd "$BUILD_DIR"

    # Add additional security tools
    cat >> config/package-lists/synos-security.list.chroot << 'EOF'

# Additional Security Tools for Full Build
beef-xss
kismet
reaver
wpscan
armitage
zaproxy
maltego
theharvester
dnsrecon
fierce
sublist3r
amass
ffuf
wfuzz
commix
nuclei
subfinder
httpx
gau
waybackurls
feroxbuster
EOF

    # Add forensics tools
    cat > config/package-lists/synos-forensics.list.chroot << 'EOF'
# Digital Forensics Tools
autopsy
sleuthkit
bulk-extractor
scalpel
safecopy
guymager
dc3dd
ewf-tools
afflib-tools
libewf-utils
EOF

    print_status "success" "Full build configured"
}

# Function to execute the build
execute_build() {
    local build_type=$1

    print_status "header" "Starting $build_type build process..."

    cd "$BUILD_DIR"

    # Check available disk space
    local available_space=$(df . | awk 'NR==2 {print $4}')
    local required_space=8000000  # 8GB in KB

    if [[ $available_space -lt $required_space ]]; then
        print_status "warning" "Low disk space. Required: 8GB, Available: $(($available_space/1024/1024))GB"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "info" "Build cancelled"
            return 1
        fi
    fi

    # Start the build
    print_status "section" "Executing live-build..."

    # Create build log directory
    mkdir -p logs

    # Execute build with logging
    if sudo lb build 2>&1 | tee "logs/build-$(date +%Y%m%d-%H%M%S).log"; then
        print_status "success" "Build completed successfully!"

        # Check if ISO was created
        if [[ -f "live-image-amd64.hybrid.iso" ]]; then
            local iso_size=$(du -h live-image-amd64.hybrid.iso | cut -f1)
            local iso_name="synos-linux-$(date +%Y%m%d)-amd64.iso"

            # Move and rename ISO
            mv live-image-amd64.hybrid.iso "$iso_name"

            print_status "success" "ISO created: $iso_name (Size: $iso_size)"
            print_status "info" "Location: $BUILD_DIR/$iso_name"

            # Generate checksums
            sha256sum "$iso_name" > "$iso_name.sha256"
            md5sum "$iso_name" > "$iso_name.md5"

            print_status "success" "Checksums generated"

            # Test command
            echo ""
            print_status "info" "Test with QEMU:"
            print_status "info" "qemu-system-x86_64 -m 2048 -cdrom '$BUILD_DIR/$iso_name'"
            echo ""

        else
            print_status "error" "ISO file not found after build"
            return 1
        fi

    else
        print_status "error" "Build failed. Check logs in $BUILD_DIR/logs/"
        return 1
    fi
}

# Function to clean build environment
clean_build() {
    print_status "section" "Cleaning build environment..."

    if [[ -d "$BUILD_DIR" ]]; then
        cd "$BUILD_DIR"
        sudo lb clean --purge 2>/dev/null || true
        cd "$PROJECT_ROOT"
        rm -rf "$BUILD_DIR"
        print_status "success" "Build environment cleaned"
    else
        print_status "info" "Build environment already clean"
    fi
}

# Function to show current configuration
show_configuration() {
    print_status "section" "Current build configuration:"

    if [[ -f "$BUILD_DIR/config/lb" ]]; then
        echo ""
        echo "📋 Live-build Configuration:"
        grep -E "^LB_" "$BUILD_DIR/config/lb" | head -10
        echo ""

        if [[ -f "$BUILD_DIR/config/package-lists/synos-base.list.chroot" ]]; then
            local package_count=$(wc -l < "$BUILD_DIR/config/package-lists/synos-base.list.chroot")
            echo "📦 Base Packages: $package_count configured"
        fi

        if [[ -f "$BUILD_DIR/config/package-lists/synos-security.list.chroot" ]]; then
            local security_count=$(grep -v '^#' "$BUILD_DIR/config/package-lists/synos-security.list.chroot" | grep -v '^$' | wc -l)
            echo "🛡️ Security Tools: $security_count configured"
        fi

        if [[ -d "$BUILD_DIR/config/includes.chroot/opt/synos" ]]; then
            echo "🧠 SynOS Components: ✅ Configured"
        else
            echo "🧠 SynOS Components: ❌ Not configured"
        fi

        echo ""
    else
        print_status "warning" "No build configuration found"
        print_status "info" "Run a configuration option first"
    fi
}

# Main menu loop
main() {
    # Initial header
    clear
    echo ""
    print_status "header" "======================================================="
    print_status "header" "    SynOS Linux Distribution Builder v1.0"
    print_status "header" "    Creating AI-Enhanced Cybersecurity Distribution"
    print_status "header" "======================================================="
    echo ""

    # Check prerequisites once
    if ! check_prerequisites; then
        print_status "error" "Prerequisites not met. Please install required tools first."
        exit 1
    fi

    while true; do
        show_build_options

        read -p "Select option [1-6,0]: " choice

        case $choice in
            1)
                print_status "info" "Starting Quick Test Build..."
                quick_test_build && execute_build "Quick Test"
                ;;
            2)
                print_status "info" "Starting Standard Build..."
                standard_build && execute_build "Standard"
                ;;
            3)
                print_status "info" "Starting Full Build..."
                full_build && execute_build "Full"
                ;;
            4)
                print_status "info" "Custom configuration mode not implemented yet"
                print_status "info" "Use individual scripts in $SCRIPTS_DIR/"
                ;;
            5)
                show_configuration
                ;;
            6)
                clean_build
                ;;
            0)
                print_status "info" "Exiting SynOS Linux Builder"
                exit 0
                ;;
            *)
                print_status "warning" "Invalid option. Please select 1-6 or 0."
                ;;
        esac

        echo ""
        read -p "Press Enter to continue..." -r
        clear
    done
}

# Script execution starts here
main "$@"