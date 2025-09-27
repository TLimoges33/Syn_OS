//! Syn_OS Kernel - Main Entry Point
//! 
//! This is the main entry point for the Syn_OS kernel, providing
//! the core functionality for the security-first operating system
//! with consciousness integration.

#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![test_runner(crate::test_runner)]
#![reexport_test_harness_main = "test_main"]

// Core kernel modules
mod boot;
mod memory;
mod scheduler;
mod drivers;
mod security;
mod consciousness;
mod time;
mod vga_buffer;

// External crates
extern crate alloc;

use core::panic::PanicInfo;
use bootloader::{BootInfo, entry_point};

// Entry point definition
entry_point!(kernel_main);

/// Kernel main function - entry point after boot
fn kernel_main(boot_info: &'static BootInfo) -> ! {
    println!("Syn_OS Kernel booting...");
    
    // Initialize essential subsystems
    boot::init();
    time::init();
    memory::init(boot_info);
    drivers::init();
    
    // Initialize security subsystem
    security::init();
    
    // Initialize consciousness integration
    consciousness::init();
    
    // Initialize process scheduler
    scheduler::init();
    
    println!("Syn_OS Kernel initialization complete.");
    
    // Start main kernel loop
    kernel_loop();
}

/// Main kernel loop
fn kernel_loop() -> ! {
    let mut tick_count: u64 = 0;
    
    loop {
        // Process scheduler tasks
        scheduler::process_tasks();
        
        // Update consciousness state
        consciousness::update();
        
        // Process security monitoring
        security::monitor();
        
        // Handle hardware events
        drivers::process_events();
        
        // Every 1000 ticks, check memory status
        if tick_count % 1000 == 0 {
            let memory_status = memory::get_status();
            
            // Apply consciousness-based memory optimization
            memory::consciousness::optimize();
            
            // Log memory status if needed
            if cfg!(feature = "debug-mode") {
                println!("Memory status: {} bytes used, {} bytes free",
                         memory_status.used_memory,
                         memory_status.total_memory - memory_status.used_memory);
            }
        }
        
        tick_count = tick_count.wrapping_add(1);
    }
}

/// Panic handler
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    println!("KERNEL PANIC: {}", info);
    
    // Log panic information
    if let Some(location) = info.location() {
        println!("Location: {}:{}", location.file(), location.line());
    }
    
    // Attempt to recover or halt system
    loop {
        x86_64::instructions::hlt();
    }
}

/// Test runner for kernel tests
#[cfg(test)]
fn test_runner(tests: &[&dyn Fn()]) {
    println!("Running {} tests", tests.len());
    for test in tests {
        test();
    }
    exit_qemu(QemuExitCode::Success);
}

/// Exit codes for QEMU testing
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u32)]
pub enum QemuExitCode {
    Success = 0x10,
    Failed = 0x11,
}

/// Exit QEMU with the given exit code
pub fn exit_qemu(exit_code: QemuExitCode) {
    use x86_64::instructions::port::Port;
    
    unsafe {
        let mut port = Port::new(0xf4);
        port.write(exit_code as u32);
    }
}
