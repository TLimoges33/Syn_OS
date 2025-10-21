#!/bin/bash
#
# SynOS Command Center
# Interactive menu system for accessing all SynOS tools
#
# Installation: Copy to /usr/local/bin/synos-menu in ISO
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to display header
show_header() {
    clear
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗                    ║
║     ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝                    ║
║     ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗                    ║
║     ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║                    ║
║     ███████║   ██║   ██║ ╚████║╚██████╔╝███████║                    ║
║     ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝                    ║
║                                                                      ║
║              🔒 The Pinnacle of Cybersecurity OS 🔒                  ║
║                     v1.0 "Red Phoenix"                               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
    echo ""
}

# Function to display main menu
show_main_menu() {
    show_header
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}                    MAIN MENU${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}[1]${NC}  🔒 Security Tools          - Advanced security arsenal"
    echo -e "${GREEN}[2]${NC}  🧠 AI & Consciousness      - AI systems and ALFRED"
    echo -e "${GREEN}[3]${NC}  🎯 Threat Intelligence     - Threat intel platform"
    echo -e "${GREEN}[4]${NC}  🔍 Threat Hunting          - Proactive threat hunting"
    echo -e "${GREEN}[5]${NC}  ✅ Compliance & Audit      - Automated compliance"
    echo -e "${GREEN}[6]${NC}  📊 Security Analytics      - Behavioral analysis"
    echo -e "${GREEN}[7]${NC}  🎭 Deception Technology    - Honeypots & traps"
    echo -e "${GREEN}[8]${NC}  🔐 Zero Trust Engine       - Zero trust architecture"
    echo -e "${GREEN}[9]${NC}  🔑 HSM Integration         - Hardware security"
    echo -e "${GREEN}[10]${NC} 🐛 Vulnerability Research  - Vuln discovery tools"
    echo -e "${GREEN}[11]${NC} 🎮 War Games & CTF         - Training scenarios"
    echo -e "${GREEN}[12]${NC} 🛠️  Development Tools       - Build & debug tools"
    echo -e "${GREEN}[13]${NC} 📦 Package Management      - SynPkg system"
    echo -e "${GREEN}[14]${NC} 🧪 Testing & QA            - Test suites"
    echo -e "${GREEN}[15]${NC} 📚 Documentation           - Learn SynOS"
    echo -e "${GREEN}[16]${NC} ℹ️  System Information     - About SynOS"
    echo ""
    echo -e "${RED}[0]${NC}  Exit"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -n "Select option: "
}

# Security Tools Menu
security_menu() {
    while true; do
        show_header
        echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${WHITE}              🔒 SECURITY TOOLS${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "${GREEN}[1]${NC}  Network Security     - nmap, wireshark, tcpdump"
        echo -e "${GREEN}[2]${NC}  Web Security         - burpsuite, nikto, sqlmap"
        echo -e "${GREEN}[3]${NC}  Exploitation         - metasploit, exploit-db"
        echo -e "${GREEN}[4]${NC}  Password Tools       - john, hashcat, hydra"
        echo -e "${GREEN}[5]${NC}  Wireless Security    - aircrack-ng, kismet"
        echo -e "${GREEN}[6]${NC}  Forensics            - autopsy, volatility"
        echo -e "${GREEN}[7]${NC}  Reverse Engineering  - ghidra, radare2"
        echo -e "${GREEN}[8]${NC}  Security Orchestrator - Launch SynOS orchestrator"
        echo ""
        echo -e "${RED}[0]${NC}  Back to Main Menu"
        echo ""
        read -p "Select tool category: " choice

        case $choice in
            1) clear; echo "Available network security tools:"; ls /usr/bin | grep -E "nmap|wireshark|tcpdump|netcat"; read -p "Press Enter to continue..." ;;
            2) clear; echo "Available web security tools:"; ls /usr/bin | grep -E "nikto|sqlmap|dirb|wfuzz"; read -p "Press Enter to continue..." ;;
            3) clear; echo "Launching Metasploit..."; msfconsole ;;
            4) clear; echo "Available password tools:"; ls /usr/bin | grep -E "john|hashcat|hydra|medusa"; read -p "Press Enter to continue..." ;;
            5) clear; echo "Available wireless tools:"; ls /usr/bin | grep -E "aircrack|kismet|reaver|wifite"; read -p "Press Enter to continue..." ;;
            6) clear; echo "Available forensics tools:"; ls /usr/bin | grep -E "autopsy|volatility|foremost|binwalk"; read -p "Press Enter to continue..." ;;
            7) clear; echo "Available reverse engineering tools:"; ls /usr/bin | grep -E "ghidra|radare2|objdump|strings"; read -p "Press Enter to continue..." ;;
            8) clear; synos-security-orchestrator ;;
            0) return ;;
        esac
    done
}

