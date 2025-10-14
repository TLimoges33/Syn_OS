#!/bin/bash

################################################################################
# SYNOS V1.0 FINAL BUILD - EXACT COMMANDS
# Date: October 11, 2025
# All critical issues fixed - Ready for production ISO build
################################################################################

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         SYN_OS V1.0 - FINAL PRODUCTION BUILD                 ║"
echo "║         All Critical Fixes Applied                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Stop any running builds
echo "Step 1: Stopping any existing build processes..."
sudo pkill -f build-synos-ultimate-iso 2>/dev/null || echo "  No running builds found"
sleep 2

# Step 2: Clean up previous build directory
echo ""
echo "Step 2: Cleaning up previous build directory..."
if [ -d "/home/diablorain/Syn_OS/build/synos-ultimate" ]; then
    sudo rm -rf /home/diablorain/Syn_OS/build/synos-ultimate
    echo "  ✓ Old build directory removed"
else
    echo "  ✓ No cleanup needed"
fi

# Step 3: Verify build script has all fixes
echo ""
echo "Step 3: Verifying build script has all fixes..."
SCRIPT="/home/diablorain/Syn_OS/scripts/build/build-synos-ultimate-iso.sh"

# Check for critical fixes
FIXES_OK=true

if grep -q "linux-image-amd64" "$SCRIPT"; then
    echo "  ✓ Linux kernel installation: PRESENT"
else
    echo "  ✗ Linux kernel installation: MISSING"
    FIXES_OK=false
fi

if grep -q "signed-by=/usr/share/keyrings/parrot-archive-keyring.gpg" "$SCRIPT"; then
    echo "  ✓ ParrotOS GPG key fix: PRESENT"
else
    echo "  ✗ ParrotOS GPG key fix: MISSING"
    FIXES_OK=false
fi

if grep -q "mkdir -p /etc/sudoers.d" "$SCRIPT"; then
    echo "  ✓ Sudoers directory fix: PRESENT"
else
    echo "  ✗ Sudoers directory fix: MISSING"
    FIXES_OK=false
fi

if ! grep -q "git vim nano emacs" "$SCRIPT"; then
    echo "  ✓ Emacs removed: CONFIRMED"
else
    echo "  ✗ Emacs still in package list"
    FIXES_OK=false
fi

if grep -q 'PROJECT_ROOT="\$(cd "\$SCRIPT_DIR/../.." && pwd)"' "$SCRIPT"; then
    echo "  ✓ PROJECT_ROOT path fix: PRESENT (CRITICAL)"
else
    echo "  ✗ PROJECT_ROOT path fix: MISSING (will cause kernel/AI source not found!)"
    FIXES_OK=false
fi

if [ "$FIXES_OK" = false ]; then
    echo ""
    echo "❌ ERROR: Build script missing critical fixes!"
    echo "Please ensure all fixes from BUILD_FIXES_OCT11_2025.md are applied."
    exit 1
fi

echo ""
echo "✅ All critical fixes verified in build script!"

# Step 4: Check disk space
echo ""
echo "Step 4: Checking available disk space..."
AVAILABLE=$(df -BG /home/diablorain/Syn_OS/scripts/build | tail -1 | awk '{print $4}' | sed 's/G//')
REQUIRED=15

if [ "$AVAILABLE" -lt "$REQUIRED" ]; then
    echo "  ⚠ WARNING: Low disk space!"
    echo "  Available: ${AVAILABLE}GB"
    echo "  Required: ${REQUIRED}GB minimum"
    echo "  Recommended: 25GB+"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "  ✓ Sufficient disk space: ${AVAILABLE}GB available"
fi

# Step 5: Start the build
echo ""
echo "Step 5: Starting SynOS v1.0 ISO build..."
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Build will take approximately 45-60 minutes"
echo "  Output will be logged to /tmp/synos-ultimate-build-final.log"
echo "  ISO will be created in build/synos-ultimate/"
echo "════════════════════════════════════════════════════════════════"
echo ""
read -p "Press ENTER to start the build, or Ctrl+C to cancel..."
echo ""

cd /home/diablorain/Syn_OS/scripts/build

# Run the build with logging
sudo ./build-synos-ultimate-iso.sh 2>&1 | tee /tmp/synos-ultimate-build-final.log

# Step 6: Check build results
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Build process completed! Checking results..."
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "/home/diablorain/Syn_OS/build/synos-ultimate/SynOS-Ultimate"*.iso ]; then
    ISO_PATH=$(ls -1 /home/diablorain/Syn_OS/build/synos-ultimate/SynOS-Ultimate*.iso | head -1)
    ISO_SIZE=$(du -h "$ISO_PATH" | cut -f1)

    echo "✅ SUCCESS! ISO built successfully!"
    echo ""
    echo "📀 ISO Location: $ISO_PATH"
    echo "📊 ISO Size: $ISO_SIZE"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Username: synos"
    echo "   Password: synos"
    echo "   Root password: toor"
    echo ""
    echo "🚀 Test the ISO:"
    echo "   qemu-system-x86_64 -cdrom \"$ISO_PATH\" -m 4G -enable-kvm"
    echo ""
    echo "📝 Build log: /tmp/synos-ultimate-build-final.log"

    # Create checksum
    echo ""
    echo "Creating SHA256 checksum..."
    sha256sum "$ISO_PATH" > "${ISO_PATH}.sha256"
    echo "✓ Checksum saved: ${ISO_PATH}.sha256"

else
    echo "❌ BUILD FAILED: ISO file not found"
    echo ""
    echo "Check the build log for errors:"
    echo "   tail -100 /tmp/synos-ultimate-build-final.log"
    echo ""
    echo "Common issues:"
    echo "   - Insufficient disk space"
    echo "   - Network connectivity problems"
    echo "   - Permission issues"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  🎉 SYN_OS V1.0 BUILD COMPLETE! 🎉"
echo "════════════════════════════════════════════════════════════════"
