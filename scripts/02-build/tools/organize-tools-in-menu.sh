#!/bin/bash

###############################################################################
# SynOS - Organize All Security Tools in Applications Menu
# Creates .desktop files for all 72+ installed tools
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHROOT_DIR="$1"
if [ -z "$CHROOT_DIR" ]; then
    echo -e "${RED}Usage: $0 <chroot_directory>${NC}"
    exit 1
fi

APPS_DIR="$CHROOT_DIR/usr/share/applications"
REPOS_DIR="$CHROOT_DIR/opt/github-repos"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Organizing Security Tools in Applications Menu            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create category directories
sudo mkdir -p "$APPS_DIR"

CREATED=0

create_desktop_file() {
    local name="$1"
    local exec="$2"
    local comment="$3"
    local category="$4"
    local icon="${5:-security-high}"

    local filename="synos-${name}.desktop"
    local filepath="$APPS_DIR/$filename"

    sudo tee "$filepath" > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$name
Comment=$comment
Exec=x-terminal-emulator -e bash -c "cd /opt/github-repos/$name 2>/dev/null || cd /usr/bin; $exec; echo 'Press Enter to close...'; read"
Icon=$icon
Terminal=true
Categories=Security;$category;
Keywords=security;hacking;pentesting;
StartupNotify=false
EOF

    sudo chmod 644 "$filepath"
    CREATED=$((CREATED + 1))
}

echo -e "${YELLOW}[→] Creating OSINT Tools Menu Entries...${NC}"
create_desktop_file "maigret" "python3 maigret.py --help" "Username OSINT - Search 3000+ sites" "OSINT" "avatar-default"
create_desktop_file "blackbird" "python3 blackbird.py --help" "Fast username search - 600+ sites" "OSINT" "avatar-default"
create_desktop_file "theHarvester" "theHarvester -h" "Email/subdomain OSINT gathering" "OSINT" "mail-message-new"
create_desktop_file "sherlock" "python3 sherlock --help" "Hunt social media accounts by username" "OSINT" "avatar-default"
create_desktop_file "holehe" "holehe --help" "Check if email is used on sites" "OSINT" "mail-mark-junk"

echo -e "${YELLOW}[→] Creating Web Security Menu Entries...${NC}"
create_desktop_file "httpx" "httpx -h" "Fast HTTP toolkit for web recon" "Web" "network-server"
create_desktop_file "dirsearch" "python3 dirsearch.py -h" "Web path scanner and directory brute-forcer" "Web" "folder-open"
create_desktop_file "ffuf" "ffuf -h" "Fast web fuzzer" "Web" "system-search"
create_desktop_file "subzy" "subzy -h" "Subdomain takeover scanner" "Web" "network-workgroup"
create_desktop_file "sqlmap" "python3 sqlmap.py -h" "Automatic SQL injection tool" "Web" "database"

echo -e "${YELLOW}[→] Creating Reconnaissance Menu Entries...${NC}"
create_desktop_file "Sn1per" "./sniper -h" "Automated pentest framework - 190+ tools" "Recon" "security-medium"
create_desktop_file "amass" "amass -h" "OWASP network mapping and discovery" "Recon" "network-workgroup"
create_desktop_file "subfinder" "subfinder -h" "Fast passive subdomain discovery" "Recon" "network-workgroup"
create_desktop_file "assetfinder" "assetfinder --help" "Find domains and subdomains" "Recon" "edit-find"
create_desktop_file "waybackurls" "waybackurls -h" "Fetch URLs from Wayback Machine" "Recon" "document-open-recent"
create_desktop_file "gau" "gau --help" "Fetch known URLs from multiple sources" "Recon" "network-transmit"

echo -e "${YELLOW}[→] Creating Exploitation Menu Entries...${NC}"
create_desktop_file "AutoPWN-Suite" "python3 autopwn-suite.py --help" "Automated vulnerability scanning and exploitation" "Exploit" "security-low"
create_desktop_file "Villain" "python3 Villain.py --help" "Windows/Linux backdoor generator and C2" "Exploit" "network-error"
create_desktop_file "PhoneSploit-Pro" "python3 main.py" "Advanced ADB exploitation toolkit" "Exploit" "phone"
create_desktop_file "GitTools" "bash gitdumper.sh -h" "Find and exploit exposed .git directories" "Exploit" "git"
create_desktop_file "git-dumper" "git-dumper --help" "Dump exposed .git repositories" "Exploit" "git"
create_desktop_file "BloodHound" "echo 'BloodHound - See /opt/github-repos/BloodHound for setup'" "Active Directory attack path mapper" "Exploit" "network-workgroup"

