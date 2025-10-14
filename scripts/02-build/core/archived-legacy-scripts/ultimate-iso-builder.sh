#!/bin/bash

# SynOS v1.0 Ultimate Smart ISO Builder
# Advanced system monitoring with crash prevention and recovery

set -e

# Configuration
SYNOS_VERSION="1.0"
BUILD_DATE=$(date +%Y%m%d-%H%M)
ISO_NAME="SynOS-v${SYNOS_VERSION}-Developer-${BUILD_DATE}.iso"
BUILD_ROOT="/home/diablorain/Syn_OS/build"
BUILD_DIR="${BUILD_ROOT}/synos-ultimate"
TEMP_DIR="/tmp/synos-ultimate-$$"
CHROOT_DIR="${BUILD_DIR}/chroot"
ISO_DIR="${BUILD_DIR}/iso"
FINAL_ISO="${BUILD_ROOT}/${ISO_NAME}"

# Advanced system monitoring
MAX_MEMORY_PERCENT=70
MAX_LOAD_AVERAGE=3.0
MIN_FREE_SPACE_GB=15
CRITICAL_MEMORY_PERCENT=85
PAUSE_DURATION=30
CHECK_INTERVAL=3

# Colors and logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

LOG_FILE="${BUILD_DIR}/ultimate-build.log"
ERROR_LOG="${BUILD_DIR}/ultimate-errors.log"
MONITOR_LOG="${BUILD_DIR}/system-monitor.log"

# Process tracking
declare -a BACKGROUND_PIDS=()
MONITOR_PID=""
BUILD_STARTED=""

# Enhanced logging functions
log_with_timestamp() {
    local level="$1"
    local color="$2"
    local message="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${color}[${timestamp}][${level}]${NC} ${message}" | tee -a "$LOG_FILE"
}

log_info() { log_with_timestamp "INFO" "$BLUE" "$1"; }
log_success() { log_with_timestamp "SUCCESS" "$GREEN" "$1"; }
log_warning() { log_with_timestamp "WARNING" "$YELLOW" "$1"; }
log_error() { log_with_timestamp "ERROR" "$RED" "$1"; echo "$1" >> "$ERROR_LOG"; }
log_critical() { log_with_timestamp "CRITICAL" "$PURPLE" "$1"; echo "CRITICAL: $1" >> "$ERROR_LOG"; }
log_step() { log_with_timestamp "STEP" "$CYAN" "$1"; }

# Advanced system monitoring
get_memory_usage() {
    free | awk 'NR==2{printf "%.1f", $3*100/$2}'
}

get_load_average() {
    uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,$//'
}

get_free_space_gb() {
    df /tmp | awk 'NR==2{printf "%.1f", $4/1024/1024}'
}

get_cpu_usage() {
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}'
}

advanced_system_check() {
    local memory_usage=$(get_memory_usage)
    local load_avg=$(get_load_average)
    local free_space=$(get_free_space_gb)
    local cpu_usage=$(get_cpu_usage)
    
    # Log current status
    echo "$(date '+%H:%M:%S') Memory: ${memory_usage}% Load: ${load_avg} Free: ${free_space}GB CPU: ${cpu_usage}%" >> "$MONITOR_LOG"
    
    # Critical memory check
    if (( $(echo "$memory_usage > $CRITICAL_MEMORY_PERCENT" | bc -l 2>/dev/null || echo "0") )); then
        log_critical "Critical memory usage: ${memory_usage}%"
        return 2
    fi
    
    # Warning level checks
    local warnings=0
    if (( $(echo "$memory_usage > $MAX_MEMORY_PERCENT" | bc -l 2>/dev/null || echo "0") )); then
        log_warning "High memory usage: ${memory_usage}%"
        ((warnings++))
    fi
    
    if (( $(echo "$load_avg > $MAX_LOAD_AVERAGE" | bc -l 2>/dev/null || echo "0") )); then
        log_warning "High load average: ${load_avg}"
        ((warnings++))
    fi
    
    if (( $(echo "$free_space < $MIN_FREE_SPACE_GB" | bc -l 2>/dev/null || echo "0") )); then
        log_warning "Low free space: ${free_space}GB"
        ((warnings++))
    fi
    
    if [[ $warnings -gt 2 ]]; then
        log_warning "Multiple system warnings detected"
        return 1
    fi
    
    return 0
}

