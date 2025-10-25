#!/bin/bash
# SynOS Day 2: Simplified Build - Focus on ONE working ISO
# Strategy: Build minimal Debian + core security tools FIRST
# Then expand with external repos in hooks AFTER ca-certificates installed

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
═══════════════════════════════════════════════
   SynOS Day 2: Simplified Build Strategy
   Goal: ONE WORKING ISO with core tools
═══════════════════════════════════════════════
EOF
echo -e "${NC}"

# Check we're in the right directory
if [ ! -f "config/binary" ]; then
    echo -e "${RED}Error: Must be run from SynOS-Linux-Builder directory${NC}"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG="build-simplified-${TIMESTAMP}.log"

echo -e "${YELLOW}[1/7] Cleaning previous build...${NC}"
sudo lb clean --purge 2>&1 | tee -a "$LOG"

echo -e "${YELLOW}[2/7] Disabling problematic external repos (will add later in hooks)...${NC}"
# Temporarily disable Kali/Parrot repos - add them AFTER ca-certificates installed
if [ -f config/archives/kali.list.chroot ]; then
    mv config/archives/kali.list.chroot config/archives/kali.list.chroot.disabled || true
fi
if [ -f config/archives/parrot.list.chroot ]; then
    mv config/archives/parrot.list.chroot config/archives/parrot.list.chroot.disabled || true
fi

echo -e "${YELLOW}[3/7] Creating minimal security package list...${NC}"
cat > config/package-lists/synos-security-core.list.chroot << 'PKGEOF'
# Core security tools available in Debian repos
# These will install without certificate issues

# ─────────────────────────────────────────────
# SYSTEM ESSENTIALS (install these first)
# ─────────────────────────────────────────────
ca-certificates
apt-transport-https
gnupg
wget
curl

# ─────────────────────────────────────────────
# RECONNAISSANCE
# ─────────────────────────────────────────────
nmap
dnsutils
whois
netcat-openbsd
tcpdump
wireshark
tshark
arp-scan

# ─────────────────────────────────────────────
# WEB APPLICATION TESTING
# ─────────────────────────────────────────────
nikto
sqlmap
dirb
wfuzz

# ─────────────────────────────────────────────
# PASSWORD ATTACKS
# ─────────────────────────────────────────────
hydra
john
hashcat
crunch

# ─────────────────────────────────────────────
# WIRELESS TESTING
# ─────────────────────────────────────────────
aircrack-ng
reaver
bully
wifite

# ─────────────────────────────────────────────
# EXPLOITATION FRAMEWORKS
# ─────────────────────────────────────────────
metasploit-framework
beef-xss

# ─────────────────────────────────────────────
# FORENSICS
# ─────────────────────────────────────────────
autopsy
sleuthkit
binwalk
foremost

# ─────────────────────────────────────────────
# REVERSE ENGINEERING
# ─────────────────────────────────────────────
radare2
gdb
ghidra
objdump

# ─────────────────────────────────────────────
# SNIFFING & SPOOFING
# ─────────────────────────────────────────────
ettercap-text-only
dsniff
mitmproxy
sslstrip

# ─────────────────────────────────────────────
# POST-EXPLOITATION
# ─────────────────────────────────────────────
powersploit
mimikatz
netcat-traditional

# ─────────────────────────────────────────────
# DEVELOPMENT & SCRIPTING
# ─────────────────────────────────────────────
python3
python3-pip
git
vim
tmux
screen
PKGEOF

echo -e "${YELLOW}[4/7] Creating hook to add security repos AFTER certificates installed...${NC}"
mkdir -p config/hooks/normal
cat > config/hooks/normal/0500-add-security-repos.hook.chroot << 'HOOKEOF'
#!/bin/bash
# Add Kali/Parrot repos AFTER ca-certificates is installed

set -e

echo "=== Adding Kali repository ==="
wget -q -O /etc/apt/trusted.gpg.d/kali-archive-keyring.asc https://archive.kali.org/archive-key.asc
echo "deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" > /etc/apt/sources.list.d/kali.list

