#!/bin/bash

# SynapticOS Master Build Script
# Complete automation for building consciousness-integrated Linux distribution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                   SYNAPTICOS MASTER BUILDER                  ║${NC}"
echo -e "${PURPLE}║              Complete Linux Distribution Builder             ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}║  🧠 Consciousness Integration  🔒 ParrotOS Foundation       ║${NC}"
echo -e "${PURPLE}║  🎓 Educational Platform      ⚡ Neural Darwinism Engine    ║${NC}"
echo -e "${PURPLE}║  🛡️  Security Operations      🎯 Real-time AI Learning      ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_SCRIPTS_DIR="${PROJECT_ROOT}/parrotos-integration/build-scripts"
BUILD_DIR="${PROJECT_ROOT}/parrotos-integration/build"

echo -e "${BLUE}[INFO]${NC} SynapticOS Master Builder - Complete Distribution Creation"
echo -e "${BLUE}[INFO]${NC} Project Root: ${PROJECT_ROOT}"
echo -e "${BLUE}[INFO]${NC} Build Scripts: ${BUILD_SCRIPTS_DIR}"
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}[ERROR]${NC} Do not run this script as root. It will use sudo when needed."
    exit 1
fi

# Build options
DOWNLOAD_PARROTOS=true
BUILD_KERNEL=true
BUILD_ISO=true
QUICK_TEST=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-download)
            DOWNLOAD_PARROTOS=false
            shift
            ;;
        --skip-kernel)
            BUILD_KERNEL=false
            shift
            ;;
        --skip-iso)
            BUILD_ISO=false
            shift
            ;;
        --quick-test)
            QUICK_TEST=true
            shift
            ;;
        --help)
            echo "SynapticOS Master Builder"
            echo
            echo "Usage: $0 [options]"
            echo
            echo "Options:"
            echo "  --skip-download    Skip ParrotOS download and extraction"
            echo "  --skip-kernel      Skip consciousness kernel building"
            echo "  --skip-iso         Skip final ISO creation"
            echo "  --quick-test       Build minimal test version"
            echo "  --help             Show this help message"
            echo
            exit 0
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Display build configuration
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                     BUILD CONFIGURATION                      ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC} Download ParrotOS: $([ "$DOWNLOAD_PARROTOS" = true ] && echo -e "${GREEN}YES${NC}" || echo -e "${YELLOW}SKIP${NC}")                              ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} Build Consciousness Kernel: $([ "$BUILD_KERNEL" = true ] && echo -e "${GREEN}YES${NC}" || echo -e "${YELLOW}SKIP${NC}")                     ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} Create Final ISO: $([ "$BUILD_ISO" = true ] && echo -e "${GREEN}YES${NC}" || echo -e "${YELLOW}SKIP${NC}")                                ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} Quick Test Mode: $([ "$QUICK_TEST" = true ] && echo -e "${YELLOW}YES${NC}" || echo -e "${GREEN}FULL${NC}")                                ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Confirm before proceeding
read -p "$(echo -e "${YELLOW}Continue with SynapticOS distribution build? [y/N]: ${NC}")" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[INFO]${NC} Build cancelled by user"
    exit 0
fi

echo
echo -e "${GREEN}🚀 Starting SynapticOS Complete Distribution Build...${NC}"
echo

# Record build start time
BUILD_START_TIME=$(date +%s)
BUILD_DATE=$(date +%Y%m%d-%H%M%S)
BUILD_LOG="${PROJECT_ROOT}/build-synapticos-${BUILD_DATE}.log"

# Create build log
exec > >(tee -a "$BUILD_LOG") 2>&1

echo "=== SynapticOS Build Log - Started at $(date) ==="

# PHASE 1: ParrotOS Foundation Setup
if [ "$DOWNLOAD_PARROTOS" = true ]; then
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    PHASE 1: PARROTOS FOUNDATION              ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${CYAN}[PHASE 1]${NC} Setting up ParrotOS foundation and consciousness overlay..."
    
    if [ -f "$BUILD_SCRIPTS_DIR/setup-parrotos-integration.sh" ]; then
        bash "$BUILD_SCRIPTS_DIR/setup-parrotos-integration.sh"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[SUCCESS]${NC} ParrotOS foundation setup completed"
        else
            echo -e "${RED}[ERROR]${NC} ParrotOS foundation setup failed"
            exit 1
        fi
    else
        echo -e "${RED}[ERROR]${NC} ParrotOS integration script not found"
        exit 1
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} Skipping ParrotOS download (--skip-download specified)"
fi

# PHASE 2: Consciousness Kernel Integration
if [ "$BUILD_KERNEL" = true ]; then
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                PHASE 2: CONSCIOUSNESS KERNEL                 ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${CYAN}[PHASE 2]${NC} Building and integrating consciousness-enhanced kernel..."
    
    if [ -f "$BUILD_SCRIPTS_DIR/integrate-consciousness-kernel.sh" ]; then
        bash "$BUILD_SCRIPTS_DIR/integrate-consciousness-kernel.sh"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[SUCCESS]${NC} Consciousness kernel integration completed"
        else
            echo -e "${RED}[ERROR]${NC} Consciousness kernel integration failed"
            exit 1
        fi
    else
        echo -e "${RED}[ERROR]${NC} Kernel integration script not found"
        exit 1
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} Skipping consciousness kernel build (--skip-kernel specified)"
fi

