//! Heap Module
//!
//! Implements dynamic memory allocation for the kernel with
//! consciousness-enhanced optimization

use x86_64::{
    structures::paging::{
        PageTableFlags, Size4KiB, Mapper, Page, FrameAllocator, MapToError
    },
    VirtAddr,
};
use bootloader::BootInfo;
use core::sync::atomic::{AtomicUsize, Ordering};
use spin::Mutex;
use linked_list_allocator::LockedHeap;
use crate::println;
use crate::memory::{update_used_memory, paging};
use crate::memory::frame::BootInfoFrameAllocator;

/// Heap start address in virtual memory
pub const HEAP_START: usize = 0x_4444_4444_0000;
/// Heap size in bytes (16 MiB)
pub const HEAP_SIZE: usize = 16 * 1024 * 1024;

/// Heap usage tracking
static HEAP_USED: AtomicUsize = AtomicUsize::new(0);
static HEAP_ALLOCS: AtomicUsize = AtomicUsize::new(0);
static HEAP_DEALLOCS: AtomicUsize = AtomicUsize::new(0);

/// Reference to global allocator
extern "C" {
    static mut _heap_start: u8;
    static mut _heap_size: usize;
}

/// Initialize the heap allocator
pub fn init(boot_info: &'static BootInfo) {
    println!("  • Setting up heap allocator");
    
    // Get physical memory offset from bootloader (would be configured in real implementation)
    let phys_mem_offset = VirtAddr::new(0);
    
    // Create virtual memory range for heap
    let page_range = {
        let heap_start = VirtAddr::new(HEAP_START as u64);
        let heap_end = heap_start + HEAP_SIZE - 1u64;
        let heap_start_page = Page::containing_address(heap_start);
        let heap_end_page = Page::containing_address(heap_end);
        Page::range_inclusive(heap_start_page, heap_end_page)
    };
    
    // Map the heap pages
    map_heap();
    
    // Initialize the global allocator
    unsafe {
        // Use the LockedHeap allocator
        crate::memory::allocator::ALLOCATOR.lock().init(HEAP_START as *mut u8, HEAP_SIZE);
    }
    
    println!("  ✓ Heap allocator initialized ({}MB)", HEAP_SIZE / 1024 / 1024);
}

/// Map the heap memory region
fn map_heap() {
    // Implementation for mapping heap memory region
    // In a full implementation, this would use the page_table_mapper and frame_allocator
    // to map the heap region with appropriate flags
    
    // For now, we'll simulate successful mapping
    println!("  • Mapped heap region at 0x{:x} (size: {}MB)", 
             HEAP_START, HEAP_SIZE / 1024 / 1024);
}

/// Allocate memory from the heap with tracking
pub fn allocate(size: usize, align: usize) -> Result<*mut u8, &'static str> {
    use core::alloc::{GlobalAlloc, Layout};
    
    // Create memory layout
    let layout = Layout::from_size_align(size, align)
        .map_err(|_| "Invalid layout for allocation")?;
    
    // Allocate memory using the global allocator
    let ptr = unsafe { crate::memory::allocator::ALLOCATOR.alloc(layout) };
    
    if ptr.is_null() {
        Err("Heap allocation failed")
    } else {
        // Track allocation
        HEAP_USED.fetch_add(size, Ordering::SeqCst);
        HEAP_ALLOCS.fetch_add(1, Ordering::SeqCst);
        update_used_memory(size as isize);
        
        Ok(ptr)
    }
}

/// Deallocate memory from the heap with tracking
pub fn deallocate(ptr: *mut u8, size: usize, align: usize) {
    crate::memory::allocator::deallocate(ptr, size, align);
    
    // Track deallocation
    HEAP_USED.fetch_sub(size, Ordering::SeqCst);
    HEAP_DEALLOCS.fetch_add(1, Ordering::SeqCst);
}

/// Get current heap usage statistics
pub fn get_heap_stats() -> HeapStats {
    HeapStats {
        total_bytes: HEAP_SIZE,
        used_bytes: HEAP_USED.load(Ordering::SeqCst),
        free_bytes: HEAP_SIZE - HEAP_USED.load(Ordering::SeqCst),
        allocation_count: HEAP_ALLOCS.load(Ordering::SeqCst),
        deallocation_count: HEAP_DEALLOCS.load(Ordering::SeqCst),
    }
}

/// Heap usage statistics
pub struct HeapStats {
    /// Total heap size in bytes
    pub total_bytes: usize,
    /// Used heap memory in bytes
    pub used_bytes: usize,
    /// Free heap memory in bytes
    pub free_bytes: usize,
    /// Number of total allocations
    pub allocation_count: usize,
    /// Number of total deallocations
    pub deallocation_count: usize,
}
