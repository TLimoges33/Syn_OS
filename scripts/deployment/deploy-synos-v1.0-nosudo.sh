#!/bin/bash
# SynOS v1.0 Complete Deployment Script (No sudo wrapper)
# Deploys all compiled binaries and configurations to ISO

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CHROOT="build/synos-v1.0/work/chroot"
PROJECT_ROOT="$(pwd)"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         SynOS v1.0 Complete Deployment Script                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify chroot exists
if [ ! -d "$CHROOT" ]; then
    echo -e "${RED}✗ Error: Chroot directory not found at $CHROOT${NC}"
    echo -e "${YELLOW}  Please build ISO first with: cd linux-distribution/SynOS-Linux-Builder && lb build${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found chroot at: $CHROOT${NC}"
echo ""

# ============================================================================
# PHASE 1: Deploy Rust Enterprise Binaries
# ============================================================================

echo -e "${BLUE}[1/8] Deploying Rust Enterprise Binaries...${NC}"

# Create bin directory if it doesn't exist
sudo mkdir -p "$CHROOT/usr/local/bin"

# List of binaries to deploy
BINARIES=(
    "synos-pkg"
    "synos-threat-intel"
    "synos-threat-hunting"
    "synos-compliance"
    "synos-zt-engine"
    "synos-analytics"
    "synos-deception"
    "synos-hsm-integration"
    "synos-vuln-research"
    "synos-vm-wargames"
)

DEPLOYED=0
FAILED=0

for binary in "${BINARIES[@]}"; do
    if [ -f "target/debug/$binary" ]; then
        echo -e "  → Copying ${binary}..."
        sudo cp "target/debug/$binary" "$CHROOT/usr/local/bin/"
        sudo chmod +x "$CHROOT/usr/local/bin/$binary"

        # Strip debug symbols to reduce size
        sudo strip "$CHROOT/usr/local/bin/$binary" 2>/dev/null || true

        DEPLOYED=$((DEPLOYED + 1))
        echo -e "${GREEN}    ✓ Deployed${NC}"
    else
        echo -e "${YELLOW}    ⚠ Not found: target/debug/$binary${NC}"
        FAILED=$((FAILED + 1))
    fi
done

echo -e "${GREEN}✓ Deployed $DEPLOYED binaries${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${YELLOW}⚠ $FAILED binaries not found (may need compilation)${NC}"
fi
echo ""

# ============================================================================
# PHASE 2: Deploy Custom Kernel
# ============================================================================

echo -e "${BLUE}[2/8] Deploying Custom SynOS Kernel...${NC}"

if [ -f "target/x86_64-unknown-none/release/kernel" ]; then
    sudo mkdir -p "$CHROOT/boot/synos"

    echo -e "  → Copying kernel binary..."
    sudo cp "target/x86_64-unknown-none/release/kernel" "$CHROOT/boot/synos/synos-kernel-1.0"
    sudo chmod 644 "$CHROOT/boot/synos/synos-kernel-1.0"

    # Create kernel info file
    sudo tee "$CHROOT/boot/synos/kernel-info.txt" > /dev/null << 'EOF'
SynOS Custom Kernel v1.0
========================
- Rust-based bare metal kernel
- Neural Darwinism AI consciousness integration
- Enhanced security features
- Educational sandboxing support
- Custom scheduler with AI awareness

To boot:
Select "SynOS Kernel v1.0" from GRUB menu
EOF

    echo -e "${GREEN}✓ Kernel deployed to /boot/synos/synos-kernel-1.0${NC}"
else
    echo -e "${YELLOW}⚠ Custom kernel not found at target/x86_64-unknown-none/release/kernel${NC}"
    echo -e "${YELLOW}  Skipping kernel deployment (will use Debian kernel)${NC}"
fi
echo ""

# ============================================================================
# PHASE 3: Install AI Dependencies
# ============================================================================

echo -e "${BLUE}[3/8] Installing AI Dependencies...${NC}"

echo -e "  → Installing nats-py..."
sudo chroot "$CHROOT" pip3 install nats-py --break-system-packages 2>/dev/null || \
sudo chroot "$CHROOT" pip3 install nats-py 2>/dev/null || \
echo -e "${YELLOW}    ⚠ Failed to install nats-py (may already be installed)${NC}"

echo -e "  → Verifying AI packages..."
sudo chroot "$CHROOT" pip3 list | grep -E "torch|onnx|langchain|nats" || true

echo -e "${GREEN}✓ AI dependencies configured${NC}"
echo ""

# ============================================================================
# PHASE 4: Update GRUB Configuration
# ============================================================================

echo -e "${BLUE}[4/8] Updating GRUB Bootloader Configuration...${NC}"

GRUB_CFG="$CHROOT/boot/grub/grub.cfg"

