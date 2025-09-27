#!/bin/bash
# SynOS eBPF Security Program Loader
# Complete security monitoring program deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EBPF_DIR="$SCRIPT_DIR"
BUILD_DIR="$EBPF_DIR/build"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_banner() {
    echo -e "${BLUE}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🛡️  SynOS eBPF Security Framework Loader 🛡️              ║
║                                                              ║
║  🔍 Real-time threat detection                               ║
║  🧠 Consciousness-integrated monitoring                      ║
║  📊 Performance optimization                                 ║
║  🎯 Educational security analytics                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root for eBPF program loading"
        exit 1
    fi

    # Check for required tools
    local required_tools=("clang" "llc" "bpftool" "mount")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool '$tool' not found"
            exit 1
        fi
    done

    # Check for BPF filesystem
    if ! mount | grep -q bpf; then
        log_info "Mounting BPF filesystem..."
        mount -t bpf bpf /sys/fs/bpf/ || {
            log_error "Failed to mount BPF filesystem"
            exit 1
        }
    fi

    # Check kernel version
    local kernel_version=$(uname -r)
    log_info "Kernel version: $kernel_version"

    # Create build directory
    mkdir -p "$BUILD_DIR"

    log_success "Prerequisites check completed"
}

compile_security_programs() {
    log_info "Compiling eBPF security programs..."

    local programs=(
        "security/security_monitor.c"
        "memory/memory_monitor_simple.c"
        "process/process_monitor_simple.c"
        "network/network_monitor.c"
    )

    for program in "${programs[@]}"; do
        local source_file="$EBPF_DIR/$program"
        local program_name=$(basename "$program" .c)
        local object_file="$BUILD_DIR/${program_name}.o"

        if [[ ! -f "$source_file" ]]; then
            log_warning "Source file not found: $source_file"
            continue
        fi

        log_info "Compiling $program_name..."

        # Compile with clang
        clang -O2 -target bpf -c "$source_file" -o "$object_file" \
            -I/usr/include/$(uname -m)-linux-gnu \
            -I/usr/src/linux-headers-$(uname -r)/include \
            -I/usr/src/linux-headers-$(uname -r)/arch/x86/include \
            -I/usr/src/linux-headers-$(uname -r)/arch/x86/include/generated \
            2>/dev/null || {
            log_warning "Failed to compile $program_name with clang, trying gcc-based approach..."

            # Alternative compilation approach
            clang -O2 -target bpf -c "$source_file" -o "$object_file" \
                -D__KERNEL__ -D__BPF_TRACING__ \
                -Wno-unused-value -Wno-pointer-sign \
                -Wno-compare-distinct-pointer-types || {
                log_error "Failed to compile $program_name"
                continue
            }
        }

        if [[ -f "$object_file" ]]; then
            log_success "Compiled $program_name successfully"
        else
            log_error "Compilation failed for $program_name"
        fi
    done
}

load_security_programs() {
    log_info "Loading eBPF security programs into kernel..."

    local programs=(
        "security_monitor"
        "memory_monitor_simple"
        "process_monitor_simple"
        "network_monitor"
    )

    for program in "${programs[@]}"; do
        local object_file="$BUILD_DIR/${program}.o"
        local pin_path="/sys/fs/bpf/synos_${program}"

        if [[ ! -f "$object_file" ]]; then
            log_warning "Object file not found: $object_file"
            continue
        fi

        log_info "Loading $program..."

        # Load program with bpftool
        bpftool prog load "$object_file" "$pin_path" type kprobe 2>/dev/null || {
            # Try alternative loading methods
            bpftool prog load "$object_file" "$pin_path" type tracepoint 2>/dev/null || {
                log_warning "Standard loading failed for $program, trying force load..."

                # Force load (may not work on all kernels)
                bpftool prog load "$object_file" "$pin_path" 2>/dev/null || {
                    log_error "Failed to load $program"
                    continue
                }
            }
        }

        if [[ -e "$pin_path" ]]; then
            log_success "Loaded $program successfully"

            # Attach program to appropriate hooks
            case "$program" in
                "security_monitor")
                    attach_security_monitor "$pin_path"
                    ;;
                "memory_monitor_simple")
                    attach_memory_monitor "$pin_path"
                    ;;
                "process_monitor_simple")
                    attach_process_monitor "$pin_path"
                    ;;
                "network_monitor")
                    attach_network_monitor "$pin_path"
                    ;;
            esac
        else
            log_error "Failed to pin $program"
        fi
    done
}

attach_security_monitor() {
    local pin_path="$1"
    log_info "Attaching security monitor hooks..."

    # Attach to various tracepoints and kprobes
    local attach_points=(
        "tracepoint:syscalls:sys_enter_openat"
        "tracepoint:syscalls:sys_enter_execve"
        "tracepoint:sched:sched_process_exit"
        "kprobe:tcp_connect"
        "kprobe:vfs_read"
        "kprobe:vfs_write"
    )

    for attach_point in "${attach_points[@]}"; do
        bpftool prog attach "$pin_path" "$attach_point" 2>/dev/null || {
            log_warning "Could not attach to $attach_point"
        }
    done
}

attach_memory_monitor() {
    local pin_path="$1"
    log_info "Attaching memory monitor..."

    bpftool prog attach "$pin_path" kprobe:__alloc_pages_nodemask 2>/dev/null || {
        log_warning "Could not attach memory monitor"
    }
}

