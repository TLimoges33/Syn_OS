#![no_std]
#![no_main]

use bootloader::{entry_point, BootInfo};
use core::panic::PanicInfo;

// Serial port for debugging (COM1)
const SERIAL_PORT: u16 = 0x3F8;

// Simple serial output function
fn serial_print(message: &[u8]) {
    for &byte in message {
        unsafe {
            // Wait for transmit buffer to be empty
            while (read_port(SERIAL_PORT + 5) & 0x20) == 0 {}
            write_port(SERIAL_PORT, byte);
        }
    }
}

unsafe fn write_port(port: u16, value: u8) {
    core::arch::asm!("out dx, al", in("dx") port, in("al") value);
}

unsafe fn read_port(port: u16) -> u8 {
    let value: u8;
    core::arch::asm!("in al, dx", out("al") value, in("dx") port);
    value
}

fn init_serial() {
    unsafe {
        write_port(SERIAL_PORT + 1, 0x00);    // Disable all interrupts
        write_port(SERIAL_PORT + 3, 0x80);    // Enable DLAB (set baud rate divisor)
        write_port(SERIAL_PORT + 0, 0x03);    // Set divisor to 3 (lo byte) 38400 baud
        write_port(SERIAL_PORT + 1, 0x00);    //                  (hi byte)
        write_port(SERIAL_PORT + 3, 0x03);    // 8 bits, no parity, one stop bit
        write_port(SERIAL_PORT + 2, 0xC7);    // Enable FIFO, clear them, with 14-byte threshold
        write_port(SERIAL_PORT + 4, 0x0B);    // IRQs enabled, RTS/DSR set
    }
}

#[no_mangle]
pub fn kernel_main(_boot_info: &'static BootInfo) -> ! {
    // Initialize serial port first
    init_serial();
    
    // IMMEDIATE DEBUG OUTPUT
    serial_print(b"[KERNEL] Entry point reached!\n");
    serial_print(b"[DEBUG] Stage 1: Serial output working\n");
    serial_print(b"[DEBUG] Boot info received from bootloader\n");
    
    // Test basic functionality
    serial_print(b"[DEBUG] Stage 2: Testing memory access...\n");
    
    // Test memory access safely
    let test_value = 0xDEADBEEF_u32;
    let ptr = &test_value as *const u32;
    
    unsafe {
        let read_value = *ptr;
        if read_value == 0xDEADBEEF {
            serial_print(b"[DEBUG] Stage 2: Memory access OK\n");
        } else {
            serial_print(b"[ERROR] Stage 2: Memory access failed\n");
        }
    }
    
    serial_print(b"[DEBUG] Stage 3: Basic kernel initialization\n");
    
    // Test interrupt disable
    unsafe {
        core::arch::asm!("cli");
    }
    serial_print(b"[DEBUG] Stage 4: Interrupts disabled\n");
    
    // Main kernel loop with heartbeat
    serial_print(b"[DEBUG] Stage 5: Entering main loop\n");
    let mut counter = 0u32;
    
    loop {
        counter = counter.wrapping_add(1);
        
        // Heartbeat every 10M iterations
        if counter % 10000000 == 0 {
            serial_print(b"[HEARTBEAT] Kernel alive\n");
        }
        
        // CPU pause to prevent overheating
        unsafe {
            core::arch::asm!("pause");
        }
        
        // Test halt instruction periodically
        if counter % 1000000 == 0 {
            unsafe {
                core::arch::asm!("hlt");
            }
        }
    }
}

entry_point!(kernel_main);

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    serial_print(b"[PANIC] Kernel panic occurred!\n");
    
    if let Some(location) = info.location() {
        serial_print(b"[PANIC] Location: ");
        // Note: We can't easily print the location details without alloc
        serial_print(b"(location info available)\n");
    }
    
    if let Some(msg) = info.payload().downcast_ref::<&str>() {
        serial_print(b"[PANIC] Message: ");
        serial_print(msg.as_bytes());
        serial_print(b"\n");
    }
    
    serial_print(b"[PANIC] Halting system...\n");
    
    loop {
        unsafe {
            core::arch::asm!("cli");
            core::arch::asm!("hlt");
        }
    }
}
