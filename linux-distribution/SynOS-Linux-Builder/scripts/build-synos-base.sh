#!/bin/bash

# SynOS Linux Distribution Builder
# Creates a custom Linux distribution based on ParrotOS with SynOS AI integration

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
SYNOS_ROOT="/home/diablorain/Syn_OS"

# Colors for output
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

echo ""
print_status "header" "======================================================="
print_status "header" "    SynOS Linux Distribution Builder v1.0"
print_status "header" "    Building AI-Enhanced Cybersecurity Distribution"
print_status "header" "======================================================="
echo ""

# Clean and prepare build directory
print_status "section" "Preparing build environment..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

print_status "success" "Build directory prepared: $BUILD_DIR"

# Initialize live-build configuration
print_status "section" "Initializing live-build configuration..."

lb config \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --architectures amd64 \
    --linux-flavours amd64 \
    --debian-installer false \
    --bootappend-live "boot=live components quiet splash persistence" \
    --bootappend-install "quiet splash" \
    --binary-images iso-hybrid \
    --binary-filesystem ext4 \
    --chroot-filesystem squashfs \
    --compression gzip \
    --zsync false \
    --checksums sha256 \
    --build-with-chroot true \
    --cache true \
    --cache-indices true \
    --cache-packages true \
    --cache-stages true \
    --debootstrap-options "--variant=minbase --include=ca-certificates" \
    --system live \
    --mode debian \
    --updates true \
    --security true \
    --backports false \
    --firmware-chroot true \
    --firmware-binary true \
    --win32-loader false \
    --iso-application "SynOS Linux" \
    --iso-publisher "SynOS Development Team" \
    --iso-volume "SynOS-Linux-1.0" \
    --memtest none

print_status "success" "Live-build configuration initialized"

# Configure package repositories
print_status "section" "Configuring package repositories..."

# Add ParrotOS repositories
cat > config/archives/parrotsec.list.chroot << 'EOF'
# ParrotOS Security Repository
deb https://deb.parrotsec.org/parrot/ lory main contrib non-free
deb https://deb.parrotsec.org/parrot/ lory-security main contrib non-free
deb https://deb.parrotsec.org/parrot/ lory-backports main contrib non-free
EOF

cat > config/archives/parrotsec.list.binary << 'EOF'
# ParrotOS Security Repository
deb https://deb.parrotsec.org/parrot/ lory main contrib non-free
deb https://deb.parrotsec.org/parrot/ lory-security main contrib non-free
deb https://deb.parrotsec.org/parrot/ lory-backports main contrib non-free
EOF

# Add Kali repositories for additional security tools
cat > config/archives/kali.list.chroot << 'EOF'
# Kali Linux Repository (for additional security tools)
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF

cat > config/archives/kali.list.binary << 'EOF'
# Kali Linux Repository (for additional security tools)
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF

print_status "success" "Repository configuration complete"

# Configure base packages
print_status "section" "Configuring base package selection..."

# Core system packages
cat > config/package-lists/synos-base.list.chroot << 'EOF'
# SynOS Base System
live-boot
live-config
live-config-systemd
live-tools

# Essential system tools
sudo
curl
wget
git
vim
nano
htop
tree
unzip
p7zip-full
rsync

# Network tools
openssh-client
openssh-server
network-manager
wireless-tools
wpasupplicant

# Desktop environment (MATE - ParrotOS default)
mate-desktop-environment-core
mate-desktop-environment-extras
mate-themes
mate-icon-theme-faenza
lightdm
lightdm-gtk-greeter

# Development tools
build-essential
python3
python3-pip
python3-dev
nodejs
npm
rust-all

# Security basics
gnupg
ca-certificates
apt-transport-https
software-properties-common
EOF

# Security tools (essential subset)
cat > config/package-lists/synos-security.list.chroot << 'EOF'
# Core Security Tools
nmap
wireshark
burpsuite
metasploit-framework
aircrack-ng
john
hashcat
hydra
sqlmap
nikto
dirb
gobuster
masscan
netdiscover
recon-ng

# Network analysis
tcpdump
netcat-traditional
socat
proxychains

# Web security
wfuzz
wpscan
whatweb

# Forensics
binwalk
foremost
exiftool
volatility3

# Reverse engineering
gdb
radare2
objdump
strings
file

# Privacy tools
tor
torsocks
macchanger
EOF

print_status "success" "Package configuration complete"

# Configure custom files and hooks
print_status "section" "Setting up custom configurations..."

# Create custom hostname
mkdir -p config/includes.chroot/etc
echo "synos-linux" > config/includes.chroot/etc/hostname

# Create custom hosts file
mkdir -p config/includes.chroot/etc
cat > config/includes.chroot/etc/hosts << 'EOF'
127.0.0.1   localhost
127.0.1.1   synos-linux.localdomain synos-linux

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF

# Create custom MOTD
mkdir -p config/includes.chroot/etc/update-motd.d
cat > config/includes.chroot/etc/update-motd.d/01-synos << 'EOF'
#!/bin/sh
echo ""
echo "🧠 Welcome to SynOS Linux - AI-Enhanced Cybersecurity Distribution"
echo "📚 Educational | 🛡️ Security-Focused | 🤖 AI-Powered"
echo ""
echo "🔗 Documentation: https://synos.dev/docs"
echo "🆘 Support: https://synos.dev/support"
echo ""
EOF

chmod +x config/includes.chroot/etc/update-motd.d/01-synos

