# Syn_OS Security Tools Integration

This directory contains the integration configuration for Parrot Security OS tools within Syn_OS.

## Quick Start

1. Source the environment configuration:
   ```bash
   source /home/diablorain/Syn_OS/config/security-tools/environment.sh
   ```

2. Use the security launcher:
   ```bash
   synos-security --menu
   ```

3. Run specific tools:
   ```bash
   synos-nmap -sV target.com
   synos-sqlmap -u "http://target.com/page?id=1"
   ```

## Available Commands

- `synos-security` - Interactive security tools launcher
- `synos_security_status` - Show security tools status
- `synos_security_update` - Update security environment

## Tool Categories

- **Network**: nmap, masscan, tcpdump, ettercap
- **Web**: sqlmap, nikto, burpsuite, gobuster
- **Wireless**: aircrack-ng, airodump-ng, reaver
- **Password**: hydra, john, hashcat
- **Forensics**: volatility, autopsy, foremost
- **Reverse**: radare2, gdb, objdump
- **Exploit**: metasploit, linux-exploit-suggester

## Integration Status

Total Tools: 60
Wordlists: Available in toolset/wordlists
Configurations: Available in toolset/config
