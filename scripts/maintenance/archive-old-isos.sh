#!/usr/bin/env bash
################################################################################
# SynOS ISO Archive Tool
# 
# Archive and compress old ISO images to save disk space while preserving
# the ability to restore them later.
#
# Usage:
#   ./scripts/maintenance/archive-old-isos.sh [OPTIONS]
#
# Options:
#   --archive         Archive ISOs to compressed format
#   --restore ISO     Restore archived ISO
#   --list            List archived ISOs
#   --age N           Archive ISOs older than N days (default: 30)
#   --compress TYPE   Compression type: gzip|xz|zstd (default: xz)
#   --level N         Compression level 1-9 (default: 6)
#   --keep N          Keep N most recent ISOs unarchived
#   --archive-dir DIR Archive directory (default: build/archives/)
#   --verify          Verify archives after creation
#   --dry-run         Show what would be archived
#   --verbose         Show detailed information
#   --help            Show this help message
#
# Features:
#   - Multiple compression formats (gzip, xz, zstd)
#   - Preserves checksums with archives
#   - Verification support
#   - Easy restoration
#   - Safe operation (never deletes without archiving)
#
# Exit Codes:
#   0 - Success
#   1 - Error during operation
#   2 - Verification failed
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

MODE=""  # archive, restore, list
AGE_DAYS=30
KEEP_COUNT=0
COMPRESS_TYPE="xz"
COMPRESS_LEVEL=6
ARCHIVE_DIR=""
VERIFY=false
DRY_RUN=false
VERBOSE=false

# Statistics
ISOS_ARCHIVED=0
SPACE_SAVED=0
RESTORE_ISO=""

################################################################################
# Argument Parsing
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --archive)
            MODE="archive"
            shift
            ;;
        --restore)
            MODE="restore"
            RESTORE_ISO="$2"
            shift 2
            ;;
        --list)
            MODE="list"
            shift
            ;;
        --age)
            AGE_DAYS="$2"
            shift 2
            ;;
        --keep)
            KEEP_COUNT="$2"
            shift 2
            ;;
        --compress)
            COMPRESS_TYPE="$2"
            shift 2
            ;;
        --level)
            COMPRESS_LEVEL="$2"
            shift 2
            ;;
        --archive-dir)
            ARCHIVE_DIR="$2"
            shift 2
            ;;
        --verify)
            VERIFY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
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

# Set archive directory
if [[ -z "$ARCHIVE_DIR" ]]; then
    ARCHIVE_DIR="${PROJECT_ROOT}/build/archives"
fi

# Validate mode
if [[ -z "$MODE" ]]; then
    error "No mode specified. Use --archive, --restore, or --list"
    exit 1
fi

# Validate compression type
case "$COMPRESS_TYPE" in
    gzip|xz|zstd)
        ;;
    *)
        error "Invalid compression type: $COMPRESS_TYPE"
        error "Valid types: gzip, xz, zstd"
        exit 1
        ;;
esac

################################################################################
# Helper Functions
################################################################################

get_compress_ext() {
    case "$COMPRESS_TYPE" in
        gzip) echo ".gz" ;;
        xz) echo ".xz" ;;
        zstd) echo ".zst" ;;
    esac
}

get_compress_cmd() {
    local level="$1"
    case "$COMPRESS_TYPE" in
        gzip) echo "gzip -${level}" ;;
        xz) echo "xz -${level}" ;;
        zstd) echo "zstd -${level}" ;;
    esac
}

get_decompress_cmd() {
    case "$COMPRESS_TYPE" in
        gzip) echo "gunzip" ;;
        xz) echo "unxz" ;;
        zstd) echo "unzstd" ;;
    esac
}

check_compression_tool() {
    case "$COMPRESS_TYPE" in
        gzip)
            if ! command -v gzip &> /dev/null; then
                error "gzip not found. Install: apt install gzip"
                exit 1
            fi
            ;;
        xz)
            if ! command -v xz &> /dev/null; then
                error "xz not found. Install: apt install xz-utils"
                exit 1
            fi
            ;;
        zstd)
            if ! command -v zstd &> /dev/null; then
                error "zstd not found. Install: apt install zstd"
                exit 1
            fi
            ;;
    esac
}

get_file_age_days() {
    local file="$1"
    local now
    local mtime
    local age
    
    now=$(date +%s)
    mtime=$(stat -c%Y "$file" 2>/dev/null || echo "$now")
    age=$((($now - $mtime) / 86400))
    echo "$age"
}

################################################################################
# Archive Operations
################################################################################

