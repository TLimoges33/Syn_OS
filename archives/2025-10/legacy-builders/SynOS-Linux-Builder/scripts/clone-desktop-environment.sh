#!/bin/bash

# SynOS Desktop Environment Cloning System
# Captures EVERY detail of current desktop and replicates in ISO

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/build"
CLONE_DIR="$BUILD_DIR/desktop-clone"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🖥️ SynOS Desktop Environment Cloning System${NC}"
echo "=============================================="
echo ""

# Create clone directory structure
mkdir -p "$CLONE_DIR"/{configs,applications,themes,panels,shortcuts,fonts,icons}

echo -e "${BLUE}Phase 1: Capturing current desktop environment...${NC}"

# Detect desktop environment
if [[ "$XDG_CURRENT_DESKTOP" == *"MATE"* ]]; then
    DE="MATE"
elif [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]]; then
    DE="GNOME"
elif [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]]; then
    DE="KDE"
else
    DE="UNKNOWN"
fi

echo "🔍 Detected Desktop Environment: $DE"

# Capture MATE desktop configuration
if [[ "$DE" == "MATE" ]]; then
    echo -e "${BLUE}📋 Capturing MATE configuration...${NC}"

    # Export all dconf/gsettings configurations
    dconf dump /org/mate/ > "$CLONE_DIR/configs/mate-dconf.conf"

    # Capture panel configuration
    dconf dump /org/mate/panel/ > "$CLONE_DIR/configs/mate-panel.conf"

    # Capture window manager settings
    dconf dump /org/mate/marco/ > "$CLONE_DIR/configs/mate-marco.conf"

    # Capture desktop background and theme
    dconf dump /org/mate/desktop/ > "$CLONE_DIR/configs/mate-desktop.conf"

    # Capture file manager settings
    dconf dump /org/mate/caja/ > "$CLONE_DIR/configs/mate-caja.conf"

    # Capture terminal settings
    dconf dump /org/mate/terminal/ > "$CLONE_DIR/configs/mate-terminal.conf"

    echo "✅ MATE configuration captured"
fi

# Capture installed applications
echo -e "${BLUE}📦 Capturing installed applications...${NC}"

# Get all installed packages
dpkg --get-selections | grep -v deinstall > "$CLONE_DIR/applications/installed-packages.list"

# Get manually installed packages (non-automatic)
apt-mark showmanual > "$CLONE_DIR/applications/manual-packages.list"

# Get snap packages if any
if command -v snap &> /dev/null; then
    snap list > "$CLONE_DIR/applications/snap-packages.list" 2>/dev/null || echo "No snap packages" > "$CLONE_DIR/applications/snap-packages.list"
fi

# Get flatpak packages if any
if command -v flatpak &> /dev/null; then
    flatpak list > "$CLONE_DIR/applications/flatpak-packages.list" 2>/dev/null || echo "No flatpak packages" > "$CLONE_DIR/applications/flatpak-packages.list"
fi

# Capture application menu structure
if [[ -d "$HOME/.local/share/applications" ]]; then
    cp -r "$HOME/.local/share/applications" "$CLONE_DIR/applications/local-applications"
fi

if [[ -d "/usr/share/applications" ]]; then
    cp -r "/usr/share/applications" "$CLONE_DIR/applications/system-applications"
fi

echo "✅ Applications catalog captured"

# Capture desktop files and shortcuts
echo -e "${BLUE}🔗 Capturing desktop shortcuts and files...${NC}"

if [[ -d "$HOME/Desktop" ]]; then
    cp -r "$HOME/Desktop" "$CLONE_DIR/shortcuts/desktop-files"
fi

# Capture taskbar/panel items
if [[ "$DE" == "MATE" ]]; then
    # Get panel applets and their positions
    gsettings list-recursively org.mate.panel > "$CLONE_DIR/panels/mate-panel-settings.txt"
fi

echo "✅ Shortcuts and panel configuration captured"

# Capture themes and appearance
echo -e "${BLUE}🎨 Capturing themes and appearance...${NC}"

# Copy user themes
if [[ -d "$HOME/.themes" ]]; then
    cp -r "$HOME/.themes" "$CLONE_DIR/themes/user-themes"
fi

if [[ -d "$HOME/.icons" ]]; then
    cp -r "$HOME/.icons" "$CLONE_DIR/themes/user-icons"
fi

# Copy system themes being used
CURRENT_THEME=$(gsettings get org.mate.interface gtk-theme 2>/dev/null | tr -d "'")
CURRENT_ICONS=$(gsettings get org.mate.interface icon-theme 2>/dev/null | tr -d "'")

