#!/usr/bin/env bash
################################################################################
# SynOS ULTIMATE ISO Enhancement Script
# Phase 4: Configuration Management & Menu Organization
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/chroot}"
PROJECT_ROOT="/home/diablorain/Syn_OS"

source "$PROJECT_ROOT/scripts/build/enhancement-utils.sh" 2>/dev/null || true

section "Phase 4: Configuration Management"

################################################################################
# CREATE SYNOS TOOLS MENU STRUCTURE
################################################################################

create_tools_menu() {
    log "Creating organized 'SynOS Tools' menu structure..."

    mkdir -p "$CHROOT_DIR/usr/share/desktop-directories"
    mkdir -p "$CHROOT_DIR/etc/xdg/menus/applications-merged"

    # Main SynOS Tools menu
    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-tools.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=SynOS Tools
Icon=security-high
Comment=Complete Security and Penetration Testing Toolkit
EOF

    # Category directories
    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-information-gathering.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=01 - Information Gathering
Icon=network-workgroup
Comment=Reconnaissance and information gathering tools
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-vulnerability-analysis.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=02 - Vulnerability Analysis
Icon=security-medium
Comment=Vulnerability scanning and analysis tools
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-web-applications.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=03 - Web Application Analysis
Icon=web-browser
Comment=Web application security testing tools
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-database.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=04 - Database Assessment
Icon=database
Comment=Database security and SQL injection tools
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-password-attacks.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=05 - Password Attacks
Icon=dialog-password
Comment=Password cracking and authentication testing
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-wireless.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=06 - Wireless Attacks
Icon=network-wireless
Comment=Wireless network security testing
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-exploitation.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=07 - Exploitation Tools
Icon=system-run
Comment=Exploitation frameworks and tools
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-sniffing.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=08 - Sniffing & Spoofing
Icon=preferences-system-network
Comment=Network sniffing and MITM tools
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-post-exploitation.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=09 - Post Exploitation
Icon=folder-publicshare
Comment=Post-exploitation and privilege escalation
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-forensics.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=10 - Forensics
Icon=document-properties
Comment=Digital forensics and incident response
EOF

    cat > "$CHROOT_DIR/usr/share/desktop-directories/synos-reporting.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=11 - Reporting Tools
Icon=document-send
Comment=Report generation and documentation
EOF

    # Main menu configuration
    cat > "$CHROOT_DIR/etc/xdg/menus/applications-merged/synos-tools.menu" <<'EOF'
<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
  "http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">
<Menu>
  <Name>Applications</Name>
  <Menu>
    <Name>SynOS Tools</Name>
    <Directory>synos-tools.directory</Directory>

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
        <Category>SynOS-Vulnerability</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Web Application Analysis</Name>
      <Directory>synos-web-applications.directory</Directory>
      <Include>
        <Category>SynOS-WebApp</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Database Assessment</Name>
      <Directory>synos-database.directory</Directory>
      <Include>
        <Category>SynOS-Database</Category>
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
      <Directory>synos-wireless.directory</Directory>
      <Include>
        <Category>SynOS-Wireless</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Exploitation Tools</Name>
      <Directory>synos-exploitation.directory</Directory>
      <Include>
        <Category>SynOS-Exploitation</Category>
      </Include>
    </Menu>

    <Menu>
      <Name>Sniffing &amp; Spoofing</Name>
      <Directory>synos-sniffing.directory</Directory>
      <Include>
        <Category>SynOS-Sniffing</Category>
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
      <Name>Reporting Tools</Name>
      <Directory>synos-reporting.directory</Directory>
      <Include>
        <Category>SynOS-Reporting</Category>
      </Include>
    </Menu>
  </Menu>
</Menu>
EOF
}

################################################################################
# GENERATE DESKTOP ENTRIES FOR TOOLS
################################################################################