# Create SynOS directory structure
mkdir -p config/includes.chroot/opt/synos/{bin,lib,share,data}
mkdir -p config/includes.chroot/etc/synos
mkdir -p config/includes.chroot/var/log/synos

# Create SynOS configuration
cat > config/includes.chroot/etc/synos/synos.conf << 'EOF'
# SynOS Linux Configuration
SYNOS_VERSION="1.0.0"
SYNOS_CODENAME="Neural Genesis"
SYNOS_AI_ENABLED=true
SYNOS_EDUCATION_MODE=true
SYNOS_SECURITY_LEVEL="standard"
SYNOS_ANALYTICS_ENABLED=false
EOF

print_status "success" "Custom configurations created"

# Create build script hooks
print_status "section" "Creating build hooks..."

# Hook to install SynOS components
cat > config/hooks/live/0010-install-synos.hook.chroot << 'EOF'
#!/bin/bash

# Install SynOS AI Consciousness Framework
echo "🧠 Installing SynOS AI Consciousness Framework..."

# Create synos user for services
useradd -r -s /bin/false synos-ai

# Install Python dependencies for AI framework
pip3 install --break-system-packages \
    flask \
    numpy \
    pandas \
    scikit-learn \
    matplotlib \
    seaborn \
    requests \
    psutil \
    pynats

# Create systemd services for SynOS
cat > /etc/systemd/system/synos-consciousness.service << 'EOL'
[Unit]
Description=SynOS AI Consciousness Engine
After=network.target

[Service]
Type=simple
User=synos-ai
ExecStart=/opt/synos/bin/consciousness-engine
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

cat > /etc/systemd/system/synos-dashboard.service << 'EOL'
[Unit]
Description=SynOS AI Dashboard
After=network.target synos-consciousness.service

[Service]
Type=simple
User=synos-ai
ExecStart=/opt/synos/bin/dashboard-server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Enable services (will start after SynOS components are installed)
systemctl enable synos-consciousness.service
systemctl enable synos-dashboard.service

echo "✅ SynOS AI framework prepared"
EOF

chmod +x config/hooks/live/0010-install-synos.hook.chroot

print_status "success" "Build hooks created"

# Create desktop customizations
print_status "section" "Creating desktop customizations..."

# Custom wallpaper directory
mkdir -p config/includes.chroot/usr/share/backgrounds/synos

# Custom MATE panel configuration
mkdir -p config/includes.chroot/etc/skel/.config/dconf/user.d
cat > config/includes.chroot/etc/skel/.config/dconf/user.d/01-synos-mate << 'EOF'
# SynOS MATE Desktop Customizations
[org/mate/desktop/background]
picture-filename='/usr/share/backgrounds/synos/synos-neural-wallpaper.jpg'
picture-options='zoom'
primary-color='#1a1a2e'
secondary-color='#16213e'

[org/mate/panel/general]
object-id-list=['menu-bar', 'notification-area', 'clock', 'synos-ai-status']
toplevel-id-list=['top']

[org/mate/panel/objects/synos-ai-status]
object-type='applet'
applet-iid='SynosAIStatusAppletFactory::SynosAIStatusApplet'
toplevel-id='top'
position=10
EOF

print_status "success" "Desktop customizations created"

# Generate build summary
print_status "section" "Generating build summary..."

cat > build-summary.md << 'EOF'
# SynOS Linux Build Configuration

## Build Information
- **Distribution**: Debian Bookworm
- **Architecture**: amd64
- **Desktop**: MATE Desktop Environment
- **Boot**: Live system with persistence support
- **Compression**: gzip
- **Format**: ISO hybrid (BIOS/UEFI)

## Repository Sources
- Debian Bookworm (main, contrib, non-free, non-free-firmware)
- ParrotOS Security (lory, lory-security, lory-backports)
- Kali Linux (additional security tools)

## Package Categories
- **Base System**: Live boot, essential tools, development environment
- **Desktop**: MATE desktop with custom SynOS theme
- **Security Tools**: 30+ essential security tools from ParrotOS/Kali
- **AI Framework**: SynOS consciousness engine and dashboard

## Custom Features
- SynOS AI Consciousness Engine (systemd services)
- Educational cybersecurity framework
- Custom branding and themes
- AI-powered tool recommendations
- Progressive learning system

## Build Commands
```bash
# To build the ISO:
sudo lb build

# To clean the build:
sudo lb clean

# To rebuild configuration:
sudo lb clean --purge
./build-synos-base.sh
```

## Post-Build
- ISO will be created as: `live-image-amd64.hybrid.iso`
- Rename to: `synos-linux-1.0-amd64.iso`
- Test with QEMU before release
EOF

print_status "success" "Build summary generated: build-summary.md"

echo ""
print_status "header" "======================================================="
print_status "header" "    🎉 SynOS Linux Base Configuration Complete! 🎉"
print_status "header" "======================================================="
echo ""
print_status "success" "Configuration directory: $BUILD_DIR"
print_status "info" "Next steps:"
print_status "info" "1. Install required tools: ./scripts/setup-build-environment.sh"
print_status "info" "2. Copy SynOS components: ./scripts/copy-synos-components.sh"
print_status "info" "3. Build ISO: cd build && sudo lb build"
print_status "info" "4. Test ISO: qemu-system-x86_64 -cdrom synos-linux-1.0-amd64.iso -m 2048"
echo ""
print_status "header" "SynOS Linux is ready for Phase 1 build!"
echo ""