//! # Memory Allocator Integration Tests
//!
//! Tests for the SynOS memory allocator implementation

#![no_std]
#![no_main]

extern crate alloc;

use synlibc::{init_heap, get_allocation_stats, malloc, free, calloc, realloc};
use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

/// Test basic malloc/free functionality
#[test_case]
fn test_malloc_free() {
    unsafe {
        // Initialize heap first
        init_heap().expect("Failed to initialize heap");

        // Allocate 1KB
        let ptr = malloc(1024);
        assert!(!ptr.is_null(), "malloc should return valid pointer");

        // Free it
        free(ptr);

        // Stats should show allocation happened
        let stats = get_allocation_stats();
        assert!(stats.total_allocations > 0, "Should have recorded allocation");
    }
}

/// Test calloc (zeroed allocation)
#[test_case]
fn test_calloc() {
    unsafe {
        init_heap().expect("Failed to initialize heap");

        // Allocate array of 10 u64s
        let ptr = calloc(10, 8) as *mut u64;
        assert!(!ptr.is_null(), "calloc should return valid pointer");

        // Verify it's zeroed
        for i in 0..10 {
            assert_eq!(*ptr.add(i), 0, "calloc should zero memory");
        }

        free(ptr as *mut core::ffi::c_void);
    }
}

/// Test realloc functionality
#[test_case]
fn test_realloc() {
    unsafe {
        init_heap().expect("Failed to initialize heap");

        // Initial allocation
        let mut ptr = malloc(100);
        assert!(!ptr.is_null());

        // Write test data
        let test_ptr = ptr as *mut u8;
        *test_ptr = 42;

        // Grow allocation
        ptr = realloc(ptr, 200);
        assert!(!ptr.is_null(), "realloc should succeed");

        // Data should be preserved
        let test_ptr = ptr as *mut u8;
        assert_eq!(*test_ptr, 42, "realloc should preserve data");

        free(ptr);
    }
}

/// Test allocation statistics tracking
#[test_case]
fn test_allocation_stats() {
    unsafe {
        init_heap().expect("Failed to initialize heap");

        let stats_before = get_allocation_stats();

        // Allocate some memory
        let ptr1 = malloc(1024);
        let ptr2 = malloc(2048);

        let stats_after = get_allocation_stats();

        assert!(stats_after.total_allocations > stats_before.total_allocations);
        assert!(stats_after.current_usage >= 3072); // At least 3KB

        free(ptr1);
        free(ptr2);

        let stats_final = get_allocation_stats();
        assert!(stats_final.total_deallocations > 0);
    }
}

/// Test peak usage tracking
#[test_case]
fn test_peak_usage() {
    unsafe {
        init_heap().expect("Failed to initialize heap");

        // Allocate large block
        let ptr = malloc(10 * 1024 * 1024); // 10MB
        assert!(!ptr.is_null());

        let stats = get_allocation_stats();
        let peak = stats.peak_usage;

        free(ptr);

        // Peak should remain even after free
        let stats_after = get_allocation_stats();
        assert_eq!(stats_after.peak_usage, peak, "Peak usage should persist");
    }
}

/// Test multiple allocations
#[test_case]
fn test_multiple_allocations() {
    unsafe {
        init_heap().expect("Failed to initialize heap");

        let mut ptrs = [core::ptr::null_mut(); 100];

        // Allocate 100 small blocks
        for i in 0..100 {
            ptrs[i] = malloc(64);
            assert!(!ptrs[i].is_null(), "Allocation {} should succeed", i);
        }

        // Free all
        for ptr in ptrs.iter() {
            free(*ptr);
        }

        let stats = get_allocation_stats();
        assert_eq!(stats.total_allocations, 100);
        assert_eq!(stats.total_deallocations, 100);
    }
}

/// Test allocation failure handling
#[test_case]
fn test_allocation_failure() {
    unsafe {
        init_heap().expect("Failed to initialize heap");

        // Try to allocate impossibly large block (should fail gracefully)
        let ptr = malloc(usize::MAX);
        assert!(ptr.is_null(), "Huge allocation should fail");

        // errno should be set to ENOMEM
        let errno_ptr = synlibc::__errno_location();
        assert_eq!(*errno_ptr, synlibc::ENOMEM);
    }
}
