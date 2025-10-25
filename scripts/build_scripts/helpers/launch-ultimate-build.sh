#!/bin/bash

# SynOS Ultimate ISO Build Launcher
# Handles terminal issues and provides multiple execution methods

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

SCRIPT_DIR="/home/diablorain/Syn_OS/scripts/02-build/core"
BUILD_DIR="/home/diablorain/Syn_OS/build"
MONITOR_URL="http://localhost:8090"

print_launcher_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║              SynOS Ultimate ISO Build Launcher              ║"
    echo "║           Smart Execution with Terminal Resilience          ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_prerequisites() {
    echo -e "${BLUE}[INFO]${NC} Checking build prerequisites..."

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}[ERROR]${NC} This script must be run as root"
        echo -e "${YELLOW}[INFO]${NC} Run with: sudo $0"
        return 1
    fi

    # Check required files
    local required_files=(
        "$SCRIPT_DIR/ultimate-final-master-developer-v1.0-build.sh"
    )

    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}[SUCCESS]${NC} ✓ Found: $(basename "$file")"
        else
            echo -e "${RED}[ERROR]${NC} ✗ Missing: $file"
            return 1
        fi
    done

    # Check system requirements
    local required_tools=("python3" "debootstrap" "xorriso" "mksquashfs")
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" >/dev/null 2>&1; then
            echo -e "${GREEN}[SUCCESS]${NC} ✓ Tool available: $tool"
        else
            echo -e "${RED}[ERROR]${NC} ✗ Missing tool: $tool"
            echo -e "${YELLOW}[INFO]${NC} Install with: sudo apt update && sudo apt install debootstrap xorriso squashfs-tools"
            return 1
        fi
    done

    echo -e "${GREEN}[SUCCESS]${NC} All prerequisites satisfied"
    return 0
}

start_build_monitor() {
    echo -e "${CYAN}[MONITOR]${NC} Starting independent build monitor..."

    # Start monitor in background
    cd "$SCRIPT_DIR"
    nohup python3 build-monitor.py > /dev/null 2>&1 &
    local monitor_pid=$!

    echo -e "${GREEN}[SUCCESS]${NC} Build monitor started (PID: $monitor_pid)"
    echo -e "${CYAN}[INFO]${NC} Monitor dashboard: $MONITOR_URL"
    echo -e "${YELLOW}[INFO]${NC} Open browser to monitor build progress independently"

    # Wait a moment for monitor to start
    sleep 3

    # Test if monitor is responding
    if curl -s "$MONITOR_URL" >/dev/null 2>&1; then
        echo -e "${GREEN}[SUCCESS]${NC} ✓ Monitor is responding"
        return 0
    else
        echo -e "${YELLOW}[WARNING]${NC} Monitor may be starting up, check $MONITOR_URL manually"
        return 0
    fi
}

launch_iso_build() {
    echo -e "${CYAN}[BUILD]${NC} Launching SynOS Ultimate ISO Builder..."

    # Make sure script is executable
    chmod +x "$SCRIPT_DIR/ultimate-final-master-developer-v1.0-build.sh"

    # Create log directory
    mkdir -p "$BUILD_DIR/logs"

    local build_log="$BUILD_DIR/logs/launcher-$(date +%Y%m%d-%H%M%S).log"

    echo -e "${BLUE}[INFO]${NC} Build output will be logged to: $build_log"
    echo -e "${BLUE}[INFO]${NC} Monitor progress at: $MONITOR_URL"
    echo -e "${YELLOW}[INFO]${NC} This process may take 30-60 minutes"

    # Offer different execution methods
    echo ""
    echo -e "${CYAN}Choose execution method:${NC}"
    echo "1) Standard execution (recommended)"
    echo "2) Background execution with logging"
    echo "3) Terminal-independent execution"
    echo "4) Monitor only (don't start build)"
    echo ""
    read -p "Enter choice (1-4): " choice

    case $choice in
        1)
            echo -e "${BLUE}[INFO]${NC} Starting standard execution..."
            exec "$SCRIPT_DIR/ultimate-final-master-developer-v1.0-build.sh" 2>&1 | tee "$build_log"
            ;;
        2)
            echo -e "${BLUE}[INFO]${NC} Starting background execution..."
            nohup "$SCRIPT_DIR/ultimate-final-master-developer-v1.0-build.sh" > "$build_log" 2>&1 &
            local build_pid=$!
            echo -e "${GREEN}[SUCCESS]${NC} Build started in background (PID: $build_pid)"
            echo -e "${CYAN}[INFO]${NC} Monitor progress at: $MONITOR_URL"
            echo -e "${CYAN}[INFO]${NC} Check log: tail -f $build_log"
            ;;
        3)
            echo -e "${BLUE}[INFO]${NC} Starting terminal-independent execution..."
            setsid "$SCRIPT_DIR/ultimate-final-master-developer-v1.0-build.sh" > "$build_log" 2>&1 &
            echo -e "${GREEN}[SUCCESS]${NC} Build started independently"
            echo -e "${CYAN}[INFO]${NC} Monitor at: $MONITOR_URL"
            echo -e "${CYAN}[INFO]${NC} Check log: tail -f $build_log"
            ;;
        4)
            echo -e "${BLUE}[INFO]${NC} Monitor-only mode selected"
            echo -e "${CYAN}[INFO]${NC} Access monitor at: $MONITOR_URL"
            echo -e "${YELLOW}[INFO]${NC} To start build later, run: sudo $SCRIPT_DIR/ultimate-final-master-developer-v1.0-build.sh"
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Invalid choice, using standard execution"
            exec "$SCRIPT_DIR/ultimate-final-master-developer-v1.0-build.sh" 2>&1 | tee "$build_log"
            ;;
    esac
}

