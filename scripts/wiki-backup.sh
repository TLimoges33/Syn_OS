#!/bin/bash
# ==================================================
# SynOS Wiki Backup Script
# Creates encrypted backups of sensitive documentation
# ==================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WIKI_DIR="$REPO_ROOT/docs/wiki"
BACKUP_DIR="$HOME/synos-backups"
DATE=$(date +%Y%m%d-%H%M%S)

echo "=========================================="
echo "SynOS Wiki Backup"
echo "=========================================="
echo

# Create backup directory
mkdir -p "$BACKUP_DIR"

# ==================================================
# Backup Internal Documentation
# ==================================================
if [ -d "$WIKI_DIR/internal" ]; then
    echo "📦 Backing up internal/ documentation..."
    BACKUP_FILE="$BACKUP_DIR/synos-wiki-internal-$DATE.tar.gz.gpg"
    
    tar czf - -C "$WIKI_DIR" internal/ | \
        gpg --symmetric --cipher-algo AES256 \
        --output "$BACKUP_FILE"
    
    echo "   ✅ Encrypted backup: $BACKUP_FILE"
    echo "   📊 Size: $(du -h "$BACKUP_FILE" | cut -f1)"
fi

echo

# ==================================================
# Backup Restricted Documentation
# ==================================================
if [ -d "$WIKI_DIR/restricted" ]; then
    echo "📦 Backing up restricted/ documentation..."
    BACKUP_FILE="$BACKUP_DIR/synos-wiki-restricted-$DATE.tar.gz.gpg"
    
    tar czf - -C "$WIKI_DIR" restricted/ | \
        gpg --symmetric --cipher-algo AES256 \
        --output "$BACKUP_FILE"
    
    echo "   ✅ Encrypted backup: $BACKUP_FILE"
    echo "   📊 Size: $(du -h "$BACKUP_FILE" | cut -f1)"
fi

echo

# ==================================================
# Combined Backup
# ==================================================
if [ -d "$WIKI_DIR/internal" ] && [ -d "$WIKI_DIR/restricted" ]; then
    echo "📦 Creating combined backup..."
    BACKUP_FILE="$BACKUP_DIR/synos-wiki-all-$DATE.tar.gz.gpg"
    
    tar czf - -C "$WIKI_DIR" internal/ restricted/ | \
        gpg --symmetric --cipher-algo AES256 \
        --output "$BACKUP_FILE"
    
    echo "   ✅ Encrypted backup: $BACKUP_FILE"
    echo "   📊 Size: $(du -h "$BACKUP_FILE" | cut -f1)"
fi

echo

# ==================================================
# Summary
# ==================================================
echo "=========================================="
echo "✅ Backup Complete!"
echo "=========================================="
echo
echo "📁 Backup location: $BACKUP_DIR"
echo "📊 Total backups: $(ls -1 "$BACKUP_DIR"/*.gpg 2>/dev/null | wc -l)"
echo
echo "🔓 To restore a backup:"
echo "   gpg -d <backup-file>.tar.gz.gpg | tar xzf -"
echo
echo "⚠️  IMPORTANT:"
echo "   - Store backups in secure location"
echo "   - Keep passphrase in password manager"
echo "   - Test restoration periodically"
echo

# List recent backups
echo "📋 Recent backups:"
ls -lht "$BACKUP_DIR"/*.gpg 2>/dev/null | head -5 || echo "   No backups found"
echo
