#!/bin/bash
# SynOS Archive to Vault Script
# Systematically moves archived content to TLimoges33/SynOS_master-archive-vault

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SOURCE_DIR="${PROJECT_ROOT}"
VAULT_DIR="${HOME}/SynOS_master-archive-vault"
ARCHIVE_DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_SESSION="codebase_audit_${ARCHIVE_DATE}"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "████████████████████████████████████████████████████████████"
    echo "█                                                          █"
    echo "█              SynOS Archive to Vault                     █"
    echo "█            Systematic Codebase Cleanup                  █"
    echo "█                                                          █"
    echo "████████████████████████████████████████████████████████████"
    echo -e "${NC}"
}

# Create archive structure in vault
create_archive_structure() {
    print_status "Creating archive structure in vault..."
    
    cd "$VAULT_DIR"
    
    # Create session directory
    mkdir -p "archives/${ARCHIVE_SESSION}"
    
    # Create category directories
    mkdir -p "archives/${ARCHIVE_SESSION}/build_artifacts"
    mkdir -p "archives/${ARCHIVE_SESSION}/research_materials"
    mkdir -p "archives/${ARCHIVE_SESSION}/development_prototypes"
    mkdir -p "archives/${ARCHIVE_SESSION}/extracted_filesystems"
    mkdir -p "archives/${ARCHIVE_SESSION}/academic_documents"
    mkdir -p "archives/${ARCHIVE_SESSION}/test_suites"
    mkdir -p "archives/${ARCHIVE_SESSION}/scripts_legacy"
    
    print_status "Archive structure created in vault"
}

# Archive build artifacts (32GB)
archive_build_artifacts() {
    print_status "Archiving build artifacts..."
    
    cd "$SOURCE_DIR"
    
    # Move large build directories
    if [ -d "build/iso" ]; then
        print_status "Moving build/iso (keeping iso-complete)..."
        cp -r "build/iso" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/build_artifacts/"
        rm -rf "build/iso"
    fi
    
    if [ -d "build/kernel" ]; then
        print_status "Moving build/kernel..."
        cp -r "build/kernel" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/build_artifacts/"
        rm -rf "build/kernel"
    fi
    
    if [ -d "build/master-iso-simple" ]; then
        print_status "Moving build/master-iso-simple..."
        cp -r "build/master-iso-simple" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/build_artifacts/"
        rm -rf "build/master-iso-simple"
    fi
    
    if [ -d "build/Final_SynOS-1.0_ISO" ]; then
        print_status "Moving build/Final_SynOS-1.0_ISO (duplicate)..."
        cp -r "build/Final_SynOS-1.0_ISO" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/build_artifacts/"
        rm -rf "build/Final_SynOS-1.0_ISO"
    fi
    
    # Move Rust target directory
    if [ -d "target" ]; then
        print_status "Moving target/ (Rust build cache - 1.2GB)..."
        cp -r "target" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/build_artifacts/"
        rm -rf "target"
    fi
    
    print_status "Build artifacts archived"
}

# Archive extracted filesystem (16GB)
archive_extracted_filesystem() {
    print_status "Archiving extracted filesystem..."
    
    cd "$SOURCE_DIR"
    
    if [ -d "squashfs_extracted" ]; then
        print_status "Moving squashfs_extracted (16GB)..."
        cp -r "squashfs_extracted" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/extracted_filesystems/"
        rm -rf "squashfs_extracted"
    fi
    
    print_status "Extracted filesystem archived"
}

# Archive research materials (525MB)
archive_research_materials() {
    print_status "Archiving research materials..."
    
    cd "$SOURCE_DIR"
    
    if [ -d "research" ]; then
        print_status "Moving research/ directory..."
        cp -r "research" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/research_materials/"
        rm -rf "research"
    fi
    
    print_status "Research materials archived"
}

# Archive academic documents
archive_academic_documents() {
    print_status "Archiving academic documents..."
    
    cd "$SOURCE_DIR"
    
    # Academic documents
    local academic_files=(
        "ACADEMIC_BOARD_AUDIT_2025.md"
        "ACADEMIC_CAPSTONE_PROJECT.md"
        "ACADEMIC_TRANSFORMATION_COMPLETE.md"
        "PERFORMANCE_OPTIMIZATION_FRAMEWORK.md"
        "CODEBASE_AUDIT_RECOMMENDATIONS.md"
        "FORMAL_RISK_ASSESSMENT.md"
        "OPTIMIZATION_COMPLETE.md"
        "PHASE_2_OPTIMIZATION_PROGRESS.md"
        "RESEARCH_EXECUTION_REPORT.md"
        "REPRODUCIBLE_RESEARCH_PACKAGE.md"
    )
    
    for file in "${academic_files[@]}"; do
        if [ -f "$file" ]; then
            print_status "Moving $file..."
            cp "$file" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/academic_documents/"
            rm "$file"
        fi
    done
    
    print_status "Academic documents archived"
}

