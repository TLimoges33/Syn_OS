#!/usr/bin/env bash
################################################################################
# SynOS Enhancement Utility Functions
# Shared functions for all enhancement phases
################################################################################

# Color definitions
RESET="\033[0m"
BOLD="\033[1m"
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
BLUE="\033[94m"
MAGENTA="\033[95m"
CYAN="\033[96m"

################################################################################
# LOGGING FUNCTIONS
################################################################################

section() {
    echo -e "\n${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${CYAN}${BOLD}  $1${RESET}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
}

log() {
    echo -e "${GREEN}[✓]${RESET} $1"
}

warn() {
    echo -e "${YELLOW}[!]${RESET} $1"
}

error() {
    echo -e "${RED}[✗]${RESET} $1"
}

info() {
    echo -e "${BLUE}[i]${RESET} $1"
}

################################################################################
# PROGRESS FUNCTIONS
################################################################################

progress() {
    local current=$1
    local total=$2
    local task=$3
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))

    printf "\r${BLUE}[${RESET}"
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "${BLUE}]${RESET} ${percent}%% - ${task}"
}

spinner() {
    local pid=$1
    local task=$2
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'

    while kill -0 "$pid" 2>/dev/null; do
        local temp=${spinstr#?}
        printf "\r${MAGENTA}[%c]${RESET} %s" "$spinstr" "$task"
        spinstr=$temp${spinstr%"$temp"}
        sleep 0.1
    done
    printf "\r${GREEN}[✓]${RESET} %s\n" "$task"
}

################################################################################
# VALIDATION FUNCTIONS
################################################################################

check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root"
        exit 1
    fi
}

check_command() {
    local cmd=$1
    if ! command -v "$cmd" &> /dev/null; then
        error "Required command '$cmd' not found"
        return 1
    fi
    return 0
}

check_dir() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        error "Directory not found: $dir"
        return 1
    fi
    return 0
}

check_file() {
    local file=$1
    if [ ! -f "$file" ]; then
        error "File not found: $file"
        return 1
    fi
    return 0
}

################################################################################
# CHROOT HELPER FUNCTIONS
################################################################################

chroot_exec() {
    local chroot_dir=$1
    shift
    chroot "$chroot_dir" /bin/bash -c "$*"
}

mount_chroot() {
    local chroot_dir=$1

    info "Mounting virtual filesystems in chroot..."
    mount --bind /dev "$chroot_dir/dev"
    mount --bind /dev/pts "$chroot_dir/dev/pts"
    mount --bind /proc "$chroot_dir/proc"
    mount --bind /sys "$chroot_dir/sys"
    mount --bind /run "$chroot_dir/run"
}

unmount_chroot() {
    local chroot_dir=$1

    info "Unmounting virtual filesystems from chroot..."
    umount "$chroot_dir/dev/pts" 2>/dev/null || true
    umount "$chroot_dir/dev" 2>/dev/null || true
    umount "$chroot_dir/proc" 2>/dev/null || true
    umount "$chroot_dir/sys" 2>/dev/null || true
    umount "$chroot_dir/run" 2>/dev/null || true
}

################################################################################
# FILE OPERATIONS
################################################################################

safe_copy() {
    local src=$1
    local dst=$2

    if [ -e "$src" ]; then
        cp -r "$src" "$dst" 2>/dev/null || warn "Failed to copy $src to $dst"
        return 0
    else
        warn "Source not found: $src"
        return 1
    fi
}

backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "${file}.backup.$(date +%Y%m%d-%H%M%S)"
        log "Backed up: $file"
    fi
}

################################################################################
# PACKAGE MANAGEMENT
################################################################################

apt_install() {
    local chroot_dir=$1
    shift
    local packages="$*"

    info "Installing packages: $packages"
    chroot "$chroot_dir" bash -c "
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y -qq $packages 2>&1 | grep -v 'debconf: unable to initialize' || true
    "
}

