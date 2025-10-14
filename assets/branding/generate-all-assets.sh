#!/bin/bash
################################################################################
# SynOS Revolutionary Branding - Asset Generation Script
# Generates all logo variants, boot assets, and desktop elements
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/source-designs"
OUTPUT_DIR="${SCRIPT_DIR}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     SynOS Revolutionary Branding - Asset Generator           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for required tools
command -v convert &> /dev/null || { echo -e "${RED}Error: ImageMagick not found${NC}"; exit 1; }

################################################################################
# Create directory structure
################################################################################

echo -e "${CYAN}Creating directory structure...${NC}"

mkdir -p "${OUTPUT_DIR}/logos/phoenix"
mkdir -p "${OUTPUT_DIR}/logos/neural-lock"
mkdir -p "${OUTPUT_DIR}/logos/neural-spiral"
mkdir -p "${OUTPUT_DIR}/logos/circuit-mandala"
mkdir -p "${OUTPUT_DIR}/backgrounds/red-phoenix"
mkdir -p "${OUTPUT_DIR}/plymouth/red-phoenix"
mkdir -p "${OUTPUT_DIR}/grub/neural-command"
mkdir -p "${OUTPUT_DIR}/icons/synos-red"

echo -e "${GREEN}✓ Directory structure created${NC}"

################################################################################
# Generate Phoenix Logo (Primary) - Multiple resolutions
################################################################################

echo -e "${CYAN}Generating Phoenix logo variants...${NC}"

PHOENIX_SOURCE="${SOURCE_DIR}/phoenix-eagle-original.png"

# Multi-resolution PNGs
for size in 1024 512 256 128 64 32 16; do
    convert "${PHOENIX_SOURCE}" -resize ${size}x${size} \
        "${OUTPUT_DIR}/logos/phoenix/phoenix-${size}.png"
    echo -e "${GREEN}✓ Generated phoenix-${size}.png${NC}"
done

# White version (for dark backgrounds)
convert "${PHOENIX_SOURCE}" -fuzz 20% -fill white -opaque red \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-512-white.png"
echo -e "${GREEN}✓ Generated white phoenix variant${NC}"

# Glowing version (with red aura)
convert "${OUTPUT_DIR}/logos/phoenix/phoenix-512.png" \
    \( +clone -background red -shadow 80x8+0+0 \) \
    +swap -background none -layers merge +repage \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-512-glow.png"
echo -e "${GREEN}✓ Generated glowing phoenix variant${NC}"

# Favicon (ICO format)
convert "${OUTPUT_DIR}/logos/phoenix/phoenix-16.png" \
        "${OUTPUT_DIR}/logos/phoenix/phoenix-32.png" \
        "${OUTPUT_DIR}/logos/phoenix/favicon.ico"
echo -e "${GREEN}✓ Generated favicon.ico${NC}"

################################################################################
# Generate Neural Lock Logo (Secondary)
################################################################################

echo -e "${CYAN}Generating Neural Lock logo variants...${NC}"

LOCK_SOURCE="${SOURCE_DIR}/neural-lock-original.png"

for size in 512 256 128 64 32; do
    convert "${LOCK_SOURCE}" -resize ${size}x${size} \
        "${OUTPUT_DIR}/logos/neural-lock/neural-lock-${size}.png"
    echo -e "${GREEN}✓ Generated neural-lock-${size}.png${NC}"
done

# White version
convert "${LOCK_SOURCE}" -fuzz 20% -fill white -opaque red \
    "${OUTPUT_DIR}/logos/neural-lock/neural-lock-512-white.png"
echo -e "${GREEN}✓ Generated white neural-lock variant${NC}"

################################################################################
# Generate Neural Spiral Logo (Tertiary)
################################################################################

echo -e "${CYAN}Generating Neural Spiral logo variants...${NC}"

SPIRAL_SOURCE="${SOURCE_DIR}/neural-spiral-original.png"

for size in 512 256 128 64 32; do
    convert "${SPIRAL_SOURCE}" -resize ${size}x${size} \
        "${OUTPUT_DIR}/logos/neural-spiral/neural-spiral-${size}.png"
    echo -e "${GREEN}✓ Generated neural-spiral-${size}.png${NC}"
