#!/bin/bash
#
# Kernel Source Reorganization Script
# Moves flat kernel source files into organized module directories
#

set -e  # Exit on error

KERNEL_SRC="/home/diablorain/Syn_OS/src/kernel/src"
cd "$KERNEL_SRC"

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║         SYNOS KERNEL SOURCE REORGANIZATION                           ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Working directory: $KERNEL_SRC"
echo ""

# First, clean up compiler artifact files (0-byte files with line numbers)
echo "📁 Step 1: Cleaning up compiler artifacts..."
find . -maxdepth 1 -type f -size 0 -name "*.rs:*" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -size 0 -name "*.rs:*:*" -delete 2>/dev/null || true
CLEANED=$(find . -maxdepth 1 -type f -size 0 | wc -l)
if [ "$CLEANED" -gt 0 ]; then
    echo "   ✓ Cleaned $CLEANED empty artifact files"
else
    echo "   ✓ No artifacts to clean"
fi
echo ""

# Check what directories already exist
echo "📁 Step 2: Checking existing module directories..."
EXISTING_DIRS=$(find . -maxdepth 1 -type d | grep -v "^\.$" | wc -l)
echo "   ✓ Found $EXISTING_DIRS existing directories"
ls -d */ 2>/dev/null | sed 's|^|     - |' || echo "     (none)"
echo ""

# Create missing directories
echo "📁 Step 3: Creating new module directories..."
DIRS_TO_CREATE=(
    "io"
    "utils"
    "phase5"
    "phase6"
    "legacy"
)

for dir in "${DIRS_TO_CREATE[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "   ✓ Created $dir/"
    else
        echo "   • $dir/ already exists"
    fi
done
echo ""

# Function to move file safely
move_file() {
    local src="$1"
    local dest_dir="$2"
    local dest_name="${3:-$(basename "$src")}"

    if [ -f "$src" ]; then
        if [ -f "$dest_dir/$dest_name" ]; then
            echo "   ⚠️  $dest_dir/$dest_name already exists, skipping $src"
        else
            mv "$src" "$dest_dir/$dest_name"
            echo "   ✓ $src → $dest_dir/$dest_name"
        fi
    fi
}

# Move files to appropriate directories
echo "📦 Step 4: Moving files to module directories..."
echo ""

echo "   [I/O Files]"
move_file "serial.rs" "io"
move_file "serial_logger.rs" "io"
move_file "vga_buffer.rs" "io"
echo ""

echo "   [Memory Files]"
move_file "allocator.rs" "memory"
move_file "heap.rs" "memory"
move_file "paging.rs" "memory"
move_file "frame.rs" "memory"
move_file "guard.rs" "memory"
move_file "tests.rs" "memory"
echo ""

echo "   [Security Files]"
move_file "threat_detection.rs" "security"
move_file "verification.rs" "security"
move_file "stack_protection.rs" "security"
move_file "security_panic.rs" "security"
move_file "memory_corruption.rs" "security"
move_file "pqc.rs" "security"
echo ""

echo "   [Interrupt Files]"
move_file "interrupts.rs" "interrupts"
move_file "gdt.rs" "interrupts"
move_file "interrupt_security.rs" "interrupts"
echo ""

echo "   [Process Files]"
move_file "scheduler.rs" "process"
move_file "process_execution.rs" "process" "execution.rs"
move_file "process_lifecycle.rs" "process" "lifecycle.rs"
move_file "signals.rs" "process"
echo ""

echo "   [AI Files]"
move_file "ai_interface.rs" "ai" "interface.rs"
move_file "ai_bridge.rs" "ai" "bridge.rs"
echo ""

echo "   [Network Files]"
move_file "networking.rs" "network" "stack.rs"
echo ""

echo "   [Filesystem Files]"
move_file "filesystem.rs" "fs"
echo ""

echo "   [IPC Files]"
move_file "ipc_advanced.rs" "ipc" "advanced.rs"
echo ""

