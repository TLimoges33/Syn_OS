#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u32);
    __type(value, u64);
} memory_stats SEC(".maps");

SEC("kprobe/kmalloc")
int monitor_memory_alloc(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 size = PT_REGS_PARM1(ctx);
    
    u64 *existing = bpf_map_lookup_elem(&memory_stats, &pid);
    if (existing) {
        *existing += size;
    } else {
        bpf_map_update_elem(&memory_stats, &pid, &size, BPF_ANY);
    }
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