attach_process_monitor() {
    local pin_path="$1"
    log_info "Attaching process monitor..."

    bpftool prog attach "$pin_path" tracepoint:sched:sched_process_fork 2>/dev/null || {
        log_warning "Could not attach process monitor"
    }
}

attach_network_monitor() {
    local pin_path="$1"
    log_info "Attaching network monitor..."

    bpftool prog attach "$pin_path" kprobe:tcp_sendmsg 2>/dev/null || {
        log_warning "Could not attach network monitor"
    }
}

setup_consciousness_integration() {
    log_info "Setting up consciousness integration..."

    # Create configuration map for consciousness communication
    bpftool map create /sys/fs/bpf/consciousness_config \
        type array key 4 value 8 entries 16 name consciousness_config 2>/dev/null || {
        log_warning "Could not create consciousness config map"
    }

    # Create shared memory for consciousness data exchange
    mkdir -p /tmp/synos_consciousness
    chmod 755 /tmp/synos_consciousness

    # Set initial consciousness configuration
    echo "1" > /tmp/synos_consciousness/monitoring_enabled
    echo "0.8" > /tmp/synos_consciousness/threat_sensitivity
    echo "0.9" > /tmp/synos_consciousness/learning_rate

    log_success "Consciousness integration configured"
}

verify_installation() {
    log_info "Verifying eBPF security framework installation..."

    local loaded_programs=0
    local total_programs=4

    # Check loaded programs
    for program in security_monitor memory_monitor_simple process_monitor_simple network_monitor; do
        if bpftool prog list | grep -q "synos_$program"; then
            log_success "$program is loaded and active"
            ((loaded_programs++))
        else
            log_warning "$program is not loaded"
        fi
    done

    # Check maps
    if bpftool map list | grep -q "consciousness_config"; then
        log_success "Consciousness integration maps are active"
    else
        log_warning "Consciousness integration maps not found"
    fi

    # Performance check
    log_info "Performance verification:"
    echo "  - Loaded programs: $loaded_programs/$total_programs"
    echo "  - Memory usage: $(cat /proc/meminfo | grep MemAvailable)"
    echo "  - BPF filesystem: $(mount | grep bpf | wc -l) mounts"

    if [[ $loaded_programs -eq $total_programs ]]; then
        log_success "eBPF security framework is fully operational"
        return 0
    else
        log_warning "eBPF security framework is partially operational"
        return 1
    fi
}

create_monitoring_service() {
    log_info "Creating systemd monitoring service..."

    cat > /etc/systemd/system/synos-ebpf-monitor.service << 'EOF'
[Unit]
Description=SynOS eBPF Security Monitoring Service
Documentation=https://synos.dev/docs/security
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/local/bin/synos-ebpf-monitor
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Create monitor binary placeholder
    cat > /usr/local/bin/synos-ebpf-monitor << 'EOF'
#!/bin/bash
# SynOS eBPF Monitoring Service
echo "SynOS eBPF Security Monitor starting..."
while true; do
    # Monitor eBPF programs
    if ! bpftool prog list | grep -q synos_security_monitor; then
        echo "WARNING: Security monitor not loaded"
    fi
    sleep 30
done
EOF

    chmod +x /usr/local/bin/synos-ebpf-monitor

    systemctl daemon-reload
    systemctl enable synos-ebpf-monitor
    systemctl start synos-ebpf-monitor

    log_success "Monitoring service created and started"
}

generate_report() {
    log_info "Generating installation report..."

    local report_file="/tmp/synos_ebpf_installation_report.txt"

    cat > "$report_file" << EOF
SynOS eBPF Security Framework Installation Report
Generated: $(date)
Kernel: $(uname -r)
System: $(uname -a)

LOADED PROGRAMS:
$(bpftool prog list | grep synos || echo "No SynOS programs found")

ACTIVE MAPS:
$(bpftool map list | grep -E "(security|consciousness)" || echo "No security maps found")

SYSTEM STATUS:
- BPF filesystem mounted: $(mount | grep bpf >/dev/null && echo "YES" || echo "NO")
- Memory available: $(cat /proc/meminfo | grep MemAvailable)
- CPU usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')

CONSCIOUSNESS INTEGRATION:
- Config directory: $(ls -la /tmp/synos_consciousness 2>/dev/null || echo "Not found")
- Monitoring enabled: $(cat /tmp/synos_consciousness/monitoring_enabled 2>/dev/null || echo "Unknown")

RECOMMENDATIONS:
- Monitor system performance impact
- Verify consciousness integration functionality
- Test security event generation
- Review log outputs regularly

Report saved to: $report_file
EOF

    log_success "Installation report generated: $report_file"
}

main() {
    print_banner

    check_prerequisites
    compile_security_programs
    load_security_programs
    setup_consciousness_integration
    create_monitoring_service

    echo
    if verify_installation; then
        log_success "🎉 SynOS eBPF Security Framework installation completed successfully!"
    else
        log_warning "⚠️  SynOS eBPF Security Framework installation completed with warnings"
    fi

    generate_report

    echo
    log_info "Next steps:"
    echo "  1. Monitor system logs: journalctl -u synos-ebpf-monitor -f"
    echo "  2. Check eBPF programs: bpftool prog list | grep synos"
    echo "  3. Verify consciousness integration: ls /tmp/synos_consciousness/"
    echo "  4. Test security events with consciousness integration"
    echo
}

# Execute main function
main "$@"