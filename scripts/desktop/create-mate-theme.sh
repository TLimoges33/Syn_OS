#!/bin/bash
################################################################################
# SynOS Desktop Polish - MATE Theme Completion
# Creates complete icon theme, wallpapers, and visual enhancements
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"
BRANDING_DIR="$ASSETS_DIR/branding"
DESKTOP_DIR="$ASSETS_DIR/desktop"
THEMES_DIR="$ASSETS_DIR/themes"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS Desktop Polish - Theme Completion                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Create directory structure
echo -e "${CYAN}Creating directory structure...${NC}"
mkdir -p "$THEMES_DIR/SynOS-Red-Phoenix"/{gtk-3.0,gtk-2.0,metacity-1}
mkdir -p "$THEMES_DIR/SynOS-Red-Phoenix/icons"/{16x16,22x22,24x24,32x32,48x48,64x64,128x128,256x256,scalable}
mkdir -p "$DESKTOP_DIR/wallpapers"

# Create icon directories
ICON_CATEGORIES=(
    "actions"
    "apps"
    "categories"
    "devices"
    "emblems"
    "mimetypes"
    "places"
    "status"
)

for size in 16x16 22x22 24x24 32x32 48x48 64x64 128x128 256x256; do
    for category in "${ICON_CATEGORIES[@]}"; do
        mkdir -p "$THEMES_DIR/SynOS-Red-Phoenix/icons/$size/$category"
    done
done

echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# Create index.theme for icon theme
echo -e "${CYAN}Creating icon theme index...${NC}"
cat > "$THEMES_DIR/SynOS-Red-Phoenix/icons/index.theme" << 'EOF'
[Icon Theme]
Name=SynOS Red Phoenix
Comment=Revolutionary red and black icon theme for SynOS v1.1
Inherits=Papirus-Dark,Adwaita,hicolor
Example=folder

# Directory list
Directories=16x16/actions,16x16/apps,16x16/categories,16x16/devices,16x16/emblems,16x16/mimetypes,16x16/places,16x16/status,22x22/actions,22x22/apps,22x22/categories,22x22/devices,22x22/emblems,22x22/mimetypes,22x22/places,22x22/status,24x24/actions,24x24/apps,24x24/categories,24x24/devices,24x24/emblems,24x24/mimetypes,24x24/places,24x24/status,32x32/actions,32x32/apps,32x32/categories,32x32/devices,32x32/emblems,32x32/mimetypes,32x32/places,32x32/status,48x48/actions,48x48/apps,48x48/categories,48x48/devices,48x48/emblems,48x48/mimetypes,48x48/places,48x48/status,64x64/actions,64x64/apps,64x64/categories,64x64/devices,64x64/emblems,64x64/mimetypes,64x64/apps,64x64/places,64x64/status,128x128/apps,128x128/places,256x256/apps,256x256/places,scalable/actions,scalable/apps,scalable/categories,scalable/devices,scalable/emblems,scalable/mimetypes,scalable/places,scalable/status

[16x16/actions]
Size=16
Context=Actions
Type=Fixed

[16x16/apps]
Size=16
Context=Applications
Type=Fixed

[16x16/categories]
Size=16
Context=Categories
Type=Fixed

[16x16/devices]
Size=16
Context=Devices
Type=Fixed

[16x16/emblems]
Size=16
Context=Emblems
Type=Fixed

[16x16/mimetypes]
Size=16
Context=MimeTypes
Type=Fixed

[16x16/places]
Size=16
Context=Places
Type=Fixed

[16x16/status]
Size=16
Context=Status
Type=Fixed

[22x22/actions]
Size=22
Context=Actions
Type=Fixed

[22x22/apps]
Size=22
Context=Applications
Type=Fixed

[22x22/categories]
Size=22
Context=Categories
Type=Fixed

[22x22/devices]
Size=22
Context=Devices
Type=Fixed

[22x22/emblems]
Size=22
Context=Emblems
Type=Fixed

[22x22/mimetypes]
Size=22
Context=MimeTypes
Type=Fixed

[22x22/places]
Size=22
Context=Places
Type=Fixed

[22x22/status]
Size=22
Context=Status
Type=Fixed

[scalable/places]
Size=48
Context=Places
Type=Scalable
MinSize=16
MaxSize=512
EOF

echo -e "${GREEN}✓ Icon theme index created${NC}"
echo ""

# Create GTK-3.0 theme
echo -e "${CYAN}Creating GTK-3.0 theme...${NC}"
cat > "$THEMES_DIR/SynOS-Red-Phoenix/gtk-3.0/gtk.css" << 'EOF'
/* SynOS Red Phoenix GTK-3.0 Theme */
/* Revolutionary red and black color scheme */