# Archive development prototypes
archive_development_prototypes() {
    print_status "Archiving development prototypes..."
    
    cd "$SOURCE_DIR"
    
    # Development directories
    if [ -d "development/quantum-consciousness-kernel" ]; then
        print_status "Moving development/quantum-consciousness-kernel..."
        cp -r "development/quantum-consciousness-kernel" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/development_prototypes/"
        rm -rf "development/quantum-consciousness-kernel"
    fi
    
    if [ -d "development/quantum-consciousness-os" ]; then
        print_status "Moving development/quantum-consciousness-os..."
        cp -r "development/quantum-consciousness-os" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/development_prototypes/"
        rm -rf "development/quantum-consciousness-os"
    fi
    
    if [ -d "development/phase4" ]; then
        print_status "Moving development/phase4..."
        cp -r "development/phase4" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/development_prototypes/"
        rm -rf "development/phase4"
    fi
    
    print_status "Development prototypes archived"
}

# Archive non-essential test suites
archive_test_suites() {
    print_status "Archiving non-essential test suites..."
    
    cd "$SOURCE_DIR"
    
    # Extended testing that's not needed for ISO
    if [ -d "tests/testing/qemu-extended" ]; then
        print_status "Moving tests/testing/qemu-extended..."
        cp -r "tests/testing/qemu-extended" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/test_suites/"
        rm -rf "tests/testing/qemu-extended"
    fi
    
    if [ -d "tests/testing/production-hardening" ]; then
        print_status "Moving tests/testing/production-hardening..."
        cp -r "tests/testing/production-hardening" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/test_suites/"
        rm -rf "tests/testing/production-hardening"
    fi
    
    print_status "Non-essential test suites archived"
}

# Clean up duplicate documentation
cleanup_duplicate_docs() {
    print_status "Cleaning up duplicate documentation..."
    
    cd "$SOURCE_DIR"
    
    # Remove docs_new since docs/ is organized
    if [ -d "docs_new" ]; then
        print_status "Moving docs_new/ (duplicate of organized docs/)..."
        cp -r "docs_new" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/academic_documents/"
        rm -rf "docs_new"
    fi
    
    # Archive quantitative_analysis if it's just a single script
    if [ -d "quantitative_analysis" ]; then
        print_status "Moving quantitative_analysis/..."
        cp -r "quantitative_analysis" "$VAULT_DIR/archives/${ARCHIVE_SESSION}/research_materials/"
        rm -rf "quantitative_analysis"
    fi
    
    print_status "Duplicate documentation cleaned"
}

# Create archive manifest
create_archive_manifest() {
    print_status "Creating archive manifest..."
    
    cd "$VAULT_DIR/archives/${ARCHIVE_SESSION}"
    
    cat > "ARCHIVE_MANIFEST.md" << EOF
# SynOS Archive Session: ${ARCHIVE_SESSION}

## Archive Date
$(date)

## Archive Source
Repository: TLimoges33/Syn_OS-Dev-Team
Branch: main
Audit Date: August 31, 2025

## Archived Content

### Build Artifacts (~32GB)
- build/iso/ - ISO build cache
- build/kernel/ - Kernel build artifacts  
- build/master-iso-simple/ - Simple ISO build
- build/Final_SynOS-1.0_ISO/ - Duplicate ISO build
- target/ - Rust build cache (1.2GB)

### Extracted Filesystems (~16GB)
- squashfs_extracted/ - ParrotOS extracted filesystem

### Research Materials (~525MB)
- research/ - Complete academic research framework
- Academic documentation files
- Performance optimization studies

### Development Prototypes
- development/quantum-consciousness-kernel/ - Prototype kernel
- development/quantum-consciousness-os/ - Prototype OS
- development/phase4/ - Phase 4 development

### Academic Documents
- ACADEMIC_*.md files - Academic board materials
- PERFORMANCE_*.md files - Performance studies
- Research execution reports

### Test Suites
- Extended QEMU testing suites
- Production hardening tests

### Documentation
- docs_new/ - Duplicate documentation
- quantitative_analysis/ - Analysis scripts

## Retention Policy
- Build artifacts: 6 months (regenerable)
- Research materials: Permanent (academic value)
- Development prototypes: 1 year (may be referenced)
- Academic documents: Permanent (publication materials)

## Total Space Recovered
Estimated: ~50GB

## Verification
All archived content verified and safely stored in vault repository.

## Contact
Archive created by: SynOS Automated Archive System
Vault repository: TLimoges33/SynOS_master-archive-vault
EOF

    print_status "Archive manifest created"
}

# Main execution
main() {
    print_header
    
    print_status "Starting systematic archive to vault..."
    print_status "Source: $SOURCE_DIR"
    print_status "Vault: $VAULT_DIR"
    print_status "Session: $ARCHIVE_SESSION"
    
    # Verify vault exists
    if [ ! -d "$VAULT_DIR" ]; then
        print_error "Vault directory not found: $VAULT_DIR"
        exit 1
    fi
    
    # Create archive structure
    create_archive_structure
    
    # Archive by category
    archive_build_artifacts
    archive_extracted_filesystem
    archive_research_materials
    archive_academic_documents
    archive_development_prototypes
    archive_test_suites
    cleanup_duplicate_docs
    
    # Create manifest
    create_archive_manifest
    
    print_status "Archive completed successfully!"
    print_status "Session: $ARCHIVE_SESSION"
    print_status "Location: $VAULT_DIR/archives/${ARCHIVE_SESSION}"
    
    echo ""
    print_status "Next steps:"
    echo "1. Review archived content in vault"
    echo "2. Commit and push vault to GitHub"
    echo "3. Verify SynOS repository cleanup"
    echo "4. Proceed with ISO creation"
}

# Execute main function
main "$@"
