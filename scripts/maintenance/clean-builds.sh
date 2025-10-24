#!/usr/bin/env bash
################################################################################
# SynOS Build Cleanup Tool
# 
# Smart cleanup of build artifacts with safety checks and multiple modes.
#
# Usage:
#   ./scripts/maintenance/clean-builds.sh [OPTIONS]
#
# Options:
#   --all             Clean everything (use with caution!)
#   --old             Clean builds older than N days (default: 7)
#   --large           Clean builds larger than N MB (default: 1000)
#   --workspace       Clean Rust target/workspace directories
#   --isos            Clean old ISO files
#   --logs            Clean old log files
#   --temp            Clean temporary build files
#   --days N          Set age threshold in days (default: 7)
#   --size N          Set size threshold in MB (default: 1000)
#   --dry-run         Show what would be deleted (safe mode)
#   --interactive     Ask before deleting each item
#   --force           Skip confirmation prompts
#   --verbose         Show detailed information
#   --help            Show this help message
#
# Safety Features:
#   - Preserves most recent ISO
#   - Never deletes current workspace
#   - Interactive mode available
#   - Dry-run mode for testing
#   - Size reporting before deletion
#
# Exit Codes:
#   0 - Success
#   1 - Error during cleanup
#
################################################################################

set -euo pipefail

# Determine project root first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source shared library
source "${SCRIPT_DIR}/../lib/build-common.sh"

################################################################################
# Configuration
################################################################################

CLEAN_ALL=false
CLEAN_OLD=false
CLEAN_LARGE=false
CLEAN_WORKSPACE=false
CLEAN_ISOS=false
CLEAN_LOGS=false
CLEAN_TEMP=false

DRY_RUN=false
INTERACTIVE=false
FORCE=false
VERBOSE=false

AGE_DAYS=7
SIZE_MB=1000

# Statistics
ITEMS_FOUND=0
ITEMS_DELETED=0
SPACE_FREED=0

################################################################################
# Argument Parsing
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --old)
            CLEAN_OLD=true
            shift
            ;;
        --large)
            CLEAN_LARGE=true
            shift
            ;;
        --workspace)
            CLEAN_WORKSPACE=true
            shift
            ;;
        --isos)
            CLEAN_ISOS=true
            shift
            ;;
        --logs)
            CLEAN_LOGS=true
            shift
            ;;
        --temp)
            CLEAN_TEMP=true
            shift
            ;;
        --days)
            AGE_DAYS="$2"
            shift 2
            ;;
        --size)
            SIZE_MB="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --interactive|-i)
            INTERACTIVE=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# If --all is set, enable everything
if [[ "$CLEAN_ALL" == true ]]; then
    CLEAN_OLD=true
    CLEAN_LARGE=true
    CLEAN_WORKSPACE=true
    CLEAN_ISOS=true
    CLEAN_LOGS=true
    CLEAN_TEMP=true
fi

# If nothing specified, default to safe cleanup
if [[ "$CLEAN_OLD" == false && "$CLEAN_LARGE" == false && \
      "$CLEAN_WORKSPACE" == false && "$CLEAN_ISOS" == false && \
      "$CLEAN_LOGS" == false && "$CLEAN_TEMP" == false ]]; then
    CLEAN_OLD=true
    CLEAN_LOGS=true
    CLEAN_TEMP=true
fi

################################################################################
# Helper Functions
################################################################################

