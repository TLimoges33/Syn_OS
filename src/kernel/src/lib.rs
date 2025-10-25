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
pub mod error; // Kernel-wide error handling (replaces unwrap() calls)
pub mod panic; // Centralized panic handler

// Organized module structure
pub mod memory;      // Memory management subsystem
pub mod interrupts;  // Interrupt handling and IDT
pub mod io;          // I/O subsystem (serial, VGA, etc.)
pub mod utils;       // Kernel utilities (time, debug, CPU, etc.)
pub mod ipc;         // Inter-Process Communication
pub mod syscalls;    // System call interface
pub mod process;     // Process management (scheduler, execution, lifecycle)

// Hardware abstraction and drivers
pub mod hal;      // Hardware Abstraction Layer
pub mod drivers;  // Device drivers
pub mod devices;  // Device management
pub mod network;  // Network stack
pub mod fs;       // Filesystem

// Integrated systems
pub mod boot;      // Boot system management
pub mod ai;        // AI integration and consciousness
pub mod security;  // Security framework
pub mod education; // Educational platform
pub mod container; // Container runtime and security

// Phase integration modules
pub mod phase5;    // Phase 5 integration and testing
pub mod phase6;    // Phase 6 integration

// Legacy modules (maintained for compatibility)
#[cfg(feature = "legacy")]
pub mod legacy;

// Re-export commonly used submodules for convenience
pub use io::{serial, vga_buffer};
pub use utils::{time, time_utils, cpu, debug, system};
pub use process::{scheduler, signals, elf_loader, userspace_integration};
pub use syscalls::optimization as syscall_optimization;
pub use ipc::advanced as ipc_advanced;
pub use interrupts::{gdt, interrupt_security};
pub use memory::{allocator, heap, paging, frame, guard};
pub use security::{threat_detection, verification, stack_protection, security_panic, memory_corruption, pqc};
pub use network::stack as networking;
pub use education::{platform_minimal as education_platform_minimal, advanced_applications_minimal};
pub use ai::{interface as ai_interface, bridge as ai_bridge};
pub use process::{execution as process_execution, lifecycle as process_lifecycle};

// Phase integration re-exports
pub use phase5::integration as phase5_integration;
pub use phase6::integration as phase6_integration;

// Alias for backward compatibility
pub use education::platform_minimal as education_platform;
pub use education::advanced_applications_minimal as advanced_applications;

// Re-export components
pub use bootloader;
pub use x86_64;

// Testing modules
#[cfg(test)]
pub mod testing;

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
