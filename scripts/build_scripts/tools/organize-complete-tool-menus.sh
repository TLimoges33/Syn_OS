#!/bin/bash
# Organize ALL tools (GitHub repos + ParrotOS tools + existing) into application menus
set -e

CHROOT="$1"
if [ -z "$CHROOT" ]; then
    echo "Usage: $0 /path/to/chroot"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ORGANIZING COMPLETE TOOL ARSENAL INTO MENUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

MENU_DIR="$CHROOT/usr/share/applications"
sudo mkdir -p "$MENU_DIR"

# Counter for created entries
CREATED=0

# Function to create .desktop file
create_desktop_entry() {
    local name="$1"
    local exec="$2"
    local category="$3"
    local icon="${4:-utilities-terminal}"
    local comment="${5:-Security and penetration testing tool}"

    local filename=$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    local desktop_file="$MENU_DIR/synos-${filename}.desktop"

    sudo tee "$desktop_file" > /dev/null << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$name
Comment=$comment
Exec=$exec
Icon=$icon
Terminal=true
Categories=$category;Security;
Keywords=security;pentesting;hacking;
StartupNotify=false
EOF

    sudo chmod 644 "$desktop_file"
    CREATED=$((CREATED + 1))
}

echo "[1/10] Creating Priority Tool Entries..."
# Wireshark & Metasploit
create_desktop_entry "Wireshark" "wireshark" "Network" "wireshark" "Network protocol analyzer"
create_desktop_entry "Metasploit Console" "msfconsole" "Exploitation" "metasploit" "Metasploit Framework console"
create_desktop_entry "Msfvenom" "msfvenom --help" "Exploitation" "metasploit" "Metasploit payload generator"
echo "  ✓ Created 3 priority entries"

echo "[2/10] Creating Network Analysis Tools..."
create_desktop_entry "Nmap" "nmap" "Network" "network-wired" "Network scanner"
create_desktop_entry "Masscan" "masscan" "Network" "network-wired" "Fast network scanner"
create_desktop_entry "Unicornscan" "unicornscan" "Network" "network-wired" "Network information gathering"
create_desktop_entry "Dmitry" "dmitry" "Network" "network-wired" "Deepmagic Information Gathering Tool"
echo "  ✓ Created 4 network analysis entries"

echo "[3/10] Creating Web Application Testing Tools..."
create_desktop_entry "Burp Suite" "burpsuite" "WebApp" "burpsuite" "Web application security testing"
create_desktop_entry "OWASP ZAP" "zaproxy" "WebApp" "zaproxy" "Web app scanner"
create_desktop_entry "SQLMap" "sqlmap" "WebApp" "terminal" "SQL injection tool"
create_desktop_entry "Nikto" "nikto" "WebApp" "terminal" "Web server scanner"
create_desktop_entry "Skipfish" "skipfish" "WebApp" "terminal" "Web application security scanner"
create_desktop_entry "WFuzz" "wfuzz" "WebApp" "terminal" "Web application fuzzer"
create_desktop_entry "Dirb" "dirb" "WebApp" "terminal" "Web content scanner"
create_desktop_entry "Gobuster" "gobuster" "WebApp" "terminal" "Directory/file brute forcer"
create_desktop_entry "BeEF" "beef-xss" "WebApp" "beef" "Browser Exploitation Framework"
echo "  ✓ Created 9 web app testing entries"

echo "[4/10] Creating Password Cracking Tools..."
create_desktop_entry "John the Ripper" "john" "Password" "password" "Password cracker"
create_desktop_entry "Hashcat" "hashcat" "Password" "password" "Advanced password cracker"
create_desktop_entry "Hydra" "hydra" "Password" "password" "Network login cracker"
echo "  ✓ Created 3 password cracking entries"

echo "[5/10] Creating Wireless Tools..."
create_desktop_entry "Aircrack-ng" "aircrack-ng" "Wireless" "network-wireless" "WiFi security tool"
create_desktop_entry "Bettercap" "bettercap" "Wireless" "network-wireless" "Network attacks and monitoring"
create_desktop_entry "Ettercap" "ettercap" "Wireless" "network-wireless" "Network sniffer/interceptor"
echo "  ✓ Created 3 wireless entries"

echo "[6/10] Creating Information Gathering Tools..."
create_desktop_entry "theHarvester" "theharvester" "InfoGathering" "search" "E-mail, subdomain and name harvester"
create_desktop_entry "Recon-ng" "recon-ng" "InfoGathering" "search" "Web reconnaissance framework"
create_desktop_entry "Maltego" "maltego" "InfoGathering" "maltego" "Data mining and intelligence gathering"
create_desktop_entry "DNSenum" "dnsenum" "InfoGathering" "network-wired" "DNS enumeration tool"
create_desktop_entry "Enum4linux" "enum4linux" "InfoGathering" "network-wired" "Windows/Samba enumeration"
echo "  ✓ Created 5 info gathering entries"

echo "[7/10] Creating SSL/TLS Analysis Tools..."
create_desktop_entry "SSLscan" "sslscan" "Network" "security-high" "SSL/TLS scanner"
echo "  ✓ Created 1 SSL/TLS entry"

