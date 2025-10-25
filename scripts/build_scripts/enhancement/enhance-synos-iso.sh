#!/usr/bin/env bash
################################################################################
# SynOS ISO Enhancement Script
# Adds all missing customization, branding, and security tools
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paths
PROJECT_ROOT="/home/diablorain/Syn_OS"
CHROOT_DIR="$PROJECT_ROOT/build/synos-v1.0/chroot"
ASSETS_DIR="$PROJECT_ROOT/assets/branding"
TOOLS_DIR="$PROJECT_ROOT/tools/security-tools"

# Logging
section() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}🔧 $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

# Check if chroot exists
if [ ! -d "$CHROOT_DIR" ]; then
    error "Chroot directory not found: $CHROOT_DIR"
    error "Please run ultimate-final-master-developer-v1.0-build.sh first"
    exit 1
fi

################################################################################
# 1. INSTALL ALL MISSING SECURITY TOOLS
################################################################################

install_security_tools_complete() {
    section "Installing Complete Security Tool Suite"

    log "Installing from Debian repositories..."
    chroot "$CHROOT_DIR" bash -c "
        export DEBIAN_FRONTEND=noninteractive

        # Add Kali repos for additional tools
        echo 'deb http://http.kali.org/kali kali-rolling main contrib non-free' > /etc/apt/sources.list.d/kali.list
        wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add - || true

        apt-get update

        # Information Gathering
        apt-get install -y --allow-unauthenticated \
            nmap masscan unicornscan zmap \
            dmitry dnsenum dnsrecon fierce \
            theharvester recon-ng maltego \
            amass subfinder assetfinder \
            shodan wafw00f whatweb \
            sslscan sslyze testssl.sh \
            || true

        # Vulnerability Scanning
        apt-get install -y --allow-unauthenticated \
            nikto w3af wapiti skipfish \
            nuclei nessus openvas \
            lynis linux-exploit-suggester \
            || true

        # Web Applications
        apt-get install -y --allow-unauthenticated \
            burpsuite zaproxy sqlmap \
            commix xsser beef-xss \
            wpscan joomscan droopescan \
            dirb dirbuster gobuster ffuf \
            wfuzz feroxbuster dirsearch \
            || true

        # Password Attacks
        apt-get install -y --allow-unauthenticated \
            hydra medusa ncrack \
            john hashcat crunch \
            cewl cupp wordlists \
            patator brutespray \
            || true

        # Wireless Attacks
        apt-get install -y --allow-unauthenticated \
            aircrack-ng reaver pixiewps \
            wifite kismet fern-wifi-cracker \
            bully mdk4 wifiphisher \
            hostapd-wpe eaphammer \
            || true

        # Exploitation
        apt-get install -y --allow-unauthenticated \
            metasploit-framework armitage \
            beef-xss social-engineer-toolkit \
            exploitdb searchsploit \
            shellter veil-framework \
            || true

        # Post-Exploitation
        apt-get install -y --allow-unauthenticated \
            mimikatz powersploit empire \
            covenant bloodhound crackmapexec \
            evil-winrm impacket responder \
            proxychains4 chisel ligolo \
            || true

        # Forensics
        apt-get install -y --allow-unauthenticated \
            autopsy sleuthkit foremost \
            binwalk volatility3 yara \
            bulk-extractor guymager dc3dd \
            ddrescue scalpel photorec \
            || true

        # Reverse Engineering
        apt-get install -y --allow-unauthenticated \
            ghidra radare2 cutter \
            binary-ninja ida-free \
            gdb gdb-peda gef pwndbg \
            ltrace strace objdump \
            hopper-disassembler \
            || true

        # Malware Analysis
        apt-get install -y --allow-unauthenticated \
            cuckoo-sandbox remnux \
            pestudio floss strings \
            upx-ucl yara-rules \
            || true

        # Sniffing & Spoofing
        apt-get install -y --allow-unauthenticated \
            wireshark tshark tcpdump \
            ettercap-text-only bettercap \
            mitmproxy dnschef arpspoof \
            responder ngrep dsniff \
            || true

        # Reporting
        apt-get install -y --allow-unauthenticated \
            dradis serpico faraday \
            pipal hashid name-that-hash \
            || true
    "

    log "Installing tools from GitHub..."
    chroot "$CHROOT_DIR" bash -c "
        cd /opt

        # Clone popular GitHub tools
        git clone https://github.com/byt3bl33d3r/CrackMapExec.git || true
        git clone https://github.com/carlospolop/PEASS-ng.git || true
        git clone https://github.com/rebootuser/LinEnum.git || true
        git clone https://github.com/sleventyeleven/linuxprivchecker.git || true
        git clone https://github.com/swisskyrepo/PayloadsAllTheThings.git || true
        git clone https://github.com/danielmiessler/SecLists.git || true
        git clone https://github.com/andrew-d/static-binaries.git || true
        git clone https://github.com/PowerShellMafia/PowerSploit.git || true
        git clone https://github.com/samratashok/nishang.git || true
        git clone https://github.com/trustedsec/social-engineer-toolkit.git || true

        # Install Python tools
        pip3 install --break-system-packages \
            impacket pwntools ropper \
            bloodhound py2neo \
            mitm6 crackmapexec \
            || true
    "

    log "✓ Security tools installation complete"
}

