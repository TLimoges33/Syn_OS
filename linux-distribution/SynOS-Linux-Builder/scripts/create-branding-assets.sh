#!/bin/bash

# SynOS Branding Assets Creator
# Creates custom themes, wallpapers, and branding elements

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    local timestamp=$(date '+%H:%M:%S')

    case $status in
        "success") echo -e "${GREEN}✅ [$timestamp]${NC} $message" ;;
        "error") echo -e "${RED}❌ [$timestamp]${NC} $message" ;;
        "info") echo -e "${BLUE}ℹ️  [$timestamp]${NC} $message" ;;
        "warning") echo -e "${YELLOW}⚠️  [$timestamp]${NC} $message" ;;
        "header") echo -e "${CYAN}🚀 $message${NC}" ;;
        "section") echo -e "${PURPLE}🔧 [$timestamp]${NC} $message" ;;
    esac
}

echo ""
print_status "header" "======================================================="
print_status "header" "    SynOS Branding Assets Creation"
print_status "header" "    Creating Custom Themes and Visual Identity"
print_status "header" "======================================================="
echo ""

# Verify build directory
if [[ ! -d "$BUILD_DIR" ]]; then
    print_status "error" "Build directory not found. Run build-synos-base.sh first"
    exit 1
fi

cd "$BUILD_DIR"

# Create branding directory structure
print_status "section" "Creating branding directory structure..."
mkdir -p config/includes.chroot/usr/share/backgrounds/synos
mkdir -p config/includes.chroot/usr/share/themes/SynOS
mkdir -p config/includes.chroot/usr/share/icons/synos
mkdir -p config/includes.chroot/usr/share/pixmaps/synos
mkdir -p config/includes.chroot/usr/share/plymouth/themes/synos

print_status "success" "Branding directories created"

# Create SynOS color scheme
print_status "section" "Creating SynOS color scheme..."

# SynOS Color Palette
cat > config/includes.chroot/usr/share/synos/colors.conf << 'EOF'
# SynOS Color Palette
# Neural Network Consciousness Theme

# Primary Colors
SYNOS_PURPLE="#6366f1"
SYNOS_BLUE="#3b82f6"
SYNOS_CYAN="#06b6d4"
SYNOS_GREEN="#10b981"

# Background Colors
SYNOS_DARK_BG="#1a1a2e"
SYNOS_MEDIUM_BG="#16213e"
SYNOS_LIGHT_BG="#334155"

# Text Colors
SYNOS_TEXT_PRIMARY="#f8fafc"
SYNOS_TEXT_SECONDARY="#cbd5e1"
SYNOS_TEXT_ACCENT="#c084fc"

# Accent Colors
SYNOS_ACCENT_1="#8b5cf6"
SYNOS_ACCENT_2="#ec4899"
SYNOS_WARNING="#f59e0b"
SYNOS_ERROR="#ef4444"
SYNOS_SUCCESS="#22c55e"
EOF

print_status "success" "Color scheme defined"

# Create ASCII art wallpaper (text-based for compatibility)
print_status "section" "Creating SynOS wallpaper..."

cat > config/includes.chroot/usr/share/backgrounds/synos/synos-ascii-art.txt << 'EOF'
   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗
   ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝
   ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗
   ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║
   ███████║   ██║   ██║ ╚████║╚██████╔╝███████║
   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝

    ⚡ Consciousness-Enhanced Cybersecurity Distribution ⚡

         🧠 Neural Darwinism Engine
         📚 Educational Framework
         🛡️ Advanced Security Tools
         🤖 AI-Powered Learning

EOF

# Create simple wallpaper script (creates solid color background)
cat > config/includes.chroot/usr/share/backgrounds/synos/create-wallpaper.sh << 'EOF'
#!/bin/bash
# Create SynOS wallpaper with ImageMagick if available

WALLPAPER_DIR="/usr/share/backgrounds/synos"
WIDTH=1920
HEIGHT=1080

# Check if ImageMagick is available
if command -v convert &>/dev/null; then
    echo "Creating SynOS neural network wallpaper..."

    # Create gradient background
    convert -size ${WIDTH}x${HEIGHT} \
        gradient:'#1a1a2e-#16213e' \
        "$WALLPAPER_DIR/synos-neural-wallpaper.jpg"

    # Add neural network overlay (simple version)
    convert "$WALLPAPER_DIR/synos-neural-wallpaper.jpg" \
        -fill '#6366f1' -pointsize 72 \
        -gravity center -annotate +0-200 "SynOS Linux" \
        -fill '#cbd5e1' -pointsize 24 \
        -gravity center -annotate +0-100 "AI-Enhanced Cybersecurity Distribution" \
        -fill '#8b5cf6' -pointsize 18 \
        -gravity center -annotate +0+100 "🧠 Neural Darwinism • 📚 Education • 🛡️ Security" \
        "$WALLPAPER_DIR/synos-neural-wallpaper.jpg"

    echo "✅ SynOS wallpaper created"