echo "   [Syscall Files]"
move_file "syscall_optimization.rs" "syscalls" "optimization.rs"
echo ""

echo "   [Utility Files]"
move_file "time.rs" "utils"
move_file "time_utils.rs" "utils"
move_file "log.rs" "utils"
move_file "debug.rs" "utils"
move_file "cpu.rs" "utils"
move_file "system.rs" "utils"
echo ""

echo "   [Testing Files]"
move_file "kernel_tests.rs" "testing"
move_file "test_main.rs" "testing"
move_file "minimal_test.rs" "testing"
move_file "hardening_tests.rs" "testing"
echo ""

echo "   [Education Files]"
move_file "hud_tutorial_engine.rs" "education"
move_file "hud_command_interface.rs" "education"
move_file "cybersecurity_tutorial_content.rs" "education"
move_file "education_platform_minimal.rs" "education" "platform_minimal.rs"
move_file "advanced_applications_minimal.rs" "education"
echo ""

echo "   [Phase 5 Files]"
move_file "phase5_integration.rs" "phase5" "integration.rs"
move_file "phase5_testing.rs" "phase5" "testing.rs"
echo ""

echo "   [Phase 6 Files]"
move_file "phase6_integration.rs" "phase6" "integration.rs"
echo ""

echo "   [ELF & Userspace Files]"
move_file "elf_loader.rs" "process"
move_file "userspace_integration.rs" "process"
echo ""

echo "   [Legacy Files]"
move_file "main_minimal.rs" "legacy"
if [ -f "mod.rs" ] && [ $(wc -l < "mod.rs") -lt 100 ]; then
    # Only move mod.rs if it's small (likely old consciousness or legacy)
    move_file "mod.rs" "legacy"
fi
echo ""

# Create mod.rs files for directories that need them
echo "📝 Step 5: Creating/updating mod.rs files..."

create_mod_rs() {
    local dir="$1"
    local content="$2"

    if [ ! -f "$dir/mod.rs" ]; then
        echo "$content" > "$dir/mod.rs"
        echo "   ✓ Created $dir/mod.rs"
    else
        echo "   • $dir/mod.rs already exists"
    fi
}

# IO module
create_mod_rs "io" "// I/O subsystem
pub mod serial;
pub mod vga_buffer;

#[cfg(feature = \"serial_logging\")]
pub mod serial_logger;
"

# Utils module
create_mod_rs "utils" "// Kernel utilities
pub mod time;
pub mod time_utils;
pub mod debug;
pub mod cpu;
pub mod system;

#[cfg(feature = \"logging\")]
pub mod log;
"

# Phase5 module
create_mod_rs "phase5" "// Phase 5 Integration
pub mod integration;

#[cfg(test)]
pub mod testing;
"

# Phase6 module
create_mod_rs "phase6" "// Phase 6 Integration
pub mod integration;
"

# Legacy module
create_mod_rs "legacy" "// Legacy and deprecated code
// Maintained for backward compatibility

#[cfg(feature = \"minimal_kernel\")]
pub mod main_minimal;
"

echo ""

# Count files in root vs modules
echo "📊 Step 6: Reorganization Statistics"
ROOT_RS=$(find . -maxdepth 1 -name "*.rs" -type f | wc -l)
ROOT_ASM=$(find . -maxdepth 1 -name "*.asm" -type f | wc -l)
TOTAL_ROOT=$((ROOT_RS + ROOT_ASM))
ALL_RS=$(find . -name "*.rs" -type f | wc -l)

echo "   Files remaining in src/: $TOTAL_ROOT ($ROOT_RS .rs, $ROOT_ASM .asm)"
echo "   Total .rs files in tree: $ALL_RS"
echo "   Module directories: $(find . -maxdepth 1 -type d | grep -v "^\.$" | wc -l)"
echo ""

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    REORGANIZATION COMPLETE                           ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Update lib.rs module declarations"
echo "  2. cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none"
echo "  3. Fix any module path errors"
echo ""
