# SynOS v1.0 - Official Wiki Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [Security Tools](#security-tools)
6. [AI Features](#ai-features)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

SynOS (Synthesis Operating System) is an advanced AI-powered security distribution built on Debian Bookworm. It combines 500+ security tools with cutting-edge AI assistants to provide an unparalleled penetration testing and security research environment.

### Key Highlights

- **500+ Security Tools** - Complete arsenal from Kali, ParrotOS, and BlackArch
- **AI Integration** - Claude, Gemini, GPT, and Ollama for AI-powered analysis
- **Custom Theme** - Beautiful ARK-Dark theme with ara icons
- **Pre-configured** - Ready to use out of the box with sensible defaults
- **Comprehensive** - Everything from reconnaissance to exploitation to forensics

### Version Information

- **Version:** 1.0 (Synthesis)
- **Release Date:** October 2025
- **Base:** Debian Bookworm
- **Architecture:** x86_64

---

## Features

### Security Tools (500+)

SynOS includes comprehensive security tools across 11 categories:

1. **Information Gathering** - nmap, masscan, amass, subfinder, dnsenum
2. **Vulnerability Analysis** - nuclei, nikto, openvas, nessus
3. **Web Applications** - burpsuite, zaproxy, sqlmap, wfuzz
4. **Password Attacks** - hydra, hashcat, john, medusa
5. **Wireless** - aircrack-ng, wifite, kismet, reaver
6. **Exploitation** - metasploit, beef-xss, SET, exploit-db
7. **Post-Exploitation** - mimikatz, bloodhound, empire, covenant
8. **Forensics** - autopsy, volatility, binwalk, foremost
9. **Reverse Engineering** - ghidra, radare2, gdb-peda, objdump
10. **Sniffing & Spoofing** - wireshark, ettercap, bettercap, tcpdump
11. **Reporting** - pipal, rsmangler, crunch

### AI Assistants

Four AI assistants available via command line:

- **Claude** (Anthropic) - `ask-claude` - Advanced reasoning and coding
- **Gemini** (Google) - `ask-gemini` - Multimodal AI with web access
- **GPT** (OpenAI) - `ask-gpt` - General purpose AI assistant
- **Ollama** (Local) - `local-ai` - Offline AI for privacy

### Machine Learning

- **PyTorch 2.8.0** - Deep learning framework
- **TensorFlow 2.20.0** - ML framework
- **Jupyter Lab 4.4.9** - Interactive notebooks
- **scikit-learn** - Classical ML algorithms
- **pandas, numpy** - Data analysis

### Theme & Appearance

- **GTK Theme:** ARK-Dark (dark theme optimized for long sessions)
- **Icon Theme:** ara (modern, clean icons)
- **Cursor Theme:** mate
- **Terminal:** Custom cyan prompt with SynOS branding

---

## Installation

### System Requirements

**Minimum:**
- 50GB disk space
- 8GB RAM
- 64-bit CPU
- UEFI or Legacy BIOS

**Recommended:**
- 100GB disk space
- 16GB RAM
- Multi-core CPU
- SSD for better performance

### Download

Download SynOS ISO from:
- Official website: [synos.io](https://synos.io) *(placeholder)*
- GitHub releases: [github.com/TLimoges33/Syn_OS](https://github.com/TLimoges33/Syn_OS)

**Verify checksums before installation:**
```bash
md5sum synos-v1.0.iso
sha256sum synos-v1.0.iso
```

### Boot Modes

SynOS supports 4 boot modes:

1. **Live** - Boot without installing (changes not persistent)
2. **Live with Persistence** - Save changes to USB drive
3. **Safe Mode** - Boot with minimal drivers
4. **Forensics Mode** - No disk auto-mounting (for digital forensics)

### Installation Steps

1. Create bootable USB:
   ```bash
   sudo dd if=synos-v1.0.iso of=/dev/sdX bs=4M status=progress
   ```

2. Boot from USB and select "Install SynOS"

3. Follow installation wizard

4. **Important:** Change default passwords after first boot!

---

## Getting Started

### First Boot

On first boot, you'll see the SynOS welcome screen. The default credentials are:

- **Root:** root / superroot
- **User:** user / user

**⚠️ CHANGE THESE IMMEDIATELY:**
```bash
# Change root password
sudo passwd root

# Change user password
passwd
```

### Quick Reference Guide

The Desktop contains a `QUICK-START.txt` file with essential commands and information.

### Terminal Shortcuts

Open a terminal and try these commands:

```bash
# AI Assistants
ask-claude "how do I scan a network?"
ask-gemini "explain SQL injection"
ask-gpt "write a python port scanner"
local-ai  # Offline AI chat

# Security Tools
synos-tools   # Launch tool browser
pentest       # Go to tools directory
metasploit    # Start Metasploit Framework
wireshark     # Network analysis

# System Information
synos-help    # View documentation
ai-status     # Check AI services
```

### Jupyter Lab

Start Jupyter Lab for interactive analysis:

```bash
jupyter lab
# Access at http://localhost:8888
```

Pre-loaded tutorials available in `~/SynOS-Tutorials/`

---

## Security Tools

### Common Tasks

#### Network Scanning
```bash
# Quick scan
nmap -sn 192.168.1.0/24

# Full scan
nmap -A -T4 target.com

# Fast scan
masscan -p1-65535 target.com --rate=1000
```

#### Web Application Testing
```bash
# Directory enumeration
dirb http://target.com

# Vulnerability scanning
nikto -h http://target.com

# SQL injection testing
sqlmap -u "http://target.com/page?id=1" --dbs
```

#### Password Attacks
```bash
# Brute force SSH
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://target.com

# Crack hashes
hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
```

#### Wireless Testing
```bash
# Monitor mode
airmon-ng start wlan0

# Capture handshakes
airodump-ng wlan0mon

# Automated attacks
wifite
```

### Tool Categories

See `/opt/synos/docs/TOOLS.md` for complete tool catalog.

---

## AI Features

### Claude (Anthropic)

Advanced AI with strong reasoning capabilities:

```bash
ask-claude "analyze this network traffic"
ask-claude "write a custom exploit for CVE-2024-XXXX"
ask-claude "explain this malware behavior"
```

### Gemini (Google)

Multimodal AI with web access:

```bash
ask-gemini "latest vulnerabilities in Apache"
ask-gemini "compare these two security tools"
ask-gemini "summarize this security research paper"
```

### GPT (OpenAI)

General purpose AI assistant:

```bash
ask-gpt "generate a phishing template"
ask-gpt "write a python scanner script"
ask-gpt "explain this code"
```

### Ollama (Local AI)

Offline AI for privacy-sensitive work:

```bash
local-ai  # Start interactive chat
# or
ollama run llama3.1 "your prompt here"
```

### Jupyter with AI

Combine Jupyter notebooks with AI for analysis:

```python
# In Jupyter notebook
import subprocess
result = subprocess.run(['ask-claude', 'explain this dataset'], 
                       capture_output=True, text=True)
print(result.stdout)
```

---

## Configuration

### Network Settings

- **Hostname:** synos
- **DNS:** Cloudflare (1.1.1.1) + Google (8.8.8.8)
- **Firewall:** UFW enabled by default

### Firewall Rules

Open ports by default:
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)
- 8888 (Jupyter Lab)
- 11434 (Ollama AI)

Modify firewall:
```bash
sudo ufw allow PORT/tcp
sudo ufw delete allow PORT/tcp
sudo ufw status
```

### Security Hardening

SynOS includes kernel-level security hardening. Configuration in:
- `/etc/sysctl.d/99-synos-security.conf`

### Auditing

System auditing enabled via auditd. View logs:
```bash
sudo ausearch -k auth_log
sudo ausearch -k network_connections
sudo aureport --summary
```

### Customization

Theme settings in:
- `/etc/skel/.config/gtk-3.0/settings.ini`
- `/etc/skel/.gtkrc-2.0`

Terminal customization in:
- `/etc/skel/.bashrc`

---

## Troubleshooting

### AI Assistants Not Working

Check API keys:
```bash
# Claude
echo $ANTHROPIC_API_KEY

# Gemini
echo $GOOGLE_API_KEY

# GPT
echo $OPENAI_API_KEY
```

Set API keys:
```bash
export ANTHROPIC_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

For Ollama (local):
```bash
sudo systemctl status ollama
sudo systemctl start ollama
```

### Network Issues

Reset network:
```bash
sudo systemctl restart NetworkManager
sudo systemctl restart networking
```

Check firewall:
```bash
sudo ufw status
sudo ufw disable  # Temporary
```

### Tool Not Found

Update package lists:
```bash
sudo apt update
sudo apt install TOOL_NAME
```

### Performance Issues

- Disable unnecessary services
- Increase swap space
- Close unused applications
- Check disk space: `df -h`

### Getting Help

- Documentation: `/opt/synos/docs/`
- Terminal help: `synos-help`
- Community: GitHub Issues
- Email: support@synos.io *(placeholder)*

---

## Additional Resources

### Demo Projects

Located in `/opt/synos/demos/`:
- Web application scanner
- AI-powered log analysis
- Network reconnaissance templates

### Tutorials

Located in `~/SynOS-Tutorials/`:
- Getting Started notebook
- Python security scripting
- AI-assisted analysis

### External Resources

- OWASP: https://owasp.org
- Exploit Database: https://exploit-db.com
- SecLists: https://github.com/danielmiessler/SecLists
- HackTricks: https://book.hacktricks.xyz

---

**SynOS v1.0 - Built for security professionals, by security professionals.**

*Last Updated: October 8, 2025*
