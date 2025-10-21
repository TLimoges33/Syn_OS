#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# SynOS v1.0 - ParrotOS Remaster Build Script
# ═══════════════════════════════════════════════════════════════════════════
#
# This script takes ParrotOS Security Edition and transforms it into SynOS:
# - Replaces kernel with our custom Rust kernel
# - Injects all SynOS proprietary components
# - Rebrands everything (boot, desktop, branding)
# - Adds our 5 custom DEBs
# - Packages missing tools as DEBs
#
# Result: A pure SynOS experience built on ParrotOS foundation
# ═══════════════════════════════════════════════════════════════════════════

set -e

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORK_DIR="$PROJECT_ROOT/build/parrot-remaster"
ISO_DIR="$WORK_DIR/iso"
EXTRACT_DIR="$WORK_DIR/extract"
SQUASHFS_DIR="$WORK_DIR/squashfs"
NEW_ISO="$PROJECT_ROOT/build/iso/SynOS-v1.0-$(date +%Y%m%d).iso"

# ParrotOS ISO - accept as parameter or use wildcard
if [ -n "$1" ]; then
    PARROT_ISO="$1"
else
    PARROT_ISO="$WORK_DIR/Parrot-security-*.iso"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════════════
# Functions
# ═══════════════════════════════════════════════════════════════════════════

log() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
    exit 1
}

header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} $1"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root (use sudo)"
    fi
}

