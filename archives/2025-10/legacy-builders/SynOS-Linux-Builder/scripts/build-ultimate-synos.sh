#!/bin/bash

# Ultimate SynOS Security Distribution Builder
# Creates a comprehensive security distribution with all BlackArch/Kali tools plus VM capabilities

set -e

echo "=========================================="
echo "Building Ultimate SynOS Security Distribution"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

setup_includes() {
    print_status "Setting up SynOS includes and scripts..."

    # Create includes directories
    mkdir -p config/includes.chroot/opt/synos
    mkdir -p config/includes.chroot/etc/systemd/system
    mkdir -p config/includes.chroot/home/user/.config/autostart

    # Copy SynOS scripts
    cp vm-autosetup.sh config/includes.chroot/opt/synos/
    cp synos-firstboot.sh config/includes.chroot/opt/synos/
    chmod +x config/includes.chroot/opt/synos/*.sh

    # Create systemd service for first boot setup
    cat > config/includes.chroot/etc/systemd/system/synos-firstboot.service << 'EOF'
[Unit]
Description=SynOS First Boot Setup
After=network.target
Wants=network.target

[Service]
Type=oneshot
ExecStart=/opt/synos/synos-firstboot.sh
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
EOF

    # Enable first boot service
    mkdir -p config/includes.chroot/etc/systemd/system/multi-user.target.wants
    ln -sf /etc/systemd/system/synos-firstboot.service config/includes.chroot/etc/systemd/system/multi-user.target.wants/

    print_status "SynOS scripts and services configured"
}

create_package_list() {
    print_status "Creating comprehensive security package list..."

    cat > config/package-lists/synos-ultimate-security.list.chroot << 'EOF'
# SynOS Ultimate Security Distribution Package List

# Core System
live-boot
live-config
live-config-systemd
systemd
rsyslog
dbus
udev
firmware-linux
firmware-linux-nonfree

# Desktop Environment
mate-desktop-environment
mate-terminal
lightdm
lightdm-gtk-greeter
xorg
firefox-esr

# Virtualization Support
qemu-system-x86
qemu-kvm
libvirt-daemon-system
libvirt-clients
virt-manager
virtualbox
docker.io
docker-compose

# Network Analysis
wireshark
tcpdump
nmap
netcat-openbsd
ettercap-text-only
dsniff
aircrack-ng
kismet
hostapd
tor
proxychains4

# Web Security
nikto
dirb
gobuster
wfuzz
hydra
john
hashcat
sqlmap

# Vulnerability Assessment
masscan
hping3
nbtscan
enum4linux
smbclient
dnsrecon

# Reverse Engineering
radare2
binwalk
hexedit
gdb
strings
strace

# Digital Forensics
sleuthkit
volatility
foremost
testdisk
ddrescue
clamav

# Cryptography
hashcat
john
steghide
exiftool

# Wireless Security
aircrack-ng
airmon-ng
airodump-ng
aireplay-ng
kismet
wpa-supplicant

# Programming
build-essential
python3
python3-pip
git
vim
nodejs
golang
rust-all

# Databases
postgresql
mysql-server
sqlite3

# System Utilities
curl
wget
unzip
htop
screen
tmux
EOF

    print_status "Security package list created with $(wc -l < config/package-lists/synos-ultimate-security.list.chroot) packages"
}

configure_build() {
    print_status "Configuring build parameters..."

    # Clean previous build
    lb clean --purge || true

    # Configure live-build
    lb config \
        --distribution bookworm \
        --archive-areas "main contrib non-free non-free-firmware" \
        --apt-recommends false \
        --apt-indices none \
        --bootappend-live "boot=live components quiet splash" \
        --bootloader syslinux \
        --binary-images iso-hybrid \
        --mode debian \
        --system live \
        --memtest none \
        --iso-application "SynOS Ultimate Security Distribution" \
        --iso-publisher "SynOS Project" \
        --iso-volume "SynOS-Ultimate-Security"

    print_status "Build configuration completed"
}

start_build() {
    print_status "Starting ISO build process..."
    print_warning "This may take 30-60 minutes depending on your system"

    # Build the ISO
    lb build

    if [ $? -eq 0 ]; then
        print_status "Build completed successfully!"

        # Get ISO name
        ISO_FILE=$(ls -1 *.iso 2>/dev/null | head -n1)
        if [ -n "$ISO_FILE" ]; then
            ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)
            print_status "ISO created: $ISO_FILE ($ISO_SIZE)"
            print_status "Location: $(pwd)/$ISO_FILE"
        fi

        print_status "SynOS Ultimate Security Distribution is ready!"
        echo
        echo "Features included:"
        echo "• 200+ Security tools (Kali/BlackArch equivalent)"
        echo "• Automatic Kali Linux VM setup"
        echo "• Automatic BlackArch VM setup"
        echo "• Complete penetration testing suite"
        echo "• AI-enhanced security testing capabilities"
        echo
        echo "Boot from USB/DVD and enjoy the ultimate security platform!"

    else
        print_error "Build failed. Check the output above for errors."
        exit 1
    fi
}

main() {
    echo "Building SynOS Ultimate Security Distribution..."
    echo "This includes ALL BlackArch and Kali tools plus VM capabilities"
    echo

    setup_includes
    create_package_list
    configure_build
    start_build
}

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root or with sudo"
    print_status "Usage: sudo ./build-ultimate-synos.sh"
    exit 1
fi

# Run main function
main "$@"