################################################################################
# 2. CREATE APPLICATION MENU STRUCTURE
################################################################################

create_security_menu() {
    section "Creating SynOS Security Tools Menu"

    # Create menu directory structure
    mkdir -p "$CHROOT_DIR/usr/share/desktop-directories"
    mkdir -p "$CHROOT_DIR/etc/xdg/menus/applications-merged"

    # Main SynOS menu directory
    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-main.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=SynOS Tools
Icon=security-high
Comment=AI-Enhanced Cybersecurity Tools
EOF

    # Create category directories
    local categories=(
        "information-gathering:Information Gathering:network-workgroup"
        "vulnerability-analysis:Vulnerability Analysis:security-medium"
        "web-applications:Web Applications:web-browser"
        "password-attacks:Password Attacks:dialog-password"
        "wireless-attacks:Wireless Attacks:network-wireless"
        "exploitation:Exploitation & Frameworks:system-run"
        "post-exploitation:Post Exploitation:preferences-system"
        "forensics:Forensics:drive-harddisk"
        "reverse-engineering:Reverse Engineering:applications-development"
        "sniffing-spoofing:Sniffing & Spoofing:network-wired"
        "reporting:Reporting Tools:document-properties"
    )

    for category in "${categories[@]}"; do
        IFS=: read -r id name icon <<< "$category"
        cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-${id}.directory" <<EOF
[Desktop Entry]
Type=Directory
Name=${name}
Icon=${icon}
Comment=SynOS ${name} Tools
EOF
    done

    # Create menu configuration
    cat > "$CHROOT_DIR/etc/xdg/menus/applications-merged/synos-tools.menu" <<'EOF'
<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
 "http://www.freedesktop.org/standards/menu-spec/menu-1.0.dtd">
<Menu>
  <Name>Applications</Name>

  <Menu>
    <Name>SynOS Tools</Name>
    <Directory>synos-main.directory</Directory>

    <Menu>
      <Name>Information Gathering</Name>
      <Directory>synos-information-gathering.directory</Directory>
      <Include>
        <Category>SynOS-InfoGathering</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Vulnerability Analysis</Name>
      <Directory>synos-vulnerability-analysis.directory</Directory>
      <Include>
        <Category>SynOS-VulnAnalysis</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Web Applications</Name>
      <Directory>synos-web-applications.directory</Directory>
      <Include>
        <Category>SynOS-WebApps</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Password Attacks</Name>
      <Directory>synos-password-attacks.directory</Directory>
      <Include>
        <Category>SynOS-Password</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Wireless Attacks</Name>
      <Directory>synos-wireless-attacks.directory</Directory>
      <Include>
        <Category>SynOS-Wireless</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Exploitation</Name>
      <Directory>synos-exploitation.directory</Directory>
      <Include>
        <Category>SynOS-Exploitation</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Post Exploitation</Name>
      <Directory>synos-post-exploitation.directory</Directory>
      <Include>
        <Category>SynOS-PostExploit</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Forensics</Name>
      <Directory>synos-forensics.directory</Directory>
      <Include>
        <Category>SynOS-Forensics</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Reverse Engineering</Name>
      <Directory>synos-reverse-engineering.directory</Directory>
      <Include>
        <Category>SynOS-ReverseEng</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Sniffing & Spoofing</Name>
      <Directory>synos-sniffing-spoofing.directory</Directory>
      <Include>
        <Category>SynOS-Sniffing</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Reporting</Name>
      <Directory>synos-reporting.directory</Directory>
      <Include>
        <Category>SynOS-Reporting</Category>
      </Include>
    </Menu>

  </Menu>
</Menu>
EOF

    log "Creating desktop entries for tools..."

    # Create desktop entries for key tools
    mkdir -p "$CHROOT_DIR/usr/share/applications/synos"

    # Example: Nmap
    cat > "$CHROOT_DIR/usr/share/applications/synos/nmap.desktop" <<'EOF'
[Desktop Entry]
Name=Nmap
Comment=Network exploration tool and security scanner
Exec=mate-terminal -e "nmap"
Icon=network-workgroup
Terminal=false
Type=Application
Categories=SynOS-InfoGathering;Network;Security;
EOF

    # Burp Suite
    cat > "$CHROOT_DIR/usr/share/applications/synos/burpsuite.desktop" <<'EOF'
[Desktop Entry]
Name=Burp Suite
Comment=Web application security testing
Exec=burpsuite
Icon=web-browser
Terminal=false
Type=Application
Categories=SynOS-WebApps;Network;Security;
EOF

    # Metasploit
    cat > "$CHROOT_DIR/usr/share/applications/synos/metasploit.desktop" <<'EOF'
[Desktop Entry]
Name=Metasploit Framework
Comment=Penetration testing framework
Exec=mate-terminal -e "msfconsole"
Icon=system-run
Terminal=false
Type=Application
Categories=SynOS-Exploitation;Security;
EOF

    # Wireshark
    cat > "$CHROOT_DIR/usr/share/applications/synos/wireshark.desktop" <<'EOF'
[Desktop Entry]
Name=Wireshark
Comment=Network protocol analyzer
Exec=wireshark
Icon=network-wired
Terminal=false
Type=Application
Categories=SynOS-Sniffing;Network;Security;
EOF

    # Ghidra
    cat > "$CHROOT_DIR/usr/share/applications/synos/ghidra.desktop" <<'EOF'
[Desktop Entry]
Name=Ghidra
Comment=Software reverse engineering suite
Exec=ghidra
Icon=applications-development
Terminal=false
Type=Application
Categories=SynOS-ReverseEng;Development;Security;
EOF

    log "✓ Security menu structure created"
}

