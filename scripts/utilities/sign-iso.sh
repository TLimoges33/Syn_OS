#!/usr/bin/env bash
################################################################################
# SynOS ISO Signing Tool
# 
# GPG-based digital signing and verification of ISO images.
#
# Usage:
#   ./scripts/utilities/sign-iso.sh [OPTIONS] <ISO_FILE>
#
# Options:
#   --sign            Sign the ISO file
#   --verify          Verify ISO signature
#   --batch           Batch sign multiple ISOs
#   --key-id ID       GPG key ID to use (default: auto-detect)
#   --output FILE     Output signature file (default: <ISO>.sig)
#   --armor           Create ASCII-armored signature
#   --detach          Create detached signature (default)
#   --check-key       Check if signing key exists
#   --list-keys       List available GPG keys
#   --help            Show this help message
#
# Examples:
#   # Sign an ISO
#   ./scripts/utilities/sign-iso.sh --sign build/SynOS-v1.0.0.iso
#
#   # Verify signature
#   ./scripts/utilities/sign-iso.sh --verify build/SynOS-v1.0.0.iso
#
#   # Sign with specific key
#   ./scripts/utilities/sign-iso.sh --sign --key-id ABC123 build/SynOS.iso
#
#   # Batch sign all ISOs in directory
#   ./scripts/utilities/sign-iso.sh --batch build/*.iso
#
# Exit Codes:
#   0 - Success
#   1 - Error during operation
#   2 - Verification failed
#   3 - No GPG key found
#
################################################################################

set -euo pipefail

# Determine project root first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PROJECT_ROOT

# Source shared library
source "${SCRIPT_DIR}/../lib/build-common.sh"

################################################################################
# Configuration
################################################################################

MODE=""  # sign, verify, batch, check-key, list-keys
ISO_FILE=""
KEY_ID=""
OUTPUT_FILE=""
ARMOR=false
DETACH=true

# Statistics
SIGNED_COUNT=0
VERIFIED_COUNT=0
FAILED_COUNT=0

################################################################################
# Argument Parsing
################################################################################

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --sign)
            MODE="sign"
            shift
            ;;
        --verify)
            MODE="verify"
            shift
            ;;
        --batch)
            MODE="batch"
            shift
            ;;
        --check-key)
            MODE="check-key"
            shift
            ;;
        --list-keys)
            MODE="list-keys"
            shift
            ;;
        --key-id)
            KEY_ID="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --armor)
            ARMOR=true
            shift
            ;;
        --detach)
            DETACH=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# \?//'
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Restore positional parameters
set -- "${POSITIONAL_ARGS[@]}"

# Validate mode
if [[ -z "$MODE" ]]; then
    error "No mode specified. Use --sign, --verify, --batch, --check-key, or --list-keys"
    exit 1
fi

################################################################################
# Helper Functions
################################################################################

check_gpg() {
    if ! command -v gpg &> /dev/null; then
        error "GPG not found. Install: apt install gnupg"
        exit 1
    fi
}

get_default_key() {
    # Try to get default signing key
    local key
    key=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | \
          grep -A 1 "^sec" | grep -v "^--" | head -1 | \
          awk '{print $1}' | cut -d'/' -f2 || echo "")
    
    if [[ -z "$key" ]]; then
        return 1
    fi
    
    echo "$key"
}

