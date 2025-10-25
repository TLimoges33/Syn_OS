#!/usr/bin/env bash
################################################################################
# SynOS ULTIMATE ISO Enhancement System
# Main Orchestrator - Runs all 6 phases
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
BUILD_DIR="$PROJECT_ROOT/build"
CHROOT_DIR="${1:-$BUILD_DIR/synos-v1.0/chroot}"

source "$SCRIPT_DIR/enhancement-utils.sh"

################################################################################
# CONFIGURATION
################################################################################

PHASES=(
    "enhance-phase1-repos-tools.sh|Repository Setup & Tool Installation|30"
    "enhance-phase2-core-integration.sh|Core System Integration|10"
    "enhance-phase3-branding.sh|Branding & Visual Customization|10"
    "enhance-phase4-configuration.sh|Configuration Management|10"
    "enhance-phase5-demo-docs.sh|Demo Application & Documentation|15"
    "enhance-phase6-iso-rebuild.sh|ISO Rebuild & Finalization|45"
)

TOTAL_PHASES=${#PHASES[@]}

################################################################################
# PRE-FLIGHT CHECKS
################################################################################

preflight_checks() {
    section "Pre-Flight Checks"

    # Check root
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root"
        echo "Try: sudo $0"
        exit 1
    fi
    log "Running as root ✓"

    # Check chroot directory
    if [ ! -d "$CHROOT_DIR" ]; then
        error "Chroot directory not found: $CHROOT_DIR"
        echo ""
        echo "Expected structure:"
        echo "  $BUILD_DIR/synos-v1.0/chroot/"
        echo ""
        echo "If your chroot is elsewhere, specify it:"
        echo "  sudo $0 /path/to/chroot"
        exit 1
    fi
    log "Chroot directory found ✓"

    # Check disk space (need at least 15GB)
    local available
    available=$(df -BG "$BUILD_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available" -lt 15 ]; then
        error "Insufficient disk space: ${available}GB available, 15GB required"
        exit 1
    fi
    log "Disk space sufficient: ${available}GB available ✓"

    # Check required commands
    local required_cmds=("chroot" "mksquashfs" "xorriso" "git" "pip3")
    for cmd in "${required_cmds[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command not found: $cmd"
            echo "Install with: apt-get install squashfs-tools xorriso git python3-pip"
            exit 1
        fi
    done
    log "Required commands available ✓"

    # Check phase scripts exist
    for phase_info in "${PHASES[@]}"; do
        local script="${phase_info%%|*}"
        if [ ! -f "$SCRIPT_DIR/$script" ]; then
            error "Phase script not found: $script"
            exit 1
        fi
    done
    log "All phase scripts found ✓"

    echo ""
}

################################################################################
# DISPLAY ENHANCEMENT PLAN
################################################################################

show_plan() {
    print_banner

    cat <<EOF

${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗
║                  ENHANCEMENT PLAN                          ║
╚════════════════════════════════════════════════════════════╝${RESET}

${BOLD}This enhancement will:${RESET}

${GREEN}Phase 1: Repository Setup & Tool Installation (30 min)${RESET}
  • Add ParrotOS, Kali Linux repositories
  • Install 500+ security tools from all sources
  • Execute your custom tools/security-tools/install-all.sh
  • Clone essential GitHub repositories
  • Install Python security packages

${GREEN}Phase 2: Core System Integration (10 min)${RESET}
  • Integrate core/ai/ AI consciousness services
  • Apply core/security/ security modules
  • Set up core/services/ system services
  • Apply config/ templates and configurations
  • Enable kernel optimizations

${GREEN}Phase 3: Branding & Visual Customization (10 min)${RESET}
  • Install SynOS GRUB theme
  • Configure Plymouth boot splash
  • Apply Windows 10 Dark + ARK-Dark themes
  • Install nuclear/space wallpapers
  • Configure branded login screen

${GREEN}Phase 4: Configuration Management (10 min)${RESET}
  • Create organized "SynOS Tools" menu (11 categories)
  • Generate desktop entries for all tools
  • Create desktop shortcuts
  • Configure MATE desktop (matching your system)
  • Set up system defaults

${GREEN}Phase 5: Demo Application & Documentation (15 min)${RESET}
  • Create fully functional synos-demo application
  • Pre-install GitHub security repositories
  • Generate comprehensive documentation
  • Create quick reference guides

${GREEN}Phase 6: ISO Rebuild & Finalization (45 min)${RESET}
  • Clean and optimize chroot
  • Build compressed squashfs filesystem
  • Generate ISO with custom GRUB
  • Create checksums (MD5, SHA256)
  • Generate release notes

${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗
║                    WHAT YOU'LL GET                         ║
╚════════════════════════════════════════════════════════════╝${RESET}

${GREEN}✓${RESET} Production-ready SynOS ISO (4.5-5GB)
${GREEN}✓${RESET} 500+ security tools from ParrotOS + Kali + GitHub
${GREEN}✓${RESET} Organized menu with 11 tool categories
${GREEN}✓${RESET} Full SynOS branding (GRUB, Plymouth, themes)
${GREEN}✓${RESET} Your exact desktop config (Windows 10 Dark, space.jpg)
${GREEN}✓${RESET} Functional demo app (no more "coming soon")
${GREEN}✓${RESET} Pre-installed GitHub repos and documentation
${GREEN}✓${RESET} AI/consciousness integration
${GREEN}✓${RESET} Complete showcase of your project

${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗
║                    TIME ESTIMATE                           ║
╚════════════════════════════════════════════════════════════╝${RESET}

${YELLOW}Total Time: ~2 hours${RESET} (depends on system speed)
  • Phase 1: 30 minutes (tool downloads)
  • Phase 2-5: 45 minutes
  • Phase 6: 45 minutes (squashfs compression + ISO build)

${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗
║                  CONFIGURATION                             ║
╚════════════════════════════════════════════════════════════╝${RESET}

Chroot: ${CYAN}$CHROOT_DIR${RESET}
Build:  ${CYAN}$BUILD_DIR${RESET}
Output: ${CYAN}$BUILD_DIR/SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso${RESET}

EOF
}

################################################################################
# RUN PHASE
################################################################################

run_phase() {
    local phase_num=$1
    local script=$2
    local description=$3
    local estimated_min=$4

    section "Phase $phase_num/$TOTAL_PHASES: $description"

    info "Estimated time: ~${estimated_min} minutes"
    echo ""

    timer_start

    # Make script executable
    chmod +x "$SCRIPT_DIR/$script"

    # Run phase script
    if bash "$SCRIPT_DIR/$script" "$CHROOT_DIR"; then
        timer_end "Phase $phase_num"
        log "Phase $phase_num completed successfully!"
    else
        error "Phase $phase_num failed!"
        echo ""
        echo "Check the output above for errors."
        echo "You can manually run the phase with:"
        echo "  sudo bash $SCRIPT_DIR/$script $CHROOT_DIR"
        exit 1
    fi

    echo ""
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    # Pre-flight checks
    preflight_checks

    # Show plan
    show_plan

    # Confirm
    echo ""
    read -p "${YELLOW}Ready to begin? This will take ~2 hours. Continue? [y/N]:${RESET} " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Enhancement cancelled."
        exit 0
    fi

    echo ""
    log "Starting SynOS ULTIMATE enhancement..."
    echo ""

    # Start overall timer
    OVERALL_START=$(date +%s)

    # Mount chroot for phases that need it
    mount_chroot "$CHROOT_DIR"

    # Run all phases
    local phase_num=1
    for phase_info in "${PHASES[@]}"; do
        IFS='|' read -r script description estimated_min <<< "$phase_info"

        run_phase "$phase_num" "$script" "$description" "$estimated_min"

        phase_num=$((phase_num + 1))
    done

    # Unmount chroot
    unmount_chroot "$CHROOT_DIR"

    # Calculate total time
    local overall_end
    overall_end=$(date +%s)
    local total_duration=$((overall_end - OVERALL_START))
    local hours=$((total_duration / 3600))
    local minutes=$(((total_duration % 3600) / 60))

    # Success summary
    cat <<EOF

${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                  ✓ ENHANCEMENT COMPLETE! ✓                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝${RESET}

${BOLD}Total Time:${RESET} ${hours}h ${minutes}m

${BOLD}Enhanced ISO Location:${RESET}
  ${CYAN}$BUILD_DIR/SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso${RESET}

${BOLD}Checksums:${RESET}
  ${CYAN}$BUILD_DIR/SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso.md5${RESET}
  ${CYAN}$BUILD_DIR/SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso.sha256${RESET}

${BOLD}Release Notes:${RESET}
  ${CYAN}$BUILD_DIR/RELEASE_NOTES.md${RESET}

${GREEN}${BOLD}WHAT'S NEW:${RESET}
${GREEN}✓${RESET} 500+ security tools from ParrotOS + Kali + GitHub
${GREEN}✓${RESET} Organized "SynOS Tools" menu with 11 categories
${GREEN}✓${RESET} Full branding (GRUB, Plymouth, themes, wallpapers)
${GREEN}✓${RESET} Your desktop config (Windows 10 Dark, ARK-Dark, space.jpg)
${GREEN}✓${RESET} Fully functional synos-demo application
${GREEN}✓${RESET} Pre-installed GitHub security repos
${GREEN}✓${RESET} AI consciousness integration
${GREEN}✓${RESET} Complete documentation

${YELLOW}${BOLD}NEXT STEPS:${RESET}

${BOLD}1. Test the ISO:${RESET}
   qemu-system-x86_64 -m 4G -cdrom $BUILD_DIR/SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso -boot d

${BOLD}2. Write to USB:${RESET}
   sudo dd if=$BUILD_DIR/SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso of=/dev/sdX bs=4M status=progress

${BOLD}3. Verify checksums:${RESET}
   cd $BUILD_DIR
   md5sum -c SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso.md5
   sha256sum -c SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso.sha256

${BOLD}4. Boot and enjoy:${RESET}
   • Select "SynOS 1.0.0 Ultimate (Live)"
   • Run: synos-demo
   • Access: Applications → SynOS Tools

${GREEN}${BOLD}Congratulations! Your SynOS Ultimate ISO is ready! 🎉${RESET}

EOF
}

main "$@"
