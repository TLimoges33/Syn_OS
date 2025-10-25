#!/bin/bash
# Bind mount package repository into chroot

REPO_SRC="/home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder/packages"
REPO_DST="chroot/tmp/synos-repo"

if [ -d "chroot" ] && [ -d "$REPO_SRC" ]; then
    mkdir -p "$REPO_DST"

    # Copy packages instead of bind mount (more reliable)
    cp -av "$REPO_SRC"/* "$REPO_DST/" 2>/dev/null || true

    echo "✓ Repository copied to chroot"
fi