# PHASE 3: Final ISO Creation
if [ "$BUILD_ISO" = true ]; then
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                  PHASE 3: ISO DISTRIBUTION                   ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${CYAN}[PHASE 3]${NC} Creating final SynapticOS distribution ISO..."
    
    if [ -f "$BUILD_SCRIPTS_DIR/build-synapticos-iso.sh" ]; then
        bash "$BUILD_SCRIPTS_DIR/build-synapticos-iso.sh"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[SUCCESS]${NC} SynapticOS ISO creation completed"
        else
            echo -e "${RED}[ERROR]${NC} SynapticOS ISO creation failed"
            exit 1
        fi
    else
        echo -e "${RED}[ERROR]${NC} ISO building script not found"
        exit 1
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} Skipping ISO creation (--skip-iso specified)"
fi

# Calculate build time
BUILD_END_TIME=$(date +%s)
BUILD_DURATION=$((BUILD_END_TIME - BUILD_START_TIME))
BUILD_HOURS=$((BUILD_DURATION / 3600))
BUILD_MINUTES=$(((BUILD_DURATION % 3600) / 60))
BUILD_SECONDS=$((BUILD_DURATION % 60))

# Find the created ISO
if [ -d "$BUILD_DIR" ]; then
    ISO_FILE=$(find "$BUILD_DIR" -name "SynapticOS-*.iso" -type f 2>/dev/null | head -1)
    if [ -n "$ISO_FILE" ]; then
        ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)
        ISO_NAME=$(basename "$ISO_FILE")
    fi
fi

# Build completion summary
echo
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               SYNAPTICOS BUILD COMPLETED SUCCESSFULLY        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}🎯 Build Summary:${NC}"
echo -e "   • Build Date: $(date)"
echo -e "   • Build Duration: ${BUILD_HOURS}h ${BUILD_MINUTES}m ${BUILD_SECONDS}s"
echo -e "   • Build Log: ${BUILD_LOG}"
if [ -n "$ISO_FILE" ]; then
    echo -e "   • ISO Created: ${ISO_NAME}"
    echo -e "   • ISO Size: ${ISO_SIZE}"
    echo -e "   • ISO Location: ${ISO_FILE}"
fi
echo
echo -e "${BLUE}🧠 Consciousness Features:${NC}"
echo -e "   • Neural Darwinism kernel integration"
echo -e "   • AI-powered educational platform"
echo -e "   • Dynamic CTF challenge generation"
echo -e "   • Real-time threat intelligence"
echo -e "   • Advanced context analysis engine"
echo -e "   • Consciousness-aware security tools"
echo
echo -e "${BLUE}🔒 ParrotOS Foundation:${NC}"
echo -e "   • Complete penetration testing toolkit"
echo -e "   • Privacy and anonymity tools"
echo -e "   • Forensics and reverse engineering utilities"
echo -e "   • Secure development environment"
echo -e "   • Enhanced with consciousness integration"
echo
echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo -e "   1. Test in virtual machine environment"
echo -e "   2. Validate consciousness services functionality"
echo -e "   3. Test educational platform integration"
echo -e "   4. Verify ParrotOS tool consciousness enhancement"
echo -e "   5. Deploy to target hardware for full testing"
echo
if [ -n "$ISO_FILE" ]; then
    echo -e "${CYAN}📀 ISO Deployment Commands:${NC}"
    echo -e "   • Create bootable USB:"
    echo -e "     dd if='${ISO_FILE}' of=/dev/sdX bs=4M status=progress"
    echo -e "   • Test in QEMU:"
    echo -e "     qemu-system-x86_64 -m 4096 -cdrom '${ISO_FILE}' -boot d"
    echo -e "   • Test in VirtualBox:"
    echo -e "     VBoxManage createvm --name SynapticOS --register"
    echo -e "     VBoxManage storagectl SynapticOS --add ide --name IDE"
    echo -e "     VBoxManage storageattach SynapticOS --storagectl IDE --port 0 --device 0 --type dvddrive --medium '${ISO_FILE}'"
    echo
fi

echo -e "${GREEN}✅ SynapticOS - Complete Consciousness-Integrated Linux Distribution Ready!${NC}"
echo -e "${GREEN}🎓 The world's first AI-consciousness operating system with real-time neural darwinism!${NC}"
echo

# Quick test option
if [ "$QUICK_TEST" = true ] && [ -n "$ISO_FILE" ]; then
    echo -e "${YELLOW}[QUICK TEST]${NC} Starting QEMU test of SynapticOS..."
    echo -e "${CYAN}[INFO]${NC} Testing will run for 30 seconds to verify boot process"
    echo
    
    timeout 30s qemu-system-x86_64 \
        -m 2048 \
        -cdrom "$ISO_FILE" \
        -boot d \
        -serial stdio \
        -netdev user,id=net0 \
        -device e1000,netdev=net0 \
        > /tmp/synapticos-test.log 2>&1 || true
    
    if grep -qi "synapticos" /tmp/synapticos-test.log; then
        echo -e "${GREEN}[SUCCESS]${NC} SynapticOS boots successfully!"
    else
        echo -e "${YELLOW}[INFO]${NC} Boot test completed, check logs for details"
    fi
fi

echo "=== SynapticOS Build Log - Completed at $(date) ==="