confirm() {
    local message="$1"
    
    if [[ "$FORCE" == true ]]; then
        return 0
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        return 0
    fi
    
    read -p "$message (y/N): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

safe_delete() {
    local path="$1"
    local size=0
    
    if [[ ! -e "$path" ]]; then
        return 0
    fi
    
    # Get size before deletion
    if [[ -f "$path" ]]; then
        size=$(stat -c%s "$path" 2>/dev/null || echo 0)
    elif [[ -d "$path" ]]; then
        size=$(du -sb "$path" 2>/dev/null | cut -f1 || echo 0)
    fi
    
    ((ITEMS_FOUND++))
    
    # Interactive confirmation
    if [[ "$INTERACTIVE" == true ]]; then
        if ! confirm "Delete $path ($(human_size "$size"))?"; then
            info "Skipped: $path"
            return 0
        fi
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY-RUN] Would delete: $path ($(human_size "$size"))"
        ((SPACE_FREED += size))
        return 0
    fi
    
    # Actual deletion
    if [[ -f "$path" ]]; then
        rm -f "$path" && {
            ((ITEMS_DELETED++))
            ((SPACE_FREED += size))
            if [[ "$VERBOSE" == true ]]; then
                success "Deleted: $path ($(human_size "$size"))"
            fi
        }
    elif [[ -d "$path" ]]; then
        rm -rf "$path" && {
            ((ITEMS_DELETED++))
            ((SPACE_FREED += size))
            if [[ "$VERBOSE" == true ]]; then
                success "Deleted: $path ($(human_size "$size"))"
            fi
        }
    fi
}

get_file_age_days() {
    local file="$1"
    local now=$(date +%s)
    local mtime=$(stat -c%Y "$file" 2>/dev/null || echo "$now")
    local age=$((($now - $mtime) / 86400))
    echo "$age"
}

get_size_mb() {
    local path="$1"
    local size_bytes
    
    if [[ -f "$path" ]]; then
        size_bytes=$(stat -c%s "$path" 2>/dev/null || echo 0)
    elif [[ -d "$path" ]]; then
        size_bytes=$(du -sb "$path" 2>/dev/null | cut -f1 || echo 0)
    else
        size_bytes=0
    fi
    
    echo $((size_bytes / 1024 / 1024))
}

################################################################################
# Cleanup Functions
################################################################################

clean_old_builds() {
    section "Cleaning Builds Older Than ${AGE_DAYS} Days"
    
    local build_dir="${PROJECT_ROOT}/build"
    
    if [[ ! -d "$build_dir" ]]; then
        info "No build directory found"
        return 0
    fi
    
    # Clean old workspace directories
    if find "$build_dir" -maxdepth 1 -name "workspace-*" -type d 2>/dev/null | grep -q .; then
        while IFS= read -r dir; do
            local age=$(get_file_age_days "$dir")
            if [[ $age -ge $AGE_DAYS ]]; then
                info "Found old workspace: $(basename "$dir") (${age} days old)"
                safe_delete "$dir"
            fi
        done < <(find "$build_dir" -maxdepth 1 -name "workspace-*" -type d 2>/dev/null)
    else
        info "No old workspace directories found"
    fi
    
    # Clean old ISO root directories
    if find "$build_dir" -maxdepth 1 -name "isoroot-*" -type d 2>/dev/null | grep -q .; then
        while IFS= read -r dir; do
            local age=$(get_file_age_days "$dir")
            if [[ $age -ge $AGE_DAYS ]]; then
                info "Found old isoroot: $(basename "$dir") (${age} days old)"
                safe_delete "$dir"
            fi
        done < <(find "$build_dir" -maxdepth 1 -name "isoroot-*" -type d 2>/dev/null)
    fi
}

clean_large_builds() {
    section "Cleaning Builds Larger Than ${SIZE_MB}MB"
    
    local build_dir="${PROJECT_ROOT}/build"
    
    if [[ ! -d "$build_dir" ]]; then
        info "No build directory found"
        return 0
    fi
    
    # Find large directories
    while IFS= read -r dir; do
        local size_mb=$(get_size_mb "$dir")
        if [[ $size_mb -ge $SIZE_MB ]]; then
            info "Found large build: $(basename "$dir") (${size_mb}MB)"
            safe_delete "$dir"
        fi
    done < <(find "$build_dir" -maxdepth 1 -type d -name "workspace-*" -o -name "isoroot-*" 2>/dev/null)
}

