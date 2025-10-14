#!/bin/bash

# SynOS Build Safety Framework
# Prevents dangerous permission operations that could corrupt the system
# Created in response to PERM-CORRUPT-2025-09-15 incident

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Safety configuration
SYNOS_PROJECT_ROOT="/home/diablorain/Syn_OS"
ALLOWED_BUILD_DIRS=("$SYNOS_PROJECT_ROOT/build" "$SYNOS_PROJECT_ROOT/dist" "$SYNOS_PROJECT_ROOT/tmp")

# Logging function
log_safety() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$SYNOS_PROJECT_ROOT/logs/build-safety.log"
}

log_info() { log_safety "${BLUE}INFO${NC}" "$1"; }
log_warn() { log_safety "${YELLOW}WARN${NC}" "$1"; }
log_error() { log_safety "${RED}ERROR${NC}" "$1"; }
log_success() { log_safety "${GREEN}SUCCESS${NC}" "$1"; }

# Create logs directory if it doesn't exist
mkdir -p "$SYNOS_PROJECT_ROOT/logs"

# Validate build environment
validate_build_environment() {
    log_info "Validating build environment..."

    # Check we're in the right project
    if [[ "$PWD" != *"Syn_OS"* ]]; then
        log_error "Not executing from within Syn_OS project directory"
        log_error "Current directory: $PWD"
        log_error "Expected: somewhere under $SYNOS_PROJECT_ROOT"
        exit 1
    fi

    # Validate BUILD_DIR if set
    if [[ -n "${BUILD_DIR:-}" ]]; then
        if [[ ! "$BUILD_DIR" =~ ^$SYNOS_PROJECT_ROOT ]]; then
            log_error "BUILD_DIR points outside project directory"
            log_error "BUILD_DIR: $BUILD_DIR"
            log_error "Project root: $SYNOS_PROJECT_ROOT"
            exit 1
        fi

        if [[ ! -d "$BUILD_DIR" ]]; then
            log_warn "BUILD_DIR does not exist, creating: $BUILD_DIR"
            mkdir -p "$BUILD_DIR"
        fi
    fi

    # Validate WORK_DIR if set
    if [[ -n "${WORK_DIR:-}" ]]; then
        if [[ ! "$WORK_DIR" =~ ^$SYNOS_PROJECT_ROOT ]]; then
            log_error "WORK_DIR points outside project directory"
            log_error "WORK_DIR: $WORK_DIR"
            exit 1
        fi
    fi

    log_success "Build environment validation passed"
}