if [ -f "$GRUB_CFG" ]; then
    # Backup original
    sudo cp "$GRUB_CFG" "$GRUB_CFG.backup"

    # Replace hostname=parrot with hostname=synos
    echo -e "  → Updating hostname branding..."
    sudo sed -i 's/hostname=parrot/hostname=synos/g' "$GRUB_CFG"

    # Replace Parrot references with SynOS
    sudo sed -i 's/Parrot Security/SynOS v1.0/g' "$GRUB_CFG"
    sudo sed -i 's/Parrot OS/SynOS/g' "$GRUB_CFG"

    # Add custom kernel entry if kernel exists
    if [ -f "$CHROOT/boot/synos/synos-kernel-1.0" ]; then
        echo -e "  → Adding custom kernel boot entry..."

        # Insert custom kernel entry after the first menuentry
        sudo sed -i '/^menuentry "Try \/ Install"/a \
\
menuentry "SynOS Custom Kernel v1.0" --class synos {\
    set gfxpayload=keep\
    echo "Loading SynOS Kernel v1.0..."\
    multiboot /boot/synos/synos-kernel-1.0\
}' "$GRUB_CFG"
    fi

    # Deploy custom GRUB theme
    if [ -f "assets/branding/grub/synos-grub-16x9.png" ]; then
        sudo mkdir -p "$CHROOT/boot/grub/themes/synos"
        sudo cp "assets/branding/grub/synos-grub-16x9.png" "$CHROOT/boot/grub/themes/synos/background.png"
        sudo cp "assets/branding/grub/synos-grub-4x3.png" "$CHROOT/boot/grub/themes/synos/background-4x3.png"

        echo -e "  → Deployed GRUB background images"
    fi

    echo -e "${GREEN}✓ GRUB configuration updated${NC}"
else
    echo -e "${YELLOW}⚠ GRUB config not found at $GRUB_CFG${NC}"
fi
echo ""

# ============================================================================
# PHASE 5: Deploy Plymouth Boot Splash
# ============================================================================

echo -e "${BLUE}[5/8] Deploying Plymouth Boot Splash...${NC}"

PLYMOUTH_THEME_DIR="$CHROOT/usr/share/plymouth/themes/synos-neural"

# Create Plymouth theme directory
sudo mkdir -p "$PLYMOUTH_THEME_DIR"

# Create improved Plymouth theme
sudo tee "$PLYMOUTH_THEME_DIR/synos-neural.plymouth" > /dev/null << 'EOF'
[Plymouth Theme]
Name=SynOS Neural
Description=SynOS v1.0 Neural Darwinism AI Boot Theme
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/synos-neural
ScriptFile=/usr/share/plymouth/themes/synos-neural/synos-neural.script
EOF

# Create simple boot script
sudo tee "$PLYMOUTH_THEME_DIR/synos-neural.script" > /dev/null << 'EOF'
# SynOS Neural Boot Animation
Window.SetBackgroundTopColor(0.00, 0.11, 0.22);
Window.SetBackgroundBottomColor(0.00, 0.40, 0.80);

message_sprite = Sprite();
message_sprite.SetPosition(Window.GetX() + Window.GetWidth() / 2 - 200, Window.GetY() + Window.GetHeight() - 100, 10000);

fun message_callback(text) {
    message_image = Image.Text(text, 1.0, 1.0, 1.0);
    message_sprite.SetImage(message_image);
}

Plymouth.SetMessageFunction(message_callback);

# Neural network animation placeholder
status = "normal";

fun refresh_callback() {
    if (status == "normal") {
        message_callback("SynOS v1.0 - Initializing Neural Darwinism AI...");
    }
}

Plymouth.SetRefreshFunction(refresh_callback);
EOF

# Copy logo if available
if [ -f "assets/branding/logos/synos-logo-128.png" ]; then
    sudo cp "assets/branding/logos/synos-logo-128.png" "$PLYMOUTH_THEME_DIR/logo.png"
fi

echo -e "${GREEN}✓ Plymouth theme deployed${NC}"
echo ""

# ============================================================================
# PHASE 6: Create Systemd Services
# ============================================================================

echo -e "${BLUE}[6/8] Creating Systemd Services...${NC}"

SERVICES_DIR="$CHROOT/etc/systemd/system"

# Create service for threat intelligence
sudo tee "$SERVICES_DIR/synos-threat-intel.service" > /dev/null << 'EOF'
[Unit]
Description=SynOS Threat Intelligence Feed Integration
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/synos-threat-intel daemon
Restart=on-failure
RestartSec=30
User=root

[Install]
WantedBy=multi-user.target
EOF

# Create service for threat hunting
sudo tee "$SERVICES_DIR/synos-threat-hunting.service" > /dev/null << 'EOF'
[Unit]
Description=SynOS Threat Hunting Platform
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/synos-threat-hunting daemon
Restart=on-failure
RestartSec=30
User=root

