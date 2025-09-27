#!/bin/bash

# SynOS ParrotOS Fork Setup Script
# Creates your custom operating system development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
FORK_NAME="${1:-SynOS-Custom}"
FORK_DIR="/home/diablorain/${FORK_NAME}"
PARROT_VERSION="6.4"
BUILD_DATE=$(date +%Y%m%d)

print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║         🍴 ParrotOS Fork Development Setup 🍴               ║"
    echo "║                                                              ║"
    echo "║     Create Your Own Operating System Based on ParrotOS      ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    log_info "Checking prerequisites for fork development..."
    
    # Check if running as regular user
    if [[ $EUID -eq 0 ]]; then
        log_error "Don't run this script as root"
        exit 1
    fi
    
    # Check required tools
    local required_tools=("git" "wget" "curl" "python3" "build-essential")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1 && ! dpkg -l | grep -q "^ii.*$tool "; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_warning "Missing tools: ${missing_tools[*]}"
        log_info "Installing required tools..."
        sudo apt update
        sudo apt install -y "${missing_tools[@]}"
    fi
    
    # Check available space (need at least 20GB)
    local available_gb=$(df /home | awk 'NR==2{printf "%.0f", $4/1024/1024}')
    if [[ $available_gb -lt 20 ]]; then
        log_warning "Low disk space: ${available_gb}GB available, 20GB+ recommended"
    fi
    
    log_success "Prerequisites check completed"
}

