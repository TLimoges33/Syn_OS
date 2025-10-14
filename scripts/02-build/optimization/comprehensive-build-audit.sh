#!/bin/bash
# Comprehensive Build Audit for SynOS v1.0
# Verifies all codebase components are reflected in the ISO

set -e

CHROOT=/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot
AUDIT_LOG=/home/diablorain/Syn_OS/logs/build-audit-$(date +%Y%m%d-%H%M%S).log

echo "╔══════════════════════════════════════════════════════════════╗" | tee -a "$AUDIT_LOG"
echo "║     🔍 COMPREHENSIVE BUILD AUDIT - SynOS v1.0                ║" | tee -a" $AUDIT_LO"G
echo "╚══════════════════════════════════════════════════════════════╝" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"
echo "Audit Started: $(date)" | tee -a "$AUDIT_LOG"
echo "Chroot Location: $CHROOT" | tee -a "$AUDIT_LOG"
echo "Log File: $AUDIT_LOG" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

# Counter for issues
ISSUES=0
WARNINGS=0

# Function to check existence
check_exists() {
    local path="$1"
    local description="$2"

    if [ -e "$CHROOT/$path" ]; then
        echo "  ✅ $description" | tee -a "$AUDIT_LOG"
        return 0
    else
        echo "  ❌ MISSING: $description ($path)" | tee -a "$AUDIT_LOG"
        ((ISSUES++))
        return 1
    fi
}

# Function to check command
check_command() {
    local cmd="$1"
    local description="$2"

    if chroot $CHROOT which "$cmd" >/dev/null 2>&1; then
        echo "  ✅ $description" | tee -a "$AUDIT_LOG"
        return 0
    else
        echo "  ❌ MISSING: $description (command: $cmd)" | tee -a "$AUDIT_LOG"
        ((ISSUES++))
        return 1
    fi
}

