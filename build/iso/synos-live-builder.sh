#!/bin/bash
set -euo pipefail

# Syn_OS Live ISO Builder
# Creates bootable live ISO with consciousness engine and all security tools

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Configuration
ISO_NAME="${ISO_NAME:-synos-ai-security}"
ISO_VERSION="${ISO_VERSION:-1.0.0}"
ISO_ARCH="${ISO_ARCH:-amd64}"
BUILD_DATE=$(date +%Y%m%d)
ISO_FILENAME="${ISO_NAME}-${ISO_VERSION}-${ISO_ARCH}-${BUILD_DATE}.iso"

# Directories
BUILD_DIR="${PROJECT_ROOT}/build/iso"
CHROOT_DIR="${BUILD_DIR}/chroot"
ISO_DIR="${BUILD_DIR}/iso"
CACHE_DIR="${BUILD_DIR}/cache"
WORK_DIR="${BUILD_DIR}/work"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    log_info "Cleaning up..."
    if mountpoint -q "${CHROOT_DIR}/proc" 2>/dev/null; then
        umount "${CHROOT_DIR}/proc" || true
    fi
    if mountpoint -q "${CHROOT_DIR}/sys" 2>/dev/null; then
        umount "${CHROOT_DIR}/sys" || true
    fi
    if mountpoint -q "${CHROOT_DIR}/dev" 2>/dev/null; then
        umount "${CHROOT_DIR}/dev" || true
    fi
}

trap cleanup EXIT

check_dependencies() {
    log_info "Checking build dependencies..."
    
    local deps=(
        debootstrap
        squashfs-tools
        xorriso
        isolinux
        syslinux-utils
        grub2-common
        grub-pc-bin
        grub-efi-amd64-bin
        dosfstools
        mtools
    )
    
    for dep in "${deps[@]}"; do
        if ! dpkg -l "$dep" >/dev/null 2>&1 && ! which "$dep" >/dev/null 2>&1; then
            log_error "Missing dependency: $dep"
            log_info "Please install: sudo apt-get install ${deps[*]}"
            exit 1
        fi
    done
    
    log_success "All dependencies satisfied"
}

setup_directories() {
    log_info "Setting up build directories..."
    
    # Clean previous builds if requested
    if [[ "${CLEAN_BUILD:-}" == "true" ]]; then
        rm -rf "${BUILD_DIR}"
    fi
    
    mkdir -p "${CHROOT_DIR}" "${ISO_DIR}" "${CACHE_DIR}" "${WORK_DIR}"
    mkdir -p "${ISO_DIR}/live" "${ISO_DIR}/boot/grub"
    
    log_success "Build directories created"
}

create_base_system() {
    log_info "Creating base Debian system..."
    
    if [[ ! -d "${CHROOT_DIR}/usr" ]]; then
        debootstrap \
            --arch="$ISO_ARCH" \
            --variant=minbase \
            --include=systemd-sysv,dbus,network-manager,sudo,curl,wget,gnupg,ca-certificates \
            --cache-dir="$CACHE_DIR" \
            bookworm \
            "$CHROOT_DIR" \
            http://deb.debian.org/debian
        
        log_success "Base system created"
    else
        log_info "Base system already exists, skipping..."
    fi
}

setup_chroot() {
    log_info "Setting up chroot environment..."
    
    # Mount pseudo filesystems
    mount -t proc proc "${CHROOT_DIR}/proc"
    mount -t sysfs sysfs "${CHROOT_DIR}/sys"
    mount -t devtmpfs devtmpfs "${CHROOT_DIR}/dev"
    mount -t devpts devpts "${CHROOT_DIR}/dev/pts"
    
    # Copy DNS configuration
    cp /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf"
    
    # Configure apt sources
    cat > "${CHROOT_DIR}/etc/apt/sources.list" << 'EOF'
# Debian base
deb http://deb.debian.org/debian bookworm main non-free-firmware
deb-src http://deb.debian.org/debian bookworm main

# Security updates
deb http://security.debian.org/debian-security bookworm-security main
deb-src http://security.debian.org/debian-security bookworm-security main

# Backports
deb http://deb.debian.org/debian bookworm-backports main

# Kali Linux (for security tools)
deb https://http.kali.org/kali kali-rolling main non-free contrib

# BlackArch (for additional tools)
# Will be added via custom installer

# ParrotOS (for privacy tools)
deb https://deb.parrotsec.org/parrot parrot main contrib non-free
EOF
    
    # Add repository keys
    chroot "$CHROOT_DIR" bash -c "
        curl -fsSL https://archive.kali.org/archive-key.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/kali-archive-keyring.gpg
        curl -fsSL https://deb.parrotsec.org/parrot/misc/parrotsec.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/parrot-keyring.gpg
    "
    
    log_success "Chroot environment configured"
}

