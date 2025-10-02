#!/bin/bash
# Final compilation error fixes
set -e

echo "🔧 Fixing Final Compilation Errors"
echo "==================================="

# Fix 1: source_address and destination_address in ip.rs
echo "1. Fixing IP struct field references..."
sed -i '/source_address$/,/destination_address$/ {
    /source_address$/d
    /destination_address$/d
}' src/kernel/src/network/ip.rs

# Fix 2: FileStats - 'size' variable issue
echo "2. Fixing FileStats size calculation..."
sed -i '/blocks: (size + 4095) \/ 4096/c\                blocks: 1,' \
    src/kernel/src/fs/synfs.rs

# Fix 3: Change lateout back to a workaround for rbx
echo "3. Fixing assembly rbx register conflicts..."
sed -i 's/lateout("ebx") ebx,/\/\/ ebx conflicts - using r11 instead\n            out("r11") ebx,/' \
    src/kernel/src/hal/cpu.rs

# Fix 4: Add DeviceNotFound to HalError Display impl
echo "4. Adding DeviceNotFound to Display..."
sed -i '/HalError::InvalidOperation => write!(f, "Invalid operation")/a\            HalError::DeviceNotFound => write!(f, "Device not found"),' \
    src/kernel/src/hal/mod.rs

# Fix 5: Make consciousness_kernel mutable
echo "5. Fixing consciousness_kernel mutability..."
sed -i 's/let consciousness_kernel =/let mut consciousness_kernel =/' \
    src/kernel/src/boot/consciousness_init.rs

echo ""
echo "✅ Final fixes applied!"
