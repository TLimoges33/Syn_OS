/*
 * SynOS eBPF Security Monitor
 * Comprehensive security monitoring using eBPF programs
 *
 * Features:
 * - Real-time threat detection
 * - Process behavior analysis
 * - Network traffic monitoring
 * - File system access control
 * - System call auditing
 */

#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <linux/sched.h>
#include <linux/fs.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

// Security event types
#define SECURITY_EVENT_SYSCALL_ANOMALY     1
#define SECURITY_EVENT_NETWORK_ANOMALY     2
#define SECURITY_EVENT_FILE_ACCESS_DENIED  3
#define SECURITY_EVENT_PROCESS_CREATION    4
#define SECURITY_EVENT_PRIVILEGE_ESCALATION 5

// Security threat levels
#define THREAT_LEVEL_LOW        1
#define THREAT_LEVEL_MEDIUM     2
#define THREAT_LEVEL_HIGH       3
#define THREAT_LEVEL_CRITICAL   4

// Maximum tracked processes and files
#define MAX_TRACKED_PROCESSES   1024
#define MAX_TRACKED_FILES       2048
#define MAX_TRACKED_CONNECTIONS 512

// Security event structure
struct security_event {
    __u32 event_type;
    __u32 threat_level;
    __u32 pid;
    __u32 uid;
    __u32 gid;
    __u64 timestamp;
    char comm[16];
    char details[128];
};

// Process behavior tracking
struct process_behavior {
    __u32 pid;
    __u32 syscall_count;
    __u32 file_access_count;
    __u32 network_connections;
    __u64 last_activity;
    __u8 is_suspicious;
};

// File access tracking
struct file_access {
    __u32 pid;
    __u32 access_type;  // read, write, execute
    char filename[256];
    __u64 timestamp;
};

// Network connection tracking
struct network_connection {
    __u32 pid;
    __u32 src_ip;
    __u32 dst_ip;
    __u16 src_port;
    __u16 dst_port;
    __u8 protocol;
    __u64 timestamp;
};

// eBPF maps for tracking security events
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} security_events SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_TRACKED_PROCESSES);
    __type(key, __u32);
    __type(value, struct process_behavior);
} process_behavior_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_TRACKED_FILES);
    __type(key, __u64);  // inode number
    __type(value, struct file_access);
} file_access_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_TRACKED_CONNECTIONS);
    __type(key, __u64);  // connection hash
    __type(value, struct network_connection);
} network_connection_map SEC(".maps");

// Configuration map
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 16);
    __type(key, __u32);
    __type(value, __u64);
} security_config SEC(".maps");

// Helper function to emit security event
static inline void emit_security_event(__u32 event_type, __u32 threat_level,
                                      const char *details) {
    struct security_event *event;

    event = bpf_ringbuf_reserve(&security_events, sizeof(*event), 0);
    if (!event)
        return;

    event->event_type = event_type;
    event->threat_level = threat_level;
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->uid = bpf_get_current_uid_gid() & 0xffffffff;
    event->gid = bpf_get_current_uid_gid() >> 32;
    event->timestamp = bpf_ktime_get_ns();

    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    // Copy details (safely)
    __builtin_memset(event->details, 0, sizeof(event->details));
    bpf_probe_read_str(event->details, sizeof(event->details), details);

    bpf_ringbuf_submit(event, 0);
}

// Helper function to check if process is suspicious
static inline int is_process_suspicious(__u32 pid) {
    struct process_behavior *behavior;

    behavior = bpf_map_lookup_elem(&process_behavior_map, &pid);
    if (!behavior)
        return 0;

    // Heuristics for suspicious behavior
    if (behavior->syscall_count > 1000 ||  // Too many syscalls
        behavior->file_access_count > 100 ||  // Too many file accesses
        behavior->network_connections > 50) {  // Too many network connections
        return 1;
    }

    return behavior->is_suspicious;
}

// System call monitoring
SEC("tracepoint/syscalls/sys_enter_openat")
int trace_openat(struct trace_event_raw_sys_enter *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    // Update process behavior
    struct process_behavior *behavior = bpf_map_lookup_elem(&process_behavior_map, &pid);
    if (!behavior) {
        struct process_behavior new_behavior = {
            .pid = pid,
            .syscall_count = 1,
            .file_access_count = 1,
            .network_connections = 0,
            .last_activity = bpf_ktime_get_ns(),
            .is_suspicious = 0
        };
        bpf_map_update_elem(&process_behavior_map, &pid, &new_behavior, BPF_ANY);
    } else {
        behavior->file_access_count++;
        behavior->last_activity = bpf_ktime_get_ns();

        // Check for suspicious file access patterns
        if (behavior->file_access_count > 100) {
            behavior->is_suspicious = 1;
            emit_security_event(SECURITY_EVENT_SYSCALL_ANOMALY, THREAT_LEVEL_MEDIUM,
                              "Excessive file access detected");
        }
    }

    return 0;
}

