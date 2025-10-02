#!/bin/bash

# SynOS V1.0 Custom initrd Builder
# Creates a minimal initial ramdisk for SynOS kernel

set -e

INITRD_DIR="core/initrd"
BUILD_DIR="build/initrd"
OUTPUT_FILE="build/synos-initrd.img"

echo "🛠️ SynOS V1.0 Custom initrd Builder"
echo "==================================="
echo "📅 $(date)"

# Create build directory
mkdir -p "${BUILD_DIR}"
rm -rf "${BUILD_DIR}"/*

echo "📁 Creating initrd directory structure..."

# Create essential directories
mkdir -p "${BUILD_DIR}"/{bin,sbin,etc,proc,sys,dev,tmp,var,lib,usr/bin,usr/sbin}

echo "🔧 Creating basic device nodes..."
# Create essential device nodes
mknod "${BUILD_DIR}/dev/console" c 5 1 2>/dev/null || echo "⚠️ mknod requires root - creating placeholder"
mknod "${BUILD_DIR}/dev/null" c 1 3 2>/dev/null || echo "⚠️ mknod requires root - creating placeholder"
mknod "${BUILD_DIR}/dev/zero" c 1 5 2>/dev/null || echo "⚠️ mknod requires root - creating placeholder"

# Create placeholder files if mknod failed
[ ! -c "${BUILD_DIR}/dev/console" ] && touch "${BUILD_DIR}/dev/console"
[ ! -c "${BUILD_DIR}/dev/null" ] && touch "${BUILD_DIR}/dev/null"
[ ! -c "${BUILD_DIR}/dev/zero" ] && touch "${BUILD_DIR}/dev/zero"

echo "📜 Creating init script..."
cat > "${BUILD_DIR}/init" << 'EOF'
#!/bin/sh
# SynOS V1.0 initrd init script

echo "🚀 SynOS V1.0 initrd starting..."
echo "================================"

# Mount essential filesystems
echo "📂 Mounting essential filesystems..."
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev

# Display system information
echo ""
echo "💻 System Information:"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo "Memory:"
if [ -f /proc/meminfo ]; then
    grep -E "(MemTotal|MemFree)" /proc/meminfo
else
    echo "  /proc/meminfo not available"
fi

echo ""
echo "🔧 SynOS V1.0 Services:"
echo "✓ initrd initialization complete"
echo "✓ Essential filesystems mounted"
echo "✓ Device nodes created"

# Check for SynOS kernel modules
echo ""
echo "🧠 AI Consciousness Engine Status:"
if [ -f /proc/modules ]; then
    if grep -q synos_consciousness /proc/modules; then
        echo "✅ Consciousness module loaded"
    else
        echo "⚠️ Consciousness module not loaded"
    fi
else
    echo "ℹ️ Module information not available"
fi

echo ""
echo "🎯 SynOS V1.0 Ready!"
echo "Dropping to emergency shell for development..."
echo "Type 'exit' to continue or 'poweroff' to shutdown"

# Basic shell for debugging
exec /bin/sh
EOF

chmod +x "${BUILD_DIR}/init"

echo "🛠️ Creating basic utilities..."

# Create a minimal shell script for essential commands
cat > "${BUILD_DIR}/bin/sh" << 'EOF'
#!/bin/sh
# Minimal shell for SynOS initrd
echo "SynOS Emergency Shell - Type 'help' for commands"
while true; do
    echo -n "synos> "
    read cmd args
    case "$cmd" in
        help)
            echo "Available commands:"
            echo "  ls       - list files"
            echo "  cat      - display file content"
            echo "  echo     - display text"
            echo "  pwd      - show current directory"
            echo "  cd       - change directory"
            echo "  mount    - mount filesystem"
            echo "  umount   - unmount filesystem"
            echo "  ps       - show processes"
            echo "  free     - show memory"
            echo "  exit     - exit shell"
            echo "  poweroff - shutdown system"
            ;;
        ls)
            ls $args
            ;;
        cat)
            cat $args
            ;;
        echo)
            echo $args
            ;;
        pwd)
            pwd
            ;;
        cd)
            cd $args 2>/dev/null || echo "cd: cannot change directory"
            ;;
        mount)
            mount $args
            ;;
        umount)
            umount $args
            ;;
        ps)
            ps $args 2>/dev/null || echo "ps: command not fully available"
            ;;
        free)
            free $args 2>/dev/null || grep -E "(MemTotal|MemFree)" /proc/meminfo 2>/dev/null || echo "free: memory info not available"
            ;;
        exit)
            echo "Exiting shell..."
            break
            ;;
        poweroff)
            echo "Shutting down SynOS..."
            poweroff
            ;;
        "")
            ;;
        *)
            echo "$cmd: command not found"
            ;;
    esac
done
EOF

chmod +x "${BUILD_DIR}/bin/sh"

# Create symlinks for common commands
ln -sf sh "${BUILD_DIR}/bin/ls"
ln -sf sh "${BUILD_DIR}/bin/cat"
ln -sf sh "${BUILD_DIR}/bin/echo"

echo "📄 Creating configuration files..."

# Create basic fstab
cat > "${BUILD_DIR}/etc/fstab" << 'EOF'
# SynOS V1.0 initrd fstab
proc /proc proc defaults 0 0
sysfs /sys sysfs defaults 0 0
devtmpfs /dev devtmpfs defaults 0 0
EOF

# Create basic passwd
cat > "${BUILD_DIR}/etc/passwd" << 'EOF'
root:x:0:0:SynOS Root:/root:/bin/sh
synos:x:1000:1000:SynOS User:/home/synos:/bin/sh
EOF

# Create version info
cat > "${BUILD_DIR}/etc/synos-release" << 'EOF'
SynOS V1.0
AI-Powered Cybersecurity Education Operating System
Build Date: $(date)
Kernel: Custom Multiboot
Architecture: x86_64
initrd: Custom
EOF

echo "📦 Creating initrd image..."

# Create the initrd image using cpio
cd "${BUILD_DIR}"
find . | cpio -o -H newc | gzip > "../synos-initrd.img"
cd - > /dev/null

echo ""
echo "✅ Custom initrd created successfully!"
echo "📁 Location: ${OUTPUT_FILE}"
echo "📊 Size: $(ls -lh "${OUTPUT_FILE}" | awk '{print $5}')"
echo ""

echo "🔍 initrd Contents:"
echo "=================="
cd "${BUILD_DIR}"
find . -type f -exec ls -la {} \; | head -20
cd - > /dev/null

echo ""
echo "🎯 Integration Instructions:"
echo "1. Update GRUB configuration to use this initrd"
echo "2. Test with: qemu-system-x86_64 -kernel kernel -initrd ${OUTPUT_FILE}"
echo "3. Verify init script execution and shell functionality"
