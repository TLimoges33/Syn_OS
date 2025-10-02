#!/bin/bash
# SynOS Final Archive and Push Script
# Completes the archive process and pushes to vault

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "████████████████████████████████████████████████████████████"
    echo "█                                                          █"
    echo "█          SynOS Final Archive and Push to Vault          █"
    echo "█                                                          █"
    echo "████████████████████████████████████████████████████████████"
    echo -e "${NC}"
}

VAULT_DIR="${HOME}/SynOS_master-archive-vault"
SOURCE_DIR="${PROJECT_ROOT}"
ARCHIVE_SESSION="codebase_audit_20250831_172752"

print_header

# Move to vault directory
cd "$VAULT_DIR"

print_status "Current location: $(pwd)"
print_status "Adding archived content to git..."

# Add all changes
git add .

print_status "Checking git status..."
git status

print_status "Committing archive session..."
git commit -m "Archive Session: $ARCHIVE_SESSION

- Archived test suites (qemu-extended, production-hardening)
- Archived existing archive directory structure
- Created comprehensive archive manifest
- Date: $(date)
- Source: TLimoges33/Syn_OS-Dev-Team
- Session: $ARCHIVE_SESSION

Space optimization for ISO creation readiness."

print_status "Pushing to vault repository..."
git push origin main

print_status "Archive and push completed successfully!"

print_status "Returning to source directory for final cleanup..."
cd "$SOURCE_DIR"

print_status "Current SynOS repository state:"
echo "Directory: $(pwd)"
echo "Size analysis:"
du -sh . 2>/dev/null || echo "Size check completed"

print_status "Checking git status in source repository..."
git status --short | head -10

print_status "Archive process completed!"
echo ""
echo "✅ Vault Repository: https://github.com/TLimoges33/SynOS_master-archive-vault"
echo "✅ Archive Session: $ARCHIVE_SESSION"
echo "✅ SynOS repository optimized for ISO creation"
echo ""
echo "Next steps:"
echo "1. Review vault at: https://github.com/TLimoges33/SynOS_master-archive-vault"
echo "2. Proceed with SynOS ISO creation"
echo "3. Use: make iso or Final_SynOS-1.0_ISO/build_synos_iso.sh"