else
    echo "⚠️ ImageMagick not available, using fallback wallpaper"
    # Create a simple solid color image with shell tools
    printf "P3\n$WIDTH $HEIGHT\n255\n" > "$WALLPAPER_DIR/synos-neural-wallpaper.ppm"
    for ((i=0; i<WIDTH*HEIGHT; i++)); do
        echo "26 26 46"  # RGB for #1a1a2e
    done >> "$WALLPAPER_DIR/synos-neural-wallpaper.ppm"

    # Convert to JPEG if possible, otherwise keep PPM
    if command -v ppmtojpeg &>/dev/null; then
        ppmtojpeg "$WALLPAPER_DIR/synos-neural-wallpaper.ppm" > "$WALLPAPER_DIR/synos-neural-wallpaper.jpg"
        rm "$WALLPAPER_DIR/synos-neural-wallpaper.ppm"
    fi
fi
EOF

chmod +x config/includes.chroot/usr/share/backgrounds/synos/create-wallpaper.sh

print_status "success" "Wallpaper creation script prepared"

# Create MATE theme configuration
print_status "section" "Creating MATE desktop theme..."

mkdir -p config/includes.chroot/usr/share/themes/SynOS/gtk-2.0
mkdir -p config/includes.chroot/usr/share/themes/SynOS/gtk-3.0
mkdir -p config/includes.chroot/usr/share/themes/SynOS/metacity-1

# GTK 3.0 theme
cat > config/includes.chroot/usr/share/themes/SynOS/gtk-3.0/gtk.css << 'EOF'
/* SynOS GTK 3.0 Theme - Neural Network Consciousness */

@define-color synos_purple #6366f1;
@define-color synos_blue #3b82f6;
@define-color synos_cyan #06b6d4;
@define-color synos_dark_bg #1a1a2e;
@define-color synos_medium_bg #16213e;
@define-color synos_light_bg #334155;
@define-color synos_text #f8fafc;
@define-color synos_text_secondary #cbd5e1;

/* Window and panel styling */
.background {
    background-color: @synos_dark_bg;
    color: @synos_text;
}

/* Panel styling */
PanelToplevel, .mate-panel-menu-bar {
    background: linear-gradient(to bottom, @synos_medium_bg, @synos_dark_bg);
    color: @synos_text;
    border-bottom: 2px solid @synos_purple;
}

/* Menu styling */
.menu, .mate-panel-menu {
    background-color: @synos_medium_bg;
    color: @synos_text;
    border: 1px solid @synos_purple;
}

.menuitem:hover {
    background-color: @synos_purple;
    color: white;
}

/* Button styling */
.button {
    background: linear-gradient(to bottom, @synos_light_bg, @synos_medium_bg);
    color: @synos_text;
    border: 1px solid @synos_purple;
    border-radius: 3px;
}

.button:hover {
    background: linear-gradient(to bottom, @synos_purple, @synos_blue);
    color: white;
}

/* Window decoration */
.titlebar {
    background: linear-gradient(to bottom, @synos_medium_bg, @synos_dark_bg);
    color: @synos_text;
    border-bottom: 1px solid @synos_purple;
}

/* Entry fields */
.entry {
    background-color: @synos_light_bg;
    color: @synos_text;
    border: 1px solid @synos_purple;
}

/* Scrollbars */
.scrollbar {
    background-color: @synos_medium_bg;
}

.scrollbar .slider {
    background-color: @synos_purple;
}
EOF

# Create theme index
cat > config/includes.chroot/usr/share/themes/SynOS/index.theme << 'EOF'
[Desktop Entry]
Type=X-GNOME-Metatheme
Name=SynOS
Comment=SynOS Neural Network Consciousness Theme
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=SynOS
MetacityTheme=SynOS
IconTheme=Faenza-Dark
CursorTheme=DMZ-Black
ButtonLayout=menu:minimize,maximize,close
EOF

print_status "success" "MATE theme created"

# Create Plymouth boot theme
print_status "section" "Creating Plymouth boot theme..."

cat > config/includes.chroot/usr/share/plymouth/themes/synos/synos.plymouth << 'EOF'
[Plymouth Theme]
Name=SynOS
Description=SynOS Neural Network Boot Theme
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/synos
ScriptFile=/usr/share/plymouth/themes/synos/synos.script
EOF

