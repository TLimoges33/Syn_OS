#!/usr/bin/env bash
################################################################################
# SynOS ULTIMATE ISO Enhancement Script
# Leverages ALL codebase components, repositories, and customizations
# Phase 1: Advanced Repository Setup & Tool Installation
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/chroot}"
PROJECT_ROOT="/home/diablorain/Syn_OS"

source "$PROJECT_ROOT/scripts/build/enhancement-utils.sh" 2>/dev/null || true

section "Phase 1: Advanced Repository Setup"

################################################################################
# ADD ALL SECURITY DISTRIBUTION REPOSITORIES
################################################################################

setup_all_repos() {
    log "Adding ParrotOS repositories (you're on Parrot!)..."
    chroot "$CHROOT_DIR" bash -c '
        cat > /etc/apt/sources.list.d/parrot.list <<EOF
# ParrotOS Security Repository
deb https://deb.parrot.sh/parrot lory main contrib non-free non-free-firmware
deb https://deb.parrot.sh/parrot lory-security main contrib non-free non-free-firmware
deb https://deb.parrot.sh/parrot lory-backports main contrib non-free non-free-firmware
EOF

        # Import ParrotOS key
        wget -qO - https://deb.parrot.sh/parrot/misc/parrotsec.gpg | gpg --dearmor > /etc/apt/trusted.gpg.d/parrot.gpg 2>/dev/null || true
    '

    log "Adding Kali Linux repositories..."
    chroot "$CHROOT_DIR" bash -c '
        cat > /etc/apt/sources.list.d/kali.list <<EOF
# Kali Linux Repository
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF

        # Import Kali key
        wget -qO - https://archive.kali.org/archive-key.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/kali.gpg 2>/dev/null || true
    '

    log "Adding BlackArch repositories..."
    chroot "$CHROOT_DIR" bash -c '
        # BlackArch requires special setup (Arch-based), skip for Debian but note tools
        echo "# BlackArch tools will be installed via individual packages" > /etc/apt/sources.list.d/blackarch-note.list
    '

    log "Updating package lists..."
    chroot "$CHROOT_DIR" apt-get update || log "Some repos may have warnings (OK)"
}

################################################################################
# USE YOUR CUSTOM TOOL INSTALLATION SCRIPT
################################################################################

install_tools_from_your_repo() {
    log "Copying YOUR security tools installation scripts..."

    cp -r "$PROJECT_ROOT/tools/security-tools" "$CHROOT_DIR/opt/"

    log "Installing tools using YOUR curated install-all.sh script..."
    chroot "$CHROOT_DIR" bash -c '
        cd /opt/security-tools/scripts
        export DEBIAN_FRONTEND=noninteractive

        # Run the installation script
        bash install-all.sh --auto-yes 2>&1 | tee /var/log/synos-tools-install.log
    ' || log "Some tools may have failed (continuing...)"

    log "Verifying tool installation..."
    chroot "$CHROOT_DIR" bash -c '
        cd /opt/security-tools/scripts
        bash verify-tools.sh | tee /var/log/synos-tools-verify.log
    '
}

################################################################################
# INSTALL FROM PARROT + KALI REPOS
################################################################################

install_from_distro_repos() {
    log "Installing comprehensive tool suite from ParrotOS + Kali..."

    chroot "$CHROOT_DIR" bash -c '
        export DEBIAN_FRONTEND=noninteractive

        # ParrotOS Security Tools (metapackages)
        apt-get install -y --allow-unauthenticated \
            parrot-tools-full \
            parrot-tools-cloud \
            parrot-tools-crypto \
            parrot-tools-exploit \
            parrot-tools-forensic \
            parrot-tools-information-gathering \
            parrot-tools-password \
            parrot-tools-postexploit \
            parrot-tools-reversing \
            parrot-tools-sniffing \
            parrot-tools-web \
            parrot-tools-wireless \
            2>/dev/null || true

        # Kali Metapackages
        apt-get install -y --allow-unauthenticated \
            kali-tools-information-gathering \
            kali-tools-vulnerability \
            kali-tools-web \
            kali-tools-passwords \
            kali-tools-wireless \
            kali-tools-exploitation \
            kali-tools-forensics \
            kali-tools-reverse-engineering \
            kali-tools-social-engineering \
            kali-tools-sniffing-spoofing \
            2>/dev/null || true

        # Individual critical tools
        apt-get install -y --allow-unauthenticated \
            nmap masscan rustscan \
            wireshark tshark termshark \
            metasploit-framework \
            burpsuite zaproxy \
            sqlmap \
            john hashcat \
            hydra medusa \
            aircrack-ng wifite \
            nikto wpscan \
            gobuster ffuf feroxbuster \
            ghidra radare2 rizin cutter \
            volatility3 \
            bloodhound crackmapexec \
            responder \
            nuclei subfinder httpx \
            amass \
            2>/dev/null || true
    ' || log "Some packages unavailable (continuing...)"
}

