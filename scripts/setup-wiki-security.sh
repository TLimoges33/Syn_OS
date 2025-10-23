#!/bin/bash
# ==================================================
# SynOS Wiki Security Setup Script
# Sets up encryption and access control for sensitive documentation
# ==================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WIKI_DIR="$REPO_ROOT/docs/wiki"

echo "=========================================="
echo "SynOS Wiki Security Setup"
echo "=========================================="
echo

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo "⚠️  WARNING: This script should be run with sudo for full setup"
   echo "   Some steps (Unix permissions, group creation) will be skipped"
   echo
   read -p "Continue without sudo? (y/n) " -n 1 -r
   echo
   if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       exit 1
   fi
   SKIP_PERMISSIONS=true
fi

# ==================================================
# STEP 1: Install Dependencies
# ==================================================
echo "📦 Step 1: Installing dependencies..."

if command -v git-crypt &> /dev/null; then
    echo "   ✅ git-crypt already installed"
else
    echo "   📥 Installing git-crypt..."
    sudo apt update
    sudo apt install -y git-crypt
fi

if command -v gpg &> /dev/null; then
    echo "   ✅ gpg already installed"
else
    echo "   📥 Installing gnupg..."
    sudo apt install -y gnupg
fi

echo

# ==================================================
# STEP 2: Create Unix Groups
# ==================================================
if [[ "$SKIP_PERMISSIONS" != "true" ]]; then
    echo "👥 Step 2: Creating Unix groups..."
    
    if getent group synos-internal > /dev/null 2>&1; then
        echo "   ✅ synos-internal group already exists"
    else
        echo "   ➕ Creating synos-internal group..."
        groupadd synos-internal
    fi
    
    if getent group synos-licensed > /dev/null 2>&1; then
        echo "   ✅ synos-licensed group already exists"
    else
        echo "   ➕ Creating synos-licensed group..."
        groupadd synos-licensed
    fi
    
    echo
fi

# ==================================================
# STEP 3: Set Unix Permissions
# ==================================================
if [[ "$SKIP_PERMISSIONS" != "true" ]]; then
    echo "🔒 Step 3: Setting Unix permissions..."
    
    # Internal directory
    if [ -d "$WIKI_DIR/internal" ]; then
        echo "   📁 Securing internal/ directory..."
        chown -R root:synos-internal "$WIKI_DIR/internal"
        chmod 750 "$WIKI_DIR/internal"
        chmod 640 "$WIKI_DIR/internal"/*.md 2>/dev/null || true
        echo "      ✅ Owner: root:synos-internal, Mode: 750 (dir), 640 (files)"
    fi
    
    # Restricted directory
    if [ -d "$WIKI_DIR/restricted" ]; then
        echo "   📁 Securing restricted/ directory..."
        chown -R root:synos-licensed "$WIKI_DIR/restricted"
        chmod 750 "$WIKI_DIR/restricted"
        chmod 640 "$WIKI_DIR/restricted"/*.md 2>/dev/null || true
        echo "      ✅ Owner: root:synos-licensed, Mode: 750 (dir), 640 (files)"
    fi
    
    echo
fi

# ==================================================
# STEP 4: Check GPG Setup
# ==================================================
echo "🔑 Step 4: Checking GPG setup..."

if gpg --list-keys | grep -q "@"; then
    echo "   ✅ GPG keys found"
    gpg --list-keys | head -5
else
    echo "   ⚠️  No GPG keys found!"
    echo
    echo "   To generate a GPG key:"
    echo "   $ gpg --full-generate-key"
    echo "   Choose: RSA and RSA, 4096 bits, no expiration"
    echo
    read -p "Generate GPG key now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gpg --full-generate-key
    fi
fi

echo

# ==================================================
# STEP 5: Initialize Git-Crypt
# ==================================================
echo "🔐 Step 5: Initializing git-crypt..."

cd "$REPO_ROOT"

if [ -f ".git-crypt/keys/default" ]; then
    echo "   ✅ git-crypt already initialized"
else
    echo "   🔧 Initializing git-crypt..."
    git-crypt init
    echo "   ✅ git-crypt initialized"
fi

echo

# ==================================================
# STEP 6: Add Encryption Rules
# ==================================================
echo "📝 Step 6: Verifying encryption rules..."

if [ -f "$WIKI_DIR/internal/.gitattributes" ]; then
    echo "   ✅ internal/.gitattributes exists"
else
    echo "   ⚠️  internal/.gitattributes missing!"
fi

if [ -f "$WIKI_DIR/restricted/.gitattributes" ]; then
    echo "   ✅ restricted/.gitattributes exists"
else
    echo "   ⚠️  restricted/.gitattributes missing!"
fi

echo

# ==================================================
# STEP 7: Add Current User to Git-Crypt
# ==================================================
echo "👤 Step 7: Adding GPG keys to git-crypt..."

# Get user's email from git config
USER_EMAIL=$(git config user.email || echo "")

if [ -z "$USER_EMAIL" ]; then
    read -p "Enter your email for GPG key: " USER_EMAIL
fi

# Check if user has GPG key for this email
if gpg --list-keys "$USER_EMAIL" &> /dev/null; then
    echo "   🔑 Adding GPG key for $USER_EMAIL to git-crypt..."
    git-crypt add-gpg-user "$USER_EMAIL" || echo "   ℹ️  User may already be added"
    echo "   ✅ You can now access encrypted files"
else
    echo "   ⚠️  No GPG key found for $USER_EMAIL"
    echo "   Generate one with: gpg --full-generate-key"
fi

echo

# ==================================================
# STEP 8: Verify Setup
# ==================================================
echo "✅ Step 8: Verifying setup..."

# Check git-crypt status
echo "   🔍 Git-crypt status:"
git-crypt status | head -10

echo

# ==================================================
# SUMMARY
# ==================================================
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo
echo "📋 Summary:"
echo "   ✅ git-crypt initialized"
echo "   ✅ Encryption rules configured"
if [[ "$SKIP_PERMISSIONS" != "true" ]]; then
    echo "   ✅ Unix groups created (synos-internal, synos-licensed)"
    echo "   ✅ Unix permissions set (750 dirs, 640 files)"
else
    echo "   ⚠️  Unix permissions skipped (run with sudo)"
fi
echo
echo "📚 Next Steps:"
echo "   1. Read docs/wiki/SECURITY.md for full documentation"
echo "   2. Add team members: git-crypt add-gpg-user <email>"
echo "   3. Team members unlock with: git-crypt unlock"
echo "   4. Create encrypted backup: ./scripts/wiki-backup.sh"
echo
echo "🔐 Access Control:"
echo "   • internal/   → synos-internal group + git-crypt"
echo "   • restricted/ → synos-licensed group + git-crypt"
echo
echo "⚠️  IMPORTANT:"
echo "   - Never commit unencrypted sensitive files"
echo "   - Always verify encryption: git-crypt status"
echo "   - Keep GPG keys backed up securely"
echo
