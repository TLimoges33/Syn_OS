#!/bin/bash

# Clean up conflict markers in all files
# This script removes git merge conflict markers and keeps all content

echo "Cleaning up conflict markers in files..."

# Find all files with conflict markers
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.rs" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) \
    -exec grep -l "<<<<<<< HEAD" {} \; 2>/dev/null | while read conflict_file; do
    
    echo "Cleaning conflict markers in: $conflict_file"
    
    # Create a backup
    cp "$conflict_file" "${conflict_file}.backup"
    
    # Remove conflict markers but keep all content
    # This removes the lines with <<<<<<< HEAD, =======, and >>>>>>> but keeps everything else
    sed -i '/^<<<<<<< HEAD$/d; /^=======$/d; /^>>>>>>> /d' "$conflict_file"
    
    echo "  Cleaned: $conflict_file"
done

echo "Conflict marker cleanup complete!"

# Verify no conflict markers remain
echo "Verifying cleanup..."
remaining_conflicts=$(find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.rs" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) -exec grep -l "<<<<<<< HEAD" {} \; 2>/dev/null | wc -l)

if [ "$remaining_conflicts" -eq 0 ]; then
    echo "✅ All conflict markers removed successfully!"
else
    echo "⚠️  Warning: $remaining_conflicts files still have conflict markers"
fi
