#!/bin/bash
#
# Quick fixes for kernel module reorganization issues
#

set -e

KERNEL_SRC="/home/diablorain/Syn_OS/src/kernel/src"
cd "$KERNEL_SRC"

echo "🔧 Applying quick fixes to kernel modules..."
echo ""

# Fix 1: Remove duplicate ai_dpi in network/mod.rs
echo "1. Fixing duplicate ai_dpi in network/mod.rs..."
sed -i '/^pub mod ai_dpi;$/d' network/mod.rs
echo "pub mod ai_dpi;" >> network/mod.rs
echo "   ✓ Fixed"

# Fix 2: Comment out broken ai::bridge calls (these modules don't have those functions)
echo "2. Commenting out unavailable ai::bridge calls..."
sed -i 's/crate::ai::bridge::init();/\/\/ crate::ai::bridge::init(); \/\/ TODO: implement/g' memory/init.rs memory/manager.rs
sed -i 's/crate::ai::bridge::is_initialized()/false \/\/ crate::ai::bridge::is_initialized() TODO/g' memory/init.rs
sed -i 's/crate::ai::bridge::get_bridge()/None::<()> \/\/ crate::ai::bridge::get_bridge() TODO/g' memory/virtual_memory.rs
echo "   ✓ Fixed"

# Fix 3: Fix InterruptManager import in process/real_process_manager.rs
echo "3. Fixing InterruptManager import..."
sed -i 's/use crate::interrupts::InterruptManager;/use crate::interrupts::manager::InterruptManager;/g' process/real_process_manager.rs
echo "   ✓ Fixed"

# Fix 4: Fix init_interrupts call in boot/mod.rs
echo "4. Fixing init_interrupts call..."
sed -i 's/crate::interrupts::init_interrupts()?;/crate::interrupts::interrupts::init_interrupts()?;/g' boot/mod.rs
echo "   ✓ Fixed"

# Fix 5: Remove GDT export from interrupts/mod.rs (it's private)
echo "5. Removing private GDT export..."
sed -i 's/pub use gdt::{init as init_gdt, GDT};/pub use gdt::{init as init_gdt};/g' interrupts/mod.rs
echo "   ✓ Fixed"

# Fix 6: Comment out missing memory functions in security_panic.rs
echo "6. Commenting out missing memory functions..."
sed -i 's/crate::memory::get_heap_status()/None \/\/ crate::memory::get_heap_status() TODO/g' security/security_panic.rs
sed -i 's/crate::memory::get_kernel_stack_base()/0 \/\/ crate::memory::get_kernel_stack_base() TODO/g' security/security_panic.rs
sed -i 's/crate::memory::get_kernel_stack_size()/0 \/\/ crate::memory::get_kernel_stack_size() TODO/g' security/security_panic.rs
echo "   ✓ Fixed"

# Fix 7: Fix time function call
echo "7. Fixing time function call..."
sed -i 's/crate::time::get_timestamp()/crate::utils::time::get_time_ms()/g' security/security_panic.rs
echo "   ✓ Fixed"

# Fix 8: Fix update_used_memory in heap.rs
echo "8. Commenting out update_used_memory..."
sed -i 's/update_used_memory(size);/\/\/ update_used_memory(size); \/\/ TODO: implement/g' memory/heap.rs
sed -i '/^use crate::memory::update_used_memory;$/d' memory/heap.rs
echo "   ✓ Fixed"

# Fix 9: Fix ALLOCATOR references in heap.rs
echo "9. Fixing ALLOCATOR references..."
sed -i 's/allocator::ALLOCATOR/crate::memory::allocator::ALLOCATOR/g' memory/heap.rs
echo "   ✓ Fixed"

# Fix 10: Comment out print! macros in phase6
echo "10. Adding use crate::print to phase6/integration.rs..."
if ! grep -q "use crate::print" phase6/integration.rs; then
    sed -i '1i use crate::{print, println};' phase6/integration.rs
fi
echo "   ✓ Fixed"

echo ""
echo "✅ All quick fixes applied!"
echo ""
echo "Remaining issues to address manually:"
echo "  - Missing types in hud_tutorial_engine.rs (NmapTutorials, SIEMTutorials, etc.)"
echo "  - Missing ProcessMemoryLayout, ElfResult in process/execution.rs"
echo "  - Missing PQCAlgorithm, PQCKeyPair in security/pqc.rs"
echo ""
