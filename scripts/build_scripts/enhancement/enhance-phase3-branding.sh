#!/usr/bin/env bash
################################################################################
# SynOS ULTIMATE ISO Enhancement Script
# Phase 3: Branding & Visual Customization
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/chroot}"
PROJECT_ROOT="/home/diablorain/Syn_OS"

source "$PROJECT_ROOT/scripts/build/enhancement-utils.sh" 2>/dev/null || true

section "Phase 3: Branding & Visual Customization"

################################################################################
# APPLY GRUB THEME
################################################################################

apply_grub_theme() {
    log "Applying SynOS GRUB theme..."

    if [ -d "$PROJECT_ROOT/assets/branding/grub-theme" ]; then
        mkdir -p "$CHROOT_DIR/boot/grub/themes/synos"
        cp -r "$PROJECT_ROOT/assets/branding/grub-theme"/* "$CHROOT_DIR/boot/grub/themes/synos/" 2>/dev/null || true
    fi

    # Configure GRUB to use theme
    cat >> "$CHROOT_DIR/etc/default/grub" <<'EOF'

# SynOS GRUB Theme
GRUB_THEME="/boot/grub/themes/synos/theme.txt"
GRUB_GFXMODE=1920x1080
GRUB_GFXPAYLOAD_LINUX=keep
EOF
}

################################################################################
# INSTALL PLYMOUTH BOOT SPLASH
################################################################################

install_plymouth_splash() {
    log "Installing Plymouth boot splash..."

    chroot "$CHROOT_DIR" apt-get install -y plymouth plymouth-themes

    if [ -d "$PROJECT_ROOT/assets/branding/plymouth-theme" ]; then
        mkdir -p "$CHROOT_DIR/usr/share/plymouth/themes/synos"
        cp -r "$PROJECT_ROOT/assets/branding/plymouth-theme"/* "$CHROOT_DIR/usr/share/plymouth/themes/synos/" 2>/dev/null || true

        chroot "$CHROOT_DIR" plymouth-set-default-theme synos 2>/dev/null || true
    fi

    # Update initramfs to include Plymouth
    chroot "$CHROOT_DIR" update-initramfs -u 2>/dev/null || true
}

################################################################################
# APPLY GTK/QT THEMES
################################################################################

apply_desktop_themes() {
    log "Applying GTK and QT themes..."

    # Install Windows 10 Dark theme and dependencies
    chroot "$CHROOT_DIR" bash -c '
        apt-get install -y \
            gnome-themes-extra \
            gtk2-engines-murrine \
            gtk2-engines-pixbuf \
            qt5-style-plugins \
            2>/dev/null || true
    '

    # Copy custom themes
    if [ -d "$PROJECT_ROOT/assets/branding/gtk-themes" ]; then
        mkdir -p "$CHROOT_DIR/usr/share/themes"
        cp -r "$PROJECT_ROOT/assets/branding/gtk-themes"/* "$CHROOT_DIR/usr/share/themes/" 2>/dev/null || true
    fi

    # ARK-Dark window manager theme (from user's system)
    if [ -d "/usr/share/themes/ARK-Dark" ]; then
        cp -r /usr/share/themes/ARK-Dark "$CHROOT_DIR/usr/share/themes/" 2>/dev/null || true
    fi

    # Windows-10-Dark theme (from user's system)
    if [ -d "/usr/share/themes/Windows-10-Dark" ]; then
        cp -r /usr/share/themes/Windows-10-Dark "$CHROOT_DIR/usr/share/themes/" 2>/dev/null || true
    fi
}

################################################################################
# INSTALL ICON THEMES
################################################################################

install_icon_themes() {
    log "Installing icon themes..."

    chroot "$CHROOT_DIR" apt-get install -y gnome-icon-theme

    # Copy custom icons
    if [ -d "$PROJECT_ROOT/assets/branding/icons" ]; then
        mkdir -p "$CHROOT_DIR/usr/share/icons/synos"
        cp -r "$PROJECT_ROOT/assets/branding/icons"/* "$CHROOT_DIR/usr/share/icons/synos/" 2>/dev/null || true
    fi
}

################################################################################
# SET WALLPAPERS
################################################################################

install_wallpapers() {
    log "Installing wallpapers (nuclear/space imagery)..."

    mkdir -p "$CHROOT_DIR/usr/share/backgrounds/synos"

    # Copy from assets/branding
    if [ -d "$PROJECT_ROOT/assets/branding/backgrounds" ]; then
        cp -r "$PROJECT_ROOT/assets/branding/backgrounds"/* "$CHROOT_DIR/usr/share/backgrounds/synos/" 2>/dev/null || true
    fi

    # Copy user's space.jpg wallpaper
    if [ -f "/usr/share/backgrounds/space.jpg" ]; then
        cp /usr/share/backgrounds/space.jpg "$CHROOT_DIR/usr/share/backgrounds/synos/" 2>/dev/null || true
    fi

    # Set as default
    mkdir -p "$CHROOT_DIR/etc/dconf/db/local.d"
    cat > "$CHROOT_DIR/etc/dconf/db/local.d/01-background" <<'EOF'
[org/mate/desktop/background]
picture-filename='/usr/share/backgrounds/synos/space.jpg'
picture-options='zoom'
EOF
}

################################################################################
# INSTALL FONTS
################################################################################

install_fonts() {
    log "Installing fonts..."

    chroot "$CHROOT_DIR" bash -c '
        apt-get install -y \
            fonts-hack \
            fonts-firacode \
            fonts-jetbrains-mono \
            fonts-noto \
            fonts-noto-color-emoji \
            2>/dev/null || true
    '

    # Copy custom fonts
    if [ -d "$PROJECT_ROOT/assets/branding/fonts" ]; then
        mkdir -p "$CHROOT_DIR/usr/share/fonts/truetype/synos"
        cp -r "$PROJECT_ROOT/assets/branding/fonts"/* "$CHROOT_DIR/usr/share/fonts/truetype/synos/" 2>/dev/null || true
        chroot "$CHROOT_DIR" fc-cache -f 2>/dev/null || true
    fi
}

################################################################################
# CONFIGURE LOGIN SCREEN
################################################################################

configure_login_screen() {
    log "Configuring login screen branding..."

    # LightDM configuration
    cat > "$CHROOT_DIR/etc/lightdm/lightdm-gtk-greeter.conf" <<'EOF'
[greeter]
background=/usr/share/backgrounds/synos/space.jpg
theme-name=Windows-10-Dark
icon-theme-name=synos
font-name=Hack 11
hide-user-image=false
EOF

    # Copy logo for login screen
    if [ -f "$PROJECT_ROOT/assets/branding/logos/synos-logo.png" ]; then
        cp "$PROJECT_ROOT/assets/branding/logos/synos-logo.png" "$CHROOT_DIR/usr/share/pixmaps/synos-logo.png"
    fi
}

################################################################################
# APPLY MATE PANEL CONFIGURATION
################################################################################

apply_mate_panel_config() {
    log "Applying MATE panel configuration (matching user's system)..."

    # Export user's current dconf settings
    mkdir -p "$CHROOT_DIR/etc/dconf/db/local.d"

    cat > "$CHROOT_DIR/etc/dconf/db/local.d/02-mate-panel" <<'EOF'
[org/mate/panel/general]
toplevel-id-list=['top']
object-id-list=['menu', 'show-desktop', 'window-list', 'notification-area', 'clock']

[org/mate/panel/toplevels/top]
orientation='top'
size=24

[org/mate/panel/objects/menu]
object-type='menu-bar'
toplevel-id='top'
position=0

[org/mate/desktop/interface]
gtk-theme='Windows-10-Dark'
icon-theme='gnome'

[org/mate/marco/general]
theme='ARK-Dark'
EOF

    chroot "$CHROOT_DIR" dconf update 2>/dev/null || true
}

################################################################################
# CREATE ABOUT/BRANDING INFO
################################################################################

create_branding_info() {
    log "Creating SynOS branding info..."

    cat > "$CHROOT_DIR/etc/os-release" <<'EOF'
NAME="SynOS"
VERSION="1.0.0 Ultimate"
ID=synos
ID_LIKE=debian
PRETTY_NAME="SynOS 1.0.0 Ultimate - AI-Powered Security OS"
VERSION_ID="1.0.0"
HOME_URL="https://github.com/diablorain/Syn_OS"
SUPPORT_URL="https://github.com/diablorain/Syn_OS/issues"
BUG_REPORT_URL="https://github.com/diablorain/Syn_OS/issues"
LOGO=synos-logo
EOF

    cat > "$CHROOT_DIR/etc/issue" <<'EOF'
SynOS 1.0.0 Ultimate \n \l

Welcome to SynOS - AI-Powered Security Operating System
For help, visit: https://github.com/diablorain/Syn_OS/wiki

EOF

    cat > "$CHROOT_DIR/etc/motd" <<'EOF'

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗               ║
║   ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝               ║
║   ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗               ║
║   ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║               ║
║   ███████║   ██║   ██║ ╚████║╚██████╔╝███████║               ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝               ║
║                                                               ║
║              AI-Powered Security Operating System            ║
║                      Version 1.0.0 Ultimate                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Welcome to SynOS - Your Comprehensive Security Platform

🛡️  500+ Security Tools Pre-installed
🤖 AI-Powered Threat Detection
🔐 Advanced Penetration Testing Suite
📊 Real-time Security Monitoring
🌐 Cloud-Native Architecture

Quick Start:
  • Applications Menu → SynOS Tools (organized by category)
  • Terminal: 'synos-demo' for feature showcase
  • Documentation: /usr/share/doc/synos/

For support: https://github.com/diablorain/Syn_OS

EOF
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo "Phase 3: Branding & Visual Customization"
    echo "========================================"

    apply_grub_theme
    install_plymouth_splash
    apply_desktop_themes
    install_icon_themes
    install_wallpapers
    install_fonts
    configure_login_screen
    apply_mate_panel_config
    create_branding_info

    log "✓ Phase 3 complete!"
    log "Applied: GRUB theme, Plymouth, Desktop themes, Icons, Wallpapers, Login screen"
}

main "$@"
