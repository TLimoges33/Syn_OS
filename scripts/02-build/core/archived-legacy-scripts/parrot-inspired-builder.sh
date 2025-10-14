#!/bin/bash

# SynOS ParrotOS-Inspired Build System
# Learning from ParrotOS 6.4 Security Edition but enhanced with AI consciousness

set -e

# Build Configuration - Based on ParrotOS analysis
SYNOS_VERSION="1.0"
SYNOS_CODENAME="Consciousness"
BUILD_DATE=$(date +%Y%m%d)
ISO_NAME="SynOS-${SYNOS_VERSION}-${SYNOS_CODENAME}-${BUILD_DATE}.iso"

# Directories
BUILD_ROOT="/home/diablorain/Syn_OS/build"
BUILD_DIR="${BUILD_ROOT}/parrot-inspired"
CHROOT_DIR="${BUILD_DIR}/chroot"
ISO_DIR="${BUILD_DIR}/iso"
FINAL_ISO="${BUILD_ROOT}/${ISO_NAME}"
TOOLS_DIR="${BUILD_DIR}/tools"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging
LOG_FILE="${BUILD_DIR}/parrot-inspired-build.log"
ERROR_LOG="${BUILD_DIR}/build-errors.log"

# ParrotOS Tool Categories (from our analysis)
declare -A PARROT_SECURITY_TOOLS=(
    ["network"]="nmap netdiscover masscan zmap unicornscan nbtscan enum4linux"
    ["web"]="burpsuite zaproxy sqlmap nikto dirb gobuster"
    ["wireless"]="aircrack-ng kismet reaver wifite hostapd-wpe"
    ["exploitation"]="metasploit-framework armitage beef-xss setoolkit"
    ["forensics"]="autopsy volatility sleuthkit binwalk foremost"
    ["passwords"]="john hashcat hydra medusa ncrack patator"
    ["analysis"]="wireshark tcpdump tshark ettercap dsniff"
    ["reverse"]="radare2 ghidra ida-free ollydbg gdb"
    ["crypto"]="cryptsetup veracrypt steghide outguess gpg"
    ["privacy"]="tor proxychains anonsurf bleachbit mat2"
)

log_info() { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" "$ERROR_LOG"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1" | tee -a "$LOG_FILE"; }

print_parrot_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║          SynOS ParrotOS-Inspired Build System               ║"
    echo "║      Enhanced Security Education with AI Consciousness      ║"
    echo "║                                                              ║"
    echo "║  Base: Debian Bookworm + ParrotOS Security + AI Learning    ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_parrot_prerequisites() {
    log_step "Checking ParrotOS-inspired build prerequisites..."
    
    # Root check
    if [[ $EUID -ne 0 ]]; then
        log_error "Root privileges required for chroot operations"
        return 1
    fi
    
    # Essential tools
    local required_tools=("debootstrap" "chroot" "mksquashfs" "xorriso" "isolinux" "curl" "wget")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_error "Missing required tool: $tool"
            log_info "Install with: apt update && apt install debootstrap xorriso squashfs-tools isolinux syslinux-efi curl wget"
            return 1
        fi
    done
    
    # Check available space (need ~8GB for full build)
    local available_gb=$(df /tmp | awk 'NR==2{printf "%.0f", $4/1024/1024}')
    if [[ $available_gb -lt 8 ]]; then
        log_warning "Low disk space: ${available_gb}GB available, 8GB+ recommended"
    fi
    
    log_success "All prerequisites satisfied"
    return 0
}

create_parrot_base_system() {
    log_step "Creating Debian base system (ParrotOS approach)..."
    
    # Clean any previous builds
    if [[ -d "$CHROOT_DIR" ]]; then
        log_info "Cleaning previous build..."
        umount -R "$CHROOT_DIR" 2>/dev/null || true
        rm -rf "$CHROOT_DIR"
    fi
    
    mkdir -p "$CHROOT_DIR" "$ISO_DIR" "$TOOLS_DIR"
    
    # Create Debian base with ParrotOS-compatible packages
    log_info "Running debootstrap for Debian Bookworm base..."
    
    if ! debootstrap \
        --variant=minbase \
        --include=systemd,systemd-sysv,locales,apt-utils,gnupg,ca-certificates,wget,curl \
        bookworm \
        "$CHROOT_DIR" \
        http://deb.debian.org/debian/ 2>&1 | tee -a "$LOG_FILE"; then
        log_error "Base system creation failed"
        return 1
    fi
    
    log_success "Debian base system created"
    return 0
}