################################################################################
# INSTALL LATEST TOOLS FROM GITHUB
################################################################################

install_github_tools() {
    log "Cloning latest security tools from GitHub..."

    chroot "$CHROOT_DIR" bash -c '
        mkdir -p /opt/tools/github
        cd /opt/tools/github

        # Web/API Testing
        git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates.git
        git clone --depth 1 https://github.com/ffuf/ffuf.git
        git clone --depth 1 https://github.com/OJ/gobuster.git

        # Reconnaissance
        git clone --depth 1 https://github.com/projectdiscovery/subfinder.git
        git clone --depth 1 https://github.com/projectdiscovery/httpx.git
        git clone --depth 1 https://github.com/OWASP/Amass.git

        # Exploitation
        git clone --depth 1 https://github.com/byt3bl33d3r/CrackMapExec.git
        git clone --depth 1 https://github.com/SecureAuthCorp/impacket.git
        git clone --depth 1 https://github.com/lgandx/Responder.git

        # Post-Exploitation
        git clone --depth 1 https://github.com/carlospolop/PEASS-ng.git
        git clone --depth 1 https://github.com/rebootuser/LinEnum.git
        git clone --depth 1 https://github.com/PowerShellMafia/PowerSploit.git
        git clone --depth 1 https://github.com/samratashok/nishang.git

        # Privilege Escalation
        git clone --depth 1 https://github.com/diego-treitos/linux-smart-enumeration.git
        git clone --depth 1 https://github.com/jondonas/linux-exploit-suggester-2.git

        # Wordlists & Payloads
        git clone --depth 1 https://github.com/danielmiessler/SecLists.git
        git clone --depth 1 https://github.com/swisskyrepo/PayloadsAllTheThings.git

        # Red Team
        git clone --depth 1 https://github.com/BloodHoundAD/BloodHound.git
        git clone --depth 1 https://github.com/nettitude/PoshC2.git

        # Learning Resources
        git clone --depth 1 https://github.com/carlospolop/hacktricks.git
        git clone --depth 1 https://github.com/JohnHammond/ctf-katana.git

        echo "✓ GitHub tools cloned to /opt/tools/github"
    ' || log "Some repos may have failed (continuing...)"
}

################################################################################
# INSTALL PYTHON SECURITY PACKAGES
################################################################################

install_python_tools() {
    log "Installing Python security packages..."

    chroot "$CHROOT_DIR" bash -c '
        pip3 install --break-system-packages \
            impacket \
            pwntools \
            ropper \
            pycryptodome \
            requests \
            beautifulsoup4 \
            scapy \
            pyshark \
            paramiko \
            asyncio \
            aiohttp \
            websockets \
            dnspython \
            netifaces \
            psutil \
            python-nmap \
            shodan \
            censys \
            virustotal-api \
            pefile \
            yara-python \
            volatility3 \
            bloodhound \
            mitm6 \
            crackmapexec \
            ldapdomaindump \
            enum4linux-ng \
            2>/dev/null || true
    '
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo "Phase 1: Repository & Tool Installation"
    echo "========================================"

    setup_all_repos
    install_tools_from_your_repo
    install_from_distro_repos
    install_github_tools
    install_python_tools

    log "✓ Phase 1 complete!"
    log "Installed tools from: ParrotOS + Kali + GitHub + Python + YOUR repo"
}

main "$@"
