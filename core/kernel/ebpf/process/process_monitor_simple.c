#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u32);
    __type(value, u64);
} process_events SEC(".maps");

SEC("tracepoint/sched/sched_process_fork")
int monitor_process_fork(void *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 timestamp = bpf_ktime_get_ns();
    
    bpf_map_update_elem(&process_events, &pid, &timestamp, BPF_ANY);
    
    return 0;
}

SEC("tracepoint/sched/sched_process_exit")
int monitor_process_exit(void *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    bpf_map_delete_elem(&process_events, &pid);
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