# Simple Plymouth script
cat > config/includes.chroot/usr/share/plymouth/themes/synos/synos.script << 'EOF'
# SynOS Plymouth Boot Animation Script

# Set background color
Window.SetBackgroundTopColor(0.10, 0.10, 0.18);    # #1a1a2e
Window.SetBackgroundBottomColor(0.09, 0.13, 0.24); # #16213e

# Create SynOS logo text
synos_logo = Image.Text("SynOS Linux", 1.0, 1.0, 1.0, 1.0, "Ubuntu 36");
synos_logo_sprite = Sprite(synos_logo);
synos_logo_sprite.SetPosition(Window.GetWidth() / 2 - synos_logo.GetWidth() / 2, Window.GetHeight() / 2 - 100);

# Create subtitle
subtitle = Image.Text("Consciousness-Enhanced Cybersecurity Distribution", 0.7, 0.7, 0.7, 1.0, "Ubuntu 16");
subtitle_sprite = Sprite(subtitle);
subtitle_sprite.SetPosition(Window.GetWidth() / 2 - subtitle.GetWidth() / 2, Window.GetHeight() / 2 - 50);

# Create loading message
loading_text = Image.Text("Initializing AI Consciousness...", 0.4, 0.4, 0.9, 1.0, "Ubuntu 14");
loading_sprite = Sprite(loading_text);
loading_sprite.SetPosition(Window.GetWidth() / 2 - loading_text.GetWidth() / 2, Window.GetHeight() / 2 + 50);

# Animation counter
progress = 0;

fun refresh_callback() {
    progress++;

    # Animate loading text
    if (progress % 30 < 10) {
        loading_text = Image.Text("Initializing AI Consciousness.", 0.4, 0.4, 0.9, 1.0, "Ubuntu 14");
    } else if (progress % 30 < 20) {
        loading_text = Image.Text("Initializing AI Consciousness..", 0.4, 0.4, 0.9, 1.0, "Ubuntu 14");
    } else {
        loading_text = Image.Text("Initializing AI Consciousness...", 0.4, 0.4, 0.9, 1.0, "Ubuntu 14");
    }

    loading_sprite.SetImage(loading_text);
    loading_sprite.SetPosition(Window.GetWidth() / 2 - loading_text.GetWidth() / 2, Window.GetHeight() / 2 + 50);
}

Plymouth.SetRefreshFunction(refresh_callback);
EOF

print_status "success" "Plymouth boot theme created"

# Create custom GRUB theme
print_status "section" "Creating GRUB boot theme..."

mkdir -p config/includes.chroot/usr/share/grub/themes/synos

cat > config/includes.chroot/usr/share/grub/themes/synos/theme.txt << 'EOF'
# SynOS GRUB Theme
# Neural Network Consciousness Boot Menu

# General settings
title-text: "SynOS Linux"
title-font: "Ubuntu Bold 24"
title-color: "#f8fafc"
desktop-image: "background.png"
desktop-color: "#1a1a2e"

# Terminal settings
terminal-font: "Ubuntu Regular 12"
terminal-box: "terminal_box_*.png"

# Menu settings
+ boot_menu {
    left = 20%
    top = 30%
    width = 60%
    height = 50%
    item_font = "Ubuntu Regular 14"
    item_color = "#cbd5e1"
    selected_item_font = "Ubuntu Bold 14"
    selected_item_color = "#ffffff"
    selected_item_pixmap_style = "select_*.png"
    item_height = 30
    item_padding = 8
    item_spacing = 4
    menu_pixmap_style = "menu_*.png"
}

# Progress bar
+ progress_bar {
    id = "__timeout__"
    left = 20%
    top = 85%
    width = 60%
    height = 20
    font = "Ubuntu Regular 12"
    text_color = "#cbd5e1"
    fg_color = "#6366f1"
    bg_color = "#334155"
    border_color = "#6366f1"
    text = "Booting SynOS in %d seconds..."
}

# Logo/header
+ label {
    top = 15%
    left = 50%
    width = 200
    height = 50
    align = "center"
    font = "Ubuntu Bold 18"
    color = "#8b5cf6"
    text = "🧠 Neural Darwinism • 📚 Education • 🛡️ Security"
}
EOF

print_status "success" "GRUB theme created"

# Create desktop icons and shortcuts
print_status "section" "Creating desktop shortcuts..."

mkdir -p config/includes.chroot/etc/skel/Desktop

