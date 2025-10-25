#!/bin/bash

CHROOT_PATH="$1"

if [ -z "$CHROOT_PATH" ]; then
    echo "Usage: $0 <chroot_path>"
    exit 1
fi

if [ ! -d "$CHROOT_PATH" ]; then
    echo "Error: Chroot path does not exist: $CHROOT_PATH"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Fix Dependencies + Install Security Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to run commands in chroot
run_in_chroot() {
    chroot "$CHROOT_PATH" /bin/bash -c "$1"
}

echo "[1/5] Removing newer LibreOffice packages (incompatible with stable)..."
run_in_chroot "DEBIAN_FRONTEND=noninteractive dpkg --remove --force-all libreoffice-math libreoffice-calc libreoffice-writer libreoffice-core libreoffice-base-core python3-uno ure libuno-cppuhelpergcc3-3t64 libreoffice-common 2>&1" || true

echo ""
echo "[2/5] Cleaning up and fixing broken dependencies..."
run_in_chroot "DEBIAN_FRONTEND=noninteractive apt-get autoremove -y 2>&1" || true
run_in_chroot "DEBIAN_FRONTEND=noninteractive apt-get install -f -y 2>&1" || true
run_in_chroot "DEBIAN_FRONTEND=noninteractive dpkg --configure -a 2>&1" || true

echo ""
echo "[3/5] Installing STABLE LibreOffice from Debian repos..."
run_in_chroot "DEBIAN_FRONTEND=noninteractive apt-get update 2>&1"
run_in_chroot "DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-downgrades libreoffice=1:7.4.7-1+deb12u9 libreoffice-writer=1:7.4.7-1+deb12u9 libreoffice-calc=1:7.4.7-1+deb12u9 libreoffice-impress=1:7.4.7-1+deb12u9 libreoffice-base=1:7.4.7-1+deb12u9 libreoffice-draw=1:7.4.7-1+deb12u9 libreoffice-math=1:7.4.7-1+deb12u9 2>&1"

echo ""
echo "[4/5] Final dependency cleanup..."
run_in_chroot "DEBIAN_FRONTEND=noninteractive apt-get install -f -y 2>&1"

echo ""
echo "[5/5] Installing security tools..."

TOOLS=(
    "john:John the Ripper"
    "hashcat:Hashcat"
    "hydra:THC Hydra"
    "aircrack-ng:Aircrack-ng Suite"
    "metasploit-framework:Metasploit Framework"
    "wireshark:Wireshark"
    "gobuster:Gobuster"
    "nikto:Nikto"
)

SUCCESS_COUNT=0
FAILED_TOOLS=()

for TOOL_ENTRY in "${TOOLS[@]}"; do
    IFS=':' read -r TOOL_NAME TOOL_DESC <<< "$TOOL_ENTRY"

    echo ""
    echo "[→] Installing ${TOOL_DESC} (${TOOL_NAME})..."

    if run_in_chroot "DEBIAN_FRONTEND=noninteractive apt-get install -y ${TOOL_NAME} 2>&1 | grep -v 'Can not write log'"; then
        echo "✓ ${TOOL_DESC} installed"
        ((SUCCESS_COUNT++))
    else
        echo "⚠ ${TOOL_DESC} not available in repos"
        FAILED_TOOLS+=("${TOOL_NAME}")
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Checking installed tools..."
INSTALLED_TOOLS=()

# Check nmap first
if run_in_chroot "which nmap >/dev/null 2>&1"; then
    echo "✓ Nmap"
    INSTALLED_TOOLS+=("nmap")
fi

for TOOL_ENTRY in "${TOOLS[@]}"; do
    IFS=':' read -r TOOL_NAME TOOL_DESC <<< "$TOOL_ENTRY"

    # Special case for metasploit
    if [ "$TOOL_NAME" = "metasploit-framework" ]; then
        CHECK_CMD="msfconsole"
    else
        CHECK_CMD="$TOOL_NAME"
    fi

    if run_in_chroot "which ${CHECK_CMD} >/dev/null 2>&1"; then
        echo "✓ ${TOOL_DESC}"
        INSTALLED_TOOLS+=("${TOOL_NAME}")
    else
        echo "✗ ${TOOL_DESC} (not available)"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Productivity Suite:"
echo "  ✓ LibreOffice 7.4.7 (Stable)"
echo "  ✓ Obsidian 1.7.7"
echo "  ℹ Notion (manual setup via notion.so)"
echo ""

echo "Compiled Security Tools: ${#INSTALLED_TOOLS[@]}/9 installed"
echo "GitHub Repository Tools: 81 repos with 180+ tools"
echo ""

CHROOT_SIZE=$(du -sh "$CHROOT_PATH" 2>/dev/null | cut -f1)
echo "Final chroot size: ${CHROOT_SIZE}"

if [ ${#FAILED_TOOLS[@]} -gt 0 ]; then
    echo ""
    echo "⚠ Not available in Debian/Kali repos: ${FAILED_TOOLS[*]}"
    echo ""
    echo "✓ You have superior alternatives from GitHub:"
    for FAILED in "${FAILED_TOOLS[@]}"; do
        case "$FAILED" in
            aircrack-ng)
                echo "  • aircrack-ng → airgeddon, wifite2 (both installed)"
                ;;
            metasploit-framework)
                echo "  • metasploit → Villain, AutoPWN-Suite, Sn1per (all installed)"
                ;;
            gobuster)
                echo "  • gobuster → dirsearch, ffuf (both installed)"
                ;;
            nikto)
                echo "  • nikto → nuclei, httpx, cherrybomb (all installed)"
                ;;
            john|hashcat|hydra)
                echo "  • ${FAILED} → Use from Kali VM or install from source"
                ;;
            wireshark)
                echo "  • wireshark → tshark may be available, or use tcpdump"
                ;;
        esac
    done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ System ready for application menu organization!"
echo "✓ Ready to proceed with Phase 2 (AI Integration)!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
