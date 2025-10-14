#!/bin/bash
# Fix GRUB Branding - Update hostname from parrot to synos

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              SynOS GRUB Branding Fix                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# GRUB configs to update
GRUB_ISO="build/synos-v1.0/iso/boot/grub/grub.cfg"
GRUB_BUILDER="linux-distribution/SynOS-Linux-Builder/synos-ultimate/boot/grub/grub.cfg"

# Update ISO GRUB
if [ -f "$GRUB_ISO" ]; then
    echo "→ Updating GRUB in existing ISO..."
    cp "$GRUB_ISO" "$GRUB_ISO.backup"
    sed -i 's/hostname=parrot/hostname=synos/g' "$GRUB_ISO"
    sed -i 's/Parrot Security/SynOS v1.0/g' "$GRUB_ISO"
    sed -i 's/Parrot OS/SynOS/g' "$GRUB_ISO"
    echo "✓ ISO GRUB updated"
else
    echo "⚠ ISO GRUB not found (will be created during build)"
fi

echo ""

# Update Builder GRUB (template for future builds)
if [ -f "$GRUB_BUILDER" ]; then
    echo "→ Updating GRUB template in builder..."
    cp "$GRUB_BUILDER" "$GRUB_BUILDER.backup"
    sed -i 's/hostname=parrot/hostname=synos/g' "$GRUB_BUILDER"
    sed -i 's/Parrot Security/SynOS v1.0/g' "$GRUB_BUILDER"
    sed -i 's/Parrot OS/SynOS/g' "$GRUB_BUILDER"

    # Add custom kernel entry if kernel exists
    if [ -f "build/synos-v1.0/work/chroot/boot/synos/synos-kernel-1.0" ]; then
        echo "→ Adding custom kernel boot entry..."
        sed -i '/^menuentry "Try \/ Install"/a \
\
menuentry "SynOS Custom Kernel v1.0" --class synos {\
    set gfxpayload=keep\
    echo "Loading SynOS Kernel v1.0..."\
    multiboot /boot/synos/synos-kernel-1.0\
}' "$GRUB_BUILDER"
    fi

    echo "✓ Builder GRUB template updated"
else
    echo "⚠ Builder GRUB not found"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    GRUB Branding Fixed!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Verification:"
echo ""

# Show updated entries
if [ -f "$GRUB_BUILDER" ]; then
    echo "GRUB entries now show:"
    grep "hostname=" "$GRUB_BUILDER" | head -3
    echo ""
    grep "menuentry" "$GRUB_BUILDER" | head -5
fi

echo ""
echo "✅ Next: Rebuild ISO with updated GRUB"
