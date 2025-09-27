#!/bin/bash
# SynOS Boot Experience Configuration Script
# Integrates GRUB theme and Plymouth splash into ISO

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration paths
ISO_ROOT="${PROJECT_ROOT}/Final_SynOS-1.0_ISO"
BOOT_EXP_DIR="$ISO_ROOT/boot_experience"
FILESYSTEM_ROOT="$ISO_ROOT/filesystem_root"
GRUB_DIR="$ISO_ROOT/boot/grub"
ISOLINUX_DIR="$ISO_ROOT/isolinux"

print_status() {
    echo -e "${GREEN}[BOOT]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[BOOT]${NC} $1"
}

print_error() {
    echo -e "${RED}[BOOT]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "██████████████████████████████████████████████████████████████"
    echo "█                                                            █"
    echo "█           SynOS v1.0 Boot Experience Configuration         █"
    echo "█          Professional Cybersecurity Boot System           █"
    echo "█                                                            █"
    echo "██████████████████████████████████████████████████████████████"
    echo -e "${NC}"
}

print_header
echo "Configuring SynOS boot experience..."
echo "ISO Root: $ISO_ROOT"
echo "Boot Experience: $BOOT_EXP_DIR"
echo "========================================"

# Step 1: Configure GRUB theme
print_status "Configuring GRUB theme..."

# Create GRUB theme directory
mkdir -p "$GRUB_DIR/themes/synos"

# Copy GRUB configuration
cp "$BOOT_EXP_DIR/grub.cfg" "$GRUB_DIR/grub.cfg"
cp "$BOOT_EXP_DIR/grub_theme.txt" "$GRUB_DIR/themes/synos/theme.txt"

# Update main GRUB configuration with SynOS settings
cat > "$GRUB_DIR/grub.cfg" << 'EOF'
# SynOS v1.0 GRUB Configuration
# Professional cybersecurity boot experience

if loadfont /boot/grub/font.pf2 ; then
  set gfxmode=auto
  insmod efi_gop
  insmod efi_uga
  insmod gfxterm
  terminal_output gfxterm
fi

set menu_color_normal=white/black
set menu_color_highlight=red/black

# Load SynOS theme
set theme=/boot/grub/themes/synos/theme.txt

# Default settings
set default=0
set timeout=10
set timeout_style=menu

# Boot entries
menuentry "SynOS v1.0 - Consciousness Mode (Recommended)" --class synos {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live components quiet splash consciousness=enabled hostname=synos
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Standard Live Mode" --class synos {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live components quiet splash hostname=synos
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Digital Forensics Mode" --class synos {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live components noswap noautomount hostname=synos
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Persistence Mode" --class synos {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live components quiet persistence hostname=synos
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Encrypted Persistence" --class synos {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live persistent=cryptsetup persistence-encryption=luks hostname=synos quiet persistence components
    initrd /live/initrd.img
}

submenu "Advanced Security Options" {
    menuentry "RAM Mode (No Disk Access)" --class synos {
        set gfxpayload=keep
        linux /live/vmlinuz boot=live components quiet splash toram hostname=synos
        initrd /live/initrd.img
    }
    
    menuentry "Terminal Mode (Text Interface)" --class synos {
        set gfxpayload=keep
        linux /live/vmlinuz boot=live hostname=synos quiet systemd.unit=multi-user.target components
        initrd /live/initrd.img
    }
    
    menuentry "Safe Mode (Minimal Drivers)" --class synos {
        set gfxpayload=keep
        linux /live/vmlinuz boot=live hostname=synos nomodeset components
        initrd /live/initrd.img
    }
}

submenu "System Tools" {
    menuentry "Memory Test" --class memtest {
        linux16 /live/memtest
    }
    
    menuentry "Boot from Hard Drive" --class harddrive {
        set root=(hd0)
        chainloader +1
    }
}
EOF

# Create GRUB theme file with consciousness elements
cat > "$GRUB_DIR/themes/synos/theme.txt" << 'EOF'
# SynOS GRUB Theme - Consciousness Integration
desktop-image: "background.png"
desktop-color: "#000000"
title-text: "Syn_OS v1.0 - Next-Gen Cybersecurity Operating System"
title-font: "DejaVu Sans Bold 18"
title-color: "#FF0000"
terminal-font: "DejaVu Sans Mono 12"

+ boot_menu {
    left = 20%
    top = 30%
    width = 60%
    height = 45%
    item_font = "DejaVu Sans 14"
    item_color = "#FFFFFF"
    selected_item_color = "#FF0000"
    selected_item_font = "DejaVu Sans Bold 14"
    item_height = 24
    item_padding = 4
    item_spacing = 2
    icon_width = 20
    icon_height = 20
    item_icon_space = 4
}