done

# Glowing version with enhanced red aura
convert "${OUTPUT_DIR}/logos/neural-spiral/neural-spiral-512.png" \
    \( +clone -background "#ff0000" -shadow 100x12+0+0 \) \
    +swap -background none -layers merge +repage \
    "${OUTPUT_DIR}/logos/neural-spiral/neural-spiral-512-glow.png"
echo -e "${GREEN}✓ Generated glowing spiral variant${NC}"

################################################################################
# Generate Circuit Mandala (Quaternary)
################################################################################

echo -e "${CYAN}Generating Circuit Mandala variants...${NC}"

MANDALA_SOURCE="${SOURCE_DIR}/circuit-mandala-original.png"

# High-resolution wallpapers
convert "${MANDALA_SOURCE}" -resize 3840x2160 \
    "${OUTPUT_DIR}/logos/circuit-mandala/mandala-4k.png"
echo -e "${GREEN}✓ Generated 4K mandala${NC}"

convert "${MANDALA_SOURCE}" -resize 1920x1080 \
    "${OUTPUT_DIR}/logos/circuit-mandala/mandala-1080p.png"
echo -e "${GREEN}✓ Generated 1080p mandala${NC}"

# Embossed/subtle version for backgrounds (reduced opacity)
convert "${MANDALA_SOURCE}" -alpha set -channel A -evaluate multiply 0.3 \
    "${OUTPUT_DIR}/logos/circuit-mandala/mandala-embossed.png"
echo -e "${GREEN}✓ Generated embossed mandala${NC}"

################################################################################
# Generate Wallpapers
################################################################################

echo -e "${CYAN}Generating wallpapers...${NC}"

# Primary Wallpaper: Phoenix Dominance (4K)
convert -size 3840x2160 xc:black \
    "${OUTPUT_DIR}/logos/circuit-mandala/mandala-embossed.png" \
    -gravity center -composite \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-512-glow.png" \
    -gravity center -composite \
    -pointsize 48 -fill white -gravity southeast -annotate +50+50 "Syn_OS" \
    "${OUTPUT_DIR}/backgrounds/red-phoenix/phoenix-dominance-4k.png"
echo -e "${GREEN}✓ Generated Phoenix Dominance 4K wallpaper${NC}"

# 1080p version
convert "${OUTPUT_DIR}/backgrounds/red-phoenix/phoenix-dominance-4k.png" \
    -resize 1920x1080 \
    "${OUTPUT_DIR}/backgrounds/red-phoenix/phoenix-dominance-1080p.png"
echo -e "${GREEN}✓ Generated Phoenix Dominance 1080p wallpaper${NC}"

# Simple black with phoenix (minimalist)
convert -size 1920x1080 xc:black \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-512-glow.png" \
    -gravity center -composite \
    "${OUTPUT_DIR}/backgrounds/red-phoenix/phoenix-minimal-1080p.png"
echo -e "${GREEN}✓ Generated minimal phoenix wallpaper${NC}"

################################################################################
# Generate Plymouth Boot Theme Assets
################################################################################

echo -e "${CYAN}Generating Plymouth boot theme...${NC}"

# Create simple boot logo (phoenix with text)
convert -size 640x480 xc:black \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-256.png" \
    -gravity north -geometry +0+80 -composite \
    -pointsize 36 -fill white -gravity north -annotate +0+360 "Syn_OS" \
    -pointsize 18 -fill "#666666" -gravity north -annotate +0+400 "Consciousness-Enhanced Cybersecurity" \
    "${OUTPUT_DIR}/plymouth/red-phoenix/boot-splash.png"
echo -e "${GREEN}✓ Generated Plymouth boot splash${NC}"

# HD version
convert -size 1920x1080 xc:black \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-512.png" \
    -gravity north -geometry +0+200 -composite \
    -pointsize 72 -fill white -gravity north -annotate +0+750 "Syn_OS" \
    -pointsize 36 -fill "#666666" -gravity north -annotate +0+840 "Consciousness-Enhanced Cybersecurity" \
    "${OUTPUT_DIR}/plymouth/red-phoenix/boot-splash-hd.png"
