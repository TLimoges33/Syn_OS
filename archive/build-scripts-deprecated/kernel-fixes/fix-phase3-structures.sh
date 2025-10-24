#!/bin/bash

set -e

KERNEL_SRC="/home/diablorain/Syn_OS/src/kernel/src"

echo "🔧 Phase 3: Fixing structural issues..."
echo ""

# Phase 3a: Fix tutorial_library visibility (4 errors)
echo "Phase 3a: Making tutorial_library public..."
sed -i 's/tutorial_library: TutorialLibrary,/pub tutorial_library: TutorialLibrary,/g' \
    "$KERNEL_SRC/education/hud_tutorial_engine.rs"
echo "   ✓ Made tutorial_library public"
echo ""

# Phase 3b: Add missing struct fields (3 errors)
echo "Phase 3b: Adding missing struct fields..."

# Add virt_addr to MemorySegment
FILE="$KERNEL_SRC/process/elf_loader.rs"
if grep -q "pub struct MemorySegment" "$FILE"; then
    # Check if virt_addr already exists
    if ! grep -A 10 "pub struct MemorySegment" "$FILE" | grep -q "pub virt_addr"; then
        # Find the struct and add the field
        sed -i '/pub struct MemorySegment {/,/^}/ {
            /pub struct MemorySegment {/a\    pub virt_addr: u64,
        }' "$FILE"
        echo "   ✓ Added virt_addr to MemorySegment"
    else
        echo "   ℹ virt_addr already exists in MemorySegment"
    fi
fi

# Add entry_point to ProcessMemoryLayout
if grep -q "pub struct ProcessMemoryLayout" "$FILE"; then
    if ! grep -A 15 "pub struct ProcessMemoryLayout" "$FILE" | grep -q "pub entry_point"; then
        sed -i '/pub struct ProcessMemoryLayout {/,/^}/ {
            /pub struct ProcessMemoryLayout {/a\    pub entry_point: u64,
        }' "$FILE"
        echo "   ✓ Added entry_point to ProcessMemoryLayout"
    else
        echo "   ℹ entry_point already exists in ProcessMemoryLayout"
    fi
fi
echo ""

# Phase 3c: Add StepValidation::CommandOutput variant (2 errors)
echo "Phase 3c: Adding StepValidation::CommandOutput..."
FILE="$KERNEL_SRC/education/hud_tutorial_engine.rs"
if grep -q "pub enum StepValidation" "$FILE"; then
    if ! grep -A 10 "pub enum StepValidation" "$FILE" | grep -q "CommandOutput"; then
        # Add CommandOutput variant to the enum
        sed -i '/pub enum StepValidation {/,/^}/ {
            /pub enum StepValidation {/a\    CommandOutput { expected: String, actual: String },
        }' "$FILE"
        echo "   ✓ Added CommandOutput variant to StepValidation"
    else
        echo "   ℹ CommandOutput already exists in StepValidation"
    fi
fi
echo ""

echo "✅ Phase 3 complete: Structural issues fixed"
echo ""
echo "Expected fixes:"
echo "  - 4 errors: tutorial_library visibility"
echo "  - 2 errors: virt_addr field"
echo "  - 1 error:  entry_point field"
echo "  - 2 errors: CommandOutput variant"
echo "  Total: 9 errors should be resolved"