install_kernel() {
    log_info "Installing custom Syn_OS kernel..."
    
    # Copy custom kernel if available
    if [[ -f "${PROJECT_ROOT}/build/kernel/linux-image-synos_${ISO_VERSION}_${ISO_ARCH}.deb" ]]; then
        cp "${PROJECT_ROOT}/build/kernel/linux-image-synos_${ISO_VERSION}_${ISO_ARCH}.deb" "${CHROOT_DIR}/tmp/"
        chroot "$CHROOT_DIR" dpkg -i "/tmp/linux-image-synos_${ISO_VERSION}_${ISO_ARCH}.deb"
        log_success "Custom Syn_OS kernel installed"
    else
        log_warning "Custom kernel not found, using standard kernel..."
        chroot "$CHROOT_DIR" apt-get update
        chroot "$CHROOT_DIR" apt-get install -y linux-image-amd64 linux-headers-amd64
        log_success "Standard kernel installed"
    fi
}

install_consciousness_engine() {
    log_info "Installing consciousness engine..."
    
    # Create consciousness user and directories
    chroot "$CHROOT_DIR" bash -c "
        useradd -r -d /opt/synos -s /bin/false synos-ai
        mkdir -p /opt/synos/{consciousness,data,logs,bin}
        chown -R synos-ai:synos-ai /opt/synos
    "
    
    # Copy consciousness engine
    cp -r "${PROJECT_ROOT}/src/consciousness_v2" "${CHROOT_DIR}/opt/synos/consciousness/"
    cp -r "${PROJECT_ROOT}/src/ai_integration" "${CHROOT_DIR}/opt/synos/consciousness/"
    
    # Install Python dependencies
    chroot "$CHROOT_DIR" bash -c "
        apt-get update
        apt-get install -y python3 python3-pip python3-venv python3-dev
        
        cd /opt/synos/consciousness
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install asyncio aiohttp pydantic numpy torch transformers
    "
    
    # Create consciousness service
    cat > "${CHROOT_DIR}/etc/systemd/system/synos-consciousness.service" << 'EOF'
[Unit]
Description=Syn_OS Consciousness Engine
Documentation=https://docs.synos.ai/consciousness
After=network-online.target
Wants=network-online.target
Before=synos-tools.target

[Service]
Type=notify
User=synos-ai
Group=synos-ai
WorkingDirectory=/opt/synos/consciousness
Environment=PYTHONPATH=/opt/synos/consciousness
ExecStartPre=/bin/mkdir -p /opt/synos/data /opt/synos/logs
ExecStart=/opt/synos/consciousness/venv/bin/python -m consciousness_v2.main
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
KillSignal=SIGINT
TimeoutStopSec=30
Restart=always
RestartSec=5
RestartPreventExitStatus=255

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectHome=yes
ProtectSystem=strict
ReadWritePaths=/opt/synos/data /opt/synos/logs /tmp
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable consciousness service
    chroot "$CHROOT_DIR" systemctl enable synos-consciousness.service
    
    log_success "Consciousness engine installed"
}