echo -e "${GREEN}✓ Generated HD Plymouth boot splash${NC}"

# Progress bar elements
convert -size 400x20 xc:"#2a2a2a" \
    "${OUTPUT_DIR}/plymouth/red-phoenix/progress_bar_bg.png"
echo -e "${GREEN}✓ Generated progress bar background${NC}"

convert -size 400x20 gradient:red-"#ff6666" \
    "${OUTPUT_DIR}/plymouth/red-phoenix/progress_bar_fg.png"
echo -e "${GREEN}✓ Generated progress bar foreground${NC}"

# Simple animation frames (5 frames - phoenix pulse)
for i in {1..5}; do
    BRIGHTNESS=$(echo "scale=2; 1 + ($i * 0.1)" | bc)
    convert "${OUTPUT_DIR}/logos/phoenix/phoenix-256.png" \
        -modulate ${BRIGHTNESS}00,100,100 \
        "${OUTPUT_DIR}/plymouth/red-phoenix/phoenix-anim-$(printf '%02d' $i).png"
done
echo -e "${GREEN}✓ Generated 5 phoenix animation frames${NC}"

################################################################################
# Generate GRUB Theme Assets
################################################################################

echo -e "${CYAN}Generating GRUB theme...${NC}"

# GRUB background (16:9)
convert -size 1920x1080 xc:black \
    -fill "#990000" \
    -draw "line 0,0 400,0" \
    -draw "line 0,0 0,400" \
    -draw "line 1920,0 1520,0" \
    -draw "line 1920,0 1920,400" \
    -draw "line 0,1080 400,1080" \
    -draw "line 0,1080 0,680" \
    -draw "line 1920,1080 1520,1080" \
    -draw "line 1920,1080 1920,680" \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-64.png" \
    -gravity north -geometry +0+20 -composite \
    "${OUTPUT_DIR}/grub/neural-command/background-16x9.png"
echo -e "${GREEN}✓ Generated GRUB 16:9 background${NC}"

# GRUB background (4:3)
convert -size 1024x768 xc:black \
    -fill "#990000" \
    -draw "line 0,0 300,0" \
    -draw "line 0,0 0,300" \
    -draw "line 1024,0 724,0" \
    -draw "line 1024,0 1024,300" \
    "${OUTPUT_DIR}/logos/phoenix/phoenix-64.png" \
    -gravity north -geometry +0+20 -composite \
    "${OUTPUT_DIR}/grub/neural-command/background-4x3.png"
echo -e "${GREEN}✓ Generated GRUB 4:3 background${NC}"

# Menu selection (red highlight bar)
convert -size 600x30 xc:"#ff0000" \
    "${OUTPUT_DIR}/grub/neural-command/select_c.png"
echo -e "${GREEN}✓ Generated GRUB selection bar${NC}"

################################################################################
# Generate Icon Theme Base Icons
################################################################################

echo -e "${CYAN}Generating base icon set...${NC}"

# Folder icon (black with red stripe)
convert -size 64x64 xc:none \
    -fill black -draw "roundrectangle 5,20 59,54 5,5" \
    -fill "#ff0000" -draw "rectangle 5,20 59,30" \
    "${OUTPUT_DIR}/icons/synos-red/folder-64.png"
echo -e "${GREEN}✓ Generated folder icon${NC}"

# Text file icon (white page with red corner)
convert -size 64x64 xc:none \
    -fill white -draw "polygon 10,5 54,5 54,59 10,59" \
    -fill "#ff0000" -draw "polygon 54,5 54,15 44,5" \
    "${OUTPUT_DIR}/icons/synos-red/text-file-64.png"
echo -e "${GREEN}✓ Generated text file icon${NC}"

# Executable icon (red gear)
convert -size 64x64 xc:none \
    -fill "#ff0000" \
    -draw "circle 32,32 32,20" \
    -fill black -draw "circle 32,32 32,26" \
    "${OUTPUT_DIR}/icons/synos-red/executable-64.png"
echo -e "${GREEN}✓ Generated executable icon${NC}"

################################################################################
# Create Plymouth Theme Configuration
################################################################################