generate_desktop_entries() {
    log "Generating desktop entries for all security tools..."

    chroot "$CHROOT_DIR" bash -c '
        DESKTOP_DIR="/usr/share/applications"

        # Function to create desktop entry
        create_entry() {
            local name="$1"
            local exec="$2"
            local category="$3"
            local icon="${4:-utilities-terminal}"
            local comment="${5:-Security tool}"

            cat > "$DESKTOP_DIR/synos-${name}.desktop" <<ENTRY
[Desktop Entry]
Version=1.0
Type=Application
Name=${name}
Comment=${comment}
Exec=${exec}
Icon=${icon}
Terminal=true
Categories=SynOS-${category};Security;
ENTRY
        }

        # Information Gathering
        create_entry "nmap" "mate-terminal -e nmap" "InfoGathering" "network-workgroup" "Network mapper"
        create_entry "masscan" "mate-terminal -e masscan" "InfoGathering" "network-workgroup" "Mass port scanner"
        create_entry "rustscan" "mate-terminal -e rustscan" "InfoGathering" "network-workgroup" "Fast port scanner"
        create_entry "subfinder" "mate-terminal -e subfinder" "InfoGathering" "network-workgroup" "Subdomain discovery"
        create_entry "amass" "mate-terminal -e amass" "InfoGathering" "network-workgroup" "Attack surface mapping"
        create_entry "theHarvester" "mate-terminal -e theHarvester" "InfoGathering" "network-workgroup" "OSINT gathering"

        # Vulnerability Analysis
        create_entry "nuclei" "mate-terminal -e nuclei" "Vulnerability" "security-medium" "Template-based scanner"
        create_entry "nikto" "mate-terminal -e nikto" "Vulnerability" "security-medium" "Web server scanner"
        create_entry "wpscan" "mate-terminal -e wpscan" "Vulnerability" "security-medium" "WordPress scanner"
        create_entry "openvas" "openvas-start" "Vulnerability" "security-medium" "Vulnerability scanner"

        # Web Applications
        create_entry "burpsuite" "burpsuite" "WebApp" "web-browser" "Web proxy"
        create_entry "zaproxy" "zaproxy" "WebApp" "web-browser" "OWASP ZAP"
        create_entry "sqlmap" "mate-terminal -e sqlmap" "WebApp" "database" "SQL injection tool"
        create_entry "gobuster" "mate-terminal -e gobuster" "WebApp" "web-browser" "Directory brute forcer"
        create_entry "ffuf" "mate-terminal -e ffuf" "WebApp" "web-browser" "Fast web fuzzer"

        # Database
        create_entry "sqlmap-gui" "mate-terminal -e sqlmap" "Database" "database" "SQL injection"

        # Password Attacks
        create_entry "john" "mate-terminal -e john" "Password" "dialog-password" "John the Ripper"
        create_entry "hashcat" "mate-terminal -e hashcat" "Password" "dialog-password" "Advanced password recovery"
        create_entry "hydra" "mate-terminal -e hydra" "Password" "dialog-password" "Network logon cracker"
        create_entry "medusa" "mate-terminal -e medusa" "Password" "dialog-password" "Parallel password cracker"

        # Wireless
        create_entry "aircrack-ng" "mate-terminal -e aircrack-ng" "Wireless" "network-wireless" "Wireless cracking"
        create_entry "wifite" "mate-terminal -e wifite" "Wireless" "network-wireless" "Automated wireless attack"
        create_entry "kismet" "mate-terminal -e kismet" "Wireless" "network-wireless" "Wireless detector"

        # Exploitation
        create_entry "msfconsole" "mate-terminal -e msfconsole" "Exploitation" "system-run" "Metasploit Framework"
        create_entry "crackmapexec" "mate-terminal -e crackmapexec" "Exploitation" "system-run" "Post-exploitation tool"
        create_entry "bloodhound" "bloodhound" "Exploitation" "folder-publicshare" "Active Directory tool"

        # Sniffing & Spoofing
        create_entry "wireshark" "wireshark" "Sniffing" "preferences-system-network" "Network analyzer"
        create_entry "ettercap" "ettercap" "Sniffing" "preferences-system-network" "MITM framework"
        create_entry "responder" "mate-terminal -e responder" "Sniffing" "preferences-system-network" "LLMNR/NBT-NS poisoner"

        # Post Exploitation
        create_entry "mimikatz" "mate-terminal -e mimikatz" "PostExploit" "folder-publicshare" "Windows post-exploit"
        create_entry "empire" "mate-terminal -e empire" "PostExploit" "folder-publicshare" "PowerShell agent"

        # Forensics
        create_entry "autopsy" "autopsy" "Forensics" "document-properties" "Digital forensics"
        create_entry "volatility" "mate-terminal -e volatility3" "Forensics" "document-properties" "Memory forensics"

        # Reporting
        create_entry "dradis" "dradis" "Reporting" "document-send" "Collaboration platform"
        create_entry "faraday" "faraday" "Reporting" "document-send" "Vulnerability management"
    '
}

################################################################################
# CREATE DESKTOP SHORTCUTS
################################################################################

