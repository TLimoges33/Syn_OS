#!/bin/bash
# Documentation Audit Script
# Finds all inaccurate claims across documentation

set -e

DOCS_DIR="/home/diablorain/Syn_OS/docs"
AUDIT_REPORT="/home/diablorain/Syn_OS/docs/DOCUMENTATION_AUDIT_RESULTS.md"

echo "# SynOS Documentation Audit Results" > "$AUDIT_REPORT"
echo "**Generated:** $(date)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

echo "## Searching for Inaccurate Claims..." >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# False completion claims
echo "### Files Claiming '100% Complete' for AI Features" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"
grep -r "100.*complete\|100.*COMPLETE\|100%.*AI\|production.*ready.*AI" "$DOCS_DIR" --include="*.md" -n | \
    grep -v "Linux Distribution\|Security Tools\|Build System\|Branding" >> "$AUDIT_REPORT" 2>/dev/null || echo "None found" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Custom kernel false claims
echo "### Files Claiming Custom Kernel is Production-Ready" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"
grep -r "custom.*kernel.*production\|custom.*kernel.*complete\|custom.*kernel.*ready" "$DOCS_DIR" --include="*.md" -n -i >> "$AUDIT_REPORT" 2>/dev/null || echo "None found" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# AI runtime false claims
echo "### Files Claiming AI Runtime is Operational" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"
grep -r "TensorFlow.*operational\|TensorFlow.*production\|ONNX.*operational\|vector.*database.*operational" "$DOCS_DIR" --include="*.md" -n -i >> "$AUDIT_REPORT" 2>/dev/null || echo "None found" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Consciousness claims
echo "### Files Claiming Consciousness Features Work" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"
grep -r "consciousness.*working\|consciousness.*operational\|consciousness.*complete" "$DOCS_DIR" --include="*.md" -n -i >> "$AUDIT_REPORT" 2>/dev/null || echo "None found" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Count markdown files
echo "## Documentation Statistics" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"
echo "- **Total markdown files:** $(find "$DOCS_DIR" -name "*.md" | wc -l)" >> "$AUDIT_REPORT"
echo "- **Files with 'complete' claims:** $(grep -r "complete\|COMPLETE" "$DOCS_DIR" --include="*.md" -l | wc -l)" >> "$AUDIT_REPORT"
echo "- **Files with 'production' claims:** $(grep -r "production\|PRODUCTION" "$DOCS_DIR" --include="*.md" -l | wc -l)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Files by subdirectory
echo "## Files by Subdirectory" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"
for dir in "$DOCS_DIR"/*/; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -name "*.md" | wc -l)
        dirname=$(basename "$dir")
        echo "- **$dirname/**: $count files" >> "$AUDIT_REPORT"
    fi
done

echo ""
echo "Audit complete! Results written to: $AUDIT_REPORT"
cat "$AUDIT_REPORT"