clean_workspace() {
    section "Cleaning Rust Workspace Cache"
    
    local target_dir="${PROJECT_ROOT}/target"
    
    if [[ ! -d "$target_dir" ]]; then
        info "No target directory found"
        return 0
    fi
    
    warning "This will clean Rust build cache (next build will be slower)"
    
    if ! confirm "Clean target/ directory?"; then
        info "Skipped workspace cleanup"
        return 0
    fi
    
    # Clean incremental builds (safe)
    if [[ -d "$target_dir/debug/incremental" ]]; then
        info "Cleaning debug incremental builds..."
        safe_delete "$target_dir/debug/incremental"
    fi
    
    if [[ -d "$target_dir/release/incremental" ]]; then
        info "Cleaning release incremental builds..."
        safe_delete "$target_dir/release/incremental"
    fi
    
    # Clean deps (more aggressive)
    if [[ "$FORCE" == true ]]; then
        if [[ -d "$target_dir/debug/deps" ]]; then
            info "Cleaning debug dependencies..."
            safe_delete "$target_dir/debug/deps"
        fi
        
        if [[ -d "$target_dir/release/deps" ]]; then
            info "Cleaning release dependencies..."
            safe_delete "$target_dir/release/deps"
        fi
    fi
}

clean_old_isos() {
    section "Cleaning Old ISO Files"
    
    local build_dir="${PROJECT_ROOT}/build"
    
    if [[ ! -d "$build_dir" ]]; then
        info "No build directory found"
        return 0
    fi
    
    # Find all ISOs
    local isos=()
    while IFS= read -r iso; do
        isos+=("$iso")
    done < <(find "$build_dir" -maxdepth 1 -name "*.iso" -type f 2>/dev/null | sort -r)
    
    if [[ ${#isos[@]} -eq 0 ]]; then
        info "No ISO files found"
        return 0
    fi
    
    info "Found ${#isos[@]} ISO file(s)"
    
    # Keep the most recent ISO
    local kept_iso="${isos[0]}"
    info "Keeping most recent: $(basename "$kept_iso")"
    
    # Delete older ISOs
    for ((i=1; i<${#isos[@]}; i++)); do
        local iso="${isos[$i]}"
        local age=$(get_file_age_days "$iso")
        
        if [[ $age -ge $AGE_DAYS ]]; then
            info "Found old ISO: $(basename "$iso") (${age} days old)"
            safe_delete "$iso"
            
            # Also delete associated checksums
            [[ -f "${iso}.md5" ]] && safe_delete "${iso}.md5"
            [[ -f "${iso}.sha256" ]] && safe_delete "${iso}.sha256"
        fi
    done
}

clean_logs() {
    section "Cleaning Old Log Files"
    
    local logs_dir="${PROJECT_ROOT}/build/logs"
    
    if [[ ! -d "$logs_dir" ]]; then
        info "No logs directory found"
        return 0
    fi
    
    # Clean old log files
    while IFS= read -r log; do
        local age=$(get_file_age_days "$log")
        if [[ $age -ge $AGE_DAYS ]]; then
            if [[ "$VERBOSE" == true ]]; then
                info "Found old log: $(basename "$log") (${age} days old)"
            fi
            safe_delete "$log"
        fi
    done < <(find "$logs_dir" -type f -name "*.log" 2>/dev/null)
}

clean_temp() {
    section "Cleaning Temporary Files"
    
    local build_dir="${PROJECT_ROOT}/build"
    
    if [[ ! -d "$build_dir" ]]; then
        info "No build directory found"
        return 0
    fi
    
    # Clean cache directory
    if [[ -d "$build_dir/cache" ]]; then
        info "Cleaning cache directory..."
        safe_delete "$build_dir/cache"
    fi
    
    # Clean temporary files
    while IFS= read -r file; do
        if [[ "$VERBOSE" == true ]]; then
            info "Found temp file: $(basename "$file")"
        fi
        safe_delete "$file"
    done < <(find "$build_dir" -maxdepth 1 -type f \( -name "*.tmp" -o -name "*.temp" -o -name "*~" \) 2>/dev/null)
    
    # Clean old checksum files without corresponding ISOs
    while IFS= read -r checksum; do
        local iso="${checksum%.md5}"
        iso="${iso%.sha256}"
        
        if [[ ! -f "$iso" ]]; then
            if [[ "$VERBOSE" == true ]]; then
                info "Found orphaned checksum: $(basename "$checksum")"
            fi
            safe_delete "$checksum"
        fi
    done < <(find "$build_dir" -maxdepth 1 -type f \( -name "*.md5" -o -name "*.sha256" \) 2>/dev/null)
}

show_disk_usage() {
    section "Disk Usage Analysis"
    
    local build_dir="${PROJECT_ROOT}/build"
    local target_dir="${PROJECT_ROOT}/target"
    
    if [[ -d "$build_dir" ]]; then
        local build_size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
        info "Build directory: $build_size"
        
        # Show breakdown
        if [[ "$VERBOSE" == true ]]; then
            echo ""
            du -h --max-depth=1 "$build_dir" 2>/dev/null | sort -h | tail -10 | while read -r line; do
                echo "  $line"
            done
        fi
    fi
    
    if [[ -d "$target_dir" ]]; then
        local target_size=$(du -sh "$target_dir" 2>/dev/null | cut -f1)
        info "Target directory: $target_size"
    fi
    
    # Available space
    local available=$(df -h "$build_dir" 2>/dev/null | awk 'NR==2 {print $4}')
    info "Available space: $available"
}

################################################################################
# Main Cleanup Flow
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS Build Cleanup Tool"
    
    # Show configuration
    info "Cleanup Configuration:"
    info "  Age threshold:    ${AGE_DAYS} days"
    info "  Size threshold:   ${SIZE_MB}MB"
    info "  Dry run:          $DRY_RUN"
    info "  Interactive:      $INTERACTIVE"
    info "  Verbose:          $VERBOSE"
    echo ""
    
    info "Cleanup targets:"
    [[ "$CLEAN_OLD" == true ]] && info "  ✓ Old builds (>${AGE_DAYS} days)"
    [[ "$CLEAN_LARGE" == true ]] && info "  ✓ Large builds (>${SIZE_MB}MB)"
    [[ "$CLEAN_WORKSPACE" == true ]] && info "  ✓ Workspace cache"
    [[ "$CLEAN_ISOS" == true ]] && info "  ✓ Old ISOs"
    [[ "$CLEAN_LOGS" == true ]] && info "  ✓ Old logs"
    [[ "$CLEAN_TEMP" == true ]] && info "  ✓ Temporary files"
    echo ""
    
    # Show current disk usage
    show_disk_usage
    echo ""
    
    # Confirmation for non-dry-run
    if [[ "$DRY_RUN" == false && "$FORCE" == false ]]; then
        if ! confirm "Proceed with cleanup?"; then
            info "Cleanup cancelled"
            return 0
        fi
        echo ""
    fi
    
    # Run cleanup operations
    [[ "$CLEAN_OLD" == true ]] && clean_old_builds
    [[ "$CLEAN_LARGE" == true ]] && clean_large_builds
    [[ "$CLEAN_WORKSPACE" == true ]] && clean_workspace
    [[ "$CLEAN_ISOS" == true ]] && clean_old_isos
    [[ "$CLEAN_LOGS" == true ]] && clean_logs
    [[ "$CLEAN_TEMP" == true ]] && clean_temp
    
    # Summary
    local end_time
    end_time=$(date +%s)
    
    echo ""
    section "Cleanup Summary"
    
    info "Items found: $ITEMS_FOUND"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "Items to delete: $ITEMS_FOUND (dry-run mode)"
        info "Space to free: $(human_size $SPACE_FREED)"
    else
        success "Items deleted: $ITEMS_DELETED"
        success "Space freed: $(human_size $SPACE_FREED)"
    fi
    
    info "Time elapsed: $(elapsed_time "$start_time" "$end_time")"
    
    echo ""
    if [[ "$DRY_RUN" == true ]]; then
        info "This was a dry-run. No files were deleted."
        info "Run without --dry-run to perform actual cleanup."
    else
        success "Cleanup complete!"
    fi
    
    return 0
}

################################################################################
# Execute
################################################################################

main "$@"
