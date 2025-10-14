#!/bin/bash

###############################################################################
# SynOS - Add Starred Repositories to ISO
# Installs high-value security tools from TLimoges33's starred repos
###############################################################################

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if chroot directory is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <chroot_directory>${NC}"
    echo "Example: $0 /home/diablorain/Syn_OS/build/synos-v1.0/work/chroot"
    exit 1
fi

CHROOT_DIR="$1"
GITHUB_DIR="$CHROOT_DIR/opt/github-repos"
LOG_FILE="/tmp/starred-repos-install.log"

# Verify chroot directory exists
if [ ! -d "$CHROOT_DIR" ]; then
    echo -e "${RED}[✗] Chroot directory not found: $CHROOT_DIR${NC}"
    exit 1
fi

# Create github-repos directory if it doesn't exist
if [ ! -d "$GITHUB_DIR" ]; then
    echo -e "${YELLOW}[i] Creating github-repos directory...${NC}"
    sudo mkdir -p "$GITHUB_DIR"
fi

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     SynOS - Starred Repositories Installation               ║"
echo "║     Installing ALL TIERS: 52 security tools                 ║"
echo "║     Personal Learning Edition - Full Arsenal                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Initialize log
echo "Starred Repositories Installation - $(date)" > "$LOG_FILE"
echo "Chroot: $CHROOT_DIR" >> "$LOG_FILE"
echo "Edition: PERSONAL LEARNING - ALL TIERS" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Track statistics
TOTAL_REPOS=52
INSTALLED=0
FAILED=0
START_TIME=$(date +%s)

###############################################################################
# ALL TIERS: Complete Security Arsenal (52 repositories)
###############################################################################

declare -A REPOS=(
    # ===== TIER 1: Essential Tools (21 repositories) =====

    # Offensive Security Tools
    ["AutoPWN-Suite"]="GamehunterKaan/AutoPWN-Suite"
    ["Villain"]="t3l3machus/Villain"
    ["SploitScan"]="xaitax/SploitScan"
    ["Sn1per"]="1N3/Sn1per"
    ["PhoneSploit-Pro"]="AzeemIdrisi/PhoneSploit-Pro"
    ["subzy"]="PentestPad/subzy"

    # OSINT & Reconnaissance
    ["maigret"]="soxoj/maigret"
    ["blackbird"]="p1ngul1n0/blackbird"
    ["pyWhat"]="bee-san/pyWhat"

    # Web Application Security
    ["httpx"]="projectdiscovery/httpx"
    ["cherrybomb"]="blst-security/cherrybomb"

    # Vulnerability Management
    ["vuls"]="future-architect/vuls"

    # Forensics & Incident Response
    ["CHIRP"]="cisagov/CHIRP"
    ["ThePhish"]="emalderson/ThePhish"
    ["beelzebub"]="mariocandela/beelzebub"

    # Network Security
    ["suricata"]="OISF/suricata"

    # Cryptography & Data Analysis
    ["haiti"]="noraj/haiti"
    ["chepy"]="securisec/chepy"

    # Malware Analysis
    ["malwoverview"]="alexandreborges/malwoverview"

    # Red Team / Purple Team
    ["caldera"]="mitre/caldera"
    ["decider"]="cisagov/decider"

    # ===== TIER 2: High-Value Optional (10 repositories) =====

    # Advanced Analysis
    ["ImHex"]="WerWolv/ImHex"
    ["SafeLine"]="chaitin/SafeLine"
    ["IntelOwl"]="intelowlproject/IntelOwl"

    # Wireless & RF Security
    ["nRFBox"]="cifertech/nRFBox"

    # Web Testing
    ["xxe-injection-payload-list"]="payloadbox/xxe-injection-payload-list"
    ["Passhunt"]="Viralmaniar/Passhunt"
    ["BugBountyScanner"]="chvancooten/BugBountyScanner"
    ["ReconAIzer"]="hisxo/ReconAIzer"
    ["sitedorks"]="Zarcolio/sitedorks"
    ["fuzz4bounty"]="0xPugal/fuzz4bounty"

    # ===== TIER 3: Reference & Learning (21 repositories) =====

    # Educational Resources
    ["90DaysOfCyberSecurity"]="farhanashrafdev/90DaysOfCyberSecurity"
    ["Awesome-Cybersecurity-Handbooks"]="0xsyr0/Awesome-Cybersecurity-Handbooks"
    ["security-study-plan"]="jassics/security-study-plan"
    ["Hacker-Roadmap"]="Hacking-Notes/Hacker-Roadmap"
    ["Cybersecurity-Resources"]="Nickyie/Cybersecurity-Resources"

    # Blue Team & Detection
    ["awesome-detection-engineering"]="infosecB/awesome-detection-engineering"
    ["awesome-incident-response"]="meirwah/awesome-incident-response"
    ["awesome-cybersecurity-blueteam"]="fabacab/awesome-cybersecurity-blueteam"

    # Privacy & Hardening
    ["privacy.sexy"]="undergroundwires/privacy.sexy"
    ["personal-security-checklist"]="Lissy93/personal-security-checklist"

    # Specialized Tools
    ["Keylogger"]="aydinnyunus/Keylogger"
    ["lockphish"]="jaykali/lockphish"
    ["buster"]="sham00n/buster"

    # Compliance & Frameworks
    ["ComplianceAsCode"]="ComplianceAsCode/content"

    # OSINT Extensions
    ["google-dorks"]="Proviesec/google-dorks"
    ["BugBountyToolkit"]="AlexisAhmed/BugBountyToolkit"

    # Advanced Payloads
    ["offensive-bookmarks"]="kargisimos/offensive-bookmarks"
    ["awesome-security-hardening"]="decalage2/awesome-security-hardening"

    # Threat Intelligence
    ["APT_REPORT"]="blackorbird/APT_REPORT"

    # Additional Tools
    ["SecToolKit"]="ProbiusOfficial/SecToolKit"
    ["CyberThreatHunting"]="A3sal0n/CyberThreatHunting"
)