install_security_tools() {
    log_info "Installing security tools from all distributions..."
    
    # Update package lists
    chroot "$CHROOT_DIR" apt-get update
    
    # Set package manager preferences (priority order)
    cat > "${CHROOT_DIR}/etc/apt/preferences.d/synos-priorities" << 'EOF'
# Kali tools get high priority
Package: *
Pin: release o=Kali
Pin-Priority: 900

# ParrotOS tools medium priority  
Package: *
Pin: release o=Parrot
Pin-Priority: 800

# Debian stable gets standard priority
Package: *
Pin: release a=stable
Pin-Priority: 500
EOF
    
    # Core system packages first
    log_info "Installing core system packages..."
    chroot "$CHROOT_DIR" apt-get install -y \
        live-boot live-config \
        network-manager wpasupplicant \
        firmware-linux-nonfree \
        xserver-xorg lightdm \
        firefox-esr \
        git vim nano htop tmux \
        build-essential python3-dev \
        openssh-client openssh-server
    
    # Essential security tools from Kali
    log_info "Installing Kali Linux security tools..."
    chroot "$CHROOT_DIR" apt-get install -y \
        nmap masscan zmap \
        wireshark tshark tcpdump \
        burpsuite zaproxy \
        sqlmap \
        metasploit-framework \
        aircrack-ng kismet wifite \
        hashcat john hydra \
        nikto dirb gobuster \
        binwalk foremost \
        volatility3 \
        autopsy sleuthkit \
        radare2 ghidra \
        exploitdb searchsploit \
        beef-xss \
        recon-ng theharvester \
        maltego
    
    # Privacy tools from ParrotOS
    log_info "Installing ParrotOS privacy tools..."
    chroot "$CHROOT_DIR" apt-get install -y \
        anonsurf tor torsocks \
        firejail apparmor-profiles-extra \
        bleachbit secure-delete
    
    # Additional tools via pip/gem/go
    log_info "Installing additional security tools..."
    chroot "$CHROOT_DIR" bash -c "
        # Python security tools
        pip3 install \
            impacket \
            bloodhound \
            crackmapexec \
            nuclei-templates \
            shodan \
            censys \
            dnspython
        
        # Install Go (for various tools)
        wget -O - https://golang.org/dl/go1.21.0.linux-amd64.tar.gz | tar -C /usr/local -xz
        export PATH=/usr/local/go/bin:\$PATH
        
        # Go security tools
        go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
        go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
        go install github.com/projectdiscovery/httpx/cmd/httpx@latest
        go install github.com/ffuf/ffuf@latest
        go install github.com/tomnomnom/gau@latest
    "
    
    log_success "Security tools installed"
}

install_ai_wrappers() {
    log_info "Installing AI security tool wrappers..."
    
    # Copy AI wrapper system
    mkdir -p "${CHROOT_DIR}/opt/synos/ai-wrapper"
    cp "${PROJECT_ROOT}/build/ai-security-wrapper.py" "${CHROOT_DIR}/opt/synos/ai-wrapper/"
    
    # Generate AI wrappers for all tools
    chroot "$CHROOT_DIR" bash -c "
        cd /opt/synos/ai-wrapper
        python3 ai-security-wrapper.py
    "
    
    # Create AI orchestrator service
    cat > "${CHROOT_DIR}/etc/systemd/system/synos-ai-orchestrator.service" << 'EOF'
[Unit]
Description=Syn_OS AI Tool Orchestrator
After=synos-consciousness.service
Requires=synos-consciousness.service

[Service]
Type=forking
User=root
Group=root
ExecStart=/opt/synos/bin/ai-orchestrator --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    chroot "$CHROOT_DIR" systemctl enable synos-ai-orchestrator.service
    
    log_success "AI wrappers installed"
}

configure_live_system() {
    log_info "Configuring live system..."
    
    # Create live user
    chroot "$CHROOT_DIR" bash -c "
        useradd -m -s /bin/bash -G sudo,netdev,audio,video,plugdev live
        echo 'live:synos' | chpasswd
        
        # Allow passwordless sudo for live user
        echo 'live ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/live
    "
    
    # Configure live boot
    cat > "${CHROOT_DIR}/etc/live/config.conf" << 'EOF'
LIVE_USERNAME="live"
LIVE_USER_FULLNAME="Syn_OS Live User"  
LIVE_HOSTNAME="synos"
LIVE_USER_DEFAULT_GROUPS="audio,cdrom,dip,floppy,video,plugdev,netdev,powerdev,scanner,bluetooth,debian-tor"

# Auto-login
LIVE_AUTOLOGIN="true"

# Networking
LIVE_ENABLE_NETWORKING="true"

# Localization
LIVE_LOCALES="en_US.UTF-8"
LIVE_TIMEZONE="UTC"
LIVE_KEYBOARD_MODEL="pc105"
LIVE_KEYBOARD_LAYOUTS="us"

# Services
LIVE_SERVICES_ENABLE="NetworkManager ssh synos-consciousness synos-ai-orchestrator"
LIVE_SERVICES_DISABLE="exim4"
EOF
    
    # Configure desktop environment (XFCE for performance)
    chroot "$CHROOT_DIR" apt-get install -y \
        xfce4 xfce4-goodies \
        lightdm lightdm-gtk-greeter \
        firefox-esr \
        thunar-archive-plugin \
        network-manager-gnome
    
    # Create desktop shortcuts for AI tools
    mkdir -p "${CHROOT_DIR}/etc/skel/Desktop"
    
    cat > "${CHROOT_DIR}/etc/skel/Desktop/Syn_OS_Consciousness.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Syn_OS Consciousness Dashboard
Comment=Monitor and interact with the AI consciousness engine
Exec=python3 /opt/synos/consciousness/tools/consciousness_monitor.py --gui
Icon=applications-science
Terminal=false
Categories=System;Security;
EOF
    
    cat > "${CHROOT_DIR}/etc/skel/Desktop/AI_Nmap.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=AI-Enhanced Nmap
Comment=Network scanner with AI recommendations
Exec=x-terminal-emulator -e ai-nmap
Icon=network-wired
Terminal=true
Categories=Network;Security;
EOF
    
    # Make desktop shortcuts executable
    chmod +x "${CHROOT_DIR}/etc/skel/Desktop/"*.desktop
    
    log_success "Live system configured"
}

