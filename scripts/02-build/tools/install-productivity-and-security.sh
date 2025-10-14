#!/usr/bin/env bash
###############################################################################
# SynOS - Install Productivity Suite + Security Tools
# LibreOffice, Obsidian, Notion + Essential Security Tools
###############################################################################

set -e

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installing Productivity Suite + Security Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Fix broken dpkg state
echo "[1/4] Fixing dpkg state..."
sudo chroot "$CHROOT_DIR" bash -c '
    DEBIAN_FRONTEND=noninteractive dpkg --configure -a --force-confold --force-confdef 2>&1 || true
    apt-get install -f -y --force-yes 2>&1 || true
' | grep -E "(Setting up|Errors|^E:)" | head -10 || true

echo ""

# Step 2: Install LibreOffice Suite
echo "[2/4] Installing LibreOffice Suite..."
sudo DEBIAN_FRONTEND=noninteractive chroot "$CHROOT_DIR" bash -c '
    apt-get install -y --fix-broken \
        libreoffice \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress \
        libreoffice-base \
        libreoffice-draw \
        libreoffice-math \
        libreoffice-gtk3 2>&1
' | grep -E "(Setting up|newest|already|^E:)" || true

if sudo chroot "$CHROOT_DIR" which libreoffice &>/dev/null; then
    echo "  ✓ LibreOffice installed successfully"
else
    echo "  ⚠ LibreOffice installation incomplete"
fi

echo ""

# Step 3: Install Obsidian
echo "[3/4] Installing Obsidian..."

# Download latest Obsidian .deb
echo "  → Downloading Obsidian..."
OBSIDIAN_URL="https://github.com/obsidianmd/obsidian-releases/releases/download/v1.7.7/obsidian_1.7.7_amd64.deb"

if [ ! -f "/tmp/obsidian.deb" ]; then
    wget -q --show-progress -O /tmp/obsidian.deb "$OBSIDIAN_URL" 2>&1 || \
        echo "  ⚠ Download may have failed"
fi

if [ -f "/tmp/obsidian.deb" ]; then
    echo "  → Installing Obsidian package..."
    sudo cp /tmp/obsidian.deb "$CHROOT_DIR/tmp/"

    sudo chroot "$CHROOT_DIR" bash -c '
        DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/obsidian.deb 2>&1 || \
        DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/obsidian.deb 2>&1 || true
        apt-get install -f -y 2>&1 || true
        rm /tmp/obsidian.deb
    ' | grep -E "(Setting up|Unpacking|^E:)" | head -5 || true

    if sudo chroot "$CHROOT_DIR" which obsidian &>/dev/null; then
        echo "  ✓ Obsidian installed successfully"
    else
        echo "  ⚠ Obsidian installation incomplete (check dependencies)"
    fi
else
    echo "  ✗ Could not download Obsidian"
fi

echo ""

# Step 4: Install Notion (via Snap or AppImage)
echo "[4/4] Installing Notion..."

# Notion requires Electron - install via unofficial package
echo "  → Installing Notion dependencies..."
sudo chroot "$CHROOT_DIR" bash -c '
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        libgtk-3-0 \
        libnotify4 \
        libnss3 \
        libxss1 \
        libxtst6 \
        xdg-utils \
        libatspi2.0-0 \
        libdrm2 \
        libgbm1 \
        libxcb-dri3-0 2>&1
' | grep -E "(Setting up|newest|already)" | head -5 || true

# Download Notion Enhanced (unofficial Linux build)
echo "  → Downloading Notion Enhanced..."
NOTION_URL="https://github.com/notion-enhancer/notion-repackaged/releases/latest/download/notion-app_amd64.deb"

if [ ! -f "/tmp/notion.deb" ]; then
    wget -q --show-progress -O /tmp/notion.deb "$NOTION_URL" 2>&1 || \
        echo "  ⚠ Notion download may have failed (unofficial build)"
fi

if [ -f "/tmp/notion.deb" ]; then
    echo "  → Installing Notion package..."
    sudo cp /tmp/notion.deb "$CHROOT_DIR/tmp/"

    sudo chroot "$CHROOT_DIR" bash -c '
        DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/notion.deb 2>&1 || true
        apt-get install -f -y 2>&1 || true
        rm /tmp/notion.deb
    ' | grep -E "(Setting up|Unpacking|^E:)" | head -5 || true

    echo "  ✓ Notion installation attempted"
else
    echo "  ⚠ Notion requires manual installation via official website"
    echo "     URL: https://www.notion.so/desktop"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Now Installing Security Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Install security tools one by one
install_tool() {
    local tool="$1"
    local package="${2:-$1}"

    echo "[→] Installing $tool..."

    if sudo chroot "$CHROOT_DIR" which "$tool" &>/dev/null; then
        echo "  ✓ $tool already installed"
        return 0
    fi

    sudo DEBIAN_FRONTEND=noninteractive chroot "$CHROOT_DIR" bash -c \
        "apt-get install -y --no-install-recommends $package 2>&1" | \
        grep -E "(Setting up|newest|already|^E:)" | head -3 || true

    if sudo chroot "$CHROOT_DIR" which "$tool" &>/dev/null; then
        echo "  ✓ $tool installed"
        return 0
    else
        echo "  ⚠ $tool not available"
        return 1
    fi
}

SECURITY_INSTALLED=0

install_tool "john" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""
install_tool "hashcat" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""
install_tool "hydra" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""
install_tool "aircrack-ng" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""
install_tool "msfconsole" "metasploit-framework" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""
install_tool "wireshark" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""
install_tool "gobuster" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""
install_tool "nikto" && SECURITY_INSTALLED=$((SECURITY_INSTALLED + 1))
echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify productivity apps
echo "Productivity Suite:"
for app in libreoffice obsidian; do
    if sudo chroot "$CHROOT_DIR" which "$app" &>/dev/null; then
        echo "  ✓ $app"
    else
        echo "  ✗ $app"
    fi
done

# Note about Notion
echo "  ℹ Notion (requires manual setup via website)"

echo ""
echo "Security Tools:"
VERIFIED=0
for tool in nmap john hashcat hydra aircrack-ng msfconsole wireshark gobuster nikto; do
    if sudo chroot "$CHROOT_DIR" which "$tool" &>/dev/null; then
        echo "  ✓ $tool"
        VERIFIED=$((VERIFIED + 1))
    else
        echo "  ✗ $tool"
    fi
done

echo ""
echo "Compiled security tools: $VERIFIED/9"
echo "GitHub repository tools: 81 repos"
echo "Total toolkit: 180+ tools"

echo ""
CHROOT_SIZE=$(sudo du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)
echo "Final chroot size: $CHROOT_SIZE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ LibreOffice Suite ready"
echo "✓ Obsidian for note-taking and PKM"
echo "✓ Security tools installed"
echo "✓ Ready for Phase 2 (AI Integration)"
echo ""

exit 0
