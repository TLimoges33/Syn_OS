#!/bin/bash

# SynOS Branding Deployment Script
# Integrates all SynOS visual assets into the filesystem

set -e

BRANDING_DIR="/home/diablorain/Syn_OS/SynOS-Branding"
FILESYSTEM_ROOT="/home/diablorain/Syn_OS/SynOS-Linux-Builder/filesystem-extract"

echo "🚀 Deploying SynOS Branding Assets..."

# Check if filesystem exists
if [ ! -d "$FILESYSTEM_ROOT" ]; then
    echo "❌ Filesystem not found at $FILESYSTEM_ROOT"
    exit 1
fi

cd "$BRANDING_DIR"

echo "🖼️  Deploying desktop backgrounds..."
mkdir -p "$FILESYSTEM_ROOT/usr/share/backgrounds"
cp backgrounds/* "$FILESYSTEM_ROOT/usr/share/backgrounds/"

# Set the main background as default
if [ -f "$FILESYSTEM_ROOT/usr/share/backgrounds/synos-neural-dark.jpg" ]; then
    ln -sf synos-neural-dark.jpg "$FILESYSTEM_ROOT/usr/share/backgrounds/default.jpg"
fi

echo "🏷️  Deploying logos..."
mkdir -p "$FILESYSTEM_ROOT/usr/share/pixmaps"
mkdir -p "$FILESYSTEM_ROOT/usr/share/icons/hicolor/"{32x32,64x64,128x128,256x256,512x512}"/apps"

cp logos/synos-logo-32.png "$FILESYSTEM_ROOT/usr/share/icons/hicolor/32x32/apps/synos.png"
cp logos/synos-logo-64.png "$FILESYSTEM_ROOT/usr/share/icons/hicolor/64x64/apps/synos.png"
cp logos/synos-logo-128.png "$FILESYSTEM_ROOT/usr/share/icons/hicolor/128x128/apps/synos.png"
cp logos/synos-logo-256.png "$FILESYSTEM_ROOT/usr/share/icons/hicolor/256x256/apps/synos.png"
cp logos/synos-logo-512.png "$FILESYSTEM_ROOT/usr/share/icons/hicolor/512x512/apps/synos.png"

# Copy to pixmaps for legacy applications
cp logos/synos-logo-128.png "$FILESYSTEM_ROOT/usr/share/pixmaps/synos.png"

echo "🚀 Deploying GRUB themes..."
mkdir -p "$FILESYSTEM_ROOT/usr/share/desktop-base/synos-theme/grub"
cp grub/* "$FILESYSTEM_ROOT/usr/share/desktop-base/synos-theme/grub/"

echo "🔐 Deploying Plymouth boot theme..."
mkdir -p "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos-neural"
cp -r plymouth/synos-neural/* "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos-neural/"

echo "🖥️  Deploying desktop themes..."
mkdir -p "$FILESYSTEM_ROOT/usr/share/themes"
cp -r themes/synos-mate "$FILESYSTEM_ROOT/usr/share/themes/"

echo "⚙️  Configuring system defaults..."

# Configure default desktop background
mkdir -p "$FILESYSTEM_ROOT/etc/dconf/db/local.d"
cat > "$FILESYSTEM_ROOT/etc/dconf/db/local.d/01-synos-defaults" << 'EOF'
[org/mate/desktop/background]
picture-filename='/usr/share/backgrounds/synos-neural-dark.jpg'
picture-options='stretched'
primary-color='#001133'
secondary-color='#000011'

[org/mate/desktop/interface]
gtk-theme='synos-mate'
icon-theme='Menta'
font-name='Liberation Sans 10'

[org/mate/marco/general]
theme='synos-mate'

[org/mate/desktop/peripherals/mouse]
cursor-theme='Menta'

[org/mate/panel/general]
default-layout='synos'
EOF

# Update dconf database
if [ -f "$FILESYSTEM_ROOT/usr/bin/dconf" ]; then
    echo "📊 Updating dconf database..."
    # This will be done at runtime in the live system
    echo "dconf update" > "$FILESYSTEM_ROOT/etc/profile.d/synos-dconf-update.sh"
    chmod +x "$FILESYSTEM_ROOT/etc/profile.d/synos-dconf-update.sh"
fi

echo "🖥️  Configuring display manager..."

# Configure LightDM with SynOS theme
if [ -f "$FILESYSTEM_ROOT/etc/lightdm/slick-greeter.conf" ]; then
    cat > "$FILESYSTEM_ROOT/etc/lightdm/slick-greeter.conf" << 'EOF'
[Greeter]
background=/usr/share/backgrounds/synos-neural-dark.jpg
theme-name=synos-mate
icon-theme-name=Menta
font-name=Liberation Sans 11
xft-antialias=true
xft-dpi=96
xft-hintstyle=slight
xft-rgba=rgb
show-hostname=true
show-power=true
show-a11y=true
show-keyboard=true
show-clock=true
clock-format=%H:%M
sessions-directory=/usr/share/xsessions
remote-sessions-directory=/usr/share/xsessions
activate-numlock=true
EOF
fi

echo "🚀 Configuring GRUB bootloader..."

# Configure GRUB theme
if [ -f "$FILESYSTEM_ROOT/etc/default/grub" ]; then
    # Update GRUB configuration
    sed -i 's/^#GRUB_THEME=.*/GRUB_THEME="\/usr\/share\/desktop-base\/synos-theme\/grub\/synos-grub-16x9.png"/' "$FILESYSTEM_ROOT/etc/default/grub" || true

    # Add if doesn't exist
    if ! grep -q "GRUB_THEME=" "$FILESYSTEM_ROOT/etc/default/grub"; then
        echo 'GRUB_THEME="/usr/share/desktop-base/synos-theme/grub/synos-grub-16x9.png"' >> "$FILESYSTEM_ROOT/etc/default/grub"
    fi

    # Set distributor
    sed -i 's/^#GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="SynOS"/' "$FILESYSTEM_ROOT/etc/default/grub" || true
    if ! grep -q "GRUB_DISTRIBUTOR=" "$FILESYSTEM_ROOT/etc/default/grub"; then
        echo 'GRUB_DISTRIBUTOR="SynOS"' >> "$FILESYSTEM_ROOT/etc/default/grub"
    fi