show_build_status() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    Build Status Summary                     ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check for existing build artifacts
    if [[ -d "$BUILD_DIR/synos-ultimate" ]]; then
        echo -e "${GREEN}[STATUS]${NC} Build environment exists"

        local log_file="$BUILD_DIR/synos-ultimate/ultimate-build.log"
        if [[ -f "$log_file" ]]; then
            echo -e "${GREEN}[STATUS]${NC} Build log found"
            echo -e "${BLUE}[INFO]${NC} Last 5 log entries:"
            tail -5 "$log_file" 2>/dev/null || echo "  (Log empty or unreadable)"
        fi

        # Check for ISO
        local iso_files=($(ls "$BUILD_DIR"/SynOS-v*.iso 2>/dev/null))
        if [[ ${#iso_files[@]} -gt 0 ]]; then
            echo -e "${GREEN}[STATUS]${NC} ✓ ISO file found: ${iso_files[-1]}"
            local iso_size=$(du -h "${iso_files[-1]}" 2>/dev/null | cut -f1)
            echo -e "${GREEN}[STATUS]${NC} ✓ ISO size: $iso_size"
        else
            echo -e "${YELLOW}[STATUS]${NC} No ISO file found yet"
        fi
    else
        echo -e "${YELLOW}[STATUS]${NC} No previous build found"
    fi

    # Monitor status
    if curl -s "$MONITOR_URL" >/dev/null 2>&1; then
        echo -e "${GREEN}[STATUS]${NC} ✓ Build monitor is running: $MONITOR_URL"
    else
        echo -e "${YELLOW}[STATUS]${NC} Build monitor not running"
    fi

    echo ""
}

cleanup_previous_builds() {
    echo -e "${YELLOW}[CLEANUP]${NC} Checking for previous build artifacts..."

    if [[ -d "$BUILD_DIR/synos-ultimate" ]]; then
        echo "Previous build directory found. Clean up before new build?"
        echo "1) Yes, clean up everything"
        echo "2) No, keep existing files"
        echo "3) Backup and clean"

        read -p "Enter choice (1-3): " cleanup_choice

        case $cleanup_choice in
            1)
                echo -e "${BLUE}[INFO]${NC} Cleaning up previous build..."
                rm -rf "$BUILD_DIR/synos-ultimate"
                echo -e "${GREEN}[SUCCESS]${NC} Cleanup completed"
                ;;
            2)
                echo -e "${BLUE}[INFO]${NC} Keeping existing files"
                ;;
            3)
                local backup_dir="$BUILD_DIR/backup-$(date +%Y%m%d-%H%M%S)"
                echo -e "${BLUE}[INFO]${NC} Creating backup: $backup_dir"
                mv "$BUILD_DIR/synos-ultimate" "$backup_dir"
                echo -e "${GREEN}[SUCCESS]${NC} Backup created and cleanup completed"
                ;;
        esac
    fi
}

show_post_build_info() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                   Build Process Information                 ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Monitor Dashboard:${NC} $MONITOR_URL"
    echo -e "${BLUE}Real-time Monitoring:${NC} System resources, build progress, logs"
    echo -e "${BLUE}Expected Duration:${NC} 30-60 minutes (depending on system)"
    echo -e "${BLUE}Final ISO Location:${NC} $BUILD_DIR/SynOS-v1.0-Developer-*.iso"
    echo ""
    echo -e "${YELLOW}Key Features of Ultimate Builder:${NC}"
    echo "  • Advanced system monitoring with emergency pause"
    echo "  • Automatic resource management and crash prevention"
    echo "  • Progressive build phases to prevent system overload"
    echo "  • Independent monitoring that works with terminal issues"
    echo "  • Recovery and cleanup mechanisms"
    echo ""
    echo -e "${CYAN}Monitoring Commands:${NC}"
    echo "  Monitor Web UI: firefox $MONITOR_URL"
    echo "  Check processes: ps aux | grep -E '(iso-builder|monitor)'"
    echo "  View build log: tail -f $BUILD_DIR/synos-ultimate/ultimate-build.log"
    echo "  System resources: top, htop, or df -h"
    echo ""
}

main() {
    print_launcher_banner

    if ! check_prerequisites; then
        echo -e "${RED}[ERROR]${NC} Prerequisites check failed"
        exit 1
    fi

    show_build_status

    if ! start_build_monitor; then
        echo -e "${YELLOW}[WARNING]${NC} Monitor start failed, continuing anyway"
    fi

    cleanup_previous_builds

    launch_iso_build

    show_post_build_info
}

# Execute main function
main "$@"