archive_iso() {
    local iso="$1"
    local iso_name
    local archive_name
    local ext
    local compress_cmd
    local original_size
    local compressed_size
    local ratio
    
    iso_name=$(basename "$iso")
    ext=$(get_compress_ext)
    archive_name="${iso_name}${ext}"
    compress_cmd=$(get_compress_cmd "$COMPRESS_LEVEL")
    
    info "Archiving: $iso_name"
    
    if [[ "$DRY_RUN" == true ]]; then
        original_size=$(stat -c%s "$iso")
        info "[DRY-RUN] Would archive to: $archive_name"
        info "[DRY-RUN] Original size: $(human_size "$original_size")"
        return 0
    fi
    
    # Create archive directory
    mkdir -p "$ARCHIVE_DIR"
    
    # Get original size
    original_size=$(stat -c%s "$iso")
    
    # Compress ISO
    if [[ "$VERBOSE" == true ]]; then
        info "Compressing with $COMPRESS_TYPE (level $COMPRESS_LEVEL)..."
    fi
    
    if ! $compress_cmd -c "$iso" > "${ARCHIVE_DIR}/${archive_name}"; then
        error "Failed to compress $iso_name"
        return 1
    fi
    
    # Get compressed size
    compressed_size=$(stat -c%s "${ARCHIVE_DIR}/${archive_name}")
    ratio=$((100 - (compressed_size * 100 / original_size)))
    
    # Copy checksums if they exist
    if [[ -f "${iso}.md5" ]]; then
        cp "${iso}.md5" "${ARCHIVE_DIR}/${archive_name}.md5"
    fi
    
    if [[ -f "${iso}.sha256" ]]; then
        cp "${iso}.sha256" "${ARCHIVE_DIR}/${archive_name}.sha256"
    fi
    
    # Verify if requested
    if [[ "$VERIFY" == true ]]; then
        if ! verify_archive "${ARCHIVE_DIR}/${archive_name}" "$iso"; then
            error "Verification failed for $archive_name"
            rm -f "${ARCHIVE_DIR}/${archive_name}"
            return 2
        fi
    fi
    
    # Report
    success "Archived: $archive_name"
    info "  Original:   $(human_size "$original_size")"
    info "  Compressed: $(human_size "$compressed_size")"
    info "  Ratio:      ${ratio}% reduction"
    
    # Update statistics
    ((ISOS_ARCHIVED++))
    ((SPACE_SAVED += original_size - compressed_size))
    
    # Delete original if archive successful
    if [[ -f "${ARCHIVE_DIR}/${archive_name}" ]]; then
        rm -f "$iso"
        rm -f "${iso}.md5" "${iso}.sha256"
    fi
    
    return 0
}

verify_archive() {
    local archive="$1"
    local original="$2"
    local decompress_cmd
    local temp_iso
    
    decompress_cmd=$(get_decompress_cmd)
    temp_iso="/tmp/verify-$(basename "$original")"
    
    info "Verifying archive..."
    
    # Decompress to temp location
    if ! $decompress_cmd -c "$archive" > "$temp_iso"; then
        error "Failed to decompress for verification"
        rm -f "$temp_iso"
        return 1
    fi
    
    # Compare sizes
    local orig_size
    local verify_size
    
    orig_size=$(stat -c%s "$original")
    verify_size=$(stat -c%s "$temp_iso")
    
    if [[ $orig_size -ne $verify_size ]]; then
        error "Size mismatch: original=$orig_size, decompressed=$verify_size"
        rm -f "$temp_iso"
        return 1
    fi
    
    # Cleanup
    rm -f "$temp_iso"
    
    success "Verification passed"
    return 0
}

