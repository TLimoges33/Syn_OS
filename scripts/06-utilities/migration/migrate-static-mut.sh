#!/bin/bash
#
# SynOS Kernel Static Mut Migration Script
# Migrate unsafe static mut to thread-safe Mutex/RwLock patterns
#

set -e

KERNEL_SRC="src/kernel/src"
LOG_FILE="static_mut_migration.log"
BACKUP_DIR="backup_static_mut_migration"

echo "🔒 SynOS Kernel Static Mut Migration Tool"
echo "=========================================="
echo ""

# Create backup
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -r "$KERNEL_SRC" "$BACKUP_DIR/"
echo "✓ Backup created in $BACKUP_DIR/"
echo ""

# Audit current static mut usage
echo "🔍 Auditing current static mut usage..."
echo "Static Mut Audit Report - $(date)" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Count static mut by file
echo "Files with static mut patterns:" >> "$LOG_FILE"
rg "static mut" "$KERNEL_SRC" --count-matches >> "$LOG_FILE" 2>&1 || true
echo "" >> "$LOG_FILE"

# Get total count
TOTAL_STATIC_MUT=$(rg "static mut" "$KERNEL_SRC" --count-matches 2>/dev/null | awk -F: '{sum+=$2} END {print sum}')
echo "Total static mut patterns found: $TOTAL_STATIC_MUT"
echo "Total static mut patterns: $TOTAL_STATIC_MUT" >> "$LOG_FILE"
echo ""

# List all static mut occurrences with context
echo "" >> "$LOG_FILE"
echo "Detailed occurrences:" >> "$LOG_FILE"
echo "--------------------" >> "$LOG_FILE"
rg "static mut" "$KERNEL_SRC" --line-number --context 2 >> "$LOG_FILE" 2>&1 || true

echo "✓ Audit complete. See $LOG_FILE for details."
echo ""

# Show high-priority files
echo "📊 Files with most static mut patterns:"
rg "static mut" "$KERNEL_SRC" --count-matches 2>/dev/null | sort -t: -k2 -rn | head -10
echo ""

# Categorize static mut by type
echo "📋 Categorizing static mut patterns..."
echo ""
echo "1. Global Singletons (use Mutex/RwLock):"
rg "static mut.*Option<" "$KERNEL_SRC" --no-filename | head -5
echo "   ... ($(rg "static mut.*Option<" "$KERNEL_SRC" --count-matches | awk -F: '{sum+=$2} END {print sum}') total)"
echo ""

echo "2. Static Buffers (use safe alternatives):"
rg "static mut.*\[" "$KERNEL_SRC" --no-filename | head -3
echo "   ... ($(rg "static mut.*\[" "$KERNEL_SRC" --count-matches | awk -F: '{sum+=$2} END {print sum}') total)"
echo ""

echo "3. Function Parameters (already safe):"
rg "boot_info: &'static mut" "$KERNEL_SRC" --no-filename | head -2
echo "   ... (these are fine - bootloader-provided)"
echo ""

# Provide migration guidance
cat << 'EOF'
📝 Migration Strategy:

====================
1. GLOBAL SINGLETONS
====================

BEFORE (unsafe):
```rust
static mut MANAGER: Option<Manager> = None;

pub fn get_manager() -> &'static mut Manager {
    unsafe {
        MANAGER.as_mut().unwrap()
    }
}
```

AFTER (safe with Mutex):
```rust
use spin::Mutex;

static MANAGER: Mutex<Option<Manager>> = Mutex::new(None);

pub fn get_manager() -> &'static Mutex<Option<Manager>> {
    &MANAGER  // Caller locks when needed
}

// Or with helper:
pub fn with_manager<F, R>(f: F) -> R
where
    F: FnOnce(&mut Manager) -> R,
{
    let mut guard = MANAGER.lock();
    f(guard.as_mut().expect("Manager not initialized"))
}
```

AFTER (safe with RwLock for read-heavy):
```rust
use spin::RwLock;

static MANAGER: RwLock<Option<Manager>> = RwLock::new(None);

pub fn read_manager<F, R>(f: F) -> R
where
    F: FnOnce(&Manager) -> R,
{
    let guard = MANAGER.read();
    f(guard.as_ref().expect("Manager not initialized"))
}
```

====================
2. STATIC BUFFERS
====================

BEFORE (unsafe):
```rust
static mut BUFFER: [u8; 1024] = [0; 1024];
```

AFTER (safe):
```rust
use spin::Mutex;

static BUFFER: Mutex<[u8; 1024]> = Mutex::new([0; 1024]);
```

====================
3. BOOT INFO (SAFE)
====================

These are fine - don't change:
```rust
fn kernel_main(boot_info: &'static mut BootInfo) -> ! {
    // This is safe - provided by bootloader
}
```

====================
4. LAZY_STATIC (IDEAL)
====================

For complex initialization:
```rust
use lazy_static::lazy_static;
use spin::Mutex;

lazy_static! {
    static ref MANAGER: Mutex<Manager> = Mutex::new(Manager::new());
}
```

📂 Migration Priority:

HIGH PRIORITY (critical for thread safety):
1. src/kernel/src/hal/minimal_hal.rs - HARDWARE_ABSTRACTION_LAYER
2. src/kernel/src/process/mod.rs - PROCESS_MANAGER
3. src/kernel/src/devices/mod.rs - DEVICE_MANAGER
4. src/kernel/src/security/*.rs - Security subsystems

MEDIUM PRIORITY:
5. src/kernel/src/process/context_switch.rs - CONTEXT_SWITCHERS
6. src/kernel/src/hal/ai_accelerator_registry.rs - AI_ACCELERATOR_REGISTRY

LOW PRIORITY (internal buffers):
7. src/kernel/src/heap.rs - _heap_start, _heap_size (linker symbols, OK)
8. src/kernel/src/gdt.rs - STACK (one-time use, OK)

SKIP (already safe):
9. Boot info parameters (&'static mut BootInfo)
10. Linker-provided symbols

🔍 Validation After Migration:

# Check remaining unsafe static mut
rg "static mut" src/kernel/src --count-matches

# Exclude safe patterns
rg "static mut" src/kernel/src | \
  grep -v "boot_info: &'static mut" | \
  grep -v "_heap_" | \
  wc -l

# Build and test
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
cargo test --manifest-path=src/kernel/Cargo.toml

✅ Target: <10 static mut (only linker symbols and boot params)

EOF

echo ""
echo "💡 To restore from backup if needed:"
echo "   rm -rf $KERNEL_SRC && cp -r $BACKUP_DIR/src ."
echo ""
