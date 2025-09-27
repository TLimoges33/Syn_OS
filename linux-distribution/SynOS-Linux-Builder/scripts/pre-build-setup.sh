#!/bin/bash

# SynOS Pre-Build Setup Script
# Ensures ALL directories exist before any build scripts run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/build"

echo "🔧 SynOS Pre-Build Setup"
echo "========================"

# Ensure we're in the build directory
cd "$BUILD_DIR" || { echo "❌ Build directory not found!"; exit 1; }

echo "📁 Creating comprehensive directory structure..."

# Core live-build directories
mkdir -p config/{includes.chroot,hooks,package-lists,archives,preseed}
mkdir -p config/hooks/{live,binary,source}
mkdir -p logs stages releases

# Complete includes.chroot structure
mkdir -p config/includes.chroot/{bin,sbin,lib,usr,var,etc,opt,home,boot,dev,proc,sys,tmp}

# /etc structure
mkdir -p config/includes.chroot/etc/{synos,systemd,init.d,update-motd.d,skel,cron.d}
mkdir -p config/includes.chroot/etc/systemd/{system,user}
mkdir -p config/includes.chroot/etc/skel/{.config,.local}
mkdir -p config/includes.chroot/etc/skel/.config/{autostart,dconf}
mkdir -p config/includes.chroot/etc/skel/.config/dconf/user.d
mkdir -p config/includes.chroot/etc/skel/.local/{share,bin}
mkdir -p config/includes.chroot/etc/skel/Desktop

# /usr structure
mkdir -p config/includes.chroot/usr/{bin,sbin,lib,share,local,include}
mkdir -p config/includes.chroot/usr/local/{bin,lib,share}
mkdir -p config/includes.chroot/usr/lib/{synos,systemd,python3}
mkdir -p config/includes.chroot/usr/share/{synos,applications,backgrounds,themes,icons,pixmaps,plymouth,grub}
mkdir -p config/includes.chroot/usr/share/synos/{tools,docs,configs}
mkdir -p config/includes.chroot/usr/share/backgrounds/synos
mkdir -p config/includes.chroot/usr/share/themes/{SynOS,synos}
mkdir -p config/includes.chroot/usr/share/icons/synos
mkdir -p config/includes.chroot/usr/share/pixmaps/synos
mkdir -p config/includes.chroot/usr/share/plymouth/themes/synos
mkdir -p config/includes.chroot/usr/share/grub/themes/synos

# /opt structure (SynOS custom)
mkdir -p config/includes.chroot/opt/{synos,packages}
mkdir -p config/includes.chroot/opt/synos/{bin,lib,share,data,src,logs,tmp}
mkdir -p config/includes.chroot/opt/synos/{consciousness,education,dashboard,security,tools}
mkdir -p config/includes.chroot/opt/synos/consciousness/{models,data,logs}
mkdir -p config/includes.chroot/opt/synos/education/{modules,tutorials,assessments,labs}
mkdir -p config/includes.chroot/opt/synos/dashboard/{static,templates,api}
mkdir -p config/includes.chroot/opt/synos/security/{tools,configs,logs}

# /var structure
mkdir -p config/includes.chroot/var/{log,lib,tmp,cache,spool}
mkdir -p config/includes.chroot/var/log/{synos,apache2,nginx}
mkdir -p config/includes.chroot/var/lib/{synos,dpkg,apt}
mkdir -p config/includes.chroot/var/cache/synos

# /home structure
mkdir -p config/includes.chroot/home/{user,synos,root}
mkdir -p config/includes.chroot/home/user/{Desktop,Documents,Downloads,.config,.local}
mkdir -p config/includes.chroot/home/user/.config/{autostart,dconf}
mkdir -p config/includes.chroot/home/user/.local/{share,bin}

# Create empty files to prevent errors
touch config/includes.chroot/etc/hostname
touch config/includes.chroot/etc/hosts
touch config/package-lists/synos-base.list.chroot
touch config/package-lists/synos-security.list.chroot
touch config/package-lists/synos-education.list.chroot

# Set proper permissions
chmod -R 755 config/includes.chroot/usr/bin config/includes.chroot/opt/synos/bin
chmod -R 755 config/includes.chroot/usr/local/bin
chmod 644 config/includes.chroot/etc/hostname config/includes.chroot/etc/hosts

echo "✅ Directory structure created successfully"

# Verify critical paths exist
CRITICAL_PATHS=(
    "config/includes.chroot/usr/bin"
    "config/includes.chroot/opt/synos/bin"
    "config/includes.chroot/etc/synos"
    "config/includes.chroot/usr/lib/synos"
    "config/includes.chroot/usr/share/synos"
    "config/hooks/live"
    "config/package-lists"
)

echo "🔍 Verifying critical paths..."
for path in "${CRITICAL_PATHS[@]}"; do
    if [[ -d "$path" ]]; then
        echo "✅ $path"
    else
        echo "❌ $path - MISSING!"
        exit 1
    fi
done

echo ""
echo "🎉 Pre-build setup complete!"
echo "📁 All directories created and ready for build scripts"
echo "✅ Ready to proceed with build process"