create_desktop_shortcuts() {
    log "Creating desktop shortcuts..."

    mkdir -p "$CHROOT_DIR/etc/skel/Desktop"

    # SynOS Demo shortcut
    cat > "$CHROOT_DIR/etc/skel/Desktop/SynOS-Demo.desktop" <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS Demo
Comment=Launch SynOS feature showcase
Exec=synos-demo
Icon=synos-logo
Terminal=false
Categories=System;
EOF

    # Tools Overview shortcut
    cat > "$CHROOT_DIR/etc/skel/Desktop/Tools-Overview.desktop" <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Tools Overview
Comment=View installed security tools
Exec=mate-terminal -e "bash -c 'cat /opt/synos-tools-inventory.txt; exec bash'"
Icon=utilities-terminal
Terminal=true
Categories=System;
EOF

    # Documentation shortcut
    cat > "$CHROOT_DIR/etc/skel/Desktop/Documentation.desktop" <<'EOF'
[Desktop Entry]
Version=1.0
Type=Link
Name=Documentation
Comment=SynOS Documentation
URL=file:///usr/share/doc/synos/README.html
Icon=help-browser
EOF

    chmod +x "$CHROOT_DIR/etc/skel/Desktop"/*.desktop
}

################################################################################
# CONFIGURE MATE DESKTOP DEFAULTS
################################################################################

configure_mate_defaults() {
    log "Configuring MATE desktop defaults..."

    mkdir -p "$CHROOT_DIR/etc/dconf/db/local.d"

    # Complete MATE configuration matching user's system
    cat > "$CHROOT_DIR/etc/dconf/db/local.d/03-mate-defaults" <<'EOF'
# Interface settings
[org/mate/desktop/interface]
gtk-theme='Windows-10-Dark'
icon-theme='gnome'
font-name='Hack 11'
monospace-font-name='Hack 10'
document-font-name='Sans 11'

# Window manager (Marco)
[org/mate/marco/general]
theme='ARK-Dark'
titlebar-font='Hack Bold 11'
action-double-click-titlebar='toggle_maximize'

# Desktop background
[org/mate/desktop/background]
picture-filename='/usr/share/backgrounds/synos/space.jpg'
picture-options='zoom'
show-desktop-icons=true

# Panel configuration
[org/mate/panel/general]
toplevel-id-list=['top']
object-id-list=['menu', 'show-desktop', 'separator1', 'window-list', 'separator2', 'notification-area', 'clock']

[org/mate/panel/toplevels/top]
orientation='top'
size=24
expand=true

# Terminal settings
[org/mate/terminal/profiles/default]
background-color='#000000'
foreground-color='#00FF00'
use-system-font=false
font='Hack 10'

# File manager (Caja)
[org/mate/caja/preferences]
default-folder-viewer='list-view'
show-hidden-files=false

# Power management
[org/mate/power-manager]
sleep-display-ac=1800
sleep-display-battery=600
EOF

    chroot "$CHROOT_DIR" dconf update 2>/dev/null || true
}

################################################################################
# SETUP SYSTEM DEFAULTS
################################################################################

setup_system_defaults() {
    log "Setting up system-wide defaults..."

    # Default applications
    cat > "$CHROOT_DIR/etc/xdg/mimeapps.list" <<'EOF'
[Default Applications]
text/html=firefox.desktop
text/xml=mousepad.desktop
text/plain=mousepad.desktop
application/pdf=atril.desktop
image/png=eom.desktop
image/jpeg=eom.desktop
EOF

    # Shell defaults
    cat >> "$CHROOT_DIR/etc/skel/.bashrc" <<'EOF'

# SynOS Custom Bash Configuration
export PS1="\[\e[1;32m\]\u@synos\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ "
export PATH="/opt/tools/github:$PATH"

# Aliases
alias ll='ls -alh --color=auto'
alias nmap-quick='nmap -sV -sC'
alias tools='cat /opt/synos-tools-inventory.txt'
alias synos-update='sudo apt update && sudo apt upgrade -y'

# Welcome message
if [ -f /etc/motd ]; then
    cat /etc/motd
fi
EOF
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo "Phase 4: Configuration Management"
    echo "================================="

    create_tools_menu
    generate_desktop_entries
    create_desktop_shortcuts
    configure_mate_defaults
    setup_system_defaults

    log "✓ Phase 4 complete!"
    log "Created: Tools menu (11 categories), Desktop entries, Shortcuts, MATE config"
}

main "$@"