+ progress_bar {
    id = "__timeout__"
    left = 20%
    top = 80%
    width = 60%
    height = 16
    fg_color = "#FF0000"
    bg_color = "#333333"
    border_color = "#800000"
    text_color = "#FFFFFF"
    font = "DejaVu Sans 10"
    text = "Consciousness initializing in %d seconds..."
}

+ label {
    top = 85%
    left = 20%
    width = 60%
    height = 10%
    text = "Consciousness-Integrated Security Platform"
    font = "DejaVu Sans 11"
    color = "#CCCCCC"
    align = "center"
}
EOF

print_status "GRUB theme configured"

# Step 2: Configure ISOLINUX for legacy boot
print_status "Configuring ISOLINUX for legacy boot..."

# Update isolinux.cfg with SynOS branding
cat > "$ISOLINUX_DIR/isolinux.cfg" << 'EOF'
UI vesamenu.c32
TIMEOUT 100
ONTIMEOUT live

MENU TITLE Syn_OS v1.0 - Next-Gen Cybersecurity Operating System
MENU BACKGROUND splash.png

# Color scheme (black background, red accents)
MENU COLOR border       30;44   #40ffffff #a0000000 std
MENU COLOR title        1;36;44 #ff0000ff #a0000000 std
MENU COLOR sel          7;37;40 #e0ffffff #20ff0000 all
MENU COLOR unsel        37;44   #50ffffff #a0000000 std
MENU COLOR help         37;40   #c0ffffff #a0000000 std
MENU COLOR timeout_msg  37;40   #80ffffff #00000000 std
MENU COLOR timeout      1;37;40 #c0ffffff #00000000 std
MENU COLOR msg07        37;40   #90ffffff #a0000000 std
MENU COLOR tabmsg       31;40   #30ffffff #00000000 std

LABEL live
  MENU LABEL ^SynOS v1.0 - Consciousness Mode (Recommended)
  MENU DEFAULT
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd.img boot=live components quiet splash consciousness=enabled hostname=synos

LABEL live-standard
  MENU LABEL SynOS v1.0 - ^Standard Live Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd.img boot=live components quiet splash hostname=synos

LABEL live-forensic
  MENU LABEL SynOS v1.0 - ^Digital Forensics Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd.img boot=live components noswap noautomount hostname=synos

LABEL live-persistence
  MENU LABEL SynOS v1.0 - ^Persistence Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd.img boot=live components quiet persistence hostname=synos

LABEL live-ram
  MENU LABEL SynOS v1.0 - ^RAM Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd.img boot=live components quiet splash toram hostname=synos

LABEL live-safe
  MENU LABEL SynOS v1.0 - Safe ^Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd.img boot=live hostname=synos nomodeset components

LABEL memtest
  MENU LABEL ^Memory Test
  KERNEL memtest

MENU SEPARATOR

MENU BEGIN advanced
  MENU TITLE Advanced Options
  
  LABEL back
    MENU LABEL ^Back to Main Menu
    MENU EXIT
    
  LABEL emergency
    MENU LABEL ^Emergency Shell
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live hostname=synos emergency components
    
MENU END

MENU SEPARATOR

LABEL local
  MENU LABEL Boot from ^Hard Drive
  LOCALBOOT 0x80
  
TEXT HELP
Welcome to Syn_OS v1.0 - Next-Gen Cybersecurity Operating System

Features:
- Consciousness-Integrated Technology
- Post-Quantum Cryptography  
- GPU-Accelerated Security
- Advanced Penetration Testing Tools
- Real-time Threat Monitoring
- Educational CTF Platform

For help: https://syn-os.ai/docs
ENDTEXT
EOF

# Update menu.cfg for consistency
cp "$ISOLINUX_DIR/isolinux.cfg" "$ISOLINUX_DIR/menu.cfg"

print_status "ISOLINUX configured"

# Step 3: Configure Plymouth boot splash
print_status "Configuring Plymouth boot splash..."

# Create Plymouth theme directory in filesystem
mkdir -p "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos"

# Copy Plymouth configuration
cp "$BOOT_EXP_DIR/synos.plymouth" "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos/"
cp "$BOOT_EXP_DIR/synos_plymouth.script" "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos/synos.script"

# Create Plymouth configuration script for chroot installation
cat > "$FILESYSTEM_ROOT/tmp/configure_plymouth.sh" << 'PLYMOUTH_EOF'
#!/bin/bash
# Configure Plymouth in chroot environment

