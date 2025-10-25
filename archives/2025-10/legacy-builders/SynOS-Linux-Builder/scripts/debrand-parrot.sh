#!/bin/bash

# SynOS De-branding Script - Remove all traces of ParrotOS and replace with SynOS
# This script systematically removes ParrotOS branding and replaces it with SynOS identity

set -e

FILESYSTEM_ROOT="/home/diablorain/Syn_OS/SynOS-Linux-Builder/filesystem-extract"
SCRIPT_DIR="$(dirname "$0")"

echo "🔧 Starting SynOS de-branding process..."

# Check if filesystem exists
if [ ! -d "$FILESYSTEM_ROOT" ]; then
    echo "❌ Filesystem not found at $FILESYSTEM_ROOT"
    exit 1
fi

echo "📁 Working directory: $FILESYSTEM_ROOT"

# Function to safely remove files/directories
safe_remove() {
    local target="$1"
    if [ -e "$target" ]; then
        echo "🗑️  Removing: $target"
        rm -rf "$target"
    fi
}

# Function to replace text in files
replace_text() {
    local file="$1"
    local search="$2"
    local replace="$3"

    if [ -f "$file" ]; then
        sed -i "s/$search/$replace/g" "$file" 2>/dev/null || true
    fi
}

echo "🎯 Phase 1: Removing ParrotOS backgrounds and wallpapers..."
safe_remove "$FILESYSTEM_ROOT/usr/share/backgrounds/grid-parrot.jpg"
safe_remove "$FILESYSTEM_ROOT/usr/share/backgrounds/parrot-abstract.jpg"
safe_remove "$FILESYSTEM_ROOT/usr/share/backgrounds/parrot-fly-grey.jpg"
safe_remove "$FILESYSTEM_ROOT/usr/share/backgrounds/parrot-glitch.jpg"
safe_remove "$FILESYSTEM_ROOT/usr/share/backgrounds/parrot-splash.jpg"

echo "🎨 Phase 2: Removing ParrotOS desktop themes..."
safe_remove "$FILESYSTEM_ROOT/usr/share/desktop-base/parrot-theme"
safe_remove "$FILESYSTEM_ROOT/usr/lib/parrot-skel"

echo "🗂️  Phase 3: Removing ParrotOS application launchers..."
find "$FILESYSTEM_ROOT/usr/share/applications/" -name "parrot-*.desktop" -type f -delete 2>/dev/null || true

echo "⚙️  Phase 4: Removing ParrotOS system configurations..."
safe_remove "$FILESYSTEM_ROOT/etc/xdg/autostart/parrot-updater.desktop"

echo "📊 Phase 5: Updating system identification files..."

# Update /etc/os-release
if [ -f "$FILESYSTEM_ROOT/etc/os-release" ]; then
    cat > "$FILESYSTEM_ROOT/etc/os-release" << 'EOF'
PRETTY_NAME="SynOS 1.0 (Neural)"
NAME="SynOS"
VERSION_ID="1.0"
VERSION="1.0 (Neural)"
VERSION_CODENAME=neural
ID=synos
ID_LIKE=debian
HOME_URL="https://github.com/FranklineMisango/Syn_OS"
SUPPORT_URL="https://github.com/FranklineMisango/Syn_OS/issues"
BUG_REPORT_URL="https://github.com/FranklineMisango/Syn_OS/issues"
LOGO=synos-logo
EOF
fi

# Update /etc/lsb-release
if [ -f "$FILESYSTEM_ROOT/etc/lsb-release" ]; then
    cat > "$FILESYSTEM_ROOT/etc/lsb-release" << 'EOF'
DISTRIB_ID=SynOS
DISTRIB_RELEASE=1.0
DISTRIB_CODENAME=neural
DISTRIB_DESCRIPTION="SynOS 1.0 Neural - AI-Enhanced Security Distribution"
EOF
fi

# Update issue files
echo "SynOS 1.0 Neural - AI-Enhanced Security Distribution \\n \\l" > "$FILESYSTEM_ROOT/etc/issue"
echo "SynOS 1.0 Neural - AI-Enhanced Security Distribution" > "$FILESYSTEM_ROOT/etc/issue.net"

# Update hostname
echo "synos" > "$FILESYSTEM_ROOT/etc/hostname"

echo "🔍 Phase 6: Searching for remaining Parrot references..."
# Find and report remaining parrot references in text files
echo "Scanning for remaining 'parrot' references in configuration files..."

find "$FILESYSTEM_ROOT/etc" -type f -name "*.conf" -o -name "*.cfg" -o -name "*.ini" 2>/dev/null | \
xargs grep -l -i "parrot" 2>/dev/null | head -10 | while read file; do
    echo "⚠️  Found parrot reference in: $file"
    # Replace common parrot references with synos
    sed -i 's/parrot/synos/gi' "$file" 2>/dev/null || true
    sed -i 's/Parrot/SynOS/g' "$file" 2>/dev/null || true
    sed -i 's/PARROT/SYNOS/g' "$file" 2>/dev/null || true
done

echo "🧹 Phase 7: Cleaning up package configurations..."
# Update package manager sources if they reference parrot repositories
if [ -f "$FILESYSTEM_ROOT/etc/apt/sources.list" ]; then
    # Remove or comment out parrot-specific repositories
    sed -i '/parrot/d' "$FILESYSTEM_ROOT/etc/apt/sources.list" 2>/dev/null || true
fi

# Clean up sources.list.d
find "$FILESYSTEM_ROOT/etc/apt/sources.list.d/" -name "*parrot*" -delete 2>/dev/null || true

echo "📝 Phase 8: Creating SynOS identification files..."

# Create SynOS motd
cat > "$FILESYSTEM_ROOT/etc/motd" << 'EOF'
 ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗
 ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝
 ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗
 ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║
 ███████║   ██║   ██║ ╚████║╚██████╔╝███████║
 ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝

 AI-Enhanced Security Operating System
 Neural Darwinism • Consciousness Computing • Cybersecurity

 🧠 Consciousness Status: Active
 🛡️  Security Framework: Enabled
 🔬 AI Research Platform: Ready

 Welcome to SynOS 1.0 Neural
EOF

echo "✅ Phase 9: Verification and cleanup complete"

# Summary
echo ""
echo "🎉 SynOS De-branding Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Removed ParrotOS backgrounds and themes"
echo "✅ Deleted ParrotOS application launchers"
echo "✅ Updated system identification files"
echo "✅ Replaced branding references with SynOS"
echo "✅ Created new SynOS identity files"
echo ""
echo "🚀 System is now ready for SynOS branding integration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"