# AI & Consciousness Menu
ai_menu() {
    while true; do
        show_header
        echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${WHITE}          🧠 AI & CONSCIOUSNESS SYSTEMS${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "${GREEN}[1]${NC}  ALFRED Voice Assistant    - Interactive AI assistant"
        echo -e "${GREEN}[2]${NC}  AI Daemon Status          - Check AI daemon"
        echo -e "${GREEN}[3]${NC}  Consciousness Status      - Neural Darwinism system"
        echo -e "${GREEN}[4]${NC}  LLM Engine                - Language model engine"
        echo -e "${GREEN}[5]${NC}  AI Model Manager          - Manage AI/ML models"
        echo -e "${GREEN}[6]${NC}  AI Runtime                - Runtime environment"
        echo ""
        echo -e "${RED}[0]${NC}  Back to Main Menu"
        echo ""
        read -p "Select option: " choice

        case $choice in
            1) clear; alfred ;;
            2) clear; systemctl status synos-ai-daemon; read -p "Press Enter to continue..." ;;
            3) clear; systemctl status synos-consciousness; read -p "Press Enter to continue..." ;;
            4) clear; systemctl status synos-llm-engine; read -p "Press Enter to continue..." ;;
            5) clear; synos-model-manager --help; read -p "Press Enter to continue..." ;;
            6) clear; synos-ai-runtime --help; read -p "Press Enter to continue..." ;;
            0) return ;;
        esac
    done
}

# Development Tools Menu
dev_menu() {
    while true; do
        show_header
        echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${WHITE}            🛠️  DEVELOPMENT TOOLS${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "${GREEN}[1]${NC}  SynOS Shell (synsh)       - Custom shell"
        echo -e "${GREEN}[2]${NC}  Rust Development          - cargo, rustc, clippy"
        echo -e "${GREEN}[3]${NC}  Python Development        - python3, pip, venv"
        echo -e "${GREEN}[4]${NC}  Distribution Builder      - Build custom SynOS"
        echo -e "${GREEN}[5]${NC}  Browse Source Code        - /usr/share/synos/source"
        echo -e "${GREEN}[6]${NC}  Build from Source         - Compile SynOS components"
        echo ""
        echo -e "${RED}[0]${NC}  Back to Main Menu"
        echo ""
        read -p "Select option: " choice

        case $choice in
            1) clear; synsh ;;
            2) clear; echo "Rust toolchain:"; rustc --version; cargo --version; read -p "Press Enter to continue..." ;;
            3) clear; echo "Python environment:"; python3 --version; pip3 --version; read -p "Press Enter to continue..." ;;
            4) clear; synos-distro-builder --help; read -p "Press Enter to continue..." ;;
            5) clear; cd /usr/share/synos/source && ls -la; read -p "Press Enter to continue..." ;;
            6) clear; echo "Build components: cd /usr/share/synos/source && cargo build --release"; read -p "Press Enter to continue..." ;;
            0) return ;;
        esac
    done
}

