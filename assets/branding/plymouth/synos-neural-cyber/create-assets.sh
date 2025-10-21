#!/bin/bash
################################################################################
# SynOS Neural-Cyber Plymouth Theme Asset Generator
# Colors: True Black (#000000), Scarlet (#DC143C), White (#FFFFFF)
################################################################################

set -euo pipefail

THEME_DIR="$(dirname "$0")"
cd "$THEME_DIR"

echo "Creating SynOS Neural-Cyber Plymouth assets..."

# Color definitions
BLACK="#000000"
SCARLET="#DC143C"
BRIGHT_SCARLET="#FF2400"
WHITE="#FFFFFF"
GRAY="#E0E0E0"

# ──────────────────────────────────────────────────────────────────────────
# 1. SYNOS LOGO (256x256)
# ──────────────────────────────────────────────────────────────────────────

echo "Creating logo..."

# Create a simple geometric scarlet logo on black background
# (Text rendering requires Pango/Cairo, use geometric shapes instead)
convert -size 256x256 xc:"$BLACK" \
    -fill "$SCARLET" \
    -draw "circle 128,128 128,60" \
    -fill "$BLACK" \
    -draw "circle 128,128 128,80" \
    -fill "$SCARLET" \
    -draw "rectangle 100,110 156,146" \
    -fill "$WHITE" \
    -draw "circle 128,128 128,115" \
    -fill "$BLACK" \
    -draw "circle 128,128 128,117" \
    synos-logo-256.png

echo "✓ Logo created (geometric design)"

# ──────────────────────────────────────────────────────────────────────────
# 2. SCANNING LINE (for cyberpunk phase)
# ──────────────────────────────────────────────────────────────────────────

echo "Creating scan line..."

# Create a horizontal scarlet line with glow effect
convert -size 1920x4 xc:"$SCARLET" \
    -blur 0x2 \
    scan-line.png

echo "✓ Scan line created"

# ──────────────────────────────────────────────────────────────────────────
# 3. PROGRESS BAR BACKGROUND
# ──────────────────────────────────────────────────────────────────────────

echo "Creating progress bar background..."

convert -size 400x4 xc:"#333333" \
    progress-bg.png

echo "✓ Progress bar background created"

# ──────────────────────────────────────────────────────────────────────────
# 4. PROGRESS BAR FOREGROUND (Scarlet)
# ──────────────────────────────────────────────────────────────────────────

echo "Creating progress bar foreground..."

convert -size 400x4 \
    gradient:"$SCARLET-$BRIGHT_SCARLET" \
    -blur 0x1 \
    progress-fg.png

echo "✓ Progress bar foreground created"

# ──────────────────────────────────────────────────────────────────────────
# 5. NEURAL NODE DOT (optional, for script reference)
# ──────────────────────────────────────────────────────────────────────────

echo "Creating neural node..."

convert -size 16x16 xc:none \
    -fill "$SCARLET" \
    -draw "circle 8,8 8,1" \
    -blur 0x1 \
    neural-node.png

echo "✓ Neural node created"

# ──────────────────────────────────────────────────────────────────────────
# COMPLETION
# ──────────────────────────────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✓ All Plymouth assets created successfully!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Assets created:"
ls -lh *.png
echo ""
echo "To install theme:"
echo "  sudo cp -r $(pwd) /usr/share/plymouth/themes/"
echo "  sudo plymouth-set-default-theme synos-neural-cyber"
echo "  sudo update-initramfs -u"
echo ""
