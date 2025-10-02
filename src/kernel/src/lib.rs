// Syn OS Kernel Library
// This is the main library file for the Syn OS kernel

// Mark this crate as not using the standard library
#![no_std]

// Enable some features for the bare-metal environment
#![feature(abi_x86_interrupt)]
#![feature(alloc_error_handler)]

// Suppress warnings during development (TODO: remove before production)
#![allow(unused)]
#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(unused_mut)]
#![allow(unreachable_patterns)]
#![allow(unused_assignments)]

// Enable external allocator with macros
#[macro_use]
extern crate alloc;

// Export core modules
pub mod memory;
pub mod gdt;
pub mod interrupts;
pub mod serial; // Serial communication for debugging
pub mod time; // Time management and timing functions
pub mod cpu; // CPU management and identification
pub mod debug; // Debug utilities and core dumps
pub mod system; // System control and power management
pub mod ipc; // Inter-Process Communication module
pub mod syscalls; // System call interface
pub mod process_lifecycle; // Advanced process lifecycle management
pub mod scheduler; // Process scheduler (for backward compatibility)

// Hardware abstraction and drivers
pub mod hal; // Hardware Abstraction Layer
pub mod drivers; // Device drivers
pub mod devices; // Device management
pub mod network; // Network stack
pub mod fs; // Filesystem

// Phase 2 reorganized modules
pub mod boot; // Boot system management
pub mod ai; // AI integration and consciousness
pub mod security; // Security framework
pub mod education; // Educational platform
pub mod process; // Enhanced process management

// Legacy modules (maintained for compatibility)
pub mod education_platform_minimal;
pub mod advanced_applications_minimal;
pub mod ai_bridge; // Legacy AI bridge

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