check_dependencies() {
    local deps=("mksquashfs" "unsquashfs" "xorriso" "genisoimage" "sed" "awk")
    local missing=()

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done

    if [ ${#missing[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing[*]}\nInstall with: sudo apt-get install squashfs-tools xorriso genisoimage"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# STEP 0: Pre-flight Checks
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 0: Pre-flight Checks"

check_root
check_dependencies

# Check if ParrotOS ISO exists
if ! ls "$PARROT_ISO" 1> /dev/null 2>&1; then
    error "ParrotOS ISO not found in $WORK_DIR/\n\nPlease download ParrotOS Security Edition from:\nhttps://www.parrotsec.org/download/\n\nPlace it in: $WORK_DIR/"
fi

PARROT_ISO_FILE=$(ls "$PARROT_ISO" | head -1)
log "Found ParrotOS ISO: $(basename "$PARROT_ISO_FILE")"

# Verify our custom components exist
log "Verifying SynOS custom components..."

REQUIRED_COMPONENTS=(
    "$PROJECT_ROOT/src/kernel/target/x86_64-unknown-none/release/kernel"
)

OPTIONAL_COMPONENTS=(
    "$PROJECT_ROOT/linux-distribution/SynOS-Packages/synos-ai-daemon_1.0.0_amd64.deb"
    "$PROJECT_ROOT/linux-distribution/SynOS-Packages/synos-consciousness-daemon_1.0.0_amd64.deb"
    "$PROJECT_ROOT/src/consciousness-framework"
)

for component in "${REQUIRED_COMPONENTS[@]}"; do
    if [ ! -e "$component" ]; then
        error "Missing component: $component"
    fi
done

for component in "${OPTIONAL_COMPONENTS[@]}"; do
    if [ ! -e "$component" ]; then
        warn "Optional component not found: $component"
    fi
done

log "All SynOS components verified!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: Create Working Directories
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 1: Creating Working Directories"

rm -rf "$EXTRACT_DIR" "$SQUASHFS_DIR"
mkdir -p "$EXTRACT_DIR" "$SQUASHFS_DIR" "$ISO_DIR"
mkdir -p "$(dirname "$NEW_ISO")"

log "Working directories created"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: Extract ParrotOS ISO
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 2: Extracting ParrotOS ISO"

log "Mounting ISO..."
mount -o loop "$PARROT_ISO_FILE" "$ISO_DIR"

log "Copying ISO contents..."
rsync -a --exclude=live/filesystem.squashfs "$ISO_DIR/" "$EXTRACT_DIR/"

log "Extracting SquashFS filesystem..."
unsquashfs -d "$SQUASHFS_DIR" "$ISO_DIR/live/filesystem.squashfs"

umount "$ISO_DIR"
log "ParrotOS ISO extracted successfully"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: Replace Kernel with SynOS Custom Rust Kernel
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 3: Installing SynOS Custom Kernel"

log "Backing up ParrotOS kernel..."
PARROT_KERNEL=$(ls "$SQUASHFS_DIR/boot/vmlinuz-"* | head -1)
mv "$PARROT_KERNEL" "${PARROT_KERNEL}.parrot.bak"

log "Installing SynOS Rust kernel..."
cp "$PROJECT_ROOT/src/kernel/target/x86_64-unknown-none/release/kernel" \
   "$SQUASHFS_DIR/boot/vmlinuz-synos-1.0.0"

# Create kernel symlink
ln -sf "vmlinuz-synos-1.0.0" "$SQUASHFS_DIR/boot/vmlinuz"

# Update initrd for our kernel
log "Regenerating initramfs for SynOS kernel..."
chroot "$SQUASHFS_DIR" update-initramfs -c -k 1.0.0

log "SynOS custom kernel installed!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: Inject SynOS Proprietary Components
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 4: Injecting SynOS Proprietary Components"

log "Installing SynOS custom DEBs..."
cp "$PROJECT_ROOT/linux-distribution/SynOS-Packages/"*.deb "$SQUASHFS_DIR/tmp/"

chroot "$SQUASHFS_DIR" bash -c 'dpkg -i /tmp/*.deb || apt-get -f install -y'
rm "$SQUASHFS_DIR/tmp/"*.deb

log "Installing ALFRED Voice Assistant..."
mkdir -p "$SQUASHFS_DIR/opt/synos/alfred"
cp -r "$PROJECT_ROOT/core/ai/alfred/target/release/alfred" "$SQUASHFS_DIR/opt/synos/alfred/"
cp -r "$PROJECT_ROOT/core/ai/alfred/config" "$SQUASHFS_DIR/opt/synos/alfred/"

log "Installing Consciousness Framework..."
mkdir -p "$SQUASHFS_DIR/opt/synos/consciousness"
cp -r "$PROJECT_ROOT/src/consciousness-framework/"* "$SQUASHFS_DIR/opt/synos/consciousness/"

log "Installing AI Daemon..."
mkdir -p "$SQUASHFS_DIR/opt/synos/ai"
cp "$PROJECT_ROOT/src/ai-engine/ai-daemon.py" "$SQUASHFS_DIR/opt/synos/ai/"

log "Installing Security Orchestrator..."
mkdir -p "$SQUASHFS_DIR/opt/synos/security"
cp -r "$PROJECT_ROOT/src/security-orchestrator/"* "$SQUASHFS_DIR/opt/synos/security/"

log "All SynOS proprietary components installed!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4.5: Install ALL Rust Binaries and Tools
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 4.5: Installing ALL Rust Components"

log "This is where we become LEGENDARY..."

# Security Tools
log "Installing advanced security tools..."
mkdir -p "$SQUASHFS_DIR/opt/synos/security"/{zero-trust,threat-intel,threat-hunting,deception,hsm}

if [ -f "$PROJECT_ROOT/src/zero-trust-engine/target/release/synos-zero-trust" ]; then
    cp "$PROJECT_ROOT/src/zero-trust-engine/target/release/synos-zero-trust" \
       "$SQUASHFS_DIR/opt/synos/security/zero-trust/"
    ln -sf /opt/synos/security/zero-trust/synos-zero-trust "$SQUASHFS_DIR/usr/bin/synos-zero-trust"
fi

if [ -f "$PROJECT_ROOT/src/threat-intel/target/release/synos-threat-intel" ]; then
    cp "$PROJECT_ROOT/src/threat-intel/target/release/synos-threat-intel" \
       "$SQUASHFS_DIR/opt/synos/security/threat-intel/"
    ln -sf /opt/synos/security/threat-intel/synos-threat-intel "$SQUASHFS_DIR/usr/bin/synos-threat-intel"
fi

if [ -f "$PROJECT_ROOT/src/threat-hunting/target/release/synos-threat-hunter" ]; then
    cp "$PROJECT_ROOT/src/threat-hunting/target/release/synos-threat-hunter" \
       "$SQUASHFS_DIR/opt/synos/security/threat-hunting/"
    ln -sf /opt/synos/security/threat-hunting/synos-threat-hunter "$SQUASHFS_DIR/usr/bin/synos-threat-hunter"
fi

if [ -f "$PROJECT_ROOT/src/deception-tech/target/release/synos-honeypot" ]; then
    cp "$PROJECT_ROOT/src/deception-tech/target/release/synos-honeypot" \
       "$SQUASHFS_DIR/opt/synos/security/deception/"
    ln -sf /opt/synos/security/deception/synos-honeypot "$SQUASHFS_DIR/usr/bin/synos-honeypot"
fi

if [ -f "$PROJECT_ROOT/src/hsm-integration/target/release/synos-hsm" ]; then
    cp "$PROJECT_ROOT/src/hsm-integration/target/release/synos-hsm" \
       "$SQUASHFS_DIR/opt/synos/security/hsm/"
    ln -sf /opt/synos/security/hsm/synos-hsm "$SQUASHFS_DIR/usr/bin/synos-hsm"
fi

# Compliance & Analytics
log "Installing compliance and analytics tools..."
mkdir -p "$SQUASHFS_DIR/opt/synos"/{compliance,analytics,research}

if [ -f "$PROJECT_ROOT/src/compliance-runner/target/release/synos-compliance" ]; then
    cp "$PROJECT_ROOT/src/compliance-runner/target/release/synos-compliance" \
       "$SQUASHFS_DIR/opt/synos/compliance/"
    ln -sf /opt/synos/compliance/synos-compliance "$SQUASHFS_DIR/usr/bin/synos-compliance"
fi

if [ -f "$PROJECT_ROOT/src/analytics/target/release/synos-analytics" ]; then
    cp "$PROJECT_ROOT/src/analytics/target/release/synos-analytics" \
       "$SQUASHFS_DIR/opt/synos/analytics/"
    ln -sf /opt/synos/analytics/synos-analytics "$SQUASHFS_DIR/usr/bin/synos-analytics"
fi

if [ -f "$PROJECT_ROOT/src/vuln-research/target/release/synos-vuln-research" ]; then
    cp "$PROJECT_ROOT/src/vuln-research/target/release/synos-vuln-research" \
       "$SQUASHFS_DIR/opt/synos/research/"
    ln -sf /opt/synos/research/synos-vuln-research "$SQUASHFS_DIR/usr/bin/synos-vuln-research"
fi

# Training & Education
log "Installing training and war games platform..."
mkdir -p "$SQUASHFS_DIR/opt/synos/training/wargames"

if [ -f "$PROJECT_ROOT/src/vm-wargames/target/release/synos-wargames" ]; then
    cp "$PROJECT_ROOT/src/vm-wargames/target/release/synos-wargames" \
       "$SQUASHFS_DIR/opt/synos/training/wargames/"
    ln -sf /opt/synos/training/wargames/synos-wargames "$SQUASHFS_DIR/usr/bin/synos-wargames"
fi

# Development Tools
log "Installing development tools..."
mkdir -p "$SQUASHFS_DIR/usr/bin"

if [ -f "$PROJECT_ROOT/src/userspace/shell/target/release/synsh" ]; then
    cp "$PROJECT_ROOT/src/userspace/shell/target/release/synsh" "$SQUASHFS_DIR/bin/"
    echo "/bin/synsh" >> "$SQUASHFS_DIR/etc/shells"
fi

if [ -f "$PROJECT_ROOT/src/userspace/synpkg/target/release/synpkg" ]; then
    cp "$PROJECT_ROOT/src/userspace/synpkg/target/release/synpkg" "$SQUASHFS_DIR/usr/bin/"
fi

if [ -f "$PROJECT_ROOT/src/tools/ai-model-manager/target/release/synos-model-manager" ]; then
    cp "$PROJECT_ROOT/src/tools/ai-model-manager/target/release/synos-model-manager" \
       "$SQUASHFS_DIR/usr/bin/"
fi

if [ -f "$PROJECT_ROOT/src/tools/distro-builder/target/release/synos-distro-builder" ]; then
    cp "$PROJECT_ROOT/src/tools/distro-builder/target/release/synos-distro-builder" \
       "$SQUASHFS_DIR/usr/bin/"
fi

if [ -d "$PROJECT_ROOT/src/tools/dev-utils/target/release" ]; then
    find "$PROJECT_ROOT/src/tools/dev-utils/target/release" -maxdepth 1 -type f -executable \
        -exec cp {} "$SQUASHFS_DIR/usr/bin/" \;
fi

# Libraries
log "Installing Rust libraries..."
mkdir -p "$SQUASHFS_DIR/usr/lib/synos"

for lib in "$PROJECT_ROOT"/core/*/target/release/*.so; do
    [ -f "$lib" ] && cp "$lib" "$SQUASHFS_DIR/usr/lib/synos/"
done

if [ -f "$PROJECT_ROOT/src/userspace/libtsynos/target/release/libtsynos.so" ]; then
    cp "$PROJECT_ROOT/src/userspace/libtsynos/target/release/libtsynos.so" \
       "$SQUASHFS_DIR/usr/lib/synos/"
fi

if [ -f "$PROJECT_ROOT/src/graphics/target/release/libsynos_graphics.so" ]; then
    cp "$PROJECT_ROOT/src/graphics/target/release/libsynos_graphics.so" \
       "$SQUASHFS_DIR/usr/lib/synos/"
fi

# Update library cache
chroot "$SQUASHFS_DIR" ldconfig

# AI Components
log "Installing AI runtime and engine..."
mkdir -p "$SQUASHFS_DIR/opt/synos/ai"/{runtime,engine,models}

if [ -f "$PROJECT_ROOT/src/ai-runtime/target/release/synos-ai-runtime" ]; then
    cp "$PROJECT_ROOT/src/ai-runtime/target/release/synos-ai-runtime" \
       "$SQUASHFS_DIR/opt/synos/ai/runtime/"
    ln -sf /opt/synos/ai/runtime/synos-ai-runtime "$SQUASHFS_DIR/usr/bin/synos-ai-runtime"
fi

if [ -f "$PROJECT_ROOT/src/ai-engine/target/release/synos-ai-engine" ]; then
    cp "$PROJECT_ROOT/src/ai-engine/target/release/synos-ai-engine" \
       "$SQUASHFS_DIR/opt/synos/ai/engine/"
    ln -sf /opt/synos/ai/engine/synos-ai-engine "$SQUASHFS_DIR/usr/bin/synos-ai-engine"
fi

# Desktop Environment
log "Installing desktop components..."
mkdir -p "$SQUASHFS_DIR/opt/synos/desktop"

if [ -d "$PROJECT_ROOT/src/desktop/target/release" ]; then
    find "$PROJECT_ROOT/src/desktop/target/release" -maxdepth 1 -type f -executable \
        -exec cp {} "$SQUASHFS_DIR/opt/synos/desktop/" \;
fi

# Testing Tools (for educational purposes)
log "Installing testing and educational tools..."
mkdir -p "$SQUASHFS_DIR/opt/synos/testing"/{fuzzing,ai,integration}

if [ -d "$PROJECT_ROOT/tests/fuzzing/target/release" ]; then
    find "$PROJECT_ROOT/tests/fuzzing/target/release" -maxdepth 1 -type f -executable \
        -exec cp {} "$SQUASHFS_DIR/opt/synos/testing/fuzzing/" \;
fi

if [ -d "$PROJECT_ROOT/tests/ai_module/target/release" ]; then
    find "$PROJECT_ROOT/tests/ai_module/target/release" -maxdepth 1 -type f -executable \
        -exec cp {} "$SQUASHFS_DIR/opt/synos/testing/ai/" \;
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4.6: Include Rust Source Code for Education
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 4.6: Including Source Code for Education"

log "Copying complete Rust source code..."
mkdir -p "$SQUASHFS_DIR/usr/share/synos/source"

# Copy source directories
cp -r "$PROJECT_ROOT/src" "$SQUASHFS_DIR/usr/share/synos/source/" 2>/dev/null || true
cp -r "$PROJECT_ROOT/core" "$SQUASHFS_DIR/usr/share/synos/source/" 2>/dev/null || true
cp -r "$PROJECT_ROOT/tests" "$SQUASHFS_DIR/usr/share/synos/source/" 2>/dev/null || true

# Copy root Cargo files
cp "$PROJECT_ROOT/Cargo.toml" "$SQUASHFS_DIR/usr/share/synos/source/" 2>/dev/null || true
cp "$PROJECT_ROOT/Cargo.lock" "$SQUASHFS_DIR/usr/share/synos/source/" 2>/dev/null || true
cp "$PROJECT_ROOT/rust-toolchain.toml" "$SQUASHFS_DIR/usr/share/synos/source/" 2>/dev/null || true

# Create source code README
cat > "$SQUASHFS_DIR/usr/share/synos/source/README.md" << 'SOURCEREADME'
# SynOS Complete Source Code

This directory contains the **complete source code** for all SynOS components.

## What's Included

- **src/** - All userspace components, services, and tools
- **core/** - Core libraries (security, AI, common, services)
- **tests/** - Complete test suites

## Building from Source

```bash
cd /usr/share/synos/source/

# Build everything
cargo build --release

# Build specific component
cd src/zero-trust-engine
cargo build --release
```

## Learning Path

1. Start with **core/common/** - Understand shared utilities
2. Explore **core/security/** - Learn security architecture
3. Study **core/ai/** - Dive into AI/ML systems
4. Build **src/services/** - See how daemons work
5. Experiment with **src/tools/** - Create your own tools

## Educational Philosophy

SynOS is designed to be:
- **Transparent** - All code is visible
- **Educational** - Learn by reading and modifying
- **Hackable** - Make it your own

**"The best way to learn security is to build a secure OS from scratch."**

Enjoy exploring!
SOURCEREADME

log "Source code included for educational purposes!"

success "✅ ALL RUST COMPONENTS INTEGRATED! 🦀"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: Complete SynOS Rebranding
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 5: Rebranding to SynOS"

log "Replacing boot splash..."
# Replace ParrotOS boot screen with SynOS
if [ -f "$PROJECT_ROOT/assets/branding/boot-splash.png" ]; then
    cp "$PROJECT_ROOT/assets/branding/boot-splash.png" \
       "$SQUASHFS_DIR/usr/share/plymouth/themes/synos/splash.png"
fi

log "Updating system identification..."
# Update /etc/os-release
cat > "$SQUASHFS_DIR/etc/os-release" << 'EOF'
NAME="SynOS"
VERSION="1.0 (Red Phoenix)"
ID=synos
ID_LIKE=debian
PRETTY_NAME="SynOS 1.0 - Red Phoenix"
VERSION_ID="1.0"
VERSION_CODENAME=phoenix
HOME_URL="https://synos.ai"
SUPPORT_URL="https://synos.ai/support"
BUG_REPORT_URL="https://github.com/synos/synos/issues"
LOGO=synos-logo
EOF

# Update /etc/issue
echo "SynOS 1.0 - Red Phoenix Edition" > "$SQUASHFS_DIR/etc/issue"
echo "" >> "$SQUASHFS_DIR/etc/issue"

# Update hostname
echo "synos" > "$SQUASHFS_DIR/etc/hostname"

log "Replacing desktop wallpapers..."
# Replace all ParrotOS wallpapers with SynOS branding
if [ -d "$PROJECT_ROOT/assets/desktop/wallpapers" ]; then
    rm -rf "$SQUASHFS_DIR/usr/share/backgrounds/parrot"
    mkdir -p "$SQUASHFS_DIR/usr/share/backgrounds/synos"
    cp -r "$PROJECT_ROOT/assets/desktop/wallpapers/"* \
          "$SQUASHFS_DIR/usr/share/backgrounds/synos/"
fi

log "Updating GRUB configuration..."
# Replace GRUB branding
sed -i 's/Parrot Security/SynOS/g' "$SQUASHFS_DIR/etc/default/grub"
sed -i 's/parrot/synos/g' "$SQUASHFS_DIR/etc/default/grub"

log "Replacing application menu branding..."
# Update menu entries
find "$SQUASHFS_DIR/usr/share/applications" -name "*.desktop" -type f \
    -exec sed -i 's/Parrot/SynOS/g' {} \;

log "Installing SynOS logos and themes..."
if [ -d "$PROJECT_ROOT/assets/themes" ]; then
    cp -r "$PROJECT_ROOT/assets/themes/"* "$SQUASHFS_DIR/usr/share/themes/"
fi

log "SynOS rebranding complete!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 6: Configure SynOS Services
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 6: Configuring SynOS Services"

log "Enabling ALFRED service..."
chroot "$SQUASHFS_DIR" systemctl enable alfred.service

log "Enabling Consciousness Framework service..."
chroot "$SQUASHFS_DIR" systemctl enable synos-consciousness.service

log "Enabling AI Daemon service..."
chroot "$SQUASHFS_DIR" systemctl enable synos-ai-daemon.service

log "Configuring SynOS startup..."
# Add SynOS welcome message
cat > "$SQUASHFS_DIR/etc/profile.d/synos-welcome.sh" << 'EOF'
#!/bin/bash
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    Welcome to SynOS v1.0                      ║"
echo "║                   Red Phoenix Edition                         ║"
echo "║                                                               ║"
echo "║  AI-Enhanced Security Operating System                       ║"
echo "║  Built with Custom Rust Kernel                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Type 'alfred' to activate voice assistant"
echo "Type 'synos-menu' for interactive command center"
echo "Type 'synos-help' for getting started guide"
echo ""
EOF

chmod +x "$SQUASHFS_DIR/etc/profile.d/synos-welcome.sh"

# Install SynOS Command Center Menu
log "Installing SynOS Command Center..."
cp "$PROJECT_ROOT/scripts/06-utilities/synos-menu.sh" "$SQUASHFS_DIR/usr/local/bin/synos-menu"
chmod +x "$SQUASHFS_DIR/usr/local/bin/synos-menu"

# Create desktop shortcut for menu
mkdir -p "$SQUASHFS_DIR/usr/share/applications"
cat > "$SQUASHFS_DIR/usr/share/applications/synos-command-center.desktop" << 'DESKTOP'
[Desktop Entry]
Name=SynOS Command Center
Comment=Access all SynOS tools and features
Exec=synos-menu
Icon=synos-logo
Terminal=true
Type=Application
Categories=System;Security;
DESKTOP

# Create simple help command
cat > "$SQUASHFS_DIR/usr/local/bin/synos-help" << 'HELP'
#!/bin/bash
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                    SynOS v1.0 - Quick Start Guide                    ║
╚══════════════════════════════════════════════════════════════════════╝

🚀 GETTING STARTED

  synos-menu          - Open interactive command center
  alfred              - Launch ALFRED AI assistant
  synsh               - Start SynOS custom shell

🔒 SECURITY TOOLS

  synos-zero-trust    - Zero trust network engine
  synos-threat-intel  - Threat intelligence platform
  synos-threat-hunter - Proactive threat hunting
  synos-honeypot      - Deception technology
  synos-compliance    - Compliance auditing

🧠 AI SYSTEMS

  Status checks:
    systemctl status synos-ai-daemon
    systemctl status synos-consciousness
    systemctl status synos-llm-engine

  Tools:
    synos-model-manager - Manage AI models
    synos-ai-runtime    - AI runtime environment

📦 PACKAGE MANAGEMENT

  synpkg install <package>   - Install package
  synpkg search <query>      - Search packages
  synpkg update              - Update package list

🛠️ DEVELOPMENT

  Source code:    /usr/share/synos/source/
  Documentation:  /usr/share/doc/synos/
  Build tools:    synos-distro-builder

🎓 LEARNING

  All source code is included in /usr/share/synos/source/
  Build from source: cd /usr/share/synos/source && cargo build
  Read the code, modify it, learn from it!

📚 MORE INFO

  Website:  https://synos.ai
  Docs:     https://synos.ai/docs
  GitHub:   https://github.com/synos/synos

═══════════════════════════════════════════════════════════════════════

The Pinnacle of Cybersecurity OS 🔥
EOF
HELP

chmod +x "$SQUASHFS_DIR/usr/local/bin/synos-help"

log "SynOS services configured!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 7: Clean Up and Prepare for Repackaging
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 7: Cleaning Up"

log "Removing ParrotOS residual files..."
rm -f "$SQUASHFS_DIR/etc/apt/sources.list.d/parrot.list"
rm -rf "$SQUASHFS_DIR/usr/share/doc/parrot-*"

log "Cleaning package cache..."
chroot "$SQUASHFS_DIR" apt-get clean
rm -rf "$SQUASHFS_DIR/var/cache/apt/archives/"*.deb

log "Updating package database..."
chroot "$SQUASHFS_DIR" apt-get update

log "Cleanup complete!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 8: Repackage as SynOS ISO
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 8: Creating SynOS ISO"

log "Creating new SquashFS filesystem..."
rm -f "$EXTRACT_DIR/live/filesystem.squashfs"
mksquashfs "$SQUASHFS_DIR" "$EXTRACT_DIR/live/filesystem.squashfs" \
    -comp xz -b 1M -Xbcj x86 -e boot

log "Updating filesystem size..."
printf $(du -sx --block-size=1 "$SQUASHFS_DIR" | cut -f1) > \
    "$EXTRACT_DIR/live/filesystem.size"

log "Calculating MD5 checksums..."
cd "$EXTRACT_DIR"
find . -type f -print0 | xargs -0 md5sum | grep -v "\./md5sum.txt" > md5sum.txt
cd "$WORK_DIR"

log "Generating ISO image..."
xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "SynOS 1.0" \
    -appid "SynOS Red Phoenix Edition" \
    -publisher "SynOS Development Team" \
    -preparer "SynOS Build System" \
    -eltorito-boot isolinux/isolinux.bin \
    -eltorito-catalog isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
    -eltorito-alt-boot \
    -e boot/grub/efi.img \
    -no-emul-boot \
    -isohybrid-gpt-basdat \
    -output "$NEW_ISO" \
    "$EXTRACT_DIR"

log "ISO created successfully!"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 9: Generate Checksums and Verification
# ═══════════════════════════════════════════════════════════════════════════

header "STEP 9: Generating Checksums"

cd "$(dirname "$NEW_ISO")"
sha256sum "$(basename "$NEW_ISO")" > "$(basename "$NEW_ISO").sha256"
md5sum "$(basename "$NEW_ISO")" > "$(basename "$NEW_ISO").md5"

log "Checksums generated!"

# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION
# ═══════════════════════════════════════════════════════════════════════════

header "🎉 SynOS v1.0 Build Complete!"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 BUILD SUCCESSFUL!                             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}ISO Location:${NC} $NEW_ISO"
echo -e "${CYAN}ISO Size:${NC} $(du -h "$NEW_ISO" | cut -f1)"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Test in VM: qemu-system-x86_64 -cdrom $NEW_ISO -m 4096 -smp 2 -enable-kvm"
echo "  2. Create bootable USB: sudo dd if=$NEW_ISO of=/dev/sdX bs=4M status=progress"
echo "  3. Verify checksums: sha256sum -c $(basename "$NEW_ISO").sha256"
echo ""
echo -e "${GREEN}Your custom SynOS with:${NC}"
echo "  ✓ Custom Rust kernel"
echo "  ✓ ALFRED voice assistant"
echo "  ✓ Consciousness framework"
echo "  ✓ AI daemon"
echo "  ✓ Full ParrotOS security tools"
echo "  ✓ Complete SynOS branding"
echo ""
echo -e "${CYAN}Time to test your creation! 🚀${NC}"
echo ""
