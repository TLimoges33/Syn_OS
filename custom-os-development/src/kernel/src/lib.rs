// Syn OS Kernel Library
// This is the main library file for the Syn OS kernel

// Mark this crate as not using the standard library
#![no_std]

// Enable some features for the bare-metal environment
#![feature(abi_x86_interrupt)]
#![feature(alloc_error_handler)]

// Export modules
// Using minimal versions that actually compile
pub mod education_platform_minimal;
pub mod advanced_applications_minimal;
pub mod memory;
pub mod gdt;
pub mod interrupts;
pub mod ipc; // Inter-Process Communication module
pub mod ai_bridge; // AI integration bridge
pub mod syscalls; // System call interface
pub mod process_lifecycle; // Advanced process lifecycle management
pub mod scheduler; // Process scheduler (for backward compatibility)

// Phase 5 modules - Graphics framework integration  
// TODO: Integrate graphics module once workspace configuration is updated
// #[path = "../../graphics/mod.rs"]
// pub mod graphics;

// Testing modules
#[cfg(test)]
pub mod testing;

// Re-export as the expected names for compatibility
pub use education_platform_minimal as education_platform;
pub use advanced_applications_minimal as advanced_applications;

// Re-export components
pub use bootloader;
pub use x86_64;

// Use custom allocator
extern crate alloc;

// Simple print and println macros for kernel debugging
#[macro_export]
macro_rules! print {
    ($($arg:tt)*) => {
        {}  // In a real kernel, this would output to serial or console
            // For now, we'll just create an empty statement block
    };
}

#[macro_export]
macro_rules! println {
    () => {
        {}  // Empty statement block
    };
    ($($arg:tt)*) => {
        {}  // In a real kernel, this would output to serial or console
            // For now, we'll just create an empty statement block
    };
}

// Import x86_64 structures
use x86_64::structures::paging::{
    FrameAllocator, Mapper, mapper::MapToError, Size4KiB, Page
};
use x86_64::VirtAddr;

// Map a memory region
#[allow(dead_code)]
fn map_region(
    mapper: &mut impl Mapper<Size4KiB>,
    start: VirtAddr,
    end: VirtAddr,
    frame_allocator: &mut impl FrameAllocator<Size4KiB>,
) -> Result<(), MapToError<Size4KiB>> {
    // Calculate page range
    let page_range = {
        let start_page = Page::containing_address(start);
        let end_page = Page::containing_address(end);
        Page::range_inclusive(start_page, end_page)
    };

    // Map each page to a physical frame
    for page in page_range {
        let frame = frame_allocator
            .allocate_frame()
            .ok_or(MapToError::FrameAllocationFailed)?;

        // Use flags for a standard heap region (read/write, but not executable)
        let flags = x86_64::structures::paging::PageTableFlags::PRESENT | 
                    x86_64::structures::paging::PageTableFlags::WRITABLE;
        
        // Map the page to the frame
        unsafe {
            mapper.map_to(page, frame, flags, frame_allocator)?.flush();
        }
    }

    Ok(())
}

// Error handling for allocation failures
#[cfg(not(test))]
#[alloc_error_handler]
fn alloc_error_handler(layout: alloc::alloc::Layout) -> ! {
    panic!("allocation error: {:?}", layout)
}

// Note: Panic handler is defined in main.rs to avoid duplicate definitions
