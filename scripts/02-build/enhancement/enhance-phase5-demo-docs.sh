#!/usr/bin/env bash
################################################################################
# SynOS ULTIMATE ISO Enhancement Script
# Phase 5: Demo Application & Documentation
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/chroot}"
PROJECT_ROOT="/home/diablorain/Syn_OS"

source "$PROJECT_ROOT/scripts/build/enhancement-utils.sh" 2>/dev/null || true

section "Phase 5: Demo Application & Documentation"

################################################################################
# CREATE SYNOS DEMO APPLICATION
################################################################################

create_demo_app() {
    log "Creating SynOS feature showcase demo application..."

    cat > "$CHROOT_DIR/usr/local/bin/synos-demo" <<'EOF'
#!/usr/bin/env python3
"""
SynOS Feature Showcase Demo Application
Demonstrates the capabilities of the SynOS platform
"""

import sys
import subprocess
import time
from pathlib import Path

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

def print_banner():
    banner = f"""
{CYAN}{BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗               ║
║   ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝               ║
║   ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗               ║
║   ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║               ║
║   ███████║   ██║   ██║ ╚████║╚██████╔╝███████║               ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝               ║
║                                                               ║
║              AI-Powered Security Operating System            ║
║                   Feature Showcase Demo                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{RESET}
"""
    print(banner)

def menu():
    print(f"\n{BOLD}Select a demo to run:{RESET}\n")
    print(f"{GREEN}1.{RESET} 🛡️  Security Tools Overview")
    print(f"{GREEN}2.{RESET} 🤖 AI Consciousness System Status")
    print(f"{GREEN}3.{RESET} 🔍 Run Basic Network Scan (nmap)")
    print(f"{GREEN}4.{RESET} 🌐 Web Application Testing (nuclei)")
    print(f"{GREEN}5.{RESET} 🔐 Password Security Demo (john)")
    print(f"{GREEN}6.{RESET} 📊 System Performance Metrics")
    print(f"{GREEN}7.{RESET} 🐍 Python Security Tools Demo")
    print(f"{GREEN}8.{RESET} 📚 View Documentation")
    print(f"{GREEN}9.{RESET} ℹ️  About SynOS")
    print(f"{RED}0.{RESET} 🚪 Exit")

    choice = input(f"\n{YELLOW}Enter your choice:{RESET} ")
    return choice

def tools_overview():
    print(f"\n{CYAN}=== Security Tools Overview ==={RESET}\n")

    categories = {
        "Information Gathering": ["nmap", "masscan", "rustscan", "subfinder", "amass"],
        "Vulnerability Analysis": ["nuclei", "nikto", "wpscan", "openvas"],
        "Web Applications": ["burpsuite", "zaproxy", "sqlmap", "gobuster", "ffuf"],
        "Password Attacks": ["john", "hashcat", "hydra", "medusa"],
        "Wireless": ["aircrack-ng", "wifite", "kismet"],
        "Exploitation": ["metasploit", "crackmapexec", "bloodhound"],
        "Sniffing": ["wireshark", "ettercap", "responder"],
        "Forensics": ["autopsy", "volatility3"]
    }

    for category, tools in categories.items():
        print(f"{BOLD}{category}:{RESET}")
        for tool in tools:
            # Check if tool is installed
            try:
                subprocess.run(["which", tool], capture_output=True, check=True)
                status = f"{GREEN}✓ Installed{RESET}"
            except:
                status = f"{RED}✗ Not found{RESET}"
            print(f"  • {tool:20s} {status}")
        print()

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def ai_status():
    print(f"\n{CYAN}=== AI Consciousness System Status ==={RESET}\n")

    services = [
        ("synos-ai.service", "AI Consciousness Engine"),
        ("synos-security-monitor.service", "Security Monitoring"),
    ]

    for service, desc in services:
        print(f"{BOLD}{desc}:{RESET}")
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True
            )
            if "active" in result.stdout:
                print(f"  Status: {GREEN}Active ✓{RESET}")
            else:
                print(f"  Status: {YELLOW}Inactive{RESET}")
        except:
            print(f"  Status: {RED}Error checking{RESET}")
        print()

    # Check AI model files
    ai_dir = Path("/opt/synos/ai")
    if ai_dir.exists():
        print(f"{BOLD}AI Models:{RESET}")
        print(f"  Directory: {ai_dir}")
        print(f"  Models: {len(list(ai_dir.glob('**/*.pt')))} PyTorch models found")

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def nmap_demo():
    print(f"\n{CYAN}=== Network Scan Demo (nmap) ==={RESET}\n")

    target = input(f"{YELLOW}Enter target (e.g., scanme.nmap.org or press Enter for demo):{RESET} ")
    if not target:
        target = "scanme.nmap.org"

    print(f"\n{GREEN}Running: nmap -F {target}{RESET}\n")

    try:
        subprocess.run(["nmap", "-F", target])
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def nuclei_demo():
    print(f"\n{CYAN}=== Web Application Testing Demo (nuclei) ==={RESET}\n")

    target = input(f"{YELLOW}Enter target URL (or press Enter to skip):{RESET} ")
    if not target:
        print(f"\n{YELLOW}Skipping active scan. Showing nuclei capabilities:{RESET}\n")
        subprocess.run(["nuclei", "-version"])
        print(f"\n{GREEN}Templates available:{RESET}")
        subprocess.run(["nuclei", "-tl"])
    else:
        print(f"\n{GREEN}Running: nuclei -u {target}{RESET}\n")
        subprocess.run(["nuclei", "-u", target])

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def john_demo():
    print(f"\n{CYAN}=== Password Security Demo (John the Ripper) ==={RESET}\n")

    print("This demo shows john's capabilities without actual cracking.\n")

    # Create sample hash file
    sample_hashes = """
demo:$1$12345678$xvjSkJJlgRiOc6BdMVQT/1
"""

    print(f"{GREEN}Sample hash file:{RESET}")
    print(sample_hashes)

    print(f"\n{BOLD}John the Ripper features:{RESET}")
    print("  • Automatic hash type detection")
    print("  • Dictionary attacks")
    print("  • Brute force attacks")
    print("  • Rainbow table attacks")
    print("  • GPU acceleration support")

    subprocess.run(["john", "--version"])

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def performance_metrics():
    print(f"\n{CYAN}=== System Performance Metrics ==={RESET}\n")

    print(f"{BOLD}CPU & Memory:{RESET}")
    subprocess.run(["bash", "-c", "top -bn1 | head -20"])

    print(f"\n{BOLD}Disk Usage:{RESET}")
    subprocess.run(["df", "-h"])

    print(f"\n{BOLD}Network Interfaces:{RESET}")
    subprocess.run(["ip", "addr", "show"])

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def python_tools_demo():
    print(f"\n{CYAN}=== Python Security Tools Demo ==={RESET}\n")

    tools = [
        ("impacket", "Network protocols implementation"),
        ("pwntools", "CTF framework and exploit development"),
        ("scapy", "Packet manipulation"),
        ("requests", "HTTP library")
    ]

    print(f"{BOLD}Installed Python security packages:{RESET}\n")

    for tool, desc in tools:
        try:
            __import__(tool)
            print(f"{GREEN}✓{RESET} {tool:20s} - {desc}")
        except:
            print(f"{RED}✗{RESET} {tool:20s} - {desc}")

    print(f"\n{BOLD}Quick scapy demo:{RESET}")
    try:
        from scapy.all import IP, ICMP
        packet = IP(dst="8.8.8.8")/ICMP()
        print(f"\nSample packet structure:\n{packet.show()}")
    except Exception as e:
        print(f"{YELLOW}Scapy demo requires root: {e}{RESET}")

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def view_docs():
    print(f"\n{CYAN}=== SynOS Documentation ==={RESET}\n")

    docs_path = Path("/usr/share/doc/synos")

    if docs_path.exists():
        print(f"{BOLD}Available documentation:{RESET}\n")
        for doc in docs_path.glob("*.md"):
            print(f"  • {doc.name}")

        print(f"\n{BOLD}GitHub Resources:{RESET}")
        github_path = Path("/opt/github-repos")
        if github_path.exists():
            for repo in github_path.iterdir():
                if repo.is_dir():
                    print(f"  • {repo.name}")
    else:
        print(f"{YELLOW}Documentation directory not found.{RESET}")

    print(f"\n{BOLD}Online Resources:{RESET}")
    print("  • GitHub: https://github.com/diablorain/Syn_OS")
    print("  • Wiki: https://github.com/diablorain/Syn_OS/wiki")

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def about():
    print(f"\n{CYAN}=== About SynOS ==={RESET}\n")

    info = """
SynOS is an AI-powered security operating system designed for:

🎯 Purpose:
  • Penetration testing and security assessments
  • Digital forensics and incident response
  • Security research and education
  • Vulnerability assessment and management

✨ Key Features:
  • 500+ pre-installed security tools
  • AI-powered threat detection and analysis
  • Organized tools menu by category
  • Cloud-native architecture
  • Real-time security monitoring
  • Comprehensive reporting tools

🛠️ Tool Categories:
  1. Information Gathering
  2. Vulnerability Analysis
  3. Web Application Analysis
  4. Database Assessment
  5. Password Attacks
  6. Wireless Attacks
  7. Exploitation Tools
  8. Sniffing & Spoofing
  9. Post Exploitation
  10. Forensics
  11. Reporting Tools

📊 System Info:
"""
    print(info)

    # Display system info
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith(("NAME=", "VERSION=", "PRETTY_NAME=")):
                    print(f"  {line.strip()}")
    except:
        pass

    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def main():
    try:
        while True:
            print_banner()
            choice = menu()

            if choice == "1":
                tools_overview()
            elif choice == "2":
                ai_status()
            elif choice == "3":
                nmap_demo()
            elif choice == "4":
                nuclei_demo()
            elif choice == "5":
                john_demo()
            elif choice == "6":
                performance_metrics()
            elif choice == "7":
                python_tools_demo()
            elif choice == "8":
                view_docs()
            elif choice == "9":
                about()
            elif choice == "0":
                print(f"\n{GREEN}Thank you for using SynOS!{RESET}\n")
                sys.exit(0)
            else:
                print(f"\n{RED}Invalid choice. Please try again.{RESET}")
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{GREEN}Thank you for using SynOS!{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
EOF

    chmod +x "$CHROOT_DIR/usr/local/bin/synos-demo"
}