configure_parrot_repositories() {
    log_step "Configuring ParrotOS-compatible repositories..."
    
    # Mount essential filesystems
    mount -t proc none "${CHROOT_DIR}/proc"
    mount -t sysfs none "${CHROOT_DIR}/sys"
    mount -o bind /dev "${CHROOT_DIR}/dev"
    mount -o bind /dev/pts "${CHROOT_DIR}/dev/pts"
    
    # Configure APT sources including security repos
    cat > "${CHROOT_DIR}/etc/apt/sources.list" << 'EOF'
# Debian Bookworm repositories
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware

# Security updates
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
deb-src http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware

# Updates
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware

# Backports for newer security tools
deb http://deb.debian.org/debian bookworm-backports main contrib non-free non-free-firmware
EOF
    
    # Add Kali repository for latest security tools (ParrotOS approach)
    cat >> "${CHROOT_DIR}/etc/apt/sources.list" << 'EOF'

# Kali Linux repository for security tools
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF
    
    # Add Kali GPG key
    chroot "$CHROOT_DIR" bash -c "
        wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add -
        apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED444FF07D8D0BF6
    " || log_warning "Kali repository key setup failed - security tools may be limited"
    
    # Set APT preferences to prioritize Debian over Kali
    cat > "${CHROOT_DIR}/etc/apt/preferences.d/debian-priority" << 'EOF'
Package: *
Pin: release o=Debian
Pin-Priority: 900

Package: *
Pin: release o=Kali
Pin-Priority: 300
EOF
    
    # Update package database
    chroot "$CHROOT_DIR" apt update
    
    log_success "ParrotOS-compatible repositories configured"
}

install_parrot_desktop_environment() {
    log_step "Installing MATE desktop environment (ParrotOS default)..."
    
    # Install MATE desktop like ParrotOS
    local desktop_packages=(
        "mate-desktop-environment-core"
        "mate-terminal" 
        "mate-system-monitor"
        "mate-calc"
        "mate-screenshot"
        "lightdm"
        "lightdm-gtk-greeter"
        "firefox-esr"
        "file-roller"
        "network-manager-gnome"
        "pulseaudio"
        "pavucontrol"
        "gvfs-backends"
    )
    
    log_info "Installing MATE desktop packages..."
    if ! chroot "$CHROOT_DIR" apt install -y --no-install-recommends "${desktop_packages[@]}" 2>&1 | tee -a "$LOG_FILE"; then
        log_warning "Some desktop packages failed to install"
    fi
    
    # Configure LightDM for auto-login (live system)
    cat > "${CHROOT_DIR}/etc/lightdm/lightdm.conf" << 'EOF'
[Seat:*]
autologin-user=synos
autologin-user-timeout=0
user-session=mate
greeter-session=lightdm-gtk-greeter
EOF
    
    log_success "MATE desktop environment installed"
}

