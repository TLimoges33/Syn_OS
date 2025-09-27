# SynOS eBPF Security Programs Build System
# Comprehensive eBPF program compilation and deployment

CLANG ?= clang
LLC ?= llc
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= bpftool

# BPF program files
BPF_PROGRAMS = network_monitor process_monitor memory_monitor security_hooks
BPF_OBJECTS = $(patsubst %,%.o,$(BPF_PROGRAMS))

# Kernel headers
KERNEL_VERSION ?= $(shell uname -r)
KERNEL_HEADERS ?= /lib/modules/$(KERNEL_VERSION)/build

# Include paths
INCLUDES = -I$(KERNEL_HEADERS)/include \
           -I$(KERNEL_HEADERS)/include/uapi \
           -I$(KERNEL_HEADERS)/include/generated/uapi \
           -I$(KERNEL_HEADERS)/arch/x86/include \
           -I$(KERNEL_HEADERS)/arch/x86/include/uapi \
           -I$(KERNEL_HEADERS)/arch/x86/include/generated \
           -I/usr/include

# Compilation flags
CFLAGS = -O2 -g -Wall -Werror \
         -target bpf \
         -D__KERNEL__ \
         -D__BPF_TRACING__ \
         -Wno-unused-value \
         -Wno-pointer-sign \
         -Wno-compare-distinct-pointer-types

.PHONY: all clean install load unload validate help

all: $(BPF_OBJECTS)
	@echo "✅ All eBPF programs compiled successfully"

# Compile eBPF programs
%.o: %.c
	@echo "🔨 Compiling eBPF program: $<"
	$(CLANG) $(CFLAGS) $(INCLUDES) -c $< -o $@
	@echo "✅ $@ compiled successfully"

# Create process monitor eBPF program
process_monitor.c:
	@echo "📝 Creating process monitor eBPF program..."
	@cat > process_monitor.c << 'EOF'
#include <linux/bpf.h>
#include <linux/sched.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u32);
    __type(value, u64);
} process_map SEC(".maps");