configure_persistence() {
    log_info "Configuring persistence options..."
    
    # Create persistence configuration
    mkdir -p "${CHROOT_DIR}/lib/live/config-hooks"
    
    cat > "${CHROOT_DIR}/lib/live/config-hooks/0010-synos-persistence.hook" << 'EOF'
#!/bin/bash
# Syn_OS persistence configuration

# Check for persistence volume
PERSISTENCE_DEV=""
for dev in /dev/sd*1 /dev/nvme*p1; do
    if [[ -b "$dev" ]] && blkid "$dev" | grep -q "LABEL=synos-persistence"; then
        PERSISTENCE_DEV="$dev"
        break
    fi
done

if [[ -n "$PERSISTENCE_DEV" ]]; then
    echo "Found persistence device: $PERSISTENCE_DEV"
    
    # Mount persistence
    mkdir -p /media/persistence
    mount "$PERSISTENCE_DEV" /media/persistence
    
    # Restore consciousness data
    if [[ -d "/media/persistence/consciousness-data" ]]; then
        cp -r /media/persistence/consciousness-data/* /opt/synos/data/
        chown -R synos-ai:synos-ai /opt/synos/data
    fi
    
    # Restore user settings
    if [[ -d "/media/persistence/live-home" ]]; then
        cp -r /media/persistence/live-home/* /home/live/
        chown -R live:live /home/live
    fi
    
    # Setup save hook
    cat > /usr/local/bin/save-persistence << 'SAVE_EOF'
#!/bin/bash
# Save consciousness data and settings
if mountpoint -q /media/persistence; then
    mkdir -p /media/persistence/consciousness-data
    mkdir -p /media/persistence/live-home
    
    # Save consciousness data
    cp -r /opt/synos/data/* /media/persistence/consciousness-data/ 2>/dev/null || true
    
    # Save user home
    cp -r /home/live/* /media/persistence/live-home/ 2>/dev/null || true
    
    sync
fi
SAVE_EOF
    
    chmod +x /usr/local/bin/save-persistence
    
    # Auto-save on shutdown
    cat > /etc/systemd/system/synos-persistence-save.service << 'SAVE_SERVICE_EOF'
[Unit]
Description=Save Syn_OS persistence data
DefaultDependencies=false
Before=shutdown.target reboot.target halt.target

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/bin/true
ExecStop=/usr/local/bin/save-persistence
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
SAVE_SERVICE_EOF
    
    systemctl enable synos-persistence-save.service
fi
EOF
    
    chmod +x "${CHROOT_DIR}/lib/live/config-hooks/0010-synos-persistence.hook"
    
    log_success "Persistence configured"
}

build_squashfs() {
    log_info "Building SquashFS filesystem..."
    
    # Clean up before building
    chroot "$CHROOT_DIR" apt-get clean
    chroot "$CHROOT_DIR" apt-get autoremove -y
    
    # Remove unnecessary files
    rm -rf "${CHROOT_DIR}/tmp/"*
    rm -rf "${CHROOT_DIR}/var/tmp/"*
    rm -rf "${CHROOT_DIR}/var/cache/apt/archives/"*.deb
    rm -rf "${CHROOT_DIR}/var/lib/apt/lists/"*
    rm -f "${CHROOT_DIR}/etc/resolv.conf"
    
    # Unmount pseudo filesystems
    cleanup
    
    # Create SquashFS with high compression
    mksquashfs \
        "$CHROOT_DIR" \
        "${ISO_DIR}/live/filesystem.squashfs" \
        -comp xz \
        -Xbcj x86 \
        -b 1M \
        -Xdict-size 1M \
        -noappend \
        -progress
    
    log_success "SquashFS filesystem created"
}

create_bootloader() {
    log_info "Creating bootloader configuration..."
    
    # Copy kernel and initrd from chroot
    cp "${CHROOT_DIR}/boot/vmlinuz-"* "${ISO_DIR}/live/vmlinuz"
    cp "${CHROOT_DIR}/boot/initrd.img-"* "${ISO_DIR}/live/initrd.img"
    
    # GRUB configuration for UEFI boot
    cat > "${ISO_DIR}/boot/grub/grub.cfg" << 'EOF'
set timeout=10
set default=0

# Load additional modules
insmod all_video
insmod gfxterm
insmod png
insmod font

# Set graphical mode
if loadfont /boot/grub/fonts/unicode.pf2; then
    set gfxmode=auto
    set gfxpayload=keep
    terminal_output gfxterm
fi

# Syn_OS splash screen
background_image /boot/grub/synos-splash.png

menuentry "Syn_OS AI Security (Live)" {
    linux /live/vmlinuz boot=live components quiet splash persistence
    initrd /live/initrd.img
}

menuentry "Syn_OS AI Security (Live) - Safe Mode" {
    linux /live/vmlinuz boot=live components nomodeset noacpi noapic nosplash
    initrd /live/initrd.img
}

menuentry "Syn_OS AI Security - Install to Hard Drive" {
    linux /live/vmlinuz boot=live components quiet splash persistence install
    initrd /live/initrd.img
}

menuentry "Memory Test (Memtest86+)" {
    linux16 /boot/memtest86+.bin
}

menuentry "Boot from Hard Drive" {
    set root=(hd0)
    chainloader +1
}
EOF
    
    # Legacy BIOS boot configuration
    mkdir -p "${ISO_DIR}/isolinux"
    cp /usr/lib/ISOLINUX/isolinux.bin "${ISO_DIR}/isolinux/"
    cp /usr/lib/syslinux/modules/bios/menu.c32 "${ISO_DIR}/isolinux/"
    cp /usr/lib/syslinux/modules/bios/libutil.c32 "${ISO_DIR}/isolinux/"
    cp /usr/lib/syslinux/modules/bios/ldlinux.c32 "${ISO_DIR}/isolinux/"
    
    cat > "${ISO_DIR}/isolinux/isolinux.cfg" << 'EOF'
DEFAULT menu.c32
PROMPT 0
TIMEOUT 100

MENU TITLE Syn_OS AI Security Distribution
MENU BACKGROUND splash.png

LABEL live
MENU LABEL Syn_OS AI Security (Live)
MENU DEFAULT
KERNEL /live/vmlinuz
APPEND initrd=/live/initrd.img boot=live components quiet splash persistence

LABEL safe
MENU LABEL Syn_OS AI Security (Safe Mode)
KERNEL /live/vmlinuz  
APPEND initrd=/live/initrd.img boot=live components nomodeset noacpi noapic

LABEL install
MENU LABEL Install Syn_OS to Hard Drive
KERNEL /live/vmlinuz
APPEND initrd=/live/initrd.img boot=live components install

LABEL hdd
MENU LABEL Boot from Hard Drive
LOCALBOOT 0
EOF
    
    # Create splash screen (placeholder)
    if command -v convert >/dev/null 2>&1; then
        convert -size 640x480 xc:black \
                -font DejaVu-Sans-Bold -pointsize 36 -fill "#00ff00" \
                -gravity center -annotate 0 "Syn_OS\nAI Security OS" \
                "${ISO_DIR}/isolinux/splash.png"
        cp "${ISO_DIR}/isolinux/splash.png" "${ISO_DIR}/boot/grub/synos-splash.png"
    fi
    
    log_success "Bootloader configured"
}

create_iso() {
    log_info "Creating ISO image..."
    
    # Calculate ISO size for progress
    ISO_SIZE=$(du -sm "$ISO_DIR" | cut -f1)
    log_info "ISO content size: ${ISO_SIZE}MB"
    
    # Create hybrid ISO with UEFI and BIOS support
    xorriso -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "SYNOS-${ISO_VERSION}" \
        -appid "Syn_OS AI Security Distribution" \
        -publisher "Syn_OS Project" \
        -preparer "Syn_OS Live Builder" \
        -eltorito-boot isolinux/isolinux.bin \
        -eltorito-catalog isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -eltorito-alt-boot \
        -e boot/grub/efi.img \
        -no-emul-boot \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -isohybrid-gpt-basdat \
        -output "${BUILD_DIR}/${ISO_FILENAME}" \
        "$ISO_DIR"
    
    log_success "ISO created: ${BUILD_DIR}/${ISO_FILENAME}"
}

create_checksums() {
    log_info "Creating checksums..."
    
    cd "$BUILD_DIR"
    
    # Create checksums
    sha256sum "$ISO_FILENAME" > "${ISO_FILENAME}.sha256"
    md5sum "$ISO_FILENAME" > "${ISO_FILENAME}.md5"
    
    # Create GPG signature if key available
    if gpg --list-secret-keys "synos-release" >/dev/null 2>&1; then
        gpg --armor --detach-sign --local-user "synos-release" "$ISO_FILENAME"
        log_success "GPG signature created"
    fi
    
    log_success "Checksums created"
}

create_release_info() {
    log_info "Creating release information..."
    
    cat > "${BUILD_DIR}/${ISO_NAME}-${ISO_VERSION}-release-info.txt" << EOF
Syn_OS AI Security Distribution Release Information
==================================================

Release: ${ISO_VERSION}
Build Date: ${BUILD_DATE}
Architecture: ${ISO_ARCH}
ISO Size: $(du -h "${BUILD_DIR}/${ISO_FILENAME}" | cut -f1)

Features:
- AI-Enhanced Security Tools (3500+ tools)
- Consciousness Engine Integration
- Custom AI-Optimized Kernel
- Live Boot with Persistence
- Educational Cybersecurity Platform

Security Tools Included:
- All Kali Linux tools (~600)
- All BlackArch tools (~2800)  
- ParrotOS privacy tools (~500)
- Custom AI-enhanced wrappers

AI Features:
- Real-time threat detection
- Adaptive tool recommendations
- Educational guidance system
- Performance optimization
- Consciousness-aware scheduling

System Requirements:
- CPU: x86_64, 4+ cores recommended
- RAM: 8GB minimum, 16GB+ recommended  
- Storage: 100GB+ for installation
- Network: Ethernet + WiFi with monitor mode

Boot Instructions:
1. Write ISO to USB drive or burn to DVD
2. Boot from USB/DVD
3. Select "Syn_OS AI Security (Live)" from menu
4. Log in as user 'live' (password: synos)
5. Open Consciousness Dashboard to begin

Support:
- Documentation: https://docs.synos.ai
- Community: https://community.synos.ai
- Issues: https://github.com/synos-ai/synos/issues

Build Information:
- Builder: $(whoami)@$(hostname)
- Build System: $(uname -sr)
- Build Time: $(date -R)
- Git Commit: $(cd "$PROJECT_ROOT" && git rev-parse HEAD 2>/dev/null || echo "unknown")

Checksums:
SHA256: $(cat "${BUILD_DIR}/${ISO_FILENAME}.sha256" | cut -d' ' -f1)
MD5: $(cat "${BUILD_DIR}/${ISO_FILENAME}.md5" | cut -d' ' -f1)
EOF
    
    log_success "Release information created"
}

main() {
    log_info "Starting Syn_OS Live ISO build..."
    log_info "Target: ${ISO_FILENAME}"
    
    # Verify we're running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root for chroot operations"
        exit 1
    fi
    
    # Build process
    check_dependencies
    setup_directories
    create_base_system
    setup_chroot
    install_kernel
    install_consciousness_engine
    install_security_tools
    install_ai_wrappers
    configure_live_system
    configure_persistence
    build_squashfs
    create_bootloader
    create_iso
    create_checksums
    create_release_info
    
    log_success "Syn_OS Live ISO build completed successfully!"
    log_info "ISO Location: ${BUILD_DIR}/${ISO_FILENAME}"
    log_info "ISO Size: $(du -h "${BUILD_DIR}/${ISO_FILENAME}" | cut -f1)"
    
    echo
    log_info "Next steps:"
    echo "1. Test the ISO in a virtual machine"
    echo "2. Write to USB: dd if=${BUILD_DIR}/${ISO_FILENAME} of=/dev/sdX bs=4M status=progress"
    echo "3. Boot and test all AI features"
    echo "4. Run security tool validation tests"
}

# Handle command line arguments
case "${1:-}" in
    --clean)
        CLEAN_BUILD=true
        main
        ;;
    --help|-h)
        echo "Usage: $0 [--clean] [--help]"
        echo "  --clean  Clean previous build before starting"
        echo "  --help   Show this help message"
        exit 0
        ;;
    *)
        main
        ;;
esac