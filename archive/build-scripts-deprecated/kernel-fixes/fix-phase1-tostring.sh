#!/bin/bash
#
# Fix missing ToString trait imports across the kernel
#

set -e

KERNEL_SRC="/home/diablorain/Syn_OS/src/kernel/src"
cd "$KERNEL_SRC"

echo "🔧 Phase 1: Fixing ToString trait imports..."
echo ""

# Function to add ToString import to a file if not present
add_tostring_import() {
    local file="$1"
    
    if ! grep -q "use alloc::string::ToString" "$file" 2>/dev/null; then
        # Check if file has alloc imports
        if grep -q "^use alloc::" "$file"; then
            # Add to existing alloc imports
            sed -i '/^use alloc::/a use alloc::string::ToString;' "$file"
            echo "   ✓ Added ToString to $file"
        elif grep -q "^use " "$file"; then
            # Add after first use statement
            sed -i '0,/^use /s//use alloc::string::ToString;\nuse /' "$file"
            echo "   ✓ Added ToString to $file"
        else
            # Add at top of file after comments
            sed -i '1i use alloc::string::ToString;' "$file"
            echo "   ✓ Added ToString to $file"
        fi
    fi
}

# Files that need ToString based on error analysis
FILES_NEEDING_TOSTRING=(
    "education/hud_tutorial_engine.rs"
    "education/hud_command_interface.rs"
    "education/cybersecurity_tutorial_content.rs"
    "security/security_panic.rs"
    "io/vga_buffer.rs"
)

echo "Adding ToString imports to files..."
for file in "${FILES_NEEDING_TOSTRING[@]}"; do
    if [ -f "$file" ]; then
        add_tostring_import "$file"
    fi
done

echo ""
echo "✅ Phase 1 complete: ToString trait imports added"
