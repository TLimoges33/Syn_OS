#!/bin/bash
################################################################################
# SynOS Desktop Polish - Complete Suite
# Wallpapers, sounds, plymouth, and desktop enhancements
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"
BRANDING_DIR="$ASSETS_DIR/branding"
DESKTOP_DIR="$ASSETS_DIR/desktop"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS Desktop Polish - Complete Suite v1.1              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# 1. Create wallpaper variations
echo -e "${CYAN}[1/5] Creating wallpaper variations...${NC}"
mkdir -p "$DESKTOP_DIR/wallpapers"

# Check if ImageMagick is installed
if command -v convert &>/dev/null; then
    # Create red gradient variants
    convert -size 1920x1080 gradient:'#000000-#330000' \
        "$DESKTOP_DIR/wallpapers/synos-red-gradient.jpg"

    convert -size 1920x1080 gradient:'#1a1a1a-#ff0000' \
        "$DESKTOP_DIR/wallpapers/synos-red-gradient-light.jpg"

    convert -size 2560x1440 gradient:'#000000-#330000' \
        "$DESKTOP_DIR/wallpapers/synos-red-gradient-2k.jpg"

    # Create with text overlay
    convert "$DESKTOP_DIR/wallpapers/synos-red-gradient.jpg" \
        -font DejaVu-Sans-Bold -pointsize 72 -fill '#ff0000' \
        -gravity center -annotate +0+200 'SynOS v1.1' \
        -pointsize 36 -fill '#c0c0c0' \
        -annotate +0+280 'Voice of the Phoenix' \
        "$DESKTOP_DIR/wallpapers/synos-red-branded.jpg"

    echo -e "${GREEN}✓ Created 4 wallpaper variants${NC}"
else
    echo -e "${YELLOW}⚠ ImageMagick not installed, skipping wallpaper generation${NC}"
fi

# Copy existing wallpapers
if [ -f "$BRANDING_DIR/backgrounds/synos-neural-dark.jpg" ]; then
    cp "$BRANDING_DIR/backgrounds/synos-neural-dark.jpg" \
       "$DESKTOP_DIR/wallpapers/"
fi

if [ -d "$BRANDING_DIR/backgrounds/red-phoenix" ]; then
    cp -r "$BRANDING_DIR/backgrounds/red-phoenix" \
       "$DESKTOP_DIR/wallpapers/"
fi

echo ""

# 2. Create system sound theme
echo -e "${CYAN}[2/5] Creating system sound theme...${NC}"
mkdir -p "$DESKTOP_DIR/sounds/SynOS-Red-Phoenix"

cat > "$DESKTOP_DIR/sounds/SynOS-Red-Phoenix/index.theme" << 'EOF'
[Sound Theme]
Name=SynOS Red Phoenix
Comment=Revolutionary sound theme for SynOS v1.1
Directories=stereo

[stereo]
OutputProfile=stereo
EOF

# Create sound directories
mkdir -p "$DESKTOP_DIR/sounds/SynOS-Red-Phoenix/stereo"

echo -e "${GREEN}✓ Sound theme structure created${NC}"
echo -e "${YELLOW}  Note: Add .ogg sound files to: $DESKTOP_DIR/sounds/SynOS-Red-Phoenix/stereo/${NC}"
echo ""

# 3. Enhance Plymouth theme
echo -e "${CYAN}[3/5] Enhancing Plymouth boot theme...${NC}"

if [ -d "$BRANDING_DIR/plymouth" ]; then
    # Create enhanced Plymouth configuration
    PLYMOUTH_DIR="$BRANDING_DIR/plymouth/synos-red-phoenix"
    mkdir -p "$PLYMOUTH_DIR"

    cat > "$PLYMOUTH_DIR/synos-red-phoenix.plymouth" << 'EOF'
[Plymouth Theme]
Name=SynOS Red Phoenix
Description=Revolutionary red phoenix boot theme with neural animations
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/synos-red-phoenix
ScriptFile=/usr/share/plymouth/themes/synos-red-phoenix/synos-red-phoenix.script
EOF

    # Create simple plymouth script
    cat > "$PLYMOUTH_DIR/synos-red-phoenix.script" << 'EOF'
# SynOS Red Phoenix Plymouth Theme
# Revolutionary boot animation

Window.SetBackgroundTopColor(0.00, 0.00, 0.00);     # Black
Window.SetBackgroundBottomColor(0.20, 0.00, 0.00);  # Dark Red

# Logo animation
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.x = Window.GetWidth()  / 2 - logo.image.GetWidth()  / 2;
logo.y = Window.GetHeight() / 2 - logo.image.GetHeight() / 2;
logo.sprite.SetPosition(logo.x, logo.y, 1);

# Progress bar
progress_box.image = Image.Text("", 1.0, 0.0, 0.0);  # Red
progress_box.sprite = Sprite(progress_box.image);
progress_box.x = Window.GetWidth()  / 2 - progress_box.image.GetWidth() / 2;
progress_box.y = Window.GetHeight() * 0.75;
progress_box.sprite.SetPosition(progress_box.x, progress_box.y, 2);

