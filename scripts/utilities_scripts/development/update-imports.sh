#!/bin/bash

# SynOS Import Update Script - Replace consciousness imports with AI
# Date: September 18, 2025

echo "🔄 SynOS Import Update Script"
echo "=============================="

BASE_DIR="/home/diablorain/Syn_OS"
BACKUP_DIR="$BASE_DIR/archive/import-updates-backup-$(date +%Y%m%d-%H%M%S)"

echo "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Function to update imports in a file
update_imports() {
    local file="$1"
    local backup_file="$BACKUP_DIR/$(basename "$file")"
    
    # Create backup
    cp "$file" "$backup_file"
    
    # Update imports
    sed -i 's/syn-consciousness/syn-ai/g' "$file"
    sed -i 's/use.*consciousness::/use syn_ai::/g' "$file"
    sed -i 's/consciousness::/ai::/g' "$file"
    sed -i 's/extern crate consciousness/extern crate syn_ai/g' "$file"
    
    echo "   Updated: $file"
}

# Find and update Cargo.toml files
echo "1. Updating Cargo.toml dependencies..."
find "$BASE_DIR" -name "Cargo.toml" -not -path "*/archive/*" -not -path "*/target/*" | while read file; do
    if grep -q "consciousness" "$file" 2>/dev/null; then
        update_imports "$file"
    fi
done

# Find and update Rust source files
echo "2. Updating Rust source imports..."
find "$BASE_DIR/src" "$BASE_DIR/core" -name "*.rs" -not -path "*/archive/*" -not -path "*/target/*" | while read file; do
    if grep -q "use.*consciousness\|extern crate consciousness" "$file" 2>/dev/null; then
        update_imports "$file"
    fi
done

echo "3. Summary of files that still reference consciousness modules:"
echo "   (These may need manual review)"
find "$BASE_DIR/src" "$BASE_DIR/core" -name "*.rs" -not -path "*/archive/*" -not -path "*/target/*" -exec grep -l "consciousness::" {} \; 2>/dev/null | head -10

echo ""
echo "✅ Import updates completed"
echo "📁 Backups stored in: $BACKUP_DIR"