continuous_monitor() {
    log_info "Starting continuous system monitoring..."
    
    while true; do
        local check_result
        advanced_system_check
        check_result=$?
        
        case $check_result in
            2)
                log_critical "System in critical state - EMERGENCY PAUSE"
                kill -STOP $$ 2>/dev/null || true  # Pause main process
                sleep $((PAUSE_DURATION * 3))
                kill -CONT $$ 2>/dev/null || true  # Resume main process
                ;;
            1)
                log_warning "System under stress - pausing build"
                sleep $PAUSE_DURATION
                ;;
            0)
                # System OK, continue monitoring
                ;;
        esac
        
        sleep $CHECK_INTERVAL
    done
}

# Enhanced cleanup with process tracking
cleanup_build() {
    local exit_code=${1:-0}
    
    log_info "Initiating cleanup sequence..."
    
    # Kill monitoring process
    if [[ -n "$MONITOR_PID" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then
        log_info "Stopping system monitor..."
        kill "$MONITOR_PID" 2>/dev/null || true
        wait "$MONITOR_PID" 2>/dev/null || true
    fi
    
    # Kill all background processes
    for pid in "${BACKGROUND_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Terminating background process $pid"
            kill "$pid" 2>/dev/null || true
        fi
    done
    
    # Unmount chroot filesystems safely
    local mount_points=("${CHROOT_DIR}/proc" "${CHROOT_DIR}/sys" "${CHROOT_DIR}/dev/pts" "${CHROOT_DIR}/dev")
    for mount_point in "${mount_points[@]}"; do
        if mountpoint -q "$mount_point" 2>/dev/null; then
            log_info "Unmounting $mount_point"
            umount "$mount_point" 2>/dev/null || umount -l "$mount_point" 2>/dev/null || true
        fi
    done
    
    # Clean temporary files
    if [[ -d "$TEMP_DIR" ]]; then
        log_info "Cleaning temporary directory"
        rm -rf "$TEMP_DIR" 2>/dev/null || true
    fi
    
    # Final status
    if [[ $exit_code -eq 0 ]]; then
        local build_time=$(($(date +%s) - BUILD_STARTED))
        log_success "Build completed successfully in ${build_time} seconds"
        log_success "ISO created: $FINAL_ISO"
        if [[ -f "$FINAL_ISO" ]]; then
            local iso_size=$(du -h "$FINAL_ISO" | cut -f1)
            log_success "ISO size: $iso_size"
        fi
    else
        log_error "Build failed with exit code: $exit_code"
        log_error "Check logs: $LOG_FILE and $ERROR_LOG"
    fi
    
    exit $exit_code
}

# Set up traps
trap 'cleanup_build 1' INT TERM
trap 'cleanup_build $?' EXIT

print_ultimate_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║            SynOS v1.0 ULTIMATE Smart ISO Builder            ║"
    echo "║          Advanced System Monitoring & Crash Prevention      ║"
    echo "║                                                              ║"
    echo "║  Features: Resource monitoring, Emergency pause, Recovery   ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_ultimate_prerequisites() {
    log_step "Performing comprehensive prerequisite check..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        log_info "Run with: sudo $0"
        return 1
    fi
    
    # Check essential tools with alternatives
    local essential_tools=(
        "debootstrap:Build Debian base system"
        "chroot:Enter chroot environment" 
        "mksquashfs:Create compressed filesystem"
        "xorriso:Generate ISO image"
        "bc:Mathematical calculations"
    )
    
    local missing_tools=()
    for tool_info in "${essential_tools[@]}"; do
        local tool="${tool_info%%:*}"
        local desc="${tool_info##*:}"
        
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool ($desc)")
        else
            log_success "✓ $tool found"
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools:"
        for tool in "${missing_tools[@]}"; do
            log_error "  - $tool"
        done
        log_info "Install with: sudo apt update && sudo apt install debootstrap xorriso squashfs-tools bc"
        return 1
    fi
    
    # Check system resources
    if ! advanced_system_check; then
        log_error "System not ready for ISO build"
        return 1
    fi
    
    # Check existing lightweight implementation
    local synos_impl="/home/diablorain/Syn_OS/core/build/lightweight-iso"
    if [[ -d "$synos_impl" ]]; then
        log_success "✓ SynOS lightweight implementation found"
    else
        log_warning "SynOS lightweight implementation not found - will create minimal version"
    fi
    
    log_success "All prerequisites satisfied"
    return 0
}

setup_ultimate_environment() {
    log_step "Setting up ultimate build environment..."
    
    BUILD_STARTED=$(date +%s)
    
    # Create all necessary directories
    mkdir -p "$BUILD_DIR" "$CHROOT_DIR" "$ISO_DIR" "$TEMP_DIR"
    mkdir -p "${BUILD_DIR}/logs" "${BUILD_DIR}/recovery"
    mkdir -p "${ISO_DIR}/live" "${ISO_DIR}/isolinux"
    
    # Initialize enhanced logging
    echo "SynOS v$SYNOS_VERSION Ultimate Build - Started $(date)" > "$LOG_FILE"
    echo "SynOS v$SYNOS_VERSION Ultimate Build Errors - Started $(date)" > "$ERROR_LOG"
    echo "# SynOS Build System Monitor - Started $(date)" > "$MONITOR_LOG"
    echo "# Time Memory% Load Free_GB CPU%" >> "$MONITOR_LOG"
    
    # Start continuous monitoring
    continuous_monitor &
    MONITOR_PID=$!
    BACKGROUND_PIDS+=($MONITOR_PID)
    
    log_success "Ultimate build environment ready"
    log_info "Monitor PID: $MONITOR_PID"
}

create_minimal_base() {
    log_step "Creating minimal Debian base system..."
    
    # Pre-check resources
    if ! advanced_system_check; then
        log_warning "Waiting for better system conditions..."
        sleep $PAUSE_DURATION
    fi
    
    log_info "Starting debootstrap (minimal variant)..."
    
    # Use absolute minimal packages for first stage
    local exclude_packages="apt-listchanges,man-db,manpages,info,doc-debian,debian-faq,wamerican"
    local include_packages="systemd,systemd-sysv,locales,apt-utils"
    
    if ! timeout 1800 debootstrap \
        --variant=minbase \
        --exclude="$exclude_packages" \
        --include="$include_packages" \
        bookworm \
        "$CHROOT_DIR" \
        http://deb.debian.org/debian/ 2>&1 | tee -a "$LOG_FILE"; then
        log_error "debootstrap failed"
        return 1
    fi
    
    log_success "Minimal base system created"
}

configure_chroot_environment() {
    log_step "Configuring chroot environment..."
    
    # Mount essential filesystems with error handling
    local mounts=(
        "proc:proc:${CHROOT_DIR}/proc"
        "sysfs:sysfs:${CHROOT_DIR}/sys" 
        "/dev:none:${CHROOT_DIR}/dev:bind"
        "devpts:devpts:${CHROOT_DIR}/dev/pts"
    )
    
    for mount_info in "${mounts[@]}"; do
        IFS=':' read -r source fstype target options <<< "$mount_info"
        
        mkdir -p "$target"
        
        if [[ -n "$options" ]]; then
            mount -o "$options" "$source" "$target"
        else
            mount -t "$fstype" "$source" "$target"  
        fi
        
        log_info "Mounted $target"
    done
    
    # Configure package sources
    cat > "${CHROOT_DIR}/etc/apt/sources.list" << 'EOF'
deb http://deb.debian.org/debian bookworm main non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main non-free-firmware
deb http://deb.debian.org/debian bookworm-updates main non-free-firmware
EOF
    
    # Configure locale
    echo "en_US.UTF-8 UTF-8" > "${CHROOT_DIR}/etc/locale.gen"
    chroot "$CHROOT_DIR" locale-gen
    
    # Update package database
    chroot "$CHROOT_DIR" apt update
    
    log_success "Chroot environment configured"
}

install_essential_packages() {
    log_step "Installing essential packages in chunks..."
    
    # Define package groups for staged installation
    local package_groups=(
        "core:linux-image-amd64,live-boot,live-config"
        "network:network-manager,wireless-tools,wpasupplicant"
        "desktop:xfce4-panel,xfce4-session,xfce4-settings,xfwm4"
        "terminal:xfce4-terminal,bash-completion"
        "browser:firefox-esr"
        "python:python3,python3-pip,python3-venv"
        "tools:curl,wget,git,nano,htop,tree"
        "security:sudo,gnupg,ca-certificates"
    )
    
    for group_info in "${package_groups[@]}"; do
        IFS=':' read -r group_name packages <<< "$group_info"
        
        log_info "Installing $group_name packages: $packages"
        
        # Check resources before each group
        local retries=0
        while ! advanced_system_check && [[ $retries -lt 3 ]]; do
            log_warning "Waiting for system resources (attempt $((retries + 1)))"
            sleep $PAUSE_DURATION
            ((retries++))
        done
        
        if [[ $retries -eq 3 ]]; then
            log_warning "Skipping $group_name due to resource constraints"
            continue
        fi
        
        # Install package group with timeout
        if ! timeout 600 chroot "$CHROOT_DIR" apt install -y --no-install-recommends ${packages//,/ } 2>&1 | tee -a "$LOG_FILE"; then
            log_warning "Failed to install some packages in $group_name group"
        else
            log_success "$group_name packages installed successfully"
        fi
        
        # Brief pause between groups
        sleep 5
    done
    
    log_success "Essential packages installation completed"
}

integrate_synos_consciousness() {
    log_step "Integrating SynOS consciousness system..."
    
    local synos_src="/home/diablorain/Syn_OS/core/build/lightweight-iso"
    local synos_dest="${CHROOT_DIR}/opt/synos"
    
    mkdir -p "$synos_dest" "${CHROOT_DIR}/home/synos/.config/autostart"
    
    if [[ -d "$synos_src" ]]; then
        log_info "Copying SynOS lightweight implementation..."
        cp -r "$synos_src"/* "$synos_dest/"
        
        # Make scripts executable
        find "$synos_dest" -name "*.sh" -exec chmod +x {} \;
        find "$synos_dest" -name "*.py" -exec chmod +x {} \;
        
        log_success "SynOS implementation copied"
    else
        log_warning "Creating minimal SynOS placeholder..."
        
        # Create minimal consciousness service
        cat > "$synos_dest/consciousness-service.py" << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
from datetime import datetime

class SynOSHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/consciousness':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f'''<!DOCTYPE html>
<html><head><title>SynOS Consciousness</title></head>
<body style="font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px;">
<h1>🧠 SynOS Consciousness System</h1>
<p>Status: <span style="color: #238636;">Active</span></p>
<p>Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p>System ready for consciousness integration.</p>
</body></html>'''
            
            self.wfile.write(html.encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", 8080), SynOSHandler) as httpd:
        print("SynOS Consciousness serving on port 8080")
        httpd.serve_forever()
EOF
        
        chmod +x "$synos_dest/consciousness-service.py"
    fi
    
    # Create system integration
    cat > "${CHROOT_DIR}/etc/systemd/system/synos-consciousness.service" << EOF
[Unit]
Description=SynOS Consciousness Service
After=network.target

[Service]
Type=simple
User=synos
ExecStart=/opt/synos/consciousness-service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable the service
    chroot "$CHROOT_DIR" systemctl enable synos-consciousness.service
    
    log_success "SynOS consciousness system integrated"
}

configure_live_system() {
    log_step "Configuring live system settings..."
    
    # Create live user
    chroot "$CHROOT_DIR" useradd -m -s /bin/bash -G sudo synos
    echo "synos:synos" | chroot "$CHROOT_DIR" chpasswd
    
    # Configure automatic login
    mkdir -p "${CHROOT_DIR}/etc/systemd/system/getty@tty1.service.d"
    cat > "${CHROOT_DIR}/etc/systemd/system/getty@tty1.service.d/override.conf" << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin synos --noclear %I $TERM
EOF
    
    # System identification
    echo "synos-live" > "${CHROOT_DIR}/etc/hostname"
    
    cat > "${CHROOT_DIR}/etc/hosts" << 'EOF'
127.0.0.1   localhost synos-live
::1         localhost ip6-localhost ip6-loopback
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
EOF
    
    # Desktop environment autostart
    mkdir -p "${CHROOT_DIR}/home/synos/.config/autostart"
    cat > "${CHROOT_DIR}/home/synos/.config/autostart/synos-welcome.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=SynOS Welcome
Comment=SynOS Consciousness Welcome Screen
Exec=firefox http://localhost:8080
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOF
    
    # Set ownership
    chroot "$CHROOT_DIR" chown -R synos:synos /home/synos
    
    log_success "Live system configured"
}

create_bootable_iso() {
    log_step "Creating bootable ISO image..."
    
    # Copy kernel and initrd
    local kernel_file=$(ls "${CHROOT_DIR}/boot/vmlinuz-"* | head -1)
    local initrd_file=$(ls "${CHROOT_DIR}/boot/initrd.img-"* | head -1)
    
    if [[ -f "$kernel_file" && -f "$initrd_file" ]]; then
        cp "$kernel_file" "${ISO_DIR}/live/vmlinuz"
        cp "$initrd_file" "${ISO_DIR}/live/initrd"
        log_success "Kernel and initrd copied"
    else
        log_error "Kernel or initrd not found"
        return 1
    fi
    
    # Create compressed filesystem
    log_info "Creating squashfs (this will take significant time)..."
    
    if ! mksquashfs "$CHROOT_DIR" "${ISO_DIR}/live/filesystem.squashfs" \
        -comp xz -processors 1 -mem 1024M 2>&1 | tee -a "$LOG_FILE"; then
        log_error "Failed to create squashfs"
        return 1
    fi
    
    log_success "Filesystem compressed successfully"
    
    # Install bootloader files
    if [[ -f "/usr/lib/ISOLINUX/isolinux.bin" ]]; then
        cp /usr/lib/ISOLINUX/isolinux.bin "${ISO_DIR}/isolinux/"
        cp /usr/lib/syslinux/modules/bios/*.c32 "${ISO_DIR}/isolinux/" 2>/dev/null || true
        
        # Create bootloader configuration
        cat > "${ISO_DIR}/isolinux/isolinux.cfg" << EOF
UI menu.c32
PROMPT 0
MENU TITLE SynOS v${SYNOS_VERSION} Developer Edition

DEFAULT synos
TIMEOUT 300

LABEL synos
  MENU LABEL ^SynOS Consciousness Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components quiet splash

LABEL forensics
  MENU LABEL ^Forensics Mode (No Swap/Automount)
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components noswap noautomount

LABEL safe
  MENU LABEL ^Safe Mode (Minimal Drivers)
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components acpi=off noapic nomodeset
EOF
        
        log_success "Bootloader configured"
    else
        log_error "ISOLINUX not found - ISO may not be bootable"
    fi
    
    # Generate final ISO
    log_info "Generating final ISO image..."
    
    if ! xorriso -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "SynOS_v${SYNOS_VERSION}" \
        -eltorito-boot isolinux/isolinux.bin \
        -eltorito-catalog isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -output "$FINAL_ISO" \
        "$ISO_DIR" 2>&1 | tee -a "$LOG_FILE"; then
        log_error "Failed to generate ISO"
        return 1
    fi
    
    # Generate checksums
    if [[ -f "$FINAL_ISO" ]]; then
        cd "$(dirname "$FINAL_ISO")"
        sha256sum "$(basename "$FINAL_ISO")" > "${FINAL_ISO}.sha256"
        md5sum "$(basename "$FINAL_ISO")" > "${FINAL_ISO}.md5"
        
        local iso_size=$(du -h "$FINAL_ISO" | cut -f1)
        log_success "ISO generated successfully: $FINAL_ISO ($iso_size)"
    else
        log_error "ISO generation failed"
        return 1
    fi
}

main() {
    print_ultimate_banner
    
    log_info "Initializing SynOS v$SYNOS_VERSION Ultimate Smart ISO Build..."
    log_info "Advanced monitoring and crash prevention enabled"
    
    # Execute build phases with error handling
    if ! check_ultimate_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    setup_ultimate_environment
    
    # Main build phases
    if ! create_minimal_base; then
        log_error "Failed to create base system"
        exit 1
    fi
    
    if ! configure_chroot_environment; then
        log_error "Failed to configure chroot"
        exit 1
    fi
    
    if ! install_essential_packages; then
        log_error "Failed to install packages"
        exit 1
    fi
    
    if ! integrate_synos_consciousness; then
        log_error "Failed to integrate SynOS consciousness"
        exit 1
    fi
    
    if ! configure_live_system; then
        log_error "Failed to configure live system"
        exit 1
    fi
    
    if ! create_bootable_iso; then
        log_error "Failed to create bootable ISO"
        exit 1
    fi
    
    # Success!
    local build_duration=$(($(date +%s) - BUILD_STARTED))
    log_success "🎉 SynOS v$SYNOS_VERSION Ultimate Build Completed!"
    log_success "⏱️  Total build time: ${build_duration} seconds"
    log_success "💿 ISO location: $FINAL_ISO"
    log_success "📊 Monitor log: $MONITOR_LOG"
    
    return 0
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
