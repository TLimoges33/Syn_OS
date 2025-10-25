#!/bin/bash
# Fix security tool categories for MATE menu compatibility
# Maps tools to SynOS-* categories for proper menu display

set -e

CHROOT=${CHROOT:-/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot}
DESKTOP_DIR="$CHROOT/usr/share/applications"

echo "========================================================================="
echo "        Fixing Security Tool Categories for SynOS Menu"
echo "========================================================================="
echo ""
echo "Chroot: $CHROOT"
echo "Desktop files: $DESKTOP_DIR"
echo ""

if [ ! -d "$DESKTOP_DIR" ]; then
    echo "ERROR: Desktop directory not found: $DESKTOP_DIR"
    exit 1
fi

# Function to update category
update_category() {
    local file="$1"
    local category="$2"

    if [ -f "$file" ]; then
        # Remove any existing Categories line and add new one
        sed -i '/^Categories=/d' "$file"
        # Add new category before the last line (usually blank)
        sed -i "\$i Categories=${category};" "$file"
        echo "  ✓ $(basename "$file") -> $category"
    fi
}

# ====================
# INFORMATION GATHERING
# ====================
echo "[1/11] Information Gathering Tools..."
for tool in nmap zenmap dmitry dnsenum enum4linux masscan theharvester theHarvester \
            unicornscan autorecon amass assetfinder subfinder gau httpx waybackurls \
            nuclei rustscan recon-ng; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-InfoGathering;Security;Network"
done

# ====================
# VULNERABILITY ANALYSIS
# ====================
echo "[2/11] Vulnerability Analysis Tools..."
for tool in nikto openvas skipfish wpscan vuls nuclei AutoPWN-Suite \
            scoutsuite cloudsploit subdomain-takeover; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Vulnerability;Security"
done

# ====================
# WEB APPLICATION ANALYSIS
# ====================
echo "[3/11] Web Application Analysis Tools..."
for tool in burp-suite burpsuite owasp-zap zaproxy sqlmap sqlmap-gui dirb dirsearch \
            ffuf gobuster wfuzz xsstrike git-dumper GitTools photon; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-WebApp;Security;WebApplication"
done

# ====================
# DATABASE ASSESSMENT
# ====================
echo "[4/11] Database Assessment Tools..."
for tool in sqlmap sqlmap-gui; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Database;Security"
done

# ====================
# PASSWORD ATTACKS
# ====================
echo "[5/11] Password Attacks Tools..."
for tool in john john-the-ripper hashcat hydra medusa haiti Passhunt; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Password;Security"
done

# ====================
# WIRELESS ATTACKS
# ====================
echo "[6/11] Wireless Attacks Tools..."
for tool in aircrack-ng airgeddon wifite wifite2 kismet bettercap; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Wireless;Security;Network"
done

# ====================
# EXPLOITATION TOOLS
# ====================
echo "[7/11] Exploitation Tools..."
for tool in metasploit-console msfconsole msfvenom beef empire caldera \
            crackmapexec impacket-examples powersploit BloodHound bloodhound \
            PhoneSploit-Pro Villain; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Exploitation;Security"
done

# ====================
# SNIFFING & SPOOFING
# ====================
echo "[8/11] Sniffing & Spoofing Tools..."
for tool in wireshark ettercap bettercap responder suricata; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Sniffing;Security;Network"
done

# ====================
# POST EXPLOITATION
# ====================
echo "[9/11] Post Exploitation Tools..."
for tool in mimikatz empire powersploit bloodhound BloodHound crackmapexec; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-PostExploit;Security"
done

# ====================
# FORENSICS
# ====================
echo "[10/11] Forensics Tools..."
for tool in autopsy volatility CyberThreatHunting malwoverview; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Forensics;Security"
done

# ====================
# REPORTING TOOLS
# ====================
echo "[11/11] Reporting Tools..."
for tool in dradis faraday maltego APT_REPORT ThePhish; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Reporting;Security;Office"
done

# ====================
# OSINT TOOLS (Special category)
# ====================
echo "OSINT & Investigation Tools..."
for tool in sherlock maigret holehe blackbird h8mail social-analyzer \
            osint-framework username-anarchy; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-InfoGathering;Security;OSINT"
done

# ====================
# REVERSE ENGINEERING (Add to Info Gathering or separate)
# ====================
echo "Reverse Engineering Tools..."
for tool in ghidra radare2 cutter frida ImHex; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-Exploitation;Security;ReverseEngineering"
done

# ====================
# UTILITIES & RESOURCES
# ====================
echo "Utilities & Resources..."
for tool in chepy pyWhat SecLists PayloadsAllTheThings decider sslscan; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "SynOS-InfoGathering;Security;Utility"
done

# ====================
# PRODUCTIVITY TOOLS
# ====================
echo "Productivity Tools..."
for tool in postman obsidian tools welcome; do
    update_category "$DESKTOP_DIR/synos-${tool}.desktop" "Utility;Office;Development"
done

# Update Sn1per separately (special case)
update_category "$DESKTOP_DIR/synos-Sn1per.desktop" "SynOS-InfoGathering;SynOS-Vulnerability;Security"

# Update mobile security framework
update_category "$DESKTOP_DIR/synos-mobsf.desktop" "SynOS-Vulnerability;Security;Mobile"

echo ""
echo "========================================================================="
echo "                   Categories Updated Successfully!"
echo "========================================================================="
echo ""
echo "Summary:"
echo "  - Information Gathering: nmap, masscan, amass, subfinder, etc."
echo "  - Vulnerability Analysis: nikto, openvas, wpscan, etc."
echo "  - Web Applications: burpsuite, sqlmap, dirb, etc."
echo "  - Password Attacks: john, hashcat, hydra, etc."
echo "  - Wireless: aircrack-ng, wifite, kismet, etc."
echo "  - Exploitation: metasploit, empire, bloodhound, etc."
echo "  - Sniffing: wireshark, ettercap, responder, etc."
echo "  - Post Exploitation: mimikatz, empire, powersploit, etc."
echo "  - Forensics: autopsy, volatility, etc."
echo "  - Reporting: dradis, faraday, maltego, etc."
echo ""
echo "Next: Update desktop database and restart panel"
echo "  chroot: update-desktop-database /usr/share/applications"
echo ""

# Update desktop database in chroot
if [ -n "$CHROOT" ] && [ -d "$CHROOT" ]; then
    echo "Updating desktop database..."
    chroot "$CHROOT" update-desktop-database /usr/share/applications 2>/dev/null || true
    echo "Desktop database updated"
fi

echo "Done!"