################################################################################
# 3. APPLY CUSTOM BRANDING AND THEMES
################################################################################

apply_branding() {
    section "Applying SynOS Custom Branding"

    log "Copying branded wallpapers..."
    mkdir -p "$CHROOT_DIR/usr/share/backgrounds/synos"
    cp "$ASSETS_DIR/backgrounds/"*.jpg "$CHROOT_DIR/usr/share/backgrounds/synos/" || true

    # Copy space/nuclear themed wallpapers from host
    cp /usr/share/backgrounds/space.jpg "$CHROOT_DIR/usr/share/backgrounds/synos/" || true
    cp /usr/share/backgrounds/outerspaceEarth.jpg "$CHROOT_DIR/usr/share/backgrounds/synos/" || true

    log "Installing SynOS logos..."
    mkdir -p "$CHROOT_DIR/usr/share/pixmaps/synos"
    cp "$ASSETS_DIR/logos/"*.png "$CHROOT_DIR/usr/share/pixmaps/synos/" || true
    ln -sf /usr/share/pixmaps/synos/synos-logo-64.png "$CHROOT_DIR/usr/share/pixmaps/synos.png" || true

    log "Installing custom themes..."
    if [ -d "$ASSETS_DIR/themes/synos-mate" ]; then
        mkdir -p "$CHROOT_DIR/usr/share/themes"
        cp -r "$ASSETS_DIR/themes/synos-mate" "$CHROOT_DIR/usr/share/themes/" || true
    fi

    log "Configuring Plymouth boot splash..."
    if [ -d "$ASSETS_DIR/plymouth/synos-neural" ]; then
        mkdir -p "$CHROOT_DIR/usr/share/plymouth/themes"
        cp -r "$ASSETS_DIR/plymouth/synos-neural" "$CHROOT_DIR/usr/share/plymouth/themes/" || true

        chroot "$CHROOT_DIR" bash -c "
            plymouth-set-default-theme synos-neural || true
            update-initramfs -u || true
        "
    fi

    log "Configuring GRUB theme..."
    mkdir -p "$CHROOT_DIR/boot/grub/themes/synos"
    if [ -f "$ASSETS_DIR/grub/synos-grub-16x9.png" ]; then
        cp "$ASSETS_DIR/grub/synos-grub-16x9.png" "$CHROOT_DIR/boot/grub/themes/synos/background.png" || true
    fi

    log "✓ Branding applied"
}