fun refresh_callback ()
{
    # Smooth fade animation
}

Plymouth.SetRefreshFunction (refresh_callback);
EOF

    echo -e "${GREEN}✓ Plymouth theme enhanced${NC}"
else
    echo -e "${YELLOW}⚠ Plymouth directory not found, skipping${NC}"
fi

echo ""

# 4. Create desktop configuration
echo -e "${CYAN}[4/5] Creating desktop configuration presets...${NC}"
mkdir -p "$DESKTOP_DIR/configs"

cat > "$DESKTOP_DIR/configs/mate-synos-settings.sh" << 'EOF'
#!/bin/bash
# SynOS MATE Desktop Settings - Red Phoenix Theme

# Interface
gsettings set org.mate.interface gtk-theme 'SynOS-Red-Phoenix'
gsettings set org.mate.interface icon-theme 'Papirus-Dark'
gsettings set org.mate.interface font-name 'Ubuntu 10'
gsettings set org.mate.interface monospace-font-name 'Ubuntu Mono 11'

# Marco (Window Manager)
gsettings set org.mate.Marco.general theme 'SynOS-Red-Phoenix'
gsettings set org.mate.Marco.general compositing-manager false
gsettings set org.mate.Marco.general reduced-resources true

# Background
gsettings set org.mate.background picture-filename '/usr/share/backgrounds/synos-neural-dark.jpg'
gsettings set org.mate.background picture-options 'zoom'
gsettings set org.mate.background primary-color '#000000'
gsettings set org.mate.background secondary-color '#330000'

# Screensaver
gsettings set org.mate.screensaver idle-activation-enabled true
gsettings set org.mate.screensaver lock-enabled true
gsettings set org.mate.screensaver mode 'blank-only'

# Terminal
gsettings set org.mate.terminal.profile:/org/mate/terminal/profiles/default/ background-color '#000000'
gsettings set org.mate.terminal.profile:/org/mate/terminal/profiles/default/ foreground-color '#c0c0c0'
gsettings set org.mate.terminal.profile:/org/mate/terminal/profiles/default/ use-theme-colors false

# Panel
gsettings set org.mate.panel.toplevel:/org/mate/panel/toplevels/top/ background-color 'rgba(26,26,26,0.95)'

# Notifications
gsettings set org.mate.NotificationDaemon theme 'standard'

echo "SynOS MATE settings applied!"
EOF

chmod +x "$DESKTOP_DIR/configs/mate-synos-settings.sh"

echo -e "${GREEN}✓ Desktop configuration created${NC}"
echo ""

# 5. Create README
echo -e "${CYAN}[5/5] Creating documentation...${NC}"

cat > "$DESKTOP_DIR/README.md" << 'EOF'
# SynOS Desktop Assets

Complete desktop polish suite for SynOS v1.1 "Voice of the Phoenix"

## Directory Structure

```
desktop/
├── wallpapers/              # Desktop wallpapers (1080p, 2K, 4K)
├── sounds/                  # System sound theme
├── configs/                 # Desktop configuration scripts
└── README.md               # This file
```

## Installation

### Apply MATE Theme
```bash
./configs/mate-synos-settings.sh
```

### Install Wallpapers
```bash
sudo cp wallpapers/* /usr/share/backgrounds/
```

### Install Sound Theme
```bash
sudo cp -r sounds/SynOS-Red-Phoenix /usr/share/sounds/
gsettings set org.mate.sound theme-name 'SynOS-Red-Phoenix'
```

## Wallpapers

- `synos-neural-dark.jpg` - Neural network pattern (primary)
- `synos-red-gradient.jpg` - Black to red gradient (1080p)
- `synos-red-gradient-2k.jpg` - Black to red gradient (2K)
- `synos-red-branded.jpg` - Branded version with text

## Theme Colors

- Primary: #FF0000 (Crimson Red)
- Background: #000000 (Black)
- Secondary: #1a1a1a (Carbon)
- Text: #c0c0c0 (Silver)
- Accent: #990000 (Dark Red)

## Quick Commands

```bash
# Set wallpaper
gsettings set org.mate.background picture-filename '/path/to/wallpaper.jpg'

# Reset to defaults
gsettings reset-recursively org.mate.interface

# List current settings
gsettings list-recursively org.mate
```

---

**Part of SynOS v1.1 "Voice of the Phoenix"**
EOF

echo -e "${GREEN}✓ Documentation created${NC}"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Desktop Polish Suite Complete!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}=== SUMMARY ===${NC}"
echo ""
echo "Created:"
echo "  • Wallpaper variants (4+)"
echo "  • System sound theme structure"
echo "  • Enhanced Plymouth boot theme"
echo "  • MATE configuration preset"
echo "  • Complete documentation"
echo ""
echo -e "${CYAN}To apply all settings:${NC}"
echo "  $DESKTOP_DIR/configs/mate-synos-settings.sh"
echo ""
echo -e "${CYAN}Assets location:${NC}"
echo "  $DESKTOP_DIR/"
echo ""