struct process_event {
    u32 pid;
    u32 ppid;
    char comm[16];
    u64 timestamp;
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

SEC("tp/sched/sched_process_fork")
int trace_process_fork(struct trace_event_raw_sched_process_fork *ctx) {
    struct process_event *event;
    u64 timestamp = bpf_ktime_get_ns();

    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;

    event->pid = ctx->child_pid;
    event->ppid = ctx->parent_pid;
    bpf_probe_read_kernel_str(event->comm, sizeof(event->comm), ctx->child_comm);
    event->timestamp = timestamp;

    bpf_ringbuf_submit(event, 0);

    // Update process count
    u32 key = 1;
    u64 *count = bpf_map_lookup_elem(&process_map, &key);
    if (count) {
        (*count)++;
    } else {
        u64 init_count = 1;
        bpf_map_update_elem(&process_map, &key, &init_count, BPF_ANY);
    }

    return 0;
}

SEC("tp/sched/sched_process_exit")
int trace_process_exit(struct trace_event_raw_sched_process_template *ctx) {
    struct process_event *event;

    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;

    event->pid = ctx->pid;
    event->ppid = 0;
    bpf_probe_read_kernel_str(event->comm, sizeof(event->comm), ctx->comm);
    event->timestamp = bpf_ktime_get_ns();

    bpf_ringbuf_submit(event, 0);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
EOF
	@echo "✅ Process monitor eBPF program created"

# Create memory monitor eBPF program
memory_monitor.c:
	@echo "📝 Creating memory monitor eBPF program..."
	@cat > memory_monitor.c << 'EOF'
#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u32);
    __type(value, u64);
} memory_stats SEC(".maps");

struct alloc_info {
    u64 size;
    u64 timestamp;
    u32 pid;
    char comm[16];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} alloc_events SEC(".maps");

SEC("kprobe/kmalloc")
int trace_kmalloc(struct pt_regs *ctx) {
    u64 size = (u64)PT_REGS_PARM1(ctx);
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct alloc_info *info;

    // Track memory allocation
    u64 *total = bpf_map_lookup_elem(&memory_stats, &pid);
    if (total) {
        (*total) += size;
    } else {
        bpf_map_update_elem(&memory_stats, &pid, &size, BPF_ANY);
    }

    // Send allocation event
    info = bpf_ringbuf_reserve(&alloc_events, sizeof(*info), 0);
    if (!info)
        return 0;

    info->size = size;
    info->timestamp = bpf_ktime_get_ns();
    info->pid = pid;
    bpf_get_current_comm(info->comm, sizeof(info->comm));

    bpf_ringbuf_submit(info, 0);
    return 0;
}

SEC("kprobe/kfree")
int trace_kfree(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    // Note: In real implementation, we'd need to track allocation sizes
    // This is a simplified version for demonstration
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
EOF
	@echo "✅ Memory monitor eBPF program created"

# Create security hooks eBPF program
security_hooks.c:
	@echo "📝 Creating security hooks eBPF program..."
	@cat > security_hooks.c << 'EOF'
#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <linux/sched.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u32);
    __type(value, u32);
} security_violations SEC(".maps");

struct security_event {
    u32 pid;
    u32 violation_type;
    u64 timestamp;
    char comm[16];
    char details[64];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} security_events SEC(".maps");

#define VIOLATION_SUSPICIOUS_SYSCALL 1
#define VIOLATION_PRIVILEGE_ESCALATION 2
#define VIOLATION_NETWORK_ANOMALY 3

SEC("tp/syscalls/sys_enter_execve")
int trace_execve(struct trace_event_raw_sys_enter *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct security_event *event;

    // Basic security check - monitor execve calls
    event = bpf_ringbuf_reserve(&security_events, sizeof(*event), 0);
    if (!event)
        return 0;

    event->pid = pid;
    event->violation_type = VIOLATION_SUSPICIOUS_SYSCALL;
    event->timestamp = bpf_ktime_get_ns();
    bpf_get_current_comm(event->comm, sizeof(event->comm));

    // Check for suspicious patterns
    char comm[16];
    bpf_get_current_comm(comm, sizeof(comm));

    // Simple heuristic: flag unusual binary names
    if (comm[0] == '.' ||
        __builtin_memcmp(comm, "nc", 2) == 0 ||
        __builtin_memcmp(comm, "ncat", 4) == 0) {
        bpf_probe_read_kernel_str(event->details, sizeof(event->details), "Suspicious binary execution");
        bpf_ringbuf_submit(event, 0);

        // Update violation count
        u32 *count = bpf_map_lookup_elem(&security_violations, &pid);
        if (count) {
            (*count)++;
        } else {
            u32 init_count = 1;
            bpf_map_update_elem(&security_violations, &pid, &init_count, BPF_ANY);
        }
    } else {
        bpf_ringbuf_discard(event, 0);
    }

    return 0;
}

SEC("kprobe/commit_creds")
int trace_privilege_escalation(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct security_event *event;

    // Monitor credential changes (potential privilege escalation)
    event = bpf_ringbuf_reserve(&security_events, sizeof(*event), 0);
    if (!event)
        return 0;

    event->pid = pid;
    event->violation_type = VIOLATION_PRIVILEGE_ESCALATION;
    event->timestamp = bpf_ktime_get_ns();
    bpf_get_current_comm(event->comm, sizeof(event->comm));
    bpf_probe_read_kernel_str(event->details, sizeof(event->details), "Credential change detected");

    bpf_ringbuf_submit(event, 0);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
EOF
	@echo "✅ Security hooks eBPF program created"

# Load all eBPF programs
load: $(BPF_OBJECTS)
	@echo "🚀 Loading eBPF programs..."
	@for prog in $(BPF_PROGRAMS); do \
		echo "Loading $$prog.o..."; \
		sudo bpftool prog load $$prog.o /sys/fs/bpf/$$prog || echo "Failed to load $$prog"; \
	done
	@echo "✅ eBPF programs loaded"

# Unload all eBPF programs
unload:
	@echo "🛑 Unloading eBPF programs..."
	@for prog in $(BPF_PROGRAMS); do \
		sudo rm -f /sys/fs/bpf/$$prog 2>/dev/null || true; \
	done
	@echo "✅ eBPF programs unloaded"

# Install eBPF programs and tools
install: $(BPF_OBJECTS)
	@echo "📦 Installing eBPF programs..."
	sudo mkdir -p /opt/synos/ebpf
	sudo cp $(BPF_OBJECTS) /opt/synos/ebpf/
	sudo cp Makefile /opt/synos/ebpf/
	@echo "✅ eBPF programs installed to /opt/synos/ebpf/"

# Validate eBPF programs
validate: $(BPF_OBJECTS)
	@echo "✅ Validating eBPF programs..."
	@for obj in $(BPF_OBJECTS); do \
		echo "Validating $$obj..."; \
		bpftool prog show pinned /sys/fs/bpf/$${obj%.o} 2>/dev/null || echo "$$obj not loaded"; \
		llvm-objdump -h $$obj | grep -E "(\.text|\.maps)" || echo "Invalid sections in $$obj"; \
	done

# Show status of eBPF programs
status:
	@echo "📊 eBPF Programs Status"
	@echo "======================"
	@echo "🔍 Loaded programs:"
	@sudo bpftool prog list | grep -E "(network_monitor|process_monitor|memory_monitor|security_hooks)" || echo "No SynOS eBPF programs loaded"
	@echo "🔍 Pinned programs:"
	@ls -la /sys/fs/bpf/ | grep -E "(network_monitor|process_monitor|memory_monitor|security_hooks)" || echo "No pinned programs found"
	@echo "🔍 Maps:"
	@sudo bpftool map list | grep -A1 -B1 "synos" || echo "No SynOS maps found"

# Monitor eBPF program events
monitor:
	@echo "📡 Monitoring eBPF events..."
	@echo "Press Ctrl+C to stop monitoring"
	@sudo bpftool prog tracelog

# Clean build artifacts
clean:
	@echo "🧹 Cleaning eBPF build artifacts..."
	rm -f $(BPF_OBJECTS)
	rm -f process_monitor.c memory_monitor.c security_hooks.c
	@echo "✅ Clean complete"

# Development cycle
dev: clean all load

# Complete deployment cycle
deploy: clean all install load

# Help
help:
	@echo "🛡️ SynOS eBPF Security Programs Build System"
	@echo "=============================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all       - Compile all eBPF programs"
	@echo "  clean     - Remove build artifacts"
	@echo "  install   - Install programs to system"
	@echo "  load      - Load programs into kernel"
	@echo "  unload    - Unload programs from kernel"
	@echo "  validate  - Validate loaded programs"
	@echo "  status    - Show program status"
	@echo "  monitor   - Monitor eBPF events"
	@echo "  dev       - Development cycle (clean, build, load)"
	@echo "  deploy    - Full deployment (clean, build, install, load)"
	@echo "  help      - Show this help"
	@echo ""
	@echo "Programs:"
	@echo "  network_monitor  - Network traffic analysis"
	@echo "  process_monitor  - Process lifecycle monitoring"
	@echo "  memory_monitor   - Memory allocation tracking"
	@echo "  security_hooks   - Security violation detection"
	@echo ""
	@echo "Requirements:"
	@echo "  - clang with BPF support"
	@echo "  - bpftool"
	@echo "  - Kernel with eBPF support"