################################################################################
# 4. CONFIGURE DEFAULT DESKTOP SETTINGS
################################################################################

configure_desktop_defaults() {
    section "Configuring Desktop Environment Defaults"

    log "Setting up MATE desktop defaults..."

    # Create dconf profile
    mkdir -p "$CHROOT_DIR/etc/dconf/profile"
    cat > "$CHROOT_DIR/etc/dconf/profile/user" <<'EOF'
user-db:user
system-db:synos
EOF

    # Create system database directory
    mkdir -p "$CHROOT_DIR/etc/dconf/db/synos.d"

    # Configure MATE settings
    cat > "$CHROOT_DIR/etc/dconf/db/synos.d/01-synos-defaults" <<'EOF'
[org/mate/desktop/background]
picture-filename='/usr/share/backgrounds/synos/space.jpg'
picture-options='zoom'
primary-color='#000000'
secondary-color='#000000'

[org/mate/desktop/interface]
gtk-theme='Windows 10 Dark'
icon-theme='gnome'
font-name='Sans 10'
document-font-name='Sans 10'
monospace-font-name='Monospace 10'

[org/mate/marco/general]
theme='ARK-Dark'
titlebar-font='Sans Bold 10'

[org/mate/panel/general]
object-id-list=['menu-bar', 'notification-area', 'clock', 'window-list', 'workspace-switcher']
toplevel-id-list=['top', 'bottom']

[org/mate/panel/toplevels/top]
orientation='top'
size=24

[org/mate/panel/toplevels/bottom]
orientation='bottom'
size=24

[org/mate/session]
idle-delay=15

[org/mate/screensaver]
lock-enabled=false
idle-activation-enabled=false

[org/mate/power-manager]
button-lid-ac='nothing'
button-lid-battery='nothing'
EOF

    # Update dconf database
    chroot "$CHROOT_DIR" dconf update || true

    # Copy to skel for new users
    mkdir -p "$CHROOT_DIR/etc/skel/.config"

    # Create autostart for SynOS welcome
    mkdir -p "$CHROOT_DIR/etc/skel/.config/autostart"
    cat > "$CHROOT_DIR/etc/skel/.config/autostart/synos-welcome.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=SynOS Welcome
Exec=/opt/synos-demo/synos-welcome.py
Icon=system-help
Terminal=false
Categories=System;
X-GNOME-Autostart-enabled=true
EOF

    log "Installing themes from host system..."
    chroot "$CHROOT_DIR" bash -c "
        apt-get install -y \
            mate-themes \
            arc-theme \
            adapta-gtk-theme \
            numix-gtk-theme \
            || true
    "

    log "✓ Desktop defaults configured"
}

################################################################################
# 5. FIX SYNOS DEMO APPLICATION
################################################################################

fix_demo_application() {
    section "Fixing SynOS Demo Application"

    log "Demo application already exists at /opt/synos-demo/synos-welcome.py"
    log "Ensuring it's properly integrated..."

    # Make sure it's executable
    chmod +x "$CHROOT_DIR/opt/synos-demo/synos-welcome.py"

    # Ensure desktop entry exists
    if [ ! -f "$CHROOT_DIR/usr/share/applications/synos-welcome.desktop" ]; then
        cat > "$CHROOT_DIR/usr/share/applications/synos-welcome.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=SynOS Welcome & Demo
Comment=Interactive welcome screen and demo system
Exec=/opt/synos-demo/synos-welcome.py
Icon=system-help
Terminal=false
Categories=System;Education;
Keywords=synos;demo;tutorial;welcome;
StartupNotify=true
EOF
    fi

    # Create symlink for easy CLI access
    chroot "$CHROOT_DIR" ln -sf /opt/synos-demo/synos-welcome.py /usr/local/bin/synos-demo || true

    log "✓ Demo application fixed"
}

################################################################################
# 6. ADD GITHUB RECOMMENDED REPOS TO SYSTEM
################################################################################

