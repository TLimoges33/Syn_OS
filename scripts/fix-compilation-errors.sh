#!/bin/bash
# SynOS Compilation Error Fixes
# Automatically fixes common trait bounds and missing derives

set -e

echo "🔧 Fixing SynOS Compilation Errors"
echo "===================================="
echo ""

# Fix 1: Add Ord/PartialOrd to Ipv4Address
echo "1. Adding Ord trait to Ipv4Address..."
sed -i 's/#\[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)\]/\n#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]/' \
    src/kernel/src/network/mod.rs || true

# Fix 2: Add Ord/PartialOrd to DeviceClass
echo "2. Adding Ord trait to DeviceClass..."
sed -i '/^pub enum DeviceClass {/i #[derive(Eq, PartialEq, Ord, PartialOrd)]' \
    src/kernel/src/devices/advanced_device_manager.rs || true

# Fix 3: Add Debug to ConsciousnessSystem
echo "3. Adding Debug trait to ConsciousnessSystem..."
sed -i '/^pub struct ConsciousnessSystem {/i #[derive(Debug)]' \
    src/kernel/src/ai/consciousness.rs || true

# Fix 4: Fix camel case naming in syscalls
echo "4. Fixing syscall naming conventions..."
sed -i 's/Clock_gettime/ClockGettime/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Clock_settime/ClockSettime/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Sched_yield/SchedYield/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Sched_setparam/SchedSetparam/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Sched_getparam/SchedGetparam/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Sched_setscheduler/SchedSetscheduler/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Sched_getscheduler/SchedGetscheduler/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Sched_get_priority_max/SchedGetPriorityMax/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Sched_get_priority_min/SchedGetPriorityMin/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Epoll_create/EpollCreate/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Epoll_ctl/EpollCtl/g' src/kernel/src/syscalls/mod.rs
sed -i 's/Epoll_wait/EpollWait/g' src/kernel/src/syscalls/mod.rs

echo "✅ Basic fixes applied!"
echo ""
echo "Run 'cargo check' to verify fixes"