# Function to clone repository with error handling
clone_repo() {
    local name="$1"
    local repo="$2"
    local dest="$GITHUB_DIR/$name"

    echo -e "${YELLOW}[→] Cloning $name...${NC}"
    echo "Cloning $repo..." >> "$LOG_FILE"

    # Check if already exists
    if [ -d "$dest" ]; then
        echo -e "${YELLOW}[!] $name already exists, skipping...${NC}"
        echo "Already exists: $name" >> "$LOG_FILE"
        return 0
    fi

    # Clone with depth 1 for faster download
    if sudo git clone --depth 1 "https://github.com/$repo.git" "$dest" >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}[✓] $name installed${NC}"
        echo "Success: $name" >> "$LOG_FILE"
        INSTALLED=$((INSTALLED + 1))

        # Show size
        local size=$(sudo du -sh "$dest" 2>/dev/null | cut -f1)
        echo -e "${BLUE}    Size: $size${NC}"
        echo "    Size: $size" >> "$LOG_FILE"
        return 0
    else
        echo -e "${RED}[✗] Failed to clone $name${NC}"
        echo "Failed: $name" >> "$LOG_FILE"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

###############################################################################
# Installation Process
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ⭐ TIER 1: ESSENTIAL TOOLS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}  OFFENSIVE SECURITY TOOLS (6 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "AutoPWN-Suite" "${REPOS[AutoPWN-Suite]}"
clone_repo "Villain" "${REPOS[Villain]}"
clone_repo "SploitScan" "${REPOS[SploitScan]}"
clone_repo "Sn1per" "${REPOS[Sn1per]}"
clone_repo "PhoneSploit-Pro" "${REPOS[PhoneSploit-Pro]}"
clone_repo "subzy" "${REPOS[subzy]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  OSINT & RECONNAISSANCE (3 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "maigret" "${REPOS[maigret]}"
clone_repo "blackbird" "${REPOS[blackbird]}"
clone_repo "pyWhat" "${REPOS[pyWhat]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  WEB APPLICATION SECURITY (2 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "httpx" "${REPOS[httpx]}"
clone_repo "cherrybomb" "${REPOS[cherrybomb]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  VULNERABILITY MANAGEMENT (1 repository)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "vuls" "${REPOS[vuls]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  FORENSICS & INCIDENT RESPONSE (3 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "CHIRP" "${REPOS[CHIRP]}"
clone_repo "ThePhish" "${REPOS[ThePhish]}"
clone_repo "beelzebub" "${REPOS[beelzebub]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  NETWORK SECURITY (1 repository)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "suricata" "${REPOS[suricata]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  CRYPTOGRAPHY & DATA ANALYSIS (2 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "haiti" "${REPOS[haiti]}"
clone_repo "chepy" "${REPOS[chepy]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  MALWARE ANALYSIS (1 repository)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "malwoverview" "${REPOS[malwoverview]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  RED TEAM / PURPLE TEAM (2 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "caldera" "${REPOS[caldera]}"
clone_repo "decider" "${REPOS[decider]}"

echo ""
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  ⭐⭐ TIER 2: HIGH-VALUE OPTIONAL${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}  ADVANCED ANALYSIS (3 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "ImHex" "${REPOS[ImHex]}"
clone_repo "SafeLine" "${REPOS[SafeLine]}"
clone_repo "IntelOwl" "${REPOS[IntelOwl]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  WIRELESS & RF SECURITY (1 repository)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "nRFBox" "${REPOS[nRFBox]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  WEB TESTING & BUG BOUNTY (6 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "xxe-injection-payload-list" "${REPOS[xxe-injection-payload-list]}"
clone_repo "Passhunt" "${REPOS[Passhunt]}"
clone_repo "BugBountyScanner" "${REPOS[BugBountyScanner]}"
clone_repo "ReconAIzer" "${REPOS[ReconAIzer]}"
clone_repo "sitedorks" "${REPOS[sitedorks]}"
clone_repo "fuzz4bounty" "${REPOS[fuzz4bounty]}"

echo ""
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ⭐⭐⭐ TIER 3: REFERENCE & LEARNING${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}  EDUCATIONAL RESOURCES (5 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "90DaysOfCyberSecurity" "${REPOS[90DaysOfCyberSecurity]}"
clone_repo "Awesome-Cybersecurity-Handbooks" "${REPOS[Awesome-Cybersecurity-Handbooks]}"
clone_repo "security-study-plan" "${REPOS[security-study-plan]}"
clone_repo "Hacker-Roadmap" "${REPOS[Hacker-Roadmap]}"
clone_repo "Cybersecurity-Resources" "${REPOS[Cybersecurity-Resources]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  BLUE TEAM & DETECTION (3 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "awesome-detection-engineering" "${REPOS[awesome-detection-engineering]}"
clone_repo "awesome-incident-response" "${REPOS[awesome-incident-response]}"
clone_repo "awesome-cybersecurity-blueteam" "${REPOS[awesome-cybersecurity-blueteam]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PRIVACY & HARDENING (2 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "privacy.sexy" "${REPOS[privacy.sexy]}"
clone_repo "personal-security-checklist" "${REPOS[personal-security-checklist]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  SPECIALIZED TOOLS (3 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "Keylogger" "${REPOS[Keylogger]}"
clone_repo "lockphish" "${REPOS[lockphish]}"
clone_repo "buster" "${REPOS[buster]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  COMPLIANCE & FRAMEWORKS (1 repository)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "ComplianceAsCode" "${REPOS[ComplianceAsCode]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  OSINT EXTENSIONS (2 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "google-dorks" "${REPOS[google-dorks]}"
clone_repo "BugBountyToolkit" "${REPOS[BugBountyToolkit]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ADVANCED PAYLOADS & BOOKMARKS (2 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "offensive-bookmarks" "${REPOS[offensive-bookmarks]}"
clone_repo "awesome-security-hardening" "${REPOS[awesome-security-hardening]}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  THREAT INTELLIGENCE & HUNTING (3 repositories)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

clone_repo "APT_REPORT" "${REPOS[APT_REPORT]}"
clone_repo "SecToolKit" "${REPOS[SecToolKit]}"
clone_repo "CyberThreatHunting" "${REPOS[CyberThreatHunting]}"

###############################################################################
# Post-Installation Setup
###############################################################################

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  POST-INSTALLATION SETUP${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Create symlinks for commonly used tools in /usr/local/bin
echo -e "${YELLOW}[→] Creating symlinks for quick access...${NC}"

SYMLINKS=(
    "maigret/maigret.py:maigret"
    "blackbird/blackbird.py:blackbird"
    "pyWhat/pywhat/pywhat.py:pywhat"
    "haiti/bin/haiti:haiti"
    "chepy/chepy/cli.py:chepy"
    "SploitScan/sploitscan.py:sploitscan"
    "subzy/subzy:subzy"
)

for link in "${SYMLINKS[@]}"; do
    IFS=':' read -r source target <<< "$link"
    src_path="$GITHUB_DIR/$source"
    dst_path="$CHROOT_DIR/usr/local/bin/$target"

    if [ -f "$src_path" ]; then
        sudo ln -sf "/opt/github-repos/$source" "$dst_path" 2>/dev/null || true
        sudo chmod +x "$dst_path" 2>/dev/null || true
        echo -e "${GREEN}[✓] Linked $target${NC}"
    fi
done

# Set proper permissions
echo -e "${YELLOW}[→] Setting permissions...${NC}"
sudo chown -R root:root "$GITHUB_DIR" 2>/dev/null || true
sudo chmod -R 755 "$GITHUB_DIR" 2>/dev/null || true

# Create a README in the github-repos directory
cat << 'READMEEOF' | sudo tee "$GITHUB_DIR/README.md" > /dev/null
# SynOS GitHub Security Tools - Complete Arsenal

This directory contains **52 curated security tools** from GitHub, selected from
TLimoges33's starred repositories for comprehensive cybersecurity learning.

**Edition:** Personal Learning - ALL TIERS
**For:** Complete hands-on cybersecurity education
**Note:** Public beta will feature a reduced toolkit for educational use only

---

## 📦 TIER 1: Essential Tools (21 repositories)

### Offensive Security
- **AutoPWN-Suite**: Automated vulnerability scanning and exploitation
- **Villain**: Advanced C2 framework for multiple reverse shells
- **SploitScan**: CVE and exploit information lookup utility
- **Sn1per**: Attack surface management and automated scanning
- **PhoneSploit-Pro**: Android device exploitation via ADB
- **subzy**: Subdomain takeover vulnerability checker

### OSINT & Reconnaissance
- **maigret**: Username search across thousands of websites (17K⭐)
- **blackbird**: Account search by username/email in social networks
- **pyWhat**: Identify emails, IPs, hashes, and more in data

### Web Application Security
- **httpx**: Fast multi-purpose HTTP toolkit (9K⭐)
- **cherrybomb**: API security auditing and testing

### Vulnerability Management
- **vuls**: Agent-less vulnerability scanner for Linux and containers

### Forensics & Incident Response
- **CHIRP**: CISA DFIR tool for incident response
- **ThePhish**: Automated phishing email analysis tool
- **beelzebub**: AI-powered honeypot framework

### Network Security
- **suricata**: IDS/IPS and network security monitoring engine

### Cryptography & Data Analysis
- **haiti**: Hash type identifier (CLI & library)
- **chepy**: Python/CLI equivalent of CyberChef

### Malware Analysis
- **malwoverview**: Threat hunting with VT, Hybrid Analysis, URLHaus

### Red Team / Purple Team
- **caldera**: MITRE automated adversary emulation platform
- **decider**: Map adversary behaviors to MITRE ATT&CK

---

## 🔥 TIER 2: High-Value Optional (10 repositories)

### Advanced Analysis
- **ImHex**: Advanced hex editor for reverse engineering (50K⭐)
- **SafeLine**: Self-hosted WAF/reverse proxy for learning bypass techniques
- **IntelOwl**: Threat intelligence management platform

### Wireless & RF Security
- **nRFBox**: ESP32 tool for BLE, Wi-Fi, 2.4GHz scanning/jamming

### Web Testing & Bug Bounty
- **xxe-injection-payload-list**: XML external entity injection payloads
- **Passhunt**: Default credentials database (523 vendors, 2084 passwords)
- **BugBountyScanner**: Automated bug bounty reconnaissance
- **ReconAIzer**: Burp extension using OpenAI for recon
- **sitedorks**: Google dorking automation
- **fuzz4bounty**: 1337 wordlists for bug bounty hunting

---

## 📚 TIER 3: Reference & Learning (21 repositories)

### Educational Resources
- **90DaysOfCyberSecurity**: 90-day cybersecurity learning roadmap
- **Awesome-Cybersecurity-Handbooks**: Personal CTF and Red Team notes
- **security-study-plan**: Complete study plan for cybersecurity roles
- **Hacker-Roadmap**: Proficiency plan for hacking/pentesting
- **Cybersecurity-Resources**: Library of cybersecurity resources

### Blue Team & Detection
- **awesome-detection-engineering**: Detection engineering resources
- **awesome-incident-response**: Curated incident response tools
- **awesome-cybersecurity-blueteam**: Blue team resources and tools

### Privacy & Hardening
- **privacy.sexy**: Privacy & security best practices enforcement
- **personal-security-checklist**: 300+ tips for digital security

### Specialized Tools
- **Keylogger**: Keyboard/mouse/screenshot capture (ethical use only!)
- **lockphish**: Lock screen phishing demonstration
- **buster**: Advanced email reconnaissance

### Compliance & Frameworks
- **ComplianceAsCode**: Security automation content (SCAP, Bash, Ansible)

### OSINT Extensions
- **google-dorks**: Useful Google dorks collection
- **BugBountyToolkit**: Multi-platform bug bounty toolkit

### Advanced Payloads & Bookmarks
- **offensive-bookmarks**: Collection of pentesting bookmarks
- **awesome-security-hardening**: Security hardening guides and tools

### Threat Intelligence & Hunting
- **APT_REPORT**: Interesting APT report collection
- **SecToolKit**: Cybersecurity tool repository / Wiki
- **CyberThreatHunting**: Resources for threat hunters

## Usage

Most tools can be accessed directly from their directories:
```bash
cd /opt/github-repos/<tool-name>
```

Some tools have symlinks in `/usr/local/bin/`:
- `maigret` - OSINT username search
- `blackbird` - Social network account search
- `pywhat` - Data identifier
- `haiti` - Hash type identifier
- `chepy` - CyberChef equivalent
- `sploitscan` - Exploit lookup
- `subzy` - Subdomain takeover checker

## Documentation

Each tool includes its own README.md with installation instructions,
usage examples, and documentation. Please review before use.

## Ethical Use

These tools are provided for educational and authorized security testing
purposes only. Always obtain proper authorization before testing systems
you do not own.

For more information, visit: https://github.com/TLimoges33/Syn_OS
READMEEOF

echo -e "${GREEN}[✓] Created README.md${NC}"

###############################################################################
# Final Statistics
###############################################################################

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# Calculate final size
FINAL_SIZE=$(sudo du -sh "$GITHUB_DIR" 2>/dev/null | cut -f1)
CHROOT_SIZE=$(sudo du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            INSTALLATION COMPLETE                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}[✓] Successfully installed: $INSTALLED/$TOTAL_REPOS repositories${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}[✗] Failed installations: $FAILED${NC}"
fi

echo ""
echo -e "${BLUE}Statistics:${NC}"
echo -e "  • Total repositories: $TOTAL_REPOS"
echo -e "  • Successful: ${GREEN}$INSTALLED${NC}"
echo -e "  • Failed: ${RED}$FAILED${NC}"
echo -e "  • Installation time: ${MINUTES}m ${SECONDS}s"
echo -e "  • GitHub repos size: ${YELLOW}$FINAL_SIZE${NC}"
echo -e "  • Total chroot size: ${YELLOW}$CHROOT_SIZE${NC}"

echo ""
echo -e "${BLUE}Repository locations:${NC}"
echo -e "  • Main directory: /opt/github-repos/"
echo -e "  • Symlinks: /usr/local/bin/"
echo -e "  • Documentation: /opt/github-repos/README.md"

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Review the README: $GITHUB_DIR/README.md"
echo -e "  2. Test tool accessibility in chroot"
echo -e "  3. Proceed with Phase 6 ISO rebuild"

echo ""
echo -e "${GREEN}Log file saved to: $LOG_FILE${NC}"
echo ""

# Write final statistics to log
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "FINAL STATISTICS" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "Total repositories: $TOTAL_REPOS" >> "$LOG_FILE"
echo "Successful: $INSTALLED" >> "$LOG_FILE"
echo "Failed: $FAILED" >> "$LOG_FILE"
echo "Installation time: ${MINUTES}m ${SECONDS}s" >> "$LOG_FILE"
echo "GitHub repos size: $FINAL_SIZE" >> "$LOG_FILE"
echo "Total chroot size: $CHROOT_SIZE" >> "$LOG_FILE"
echo "Completed: $(date)" >> "$LOG_FILE"

exit 0