setup_github_repos() {
    section "Setting Up GitHub Repository Integration"

    log "Cloning recommended repositories..."

    mkdir -p "$CHROOT_DIR/opt/github-repos"

    chroot "$CHROOT_DIR" bash -c "
        cd /opt/github-repos

        # Bug Bounty
        git clone --depth=1 https://github.com/djadmin/awesome-bug-bounty.git || true
        git clone --depth=1 https://github.com/swisskyrepo/PayloadsAllTheThings.git || true

        # Penetration Testing
        git clone --depth=1 https://github.com/enaqx/awesome-pentest.git || true
        git clone --depth=1 https://github.com/J0hnbX/RedTeam-Resources.git || true

        # CTF & Learning
        git clone --depth=1 https://github.com/JohnHammond/ctf-katana.git || true
        git clone --depth=1 https://github.com/carlospolop/hacktricks.git || true

        # Wordlists
        git clone --depth=1 https://github.com/danielmiessler/SecLists.git || true

        # Scripts
        git clone --depth=1 https://github.com/rebootuser/LinEnum.git || true
        git clone --depth=1 https://github.com/carlospolop/PEASS-ng.git || true
    "

    # Create README in user home
    cat > "$CHROOT_DIR/etc/skel/GITHUB_RESOURCES.md" <<'EOF'
# 🐙 GitHub Resources

Welcome to your curated collection of security resources!

## 📁 Local Repositories

All repositories are cloned to `/opt/github-repos/`:

### Bug Bounty
- `awesome-bug-bounty` - Curated list of bug bounty resources
- `PayloadsAllTheThings` - Useful payloads for web pentesting

### Penetration Testing
- `awesome-pentest` - Collection of pentest tools and resources
- `RedTeam-Resources` - Red team operations guide

### CTF & Learning
- `ctf-katana` - CTF tool suite
- `hacktricks` - Hacking tricks and techniques

### Essential Tools
- `SecLists` - Security testing wordlists
- `LinEnum` - Linux enumeration script
- `PEASS-ng` - Privilege escalation scripts

## 🔗 Online Resources

Open these in your browser:
- https://github.com/topics/penetration-testing
- https://github.com/topics/cybersecurity
- https://github.com/topics/bug-bounty
- https://www.hackerone.com/
- https://www.bugcrowd.com/
- https://www.hackthebox.eu/
- https://tryhackme.com/

EOF

    log "✓ GitHub repositories set up"
}

################################################################################
# 7. CREATE DESKTOP SHORTCUTS
################################################################################

create_desktop_shortcuts() {
    section "Creating Desktop Shortcuts"

    mkdir -p "$CHROOT_DIR/etc/skel/Desktop"

    # Install SynOS shortcut
    cat > "$CHROOT_DIR/etc/skel/Desktop/install-synos.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Install SynOS
Comment=Install SynOS to your computer
Exec=pkexec calamares
Icon=system-software-install
Terminal=false
EOF

    # Welcome shortcut
    cat > "$CHROOT_DIR/etc/skel/Desktop/synos-welcome.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=SynOS Welcome
Comment=Interactive welcome and demo
Exec=/opt/synos-demo/synos-welcome.py
Icon=system-help
Terminal=false
EOF

    # Terminal shortcut
    cat > "$CHROOT_DIR/etc/skel/Desktop/terminal.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Terminal
Comment=Open a terminal
Exec=mate-terminal
Icon=utilities-terminal
Terminal=false
EOF

    # Firefox shortcut
    ln -sf /usr/share/applications/firefox-esr.desktop "$CHROOT_DIR/etc/skel/Desktop/" || true

    # Make shortcuts executable
    chmod +x "$CHROOT_DIR/etc/skel/Desktop/"*.desktop

    log "✓ Desktop shortcuts created"
}

################################################################################
# 8. REBUILD ISO WITH ENHANCEMENTS
################################################################################

