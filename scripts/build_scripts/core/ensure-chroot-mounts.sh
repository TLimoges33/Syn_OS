#!/bin/bash
# Ensure chroot mounts are properly established

CHROOT_DIR="$1"

if [ -z "$CHROOT_DIR" ] || [ ! -d "$CHROOT_DIR" ]; then
    echo "Error: Invalid chroot directory"
    exit 1
fi

echo "Setting up chroot mounts in: $CHROOT_DIR"

# Ensure mount points exist
mkdir -p "$CHROOT_DIR"/{proc,sys,dev/pts}

# Mount if not already mounted
if ! mountpoint -q "$CHROOT_DIR/proc"; then
    mount -t proc proc "$CHROOT_DIR/proc" && echo "✓ Mounted /proc"
fi

if ! mountpoint -q "$CHROOT_DIR/sys"; then
    mount -t sysfs sys "$CHROOT_DIR/sys" && echo "✓ Mounted /sys"
fi

if ! mountpoint -q "$CHROOT_DIR/dev"; then
    mount -o bind /dev "$CHROOT_DIR/dev" && echo "✓ Mounted /dev"
fi

if ! mountpoint -q "$CHROOT_DIR/dev/pts"; then
    mount -t devpts devpts "$CHROOT_DIR/dev/pts" && echo "✓ Mounted /dev/pts"
fi

echo "✓ All chroot mounts verified"