archive_old_isos() {
    section "Archiving Old ISO Images"
    
    local build_dir="${PROJECT_ROOT}/build"
    
    if [[ ! -d "$build_dir" ]]; then
        error "Build directory not found: $build_dir"
        return 1
    fi
    
    # Check compression tool
    check_compression_tool
    
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
    
    # Determine which to keep
    local keep_start=0
    if [[ $KEEP_COUNT -gt 0 ]]; then
        keep_start=$KEEP_COUNT
        info "Keeping $KEEP_COUNT most recent ISO(s)"
        
        for ((i=0; i<keep_start && i<${#isos[@]}; i++)); do
            info "  Keeping: $(basename "${isos[$i]}")"
        done
    fi
    
    # Archive old ISOs
    local archived=0
    for ((i=keep_start; i<${#isos[@]}; i++)); do
        local iso="${isos[$i]}"
        local age
        
        age=$(get_file_age_days "$iso")
        
        if [[ $age -ge $AGE_DAYS ]]; then
            if [[ "$VERBOSE" == true ]]; then
                info "ISO is ${age} days old (threshold: ${AGE_DAYS})"
            fi
            
            if archive_iso "$iso"; then
                ((archived++))
            fi
        elif [[ "$VERBOSE" == true ]]; then
            info "Skipping $(basename "$iso") (only ${age} days old)"
        fi
    done
    
    if [[ $archived -eq 0 ]]; then
        info "No ISOs met archiving criteria"
    fi
    
    return 0
}

################################################################################
# Restore Operations
################################################################################

restore_iso() {
    local archive_name="$1"
    local archive_path
    local decompress_cmd
    local output_name
    local output_path
    
    section "Restoring ISO from Archive"
    
    # Find archive
    if [[ -f "$archive_name" ]]; then
        archive_path="$archive_name"
    elif [[ -f "${ARCHIVE_DIR}/${archive_name}" ]]; then
        archive_path="${ARCHIVE_DIR}/${archive_name}"
    else
        error "Archive not found: $archive_name"
        return 1
    fi
    
    info "Restoring: $(basename "$archive_path")"
    
    # Determine output name
    output_name=$(basename "$archive_path")
    output_name="${output_name%.gz}"
    output_name="${output_name%.xz}"
    output_name="${output_name%.zst}"
    output_path="${PROJECT_ROOT}/build/${output_name}"
    
    # Check if already exists
    if [[ -f "$output_path" ]]; then
        warning "ISO already exists: $output_path"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Restore cancelled"
            return 0
        fi
    fi
    
    # Detect compression type from extension
    if [[ "$archive_path" =~ \.gz$ ]]; then
        decompress_cmd="gunzip"
    elif [[ "$archive_path" =~ \.xz$ ]]; then
        decompress_cmd="unxz"
    elif [[ "$archive_path" =~ \.zst$ ]]; then
        decompress_cmd="unzstd"
    else
        error "Unknown archive format"
        return 1
    fi
    
    # Decompress
    info "Decompressing..."
    if ! $decompress_cmd -c "$archive_path" > "$output_path"; then
        error "Failed to restore ISO"
        rm -f "$output_path"
        return 1
    fi
    
    # Restore checksums
    if [[ -f "${archive_path}.md5" ]]; then
        cp "${archive_path}.md5" "${output_path}.md5"
    fi
    
    if [[ -f "${archive_path}.sha256" ]]; then
        cp "${archive_path}.sha256" "${output_path}.sha256"
    fi
    
    # Report
    local size
    size=$(stat -c%s "$output_path")
    success "Restored: $output_name"
    info "  Size: $(human_size "$size")"
    info "  Path: $output_path"
    
    return 0
}

################################################################################
# List Operations
################################################################################

list_archives() {
    section "Archived ISO Images"
    
    if [[ ! -d "$ARCHIVE_DIR" ]]; then
        info "No archive directory found"
        return 0
    fi
    
    # Find archives
    local archives=()
    while IFS= read -r archive; do
        archives+=("$archive")
    done < <(find "$ARCHIVE_DIR" -type f \( -name "*.iso.gz" -o -name "*.iso.xz" -o -name "*.iso.zst" \) 2>/dev/null | sort)
    
    if [[ ${#archives[@]} -eq 0 ]]; then
        info "No archived ISOs found"
        return 0
    fi
    
    info "Found ${#archives[@]} archived ISO(s):"
    echo ""
    
    local total_size=0
    for archive in "${archives[@]}"; do
        local name
        local size
        local mtime
        local age
        
        name=$(basename "$archive")
        size=$(stat -c%s "$archive")
        mtime=$(stat -c%Y "$archive")
        age=$(get_file_age_days "$archive")
        
        ((total_size += size))
        
        printf "  %-50s %10s  (%d days old)\n" \
            "$name" \
            "$(human_size "$size")" \
            "$age"
        
        if [[ "$VERBOSE" == true ]]; then
            # Show checksums
            if [[ -f "${archive}.md5" ]]; then
                echo "    MD5:    $(cat "${archive}.md5")"
            fi
            if [[ -f "${archive}.sha256" ]]; then
                echo "    SHA256: $(cat "${archive}.sha256")"
            fi
            echo ""
        fi
    done
    
    echo ""
    info "Total archived size: $(human_size "$total_size")"
    
    return 0
}

################################################################################
# Main Entry Point
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS ISO Archive Tool"
    
    case "$MODE" in
        archive)
            info "Archive mode: compress ISOs older than ${AGE_DAYS} days"
            info "Compression: $COMPRESS_TYPE (level $COMPRESS_LEVEL)"
            info "Archive dir: $ARCHIVE_DIR"
            [[ $KEEP_COUNT -gt 0 ]] && info "Keep unarchived: $KEEP_COUNT most recent"
            echo ""
            
            archive_old_isos
            
            # Summary
            local end_time
            end_time=$(date +%s)
            
            echo ""
            section "Archive Summary"
            
            if [[ "$DRY_RUN" == true ]]; then
                info "ISOs to archive: $ISOS_ARCHIVED (dry-run mode)"
            else
                success "ISOs archived: $ISOS_ARCHIVED"
                if [[ $SPACE_SAVED -gt 0 ]]; then
                    success "Space saved: $(human_size $SPACE_SAVED)"
                fi
            fi
            
            info "Time elapsed: $(elapsed_time "$start_time" "$end_time")"
            ;;
            
        restore)
            restore_iso "$RESTORE_ISO"
            ;;
            
        list)
            list_archives
            ;;
            
        *)
            error "Invalid mode: $MODE"
            return 1
            ;;
    esac
    
    return 0
}

################################################################################
# Execute
################################################################################

main "$@"