check_key_exists() {
    local key_id="$1"
    
    if gpg --list-secret-keys "$key_id" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

sign_iso() {
    local iso="$1"
    local sig_file="${2:-${iso}.sig}"
    local key_arg=""
    
    if [[ ! -f "$iso" ]]; then
        error "ISO file not found: $iso"
        return 1
    fi
    
    info "Signing: $(basename "$iso")"
    
    # Determine key to use
    if [[ -n "$KEY_ID" ]]; then
        if ! check_key_exists "$KEY_ID"; then
            error "GPG key not found: $KEY_ID"
            return 1
        fi
        key_arg="--default-key $KEY_ID"
    else
        # Try to get default key
        local default_key
        if default_key=$(get_default_key); then
            info "Using default key: $default_key"
            key_arg="--default-key $default_key"
        else
            error "No GPG key found. Create one with: gpg --gen-key"
            return 3
        fi
    fi
    
    # Build GPG command
    local gpg_cmd="gpg --detach-sign"
    
    if [[ "$ARMOR" == true ]]; then
        gpg_cmd="$gpg_cmd --armor"
        sig_file="${sig_file%.sig}.asc"
    fi
    
    gpg_cmd="$gpg_cmd $key_arg --output $sig_file $iso"
    
    # Sign the ISO
    if eval "$gpg_cmd" 2>&1; then
        success "Created signature: $(basename "$sig_file")"
        
        # Show signature info
        local sig_size
        sig_size=$(stat -c%s "$sig_file")
        info "  Signature size: $(human_size "$sig_size")"
        
        ((SIGNED_COUNT++))
        return 0
    else
        error "Failed to sign ISO"
        ((FAILED_COUNT++))
        return 1
    fi
}

verify_iso() {
    local iso="$1"
    local sig_file=""
    
    if [[ ! -f "$iso" ]]; then
        error "ISO file not found: $iso"
        return 1
    fi
    
    # Find signature file
    if [[ -f "${iso}.sig" ]]; then
        sig_file="${iso}.sig"
    elif [[ -f "${iso}.asc" ]]; then
        sig_file="${iso}.asc"
    else
        error "No signature file found for: $(basename "$iso")"
        error "Expected: ${iso}.sig or ${iso}.asc"
        return 2
    fi
    
    info "Verifying: $(basename "$iso")"
    info "Signature: $(basename "$sig_file")"
    
    # Verify signature
    if gpg --verify "$sig_file" "$iso" 2>&1; then
        success "✓ Signature valid for $(basename "$iso")"
        ((VERIFIED_COUNT++))
        return 0
    else
        error "✗ Signature verification failed"
        ((FAILED_COUNT++))
        return 2
    fi
}

batch_sign() {
    local files=("$@")
    
    if [[ ${#files[@]} -eq 0 ]]; then
        error "No files specified for batch signing"
        return 1
    fi
    
    section "Batch Signing ISOs"
    
    info "Files to sign: ${#files[@]}"
    echo ""
    
    for iso in "${files[@]}"; do
        if [[ ! -f "$iso" ]]; then
            warning "Skipping non-existent file: $iso"
            continue
        fi
        
        if [[ ! "$iso" =~ \.iso$ ]]; then
            warning "Skipping non-ISO file: $iso"
            continue
        fi
        
        sign_iso "$iso" || true
        echo ""
    done
}

list_keys() {
    section "Available GPG Keys"
    
    if ! gpg --list-secret-keys --keyid-format LONG 2>/dev/null; then
        info "No GPG keys found"
        echo ""
        info "Create a new key with: gpg --gen-key"
        return 0
    fi
}

check_signing_key() {
    section "GPG Key Check"
    
    if [[ -n "$KEY_ID" ]]; then
        info "Checking for key: $KEY_ID"
        
        if check_key_exists "$KEY_ID"; then
            success "✓ Key found: $KEY_ID"
            
            # Show key details
            gpg --list-secret-keys --keyid-format LONG "$KEY_ID" 2>/dev/null
            return 0
        else
            error "✗ Key not found: $KEY_ID"
            return 3
        fi
    else
        info "Checking for default signing key..."
        
        local default_key
        if default_key=$(get_default_key); then
            success "✓ Default key found: $default_key"
            
            # Show key details
            gpg --list-secret-keys --keyid-format LONG "$default_key" 2>/dev/null
            return 0
        else
            error "✗ No default signing key found"
            echo ""
            info "Create a new key with: gpg --gen-key"
            return 3
        fi
    fi
}

################################################################################
# Main Entry Point
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS ISO Signing Tool"
    
    # Check GPG availability
    check_gpg
    
    case "$MODE" in
        sign)
            if [[ ${#POSITIONAL_ARGS[@]} -eq 0 ]]; then
                error "No ISO file specified"
                exit 1
            fi
            
            ISO_FILE="${POSITIONAL_ARGS[0]}"
            
            section "Signing ISO Image"
            
            if [[ -n "$KEY_ID" ]]; then
                info "Key ID: $KEY_ID"
            fi
            if [[ -n "$OUTPUT_FILE" ]]; then
                info "Output: $OUTPUT_FILE"
            fi
            if [[ "$ARMOR" == true ]]; then
                info "Format: ASCII-armored"
            fi
            echo ""
            
            if sign_iso "$ISO_FILE" "$OUTPUT_FILE"; then
                local end_time
                end_time=$(date +%s)
                
                echo ""
                success "ISO signed successfully"
                info "Time elapsed: $(elapsed_time "$start_time" "$end_time")"
            else
                exit 1
            fi
            ;;
            
        verify)
            if [[ ${#POSITIONAL_ARGS[@]} -eq 0 ]]; then
                error "No ISO file specified"
                exit 1
            fi
            
            ISO_FILE="${POSITIONAL_ARGS[0]}"
            
            section "Verifying ISO Signature"
            echo ""
            
            if verify_iso "$ISO_FILE"; then
                local end_time
                end_time=$(date +%s)
                
                echo ""
                success "Signature verification passed"
                info "Time elapsed: $(elapsed_time "$start_time" "$end_time")"
            else
                exit 2
            fi
            ;;
            
        batch)
            if [[ ${#POSITIONAL_ARGS[@]} -eq 0 ]]; then
                error "No ISO files specified"
                exit 1
            fi
            
            batch_sign "${POSITIONAL_ARGS[@]}"
            
            local end_time
            end_time=$(date +%s)
            
            echo ""
            section "Batch Summary"
            
            success "Signed: $SIGNED_COUNT"
            if [[ $FAILED_COUNT -gt 0 ]]; then
                error "Failed: $FAILED_COUNT"
            fi
            info "Time elapsed: $(elapsed_time "$start_time" "$end_time")"
            ;;
            
        check-key)
            check_signing_key
            exit $?
            ;;
            
        list-keys)
            list_keys
            ;;
            
        *)
            error "Invalid mode: $MODE"
            exit 1
            ;;
    esac
    
    return 0
}

################################################################################
# Execute
################################################################################

main "$@"
