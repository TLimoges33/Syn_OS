#!/bin/bash
#
# SynOS Kernel Unwrap Migration Script
# Systematically migrate unwrap() calls to Result-based error handling
#

set -e

KERNEL_SRC="src/kernel/src"
LOG_FILE="unwrap_migration.log"
BACKUP_DIR="backup_unwrap_migration"

echo "🔧 SynOS Kernel Unwrap() Migration Tool"
echo "========================================"
echo ""

# Create backup
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -r "$KERNEL_SRC" "$BACKUP_DIR/"
echo "✓ Backup created in $BACKUP_DIR/"
echo ""

# Audit current unwrap() usage
echo "🔍 Auditing current unwrap() usage..."
echo "Unwrap() Audit Report - $(date)" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Count unwrap() by file
echo "Files with unwrap() calls:" >> "$LOG_FILE"
rg "\.unwrap\(\)" "$KERNEL_SRC" --count-matches >> "$LOG_FILE" 2>&1 || true
echo "" >> "$LOG_FILE"

# Get total count
TOTAL_UNWRAPS=$(rg "\.unwrap\(\)" "$KERNEL_SRC" --count-matches 2>/dev/null | awk -F: '{sum+=$2} END {print sum}')
echo "Total unwrap() calls found: $TOTAL_UNWRAPS"
echo "Total unwrap() calls: $TOTAL_UNWRAPS" >> "$LOG_FILE"
echo ""

# List all unwrap() occurrences with context
echo "" >> "$LOG_FILE"
echo "Detailed occurrences:" >> "$LOG_FILE"
echo "--------------------" >> "$LOG_FILE"
rg "\.unwrap\(\)" "$KERNEL_SRC" --line-number --context 2 >> "$LOG_FILE" 2>&1 || true

echo "✓ Audit complete. See $LOG_FILE for details."
echo ""

# Show high-priority files
echo "📊 Files with most unwrap() calls:"
rg "\.unwrap\(\)" "$KERNEL_SRC" --count-matches 2>/dev/null | sort -t: -k2 -rn | head -10
echo ""

# Provide migration guidance
cat << 'EOF'
📝 Migration Strategy:

1. Review unwrap_migration.log to understand all unwrap() usage
2. For each file, replace unwrap() with proper error handling:

   BEFORE:
   let value = some_option.unwrap();

   AFTER (Option):
   let value = some_option.ok_or(KernelError::InvalidParameter)?;

   AFTER (Result):
   let value = some_result?;

3. Use the new error types from src/kernel/src/error.rs:
   - KernelError::OutOfMemory
   - KernelError::ProcessNotFound(id)
   - KernelError::InvalidParameter
   - ... (see error.rs for full list)

4. Update function signatures to return KernelResult<T>:
   fn example() -> KernelResult<Value> {
       // your code with ? operator
   }

5. For critical sections that MUST succeed, use kernel_assert!:
   kernel_assert!(condition, "Critical invariant violated");

📂 Suggested Migration Order (by priority):

1. High Priority (kernel stability):
   - src/kernel/src/memory/*.rs
   - src/kernel/src/process/*.rs
   - src/kernel/src/interrupts.rs

2. Medium Priority (functionality):
   - src/kernel/src/network/*.rs
   - src/kernel/src/ipc/*.rs
   - src/kernel/src/filesystem/*.rs

3. Low Priority (features):
   - src/kernel/src/container/*.rs
   - src/kernel/src/security/realtime/*.rs

🔍 Validation After Migration:

# Check remaining unwrap() calls
rg "\.unwrap\(\)" src/kernel/src --count-matches

# Build and test
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
cargo test --manifest-path=src/kernel/Cargo.toml

✅ Target: 0 unwrap() calls before v1.0 release

EOF

echo ""
echo "💡 To restore from backup if needed:"
echo "   rm -rf $KERNEL_SRC && cp -r $BACKUP_DIR/src ."
echo ""
