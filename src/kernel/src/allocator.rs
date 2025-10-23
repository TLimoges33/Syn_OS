// Syn OS Kernel - Advanced Memory Management Module
// Handles memory allocation with AI-optimized pooling for the kernel

use linked_list_allocator::LockedHeap;
use spin::Mutex;
use core::alloc::{GlobalAlloc, Layout, AllocError};
use core::ptr::NonNull;
use alloc::collections::BTreeMap;

// Define a allocator using a linked list implementation
#[global_allocator]
pub static ALLOCATOR: LockedHeap = LockedHeap::empty();

// Define constants for memory management
pub const HEAP_START: usize = 0x_4444_4444_0000;
pub const HEAP_SIZE: usize = 1024 * 1024; // 1 MiB

// AI-Optimized Memory Pool for frequent tensor operations
pub struct MemoryPool {
    pools: BTreeMap<usize, spin::Mutex<alloc::vec::Vec<NonNull<u8>>>>,
    max_pool_size: usize,
}

impl MemoryPool {
    pub const fn new() -> Self {
        Self {
            pools: BTreeMap::new(),
            max_pool_size: 1024, // Maximum objects per pool size
        }
    }

    /// Allocate from pool or fallback to heap
    pub fn allocate(&self, layout: Layout) -> Result<NonNull<u8>, AllocError> {
        // Try pool allocation first for common AI sizes
        if let Some(pool) = self.pools.get(&layout.size()) {
            let mut pool_guard = pool.lock();
            if let Some(ptr) = pool_guard.pop() {
                return Ok(ptr);
            }
        }

        // Fallback to heap allocation
        unsafe {
            let ptr = ALLOCATOR.alloc(layout);
            if ptr.is_null() {
                Err(AllocError)
            } else {
                Ok(NonNull::new_unchecked(ptr))
            }
        }
    }

    /// Deallocate back to pool for reuse
    pub unsafe fn deallocate(&self, ptr: NonNull<u8>, layout: Layout) {
        // Return to pool if not full
        if let Some(pool) = self.pools.get(&layout.size()) {
            let mut pool_guard = pool.lock();
            if pool_guard.len() < self.max_pool_size {
                pool_guard.push(ptr);
                return;
            }
        }

        // Pool full or no pool for this size, use heap deallocation
        ALLOCATOR.dealloc(ptr.as_ptr(), layout);
    }

    /// Get pool statistics for monitoring
    pub fn get_stats(&self) -> BTreeMap<usize, usize> {
        let mut stats = BTreeMap::new();
        for (size, pool) in &self.pools {
            stats.insert(*size, pool.lock().len());
        }
        stats
    }
}

// Global memory pool for AI operations
pub static AI_MEMORY_POOL: MemoryPool = MemoryPool::new();

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

// AI-optimized allocation functions using memory pool
#[allow(dead_code)]
pub fn standard_allocate(layout: Layout) -> Result<NonNull<u8>, AllocError> {
    // Use memory pool for AI operations (common tensor sizes)
    if layout.size() >= 64 && layout.size() <= 8192 && layout.align() <= 64 {
        AI_MEMORY_POOL.allocate(layout)
    } else {
        // Fallback to heap for other allocations
        unsafe {
            let ptr = ALLOCATOR.alloc(layout);
            if ptr.is_null() {
                Err(AllocError)
            } else {
                Ok(NonNull::new_unchecked(ptr))
            }
        }
    }
}

#[allow(dead_code)]
pub unsafe fn standard_deallocate(ptr: NonNull<u8>, layout: Layout) {
    // Use memory pool for AI operations
    if layout.size() >= 64 && layout.size() <= 8192 && layout.align() <= 64 {
        AI_MEMORY_POOL.deallocate(ptr, layout);
    } else {
        // Fallback to heap deallocation
        ALLOCATOR.dealloc(ptr.as_ptr(), layout);
    }
}

// Helper functions for allocating specific types
#[allow(dead_code)]
pub fn alloc_type<T>() -> Option<NonNull<T>> {
    let layout = Layout::new::<T>();

    match standard_allocate(layout) {
        Ok(ptr) => Some(ptr.cast()),
        Err(_) => None,
    }
}

// Free an allocated type
#[allow(dead_code)]
pub unsafe fn dealloc_type<T>(ptr: NonNull<T>) {
    let layout = Layout::new::<T>();
    standard_deallocate(ptr.cast(), layout);
}

// Memory pool statistics for monitoring
#[allow(dead_code)]
pub fn get_memory_pool_stats() -> BTreeMap<usize, usize> {
    AI_MEMORY_POOL.get_stats()
}