# Set SynOS as default Plymouth theme
if command -v plymouth-set-default-theme &> /dev/null; then
    plymouth-set-default-theme synos
    update-initramfs -u
fi

# Update alternatives
if command -v update-alternatives &> /dev/null; then
    update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/synos/synos.plymouth 100
fi

# Configure Plymouth settings
mkdir -p /etc/plymouth
cat > /etc/plymouth/plymouthd.conf << 'EOF'
[Daemon]
Theme=synos
ShowDelay=0
DeviceTimeout=5
EOF

echo "Plymouth configured for SynOS"
PLYMOUTH_EOF

chmod +x "$FILESYSTEM_ROOT/tmp/configure_plymouth.sh"

print_status "Plymouth configuration prepared"

# Step 4: Create boot asset placeholders
print_status "Creating boot asset placeholders..."

# Create placeholder images with specifications
mkdir -p "$GRUB_DIR/themes/synos/assets"
mkdir -p "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos/assets"

# GRUB background placeholder
cat > "$GRUB_DIR/themes/synos/background_spec.txt" << 'EOF'
# GRUB Background Specification
# File: background.png
# Dimensions: 1920x1080 (with 1280x720, 1024x768 variants)
# Description: Solid black background with subtle red neural network pattern
# Elements:
# - Pure black (#000000) base
# - Faint red (#800000) circuit traces in corners (10% opacity)
# - Consciousness nodes as small red dots
# - Professional, non-distracting design
# - SynOS logo watermark in bottom right (5% opacity)
EOF

# Plymouth logo placeholder
cat > "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos/logo_spec.txt" << 'EOF'
# Plymouth Logo Specification
# File: synos_logo.png
# Dimensions: 256x256, 128x128, 64x64 variants
# Description: Main SynOS logo for boot splash
# Elements:
# - "SYN_OS" text in cybersecurity font (Courier New Bold)
# - Neural network brain symbol integrated
# - Red (#FF0000) on transparent background
# - Suitable for pulsing/breathing animation
# - Professional corporate appearance
EOF

# Create simple text-based placeholders for testing
echo "SynOS v1.0 Boot Background Placeholder" > "$GRUB_DIR/themes/synos/background.png"
echo "SynOS Logo Placeholder" > "$FILESYSTEM_ROOT/usr/share/plymouth/themes/synos/synos_logo.png"

print_status "Boot asset placeholders created"

# Step 5: Configure systemd for Plymouth
print_status "Configuring systemd for Plymouth integration..."

# Create systemd service for Plymouth
cat > "$FILESYSTEM_ROOT/etc/systemd/system/plymouth-synos.service" << 'EOF'
[Unit]
Description=SynOS Plymouth Boot Splash
After=systemd-vconsole-setup.service
Before=display-manager.service

[Service]
Type=forking
ExecStart=/usr/sbin/plymouthd --mode=boot --attach-to-session
ExecStartPost=/usr/bin/plymouth show-splash
ExecStop=/usr/bin/plymouth quit
KillMode=none
TimeoutSec=0

[Install]
WantedBy=sysinit.target
EOF

# Enable Plymouth service
mkdir -p "$FILESYSTEM_ROOT/etc/systemd/system/sysinit.target.wants"
ln -sf "/etc/systemd/system/plymouth-synos.service" "$FILESYSTEM_ROOT/etc/systemd/system/sysinit.target.wants/"

print_status "Plymouth systemd integration configured"

# Step 6: Update kernel command line for splash
print_status "Updating kernel command line for splash..."

# Update all boot configurations to include splash parameters
sed -i 's/quiet splash/quiet splash plymouth.theme=synos/g' "$GRUB_DIR/grub.cfg"
sed -i 's/quiet splash/quiet splash plymouth.theme=synos/g' "$ISOLINUX_DIR/isolinux.cfg"
sed -i 's/quiet splash/quiet splash plymouth.theme=synos/g' "$ISOLINUX_DIR/menu.cfg"

print_status "Kernel command line updated"

# Step 7: Create boot documentation
print_status "Creating boot documentation..."

cat > "$ISO_ROOT/boot_experience/BOOT_CONFIGURATION_GUIDE.md" << 'EOF'
# SynOS v1.0 Boot Configuration Guide

## Overview
This guide describes the complete boot experience configuration for SynOS v1.0, including GRUB theme, ISOLINUX branding, and Plymouth splash screen.

## Boot Options Configured