# SynOS Dashboard shortcut
cat > config/includes.chroot/etc/skel/Desktop/SynOS-Dashboard.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS AI Dashboard
Comment=Access SynOS AI consciousness and educational framework
Exec=xdg-open http://localhost:8080
Icon=applications-science
Terminal=false
Categories=Education;Science;Network;Security;
Keywords=AI;consciousness;cybersecurity;education;
StartupNotify=true
EOF

# Security Tools launcher
cat > config/includes.chroot/etc/skel/Desktop/Security-Tools.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Security Tools
Comment=Launch cybersecurity tools and applications
Exec=mate-terminal -e "synos-status"
Icon=applications-utilities
Terminal=false
Categories=System;Security;Network;
Keywords=security;tools;cybersecurity;penetration;
StartupNotify=true
EOF

# Educational Tutorials launcher
cat > config/includes.chroot/etc/skel/Desktop/Educational-Tutorials.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Educational Tutorials
Comment=Access cybersecurity learning modules
Exec=xdg-open http://localhost:8080
Icon=applications-education
Terminal=false
Categories=Education;Science;
Keywords=education;tutorials;cybersecurity;learning;
StartupNotify=true
EOF

chmod +x config/includes.chroot/etc/skel/Desktop/*.desktop

print_status "success" "Desktop shortcuts created"

# Create system info script for desktop
cat > config/includes.chroot/usr/local/bin/synos-welcome << 'EOF'
#!/bin/bash
# SynOS Welcome Screen

clear
echo ""
echo "🧠 Welcome to SynOS Linux"
echo "Consciousness-Enhanced Cybersecurity Distribution"
echo "=================================================="
echo ""
echo "🎯 Quick Start:"
echo "  • Open AI Dashboard: firefox http://localhost:8080"
echo "  • System Status: synos-status"
echo "  • Security Tools: Applications → Security"
echo "  • Tutorials: Applications → Education"
echo ""
echo "📚 Learning Paths:"
echo "  1. Cybersecurity Fundamentals"
echo "  2. Network Security Analysis"
echo "  3. Web Application Security"
echo "  4. Penetration Testing"
echo ""
echo "🛡️ Security Tools Available:"
echo "  • Nmap (Network Discovery)"
echo "  • Wireshark (Packet Analysis)"
echo "  • Burp Suite (Web Security)"
echo "  • Metasploit (Penetration Testing)"
echo "  • Aircrack-ng (Wireless Security)"
echo ""
echo "🔗 Resources:"
echo "  • Documentation: /opt/synos/share/docs"
echo "  • Logs: /var/log/synos/"
echo "  • Configuration: /etc/synos/synos.conf"
echo ""
echo "Type 'synos-status' for system information"
echo ""
EOF

chmod +x config/includes.chroot/usr/local/bin/synos-welcome

print_status "success" "Welcome screen created"

# Create auto-start configuration
print_status "section" "Creating auto-start configuration..."

mkdir -p config/includes.chroot/etc/skel/.config/autostart

# Auto-start SynOS services checker
cat > config/includes.chroot/etc/skel/.config/autostart/synos-startup.desktop << 'EOF'
[Desktop Entry]
Type=Application
Exec=bash -c "sleep 10 && notify-send 'SynOS Linux' 'AI Consciousness system is starting... Dashboard will be available at http://localhost:8080' -i applications-science"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=SynOS Startup Notification
Comment=Show SynOS startup notification
EOF

print_status "success" "Auto-start configuration created"

echo ""
print_status "header" "======================================================="
print_status "header" "    🎉 SynOS Branding Assets Complete! 🎉"
print_status "header" "======================================================="
echo ""
print_status "success" "Branding assets created:"
print_status "info" "  🎨 SynOS Color Scheme (Neural Network theme)"
print_status "info" "  🖼️ Custom Wallpaper and Graphics"
print_status "info" "  🖥️ MATE Desktop Theme"
print_status "info" "  🚀 Plymouth Boot Animation"
print_status "info" "  📋 GRUB Boot Menu Theme"
print_status "info" "  🔗 Desktop Shortcuts and Launchers"
print_status "info" "  👋 Welcome Screen and Auto-start"
echo ""
print_status "info" "Visual Identity:"
print_status "info" "  • Primary Colors: Purple (#6366f1), Blue (#3b82f6), Cyan (#06b6d4)"
print_status "info" "  • Background: Dark neural network theme (#1a1a2e)"
print_status "info" "  • Typography: Ubuntu font family"
print_status "info" "  • Iconography: Science and AI-focused icons"
echo ""
print_status "info" "Next: Run the test build to verify customizations"
echo ""