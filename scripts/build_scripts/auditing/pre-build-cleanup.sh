#!/bin/bash
###############################################################################
# PRE-BUILD CLEANUP SCRIPT
###############################################################################
# Purpose: Clean old build artifacts and prepare environment for v1.0.0 ISO build
# Version: 1.0.0 (Neural Genesis)
# Author: SynOS Development Team
# Date: October 7, 2025
###############################################################################

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Project root detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}" || {
    log_error "Failed to change to project root: ${PROJECT_ROOT}"
    exit 1
}

log_info "🧹 SynOS Pre-Build Cleanup v1.0.0"
log_info "=================================="
echo

# Check if running as root (needed for some cleanup operations)
if [[ $EUID -ne 0 ]]; then
    log_warning "Not running as root. Some cleanup operations may require sudo."
    echo
fi

###############################################################################
# SECTION 1: DISK SPACE ANALYSIS
###############################################################################

log_info "📊 Analyzing disk space usage..."
echo

# Get current build directory size
if [[ -d "build" ]]; then
    BUILD_SIZE=$(du -sh build 2>/dev/null | cut -f1)
    log_info "Current build/ size: ${BUILD_SIZE}"
else
    log_info "build/ directory does not exist"
    BUILD_SIZE="0"
fi

# Get available disk space
AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
log_info "Available disk space: ${AVAILABLE_SPACE}"

echo
log_info "Breakdown of build/ subdirectories:"
if [[ -d "build" ]]; then
    du -sh build/* 2>/dev/null | while read -r size dir; do
        echo "  - ${dir}: ${size}"
    done
fi

echo

###############################################################################
# SECTION 2: IDENTIFY OLD BUILD ARTIFACTS
###############################################################################

log_info "🔍 Identifying old build artifacts..."
echo

OLD_ARTIFACTS=(
    "build/iso-analysis"
    "build/bulletproof-iso"
    "build/synos-iso"
    "build/lightweight-iso"
    "build/phase4-integration"
    "build/bare-metal-translation"
    "build/compressed-models"
    "build/iso-v1.0"
)

FOUND_ARTIFACTS=()
TOTAL_SIZE=0

for artifact in "${OLD_ARTIFACTS[@]}"; do
    if [[ -d "${artifact}" ]]; then
        SIZE=$(du -sm "${artifact}" 2>/dev/null | cut -f1)
        FOUND_ARTIFACTS+=("${artifact}")
        TOTAL_SIZE=$((TOTAL_SIZE + SIZE))
        log_warning "Found old artifact: ${artifact} (${SIZE}MB)"
    fi
done

if [[ ${#FOUND_ARTIFACTS[@]} -eq 0 ]]; then
    log_success "No old artifacts found! Build directory is clean."
else
    echo
    log_warning "Total old artifacts: ${#FOUND_ARTIFACTS[@]} directories"
    log_warning "Total space to free: ~${TOTAL_SIZE}MB (~$((TOTAL_SIZE / 1024))GB)"
fi

echo

###############################################################################
# SECTION 3: CHECK FOR SENSITIVE FILES
###############################################################################

log_info "🔒 Checking for uncommitted sensitive files..."
echo

# Check git status for staged files
if git rev-parse --git-dir > /dev/null 2>&1; then
    STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
    if [[ -n "${STAGED_FILES}" ]]; then
        log_warning "Staged files found:"
        echo "${STAGED_FILES}" | while read -r file; do
            if [[ "${file}" =~ \.(env|key|pem|secret|credential)$ ]]; then
                log_error "  ⚠️  SENSITIVE: ${file}"
            else
                echo "  - ${file}"
            fi
        done
        echo
    fi

    # Check for untracked sensitive files
    UNTRACKED_SENSITIVE=$(git ls-files --others --exclude-standard | grep -E '\.(env|key|pem|secret|credential)$' || true)
    if [[ -n "${UNTRACKED_SENSITIVE}" ]]; then
        log_error "⚠️  Untracked sensitive files detected:"
        echo "${UNTRACKED_SENSITIVE}" | while read -r file; do
            log_error "  - ${file}"
        done
        echo
        log_warning "These files should be in .gitignore!"
    else
        log_success "No untracked sensitive files detected."
    fi
else
    log_warning "Not in a git repository, skipping git checks."
fi

echo

###############################################################################
# SECTION 4: CLEANUP CONFIRMATION
###############################################################################

if [[ ${#FOUND_ARTIFACTS[@]} -eq 0 ]]; then
    log_success "✅ No cleanup needed! Build environment is ready."
    echo
    exit 0
fi

log_warning "⚠️  CLEANUP CONFIRMATION"
log_warning "======================="
echo
log_warning "The following directories will be DELETED:"
for artifact in "${FOUND_ARTIFACTS[@]}"; do
    log_warning "  - ${artifact}"
done
echo
log_warning "This will free up approximately ${TOTAL_SIZE}MB (~$((TOTAL_SIZE / 1024))GB)"
echo

read -p "$(echo -e "${YELLOW}Do you want to proceed with cleanup? (yes/no):${NC} ")" -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    log_info "Cleanup cancelled by user."
    exit 0
fi

###############################################################################
# SECTION 5: PERFORM CLEANUP
###############################################################################

log_info "🗑️  Starting cleanup..."
echo

CLEANUP_SUCCESS=0
CLEANUP_FAILED=0

for artifact in "${FOUND_ARTIFACTS[@]}"; do
    log_info "Removing: ${artifact}"
    if sudo rm -rf "${artifact}"; then
        log_success "  ✓ Removed"
        ((CLEANUP_SUCCESS++))
    else
        log_error "  ✗ Failed to remove"
        ((CLEANUP_FAILED++))
    fi
done

echo

###############################################################################
# SECTION 6: CREATE CLEAN BUILD DIRECTORIES
###############################################################################

log_info "📁 Creating clean build structure..."
echo

mkdir -p build/synos-ultimate
mkdir -p build/checksums
mkdir -p build/logs

log_success "Build directories created:"
log_success "  - build/synos-ultimate/    (ISO output)"
log_success "  - build/checksums/         (MD5, SHA256)"
log_success "  - build/logs/              (Build logs)"

echo

###############################################################################
# SECTION 7: POST-CLEANUP VERIFICATION
###############################################################################

log_info "✅ Post-cleanup verification..."
echo

# Get new build directory size
if [[ -d "build" ]]; then
    NEW_BUILD_SIZE=$(du -sh build 2>/dev/null | cut -f1)
    log_success "New build/ size: ${NEW_BUILD_SIZE}"
else
    NEW_BUILD_SIZE="0"
fi

# Get available disk space
NEW_AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
log_success "Available disk space: ${NEW_AVAILABLE_SPACE}"

echo

###############################################################################
# SECTION 8: FINAL REPORT
###############################################################################

log_success "🎉 CLEANUP COMPLETE!"
log_success "==================="
echo
log_success "Summary:"
log_success "  - Directories removed: ${CLEANUP_SUCCESS}"
if [[ ${CLEANUP_FAILED} -gt 0 ]]; then
    log_error "  - Failed removals: ${CLEANUP_FAILED}"
fi
log_success "  - Space freed: ~$((TOTAL_SIZE / 1024))GB"
log_success "  - Build environment: READY"
echo

log_info "Next steps:"
log_info "  1. Verify .gitignore is updated"
log_info "  2. Run: sudo ./scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh"
log_info "  3. Monitor: tail -f ./build/logs/build-*.log"
echo

log_success "✅ Ready to build SynOS v1.0.0 (Neural Genesis)!"
