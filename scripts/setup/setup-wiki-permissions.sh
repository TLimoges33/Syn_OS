#!/bin/bash
# SynOS Wiki Security - File Permissions Setup
# This script sets proper Unix permissions for the 3-tier wiki structure

set -e  # Exit on error

echo "🔐 SynOS Wiki Security - Setting File Permissions"
echo "=================================================="
echo ""

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    SUDO=""
    echo "✅ Running as root"
else
    SUDO="sudo"
    echo "⚠️  Running with sudo (will prompt for password)"
fi

WIKI_DIR="/home/diablorain/Syn_OS/wiki"

# Check if wiki directory exists
if [ ! -d "$WIKI_DIR" ]; then
    echo "❌ ERROR: Wiki directory not found: $WIKI_DIR"
    exit 1
fi

echo ""
echo "📂 Wiki Directory: $WIKI_DIR"
echo ""

# ===========================================
# STEP 1: Create Security Groups
# ===========================================
echo "1️⃣  Creating security groups..."

# Create synos-internal group (for employees)
if ! getent group synos-internal > /dev/null 2>&1; then
    $SUDO groupadd synos-internal
    echo "   ✅ Created group: synos-internal (employees)"
else
    echo "   ℹ️  Group already exists: synos-internal"
fi

# Create synos-licensed group (for paying customers)
if ! getent group synos-licensed > /dev/null 2>&1; then
    $SUDO groupadd synos-licensed
    echo "   ✅ Created group: synos-licensed (licensed users)"
else
    echo "   ℹ️  Group already exists: synos-licensed"
fi

# Create synos-public group (for public access)
if ! getent group synos-public > /dev/null 2>&1; then
    $SUDO groupadd synos-public
    echo "   ✅ Created group: synos-public (everyone)"
else
    echo "   ℹ️  Group already exists: synos-public"
fi

echo ""

# ===========================================
# STEP 2: Add Current User to Groups
# ===========================================
echo "2️⃣  Adding current user to groups..."

CURRENT_USER=$(whoami)

# Add to internal (for development/testing)
if ! groups "$CURRENT_USER" | grep -q "synos-internal"; then
    $SUDO usermod -aG synos-internal "$CURRENT_USER"
    echo "   ✅ Added $CURRENT_USER to synos-internal"
else
    echo "   ℹ️  $CURRENT_USER already in synos-internal"
fi

# Add to licensed (for development/testing)
if ! groups "$CURRENT_USER" | grep -q "synos-licensed"; then
    $SUDO usermod -aG synos-licensed "$CURRENT_USER"
    echo "   ✅ Added $CURRENT_USER to synos-licensed"
else
    echo "   ℹ️  $CURRENT_USER already in synos-licensed"
fi

echo ""
echo "   ⚠️  NOTE: You may need to log out and back in for group changes to take effect"
echo ""

# ===========================================
# STEP 3: Set Permissions - PUBLIC Docs
# ===========================================
echo "3️⃣  Setting permissions for PUBLIC docs..."

# Public markdown files in root (world-readable)
cd "$WIKI_DIR"
for file in *.md; do
    if [ -f "$file" ]; then
        $SUDO chown root:synos-public "$file"
        $SUDO chmod 644 "$file"  # rw-r--r-- (everyone can read)
    fi
done

# Public directory itself
$SUDO chmod 755 "$WIKI_DIR"  # rwxr-xr-x (everyone can list)

echo "   ✅ Public docs: 644 (readable by everyone)"
echo ""

# ===========================================
# STEP 4: Set Permissions - INTERNAL Docs
# ===========================================
echo "4️⃣  Setting permissions for INTERNAL docs (employees only)..."

if [ -d "$WIKI_DIR/internal" ]; then
    # Directory: 750 (rwxr-x---)
    $SUDO chown -R root:synos-internal "$WIKI_DIR/internal"
    $SUDO chmod 750 "$WIKI_DIR/internal"

    # Files: 640 (rw-r-----)
    $SUDO find "$WIKI_DIR/internal" -type f -name "*.md" -exec chmod 640 {} \;

    echo "   ✅ Internal directory: 750 (rwxr-x---) - Only synos-internal group"
    echo "   ✅ Internal files: 640 (rw-r-----) - Only synos-internal can read"
    echo "   🔒 Contains: Pricing, MSSP ops, AI engine (54k lines), kernel internals"
else
    echo "   ⚠️  Internal directory not found (skipping)"
fi

echo ""