pip_install() {
    local chroot_dir=$1
    shift
    local packages="$*"

    info "Installing Python packages: $packages"
    chroot "$chroot_dir" bash -c "
        pip3 install --break-system-packages --quiet $packages 2>/dev/null || true
    "
}

################################################################################
# SIZE AND SPACE FUNCTIONS
################################################################################

get_dir_size() {
    local dir=$1
    du -sh "$dir" 2>/dev/null | cut -f1
}

get_free_space() {
    local path=$1
    df -h "$path" | awk 'NR==2 {print $4}'
}

check_disk_space() {
    local path=$1
    local required_gb=$2

    local available=$(df -BG "$path" | awk 'NR==2 {print $4}' | sed 's/G//')

    if [ "$available" -lt "$required_gb" ]; then
        error "Insufficient disk space. Required: ${required_gb}GB, Available: ${available}GB"
        return 1
    fi

    log "Disk space check passed: ${available}GB available"
    return 0
}

################################################################################
# TIMING FUNCTIONS
################################################################################

timer_start() {
    TIMER_START=$(date +%s)
}

timer_end() {
    local task=${1:-"Operation"}
    local end=$(date +%s)
    local duration=$((end - TIMER_START))
    local hours=$((duration / 3600))
    local minutes=$(((duration % 3600) / 60))
    local seconds=$((duration % 60))

    if [ $hours -gt 0 ]; then
        log "$task completed in ${hours}h ${minutes}m ${seconds}s"
    elif [ $minutes -gt 0 ]; then
        log "$task completed in ${minutes}m ${seconds}s"
    else
        log "$task completed in ${seconds}s"
    fi
}

################################################################################
# SUMMARY FUNCTIONS
################################################################################

print_summary() {
    local title=$1
    shift
    local items=("$@")

    echo -e "\n${CYAN}${BOLD}╔════════════════════════════════════════════╗${RESET}"
    echo -e "${CYAN}${BOLD}║  ${title}${RESET}"
    echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════╝${RESET}\n"

    for item in "${items[@]}"; do
        echo -e "  ${GREEN}✓${RESET} $item"
    done
    echo
}

################################################################################
# ERROR HANDLING
################################################################################

cleanup_on_error() {
    error "An error occurred. Cleaning up..."

    # Unmount if chroot was mounted
    if [ -n "${CHROOT_DIR:-}" ]; then
        unmount_chroot "$CHROOT_DIR" 2>/dev/null || true
    fi

    exit 1
}

trap cleanup_on_error ERR

################################################################################
# VERIFICATION FUNCTIONS
################################################################################

verify_tool() {
    local chroot_dir=$1
    local tool=$2

    if chroot "$chroot_dir" which "$tool" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

verify_service() {
    local chroot_dir=$1
    local service=$2

    if [ -f "$chroot_dir/etc/systemd/system/$service" ]; then
        return 0
    else
        return 1
    fi
}

verify_file() {
    local chroot_dir=$1
    local file=$2

    if [ -f "$chroot_dir/$file" ]; then
        return 0
    else
        return 1
    fi
}

################################################################################
# BANNER FUNCTION
################################################################################

print_banner() {
    cat << "EOF"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗               ║
║   ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝               ║
║   ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗               ║
║   ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║               ║
║   ███████║   ██║   ██║ ╚████║╚██████╔╝███████║               ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝               ║
║                                                               ║
║           ULTIMATE ISO Enhancement System                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

EOF
}

################################################################################
# EXPORT ALL FUNCTIONS
################################################################################

export -f section log warn error info
export -f progress spinner
export -f check_root check_command check_dir check_file
export -f chroot_exec mount_chroot unmount_chroot
export -f safe_copy backup_file
export -f apt_install pip_install
export -f get_dir_size get_free_space check_disk_space
export -f timer_start timer_end
export -f print_summary cleanup_on_error
export -f verify_tool verify_service verify_file
export -f print_banner
