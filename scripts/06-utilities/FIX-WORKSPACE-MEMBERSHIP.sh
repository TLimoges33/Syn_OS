#!/bin/bash
# Fix Workspace Membership Issues
# Adds missing packages to workspace or excludes them

set -e

WORKSPACE_DIR="/home/diablorain/Syn_OS"
CARGO_TOML="$WORKSPACE_DIR/Cargo.toml"

echo "════════════════════════════════════════════════════════════"
echo "  Fixing Workspace Membership Issues"
echo "════════════════════════════════════════════════════════════"

# Backup Cargo.toml
echo "📋 Backing up Cargo.toml..."
cp "$CARGO_TOML" "$CARGO_TOML.backup-$(date +%Y%m%d-%H%M%S)"

# Check if members array exists
if ! grep -q "^members = \[" "$CARGO_TOML"; then
    echo "❌ No members array found in Cargo.toml"
    exit 1
fi

# Add src/userspace/libc if not present
if grep -q '"src/userspace/libc"' "$CARGO_TOML"; then
    echo "✓ src/userspace/libc already in workspace"
else
    echo "➕ Adding src/userspace/libc to workspace..."
    # Insert before the closing bracket of members array
    sed -i '/^members = \[/,/^\]/ {
        /^\]/i\    "src/userspace/libc",
    }' "$CARGO_TOML"
    echo "✓ Added src/userspace/libc"
fi

# Add src/tools/dev-utils if not present
if grep -q '"src/tools/dev-utils"' "$CARGO_TOML"; then
    echo "✓ src/tools/dev-utils already in workspace"
else
    echo "➕ Adding src/tools/dev-utils to workspace..."
    sed -i '/^members = \[/,/^\]/ {
        /^\]/i\    "src/tools/dev-utils",
    }' "$CARGO_TOML"
    echo "✓ Added src/tools/dev-utils"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Workspace Fix Complete"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Changes made:"
echo "  • Added src/userspace/libc to workspace.members"
echo "  • Added src/tools/dev-utils to workspace.members"
echo ""
echo "Backup saved to: $CARGO_TOML.backup-*"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff Cargo.toml"
echo "  2. Test build: cargo build --workspace"
echo "  3. Commit: git add Cargo.toml && git commit -m 'Fix workspace membership'"
echo ""