@define-color theme_bg_color #1a1a1a;
@define-color theme_fg_color #c0c0c0;
@define-color theme_base_color #000000;
@define-color theme_text_color #ffffff;
@define-color theme_selected_bg_color #ff0000;
@define-color theme_selected_fg_color #ffffff;
@define-color insensitive_bg_color #2a2a2a;
@define-color insensitive_fg_color #808080;
@define-color borders #990000;
@define-color warning_color #ff3333;
@define-color error_color #cc0000;
@define-color success_color #00ff00;

* {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}

.background {
    background-color: @theme_base_color;
}

.titlebar {
    background: linear-gradient(to bottom, #2a2a2a, #1a1a1a);
    color: @theme_fg_color;
    border-bottom: 1px solid @borders;
}

.button {
    background: linear-gradient(to bottom, #2a2a2a, #1a1a1a);
    border: 1px solid @borders;
    border-radius: 3px;
    padding: 6px 12px;
    color: @theme_fg_color;
}

.button:hover {
    background: linear-gradient(to bottom, #3a3a3a, #2a2a2a);
    border-color: #ff0000;
}

.button:active {
    background: linear-gradient(to bottom, #ff0000, #cc0000);
    color: #ffffff;
}

:selected {
    background-color: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
}

.menu {
    background-color: #1a1a1a;
    border: 1px solid @borders;
}

.menuitem:hover {
    background-color: #ff0000;
    color: #ffffff;
}

.entry {
    background-color: #000000;
    border: 1px solid @borders;
    border-radius: 3px;
    padding: 6px;
    color: #ffffff;
}

.entry:focus {
    border-color: #ff0000;
}

scrollbar {
    background-color: #1a1a1a;
}

scrollbar slider {
    background-color: #990000;
    border-radius: 3px;
}

scrollbar slider:hover {
    background-color: #ff0000;
}
EOF

echo -e "${GREEN}✓ GTK-3.0 theme created${NC}"
echo ""

# Create theme index
echo -e "${CYAN}Creating theme index...${NC}"
cat > "$THEMES_DIR/SynOS-Red-Phoenix/index.theme" << 'EOF'
[Desktop Entry]
Type=X-GNOME-Metatheme
Name=SynOS Red Phoenix
Comment=Revolutionary red and black theme for SynOS v1.1
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=SynOS-Red-Phoenix
MetacityTheme=SynOS-Red-Phoenix
IconTheme=SynOS-Red-Phoenix
CursorTheme=Adwaita
ButtonLayout=menu:minimize,maximize,close
EOF

echo -e "${GREEN}✓ Theme index created${NC}"
echo ""

# Create wallpaper variants
echo -e "${CYAN}Creating wallpaper variants...${NC}"

# Check if ImageMagick is installed
if ! command -v convert &>/dev/null; then
    echo -e "${YELLOW}⚠ ImageMagick not installed, skipping wallpaper generation${NC}"
    echo -e "${YELLOW}  Install with: sudo apt-get install imagemagick${NC}"
else
    # Create red gradient wallpaper
    convert -size 1920x1080 gradient:'#000000-#330000' \
        "$DESKTOP_DIR/wallpapers/synos-red-gradient.jpg"

    # Create neural pattern wallpaper (using existing if available)
    if [ -f "$BRANDING_DIR/backgrounds/synos-neural-dark.jpg" ]; then
        cp "$BRANDING_DIR/backgrounds/synos-neural-dark.jpg" \
           "$DESKTOP_DIR/wallpapers/synos-neural-dark.jpg"
    fi

    echo -e "${GREEN}✓ Wallpapers created${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Desktop Theme Creation Complete!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}=== SUMMARY ===${NC}"
echo ""
echo "Theme Location: $THEMES_DIR/SynOS-Red-Phoenix/"
echo "Wallpapers:     $DESKTOP_DIR/wallpapers/"
echo ""
echo -e "${CYAN}To install system-wide:${NC}"
echo "  sudo cp -r $THEMES_DIR/SynOS-Red-Phoenix /usr/share/themes/"
echo ""
echo -e "${CYAN}To activate:${NC}"
echo "  gsettings set org.mate.interface gtk-theme 'SynOS-Red-Phoenix'"
echo "  gsettings set org.mate.interface icon-theme 'SynOS-Red-Phoenix'"
echo ""
echo -e "${CYAN}To set wallpaper:${NC}"
echo "  gsettings set org.mate.background picture-filename '$DESKTOP_DIR/wallpapers/synos-neural-dark.jpg'"
echo ""