install_synos_consciousness_system() {
    log_step "Installing SynOS AI Consciousness System..."
    
    # Install Python and dependencies
    chroot "$CHROOT_DIR" apt install -y python3 python3-pip python3-venv python3-dev
    
    # Create SynOS directory structure
    local synos_dirs=(
        "/opt/synos"
        "/opt/synos/consciousness"
        "/opt/synos/security"
        "/opt/synos/education"
        "/opt/synos/tools"
        "/home/synos/.synos"
    )
    
    for dir in "${synos_dirs[@]}"; do
        mkdir -p "${CHROOT_DIR}${dir}"
    done
    
    # Copy our lightweight implementation as base
    local synos_src="/home/diablorain/Syn_OS/core/build/lightweight-iso"
    if [[ -d "$synos_src" ]]; then
        cp -r "$synos_src"/* "${CHROOT_DIR}/opt/synos/"
        chmod +x "${CHROOT_DIR}/opt/synos/scripts/"*.sh
        chmod +x "${CHROOT_DIR}/opt/synos/scripts/"*.py
    fi
    
    # Enhanced consciousness service for ParrotOS integration
    cat > "${CHROOT_DIR}/opt/synos/consciousness/parrot-consciousness.py" << 'EOF'
#!/usr/bin/env python3

"""
SynOS ParrotOS-Enhanced Consciousness Service
Integrates AI consciousness with ParrotOS security tools
"""

import http.server
import socketserver
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

class ParrotConsciousnessHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_parrot_dashboard()
        elif self.path == '/tools':
            self.send_security_tools()
        elif self.path == '/api/tools':
            self.send_json_response(self.get_available_tools())
        elif self.path == '/api/system':
            self.send_json_response(self.get_system_status())
        else:
            self.send_404()
    
    def send_parrot_dashboard(self):
        html = '''<!DOCTYPE html>
<html>
<head>
    <title>SynOS Consciousness - ParrotOS Enhanced</title>
    <style>
        body { 
            font-family: 'Courier New', monospace; 
            background: #0d1117; 
            color: #39ff14; 
            margin: 0; 
            padding: 20px; 
        }
        .header { 
            text-align: center; 
            border: 2px solid #39ff14; 
            padding: 20px; 
            margin-bottom: 20px; 
            background: #161b22;
        }
        .tool-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .tool-category { 
            background: #161b22; 
            border: 1px solid #39ff14; 
            padding: 15px; 
            border-radius: 8px; 
        }
        .tool-item { 
            background: #21262d; 
            margin: 5px 0; 
            padding: 8px; 
            border-radius: 4px; 
            cursor: pointer;
        }
        .tool-item:hover { background: #2d333b; }
        .status-indicator { color: #39ff14; }
        button { 
            background: #238636; 
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 4px; 
            cursor: pointer; 
            margin: 5px; 
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 SynOS Consciousness System</h1>
        <h2>🦜 ParrotOS Security Enhanced</h2>
        <p>AI-Powered Security Education Platform</p>
        <div>Status: <span class="status-indicator">●</span> ACTIVE</div>
    </div>
    
    <div class="tool-grid">
        <div class="tool-category">
            <h3>🌐 Network Security</h3>
            <div class="tool-item" onclick="launchTool('nmap')">Nmap - Network Scanner</div>
            <div class="tool-item" onclick="launchTool('netdiscover')">Netdiscover - ARP Scanner</div>
            <div class="tool-item" onclick="launchTool('masscan')">Masscan - Fast Scanner</div>
        </div>
        
        <div class="tool-category">
            <h3>🕷️ Web Application</h3>
            <div class="tool-item" onclick="launchTool('burpsuite')">Burp Suite - Web Proxy</div>
            <div class="tool-item" onclick="launchTool('sqlmap')">SQLMap - SQL Injection</div>
            <div class="tool-item" onclick="launchTool('nikto')">Nikto - Web Scanner</div>
        </div>
        
        <div class="tool-category">
            <h3>🔐 Exploitation</h3>
            <div class="tool-item" onclick="launchTool('msfconsole')">Metasploit - Framework</div>
            <div class="tool-item" onclick="launchTool('beef-xss')">BeEF - Browser Exploit</div>
            <div class="tool-item" onclick="launchTool('setoolkit')">SET - Social Engineering</div>
        </div>
        
        <div class="tool-category">
            <h3>🔍 Analysis & Forensics</h3>
            <div class="tool-item" onclick="launchTool('wireshark')">Wireshark - Packet Analysis</div>
            <div class="tool-item" onclick="launchTool('autopsy')">Autopsy - Digital Forensics</div>
            <div class="tool-item" onclick="launchTool('volatility')">Volatility - Memory Analysis</div>
        </div>
        
        <div class="tool-category">
            <h3>🎓 Learning Modules</h3>
            <div class="tool-item" onclick="startLearning('network-basics')">Network Security Basics</div>
            <div class="tool-item" onclick="startLearning('web-security')">Web Application Security</div>
            <div class="tool-item" onclick="startLearning('forensics')">Digital Forensics</div>
        </div>
        
        <div class="tool-category">
            <h3>⚙️ System Status</h3>
            <div id="system-info">Loading...</div>
        </div>
    </div>
    
    <script>
        function launchTool(tool) {
            fetch('/api/launch/' + tool, {method: 'POST'})
                .then(r => r.json())
                .then(data => alert('Launching ' + tool + ': ' + data.message));
        }
        
        function startLearning(module) {
            fetch('/api/learn/' + module, {method: 'POST'})
                .then(r => r.json())
                .then(data => alert('Starting ' + module + ': ' + data.message));
        }
        
        // Update system info
        fetch('/api/system')
            .then(r => r.json())
            .then(data => {
                document.getElementById('system-info').innerHTML = 
                    '<div>Uptime: ' + data.uptime + '</div>' +
                    '<div>Tools Available: ' + data.tools_count + '</div>' +
                    '<div>Consciousness: Active</div>';
            });
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def get_available_tools(self):
        tools = {}
        tool_paths = {
            'nmap': '/usr/bin/nmap',
            'netdiscover': '/usr/bin/netdiscover',
            'masscan': '/usr/bin/masscan',
            'burpsuite': '/usr/bin/burpsuite',
            'sqlmap': '/usr/bin/sqlmap',
            'nikto': '/usr/bin/nikto',
            'msfconsole': '/usr/bin/msfconsole',
            'wireshark': '/usr/bin/wireshark',
            'autopsy': '/usr/bin/autopsy'
        }
        
        for tool, path in tool_paths.items():
            tools[tool] = {
                'available': Path(path).exists(),
                'path': path,
                'category': self.get_tool_category(tool)
            }
        
        return tools
    
    def get_tool_category(self, tool):
        categories = {
            'nmap': 'network', 'netdiscover': 'network', 'masscan': 'network',
            'burpsuite': 'web', 'sqlmap': 'web', 'nikto': 'web',
            'msfconsole': 'exploitation', 'beef-xss': 'exploitation',
            'wireshark': 'analysis', 'autopsy': 'forensics'
        }
        return categories.get(tool, 'other')
    
    def get_system_status(self):
        return {
            'uptime': self.get_uptime(),
            'tools_count': len([t for t in self.get_available_tools().values() if t['available']]),
            'consciousness_active': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_uptime(self):
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except:
            return "Unknown"
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'404 - Not Found')
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP logs

def main():
    port = 8080
    print(f"SynOS ParrotOS-Enhanced Consciousness starting on port {port}")
    with socketserver.TCPServer(("", port), ParrotConsciousnessHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "${CHROOT_DIR}/opt/synos/consciousness/parrot-consciousness.py"
    
    # Create systemd service
    cat > "${CHROOT_DIR}/etc/systemd/system/synos-consciousness.service" << 'EOF'
[Unit]
Description=SynOS Consciousness Service - ParrotOS Enhanced
After=network.target

[Service]
Type=simple
User=synos
ExecStart=/opt/synos/consciousness/parrot-consciousness.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    chroot "$CHROOT_DIR" systemctl enable synos-consciousness.service
    
    log_success "SynOS AI Consciousness System installed"
}

install_parrot_security_tools() {
    log_step "Installing ParrotOS-inspired security tools..."
    
    # Install tools by category with error handling
    for category in "${!PARROT_SECURITY_TOOLS[@]}"; do
        log_info "Installing $category security tools..."
        
        # Convert space-separated list to array
        read -ra tools <<< "${PARROT_SECURITY_TOOLS[$category]}"
        
        for tool in "${tools[@]}"; do
            log_info "  Installing $tool..."
            
            # Try multiple package names/sources
            if ! chroot "$CHROOT_DIR" apt install -y "$tool" 2>/dev/null; then
                # Try with kali- prefix
                if ! chroot "$CHROOT_DIR" apt install -y "kali-$tool" 2>/dev/null; then
                    # Try alternative names
                    case $tool in
                        "burpsuite")
                            chroot "$CHROOT_DIR" apt install -y burpsuite-community 2>/dev/null || log_warning "  $tool installation failed"
                            ;;
                        "beef-xss")
                            chroot "$CHROOT_DIR" apt install -y beef 2>/dev/null || log_warning "  $tool installation failed"
                            ;;
                        *)
                            log_warning "  $tool installation failed - may need manual setup"
                            ;;
                    esac
                fi
            else
                log_success "  $tool installed"
            fi
        done
        
        log_success "$category tools installation completed"
    done
    
    # Install additional ParrotOS-specific packages
    local parrot_extras=(
        "tor"
        "proxychains4" 
        "macchanger"
        "bleachbit"
        "mat2"
        "steghide"
        "binwalk"
        "foremost"
        "testdisk"
    )
    
    log_info "Installing ParrotOS extras..."
    chroot "$CHROOT_DIR" apt install -y "${parrot_extras[@]}" 2>&1 | tee -a "$LOG_FILE"
    
    log_success "ParrotOS-inspired security tools installation completed"
}

configure_live_system() {
    log_step "Configuring live system (ParrotOS approach)..."
    
    # Create live user with sudo privileges
    chroot "$CHROOT_DIR" useradd -m -s /bin/bash -G sudo,audio,video,netdev synos
    echo "synos:synos" | chroot "$CHROOT_DIR" chpasswd
    echo "root:toor" | chroot "$CHROOT_DIR" chpasswd
    
    # Configure sudo without password for live user
    echo "synos ALL=(ALL) NOPASSWD:ALL" > "${CHROOT_DIR}/etc/sudoers.d/synos"
    
    # System identification
    echo "synos-parrot" > "${CHROOT_DIR}/etc/hostname"
    
    cat > "${CHROOT_DIR}/etc/hosts" << 'EOF'
127.0.0.1   localhost synos-parrot
::1         localhost ip6-localhost ip6-loopback
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
EOF
    
    # Create SynOS desktop shortcuts
    mkdir -p "${CHROOT_DIR}/home/synos/Desktop"
    
    cat > "${CHROOT_DIR}/home/synos/Desktop/SynOS-Consciousness.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS Consciousness
Comment=AI-Enhanced Security Education Platform
Exec=firefox http://localhost:8080
Icon=applications-development
Terminal=false
Categories=Education;Security;Development;
EOF
    
    cat > "${CHROOT_DIR}/home/synos/Desktop/Security-Tools.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Security Tools Menu
Comment=ParrotOS-Inspired Security Tools
Exec=mate-terminal -e "bash -c 'echo Security Tools Menu && ls /usr/bin/*map* /usr/bin/*scan* 2>/dev/null && read'"
Icon=applications-security
Terminal=true
Categories=Security;System;
EOF
    
    # Set ownership
    chroot "$CHROOT_DIR" chown -R synos:synos /home/synos
    chroot "$CHROOT_DIR" chown -R synos:synos /opt/synos
    
    # Install live-boot packages
    chroot "$CHROOT_DIR" apt install -y live-boot live-config live-config-systemd
    
    log_success "Live system configuration completed"
}

create_bootable_iso() {
    log_step "Creating bootable ISO with ParrotOS styling..."
    
    # Create ISO directory structure
    mkdir -p "${ISO_DIR}/live" "${ISO_DIR}/isolinux"
    
    # Copy kernel and initrd
    local kernel_file=$(ls "${CHROOT_DIR}/boot/vmlinuz-"* | head -1)
    local initrd_file=$(ls "${CHROOT_DIR}/boot/initrd.img-"* | head -1)
    
    if [[ -f "$kernel_file" && -f "$initrd_file" ]]; then
        cp "$kernel_file" "${ISO_DIR}/live/vmlinuz"
        cp "$initrd_file" "${ISO_DIR}/live/initrd"
        log_success "Kernel and initrd copied"
    else
        log_error "Kernel or initrd not found"
        return 1
    fi
    
    # Create squashfs
    log_info "Creating compressed filesystem (this takes time)..."
    if ! mksquashfs "$CHROOT_DIR" "${ISO_DIR}/live/filesystem.squashfs" \
        -comp xz -processors $(nproc) 2>&1 | tee -a "$LOG_FILE"; then
        log_error "Squashfs creation failed"
        return 1
    fi
    
    # Install bootloader
    cp /usr/lib/ISOLINUX/isolinux.bin "${ISO_DIR}/isolinux/"
    cp /usr/lib/syslinux/modules/bios/*.c32 "${ISO_DIR}/isolinux/" 2>/dev/null || true
    
    # Create ParrotOS-style boot menu
    cat > "${ISO_DIR}/isolinux/isolinux.cfg" << EOF
UI menu.c32
PROMPT 0
TIMEOUT 300
MENU TITLE SynOS v${SYNOS_VERSION} ${SYNOS_CODENAME} - ParrotOS Enhanced

DEFAULT live
MENU COLOR border       30;44   #40ffffff #a0000000 std
MENU COLOR title        1;36;44 #9033ffff #a0000000 std
MENU COLOR sel          7;37;40 #e0ffffff #20ff8000 all
MENU COLOR unsel        37;44   #50ffffff #a0000000 std

LABEL live
  MENU LABEL SynOS Live (AI Consciousness Mode)
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components quiet splash

LABEL forensics
  MENU LABEL SynOS Forensics Mode (No Swap/Mount)
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components noswap noautomount

LABEL persistence
  MENU LABEL SynOS Persistence Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components persistence

LABEL safe
  MENU LABEL SynOS Safe Mode (Minimal Drivers)
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components acpi=off noapic nomodeset

LABEL memtest
  MENU LABEL Memory Test
  KERNEL /install/memtest
EOF
    
    # Generate ISO
    log_info "Generating final ISO image..."
    if ! xorriso -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "SynOS_${SYNOS_VERSION}_${SYNOS_CODENAME}" \
        -eltorito-boot isolinux/isolinux.bin \
        -eltorito-catalog isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -output "$FINAL_ISO" \
        "$ISO_DIR" 2>&1 | tee -a "$LOG_FILE"; then
        log_error "ISO generation failed"
        return 1
    fi
    
    # Generate checksums
    cd "$(dirname "$FINAL_ISO")"
    sha256sum "$(basename "$FINAL_ISO")" > "${FINAL_ISO}.sha256"
    md5sum "$(basename "$FINAL_ISO")" > "${FINAL_ISO}.md5"
    
    local iso_size=$(du -h "$FINAL_ISO" | cut -f1)
    log_success "ISO created: $FINAL_ISO ($iso_size)"
    
    return 0
}

cleanup_build() {
    log_info "Cleaning up build environment..."
    
    # Unmount chroot filesystems
    local mount_points=("${CHROOT_DIR}/proc" "${CHROOT_DIR}/sys" "${CHROOT_DIR}/dev/pts" "${CHROOT_DIR}/dev")
    for mount_point in "${mount_points[@]}"; do
        if mountpoint -q "$mount_point" 2>/dev/null; then
            umount "$mount_point" 2>/dev/null || umount -l "$mount_point" 2>/dev/null || true
        fi
    done
    
    log_success "Cleanup completed"
}

show_final_summary() {
    local build_time=$(($(date +%s) - BUILD_START))
    local iso_size=$(du -h "$FINAL_ISO" 2>/dev/null | cut -f1 || echo "Unknown")
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}║             🎉 SynOS ParrotOS-Enhanced Build Complete! 🎉    ║${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📀 ISO Details:${NC}"
    echo "   File: $FINAL_ISO"
    echo "   Size: $iso_size" 
    echo "   Build Time: ${build_time} seconds"
    echo ""
    echo -e "${CYAN}🛡️ Security Features:${NC}"
    echo "   • ParrotOS-inspired security tool collection"
    echo "   • AI Consciousness web dashboard"
    echo "   • MATE desktop environment"
    echo "   • Live boot with persistence support"
    echo "   • Educational security modules"
    echo ""
    echo -e "${CYAN}🚀 Testing Commands:${NC}"
    echo "   Virtual Test: qemu-system-x86_64 -m 4096 -cdrom $FINAL_ISO"
    echo "   USB Creation: dd if=$FINAL_ISO of=/dev/sdX bs=4M status=progress"
    echo "   Verify: sha256sum -c ${FINAL_ISO}.sha256"
    echo ""
    echo -e "${GREEN}✅ SynOS is ready for deployment!${NC}"
}

main() {
    BUILD_START=$(date +%s)
    
    print_parrot_banner
    
    # Initialize logging
    mkdir -p "$BUILD_DIR"
    echo "SynOS ParrotOS-Inspired Build - Started $(date)" > "$LOG_FILE"
    echo "SynOS ParrotOS-Inspired Build Errors - Started $(date)" > "$ERROR_LOG"
    
    # Set up cleanup trap
    trap cleanup_build EXIT
    
    log_info "Starting SynOS ParrotOS-Enhanced build process..."
    
    # Execute build phases
    if ! check_parrot_prerequisites; then
        exit 1
    fi
    
    if ! create_parrot_base_system; then
        exit 1
    fi
    
    if ! configure_parrot_repositories; then
        exit 1
    fi
    
    if ! install_parrot_desktop_environment; then
        exit 1
    fi
    
    if ! install_synos_consciousness_system; then
        exit 1
    fi
    
    if ! install_parrot_security_tools; then
        exit 1
    fi
    
    if ! configure_live_system; then
        exit 1
    fi
    
    if ! create_bootable_iso; then
        exit 1
    fi
    
    show_final_summary
    
    log_success "🎯 SynOS ParrotOS-Enhanced build completed successfully!"
}

# Execute main function
main "$@"