SEC("tracepoint/syscalls/sys_enter_execve")
int trace_execve(struct trace_event_raw_sys_enter *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u32 uid = bpf_get_current_uid_gid() & 0xffffffff;

    // Check for privilege escalation
    if (uid == 0) {  // Root execution
        emit_security_event(SECURITY_EVENT_PRIVILEGE_ESCALATION, THREAT_LEVEL_HIGH,
                          "Process executed with root privileges");
    }

    // Track process creation
    emit_security_event(SECURITY_EVENT_PROCESS_CREATION, THREAT_LEVEL_LOW,
                      "New process created");

    return 0;
}

// Network monitoring
SEC("kprobe/tcp_connect")
int kprobe__tcp_connect(struct pt_regs *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    // Update process behavior
    struct process_behavior *behavior = bpf_map_lookup_elem(&process_behavior_map, &pid);
    if (behavior) {
        behavior->network_connections++;

        // Check for excessive network activity
        if (behavior->network_connections > 50) {
            behavior->is_suspicious = 1;
            emit_security_event(SECURITY_EVENT_NETWORK_ANOMALY, THREAT_LEVEL_MEDIUM,
                              "Excessive network connections detected");
        }
    }

    return 0;
}

// File system monitoring
SEC("kprobe/vfs_read")
int kprobe__vfs_read(struct pt_regs *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    // Check if process is already flagged as suspicious
    if (is_process_suspicious(pid)) {
        emit_security_event(SECURITY_EVENT_FILE_ACCESS_DENIED, THREAT_LEVEL_HIGH,
                          "Suspicious process attempting file access");
    }

    return 0;
}

SEC("kprobe/vfs_write")
int kprobe__vfs_write(struct pt_regs *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    // Check if process is already flagged as suspicious
    if (is_process_suspicious(pid)) {
        emit_security_event(SECURITY_EVENT_FILE_ACCESS_DENIED, THREAT_LEVEL_HIGH,
                          "Suspicious process attempting file write");
    }

    return 0;
}

// Process exit cleanup
SEC("tracepoint/sched/sched_process_exit")
int trace_process_exit(struct trace_event_raw_sched_process_template *ctx) {
    __u32 pid = ctx->pid;

    // Clean up process behavior tracking
    bpf_map_delete_elem(&process_behavior_map, &pid);

    return 0;
}

// Consciousness integration hook
SEC("kprobe/synos_consciousness_hook")
int kprobe__consciousness_hook(struct pt_regs *ctx) {
    // This hook allows consciousness system to influence security decisions
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    // Get consciousness decision from map (set by userspace)
    __u32 consciousness_key = 0;
    __u64 *consciousness_decision = bpf_map_lookup_elem(&security_config, &consciousness_key);

    if (consciousness_decision && *consciousness_decision == 1) {
        // Consciousness has flagged this process as suspicious
        struct process_behavior *behavior = bpf_map_lookup_elem(&process_behavior_map, &pid);
        if (behavior) {
            behavior->is_suspicious = 1;
            emit_security_event(SECURITY_EVENT_SYSCALL_ANOMALY, THREAT_LEVEL_HIGH,
                              "Consciousness detected suspicious behavior");
        }
    }

    return 0;
}

// Performance monitoring for consciousness optimization
SEC("kprobe/finish_task_switch")
int kprobe__finish_task_switch(struct pt_regs *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    // Update process activity timestamp
    struct process_behavior *behavior = bpf_map_lookup_elem(&process_behavior_map, &pid);
    if (behavior) {
        behavior->last_activity = bpf_ktime_get_ns();
        behavior->syscall_count++;

        // Performance optimization: flag processes with excessive syscalls
        if (behavior->syscall_count > 10000) {
            emit_security_event(SECURITY_EVENT_SYSCALL_ANOMALY, THREAT_LEVEL_MEDIUM,
                              "Process showing performance impact");
        }
    }

    return 0;
}

char _license[] SEC("license") = "GPL";