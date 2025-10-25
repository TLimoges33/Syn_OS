# 🛠️ Security Tools Reference

**Total Tools**: 500+  
**Categories**: 15  
**Quick Reference**: Tool catalog and usage guide

---

## Tool Categories

### 1. Information Gathering (80+ tools)

**Network Scanning**:
- `nmap` - Network mapper, port scanner
- `masscan` - Fast port scanner
- `zmap` - Internet-wide scanner
- `unicornscan` - Advanced scanner

**DNS Enumeration**:
- `dnsenum` - DNS enumeration
- `fierce` - DNS reconnaissance
- `dnsrecon` - DNS enumeration script

**Usage**:
```bash
# Comprehensive network scan
nmap -sC -sV -oA scan_results 192.168.1.0/24

# Fast scan
masscan -p1-65535 10.0.0.0/8 --rate=10000

# DNS enumeration
dnsenum example.com
```

---

### 2. Vulnerability Analysis (60+ tools)

- `nessus` - Vulnerability scanner
- `openvas` - Open source scanner
- `nikto` - Web server scanner
- `wpscan` - WordPress scanner
- `sqlmap` - SQL injection tool

```bash
# Web vulnerability scan
nikto -h https://target.com

# WordPress scan
wpscan --url https://target.com --enumerate u,p

# SQL injection
sqlmap -u "http://target.com?id=1" --dbs
```

---

### 3. Web Application Analysis (70+ tools)

**Proxies**:
- `burpsuite` - Web proxy and scanner
- `zaproxy` - OWASP ZAP proxy
- `mitmproxy` - Man-in-the-middle proxy

**Fuzzers**:
- `ffuf` - Fast web fuzzer
- `wfuzz` - Web application fuzzer
- `dirb` - Directory brute-forcer

---

### 4. Password Attacks (40+ tools)

- `john` - John the Ripper
- `hashcat` - Advanced password cracker
- `hydra` - Network login cracker
- `medusa` - Parallel brute-forcer
- `crunch` - Wordlist generator

```bash
# Crack password hash
john --wordlist=rockyou.txt hashes.txt

# GPU-accelerated cracking
hashcat -m 0 -a 0 hash.txt rockyou.txt

# Network brute-force
hydra -L users.txt -P passwords.txt ssh://10.10.10.10
```

---

### 5. Wireless Attacks (30+ tools)

- `aircrack-ng` - WiFi cracking suite
- `reaver` - WPS cracker
- `bully` - WPS brute-forcer
- `kismet` - Wireless detector

```bash
# Monitor mode
airmon-ng start wlan0

# Capture handshake
airodump-ng -c 6 --bssid XX:XX:XX:XX:XX:XX -w capture wlan0mon

# Crack WPA
aircrack-ng -w rockyou.txt capture-01.cap
```

---

### 6. Exploitation Tools (50+ tools)

- `metasploit` - Exploitation framework
- `exploit-db` - Exploit database
- `searchsploit` - Exploit search
- `commix` - Command injection

```bash
# Start Metasploit
msfconsole

# Search exploits
search type:exploit platform:linux

# Use exploit
use exploit/linux/http/php_cgi_arg_injection
set RHOSTS 10.10.10.10
exploit
```

---

### 7. Forensics (35+ tools)

- `autopsy` - Digital forensics
- `volatility` - Memory forensics
- `foremost` - File carving
- `binwalk` - Firmware analysis

---

### 8. Reverse Engineering (25+ tools)

- `ghidra` - NSA reverse engineering tool
- `radare2` - Reverse engineering framework
- `ida` - Interactive disassembler
- `gdb` - GNU debugger

---

### 9. Social Engineering (20+ tools)

- `setoolkit` - Social Engineer Toolkit
- `gophish` - Phishing framework
- `evilginx2` - MitM phishing

---

### 10. Post-Exploitation (40+ tools)

- `mimikatz` - Credential dumper
- `bloodhound` - AD attack paths
- `empire` - Post-exploitation framework
- `covenant` - .NET C2 framework

---

## Quick Reference

### Most Used Commands

```bash
# Network discovery
nmap -sn 192.168.1.0/24

# Service scan
nmap -sV -p- 192.168.1.10

# Vulnerability scan
nmap --script vuln 192.168.1.10

# Web directory scan
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt

# SQL injection
sqlmap -u "http://target.com?id=1" --batch --dbs

# Password cracking
john --wordlist=rockyou.txt hash.txt

# Exploit search
searchsploit apache 2.4

# Metasploit
msfconsole -q -x "search apache; exit"
```

---

## Tool Installation

```bash
# Install all tools
synpkg install synos-security-tools

# Install category
synpkg install synos-web-tools

# Install specific tool
synpkg install metasploit-framework

# Update tools
synpkg update && synpkg upgrade
```

---

## Custom Tool Registry

```bash
# Register custom tool
synos-tools register \
  --name mytool \
  --category exploitation \
  --command "/opt/mytool/run.sh" \
  --description "My custom exploit tool"

# List registered tools
synos-tools list

# Run registered tool
synos-tools run mytool --target 10.10.10.10
```

---

**Last Updated**: October 4, 2025  
**For full list**: Run `synos-tools list --all`