echo -e "${YELLOW}[→] Creating Network Tools Menu Entries...${NC}"
create_desktop_file "masscan" "masscan --help" "Fast TCP port scanner - scan internet in 6min" "Network" "network-wireless"
create_desktop_file "rustscan" "rustscan --help" "Modern fast port scanner with nmap" "Network" "network-transmit-receive"

echo -e "${YELLOW}[→] Creating Wireless Tools Menu Entries...${NC}"
create_desktop_file "wifite2" "python3 wifite2.py -h" "Automated wireless auditor" "Wireless" "network-wireless"
create_desktop_file "airgeddon" "bash airgeddon.sh" "Multi-use wireless auditing script" "Wireless" "network-wireless-signal-good"

echo -e "${YELLOW}[→] Creating Password/Credential Menu Entries...${NC}"
create_desktop_file "username-anarchy" "ruby username-anarchy --help" "Generate usernames from person names" "Password" "avatar-default"
create_desktop_file "h8mail" "h8mail -h" "Email OSINT and breach hunting" "Password" "mail-mark-junk"
create_desktop_file "Passhunt" "python3 passhunt.py -h" "Search filesystems for passwords" "Password" "document-properties"

echo -e "${YELLOW}[→] Creating Forensics/Analysis Menu Entries...${NC}"
create_desktop_file "pyWhat" "pywhat --help" "Identify anything - hashes, emails, IPs" "Forensics" "search"
create_desktop_file "haiti" "haiti --help" "Advanced hash identifier - 640+ types" "Forensics" "security-high"
create_desktop_file "chepy" "chepy --help" "Python CyberChef clone for data transformation" "Forensics" "preferences-desktop-cryptography"
create_desktop_file "malwoverview" "python3 malwoverview.py -h" "Automated malware analysis" "Forensics" "dialog-warning"
create_desktop_file "ImHex" "echo 'ImHex - Advanced hex editor. See docs for installation.'" "Hex editor for reverse engineers" "Forensics" "utilities-terminal"

echo -e "${YELLOW}[→] Creating Defense/Blue Team Menu Entries...${NC}"
create_desktop_file "vuls" "vuls -h" "Agentless vulnerability scanner" "Defense" "security-high"
create_desktop_file "ThePhish" "echo 'ThePhish - See /opt/github-repos/ThePhish for setup'" "Automated phishing analysis platform" "Defense" "mail-mark-junk"
create_desktop_file "suricata" "suricata --help" "High-performance IDS/IPS" "Defense" "security-high"
create_desktop_file "caldera" "echo 'CALDERA - See /opt/github-repos/caldera for setup'" "MITRE adversary emulation platform" "Defense" "security-medium"
create_desktop_file "decider" "echo 'Decider - See /opt/github-repos/decider for setup'" "MITRE ATT&CK browser" "Defense" "help-browser"

echo -e "${YELLOW}[→] Creating Educational Resources Menu Entries...${NC}"
create_desktop_file "APT_REPORT" "cd /opt/github-repos/APT_REPORT && ls -la" "Comprehensive APT threat intel reports (3.1GB)" "Education" "folder-documents"
create_desktop_file "SecLists" "cd /opt/github-repos/SecLists && ls -la" "Ultimate wordlist collection (1.9GB)" "Education" "text-x-generic"
create_desktop_file "PayloadsAllTheThings" "cd /opt/github-repos/PayloadsAllTheThings && ls -la" "Huge collection of payloads and bypasses" "Education" "text-x-script"
create_desktop_file "CyberThreatHunting" "cd /opt/github-repos/CyberThreatHunting && ls -la" "Threat hunting resources" "Education" "folder-saved-search"

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          APPLICATIONS MENU ORGANIZATION COMPLETE             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}✓ Created $CREATED .desktop files${NC}"
echo -e "${BLUE}Tools organized in these categories:${NC}"
echo "  • OSINT: 5 tools"
echo "  • Web Security: 5 tools"
echo "  • Reconnaissance: 6 tools"
echo "  • Exploitation: 6 tools"
echo "  • Network: 2 tools"
echo "  • Wireless: 2 tools"
echo "  • Password/Credentials: 3 tools"
echo "  • Forensics/Analysis: 5 tools"
echo "  • Defense/Blue Team: 5 tools"
echo "  • Educational Resources: 4 tools"

echo ""
echo -e "${BLUE}[INFO] Applications will appear in menu after logging in${NC}"
echo -e "${BLUE}[INFO] All tools can also be accessed from /opt/github-repos/${NC}"

exit 0