### Primary Boot Modes
1. **Consciousness Mode (Default)**: Full AI integration enabled
2. **Standard Live Mode**: Traditional live boot experience
3. **Digital Forensics Mode**: No swap/automount for forensic analysis
4. **Persistence Mode**: Save changes across reboots
5. **Encrypted Persistence**: Secure encrypted storage
6. **RAM Mode**: Run entirely from memory

### Advanced Options
- Safe Mode (minimal drivers)
- Terminal Mode (text interface)
- Emergency Shell
- Memory Test
- Boot from Hard Drive

## Theme Configuration

### GRUB Theme (UEFI Boot)
- **Theme**: /boot/grub/themes/synos/theme.txt
- **Background**: Black with red neural network pattern
- **Colors**: Black background, red accents, white text
- **Menu**: Professional cybersecurity styling
- **Timeout**: 10 seconds with consciousness initialization message

### ISOLINUX Theme (Legacy Boot)
- **Configuration**: isolinux.cfg with SynOS branding
- **Colors**: Black/red cybersecurity color scheme
- **Menu**: Consistent with GRUB theme
- **Help Text**: SynOS features and documentation links

### Plymouth Splash Screen
- **Theme**: synos (consciousness initialization)
- **Animation**: Neural network activation sequence
- **Progress**: Security component loading visualization
- **Phases**: Hardware → Kernel → Networks → Security → Context → Ready
- **Messages**: Real-time boot status with consciousness theme

## Configuration Files

### GRUB Files
- `/boot/grub/grub.cfg` - Main GRUB configuration
- `/boot/grub/themes/synos/theme.txt` - Theme definition
- `/boot/grub/themes/synos/background.png` - Background image
- `/boot/grub/themes/synos/assets/` - Theme assets

### ISOLINUX Files
- `/isolinux/isolinux.cfg` - Legacy boot configuration
- `/isolinux/menu.cfg` - Menu configuration
- `/isolinux/splash.png` - Boot splash image

### Plymouth Files
- `/usr/share/plymouth/themes/synos/synos.plymouth` - Theme definition
- `/usr/share/plymouth/themes/synos/synos.script` - Animation script
- `/usr/share/plymouth/themes/synos/synos_logo.png` - Logo image
- `/etc/plymouth/plymouthd.conf` - Plymouth configuration

## Customization

### Changing Boot Options
Edit the respective configuration files to modify:
- Boot timeout values
- Default boot option
- Kernel parameters
- Menu text and descriptions

### Theme Modifications
Update theme files to change:
- Colors and styling
- Background images
- Animation sequences
- Menu layouts

### Adding Boot Modes
Add new menuentry sections to:
- `/boot/grub/grub.cfg` for UEFI
- `/isolinux/isolinux.cfg` for Legacy
- Ensure consistent naming and parameters

## Testing
1. Test UEFI boot in virtual machine
2. Test Legacy boot compatibility
3. Verify Plymouth animation
4. Check all boot modes functionality
5. Validate timeout and default selection

## Troubleshooting

### GRUB Issues
- Check theme file syntax
- Verify asset file paths
- Test with fallback theme

### ISOLINUX Issues
- Validate configuration syntax
- Check image file formats
- Test menu navigation

### Plymouth Issues
- Verify script syntax
- Check service enablement
- Test initramfs integration

## Professional Considerations
- Corporate-appropriate styling
- Quick boot times
- Clear menu options
- Accessibility compliance
- Consistent branding across boot methods
EOF

print_status "Boot documentation created"

# Final summary
echo ""
echo -e "${GREEN}✓ SynOS Boot Experience Configuration Complete!${NC}"
echo ""
echo "Configured Components:"
echo "• GRUB theme with consciousness branding"
echo "• ISOLINUX legacy boot with cybersecurity styling"
echo "• Plymouth boot splash with neural network animation"
echo "• Systemd integration for smooth boot experience"
echo "• Professional boot options and menus"
echo "• Complete documentation and specifications"
echo ""
echo "Boot Options Available:"
echo "• Consciousness Mode (default)"
echo "• Standard Live Mode"
echo "• Digital Forensics Mode"
echo "• Persistence Mode"
echo "• Encrypted Persistence"
echo "• RAM Mode"
echo "• Advanced Security Options"
echo "• System Tools"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Create required boot graphics assets"
echo "2. Test boot experience in virtual environment"
echo "3. Validate UEFI and Legacy compatibility"
echo "4. Build final ISO with integrated boot system"
echo ""
echo -e "${YELLOW}Ready for professional deployment!${NC}"

exit 0
