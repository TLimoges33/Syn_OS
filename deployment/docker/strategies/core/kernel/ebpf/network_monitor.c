#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, 256);
    __type(key, u32);
    __type(value, u64);
} packet_counts SEC(".maps");

SEC("xdp")
int monitor_network_traffic(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    if (eth->h_proto == __constant_htons(ETH_P_IP)) {
        struct iphdr *ip = (void *)(eth + 1);
        if ((void *)(ip + 1) > data_end)
            return XDP_PASS;

        u32 protocol = ip->protocol;
        u64 *count = bpf_map_lookup_elem(&packet_counts, &protocol);
        if (count) {
            (*count)++;
        } else {
            u64 init_count = 1;
            bpf_map_update_elem(&packet_counts, &protocol, &init_count, BPF_ANY);
        }
    }

    return XDP_PASS;
}

char LICENSE[] SEC("license") = "GPL";