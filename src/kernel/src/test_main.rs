// Simplified test version of main.rs to debug serial output
#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![test_runner(crate::test_runner)]
#![reexport_test_harness_main = "test_main"]

extern crate alloc;

use bootloader::{entry_point, BootInfo};
use core::fmt::Write;
use core::panic::PanicInfo;

entry_point!(kernel_main);

fn kernel_main(_boot_info: &'static BootInfo) -> ! {
    // IMMEDIATE SERIAL OUTPUT TEST
    let mut serial = unsafe { uart_16550::SerialPort::new(0x3F8) };
    serial.init();

    writeln!(serial, "=== EMERGENCY SERIAL DEBUG ===").ok();
    writeln!(serial, "SynOS Kernel Entry Point Reached!").ok();
    writeln!(serial, "If you can see this, serial output works!").ok();
    writeln!(serial, "Boot info received successfully").ok();
    writeln!(serial, "Triggering intentional panic for testing...").ok();

    // Trigger a panic to test panic handler
    panic!("Testing panic handler with serial output");
}

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    let mut serial = unsafe { uart_16550::SerialPort::new(0x3F8) };
    serial.init();

    writeln!(serial, "").ok();
    writeln!(serial, "=== PANIC HANDLER ACTIVATED ===").ok();
    writeln!(serial, "Location: {:?}", info.location()).ok();
    writeln!(serial, "Message: {:?}", info.message()).ok();
    writeln!(serial, "Full info: {}", info).ok();
    writeln!(serial, "=== PANIC HANDLER COMPLETE ===").ok();
    writeln!(serial, "").ok();

    // Infinite loop to halt
    loop {
        x86_64::instructions::hlt();
    }
}

// Test framework stuff (minimal)
#[cfg(test)]
fn test_runner(tests: &[&dyn Fn()]) {
    println!("Running {} tests", tests.len());
    for test in tests {
        test();
    }
}

#[cfg(test)]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    loop {}
}