# ===========================================
# STEP 5: Set Permissions - RESTRICTED Docs
# ===========================================
echo "5️⃣  Setting permissions for RESTRICTED docs (licensed users)..."

if [ -d "$WIKI_DIR/restricted" ]; then
    # Directory: 750 (rwxr-x---)
    $SUDO chown -R root:synos-licensed "$WIKI_DIR/restricted"
    $SUDO chmod 750 "$WIKI_DIR/restricted"

    # Files: 640 (rw-r-----)
    $SUDO find "$WIKI_DIR/restricted" -type f -name "*.md" -exec chmod 640 {} \;

    echo "   ✅ Restricted directory: 750 (rwxr-x---) - Only synos-licensed group"
    echo "   ✅ Restricted files: 640 (rw-r-----) - Only synos-licensed can read"
    echo "   🔒 Contains: 500+ tools, K8s, pentesting, build system"
else
    echo "   ⚠️  Restricted directory not found (skipping)"
fi

echo ""

# ===========================================
# STEP 6: Set Permissions - PUBLIC Directory
# ===========================================
echo "6️⃣  Setting permissions for PUBLIC directory..."

if [ -d "$WIKI_DIR/public" ]; then
    $SUDO chown -R root:synos-public "$WIKI_DIR/public"
    $SUDO chmod 755 "$WIKI_DIR/public"
    $SUDO find "$WIKI_DIR/public" -type f -name "*.md" -exec chmod 644 {} \;

    echo "   ✅ Public directory: 755 (rwxr-xr-x) - Everyone can access"
    echo "   ✅ Public files: 644 (rw-r--r--) - Everyone can read"
else
    echo "   ℹ️  Public directory not found (skipping)"
fi

echo ""

# ===========================================
# STEP 7: Verification
# ===========================================
echo "7️⃣  Verifying permissions..."
echo ""

echo "📊 Permission Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "$WIKI_DIR/internal" ]; then
    INTERNAL_PERMS=$(stat -c "%a" "$WIKI_DIR/internal")
    INTERNAL_GROUP=$(stat -c "%G" "$WIKI_DIR/internal")
    echo "🔴 INTERNAL:    $INTERNAL_PERMS ($INTERNAL_GROUP) - Employees only"
fi

if [ -d "$WIKI_DIR/restricted" ]; then
    RESTRICTED_PERMS=$(stat -c "%a" "$WIKI_DIR/restricted")
    RESTRICTED_GROUP=$(stat -c "%G" "$WIKI_DIR/restricted")
    echo "🟡 RESTRICTED:  $RESTRICTED_PERMS ($RESTRICTED_GROUP) - Licensed users"
fi

PUBLIC_PERMS=$(stat -c "%a" "$WIKI_DIR")
echo "🟢 PUBLIC:      $PUBLIC_PERMS (everyone) - Free access"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ===========================================
# STEP 8: Test Access
# ===========================================
echo "8️⃣  Testing access control..."
echo ""

# Test as current user (should have access to everything during dev)
if [ -d "$WIKI_DIR/internal" ] && [ -r "$WIKI_DIR/internal/README.md" ]; then
    echo "   ✅ Current user ($CURRENT_USER) can read internal docs"
else
    echo "   ⚠️  Current user ($CURRENT_USER) CANNOT read internal docs"
    echo "      (This is expected if not in synos-internal group yet)"
fi

echo ""

# ===========================================
# FINAL SUMMARY
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PERMISSIONS CONFIGURED SUCCESSFULLY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 Security Status:"
echo "   • Public docs:     Readable by everyone (644)"
echo "   • Restricted docs: Only synos-licensed group (640)"
echo "   • Internal docs:   Only synos-internal group (640)"
echo ""
echo "👥 Groups Created:"
echo "   • synos-public    - Everyone (world-readable)"
echo "   • synos-licensed  - Paying customers"
echo "   • synos-internal  - Employees only"
echo ""
echo "📝 Next Steps:"
echo "   1. Log out and log back in for group membership to take effect"
echo "   2. Test access with: ls -la $WIKI_DIR/internal/"
echo "   3. Add other users: sudo usermod -aG synos-internal username"
echo "   4. Review access with: groups username"
echo ""
echo "⚠️  Important Notes:"
echo "   • Users must be in the appropriate group to access docs"
echo "   • SSH users can still access if in the right group"
echo "   • For web access, additional web server config needed"
echo "   • For git security, use separate repositories (see Step 3)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
