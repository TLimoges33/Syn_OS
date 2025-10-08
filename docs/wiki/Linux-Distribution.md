# 🐧 Linux Distribution

**Complexity**: Intermediate to Advanced  
**Audience**: System Builders, Distribution Developers, DevOps Engineers  
**Prerequisites**: Linux administration, package management, system building, ISO creation

SynOS is built as a customized Linux distribution based on ParrotOS 6.4, featuring a custom kernel, integrated AI consciousness, and 500+ security tools. This guide explains how the distribution is built, customized, and maintained.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Distribution Architecture](#distribution-architecture)
3. [Base System](#base-system)
4. [Package Management](#package-management)
5. [ISO Building Process](#iso-building-process)
6. [Customization](#customization)
7. [Boot System](#boot-system)
8. [Installation System](#installation-system)
9. [Repository Management](#repository-management)
10. [Distribution Maintenance](#distribution-maintenance)

---

## 1. Overview

### What is SynOS?

SynOS is a **specialized Linux distribution** designed for:

-   **Penetration Testing**: 500+ pre-installed security tools
-   **AI Research**: Integrated AI consciousness engine
-   **Security Operations**: Red team, blue team, and SOC operations
-   **Education**: Cybersecurity training and research

### Distribution Hierarchy

```
┌─────────────────────────────────────────────────────┐
│                  SynOS Distribution                 │
│  (Custom kernel + AI + Security tools)              │
├─────────────────────────────────────────────────────┤
│                 ParrotOS 6.4 Base                   │
│  (Security-focused Debian derivative)               │
├─────────────────────────────────────────────────────┤
│                  Debian Testing                     │
│  (Package base and infrastructure)                  │
├─────────────────────────────────────────────────────┤
│                  Linux Kernel                       │
│  (Modified with SynOS kernel modules)               │
└─────────────────────────────────────────────────────┘
```

### Key Statistics

```
Distribution Stats:
├── Base OS: ParrotOS 6.4 (Debian Testing)
├── Kernel: Custom SynOS kernel (5.19+ compatible)
├── Packages: 3,500+ (including 500+ security tools)
├── Default DE: MATE (with KDE option)
├── ISO Size: ~4.2 GB (Live) / ~8 GB (Full)
├── Min RAM: 4 GB (8 GB recommended)
└── Architecture: x86_64 only
```

---

## 2. Distribution Architecture

### System Components

```
SynOS Distribution
│
├── Core System
│   ├── SynOS Custom Kernel
│   ├── SystemD Init System
│   ├── GNU Core Utilities
│   └── Base System Libraries
│
├── AI Layer
│   ├── AI Consciousness Engine
│   ├── TensorFlow Lite Runtime
│   ├── ONNX Runtime
│   └── ML Models
│
├── Security Layer
│   ├── Access Control (MAC/RBAC)
│   ├── Threat Detection
│   ├── Security Tools (500+)
│   └── HSM Support
│
├── Services
│   ├── Core Services (NATS, PostgreSQL, Redis)
│   ├── Web Interface
│   ├── API Gateway
│   └── Monitoring Stack
│
└── Desktop Environment
    ├── MATE Desktop
    ├── Custom Theme (Syn-Dark)
    ├── Control Panel
    └── Tool Launchers
```

### Directory Structure

```
/
├── bin/              # Essential binaries
├── boot/             # Boot files, kernel, initramfs
├── etc/              # System configuration
│   ├── synos/       # SynOS-specific configs
│   ├── security/    # Security policies
│   └── systemd/     # Service definitions
├── home/             # User home directories
├── lib/              # System libraries
├── opt/              # Optional software
│   └── synos/       # SynOS applications
├── root/             # Root user home
├── srv/              # Service data
├── tmp/              # Temporary files
├── usr/              # User programs and data
│   ├── bin/         # User binaries
│   ├── lib/         # User libraries
│   ├── share/       # Shared data
│   └── local/       # Local installations
└── var/              # Variable data
    ├── log/         # Log files
    ├── cache/       # Cache data
    └── lib/         # State information
```

---

## 3. Base System

### ParrotOS 6.4 Foundation

SynOS builds upon ParrotOS 6.4, which provides:

1. **Security-First Design**: Hardened by default
2. **Rich Tool Set**: Base security tools included
3. **Debian Compatibility**: Access to vast package ecosystem
4. **Rolling Release Model**: Latest software versions
5. **Active Community**: Regular updates and support

### Modifications from Base ParrotOS

```diff
+ Custom SynOS kernel (replaces stock Linux kernel)
+ AI consciousness engine and services
+ Additional 200+ security tools
+ Custom MATE theme and desktop integration
+ SynOS control panel and management tools
+ Enhanced systemd service configurations
+ Custom repository with SynOS-specific packages
+ Integrated development environment
+ Advanced monitoring and logging
```

### Package Selection

```bash
# Base system packages (minimal)
base_packages=(
    "linux-image-synos"      # Custom kernel
    "systemd"                # Init system
    "bash"                   # Shell
    "coreutils"              # Core utilities
    "apt"                    # Package manager
    "network-manager"        # Networking
)

# Desktop packages
desktop_packages=(
    "mate-desktop-environment"  # Desktop
    "synos-theme"               # Custom theme
    "synos-control-panel"       # Management
    "firefox-esr"               # Browser
    "gnome-terminal"            # Terminal
)

# Security packages
security_packages=(
    "nmap"                   # Network scanner
    "metasploit-framework"   # Exploitation
    "burpsuite"              # Web testing
    "wireshark"              # Packet analysis
    # ... 496 more tools
)

# Development packages
dev_packages=(
    "build-essential"        # Compilation tools
    "rustc"                  # Rust compiler
    "cargo"                  # Rust package manager
    "python3-dev"            # Python development
    "git"                    # Version control
)
```

---

## 4. Package Management

### SynPkg Package Manager

SynOS uses **SynPkg**, a wrapper around APT with SynOS-specific features:

```bash
# SynPkg commands
synpkg update                    # Update package lists
synpkg upgrade                   # Upgrade all packages
synpkg install <package>         # Install package
synpkg remove <package>          # Remove package
synpkg search <query>            # Search packages
synpkg info <package>            # Package information
synpkg list-tools                # List security tools
synpkg install-category <cat>    # Install tool category
```

### Package Repository Structure

```
SynOS Repository Layout:

https://repo.synos.dev/
├── dists/
│   └── stable/
│       ├── main/
│       │   ├── binary-amd64/
│       │   │   ├── Packages.gz
│       │   │   └── Release
│       │   └── source/
│       ├── security/
│       │   └── binary-amd64/
│       └── synos/
│           └── binary-amd64/    # SynOS-specific packages
│
└── pool/
    ├── main/                    # Main packages
    ├── security/                # Security tools
    └── synos/                   # SynOS packages
        ├── synos-kernel/
        ├── synos-ai-engine/
        ├── synos-control-panel/
        └── synos-theme/
```

### Custom Package Format

```bash
# Example: synos-ai-engine package

Package: synos-ai-engine
Version: 1.0.0
Architecture: amd64
Maintainer: SynOS Team <dev@synos.dev>
Depends: libtensorflowlite0, libonnxruntime1, python3 (>= 3.10)
Description: SynOS AI Consciousness Engine
 The AI consciousness engine provides adaptive learning,
 threat detection, and system optimization capabilities.
Section: synos
Priority: optional
Homepage: https://synos.dev
```

### Creating Custom Packages

```bash
# Build .deb package
#!/bin/bash

PKG_NAME="synos-ai-engine"
PKG_VERSION="1.0.0"
PKG_ARCH="amd64"

# Create package directory structure
mkdir -p ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}/DEBIAN
mkdir -p ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}/opt/synos/ai-engine
mkdir -p ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}/etc/systemd/system

# Copy files
cp -r build/ai-engine/* \
    ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}/opt/synos/ai-engine/

# Create control file
cat > ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}/DEBIAN/control << EOF
Package: ${PKG_NAME}
Version: ${PKG_VERSION}
Architecture: ${PKG_ARCH}
Maintainer: SynOS Team <dev@synos.dev>
Depends: libtensorflowlite0, libonnxruntime1, python3 (>= 3.10)
Description: SynOS AI Consciousness Engine
Section: synos
Priority: optional
EOF

# Create postinst script
cat > ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

# Enable service
systemctl daemon-reload
systemctl enable synos-ai-engine
systemctl start synos-ai-engine

exit 0
EOF

chmod +x ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}/DEBIAN/postinst

# Build package
dpkg-deb --build ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}

echo "Package created: ${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"
```

---

## 5. ISO Building Process

### Live-Build Configuration

SynOS uses `live-build` to create bootable ISO images:

```bash
# Directory structure
linux-distribution/SynOS-Linux-Builder/
├── auto/
│   ├── build                # Build script
│   ├── clean                # Clean script
│   └── config               # Configuration script
├── config/
│   ├── package-lists/
│   │   ├── base.list.chroot         # Base packages
│   │   ├── desktop.list.chroot      # Desktop packages
│   │   ├── security.list.chroot     # Security tools
│   │   └── synos.list.chroot        # SynOS packages
│   ├── hooks/
│   │   ├── normal/
│   │   │   ├── 0100-install-kernel.hook.chroot
│   │   │   ├── 0200-configure-system.hook.chroot
│   │   │   └── 0300-install-ai.hook.chroot
│   │   └── live/
│   ├── includes.chroot/
│   │   ├── etc/
│   │   │   └── synos/           # SynOS configs
│   │   └── opt/
│   │       └── synos/           # SynOS applications
│   ├── bootloaders/
│   │   └── grub-pc/
│   └── preseed/
└── build.sh                     # Master build script
```

### Build Configuration

```bash
# config/auto/config

#!/bin/bash

lb config noauto \
    --mode debian \
    --distribution testing \
    --debian-installer live \
    --debian-installer-gui true \
    --archive-areas "main contrib non-free" \
    --architectures amd64 \
    --linux-flavours amd64 \
    --bootappend-live "boot=live components quiet splash" \
    --bootappend-install "auto=true priority=critical" \
    --binary-images iso-hybrid \
    --iso-application "SynOS" \
    --iso-preparer "SynOS Team" \
    --iso-publisher "SynOS Project" \
    --iso-volume "SynOS 1.0" \
    --memtest memtest86+ \
    --win32-loader false \
    --checksums sha256 \
    --apt-recommends true \
    --apt-indices true \
    --cache-packages true \
    --debootstrap-options "--variant=minbase" \
    --firmware-chroot true \
    --firmware-binary true \
    "${@}"
```

### Build Script

```bash
#!/bin/bash
# scripts/build-synos-iso.sh

set -e

BUILD_DIR="linux-distribution/SynOS-Linux-Builder"
OUTPUT_DIR="build"

echo "==> Building SynOS ISO"

# Clean previous build
cd ${BUILD_DIR}
lb clean --purge

# Configure build
lb config

# Build ISO
lb build 2>&1 | tee build.log

# Move ISO to output directory
mkdir -p ../../${OUTPUT_DIR}
mv *.iso ../../${OUTPUT_DIR}/syn_os.iso
mv *.sha256 ../../${OUTPUT_DIR}/syn_os.iso.sha256
mv *.md5 ../../${OUTPUT_DIR}/syn_os.iso.md5

echo "==> ISO built successfully!"
echo "    Location: ${OUTPUT_DIR}/syn_os.iso"
echo "    Size: $(du -h ../../${OUTPUT_DIR}/syn_os.iso | cut -f1)"
```

### Post-Build Hooks

```bash
# config/hooks/normal/0200-configure-system.hook.chroot

#!/bin/bash

set -e

echo "Configuring SynOS system..."

# Install custom kernel
dpkg -i /tmp/synos-kernel_*.deb

# Configure systemd services
systemctl enable synos-ai-engine
systemctl enable synos-security-monitor
systemctl enable synos-web-interface

# Set up SynOS theme
update-alternatives --set gtk-theme /usr/share/themes/Syn-Dark

# Configure GRUB
cat >> /etc/default/grub << EOF
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash synos.mode=full"
GRUB_TIMEOUT=5
EOF

update-grub

# Create SynOS user
useradd -m -s /bin/bash -G sudo,synos synos
echo "synos:synos" | chpasswd

echo "System configuration complete!"
```

---

## 6. Customization

### Desktop Theme

```bash
# Custom MATE theme: Syn-Dark
/usr/share/themes/Syn-Dark/
├── gtk-2.0/
│   └── gtkrc           # GTK2 theme
├── gtk-3.0/
│   └── gtk.css         # GTK3 theme
├── metacity-1/
│   └── metacity-theme-3.xml
└── index.theme         # Theme metadata
```

**Color Scheme**:

-   Primary: `#2E3440` (dark blue-gray)
-   Secondary: `#4C566A` (medium blue-gray)
-   Accent: `#88C0D0` (light blue)
-   Success: `#A3BE8C` (green)
-   Warning: `#EBCB8B` (yellow)
-   Error: `#BF616A` (red)

### Desktop Layout

```bash
# Panel configuration
dconf write /org/mate/panel/toplevels/top/size 32
dconf write /org/mate/panel/toplevels/top/background/type "'solid'"
dconf write /org/mate/panel/toplevels/top/background/color "'#2E3440'"

# Window manager settings
dconf write /org/mate/marco/general/theme "'Syn-Dark'"
dconf write /org/mate/marco/general/titlebar-font "'Sans Bold 11'"

# Desktop background
dconf write /org/mate/desktop/background/picture-filename \
    "'/usr/share/backgrounds/synos/synos-default.png'"
```

### Menu Integration

```bash
# Desktop menu entry
/usr/share/applications/synos-control-panel.desktop

[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS Control Panel
Comment=Manage SynOS system settings
Exec=/opt/synos/bin/synos-control-panel
Icon=/usr/share/pixmaps/synos-icon.png
Terminal=false
Categories=System;Settings;
```

---

## 7. Boot System

### GRUB Configuration

```bash
# /etc/default/grub (SynOS configuration)

GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="SynOS"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash synos.mode=full"
GRUB_CMDLINE_LINUX=""
GRUB_THEME="/boot/grub/themes/synos/theme.txt"
GRUB_BACKGROUND="/boot/grub/backgrounds/synos-splash.png"
GRUB_GFXMODE=1920x1080
```

### Boot Menu Entries

```bash
# /boot/grub/grub.cfg (auto-generated)

menuentry 'SynOS' --class synos --class gnu-linux --class gnu --class os {
    load_video
    insmod gzio
    insmod part_gpt
    insmod ext2

    set root='hd0,gpt2'

    echo 'Loading SynOS kernel...'
    linux /boot/vmlinuz-synos root=/dev/sda2 ro quiet splash synos.mode=full

    echo 'Loading initial ramdisk...'
    initrd /boot/initrd.img-synos
}

menuentry 'SynOS (Safe Mode)' --class synos --class gnu-linux --class gnu --class os {
    linux /boot/vmlinuz-synos root=/dev/sda2 ro single
    initrd /boot/initrd.img-synos
}

menuentry 'SynOS (Recovery Mode)' --class synos --class gnu-linux --class gnu --class os {
    linux /boot/vmlinuz-synos root=/dev/sda2 ro recovery nomodeset
    initrd /boot/initrd.img-synos
}
```

### InitramFS

```bash
# Generate custom initramfs with SynOS modules
update-initramfs -u -k all

# Custom initramfs hooks
/etc/initramfs-tools/hooks/synos-kernel

#!/bin/bash
PREREQ=""
prereqs() { echo "$PREREQ"; }
case $1 in
    prereqs) prereqs; exit 0;;
esac

# Copy SynOS kernel modules
cp -r /lib/modules/$(uname -r)/kernel/synos ${DESTDIR}/lib/modules/$(uname -r)/kernel/
```

---

## 8. Installation System

### Debian Installer Customization

```bash
# Preseed configuration for automated installation
/config/preseed/synos.cfg

# Localization
d-i debian-installer/locale string en_US.UTF-8
d-i keyboard-configuration/xkb-keymap select us

# Network configuration
d-i netcfg/choose_interface select auto
d-i netcfg/get_hostname string synos
d-i netcfg/get_domain string localdomain

# User setup
d-i passwd/user-fullname string SynOS User
d-i passwd/username string synos
d-i passwd/user-password password synos
d-i passwd/user-password-again password synos
d-i passwd/root-login boolean false

# Partitioning
d-i partman-auto/method string lvm
d-i partman-auto-lvm/guided_size string max
d-i partman-lvm/confirm boolean true
d-i partman-auto/choose_recipe select atomic

# Enable encryption
d-i partman-auto-crypto/erase_disks boolean false
d-i partman-crypto/passphrase password synos
d-i partman-crypto/passphrase-again password synos

# Package selection
tasksel tasksel/first multiselect standard
d-i pkgsel/include string synos-kernel synos-ai-engine synos-control-panel

# GRUB
d-i grub-installer/only_debian boolean true
d-i grub-installer/bootdev string default

# Finish
d-i finish-install/reboot_in_progress note
```

### Post-Installation Script

```bash
# /usr/lib/finish-install.d/99synos

#!/bin/bash

set -e

echo "Running SynOS post-installation..."

# Update system
apt-get update
apt-get upgrade -y

# Install additional packages
apt-get install -y $(cat /tmp/package-list.txt)

# Configure services
systemctl enable synos-ai-engine
systemctl enable synos-security-monitor
systemctl enable synos-web-interface

# Set up AI models
/opt/synos/bin/synos-setup --install-models

# Generate initial configuration
/opt/synos/bin/synos-setup --configure

# Create desktop shortcuts
cp /usr/share/applications/synos-*.desktop /home/synos/Desktop/
chown synos:synos /home/synos/Desktop/*.desktop

echo "Post-installation complete!"
```

---

## 9. Repository Management

### Repository Structure

```bash
# Repository management with reprepro
/srv/repo.synos.dev/
├── conf/
│   ├── distributions      # Distribution definitions
│   └── options           # Repository options
├── db/                   # Repository database
├── dists/                # Distribution metadata
│   └── stable/
│       ├── Release
│       ├── Release.gpg
│       └── main/
│           └── binary-amd64/
│               └── Packages
└── pool/                 # Package pool
    └── main/
        ├── s/synos-kernel/
        ├── s/synos-ai-engine/
        └── ...
```

### Adding Packages to Repository

```bash
#!/bin/bash
# scripts/add-to-repo.sh

PACKAGE=$1
DISTRIBUTION="stable"
COMPONENT="main"

# Sign package
dpkg-sig --sign builder ${PACKAGE}

# Add to repository
reprepro -b /srv/repo.synos.dev \
    --component ${COMPONENT} \
    includedeb ${DISTRIBUTION} \
    ${PACKAGE}

echo "Package added to repository!"
```

### Repository Configuration

```bash
# conf/distributions

Origin: SynOS
Label: SynOS
Suite: stable
Codename: stable
Architectures: amd64 source
Components: main security synos
Description: SynOS Official Repository
SignWith: SYNOS_GPG_KEY_ID
Pull: stable

# conf/options
verbose
ask-passphrase
basedir /srv/repo.synos.dev
```

---

## 10. Distribution Maintenance

### Update Workflow

```bash
# 1. Update package lists
synpkg update

# 2. Upgrade packages
synpkg upgrade

# 3. Update kernel (if available)
synpkg install linux-image-synos

# 4. Update AI models
synos-ai update-models

# 5. Update security tools
synpkg update-tools

# 6. Reboot if kernel updated
if [ -f /var/run/reboot-required ]; then
    reboot
fi
```

### Version Management

```bash
# SynOS version information
/etc/synos-release

PRETTY_NAME="SynOS 1.0"
NAME="SynOS"
VERSION_ID="1.0"
VERSION="1.0 (Nexus)"
ID=synos
ID_LIKE=parrot debian
HOME_URL="https://synos.dev"
SUPPORT_URL="https://synos.dev/support"
BUG_REPORT_URL="https://github.com/synos/synos/issues"
```

### Release Process

```bash
#!/bin/bash
# scripts/release.sh

VERSION=$1
CODENAME=$2

echo "Creating SynOS ${VERSION} (${CODENAME})"

# 1. Update version files
sed -i "s/VERSION=.*/VERSION=\"${VERSION}\"/" /etc/synos-release
sed -i "s/VERSION_ID=.*/VERSION_ID=\"${VERSION}\"/" /etc/synos-release

# 2. Build packages
for pkg in kernel ai-engine control-panel theme; do
    cd packages/${pkg}
    dpkg-buildpackage -b -us -uc
    cd ../..
done

# 3. Build ISO
./scripts/build-synos-iso.sh

# 4. Test ISO
./scripts/test-iso.sh build/syn_os.iso

# 5. Sign and checksum
gpg --detach-sign build/syn_os.iso
sha256sum build/syn_os.iso > build/syn_os.iso.sha256
md5sum build/syn_os.iso > build/syn_os.iso.md5

# 6. Tag release
git tag -a v${VERSION} -m "SynOS ${VERSION} (${CODENAME})"
git push origin v${VERSION}

echo "Release ${VERSION} complete!"
```

### Testing

```bash
# Automated testing
./scripts/test-iso.sh build/syn_os.iso

# Tests performed:
# - Boot test (UEFI/BIOS)
# - Installation test
# - Package integrity
# - Service startup
# - AI engine initialization
# - Security tool availability
# - Network connectivity
# - Hardware detection
```

---

## 📚 Further Reading

-   [Custom Kernel](Custom-Kernel.md) - Kernel architecture
-   [Security Framework](Security-Framework.md) - Security features
-   [Development Guide](Development-Guide.md) - Building from source
-   [Debian Live Manual](https://live-team.pages.debian.net/live-manual/)
-   [ParrotOS Documentation](https://www.parrotsec.org/docs/)

---

**Last Updated**: October 4, 2025  
**Maintainer**: SynOS Distribution Team  
**License**: MIT

SynOS - The AI-powered penetration testing distribution! 🐧✨
