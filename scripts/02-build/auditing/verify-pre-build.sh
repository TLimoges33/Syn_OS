#!/bin/bash
# Final Pre-Build Verification and Summary
# Verify everything is ready before ISO build

CHROOT="$1"
if [ -z "$CHROOT" ]; then
    echo "Usage: $0 /path/to/chroot"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SYNOS PRE-BUILD VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

PASS=0
FAIL=0
WARN=0

check_tool() {
    local tool="$1"
    local critical="${2:-no}"

    if sudo chroot "$CHROOT" /bin/bash -c "which $tool >/dev/null 2>&1"; then
        echo "  ✅ $tool"
        PASS=$((PASS + 1))
        return 0
    else
        if [ "$critical" = "yes" ]; then
            echo "  ❌ $tool (CRITICAL)"
            FAIL=$((FAIL + 1))
        else
            echo "  ⚠  $tool (optional)"
            WARN=$((WARN + 1))
        fi
        return 1
    fi
}

echo "[1/10] Verifying Priority Tools (CRITICAL)..."
check_tool "wireshark" yes
check_tool "tshark" yes
check_tool "msfconsole" yes
check_tool "msfvenom" yes
echo

echo "[2/10] Verifying Core Security Tools..."
check_tool "nmap" yes
check_tool "john" yes
check_tool "hashcat" yes
check_tool "hydra" yes
check_tool "aircrack-ng" yes
check_tool "gobuster" yes
check_tool "nikto" yes
echo

echo "[3/10] Verifying Web App Tools..."
check_tool "burpsuite"
check_tool "zaproxy"
check_tool "sqlmap"
check_tool "dirb"
check_tool "skipfish"
check_tool "wfuzz"
echo

echo "[4/10] Verifying Network Tools..."
check_tool "masscan"
check_tool "unicornscan"
check_tool "dmitry"
check_tool "dnsenum"
echo

echo "[5/10] Verifying Wireless Tools..."
check_tool "bettercap"
check_tool "ettercap"
echo

echo "[6/10] Verifying Information Gathering..."
check_tool "theharvester"
check_tool "recon-ng"
check_tool "maltego"
check_tool "enum4linux"
echo

echo "[7/10] Verifying Additional Tools..."
check_tool "sslscan"
check_tool "beef-xss"
echo

echo "[8/10] Checking Directory Structure..."
echo "→ GitHub repositories..."
GITHUB_COUNT=$(sudo find "$CHROOT/opt/github-repos" -maxdepth 1 -type d 2>/dev/null | wc -l)
if [ "$GITHUB_COUNT" -gt 10 ]; then
    echo "  ✅ GitHub repos: $GITHUB_COUNT directories"
    PASS=$((PASS + 1))
else
    echo "  ⚠  GitHub repos: $GITHUB_COUNT directories (expected 80+)"
    WARN=$((WARN + 1))
fi

echo "→ Metasploit Framework..."
if [ -d "$CHROOT/usr/share/metasploit-framework" ]; then
    MSF_SIZE=$(sudo du -sh "$CHROOT/usr/share/metasploit-framework" 2>/dev/null | cut -f1)
    echo "  ✅ Metasploit: $MSF_SIZE"
    PASS=$((PASS + 1))
else
    echo "  ⚠  Metasploit directory not found"
    WARN=$((WARN + 1))
fi

echo "→ Application menus..."
MENU_COUNT=$(sudo find "$CHROOT/usr/share/applications" -name 'synos-*.desktop' 2>/dev/null | wc -l)
if [ "$MENU_COUNT" -gt 40 ]; then
    echo "  ✅ Menu entries: $MENU_COUNT"
    PASS=$((PASS + 1))
else
    echo "  ⚠  Menu entries: $MENU_COUNT (expected 48+)"
    WARN=$((WARN + 1))
fi

echo "→ Master launcher..."
if sudo chroot "$CHROOT" /bin/bash -c "[ -f /usr/local/bin/synos-tools ]"; then
    echo "  ✅ synos-tools launcher exists"
    PASS=$((PASS + 1))
else
    echo "  ⚠  synos-tools launcher not found"
    WARN=$((WARN + 1))
fi
echo

echo "[9/10] Checking System Statistics..."
echo "→ Chroot size..."
CHROOT_SIZE=$(sudo du -sh "$CHROOT" 2>/dev/null | cut -f1)
echo "  ℹ  Total: $CHROOT_SIZE"

echo "→ Binary count..."
BIN_COUNT=$(sudo ls "$CHROOT/usr/bin" 2>/dev/null | wc -l)
SBIN_COUNT=$(sudo ls "$CHROOT/usr/sbin" 2>/dev/null | wc -l)
echo "  ℹ  /usr/bin: $BIN_COUNT binaries"
echo "  ℹ  /usr/sbin: $SBIN_COUNT binaries"

echo "→ Wordlists..."
if [ -f "$CHROOT/usr/share/wordlists/rockyou.txt" ]; then
    ROCKYOU_SIZE=$(sudo du -h "$CHROOT/usr/share/wordlists/rockyou.txt" 2>/dev/null | cut -f1)
    echo "  ✅ rockyou.txt: $ROCKYOU_SIZE"
    PASS=$((PASS + 1))
else
    echo "  ⚠  rockyou.txt not found"
    WARN=$((WARN + 1))
fi
echo

echo "[10/10] Checking Build Requirements..."
echo "→ Required tools on host..."
for tool in mksquashfs xorriso; do
    if which "$tool" >/dev/null 2>&1; then
        echo "  ✅ $tool"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $tool (REQUIRED FOR ISO BUILD)"
        FAIL=$((FAIL + 1))
    fi
done

echo "→ Kernel and initrd..."
KERNEL_COUNT=$(sudo find "$CHROOT/boot" -name 'vmlinuz-*' 2>/dev/null | wc -l)
INITRD_COUNT=$(sudo find "$CHROOT/boot" -name 'initrd.img-*' 2>/dev/null | wc -l)
if [ "$KERNEL_COUNT" -gt 0 ]; then
    echo "  ✅ Kernel found"
    PASS=$((PASS + 1))
else
    echo "  ⚠  No kernel in chroot (will use host kernel)"
    WARN=$((WARN + 1))
fi
if [ "$INITRD_COUNT" -gt 0 ]; then
    echo "  ✅ Initrd found"
    PASS=$((PASS + 1))
else
    echo "  ⚠  No initrd in chroot (will generate)"
    WARN=$((WARN + 1))
fi
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  VERIFICATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "✅ Passed: $PASS"
echo "⚠  Warnings: $WARN"
echo "❌ Failed: $FAIL"
echo
echo "Chroot Size: $CHROOT_SIZE"
echo "Total Binaries: $((BIN_COUNT + SBIN_COUNT))"
echo "Menu Entries: $MENU_COUNT"
echo "GitHub Repos: $GITHUB_COUNT"
echo

if [ "$FAIL" -gt 0 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ❌ VERIFICATION FAILED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Critical tools or build requirements are missing."
    echo "Please fix the issues above before building the ISO."
    echo
    exit 1
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ READY FOR ISO BUILD!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    if [ "$WARN" -gt 0 ]; then
        echo "⚠  Note: There are $WARN warnings, but they won't block the build."
        echo "   The ISO will be created with available tools."
        echo
    fi
    echo "To build the ISO, run:"
    echo "  sudo ./scripts/build/build-final-iso.sh $CHROOT"
    echo
    echo "Estimated ISO size: ~8-12GB"
    echo "Build time: ~15-20 minutes"
    echo
fi