echo "[8/10] Creating GitHub Repository Tools..."
# AI/ML Tools
create_desktop_entry "Social Analyzer" "/opt/github-repos/Qeeqbox/social-analyzer/app.py" "OSINT" "search" "Social media analyzer"
create_desktop_entry "OSINT Framework" "xdg-open /opt/github-repos/lockfale/OSINT-Framework/index.html" "OSINT" "search" "OSINT resource collection"
create_desktop_entry "Sherlock" "python3 /opt/github-repos/sherlock-project/sherlock/sherlock/sherlock.py" "OSINT" "search" "Find usernames across social networks"
create_desktop_entry "Photon" "python3 /opt/github-repos/s0md3v/Photon/photon.py" "WebApp" "search" "Fast web crawler"
create_desktop_entry "XSStrike" "python3 /opt/github-repos/s0md3v/XSStrike/xsstrike.py" "WebApp" "terminal" "XSS detection suite"
create_desktop_entry "Subdomain Takeover" "/opt/github-repos/Ice3man543/SubOver/subover" "InfoGathering" "network-wired" "Subdomain takeover vulnerability scanner"

# Exploitation Tools
create_desktop_entry "AutoRecon" "python3 /opt/github-repos/Tib3rius/AutoRecon/src/autorecon/autorecon.py" "InfoGathering" "search" "Network reconnaissance tool"
create_desktop_entry "PowerSploit" "xdg-open /opt/github-repos/PowerShellMafia/PowerSploit" "Exploitation" "terminal" "PowerShell post-exploitation framework"
create_desktop_entry "Impacket Examples" "xdg-open /opt/github-repos/fortra/impacket/examples" "Exploitation" "terminal" "Network protocols toolkit"

# Reverse Engineering
create_desktop_entry "Ghidra" "/opt/github-repos/NationalSecurityAgency/ghidra/ghidraRun" "ReverseEngineering" "ghidra" "Software reverse engineering"
create_desktop_entry "Radare2" "r2" "ReverseEngineering" "terminal" "Reverse engineering framework"
create_desktop_entry "Cutter" "cutter" "ReverseEngineering" "cutter" "Reverse engineering GUI"

# Forensics
create_desktop_entry "Volatility" "python3 /opt/github-repos/volatilityfoundation/volatility3/vol.py" "Forensics" "system-file-manager" "Memory forensics framework"
create_desktop_entry "Autopsy" "autopsy" "Forensics" "system-file-manager" "Digital forensics platform"

# Mobile Security
create_desktop_entry "MobSF" "python3 /opt/github-repos/MobSF/Mobile-Security-Framework-MobSF/mobsf/manage.py" "Mobile" "phone" "Mobile security framework"
create_desktop_entry "Frida" "frida" "Mobile" "phone" "Dynamic instrumentation toolkit"

# Cloud Security
create_desktop_entry "ScoutSuite" "python3 /opt/github-repos/nccgroup/ScoutSuite/scout.py" "Cloud" "cloud" "Cloud security auditing tool"
create_desktop_entry "CloudSploit" "node /opt/github-repos/aquasecurity/cloudsploit/index.js" "Cloud" "cloud" "Cloud security scanner"

# API Security
create_desktop_entry "Postman" "postman" "Development" "postman" "API development environment"

echo "  ✓ Created 19 GitHub tool entries"

echo "[9/10] Creating Productivity Tools..."
create_desktop_entry "Obsidian" "obsidian" "Office" "obsidian" "Knowledge base and note-taking"
echo "  ✓ Created 1 productivity entry"

echo "[10/10] Creating Category Index..."
# Create a master launcher script
sudo tee "$CHROOT/usr/local/bin/synos-tools" > /dev/null << 'EOF'
#!/bin/bash
# SynOS Security Tools Launcher

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SynOS Security Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Categories:"
echo "  1. Network Analysis (Nmap, Masscan, Wireshark)"
echo "  2. Web Application Testing (Burp, ZAP, SQLMap, Nikto)"
echo "  3. Password Cracking (John, Hashcat, Hydra)"
echo "  4. Wireless (Aircrack-ng, Bettercap)"
echo "  5. Information Gathering (theHarvester, Recon-ng, Maltego)"
echo "  6. Exploitation (Metasploit, PowerSploit, Impacket)"
echo "  7. Reverse Engineering (Ghidra, Radare2, Cutter)"
echo "  8. Forensics (Volatility, Autopsy)"
echo "  9. Mobile Security (MobSF, Frida)"
echo " 10. Cloud Security (ScoutSuite, CloudSploit)"
echo " 11. OSINT (Sherlock, Social Analyzer, OSINT Framework)"
echo
echo "Use your application menu to browse all tools by category!"
echo "Or type the tool name directly in terminal."
echo
EOF
sudo chmod +x "$CHROOT/usr/local/bin/synos-tools"
echo "  ✓ Created master launcher"

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MENU ORGANIZATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Total .desktop entries created: $CREATED"
echo
echo "Categories created:"
echo "  • Network Analysis (7 tools)"
echo "  • Web Application Testing (9 tools)"
echo "  • Password Cracking (3 tools)"
echo "  • Wireless Tools (3 tools)"
echo "  • Information Gathering (6 tools)"
echo "  • Exploitation (3 tools)"
echo "  • Reverse Engineering (3 tools)"
echo "  • Forensics (2 tools)"
echo "  • Mobile Security (2 tools)"
echo "  • Cloud Security (2 tools)"
echo "  • OSINT (3 tools)"
echo "  • SSL/TLS Analysis (1 tool)"
echo "  • Productivity (1 tool)"
echo
echo "Master launcher: synos-tools"
echo
echo "✅ ALL TOOLS ORGANIZED AND READY!"
echo