echo -e "${CYAN}Creating Plymouth theme configuration...${NC}"

cat > "${OUTPUT_DIR}/plymouth/red-phoenix/red-phoenix.plymouth" << 'PLYMOUTH_EOF'
[Plymouth Theme]
Name=Red Phoenix
Description=SynOS Revolutionary Boot Theme - Phoenix Rising
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/red-phoenix
ScriptFile=/usr/share/plymouth/themes/red-phoenix/red-phoenix.script
PLYMOUTH_EOF

cat > "${OUTPUT_DIR}/plymouth/red-phoenix/red-phoenix.script" << 'SCRIPT_EOF'
# SynOS Red Phoenix Plymouth Script

Window.SetBackgroundTopColor(0, 0, 0);
Window.SetBackgroundBottomColor(0, 0, 0);

# Load phoenix logo
logo.image = Image("boot-splash-hd.png");
logo.sprite = Sprite(logo.image);
logo.sprite.SetX(Window.GetWidth() / 2 - logo.image.GetWidth() / 2);
logo.sprite.SetY(Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 50);

# Progress bar
progress_bar.original_image = Image("progress_bar_bg.png");
progress_bar.sprite = Sprite(progress_bar.original_image);
progress_bar.x = Window.GetWidth() / 2 - progress_bar.original_image.GetWidth() / 2;
progress_bar.y = Window.GetHeight() * 0.75;
progress_bar.sprite.SetPosition(progress_bar.x, progress_bar.y, 0);

fun progress_callback(duration, progress) {
    if (progress_bar.image.GetWidth() != Math.Int(progress_bar.original_image.GetWidth() * progress)) {
        progress_bar.image = Image("progress_bar_fg.png");
        progress_bar.image = progress_bar.image.Scale(Math.Int(progress_bar.original_image.GetWidth() * progress), progress_bar.image.GetHeight());
        progress_bar.sprite.SetImage(progress_bar.image);
    }
}

Plymouth.SetBootProgressFunction(progress_callback);
SCRIPT_EOF

echo -e "${GREEN}✓ Created Plymouth theme configuration${NC}"

################################################################################
# Create GRUB Theme Configuration
################################################################################

echo -e "${CYAN}Creating GRUB theme configuration...${NC}"

cat > "${OUTPUT_DIR}/grub/neural-command/theme.txt" << 'GRUB_EOF'
# SynOS Neural Command GRUB Theme

# General settings
title-text: ""
desktop-image: "background-16x9.png"
desktop-color: "#000000"
terminal-font: "Unifont Regular 16"

# Boot menu
+ boot_menu {
    left = 25%
    top = 30%
    width = 50%
    height = 60%
    item_color = "#ffffff"
    selected_item_color = "#000000"
    item_height = 30
    item_padding = 10
    item_spacing = 5
    selected_item_pixmap_style = "select_*.png"
}

# Progress bar
+ progress_bar {
    id = "__timeout__"
    left = 25%
    top = 85%
    height = 20
    width = 50%
    fg_color = "#ff0000"
    bg_color = "#2a2a2a"
    border_color = "#666666"
    text = ""
}
GRUB_EOF

echo -e "${GREEN}✓ Created GRUB theme configuration${NC}"

################################################################################
# Summary
################################################################################

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                  Asset Generation Complete                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Generated Assets:${NC}"
echo "  • Phoenix logos: 7 sizes + variants"
echo "  • Neural Lock logos: 5 sizes"
echo "  • Neural Spiral logos: 5 sizes + glow"
echo "  • Circuit Mandala: 4K, 1080p, embossed"
echo "  • Wallpapers: 3 variants (4K, 1080p, minimal)"
echo "  • Plymouth theme: Complete boot theme"
echo "  • GRUB theme: Complete boot menu theme"
echo "  • Icon set: 3 base icons"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  1. Review generated assets in ${OUTPUT_DIR}"
echo "  2. Run deployment script to install assets"
echo "  3. Update ISO build script to use new branding"
echo "  4. Test Plymouth and GRUB themes in VM"
echo ""
echo -e "${GREEN}Assets ready for revolutionary SynOS v1.0 branding! 🔴${NC}"
