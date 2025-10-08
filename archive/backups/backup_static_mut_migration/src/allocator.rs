// Syn OS Kernel - Allocator Module
// Handles memory allocation for the kernel

use linked_list_allocator::LockedHeap;
use spin::Mutex;
use core::alloc::{GlobalAlloc, Layout};
use core::ptr::NonNull;

// Define a allocator using a linked list implementation
#[global_allocator]
pub static ALLOCATOR: LockedHeap = LockedHeap::empty();

// Define constants for memory management
pub const HEAP_START: usize = 0x_4444_4444_0000;
pub const HEAP_SIZE: usize = 1024 * 1024; // 1 MiB

/// Initialize the heap
pub fn init_heap() -> Result<(), &'static str> {
    // For now, just initialize the allocator with a static region
    // In a real kernel, this would map virtual memory pages
    unsafe {
        ALLOCATOR.lock().init(HEAP_START as *mut u8, HEAP_SIZE);
    }
    Ok(())
}

// Memory allocation stats for monitoring
#[derive(Debug, Clone, Copy)]
pub struct AllocStats {
    pub total_allocations: usize,
    pub active_allocations: usize,
    pub bytes_allocated: usize,
    pub bytes_freed: usize,
}

// Global allocator stats
#[allow(dead_code)]
static ALLOC_STATS: Mutex<AllocStats> = Mutex::new(AllocStats {
    total_allocations: 0,
    active_allocations: 0,
    bytes_allocated: 0,
    bytes_freed: 0,
});

// Get current allocation statistics
#[allow(dead_code)]
pub fn get_allocation_stats() -> AllocStats {
    *ALLOC_STATS.lock()
}

// Custom allocator wrapper for tracking allocations
#[allow(dead_code)]
pub struct TrackedAllocator<A> {
    inner: A,
}

impl<A: GlobalAlloc> TrackedAllocator<A> {
    #[allow(dead_code)]
    pub const fn new(inner: A) -> Self {
        TrackedAllocator { inner }
    }
}

unsafe impl<A: GlobalAlloc> GlobalAlloc for TrackedAllocator<A> {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let ptr = self.inner.alloc(layout);
        
        if !ptr.is_null() {
            let mut stats = ALLOC_STATS.lock();
            stats.total_allocations += 1;
            stats.active_allocations += 1;
            stats.bytes_allocated += layout.size();
        }
        
        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        self.inner.dealloc(ptr, layout);
        
        let mut stats = ALLOC_STATS.lock();
        stats.active_allocations = stats.active_allocations.saturating_sub(1);
        stats.bytes_freed += layout.size();
    }
}

// Helper functions for allocating specific types
#[allow(dead_code)]
pub fn alloc_type<T>() -> Option<NonNull<T>> {
    let layout = Layout::new::<T>();
    
    unsafe {
        let ptr = ALLOCATOR.alloc(layout);
        if ptr.is_null() {
            None
        } else {
            Some(NonNull::new_unchecked(ptr as *mut T))
        }
    }
}

// Free an allocated type
#[allow(dead_code)]
pub unsafe fn dealloc_type<T>(ptr: NonNull<T>) {
    let layout = Layout::new::<T>();
    ALLOCATOR.dealloc(ptr.as_ptr() as *mut u8, layout);
}