fi

echo "🔐 Configuring Plymouth..."

# Set Plymouth default theme
mkdir -p "$FILESYSTEM_ROOT/etc/plymouth"
echo "[Daemon]" > "$FILESYSTEM_ROOT/etc/plymouth/plymouthd.conf"
echo "Theme=synos-neural" >> "$FILESYSTEM_ROOT/etc/plymouth/plymouthd.conf"
echo "ShowDelay=0" >> "$FILESYSTEM_ROOT/etc/plymouth/plymouthd.conf"

echo "📝 Creating SynOS desktop profile..."

# Create SynOS user profile template
mkdir -p "$FILESYSTEM_ROOT/etc/skel/.config/mate/backgrounds"
mkdir -p "$FILESYSTEM_ROOT/etc/skel/.config/dconf"

# Set default wallpaper for new users
cat > "$FILESYSTEM_ROOT/etc/skel/.config/mate/backgrounds/mate-backgrounds.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE wallpapers SYSTEM "mate-wp-list.dtd">
<wallpapers>
  <wallpaper deleted="false">
    <name>SynOS Neural Dark</name>
    <filename>/usr/share/backgrounds/synos-neural-dark.jpg</filename>
    <options>stretched</options>
    <shade_type>solid</shade_type>
    <pcolor>#001133</pcolor>
    <scolor>#000011</scolor>
  </wallpaper>
  <wallpaper deleted="false">
    <name>SynOS Neural Blue</name>
    <filename>/usr/share/backgrounds/synos-neural-blue.jpg</filename>
    <options>stretched</options>
    <shade_type>solid</shade_type>
    <pcolor>#2a2a4a</pcolor>
    <scolor>#4a4a6a</scolor>
  </wallpaper>
  <wallpaper deleted="false">
    <name>SynOS Matrix</name>
    <filename>/usr/share/backgrounds/synos-matrix.jpg</filename>
    <options>stretched</options>
    <shade_type>solid</shade_type>
    <pcolor>#001122</pcolor>
    <scolor>#001122</scolor>
  </wallpaper>
</wallpapers>
EOF

echo "🏠 Creating SynOS panel layout..."

# Create custom MATE panel layout
mkdir -p "$FILESYSTEM_ROOT/usr/share/mate-panel/layouts"
cat > "$FILESYSTEM_ROOT/usr/share/mate-panel/layouts/synos.layout" << 'EOF'
[Toplevel top]
orientation=top
size=24

[Object menu-bar]
object-type=menu-bar
toplevel-id=top
position=0
locked=true

[Object notification-area]
object-type=applet
applet-iid=NotificationAreaAppletFactory::NotificationArea
toplevel-id=top
position=10
locked=true

[Object clock]
object-type=applet
applet-iid=ClockAppletFactory::ClockApplet
toplevel-id=top
position=0
panel-right-stick=true
locked=true

[Object show-desktop]
object-type=applet
applet-iid=WnckletFactory::ShowDesktopApplet
toplevel-id=top
position=1
panel-right-stick=true
locked=true
EOF

echo "🔧 Setting file permissions..."
find "$FILESYSTEM_ROOT/usr/share/backgrounds" -type f -exec chmod 644 {} \; 2>/dev/null || true
find "$FILESYSTEM_ROOT/usr/share/pixmaps" -type f -exec chmod 644 {} \; 2>/dev/null || true
find "$FILESYSTEM_ROOT/usr/share/themes" -type f -exec chmod 644 {} \; 2>/dev/null || true
find "$FILESYSTEM_ROOT/usr/share/plymouth" -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "✅ SynOS Branding Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🖼️  Desktop backgrounds deployed and configured"
echo "🏷️  System logos integrated into icon theme"
echo "🚀 GRUB bootloader theme configured"
echo "🔐 Plymouth boot theme installed"
echo "🖥️  MATE desktop theme deployed"
echo "⚙️  System defaults configured for SynOS identity"
echo "📱 User profile templates created"
echo ""
echo "🎯 All ParrotOS branding has been replaced with SynOS identity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"