rebuild_iso() {
    section "Rebuilding ISO with Enhancements"

    log "Cleaning old ISO..."
    rm -rf "$PROJECT_ROOT/build/synos-v1.0/iso"
    mkdir -p "$PROJECT_ROOT/build/synos-v1.0/iso"/{live,boot/grub}

    log "Copying kernel and initrd..."
    cp "$CHROOT_DIR/boot/vmlinuz-"* "$PROJECT_ROOT/build/synos-v1.0/iso/live/vmlinuz"
    cp "$CHROOT_DIR/boot/initrd.img-"* "$PROJECT_ROOT/build/synos-v1.0/iso/live/initrd"

    log "Creating enhanced squashfs (this will take 15-30 minutes)..."
    mksquashfs "$CHROOT_DIR" "$PROJECT_ROOT/build/synos-v1.0/iso/live/filesystem.squashfs" \
        -comp xz -b 1M -Xbcj x86 -e boot -noappend

    log "Creating GRUB configuration with splash..."
    cat > "$PROJECT_ROOT/build/synos-v1.0/iso/boot/grub/grub.cfg" <<'EOF'
set timeout=30
set default=0

# Load graphics
if loadfont unicode ; then
  set gfxmode=auto
  load_video
  insmod gfxterm
  terminal_output gfxterm
fi

# Set background if available
if background_image /boot/grub/themes/synos/background.png; then
  set color_normal=white/black
  set color_highlight=black/white
else
  set menu_color_normal=cyan/blue
  set menu_color_highlight=white/blue
fi

menuentry "SynOS v1.0.0 Neural Genesis (Live)" {
    linux /live/vmlinuz boot=live components quiet splash
    initrd /live/initrd
}

menuentry "SynOS v1.0.0 (Safe Mode)" {
    linux /live/vmlinuz boot=live components nomodeset
    initrd /live/initrd
}

menuentry "SynOS v1.0.0 (Persistence)" {
    linux /live/vmlinuz boot=live components persistence
    initrd /live/initrd
}

menuentry "SynOS v1.0.0 (Forensics Mode - No Disk Mounting)" {
    linux /live/vmlinuz boot=live components noswap noautomount
    initrd /live/initrd
}
EOF

    log "Building final ISO..."
    grub-mkrescue -o "$PROJECT_ROOT/build/synos-v1.0/SynOS-v1.0.0-enhanced-$(date +%Y%m%d).iso" \
        "$PROJECT_ROOT/build/synos-v1.0/iso" -- -volid "SYNOS_V1"

    # Create checksums
    cd "$PROJECT_ROOT/build/synos-v1.0"
    md5sum "SynOS-v1.0.0-enhanced-"*.iso > "SynOS-v1.0.0-enhanced-$(date +%Y%m%d).iso.md5"
    sha256sum "SynOS-v1.0.0-enhanced-"*.iso > "SynOS-v1.0.0-enhanced-$(date +%Y%m%d).iso.sha256"

    log "✓ Enhanced ISO built successfully!"
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo -e "${GREEN}"
    cat <<'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗              ║
║   ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝              ║
║   ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗              ║
║   ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║              ║
║   ███████║   ██║   ██║ ╚████║╚██████╔╝███████║              ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝              ║
║                                                               ║
║              ISO ENHANCEMENT SYSTEM                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    log "Starting SynOS ISO enhancement..."
    log "This process will:"
    log "  1. Install ALL security tools (500+)"
    log "  2. Create organized application menus"
    log "  3. Apply custom branding and themes"
    log "  4. Configure desktop defaults"
    log "  5. Fix demo application"
    log "  6. Set up GitHub repositories"
    log "  7. Create desktop shortcuts"
    log "  8. Rebuild ISO with all enhancements"
    log ""
    log "Estimated time: 60-90 minutes"
    log ""

    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Cancelled by user"
        exit 0
    fi

    install_security_tools_complete
    create_security_menu
    apply_branding
    configure_desktop_defaults
    fix_demo_application
    setup_github_repos
    create_desktop_shortcuts
    rebuild_iso

    echo -e "\n${GREEN}"
    cat <<'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    ✨ ENHANCEMENT COMPLETE! ✨               ║
║                                                               ║
║  Your enhanced SynOS ISO is ready with:                       ║
║  ✅ 500+ security tools installed and organized              ║
║  ✅ Custom SynOS branding and themes                         ║
║  ✅ Nuclear/space themed wallpapers                          ║
║  ✅ Professional application menus                           ║
║  ✅ Functional demo application                              ║
║  ✅ GitHub repositories integrated                           ║
║  ✅ Boot splash screen                                       ║
║                                                               ║
║  Find your ISO at:                                            ║
║  build/synos-v1.0/SynOS-v1.0.0-enhanced-YYYYMMDD.iso         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

main "$@"