# Safe directory operations
safe_chown() {
    local target_dir="$1"
    local owner="$2"
    local dry_run="${DRY_RUN:-false}"

    log_info "Attempting to change ownership of $target_dir to $owner"

    # Validate directory path
    if [[ -z "$target_dir" ]]; then
        log_error "No directory specified for chown"
        exit 1
    fi

    # Convert to absolute path
    target_dir=$(realpath "$target_dir" 2>/dev/null || echo "$target_dir")

    # Ensure we're not in system directories
    case "$target_dir" in
        /|/usr|/usr/*|/bin|/bin/*|/sbin|/sbin/*|/lib|/lib/*|/etc|/etc/*|/var|/var/*|/opt|/opt/*|/root|/root/*)
            log_error "SECURITY VIOLATION: Refusing to chown system directory: $target_dir"
            log_error "This could cause system-wide permission corruption!"
            exit 1
            ;;
    esac

    # Ensure directory exists and is within project
    if [[ ! -d "$target_dir" ]]; then
        log_error "Directory does not exist: $target_dir"
        exit 1
    fi

    if [[ ! "$target_dir" =~ ^$SYNOS_PROJECT_ROOT ]]; then
        log_error "SECURITY VIOLATION: Directory is outside project: $target_dir"
        log_error "Project root: $SYNOS_PROJECT_ROOT"
        exit 1
    fi

    # Validate owner format
    if [[ ! "$owner" =~ ^[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$ ]]; then
        log_error "Invalid owner format: $owner (expected user:group)"
        exit 1
    fi

    if [[ "$dry_run" == "true" ]]; then
        log_info "[DRY-RUN] Would execute: chown -R $owner $target_dir"
        return 0
    fi

    log_info "Safely changing ownership of $target_dir to $owner"
    if sudo chown -R "$owner" "$target_dir"; then
        log_success "Successfully changed ownership of $target_dir"
    else
        log_error "Failed to change ownership of $target_dir"
        exit 1
    fi
}

# Safe chmod operations
safe_chmod() {
    local target_path="$1"
    local permissions="$2"
    local recursive="${3:-false}"
    local dry_run="${DRY_RUN:-false}"

    log_info "Attempting to change permissions of $target_path to $permissions"

    # Validate path
    if [[ -z "$target_path" ]]; then
        log_error "No path specified for chmod"
        exit 1
    fi

    # Convert to absolute path
    target_path=$(realpath "$target_path" 2>/dev/null || echo "$target_path")

    # Ensure we're not modifying system directories
    case "$target_path" in
        /|/usr|/usr/*|/bin|/bin/*|/sbin|/sbin/*|/lib|/lib/*|/etc|/etc/*|/var|/var/*|/opt|/opt/*|/root|/root/*)
            log_error "SECURITY VIOLATION: Refusing to chmod system path: $target_path"
            exit 1
            ;;
    esac

    # Ensure path exists and is within project
    if [[ ! -e "$target_path" ]]; then
        log_error "Path does not exist: $target_path"
        exit 1
    fi

    if [[ ! "$target_path" =~ ^$SYNOS_PROJECT_ROOT ]]; then
        log_error "SECURITY VIOLATION: Path is outside project: $target_path"
        exit 1
    fi

    # Validate permissions
    if [[ ! "$permissions" =~ ^[0-7]{3,4}$ ]] && [[ ! "$permissions" =~ ^[ugoa]*[+-=][rwxXst]+$ ]]; then
        log_error "Invalid permissions format: $permissions"
        exit 1
    fi

    # Warn about overly permissive permissions
    if [[ "$permissions" =~ 777|666 ]]; then
        log_warn "WARNING: Using overly permissive permissions: $permissions"
        read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operation cancelled by user"
            return 1
        fi
    fi

    local chmod_flags=""
    if [[ "$recursive" == "true" ]]; then
        chmod_flags="-R"
    fi

    if [[ "$dry_run" == "true" ]]; then
        log_info "[DRY-RUN] Would execute: chmod $chmod_flags $permissions $target_path"
        return 0
    fi

    log_info "Safely changing permissions of $target_path to $permissions"
    if chmod $chmod_flags "$permissions" "$target_path"; then
        log_success "Successfully changed permissions of $target_path"
    else
        log_error "Failed to change permissions of $target_path"
        exit 1
    fi
}

# Initialize safety framework
init_safety_framework() {
    log_info "Initializing SynOS Build Safety Framework"

    # Create required directories
    mkdir -p "$SYNOS_PROJECT_ROOT/logs"
    mkdir -p "$SYNOS_PROJECT_ROOT/build"
    mkdir -p "$SYNOS_PROJECT_ROOT/dist"
    mkdir -p "$SYNOS_PROJECT_ROOT/tmp"

    # Set up git hooks to prevent dangerous commits
    if [[ -d "$SYNOS_PROJECT_ROOT/.git" ]]; then
        cat > "$SYNOS_PROJECT_ROOT/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook to check for dangerous patterns

echo "Checking for dangerous permission patterns..."

# Check for dangerous patterns in staged files
if git diff --cached --name-only | grep '\.sh$' | xargs grep -l 'chown -R\|chmod -R' 2>/dev/null; then
    echo "❌ DANGER: Found scripts with recursive permission changes!"
    echo "These patterns are forbidden after PERM-CORRUPT-2025-09-15 incident:"
    git diff --cached --name-only | grep '\.sh$' | xargs grep -n 'chown -R\|chmod -R' 2>/dev/null | head -10
    echo ""
    echo "Please use the safety framework functions instead:"
    echo "- safe_chown() for ownership changes"
    echo "- safe_chmod() for permission changes"
    echo ""
    echo "To override this check (NOT RECOMMENDED):"
    echo "git commit --no-verify"
    exit 1
fi

echo "✅ No dangerous permission patterns found"
EOF
        chmod +x "$SYNOS_PROJECT_ROOT/.git/hooks/pre-commit"
        log_success "Git pre-commit hook installed"
    fi

    log_success "Safety framework initialized successfully"
}

# Scan existing scripts for dangerous patterns
scan_for_dangerous_patterns() {
    log_info "Scanning existing scripts for dangerous patterns..."

    local dangerous_files=()
    while IFS= read -r -d '' file; do
        dangerous_files+=("$file")
    done < <(find "$SYNOS_PROJECT_ROOT" -name "*.sh" -type f -exec grep -l 'chown -R\|chmod -R' {} \; 2>/dev/null | sort | tr '\n' '\0')

    if [[ ${#dangerous_files[@]} -gt 0 ]]; then
        log_warn "Found ${#dangerous_files[@]} scripts with potentially dangerous patterns:"
        for file in "${dangerous_files[@]}"; do
            log_warn "  - $file"
            grep -n 'chown -R\|chmod -R' "$file" | head -3 | while read -r line; do
                log_warn "    $line"
            done
        done
        log_warn "These files should be reviewed and updated to use safety functions"
        return 1
    else
        log_success "No dangerous patterns found in existing scripts"
        return 0
    fi
}

# Export functions for use in other scripts
export -f validate_build_environment
export -f safe_chown
export -f safe_chmod
export -f log_info
export -f log_warn
export -f log_error
export -f log_success

# Main execution
case "${1:-}" in
    init)
        init_safety_framework
        ;;
    scan)
        scan_for_dangerous_patterns
        ;;
    validate)
        validate_build_environment
        ;;
    *)
        echo "SynOS Build Safety Framework"
        echo "Usage: $0 {init|scan|validate}"
        echo ""
        echo "Commands:"
        echo "  init     - Initialize safety framework and git hooks"
        echo "  scan     - Scan for dangerous patterns in existing scripts"
        echo "  validate - Validate current build environment"
        echo ""
        echo "This script can also be sourced to provide safety functions:"
        echo "  source $0"
        echo "  safe_chown /path/to/dir user:group"
        echo "  safe_chmod /path/to/file 755"
        ;;
esac