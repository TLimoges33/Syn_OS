#!/bin/bash
################################################################################
# SynOS Red Phoenix Branding Deployment Script
# Deploys revolutionary red/black branding to ISO chroot
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Detect chroot directory
if [ -z "$CHROOT_DIR" ]; then
    if [ -d "build/synos-ultimate/chroot" ]; then
        CHROOT_DIR="build/synos-ultimate/chroot"
    elif [ -d "/tmp/synos-build/chroot" ]; then
        CHROOT_DIR="/tmp/synos-build/chroot"
    else
        echo -e "${RED}Error: CHROOT_DIR not set and cannot auto-detect${NC}"
        echo "Usage: CHROOT_DIR=/path/to/chroot $0"
        exit 1
    fi
fi

BRANDING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║      SynOS Red Phoenix Branding Deployment                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Chroot:${NC} ${CHROOT_DIR}"
echo -e "${CYAN}Branding:${NC} ${BRANDING_DIR}"
echo ""

################################################################################
# 1. Deploy Plymouth Boot Theme
################################################################################

echo -e "${CYAN}[1/7] Deploying Plymouth boot theme...${NC}"

PLYMOUTH_DIR="${CHROOT_DIR}/usr/share/plymouth/themes/red-phoenix"
mkdir -p "${PLYMOUTH_DIR}"

# Copy Plymouth assets
cp "${BRANDING_DIR}/plymouth/red-phoenix/boot-logo.png" "${PLYMOUTH_DIR}/" 2>/dev/null || true
cp "${BRANDING_DIR}/plymouth/red-phoenix/boot-logo-small.png" "${PLYMOUTH_DIR}/" 2>/dev/null || true
cp "${BRANDING_DIR}/plymouth/red-phoenix/red-phoenix.plymouth" "${PLYMOUTH_DIR}/" 2>/dev/null || true
cp "${BRANDING_DIR}/plymouth/red-phoenix/red-phoenix.script" "${PLYMOUTH_DIR}/" 2>/dev/null || true

# Create progress bar images
convert -size 400x20 xc:"#2a2a2a" "${PLYMOUTH_DIR}/progress_bar_bg.png" 2>/dev/null || true
convert -size 400x20 gradient:red-"#ff6666" "${PLYMOUTH_DIR}/progress_bar_fg.png" 2>/dev/null || true

echo -e "${GREEN}✓ Plymouth theme deployed${NC}"

################################################################################
# 2. Deploy GRUB Theme
################################################################################

echo -e "${CYAN}[2/7] Deploying GRUB theme...${NC}"

GRUB_THEME_DIR="${CHROOT_DIR}/boot/grub/themes/neural-command"
mkdir -p "${GRUB_THEME_DIR}"

# Copy GRUB assets
cp "${BRANDING_DIR}/grub/neural-command/logo-64.png" "${GRUB_THEME_DIR}/" 2>/dev/null || true
cp "${BRANDING_DIR}/grub/neural-command/theme.txt" "${GRUB_THEME_DIR}/" 2>/dev/null || true

# Create simple black background
convert -size 1920x1080 xc:black "${GRUB_THEME_DIR}/background.png" 2>/dev/null || true

# Create selection highlight
convert -size 600x30 xc:"#ff0000" "${GRUB_THEME_DIR}/select_c.png" 2>/dev/null || true

echo -e "${GREEN}✓ GRUB theme deployed${NC}"

################################################################################
# 3. Deploy Wallpapers
################################################################################

echo -e "${CYAN}[3/7] Deploying wallpapers...${NC}"

WALLPAPER_DIR="${CHROOT_DIR}/usr/share/backgrounds/synos"
mkdir -p "${WALLPAPER_DIR}"

# Copy wallpapers
cp "${BRANDING_DIR}/backgrounds/red-phoenix/"*.png "${WALLPAPER_DIR}/" 2>/dev/null || true
cp "${BRANDING_DIR}/logos/circuit-mandala/mandala-1080p.png" "${WALLPAPER_DIR}/default.png" 2>/dev/null || true

chmod 644 "${WALLPAPER_DIR}"/*.png 2>/dev/null || true

echo -e "${GREEN}✓ Wallpapers deployed${NC}"

################################################################################
# 4. Deploy Logos/Icons
################################################################################

echo -e "${CYAN}[4/7] Deploying logos...${NC}"

ICON_DIR="${CHROOT_DIR}/usr/share/pixmaps"
mkdir -p "${ICON_DIR}"

# Copy main logos
cp "${BRANDING_DIR}/logos/phoenix/phoenix-512.png" "${ICON_DIR}/synos-logo.png" 2>/dev/null || true
cp "${BRANDING_DIR}/logos/phoenix/phoenix-256.png" "${ICON_DIR}/synos-logo-256.png" 2>/dev/null || true
cp "${BRANDING_DIR}/logos/phoenix/phoenix-64.png" "${ICON_DIR}/synos-logo-64.png" 2>/dev/null || true

echo -e "${GREEN}✓ Logos deployed${NC}"

################################################################################
# 5. Configure LightDM
################################################################################

echo -e "${CYAN}[5/7] Configuring login screen...${NC}"

LIGHTDM_CONF="${CHROOT_DIR}/etc/lightdm/lightdm-gtk-greeter.conf"
if [ -f "${LIGHTDM_CONF}" ]; then
    sed -i "s|^#\?background=.*|background=/usr/share/backgrounds/synos/default.png|" "${LIGHTDM_CONF}"
    sed -i "s|^#\?theme-name=.*|theme-name=Adwaita-dark|" "${LIGHTDM_CONF}"
    sed -i "s|^#\?logo=.*|logo=/usr/share/pixmaps/synos-logo-256.png|" "${LIGHTDM_CONF}"
    echo -e "${GREEN}✓ LightDM configured${NC}"
else
    echo -e "${YELLOW}⚠ LightDM not found${NC}"
fi

################################################################################
# 6. Desktop Defaults
################################################################################

echo -e "${CYAN}[6/7] Configuring desktop...${NC}"

mkdir -p "${CHROOT_DIR}/etc/skel/.config"
mkdir -p "${CHROOT_DIR}/usr/share/synos"

echo -e "${GREEN}✓ Desktop configured${NC}"

################################################################################
# 7. Branding Info
################################################################################

echo -e "${CYAN}[7/7] Creating branding info...${NC}"

cat > "${CHROOT_DIR}/usr/share/synos/branding-info.txt" << 'INFO_EOF'
═══════════════════════════════════════════════════════════════
              🔴 SynOS Red Phoenix Branding 🔴
═══════════════════════════════════════════════════════════════

Theme:        Revolutionary Red/Black
Primary Logo: Phoenix/Eagle
Color:        Crimson Red (#FF0000) on Black (#000000)

RED MEANS POWER. RED MEANS ALERT. RED MEANS SYNOS.
INFO_EOF

echo -e "${GREEN}✓ Complete!${NC}"
echo ""
