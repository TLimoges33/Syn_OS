#!/bin/bash
################################################################################
# SynOS GRUB Theme Asset Generator
# Colors: True Black (#000000), Scarlet (#DC143C), White (#FFFFFF)
################################################################################

set -euo pipefail

THEME_DIR="$(dirname "$0")"
cd "$THEME_DIR"

echo "Creating SynOS GRUB Theme Assets..."

# Color definitions
BLACK="#000000"
SCARLET="#DC143C"
WHITE="#FFFFFF"
DARK_GRAY="#1a1a1a"

# ──────────────────────────────────────────────────────────────────────────
# 1. GRUB Background (16:9 - 1920x1080)
# ──────────────────────────────────────────────────────────────────────────

echo "Creating GRUB background (16:9)..."

convert -size 1920x1080 xc:"$BLACK" \
    -fill "$SCARLET" \
    -draw "rectangle 0,0 1920,80" \
    -blur 0x20 \
    -fill "$SCARLET" \
    -draw "circle 960,540 960,300" \
    -blur 0x50 \
    synos-grub-16x9.png

echo "✓ GRUB background created (16:9)"

# ──────────────────────────────────────────────────────────────────────────
# 2. GRUB Background (4:3 - 1024x768)
# ──────────────────────────────────────────────────────────────────────────

echo "Creating GRUB background (4:3)..."

convert -size 1024x768 xc:"$BLACK" \
    -fill "$SCARLET" \
    -draw "rectangle 0,0 1024,60" \
    -blur 0x15 \
    -fill "$SCARLET" \
    -draw "circle 512,384 512,200" \
    -blur 0x35 \
    synos-grub-4x3.png

echo "✓ GRUB background created (4:3)"

# ──────────────────────────────────────────────────────────────────────────
# 3. Selection Box (for selected menu item)
# ──────────────────────────────────────────────────────────────────────────

echo "Creating selection box..."

# Center part (scarlet with reduced opacity via color)
convert -size 800x32 xc:"#661020" \
    select_c.png

# Left edge
convert -size 8x32 xc:"#991830" \
    select_w.png

# Right edge
convert -size 8x32 xc:"#991830" \
    select_e.png

echo "✓ Selection box created"

# ──────────────────────────────────────────────────────────────────────────
# COMPLETION
# ──────────────────────────────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✓ All GRUB theme assets created successfully!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Assets created:"
ls -lh *.png
echo ""
echo "To install theme:"
echo "  sudo mkdir -p /boot/grub/themes/synos"
echo "  sudo cp -r $(pwd)/* /boot/grub/themes/synos/"
echo "  # Add to /etc/default/grub:"
echo "  GRUB_THEME=\"/boot/grub/themes/synos/theme.txt\""
echo "  sudo update-grub"
echo ""
