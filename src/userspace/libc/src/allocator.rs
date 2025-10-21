//! # SynOS Proper Memory Allocator
//!
//! Production-ready memory allocator using linked_list_allocator
//! with kernel syscall integration and AI consciousness tracking

use linked_list_allocator::LockedHeap;
use core::alloc::{GlobalAlloc, Layout};
use core::ptr::null_mut;
use spin::Mutex;

/// Heap size: 64MB for userspace applications
const HEAP_SIZE: usize = 64 * 1024 * 1024;

/// Static heap start (will be initialized via syscall)
static mut HEAP_START: usize = 0;
static HEAP_INITIALIZED: Mutex<bool> = Mutex::new(false);

/// Global allocator using linked list algorithm
#[global_allocator]
static ALLOCATOR: LockedHeap = LockedHeap::empty();

/// Allocation statistics for AI consciousness
static ALLOCATION_STATS: Mutex<AllocationStats> = Mutex::new(AllocationStats::new());

#[derive(Debug, Clone, Copy)]
pub struct AllocationStats {
    pub total_allocations: usize,
    pub total_deallocations: usize,
    pub bytes_allocated: usize,
    pub bytes_freed: usize,
    pub peak_usage: usize,
    pub current_usage: usize,
}

impl AllocationStats {
    const fn new() -> Self {
        Self {
            total_allocations: 0,
            total_deallocations: 0,
            bytes_allocated: 0,
            bytes_freed: 0,
            peak_usage: 0,
            current_usage: 0,
        }
    }

    fn record_allocation(&mut self, size: usize) {
        self.total_allocations += 1;
        self.bytes_allocated += size;
        self.current_usage += size;
        if self.current_usage > self.peak_usage {
            self.peak_usage = self.current_usage;
        }
    }

    fn record_deallocation(&mut self, size: usize) {
        self.total_deallocations += 1;
        self.bytes_freed += size;
        self.current_usage = self.current_usage.saturating_sub(size);
    }
}

/// Initialize the heap allocator
///
/// This must be called before any allocations occur.
/// It requests memory from the kernel via mmap syscall.
///
/// # Safety
/// Must be called exactly once during program initialization
pub unsafe fn init_heap() -> Result<(), &'static str> {
    let mut initialized = HEAP_INITIALIZED.lock();

    if *initialized {
        return Err("Heap already initialized");
    }

    // Request heap memory from kernel via mmap syscall
    // SYS_MMAP = 9 on x86_64
    let heap_ptr = syscall_mmap(
        0,          // addr: let kernel choose
        HEAP_SIZE,  // length
        0x3,        // prot: PROT_READ | PROT_WRITE
        0x22,       // flags: MAP_PRIVATE | MAP_ANONYMOUS
        -1,         // fd: -1 for anonymous mapping
        0,          // offset
    );

    if heap_ptr == usize::MAX {
        return Err("Failed to allocate heap memory via mmap");
    }

    HEAP_START = heap_ptr;

    // Initialize the allocator with the allocated memory
    ALLOCATOR.lock().init(heap_ptr as *mut u8, HEAP_SIZE);

    *initialized = true;

    Ok(())
}

/// Syscall wrapper for mmap
///
/// # Safety
/// Performs raw syscall - caller must ensure valid parameters
unsafe fn syscall_mmap(
    addr: usize,
    length: usize,
    prot: i32,
    flags: i32,
    fd: i32,
    offset: usize,
) -> usize {
    let result: usize;

    #[cfg(target_arch = "x86_64")]
    core::arch::asm!(
        "syscall",
        inlateout("rax") 9_usize => result,  // SYS_mmap = 9
        in("rdi") addr,
        in("rsi") length,
        in("rdx") prot,
        in("r10") flags,
        in("r8") fd,
        in("r9") offset,
        lateout("rcx") _,
        lateout("r11") _,
        options(nostack, preserves_flags)
    );

    result
}

/// Syscall wrapper for munmap
///
/// # Safety
/// Performs raw syscall - caller must ensure valid parameters
#[allow(dead_code)]
unsafe fn syscall_munmap(addr: usize, length: usize) -> i32 {
    let result: usize;

    #[cfg(target_arch = "x86_64")]
    core::arch::asm!(
        "syscall",
        inlateout("rax") 11_usize => result,  // SYS_munmap = 11
        in("rdi") addr,
        in("rsi") length,
        lateout("rcx") _,
        lateout("r11") _,
        options(nostack, preserves_flags)
    );

    result as i32
}

/// Wrapper allocator for consciousness tracking
pub struct SynOSAllocator;

unsafe impl GlobalAlloc for SynOSAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        // Ensure heap is initialized
        if !*HEAP_INITIALIZED.lock() {
            // Try to initialize heap on first allocation
            if init_heap().is_err() {
                return null_mut();
            }
        }

        // Allocate from the heap
        let ptr = ALLOCATOR.alloc(layout);

        // Track allocation for AI consciousness
        if !ptr.is_null() {
            let mut stats = ALLOCATION_STATS.lock();
            stats.record_allocation(layout.size());
        }

        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        // Deallocate from the heap
        ALLOCATOR.dealloc(ptr, layout);

        // Track deallocation for AI consciousness
        let mut stats = ALLOCATION_STATS.lock();
        stats.record_deallocation(layout.size());
    }

    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        // Use default implementation (alloc new + copy + free old)
        let new_layout = Layout::from_size_align_unchecked(new_size, layout.align());
        let new_ptr = self.alloc(new_layout);

        if !new_ptr.is_null() {
            // Copy old data to new location
            let copy_size = core::cmp::min(layout.size(), new_size);
            core::ptr::copy_nonoverlapping(ptr, new_ptr, copy_size);

            // Free old allocation
            self.dealloc(ptr, layout);
        }

        new_ptr
    }
}

/// Get current allocation statistics
///
/// Used by AI consciousness for memory optimization
pub fn get_allocation_stats() -> AllocationStats {
    *ALLOCATION_STATS.lock()
}

/// Check if heap is initialized
pub fn is_heap_initialized() -> bool {
    *HEAP_INITIALIZED.lock()
}

/// Get heap usage percentage
pub fn get_heap_usage_percent() -> f32 {
    let stats = ALLOCATION_STATS.lock();
    (stats.current_usage as f32 / HEAP_SIZE as f32) * 100.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_allocation_stats() {
        let mut stats = AllocationStats::new();

        stats.record_allocation(1024);
        assert_eq!(stats.total_allocations, 1);
        assert_eq!(stats.current_usage, 1024);

        stats.record_deallocation(512);
        assert_eq!(stats.total_deallocations, 1);
        assert_eq!(stats.current_usage, 512);
    }

    #[test]
    fn test_peak_usage_tracking() {
        let mut stats = AllocationStats::new();

        stats.record_allocation(1024);
        assert_eq!(stats.peak_usage, 1024);

        stats.record_allocation(2048);
        assert_eq!(stats.peak_usage, 3072);

        stats.record_deallocation(1024);
        assert_eq!(stats.current_usage, 2048);
        assert_eq!(stats.peak_usage, 3072); // Peak should remain
    }
}
