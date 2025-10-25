#!/bin/bash
# Fix locale issues in chroot environment

CHROOT_DIR="$1"

if [ -z "$CHROOT_DIR" ] || [ ! -d "$CHROOT_DIR" ]; then
    echo "Error: Invalid chroot directory"
    exit 1
fi

echo "Fixing locales in: $CHROOT_DIR"

# Generate locale
cat > "$CHROOT_DIR/etc/locale.gen" << EOF
en_US.UTF-8 UTF-8
C.UTF-8 UTF-8
EOF

# Set default locale
cat > "$CHROOT_DIR/etc/default/locale" << EOF
LANG=en_US.UTF-8
LC_ALL=en_US.UTF-8
LANGUAGE=en_US.UTF-8
EOF

# Generate locales in chroot
if [ -d "$CHROOT_DIR/proc" ] && mountpoint -q "$CHROOT_DIR/proc"; then
    chroot "$CHROOT_DIR" locale-gen en_US.UTF-8 2>/dev/null || echo "Note: locale-gen may need installation"
else
    echo "Warning: /proc not mounted, skipping locale-gen"
fi

echo "✓ Locale configuration updated"