echo "=== Adding ParrotOS repository ==="
wget -qO - https://deb.parrot.sh/parrot/misc/parrotsec.gpg | apt-key add -
echo "deb https://deb.parrot.sh/parrot/ parrot main contrib non-free non-free-firmware" > /etc/apt/sources.list.d/parrot.list

echo "=== Updating package lists with new repos ==="
apt-get update

echo "=== Installing additional security tools from Kali/Parrot ==="
apt-get install -y --no-install-recommends \
    burpsuite \
    zaproxy \
    gobuster \
    ffuf \
    enum4linux \
    smbmap \
    crackmapexec \
    bloodhound \
    responder \
    impacket-scripts || true  # Don't fail if some packages unavailable

echo "=== Security repos added successfully ==="
HOOKEOF

chmod +x config/hooks/normal/0500-add-security-repos.hook.chroot

echo -e "${YELLOW}[5/7] Preparing SynOS packages...${NC}"
mkdir -p packages
cp ../SynOS-Packages/*.deb packages/ 2>/dev/null || echo "No SynOS packages found (optional)"

echo -e "${YELLOW}[6/7] Starting Debian live-build (this may take 30-60 minutes)...${NC}"
echo -e "${BLUE}Building with:${NC}"
echo -e "  - Debian 12 Bookworm base"
echo -e "  - Core security tools from Debian repos"
echo -e "  - Kali/Parrot repos will be added after certificates installed"
echo -e "  - SynOS AI packages included"
echo ""
echo -e "${YELLOW}Log file: $LOG${NC}"
echo ""

sudo lb build 2>&1 | tee -a "$LOG" &
BUILD_PID=$!

# Monitor build progress
while kill -0 $BUILD_PID 2>/dev/null; do
    if [ -f chroot/debootstrap/debootstrap.log ]; then
        echo -ne "\r${GREEN}[Bootstrap] $(tail -1 chroot/debootstrap/debootstrap.log 2>/dev/null | cut -c1-80)${NC}"
    fi
    sleep 5
done

wait $BUILD_PID
BUILD_STATUS=$?

echo ""
if [ $BUILD_STATUS -eq 0 ]; then
    echo -e "${GREEN}"
    echo "═══════════════════════════════════════════════"
    echo "   BUILD SUCCESSFUL! 🎉"
    echo "═══════════════════════════════════════════════"
    echo -e "${NC}"

    if [ -f "live-image-amd64.hybrid.iso" ]; then
        ISO_NAME="SynOS-Day2-Core-${TIMESTAMP}-amd64.iso"
        mv live-image-amd64.hybrid.iso "$ISO_NAME"

        echo -e "${BLUE}ISO Details:${NC}"
        ls -lh "$ISO_NAME"

        echo -e "\n${BLUE}Generating checksums...${NC}"
        sha256sum "$ISO_NAME" > "${ISO_NAME}.sha256"
        md5sum "$ISO_NAME" > "${ISO_NAME}.md5"

        echo -e "\n${GREEN}ISO ready:${NC} $ISO_NAME"
        echo -e "${GREEN}SHA256:${NC} $(cat ${ISO_NAME}.sha256)"

        echo -e "\n${YELLOW}Next Steps:${NC}"
        echo "1. Test ISO in VM: qemu-system-x86_64 -cdrom $ISO_NAME -m 4096 -enable-kvm"
        echo "2. Verify security tools: nmap --version, metasploit-framework --version"
        echo "3. Check if Kali/Parrot repos were added during build"
        echo "4. Tomorrow: Add more tools, branding, AI integration"
    fi
else
    echo -e "${RED}"
    echo "═══════════════════════════════════════════════"
    echo "   BUILD FAILED"
    echo "═══════════════════════════════════════════════"
    echo -e "${NC}"
    echo -e "${YELLOW}Check log file:${NC} $LOG"
    echo -e "${YELLOW}Last 50 lines of errors:${NC}"
    tail -50 "$LOG" | grep -i "error\|fail\|fatal" || tail -50 "$LOG"
fi

exit $BUILD_STATUS