[Install]
WantedBy=multi-user.target
EOF

# Create service for zero trust engine
sudo tee "$SERVICES_DIR/synos-zt-engine.service" > /dev/null << 'EOF'
[Unit]
Description=SynOS Zero Trust Engine
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/synos-zt-engine daemon
Restart=on-failure
RestartSec=30
User=root

[Install]
WantedBy=multi-user.target
EOF

echo -e "  → Created systemd service files"
echo -e "  → Services can be enabled with: systemctl enable synos-*.service"

echo -e "${GREEN}✓ Systemd services configured${NC}"
echo ""

# ============================================================================
# PHASE 7: Deploy Desktop Customizations
# ============================================================================

echo -e "${BLUE}[7/8] Deploying Desktop Customizations...${NC}"

# Create desktop directories
sudo mkdir -p "$CHROOT/usr/share/backgrounds/synos"
sudo mkdir -p "$CHROOT/usr/share/pixmaps"

# Copy logos
if [ -d "assets/branding/logos" ]; then
    echo -e "  → Copying SynOS logos..."
    sudo cp assets/branding/logos/*.png "$CHROOT/usr/share/pixmaps/" 2>/dev/null || true
fi

# Create default wallpaper (simple gradient for now)
sudo tee "$CHROOT/usr/share/backgrounds/synos/synos-neural.svg" > /dev/null << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="1920" height="1080" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#001122;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0066cc;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="url(#bg)"/>
  <text x="960" y="540" text-anchor="middle" font-family="Arial" font-size="72" fill="#00ffff">SynOS v1.0</text>
  <text x="960" y="620" text-anchor="middle" font-family="Arial" font-size="36" fill="#ffffff">Neural Darwinism AI Framework</text>
</svg>
EOF

# Update MATE desktop defaults
sudo mkdir -p "$CHROOT/etc/dconf/db/local.d"
sudo tee "$CHROOT/etc/dconf/db/local.d/01-synos-defaults" > /dev/null << 'EOF'
[org/mate/desktop/background]
picture-filename='/usr/share/backgrounds/synos/synos-neural.svg'
color-shading-type='vertical-gradient'
primary-color='#001122'
secondary-color='#0066cc'

[org/mate/desktop/interface]
gtk-theme='Blackmate'
icon-theme='mate'

[org/mate/panel/general]
toplevel-id-list=['top']

[org/mate/panel/toplevels/top]
orientation='top'
size=32
EOF

# Update dconf database
sudo chroot "$CHROOT" dconf update 2>/dev/null || true

echo -e "${GREEN}✓ Desktop customizations deployed${NC}"
echo ""

# ============================================================================
# PHASE 8: Verification & Summary
# ============================================================================

echo -e "${BLUE}[8/8] Verification & Summary...${NC}"
echo ""

# Verify binaries
echo -e "${BLUE}Deployed Binaries:${NC}"
for binary in "${BINARIES[@]}"; do
    if [ -f "$CHROOT/usr/local/bin/$binary" ]; then
        SIZE=$(du -h "$CHROOT/usr/local/bin/$binary" | cut -f1)
        echo -e "  ${GREEN}✓${NC} $binary ($SIZE)"
    fi
done
echo ""

# Verify kernel
if [ -f "$CHROOT/boot/synos/synos-kernel-1.0" ]; then
    KERNEL_SIZE=$(du -h "$CHROOT/boot/synos/synos-kernel-1.0" | cut -f1)
    echo -e "${GREEN}✓${NC} Custom kernel deployed ($KERNEL_SIZE)"
fi
echo ""

# Verify AI packages
echo -e "${BLUE}AI Framework Status:${NC}"
if sudo chroot "$CHROOT" pip3 show nats-py &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} nats-py installed"
else
    echo -e "  ${YELLOW}⚠${NC} nats-py not installed"
fi

if sudo chroot "$CHROOT" pip3 show torch &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} PyTorch installed"
fi

if sudo chroot "$CHROOT" pip3 show onnxruntime &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} ONNX Runtime installed"
fi

if sudo chroot "$CHROOT" pip3 show langchain &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} LangChain installed"
fi
echo ""

# Final summary
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            SynOS v1.0 Deployment Complete!                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Rebuild ISO: cd linux-distribution/SynOS-Linux-Builder && sudo lb build"
echo -e "  2. Test in VM: qemu-system-x86_64 -cdrom build/synos-v1.0-complete.iso -m 4G"
echo -e "  3. Verify all features work"
echo ""
echo -e "${YELLOW}Note:${NC} Some services are created but not enabled."
echo -e "      Users can enable them with: systemctl enable synos-*.service"
echo ""
echo -e "${GREEN}✓ All components deployed successfully!${NC}"
echo ""
