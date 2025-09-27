use core::alloc::{GlobalAlloc, Layout};
use core::ptr::null_mut;
use core::sync::atomic::{AtomicUsize, Ordering};

/// A simple bump allocator for kernel heap management
/// This is a basic implementation - will be replaced with buddy allocator
pub struct BumpAllocator {
    heap_start: usize,
    heap_end: usize,
    next: AtomicUsize,
}

impl BumpAllocator {
    /// Create a new bump allocator
    pub const fn new() -> Self {
        BumpAllocator {
            heap_start: 0,
            heap_end: 0,
            next: AtomicUsize::new(0),
        }
    }

    /// Initialize the allocator with heap bounds
    /// SAFETY: The caller must ensure that the given heap bounds are valid
    /// and that the memory is available for allocation.
    pub unsafe fn init(&mut self, heap_start: usize, heap_size: usize) {
        self.heap_start = heap_start;
        self.heap_end = heap_start + heap_size;
        self.next.store(heap_start, Ordering::SeqCst);
    }
}

unsafe impl GlobalAlloc for BumpAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        // Use atomic operations for thread-safe allocation
        let mut current_next = self.next.load(Ordering::SeqCst);

        loop {
            let alloc_start = align_up(current_next, layout.align());
            let alloc_end = match alloc_start.checked_add(layout.size()) {
                Some(end) => end,
                None => return null_mut(),
            };

            if alloc_end > self.heap_end {
                return null_mut(); // out of memory
            }

            // Try to update next pointer atomically
            match self.next.compare_exchange_weak(
                current_next,
                alloc_end,
                Ordering::SeqCst,
                Ordering::SeqCst,
            ) {
                Ok(_) => return alloc_start as *mut u8,
                Err(next) => current_next = next,
            }
        }
    }

    unsafe fn dealloc(&self, _ptr: *mut u8, _layout: Layout) {
        // bump allocator doesn't support deallocation
        // This will be implemented in the buddy allocator
    }
}

/// Align the given address `addr` upwards to alignment `align`.
fn align_up(addr: usize, align: usize) -> usize {
    (addr + align - 1) & !(align - 1)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_align_up() {
        assert_eq!(align_up(0, 4), 0);
        assert_eq!(align_up(1, 4), 4);
        assert_eq!(align_up(4, 4), 4);
        assert_eq!(align_up(5, 4), 8);
    }
}