# System Information
system_info() {
    show_header
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}            ℹ️  SYSTEM INFORMATION${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo -e "${YELLOW}OS Information:${NC}"
    cat /etc/os-release | head -5
    echo ""

    echo -e "${YELLOW}Kernel:${NC}"
    uname -r
    echo ""

    echo -e "${YELLOW}CPU:${NC}"
    lscpu | grep "Model name" | sed 's/Model name:\s*//'
    echo ""

    echo -e "${YELLOW}Memory:${NC}"
    free -h | grep "Mem:"
    echo ""

    echo -e "${YELLOW}SynOS Services:${NC}"
    systemctl list-units --type=service | grep synos
    echo ""

    echo -e "${YELLOW}Installed Tools:${NC}"
    echo "  - Security tools: $(ls /usr/bin | grep -E "nmap|metasploit|wireshark|burp|sqlmap" | wc -l)"
    echo "  - SynOS tools: $(ls /usr/bin | grep synos | wc -l)"
    echo "  - Total binaries: $(ls /usr/bin | wc -l)"
    echo ""

    echo -e "${YELLOW}Features:${NC}"
    echo "  ✅ Custom Rust Kernel"
    echo "  ✅ ALFRED AI Assistant"
    echo "  ✅ Neural Darwinism Consciousness"
    echo "  ✅ Zero Trust Architecture"
    echo "  ✅ 600+ Security Tools"
    echo "  ✅ Complete Source Code"
    echo ""

    read -p "Press Enter to return to menu..."
}

# Documentation
show_docs() {
    show_header
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}            📚 DOCUMENTATION${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Documentation locations:${NC}"
    echo ""
    echo "  📁 /usr/share/doc/synos/          - General documentation"
    echo "  📁 /usr/share/synos/source/       - Complete source code"
    echo "  📁 /usr/share/man/                - Man pages"
    echo "  📁 /opt/synos/tutorials/          - Interactive tutorials"
    echo ""
    echo -e "${YELLOW}Quick start:${NC}"
    echo ""
    echo "  1. Try ALFRED:       ${GREEN}alfred${NC}"
    echo "  2. Check services:   ${GREEN}systemctl status synos-*${NC}"
    echo "  3. Security tools:   ${GREEN}synos-menu${NC} → Option 1"
    echo "  4. Learn Rust:       ${GREEN}cd /usr/share/synos/source${NC}"
    echo ""
    echo -e "${YELLOW}Online resources:${NC}"
    echo ""
    echo "  🌐 Website:  https://synos.ai"
    echo "  📖 Docs:     https://synos.ai/docs"
    echo "  💬 Support:  https://synos.ai/support"
    echo "  🐙 GitHub:   https://github.com/synos/synos"
    echo ""

    read -p "Press Enter to return to menu..."
}

# Main loop
main() {
    while true; do
        show_main_menu
        read choice

        case $choice in
            1) security_menu ;;
            2) ai_menu ;;
            3) clear; synos-threat-intel --help; read -p "Press Enter to continue..." ;;
            4) clear; synos-threat-hunter --help; read -p "Press Enter to continue..." ;;
            5) clear; synos-compliance --help; read -p "Press Enter to continue..." ;;
            6) clear; synos-analytics --help; read -p "Press Enter to continue..." ;;
            7) clear; synos-honeypot --help; read -p "Press Enter to continue..." ;;
            8) clear; synos-zero-trust --help; read -p "Press Enter to continue..." ;;
            9) clear; synos-hsm --help; read -p "Press Enter to continue..." ;;
            10) clear; synos-vuln-research --help; read -p "Press Enter to continue..." ;;
            11) clear; synos-wargames --help; read -p "Press Enter to continue..." ;;
            12) dev_menu ;;
            13) clear; synpkg --help; read -p "Press Enter to continue..." ;;
            14) clear; ls -la /opt/synos/testing/; read -p "Press Enter to continue..." ;;
            15) show_docs ;;
            16) system_info ;;
            0)
                clear
                echo ""
                echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
                echo -e "${CYAN}║  Thank you for using SynOS - Red Phoenix Edition!       ║${NC}"
                echo -e "${CYAN}║  Stay secure. Stay curious. Stay legendary.             ║${NC}"
                echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please try again.${NC}"
                sleep 1
                ;;
        esac
    done
}

# Run main
main