if [[ -d "/usr/share/themes/$CURRENT_THEME" ]]; then
    cp -r "/usr/share/themes/$CURRENT_THEME" "$CLONE_DIR/themes/current-gtk-theme"
fi

if [[ -d "/usr/share/icons/$CURRENT_ICONS" ]]; then
    cp -r "/usr/share/icons/$CURRENT_ICONS" "$CLONE_DIR/themes/current-icon-theme"
fi

# Capture wallpaper
WALLPAPER=$(gsettings get org.mate.background picture-filename 2>/dev/null | tr -d "'")
if [[ -f "$WALLPAPER" ]]; then
    cp "$WALLPAPER" "$CLONE_DIR/themes/current-wallpaper.jpg"
fi

echo "✅ Themes and appearance captured"

# Capture fonts
echo -e "${BLUE}🔤 Capturing font configuration...${NC}"

if [[ -d "$HOME/.fonts" ]]; then
    cp -r "$HOME/.fonts" "$CLONE_DIR/fonts/user-fonts"
fi

if [[ -f "$HOME/.config/fontconfig/fonts.conf" ]]; then
    cp "$HOME/.config/fontconfig/fonts.conf" "$CLONE_DIR/fonts/font-config.conf"
fi

# Get current font settings
gsettings list-recursively org.mate.interface | grep font > "$CLONE_DIR/fonts/current-fonts.txt" 2>/dev/null || echo "No font settings" > "$CLONE_DIR/fonts/current-fonts.txt"

echo "✅ Font configuration captured"

# Capture user configurations
echo -e "${BLUE}⚙️ Capturing user configurations...${NC}"

# Copy important config directories
CONFIG_DIRS=(
    ".config/autostart"
    ".config/gtk-3.0"
    ".config/dconf"
    ".bashrc"
    ".bash_aliases"
    ".profile"
    ".vimrc"
    ".gitconfig"
)

for config in "${CONFIG_DIRS[@]}"; do
    if [[ -e "$HOME/$config" ]]; then
        mkdir -p "$CLONE_DIR/configs/$(dirname "$config")"
        cp -r "$HOME/$config" "$CLONE_DIR/configs/$config"
    fi
done

echo "✅ User configurations captured"

# Capture system services and startup applications
echo -e "${BLUE}🚀 Capturing startup applications and services...${NC}"

# Get autostart applications
if [[ -d "$HOME/.config/autostart" ]]; then
    ls -la "$HOME/.config/autostart" > "$CLONE_DIR/configs/autostart-apps.txt"
fi

# Get enabled systemd user services
systemctl --user list-unit-files --state=enabled > "$CLONE_DIR/configs/user-services.txt" 2>/dev/null || echo "No user services" > "$CLONE_DIR/configs/user-services.txt"

echo "✅ Startup configuration captured"

# Create restoration script
echo -e "${BLUE}📜 Creating desktop restoration script...${NC}"

cat > "$CLONE_DIR/restore-desktop.sh" << 'EOF'
#!/bin/bash

# SynOS Desktop Environment Restoration Script
# Restores exact desktop environment in the ISO

set -euo pipefail

CLONE_DIR="/opt/synos/desktop-clone"

echo "🖥️ Restoring SynOS Desktop Environment..."

# Restore MATE configuration
if [[ -f "$CLONE_DIR/configs/mate-dconf.conf" ]]; then
    echo "📋 Restoring MATE configuration..."
    dconf load /org/mate/ < "$CLONE_DIR/configs/mate-dconf.conf"

    # Restore individual components
    [[ -f "$CLONE_DIR/configs/mate-panel.conf" ]] && dconf load /org/mate/panel/ < "$CLONE_DIR/configs/mate-panel.conf"
    [[ -f "$CLONE_DIR/configs/mate-marco.conf" ]] && dconf load /org/mate/marco/ < "$CLONE_DIR/configs/mate-marco.conf"
    [[ -f "$CLONE_DIR/configs/mate-desktop.conf" ]] && dconf load /org/mate/desktop/ < "$CLONE_DIR/configs/mate-desktop.conf"
    [[ -f "$CLONE_DIR/configs/mate-caja.conf" ]] && dconf load /org/mate/caja/ < "$CLONE_DIR/configs/mate-caja.conf"
    [[ -f "$CLONE_DIR/configs/mate-terminal.conf" ]] && dconf load /org/mate/terminal/ < "$CLONE_DIR/configs/mate-terminal.conf"
fi

