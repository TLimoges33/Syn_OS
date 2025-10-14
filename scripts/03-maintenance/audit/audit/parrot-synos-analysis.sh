#!/bin/bash

# SynOS vs ParrotOS 6.4 Security Edition Feature Analysis
# This script audits SynOS codebase against ParrotOS features for v1.0 ISO development

echo "🔍 SynOS vs ParrotOS 6.4 Security Edition Analysis"
echo "=================================================="

# Create analysis directory
mkdir -p /home/diablorain/Syn_OS/docs/reports/iso-development-analysis

# Extract ParrotOS package list for detailed analysis
echo "📦 Extracting ParrotOS package information..."
PARROT_PACKAGES="/home/diablorain/Downloads/parrot_analysis/live/filesystem.packages"
ANALYSIS_DIR="/home/diablorain/Syn_OS/docs/reports/iso-development-analysis"

# Categorize ParrotOS packages
echo "🏷️  Categorizing ParrotOS packages..."

# Security Tools
grep -E "(nmap|wireshark|metasploit|burp|sqlmap|aircrack|hashcat|john|hydra|nikto|gobuster|dirb|masscan|zap|beef|autopsy|foremost|binwalk|steghide|volatility|yara|clamav|rkhunter|chkrootkit|lynis|tiger|aide|samhain|tripwire|ossec|suricata|snort|bro|zeek)" $PARROT_PACKAGES > $ANALYSIS_DIR/security_tools.txt

# Network Analysis
grep -E "(tcpdump|tshark|netcat|socat|netdiscover|ettercap|dsniff|sslstrip|mitmproxy|proxychains|tor|i2p|freenet)" $PARROT_PACKAGES > $ANALYSIS_DIR/network_tools.txt

# Forensics
grep -E "(sleuthkit|autopsy|foremost|scalpel|bulk_extractor|photorec|testdisk|ddrescue|dc3dd|guymager|ewf|aff|raw)" $PARROT_PACKAGES > $ANALYSIS_DIR/forensics_tools.txt

# Crypto/Encryption
grep -E "(openssl|gpg|truecrypt|veracrypt|luks|dm-crypt|encfs|ecryptfs|steghide|outguess|stegosuite)" $PARROT_PACKAGES > $ANALYSIS_DIR/crypto_tools.txt

# Development Tools
grep -E "(gcc|g\+\+|python|perl|ruby|java|nodejs|git|make|cmake|gdb|valgrind|strace|ltrace|hexedit|bless|ghex)" $PARROT_PACKAGES > $ANALYSIS_DIR/dev_tools.txt

# System Administration
grep -E "(systemd|systemctl|service|cron|at|sudo|su|passwd|shadow|pam|apparmor|selinux|grsecurity|fail2ban)" $PARROT_PACKAGES > $ANALYSIS_DIR/sysadmin_tools.txt

echo "✅ Package categorization complete!"

# Count packages by category
echo ""
echo "📊 ParrotOS Package Statistics:"
echo "Security Tools: $(wc -l < $ANALYSIS_DIR/security_tools.txt)"
echo "Network Tools: $(wc -l < $ANALYSIS_DIR/network_tools.txt)"
echo "Forensics Tools: $(wc -l < $ANALYSIS_DIR/forensics_tools.txt)"
echo "Crypto Tools: $(wc -l < $ANALYSIS_DIR/crypto_tools.txt)"
echo "Development Tools: $(wc -l < $ANALYSIS_DIR/dev_tools.txt)"
echo "System Admin Tools: $(wc -l < $ANALYSIS_DIR/sysadmin_tools.txt)"
echo "Total Packages: $(wc -l < $PARROT_PACKAGES)"

echo ""
echo "🔧 Analyzing SynOS Current Implementation..."

# Check SynOS implementation status
SYNOS_ROOT="/home/diablorain/Syn_OS"

echo ""
echo "🏗️  SynOS Core Components Status:"

# Boot System
echo -n "Boot System: "
if [ -d "$SYNOS_ROOT/core/kernel" ] && [ -f "$SYNOS_ROOT/core/kernel/src/boot.rs" ]; then
    echo "✅ Implemented"
else
    echo "❌ Missing"
fi

# Security Framework
echo -n "Security Framework: "
if [ -d "$SYNOS_ROOT/core/security" ] && [ -f "$SYNOS_ROOT/core/security/src/lib.rs" ]; then
    echo "✅ Implemented"
else
    echo "❌ Missing"
fi

# Consciousness AI
echo -n "Consciousness AI: "
if [ -d "$SYNOS_ROOT/core/consciousness" ] && [ -f "$SYNOS_ROOT/core/consciousness/src/lib.rs" ]; then
    echo "✅ Implemented"
else
    echo "❌ Missing"
fi

# Live ISO Builder
echo -n "Live ISO Builder: "
if [ -f "$SYNOS_ROOT/scripts/build/build-iso.sh" ]; then
    echo "✅ Implemented"
else
    echo "❌ Missing"
fi

# Package Manager
echo -n "Package Manager: "
if [ -f "$SYNOS_ROOT/src/userspace/package-manager/src/main.rs" ]; then
    echo "✅ Implemented"
else
    echo "❌ Missing"
fi

# Desktop Environment
echo -n "Desktop Environment: "
if [ -d "$SYNOS_ROOT/src/ui" ]; then
    echo "✅ Implemented"
else
    echo "❌ Missing"
fi

echo ""
echo "🛠️  Creating SynOS v1.0 ISO Development Roadmap..."
