#!/bin/bash

# Merge all .keepboth files with their corresponding original files
# This script handles the "keep both" merge strategy by combining content

echo "Starting merge of .keepboth files..."
count=0

# Find all .keepboth files
find . -name "*.keepboth" -type f | while read keepboth_file; do
    # Get the original file name by removing .keepboth extension
    original_file="${keepboth_file%.keepboth}"
    
    echo "Processing: $keepboth_file -> $original_file"
    
    if [[ -f "$original_file" ]]; then
        # Check if files are identical
        if cmp -s "$original_file" "$keepboth_file"; then
            echo "  Files are identical, removing .keepboth file"
            rm "$keepboth_file"
        else
            # Files are different, need to merge
            echo "  Files differ, merging content..."
            
            # Create a backup
            cp "$original_file" "${original_file}.backup"
            
            # Simple merge: append .keepboth content to original with separator
            echo "" >> "$original_file"
            echo "# ===== MERGED CONTENT FROM CONFLICT RESOLUTION =====" >> "$original_file"
            echo "" >> "$original_file"
            cat "$keepboth_file" >> "$original_file"
            
            # Remove the .keepboth file
            rm "$keepboth_file"
            
            echo "  Merged and removed .keepboth file"
        fi
    else
        # Original file doesn't exist, just rename .keepboth to original
        echo "  Original file missing, renaming .keepboth to original"
        mv "$keepboth_file" "$original_file"
    fi
    
    count=$((count + 1))
done

echo "Processed $count .keepboth files"
echo "Merge complete!"

# Clean up any remaining conflict markers in files
echo "Checking for remaining conflict markers..."
find . -type f -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.rs" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" | xargs grep -l "<<<<<<< HEAD" 2>/dev/null | while read conflict_file; do
    echo "WARNING: Conflict markers still found in: $conflict_file"
done

echo "All .keepboth files processed!"