################################################################################
# INSTALL GITHUB REPOSITORIES
################################################################################

install_github_repos() {
    log "Pre-installing GitHub repositories for offline access..."

    mkdir -p "$CHROOT_DIR/opt/github-repos"

    repos=(
        "danielmiessler/SecLists"
        "swisskyrepo/PayloadsAllTheThings"
        "carlospolop/PEASS-ng"
        "rebootuser/LinEnum"
        "projectdiscovery/nuclei-templates"
        "BloodHoundAD/BloodHound"
        "byt3bl33d3r/CrackMapExec"
        "SecureAuthCorp/impacket"
        "lgandx/Responder"
        "mzet-/linux-exploit-suggester"
    )

    log "Cloning essential repositories (may take time)..."
    for repo in "${repos[@]}"; do
        repo_name=$(basename "$repo")
        if [ ! -d "$CHROOT_DIR/opt/github-repos/$repo_name" ]; then
            log "Cloning $repo_name..."
            git clone --depth 1 "https://github.com/$repo" "$CHROOT_DIR/opt/github-repos/$repo_name" 2>/dev/null || \
                warn "Failed to clone $repo_name"
        fi
    done
}

################################################################################
# CREATE DOCUMENTATION
################################################################################

create_documentation() {
    log "Creating comprehensive documentation..."

    mkdir -p "$CHROOT_DIR/usr/share/doc/synos"

    # Main README
    cat > "$CHROOT_DIR/usr/share/doc/synos/README.md" <<'EOF'
# SynOS Documentation

## Welcome to SynOS

SynOS is an AI-powered security operating system designed for penetration testing,
security research, and digital forensics.

## Quick Start

### Running the Demo
```bash
synos-demo
```

### Accessing Tools
- Open the Applications menu
- Navigate to "SynOS Tools"
- Tools are organized in 11 categories

### Common Commands

#### Network Scanning
```bash
nmap -sV target.com
masscan -p1-65535 target.com
rustscan target.com
```

#### Web Application Testing
```bash
nuclei -u https://target.com
gobuster dir -u https://target.com -w /opt/wordlists/common.txt
ffuf -u https://target.com/FUZZ -w /opt/wordlists/common.txt
```

#### Password Cracking
```bash
john --wordlist=/opt/wordlists/rockyou.txt hashes.txt
hashcat -m 0 -a 0 hashes.txt /opt/wordlists/rockyou.txt
hydra -L users.txt -P passwords.txt ssh://target.com
```

#### Wireless Testing
```bash
aircrack-ng -w /opt/wordlists/rockyou.txt capture.cap
wifite --kill
```

### Tool Categories

1. **Information Gathering**: nmap, masscan, subfinder, amass
2. **Vulnerability Analysis**: nuclei, nikto, wpscan
3. **Web Applications**: burpsuite, zaproxy, sqlmap
4. **Database Assessment**: sqlmap
5. **Password Attacks**: john, hashcat, hydra
6. **Wireless Attacks**: aircrack-ng, wifite
7. **Exploitation**: metasploit, crackmapexec
8. **Sniffing & Spoofing**: wireshark, ettercap
9. **Post Exploitation**: mimikatz, empire
10. **Forensics**: autopsy, volatility
11. **Reporting**: dradis, faraday

### GitHub Resources

Pre-installed repositories in `/opt/github-repos/`:
- SecLists: Comprehensive wordlists
- PayloadsAllTheThings: Useful payloads
- PEASS-ng: Privilege escalation tools
- LinEnum: Linux enumeration
- nuclei-templates: Vulnerability templates

### AI Features

SynOS includes AI-powered features:
- Automated threat detection
- Intelligent log analysis
- Security recommendation system

Check status: `systemctl status synos-ai.service`

### Getting Help

- Demo application: `synos-demo`
- List all tools: `cat /opt/synos-tools-inventory.txt`
- GitHub: https://github.com/diablorain/Syn_OS
- Wiki: https://github.com/diablorain/Syn_OS/wiki

## Configuration

### Desktop Customization
- Theme: Windows-10-Dark
- Window Manager: ARK-Dark
- Wallpaper: /usr/share/backgrounds/synos/

### Network Configuration
```bash
# View interfaces
ip addr show

# Configure static IP
nmtui
```

### Service Management
```bash
# Check AI service
systemctl status synos-ai.service

# Check security monitor
systemctl status synos-security-monitor.service
```

## Legal Notice

⚠️ **IMPORTANT**: These tools are for authorized security testing only.
Unauthorized access to computer systems is illegal.

Always obtain proper authorization before performing security assessments.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/diablorain/Syn_OS/issues
- Discussions: https://github.com/diablorain/Syn_OS/discussions

## License

See LICENSE file in the GitHub repository.
EOF

    # Quick reference card
    cat > "$CHROOT_DIR/usr/share/doc/synos/QUICK_REFERENCE.md" <<'EOF'
# SynOS Quick Reference Card

## Essential Commands

| Command | Description |
|---------|-------------|
| `synos-demo` | Launch feature showcase |
| `tools` | List all installed tools |
| `synos-update` | Update system |

## Common Workflows

### Web Application Assessment
1. `subfinder -d target.com` - Subdomain discovery
2. `httpx -l subdomains.txt` - Probe for live hosts
3. `nuclei -l live-hosts.txt` - Vulnerability scanning
4. `gobuster dir -u https://target.com -w /opt/wordlists/common.txt` - Directory enumeration

### Network Penetration Test
1. `nmap -sn 192.168.1.0/24` - Host discovery
2. `nmap -sV -sC target` - Service enumeration
3. `nuclei -target target` - Vulnerability check
4. `msfconsole` - Exploitation

### Wireless Assessment
1. `airmon-ng start wlan0` - Enable monitor mode
2. `airodump-ng wlan0mon` - Capture traffic
3. `aircrack-ng -w wordlist.txt capture.cap` - Crack password

## Important Paths

- Tools: `/opt/tools/`
- Wordlists: `/opt/wordlists/`
- GitHub repos: `/opt/github-repos/`
- Logs: `/var/log/synos/`
- Config: `/etc/synos/`
EOF

    chmod 644 "$CHROOT_DIR/usr/share/doc/synos"/*.md
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo "Phase 5: Demo Application & Documentation"
    echo "========================================="

    create_demo_app
    install_github_repos
    create_documentation

    log "✓ Phase 5 complete!"
    log "Created: Demo app (synos-demo), GitHub repos, Documentation"
}

main "$@"
