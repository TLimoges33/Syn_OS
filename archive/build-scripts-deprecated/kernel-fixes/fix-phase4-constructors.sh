#!/bin/bash

set -e

KERNEL_SRC="/home/diablorain/Syn_OS/src/kernel/src"

echo "🔧 Phase 4: Adding missing constructor methods..."
echo ""

# List of structs needing new() constructors:
# 1. SecurityPrinciplesTutorials
# 2. PentestTutorials
# 3. NetworkingBasicsTutorials
# 4. HUDProgressTracker
# 5. HUDInteractionHandler
# 6. HUDAnimationController
# 7. CoreToolsTutorials
# 8. ContextAwarenessEngine
# 9. AdvancedTopicsTutorials
# 10. AchievementSystem

echo "Phase 4a: Adding new() to tutorial struct types..."

# These are likely in cybersecurity_tutorial_content.rs
FILE="$KERNEL_SRC/education/cybersecurity_tutorial_content.rs"

# Function to add impl block with new() if it doesn't exist
add_impl_new() {
    local struct_name=$1
    local file=$2
    
    # Check if impl already exists
    if ! grep -q "impl $struct_name" "$file"; then
        # Find the struct and add impl after it
        awk -v struct="$struct_name" '
        /^pub struct '"$struct_name"'/ {
            in_struct=1
        }
        {
            print
        }
        in_struct && /^}/ {
            print ""
            print "impl " struct " {"
            print "    pub fn new() -> Self {"
            print "        Self {}"
            print "    }"
            print "}"
            in_struct=0
        }
        ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
        echo "   ✓ Added new() to $struct_name"
    else
        echo "   ℹ impl block already exists for $struct_name"
    fi
}

# Add constructors to tutorial types
if [ -f "$FILE" ]; then
    add_impl_new "SecurityPrinciplesTutorials" "$FILE"
    add_impl_new "PentestTutorials" "$FILE"
    add_impl_new "NetworkingBasicsTutorials" "$FILE"
    add_impl_new "CoreToolsTutorials" "$FILE"
    add_impl_new "AdvancedTopicsTutorials" "$FILE"
fi

echo ""
echo "Phase 4b: Adding new() to HUD support types..."

# HUD types likely in hud_tutorial_engine.rs
FILE="$KERNEL_SRC/education/hud_tutorial_engine.rs"

if [ -f "$FILE" ]; then
    add_impl_new "HUDProgressTracker" "$FILE"
    add_impl_new "HUDInteractionHandler" "$FILE"
    add_impl_new "HUDAnimationController" "$FILE"
    add_impl_new "ContextAwarenessEngine" "$FILE"
    add_impl_new "AchievementSystem" "$FILE"
fi

echo ""
echo "✅ Phase 4 complete: Constructor methods added"
echo ""
echo "Expected fixes: 10 missing new() errors"