# Function to count items
count_items() {
    local path="$1"
    local pattern="$2"
    local description="$3"

    if [ -d "$CHROOT/$path" ]; then
        local count=$(find "$CHROOT/$path" -name "$pattern" 2>/dev/null | wc -l)
        echo "  📊 $description: $count items" | tee -a" $AUDIT_LO"G
        return "$count"
    else
        echo "  ⚠️  Directory not found: $path" | tee -a "$AUDIT_LOG"
        ((WARNINGS++))
        return 0
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "PHASE 1: SECURITY TOOLS AUDIT" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

echo "[1/10] Core Security Tools..." | tee -a "$AUDIT_LOG"
check_command "metasploit" "Metasploit Framework"
check_command "nmap" "Nmap"
check_command "wireshark" "Wireshark"
check_command "burpsuite" "Burp Suite"
check_command "zaproxy" "OWASP ZAP"
check_command "aircrack-ng" "Aircrack-ng"
check_command "hashcat" "Hashcat"
check_command "john" "John the Ripper"
check_command "sqlmap" "SQLMap"
check_command "nikto" "Nikto"
echo "" | tee -a "$AUDIT_LOG"

echo "[2/10] GitHub Repositories..." | tee -a "$AUDIT_LOG"
count_items "opt/security/repos" "*" "Cloned repositories"
check_exists "opt/security/repos/sqlmap" "SQLMap repo"
check_exists "opt/security/repos/impacket" "Impacket repo"
check_exists "opt/security/repos/SecLists" "SecLists repo"
check_exists "opt/security/repos/AutoRecon" "AutoRecon repo"
echo "" | tee -a "$AUDIT_LOG"

echo "[3/10] Security Binaries..." | tee -a "$AUDIT_LOG"
if [ -f "$CHROOT/opt/security/PHASE1_COMPLETE.txt" ]; then
    BINARY_COUNT=$(grep "Total binaries:" $CHROOT/opt/security/PHASE1_COMPLETE.txt | awk '{print $3}')
    echo "  📊 Security binaries: $BINARY_COUNT" | tee -a" $AUDIT_LO"G
else
    echo "  ⚠️  Phase 1 completion marker not found" | tee -a "$AUDIT_LOG"
    ((WARNINGS++))
fi
echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "PHASE 2: AI INTEGRATION AUDIT" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

echo "[4/10] AI Command-Line Tools..." | tee -a "$AUDIT_LOG"
check_command "claude" "Claude CLI"
check_command "gemini" "Gemini CLI"
check_command "gpt" "GPT CLI"
check_command "ollama" "Ollama"
echo "" | tee -a "$AUDIT_LOG"

echo "[5/10] AI Frameworks..." | tee -a "$AUDIT_LOG"
if chroot $CHROOT python3 -c "import torch; print(torch.__version__)" 2>/dev/null | grep -q "2.8"; then
    echo "  ✅ PyTorch 2.8.0" | tee -a "$AUDIT_LOG"
else
    echo "  ❌ PyTorch 2.8.0 not found" | tee -a "$AUDIT_LOG"
    ((ISSUES++))
fi

if chroot $CHROOT python3 -c "import tensorflow; print(tensorflow.__version__)" 2>/dev/null | grep -q "2.20"; then
    echo "  ✅ TensorFlow 2.20.0" | tee -a "$AUDIT_LOG"
else
    echo "  ❌ TensorFlow 2.20.0 not found" | tee -a "$AUDIT_LOG"
    ((ISSUES++))
fi

check_command "jupyter-lab" "Jupyter Lab"
echo "" | tee -a "$AUDIT_LOG"

echo "[6/10] Python AI Packages..." | tee -a "$AUDIT_LOG"
AI_PACKAGES=$(chroot $CHROOT pip list 2>/dev/null | grep -E "torch|tensorflow|numpy|pandas|scikit|keras|jupyter" | wc -l)
echo "  📊 AI-related packages installed: $AI_PACKAGES" | tee -a" $AUDIT_LO"G
echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "PHASE 3: BRANDING & THEME AUDIT" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

echo "[7/10] Theme Files..." | tee -a "$AUDIT_LOG"
check_exists "usr/share/themes/ARK-Dark" "ARK-Dark theme"
check_exists "usr/share/icons/ara" "ara icon theme"
check_exists "etc/default/grub.d/synos.cfg" "GRUB configuration"
check_exists "usr/share/plymouth/themes/synos" "Plymouth theme"
check_exists "etc/os-release" "OS identification"
echo "" | tee -a "$AUDIT_LOG"

# Check os-release content
if grep -q "SynOS" $CHROOT/etc/os-release 2>/dev/null; then
    echo "  ✅ os-release contains SynOS branding" | tee -a "$AUDIT_LOG"
else
    echo "  ❌ os-release missing SynOS branding" | tee -a "$AUDIT_LOG"
    ((ISSUES++))
fi
echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "PHASE 4: CONFIGURATION AUDIT" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

echo "[8/10] User Accounts..." | tee -a "$AUDIT_LOG"
if chroot $CHROOT id root >/dev/null 2>&1; then
    echo "  ✅ root user exists" | tee -a "$AUDIT_LOG"
else
    echo "  ❌ root user missing" | tee -a "$AUDIT_LOG"
    ((ISSUES++))
fi

if chroot $CHROOT id user >/dev/null 2>&1; then
    echo "  ✅ user account exists" | tee -a "$AUDIT_LOG"
else
    echo "  ❌ user account missing" | tee -a "$AUDIT_LOG"
    ((ISSUES++))
fi
echo "" | tee -a "$AUDIT_LOG"

echo "[9/10] Security Configuration..." | tee -a "$AUDIT_LOG"
check_command "ufw" "UFW Firewall"
check_exists "etc/sysctl.d/99-synos-hardening.conf" "Kernel hardening"
check_exists "etc/security/limits.d/synos.conf" "Resource limits"
echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "PHASE 5: DOCUMENTATION & DEMOS AUDIT" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

echo "[10/10] Demo Content & Documentation..." | tee -a "$AUDIT_LOG"
check_exists "opt/synos/demos/README.md" "Demo projects README"
check_exists "opt/synos/demos/pentest/web-app-scan.sh" "Pentest demo"
check_exists "opt/synos/demos/ai-security/log-analysis.py" "AI security demo"
check_exists "home/user/SynOS-Tutorials/01-Getting-Started.ipynb" "Tutorial 1"
check_exists "home/user/SynOS-Tutorials/02-AI-Security-Analysis.ipynb" "Tutorial 2"
check_exists "home/user/Desktop/QUICK-START.txt" "Quick start guide"
check_exists "opt/synos/docs/TOOLS.md" "Tools catalog"
check_exists "opt/synos/docs/CONFIGURATION.md" "Configuration docs"
check_command "auditd" "Auditing system"
echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "LIVE SYSTEM AUTO-SETUP AUDIT" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

check_exists "opt/synos/scripts/first-boot-setup.sh" "First-boot setup script"
check_exists "opt/synos/scripts/welcome.py" "Welcome script"
check_exists "etc/systemd/system/synos-first-boot.service" "First-boot service"
echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "CHROOT SIZE & INTEGRITY CHECK" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

CHROOT_SIZE=$(du -sh $CHROOT 2>/dev/null | awk '{print $1}')
echo "📦 Chroot Size: $CHROOT_SIZE" | tee -a" $AUDIT_LO"G

FILE_COUNT=$(find $CHROOT -type f 2>/dev/null | wc -l)
echo "📁 Total Files: $FILE_COUNT" | tee -a" $AUDIT_LO"G

DIR_COUNT=$(find $CHROOT -type d 2>/dev/null | wc -l)
echo "📂 Total Directories: $DIR_COUNT" | tee -a" $AUDIT_LO"G
echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "CODEBASE MAPPING" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

echo "Checking workspace codebase vs chroot..." | tee -a "$AUDIT_LOG"

# Check core components
if [ -d "/home/diablorain/Syn_OS/core" ]; then
    echo "  📊 Workspace core/ directory exists" | tee -a" $AUDIT_LO"G
    CORE_DIRS=$(find /home/diablorain/Syn_OS/core -maxdepth 1 -type d | wc -l)
    echo "     Core subdirectories: $CORE_DIRS" | tee -a "$AUDIT_LOG"
fi

# Check scripts
if [ -d "/home/diablorain/Syn_OS/scripts" ]; then
    echo "  📊 Workspace scripts/ directory exists" | tee -a" $AUDIT_LO"G
    SCRIPT_COUNT=$(find /home/diablorain/Syn_OS/scripts -name "*.sh" | wc -l)
    echo "     Shell scripts: $SCRIPT_COUNT" | tee -a "$AUDIT_LOG"
fi

# Check config
if [ -d "/home/diablorain/Syn_OS/config" ]; then
    echo "  📊 Workspace config/ directory exists" | tee -a" $AUDIT_LO"G
    CONFIG_COUNT=$(find /home/diablorain/Syn_OS/config -type f | wc -l)
    echo "     Configuration files: $CONFIG_COUNT" | tee -a "$AUDIT_LOG"
fi

echo "" | tee -a "$AUDIT_LOG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "AUDIT SUMMARY" | tee -a "$AUDIT_LOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

echo "Audit Completed: $(date)" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════════╗" | tee -a "$AUDIT_LOG"
    echo "║             ✅ ALL CHECKS PASSED                             ║" | tee -a "$AUDIT_LOG"
    echo "║         Build is complete and ready for ISO generation       ║" | tee -a "$AUDIT_LOG"
    echo "╚══════════════════════════════════════════════════════════════╝" | tee -a "$AUDIT_LOG"
    exit 0
elif [ $ISSUES -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════════╗" | tee -a "$AUDIT_LOG"
    echo "║         ⚠️  BUILD PASSED WITH WARNINGS                       ║" | tee -a "$AUDIT_LOG"
    echo "║            Issues: $ISSUES | Warnings: $WARNINGS                         ║" | tee -a "$AUDIT_LOG"
    echo "║         Review warnings before ISO generation                ║" | tee -a "$AUDIT_LOG"
    echo "╚══════════════════════════════════════════════════════════════╝" | tee -a "$AUDIT_LOG"
    exit 0
else
    echo "╔══════════════════════════════════════════════════════════════╗" | tee -a "$AUDIT_LOG"
    echo "║             ❌ BUILD AUDIT FAILED                            ║" | tee -a "$AUDIT_LOG"
    echo "║            Issues: $ISSUES | Warnings: $WARNINGS                         ║" | tee -a "$AUDIT_LOG"
    echo "║         Please fix issues before ISO generation              ║" | tee -a "$AUDIT_LOG"
    echo "╚══════════════════════════════════════════════════════════════╝" | tee -a "$AUDIT_LOG"
    exit 1
fi
