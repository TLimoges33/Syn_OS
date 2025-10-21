#!/bin/bash
################################################################################
# SynOS v1.1 Build Audit & Optimization
# Comprehensive build system analysis and optimization
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

AUDIT_DIR="$PROJECT_ROOT/build/logs/audit-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$AUDIT_DIR"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS v1.1 Build Audit & Optimization                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Audit Results: $AUDIT_DIR"
echo ""

# 1. Directory Structure Analysis
echo -e "${CYAN}[1/8] Analyzing Directory Structure...${NC}"
{
    echo "=== Directory Structure Analysis ==="
    echo "Generated: $(date)"
    echo ""

    echo "--- Top-level Structure ---"
    ls -lh "$PROJECT_ROOT" | head -30
    echo ""

    echo "--- Project Size by Directory ---"
    du -sh "$PROJECT_ROOT"/* 2>/dev/null | sort -h | tail -20
    echo ""

    echo "--- Large Directories (>100MB) ---"
    find "$PROJECT_ROOT" -type d -exec du -sm {} + 2>/dev/null | awk '$1 > 100' | sort -rn | head -20
    echo ""

} > "$AUDIT_DIR/01-directory-structure.txt"
echo -e "${GREEN}✓ Directory analysis complete${NC}"
echo ""

# 2. Build Artifacts Analysis
echo -e "${CYAN}[2/8] Analyzing Build Artifacts...${NC}"
{
    echo "=== Build Artifacts Analysis ==="
    echo ""

    if [ -d "$PROJECT_ROOT/build" ]; then
        echo "--- Build Directory Size ---"
        du -sh "$PROJECT_ROOT/build"
        echo ""

        echo "--- Build Contents ---"
        ls -lh "$PROJECT_ROOT/build" | head -30
        echo ""

        echo "--- ISO Files ---"
        find "$PROJECT_ROOT/build" -name "*.iso" -exec ls -lh {} \;
        echo ""

        echo "--- Checksum Files ---"
        find "$PROJECT_ROOT/build" -name "*.md5" -o -name "*.sha256" | wc -l
        echo " checksum files found"
        echo ""

        echo "--- Cache Size ---"
        if [ -d "$PROJECT_ROOT/build/cache" ]; then
            du -sh "$PROJECT_ROOT/build/cache"
        fi
        echo ""

        echo "--- Workspace Directories ---"
        find "$PROJECT_ROOT/build" -type d -name "workspace-*" -exec du -sh {} \; 2>/dev/null | head -10
        echo ""
    fi

    if [ -d "$PROJECT_ROOT/target" ]; then
        echo "--- Rust Target Directory ---"
        du -sh "$PROJECT_ROOT/target"
        echo ""

        echo "--- Rust Build Artifacts ---"
        find "$PROJECT_ROOT/target" -name "*.rlib" -o -name "*.so" | wc -l
        echo " Rust artifacts found"
        echo ""
    fi

} > "$AUDIT_DIR/02-build-artifacts.txt"
echo -e "${GREEN}✓ Build artifacts analysis complete${NC}"
echo ""

# 3. Source Code Analysis
echo -e "${CYAN}[3/8] Analyzing Source Code...${NC}"
{
    echo "=== Source Code Analysis ==="
    echo ""

    echo "--- Code Statistics ---"
    echo "Total files:"
    find "$PROJECT_ROOT" -type f | wc -l
    echo ""

    echo "Python files:"
    find "$PROJECT_ROOT" -name "*.py" | wc -l
    echo ""

    echo "Rust files:"
    find "$PROJECT_ROOT" -name "*.rs" | wc -l
    echo ""

    echo "Shell scripts:"
    find "$PROJECT_ROOT" -name "*.sh" | wc -l
    echo ""

    echo "Markdown docs:"
    find "$PROJECT_ROOT" -name "*.md" | wc -l
    echo ""

    if command -v cloc &>/dev/null; then
        echo "--- Lines of Code (cloc) ---"
        cloc "$PROJECT_ROOT/src" "$PROJECT_ROOT/core" "$PROJECT_ROOT/scripts" --quiet 2>/dev/null || echo "cloc analysis failed"
    else
        echo "cloc not installed, skipping detailed code stats"
        echo "Install with: sudo apt-get install cloc"
    fi
    echo ""

    echo "--- Largest Source Files ---"
    find "$PROJECT_ROOT/src" "$PROJECT_ROOT/core" -type f -exec wc -l {} + 2>/dev/null | sort -rn | head -20
    echo ""

} > "$AUDIT_DIR/03-source-code.txt"
echo -e "${GREEN}✓ Source code analysis complete${NC}"
echo ""

# 4. Dependencies Analysis
echo -e "${CYAN}[4/8] Analyzing Dependencies...${NC}"
{
    echo "=== Dependencies Analysis ==="
    echo ""

    echo "--- Python Dependencies ---"
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        echo "requirements.txt:"
        wc -l < "$PROJECT_ROOT/requirements.txt"
        echo " packages listed"
        echo ""
    fi

    if [ -f "$PROJECT_ROOT/development/requirements.txt" ]; then
        echo "development/requirements.txt:"
        wc -l < "$PROJECT_ROOT/development/requirements.txt"
        echo " packages listed"
        echo ""
    fi

    echo "--- Rust Dependencies ---"
    echo "Cargo.toml files:"
    find "$PROJECT_ROOT" -name "Cargo.toml" | wc -l
    echo ""

    if [ -f "$PROJECT_ROOT/Cargo.lock" ]; then
        echo "Locked dependencies:"
        grep -c "^name = " "$PROJECT_ROOT/Cargo.lock" || echo "0"
        echo ""
    fi

    echo "--- System Dependencies ---"
    if [ -f "$PROJECT_ROOT/config/dependencies/debian-packages.list" ]; then
        echo "Debian packages:"
        wc -l < "$PROJECT_ROOT/config/dependencies/debian-packages.list"
        echo " packages listed"
    fi
    echo ""

} > "$AUDIT_DIR/04-dependencies.txt"
echo -e "${GREEN}✓ Dependencies analysis complete${NC}"
echo ""

# 5. Documentation Analysis
echo -e "${CYAN}[5/8] Analyzing Documentation...${NC}"
{
    echo "=== Documentation Analysis ==="
    echo ""

    echo "--- Documentation Files ---"
    find "$PROJECT_ROOT/docs" -name "*.md" | wc -l
    echo " markdown files"
    echo ""

    echo "--- Documentation Size ---"
    du -sh "$PROJECT_ROOT/docs"
    echo ""

    echo "--- Largest Documentation Files ---"
    find "$PROJECT_ROOT/docs" -name "*.md" -exec wc -l {} + 2>/dev/null | sort -rn | head -15
    echo ""

    echo "--- README Files ---"
    find "$PROJECT_ROOT" -name "README.md" -o -name "README*.md" | head -20
    echo ""

} > "$AUDIT_DIR/05-documentation.txt"
echo -e "${GREEN}✓ Documentation analysis complete${NC}"
echo ""

# 6. Configuration Analysis
echo -e "${CYAN}[6/8] Analyzing Configuration...${NC}"
{
    echo "=== Configuration Analysis ==="
    echo ""

    echo "--- Configuration Files ---"
    find "$PROJECT_ROOT/config" -type f 2>/dev/null | wc -l
    echo " config files"
    echo ""

    echo "--- Configuration Structure ---"
    if [ -d "$PROJECT_ROOT/config" ]; then
        tree -L 2 "$PROJECT_ROOT/config" 2>/dev/null || ls -R "$PROJECT_ROOT/config" | head -50
    fi
    echo ""

} > "$AUDIT_DIR/06-configuration.txt"
echo -e "${GREEN}✓ Configuration analysis complete${NC}"
echo ""

# 7. Optimization Opportunities
echo -e "${CYAN}[7/8] Identifying Optimization Opportunities...${NC}"
{
    echo "=== Optimization Opportunities ==="
    echo ""

    echo "--- Duplicate Files ---"
    echo "Checking for duplicate files..."
    if command -v fdupes &>/dev/null; then
        fdupes -r "$PROJECT_ROOT/build" 2>/dev/null | head -50 || echo "No duplicates found or fdupes failed"
    else
        echo "fdupes not installed (sudo apt-get install fdupes)"
    fi
    echo ""

    echo "--- Old Build Artifacts (>30 days) ---"
    find "$PROJECT_ROOT/build" -type f -mtime +30 2>/dev/null | head -20
    echo ""

    echo "--- Empty Directories ---"
    find "$PROJECT_ROOT" -type d -empty 2>/dev/null | head -20
    echo ""

    echo "--- Large Log Files (>10MB) ---"
    find "$PROJECT_ROOT" -name "*.log" -size +10M -exec ls -lh {} \; 2>/dev/null
    echo ""

    echo "--- Temporary Files ---"
    find "$PROJECT_ROOT" -name "*.tmp" -o -name "*.temp" -o -name "*~" 2>/dev/null | wc -l
    echo " temporary files found"
    echo ""

} > "$AUDIT_DIR/07-optimizations.txt"
echo -e "${GREEN}✓ Optimization opportunities identified${NC}"
echo ""

# 8. Summary Report
echo -e "${CYAN}[8/8] Generating Summary Report...${NC}"
{
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   SynOS v1.1 Build Audit Summary                           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Generated: $(date)"
    echo "Audit ID: $(basename "$AUDIT_DIR")"
    echo ""

    echo "=== PROJECT METRICS ==="
    echo ""
    echo "Total Size:"
    du -sh "$PROJECT_ROOT" | awk '{print "  " $1}'
    echo ""

    if [ -d "$PROJECT_ROOT/build" ]; then
        echo "Build Artifacts:"
        du -sh "$PROJECT_ROOT/build" | awk '{print "  " $1}'
    fi

    if [ -d "$PROJECT_ROOT/target" ]; then
        echo "Rust Target:"
        du -sh "$PROJECT_ROOT/target" | awk '{print "  " $1}'
    fi

    echo ""
    echo "Source Files:"
    find "$PROJECT_ROOT/src" -type f 2>/dev/null | wc -l | awk '{print "  " $1}'

    echo "Documentation:"
    find "$PROJECT_ROOT/docs" -name "*.md" 2>/dev/null | wc -l | awk '{print "  " $1 " markdown files"}'

    echo "Scripts:"
    find "$PROJECT_ROOT/scripts" -name "*.sh" 2>/dev/null | wc -l | awk '{print "  " $1 " shell scripts"}'

    echo ""
    echo "=== TOP SPACE CONSUMERS ==="
    echo ""
    du -sh "$PROJECT_ROOT"/* 2>/dev/null | sort -h | tail -10

    echo ""
    echo "=== OPTIMIZATION RECOMMENDATIONS ==="
    echo ""

    # Calculate build artifact size
    BUILD_SIZE=$(du -sm "$PROJECT_ROOT/build" 2>/dev/null | awk '{print $1}')
    if [ ! -z "$BUILD_SIZE" ] && [ "$BUILD_SIZE" -gt 1000 ]; then
        echo "  🟡 Build directory is large (${BUILD_SIZE}MB)"
        echo "     Consider cleaning old workspaces and cache"
    fi

    # Check for old ISOs
    ISO_COUNT=$(find "$PROJECT_ROOT/build" -name "*.iso" 2>/dev/null | wc -l)
    if [ "$ISO_COUNT" -gt 2 ]; then
        echo "  🟡 Multiple ISO files found ($ISO_COUNT)"
        echo "     Keep only the latest and remove old builds"
    fi

    # Check target directory
    if [ -d "$PROJECT_ROOT/target" ]; then
        TARGET_SIZE=$(du -sm "$PROJECT_ROOT/target" 2>/dev/null | awk '{print $1}')
        if [ ! -z "$TARGET_SIZE" ] && [ "$TARGET_SIZE" -gt 500 ]; then
            echo "  🟡 Rust target directory is large (${TARGET_SIZE}MB)"
            echo "     Run: cargo clean"
        fi
    fi

    # Check for duplicates
    echo "  ℹ️  Check 07-optimizations.txt for duplicate files"
    echo "  ℹ️  Check for old workspace directories in build/"

    echo ""
    echo "=== DETAILED REPORTS ==="
    echo ""
    echo "Full analysis available in: $AUDIT_DIR"
    echo ""
    ls -1 "$AUDIT_DIR"

} | tee "$AUDIT_DIR/00-SUMMARY.txt"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Build Audit Complete!                                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Results saved to:${NC}"
echo "  $AUDIT_DIR"
echo ""
echo -e "${CYAN}View summary:${NC}"
echo "  cat $AUDIT_DIR/00-SUMMARY.txt"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "  1. Review optimization opportunities"
echo "  2. Clean old build artifacts"
echo "  3. Run: cargo clean (if Rust target is large)"
echo "  4. Remove old workspace directories"
echo ""