# Restore themes
echo "🎨 Restoring themes and appearance..."
if [[ -d "$CLONE_DIR/themes/user-themes" ]]; then
    cp -r "$CLONE_DIR/themes/user-themes" "$HOME/.themes"
fi

if [[ -d "$CLONE_DIR/themes/user-icons" ]]; then
    cp -r "$CLONE_DIR/themes/user-icons" "$HOME/.icons"
fi

# Restore wallpaper
if [[ -f "$CLONE_DIR/themes/current-wallpaper.jpg" ]]; then
    cp "$CLONE_DIR/themes/current-wallpaper.jpg" "/usr/share/pixmaps/synos-wallpaper.jpg"
    gsettings set org.mate.background picture-filename "/usr/share/pixmaps/synos-wallpaper.jpg"
fi

# Restore fonts
echo "🔤 Restoring fonts..."
if [[ -d "$CLONE_DIR/fonts/user-fonts" ]]; then
    cp -r "$CLONE_DIR/fonts/user-fonts" "$HOME/.fonts"
    fc-cache -f
fi

# Restore user configurations
echo "⚙️ Restoring user configurations..."
if [[ -d "$CLONE_DIR/configs" ]]; then
    # Restore bash configurations
    [[ -f "$CLONE_DIR/configs/.bashrc" ]] && cp "$CLONE_DIR/configs/.bashrc" "$HOME/.bashrc"
    [[ -f "$CLONE_DIR/configs/.bash_aliases" ]] && cp "$CLONE_DIR/configs/.bash_aliases" "$HOME/.bash_aliases"
    [[ -f "$CLONE_DIR/configs/.profile" ]] && cp "$CLONE_DIR/configs/.profile" "$HOME/.profile"

    # Restore application configs
    if [[ -d "$CLONE_DIR/configs/.config" ]]; then
        cp -r "$CLONE_DIR/configs/.config"/* "$HOME/.config/" 2>/dev/null || true
    fi
fi

# Restore desktop shortcuts
echo "🔗 Restoring desktop shortcuts..."
if [[ -d "$CLONE_DIR/shortcuts/desktop-files" ]]; then
    cp -r "$CLONE_DIR/shortcuts/desktop-files"/* "$HOME/Desktop/" 2>/dev/null || true
fi

# Restart panel to apply changes
echo "🔄 Restarting desktop components..."
mate-panel --replace &
sleep 2

echo "✅ Desktop environment restoration complete!"
echo "🎯 Your exact desktop environment has been restored in SynOS!"
EOF

chmod +x "$CLONE_DIR/restore-desktop.sh"

# Create package installation script
cat > "$CLONE_DIR/install-packages.sh" << 'EOF'
#!/bin/bash

# Install all packages from cloned environment

echo "📦 Installing cloned applications..."

# Install manually selected packages first
if [[ -f "/opt/synos/desktop-clone/applications/manual-packages.list" ]]; then
    echo "Installing manually selected packages..."
    while read -r package; do
        apt-get install -y "$package" 2>/dev/null || echo "Could not install: $package"
    done < "/opt/synos/desktop-clone/applications/manual-packages.list"
fi

# Install snap packages
if [[ -f "/opt/synos/desktop-clone/applications/snap-packages.list" ]] && command -v snap &> /dev/null; then
    echo "Installing snap packages..."
    grep -v "^Name" "/opt/synos/desktop-clone/applications/snap-packages.list" | while read -r line; do
        package=$(echo "$line" | awk '{print $1}')
        [[ "$package" != "core"* ]] && snap install "$package" 2>/dev/null || true
    done
fi

echo "✅ Package installation complete!"
EOF

chmod +x "$CLONE_DIR/install-packages.sh"

echo "✅ Desktop restoration scripts created"

echo ""
echo -e "${GREEN}🎉 Desktop Environment Cloning Complete!${NC}"
echo ""
echo "📊 Captured Components:"
echo "   • Desktop Environment: $DE"
echo "   • Packages: $(wc -l < "$CLONE_DIR/applications/installed-packages.list") total"
echo "   • Manual Packages: $(wc -l < "$CLONE_DIR/applications/manual-packages.list") user-selected"
echo "   • Configuration files: $(find "$CLONE_DIR/configs" -type f | wc -l) files"
echo "   • Themes: $(find "$CLONE_DIR/themes" -type d | wc -l) directories"
echo "   • Fonts: $(find "$CLONE_DIR/fonts" -type f 2>/dev/null | wc -l || echo "0") files"
echo ""
echo "📁 Clone Location: $CLONE_DIR"
echo ""
echo "✅ Ready for integration into SynOS Red Team ISO!"