create_fork_structure() {
    log_info "Creating fork directory structure..."
    
    # Create main directories
    local directories=(
        "$FORK_DIR"
        "$FORK_DIR/source"
        "$FORK_DIR/source/packages"
        "$FORK_DIR/source/patches"
        "$FORK_DIR/source/artwork"
        "$FORK_DIR/build"
        "$FORK_DIR/build/config"
        "$FORK_DIR/build/scripts"
        "$FORK_DIR/build/hooks"
        "$FORK_DIR/packages"
        "$FORK_DIR/packages/custom"
        "$FORK_DIR/packages/modified"
        "$FORK_DIR/packages/repository"
        "$FORK_DIR/iso"
        "$FORK_DIR/iso/output"
        "$FORK_DIR/iso/testing"
        "$FORK_DIR/documentation"
        "$FORK_DIR/tools"
        "$FORK_DIR/synos-integration"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_success "Created: $dir"
    done
    
    # Copy SynOS consciousness system to fork
    if [[ -d "/home/diablorain/Syn_OS/src/consciousness" ]]; then
        cp -r "/home/diablorain/Syn_OS/src/consciousness" "$FORK_DIR/synos-integration/"
        log_success "Copied SynOS consciousness system to fork"
    fi
    
    # Copy ParrotOS analysis data
    if [[ -f "/home/diablorain/Syn_OS/src/consciousness/parrot_tool_integration.py" ]]; then
        cp "/home/diablorain/Syn_OS/src/consciousness/parrot_tool_integration.py" "$FORK_DIR/synos-integration/"
        log_success "Copied ParrotOS tool integration data"
    fi
}

create_fork_metadata() {
    log_info "Creating fork metadata and configuration..."
    
    # Fork information file
    cat > "$FORK_DIR/FORK_INFO.json" << EOF
{
    "fork_name": "$FORK_NAME",
    "base_system": "ParrotOS $PARROT_VERSION Security Edition",
    "creation_date": "$(date -I)",
    "creator": "$(whoami)",
    "synos_integration": true,
    "description": "Custom security-focused operating system based on ParrotOS with SynOS AI consciousness",
    "version": "1.0.0-dev",
    "build_date": "$BUILD_DATE",
    "features": [
        "ParrotOS security tools",
        "SynOS AI consciousness",
        "Educational framework",
        "Custom branding",
        "Enhanced privacy"
    ],
    "target_audience": [
        "Security professionals",
        "Students",
        "Researchers",
        "Privacy advocates"
    ]
}
EOF
    
    # Build configuration
    cat > "$FORK_DIR/build/config/build.conf" << EOF
# $FORK_NAME Build Configuration

# Base system
DEBIAN_SUITE="bookworm"
PARROT_MIRROR="http://deb.parrotsec.org/parrot"
DEBIAN_MIRROR="http://deb.debian.org/debian"

# Fork details
FORK_NAME="$FORK_NAME"
FORK_VERSION="1.0.0-dev"
FORK_CODENAME="Genesis"

# ISO configuration
ISO_VOLUME_ID="${FORK_NAME}_${BUILD_DATE}"
ISO_PUBLISHER="SynOS Development Team"
ISO_APPLICATION="${FORK_NAME} Security Operating System"

# Desktop environment
DESKTOP_ENVIRONMENT="mate"
DISPLAY_MANAGER="lightdm"

# Security features
ENABLE_ENCRYPTION=true
ENABLE_ANONYMITY=true
ENABLE_FORENSICS=true
ENABLE_CONSCIOUSNESS=true

# Package selection
INCLUDE_PARROT_TOOLS=true
INCLUDE_SYNOS_CONSCIOUSNESS=true
INCLUDE_EDUCATIONAL_MODULES=true
INCLUDE_CUSTOM_BRANDING=true
EOF
    
    log_success "Fork metadata created"
}

create_package_lists() {
    log_info "Creating package selection lists..."
    
    # Essential packages
    cat > "$FORK_DIR/packages/essential.list" << 'EOF'
# Essential system packages
systemd
systemd-sysv
network-manager
sudo
openssh-client
openssh-server
curl
wget
git
vim
nano
htop
tree
unzip
zip
tar
gzip
EOF
    
    # Security tools (from our ParrotOS analysis)
    cat > "$FORK_DIR/packages/security-tools.list" << 'EOF'
# Network security tools
nmap
netdiscover
masscan
wireshark
tcpdump
ettercap-text-only

# Web application security
burpsuite
zaproxy
sqlmap
nikto
dirb
gobuster

# Wireless security
aircrack-ng
kismet
reaver
wifite

# Password attacks
john
hashcat
hydra
medusa

# Forensics
autopsy
volatility
sleuthkit
binwalk
foremost

# Exploitation tools
metasploit-framework
beef-xss
set

# Privacy tools
tor
proxychains4
bleachbit
mat2

# Reverse engineering
radare2
ghidra
gdb
EOF
    
    # Desktop environment
    cat > "$FORK_DIR/packages/desktop.list" << 'EOF'
# MATE Desktop Environment
mate-desktop-environment-core
mate-terminal
mate-system-monitor
mate-calc
mate-screenshot
lightdm
lightdm-gtk-greeter

# Applications
firefox-esr
thunderbird
libreoffice
file-roller
gvfs-backends

# Multimedia
vlc
audacity
gimp

# Development
code
python3
python3-pip
nodejs
npm
EOF
    
    log_success "Package lists created"
}

create_build_scripts() {
    log_info "Creating build automation scripts..."
    
    # Main build script
    cat > "$FORK_DIR/build/scripts/build-fork.sh" << 'EOF'
#!/bin/bash

# Fork Build Script
# Builds the custom operating system ISO

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORK_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$FORK_DIR/build/config/build.conf"

# Load configuration
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    echo "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

echo "Building $FORK_NAME v$FORK_VERSION..."

# Create build environment
sudo lb config \
    --distribution "$DEBIAN_SUITE" \
    --archive-areas "main contrib non-free non-free-firmware" \
    --debian-installer false \
    --bootappend-live "boot=live components quiet splash" \
    --memtest none \
    --iso-volume "$ISO_VOLUME_ID" \
    --iso-publisher "$ISO_PUBLISHER" \
    --iso-application "$ISO_APPLICATION"

# Add package lists
cp "$FORK_DIR/packages"/*.list config/package-lists/

# Add SynOS consciousness
if [[ "$ENABLE_CONSCIOUSNESS" == "true" && -d "$FORK_DIR/synos-integration" ]]; then
    mkdir -p config/includes.chroot/opt/synos
    cp -r "$FORK_DIR/synos-integration"/* config/includes.chroot/opt/synos/
fi

# Build ISO
sudo lb build

# Move ISO to output directory
if [[ -f *.iso ]]; then
    mv *.iso "$FORK_DIR/iso/output/"
    echo "Build completed successfully!"
else
    echo "Build failed - no ISO generated"
    exit 1
fi
EOF
    
    chmod +x "$FORK_DIR/build/scripts/build-fork.sh"
    
    # Package customization script
    cat > "$FORK_DIR/build/scripts/customize-packages.sh" << 'EOF'
#!/bin/bash

# Package Customization Script
# Modifies packages for the fork

set -e

FORK_DIR="$(dirname "$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")")"

echo "Customizing packages for fork..."

# Create custom consciousness package
create_consciousness_package() {
    local pkg_dir="$FORK_DIR/packages/custom/synos-consciousness"
    mkdir -p "$pkg_dir/DEBIAN"
    mkdir -p "$pkg_dir/opt/synos"
    mkdir -p "$pkg_dir/etc/systemd/system"
    
    # Copy consciousness files
    cp -r "$FORK_DIR/synos-integration/consciousness"/* "$pkg_dir/opt/synos/"
    
    # Create package control file
    cat > "$pkg_dir/DEBIAN/control" << 'EOL'
Package: synos-consciousness
Version: 1.0.0
Section: education
Priority: optional
Architecture: all
Depends: python3, python3-pip
Maintainer: SynOS Development Team
Description: SynOS AI Consciousness System
 Provides AI-powered educational consciousness interface
 for security learning and system interaction.
EOL
    
    # Create systemd service
    cat > "$pkg_dir/etc/systemd/system/synos-consciousness.service" << 'EOL'
[Unit]
Description=SynOS Consciousness Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/opt/synos/consciousness-service.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL
    
    # Build package
    dpkg-deb --build "$pkg_dir" "$FORK_DIR/packages/repository/"
}

create_consciousness_package
echo "Package customization completed"
EOF
    
    chmod +x "$FORK_DIR/build/scripts/customize-packages.sh"
    
    log_success "Build scripts created"
}

create_branding() {
    log_info "Creating custom branding and artwork..."
    
    # Create branding configuration
    cat > "$FORK_DIR/source/artwork/branding.conf" << EOF
# $FORK_NAME Branding Configuration

# Colors (based on SynOS consciousness theme)
PRIMARY_COLOR="#39ff14"      # Matrix green
SECONDARY_COLOR="#0d1117"    # Dark background
ACCENT_COLOR="#238636"       # GitHub green
TEXT_COLOR="#ffffff"         # White text

# Boot splash
BOOT_SPLASH_TITLE="$FORK_NAME"
BOOT_SPLASH_SUBTITLE="AI-Enhanced Security Operating System"

# Desktop theme
GTK_THEME_NAME="${FORK_NAME}-Dark"
ICON_THEME_NAME="${FORK_NAME}-Icons"
WALLPAPER_NAME="${FORK_NAME}-Default"

# System info
OS_NAME="$FORK_NAME"
OS_VERSION="1.0.0-dev"
OS_CODENAME="Genesis"
OS_ID="${FORK_NAME,,}"
EOF
    
    # Create simple ASCII art logo
    cat > "$FORK_DIR/source/artwork/logo.txt" << EOF
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                        $FORK_NAME                            ║
║                                                              ║
║        🧠 AI-Enhanced Security Operating System 🧠          ║
║                                                              ║
║     Based on ParrotOS • Enhanced with SynOS Consciousness   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    
    # Create desktop entry for consciousness
    cat > "$FORK_DIR/source/artwork/synos-consciousness.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$FORK_NAME Consciousness
Comment=AI-Enhanced Security Learning Platform
Exec=firefox http://localhost:8080
Icon=applications-development
Terminal=false
Categories=Education;Security;Development;
EOF
    
    log_success "Branding materials created"
}

create_documentation() {
    log_info "Creating fork documentation..."
    
    # README for the fork
    cat > "$FORK_DIR/README.md" << EOF
# $FORK_NAME

An AI-enhanced security operating system based on ParrotOS with SynOS consciousness integration.

## Features

- **ParrotOS Security Tools**: Complete collection of security and penetration testing tools
- **SynOS AI Consciousness**: Intelligent learning and assistance system
- **Educational Framework**: Structured security education with progress tracking
- **Custom Branding**: Unique visual identity and user experience
- **Privacy Enhanced**: Built-in anonymity and privacy protection tools

## Quick Start

1. **Download**: Get the latest ISO from releases
2. **Boot**: Create USB or boot in VM
3. **Explore**: Access consciousness dashboard at localhost:8080
4. **Learn**: Follow guided security education modules

## Development

This fork is built using:
- ParrotOS $PARROT_VERSION as base system
- SynOS consciousness framework
- Custom package selection and branding
- Educational enhancement modules

## Building

\`\`\`bash
cd build/scripts
sudo ./build-fork.sh
\`\`\`

## Support

- Documentation: See docs/ directory
- Issues: Report on GitHub
- Community: Join our forums

## License

Based on ParrotOS (GPL) with SynOS enhancements.
EOF
    
    # Build instructions
    cat > "$FORK_DIR/documentation/BUILD_INSTRUCTIONS.md" << EOF
# $FORK_NAME Build Instructions

## Prerequisites

- Debian/Ubuntu system with 20GB+ free space
- Root access for build tools
- Internet connection for package downloads

## Build Process

1. **Setup Environment**:
   \`\`\`bash
   sudo apt update
   sudo apt install live-build debootstrap
   \`\`\`

2. **Configure Build**:
   \`\`\`bash
   cd build/config
   # Edit build.conf as needed
   \`\`\`

3. **Customize Packages**:
   \`\`\`bash
   cd build/scripts
   ./customize-packages.sh
   \`\`\`

4. **Build ISO**:
   \`\`\`bash
   ./build-fork.sh
   \`\`\`

5. **Test Result**:
   \`\`\`bash
   # ISO will be in iso/output/
   qemu-system-x86_64 -m 4096 -cdrom iso/output/*.iso
   \`\`\`

## Customization

- **Packages**: Edit files in packages/ directory
- **Branding**: Modify source/artwork/ files
- **Configuration**: Update build/config/build.conf
- **Scripts**: Add custom scripts to build/hooks/

## Troubleshooting

- Check build logs in build/ directory
- Ensure sufficient disk space
- Verify package dependencies
- Test in clean environment
EOF
    
    log_success "Documentation created"
}

setup_version_control() {
    log_info "Setting up version control..."
    
    cd "$FORK_DIR"
    
    # Initialize git repository
    git init
    
    # Create .gitignore
    cat > .gitignore << 'EOF'
# Build artifacts
build/auto/
build/binary/
build/cache/
build/chroot/
build/.build/
*.iso
*.log

# Temporary files
*.tmp
*.temp
*~

# System files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo
EOF
    
    # Create initial commit
    git add .
    git commit -m "Initial fork setup for $FORK_NAME

- Created directory structure
- Added build scripts and configuration
- Integrated SynOS consciousness system
- Set up package lists and branding
- Added documentation and version control"
    
    log_success "Version control initialized"
}

show_completion_summary() {
    local setup_time=$(($(date +%s) - SETUP_START))
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}║            🎉 Fork Setup Complete! 🎉                       ║${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📁 Fork Location:${NC} $FORK_DIR"
    echo -e "${CYAN}🕒 Setup Time:${NC} ${setup_time} seconds"
    echo ""
    echo -e "${CYAN}📋 What's Been Created:${NC}"
    echo "  ✅ Complete directory structure"
    echo "  ✅ Build scripts and configuration"
    echo "  ✅ Package lists (security tools from ParrotOS analysis)"
    echo "  ✅ SynOS consciousness integration"
    echo "  ✅ Custom branding and artwork"
    echo "  ✅ Documentation and README"
    echo "  ✅ Git version control"
    echo ""
    echo -e "${CYAN}🚀 Next Steps:${NC}"
    echo "  1. cd $FORK_DIR"
    echo "  2. Review and customize build/config/build.conf"
    echo "  3. Modify branding in source/artwork/"
    echo "  4. Run: sudo build/scripts/build-fork.sh"
    echo "  5. Test your custom OS ISO!"
    echo ""
    echo -e "${CYAN}🎯 Features Included:${NC}"
    echo "  • ParrotOS $PARROT_VERSION security tools"
    echo "  • SynOS AI consciousness system"
    echo "  • Educational framework integration"
    echo "  • Custom branding and identity"
    echo "  • Automated build system"
    echo ""
    echo -e "${GREEN}✨ Your custom operating system fork is ready for development!${NC}"
}

main() {
    SETUP_START=$(date +%s)
    
    print_banner
    
    if [[ -z "$1" ]]; then
        echo -e "${YELLOW}Usage: $0 <fork-name>${NC}"
        echo "Example: $0 MySecurityOS"
        exit 1
    fi
    
    log_info "Setting up fork: $FORK_NAME"
    echo ""
    
    check_prerequisites
    create_fork_structure
    create_fork_metadata
    create_package_lists
    create_build_scripts
    create_branding
    create_documentation
    setup_version_control
    
    show_completion_summary
}

# Run main function with arguments
main "$@"
