#![no_std]
#![no_main]

use core::panic::PanicInfo;

// VGA text buffer for early debugging
static VGA_BUFFER: *mut u8 = 0xb8000 as *mut u8;

// Simple function to write to VGA buffer
fn write_to_vga(message: &[u8], color: u8) {
    unsafe {
        for (i, &byte) in message.iter().enumerate() {
            if i >= 80 * 25 {
                break;
            } // Prevent overflow
            *VGA_BUFFER.offset(i as isize * 2) = byte;
            *VGA_BUFFER.offset(i as isize * 2 + 1) = color;
        }
    }
}

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // IMMEDIATE DEBUG OUTPUT - Stage 1
    write_to_vga(b"[KERNEL] Entry point reached!", 0x0A); // Green on black

    // Clear screen after entry point message
    unsafe {
        for i in 160..80 * 25 * 2 {
            // Start from line 2
            *VGA_BUFFER.offset(i) = 0x20; // Space
            *VGA_BUFFER.offset(i + 1) = 0x07; // White on black
        }
    }

    // Write stage messages
    write_to_vga(b"[DEBUG] Stage 1: Kernel loaded successfully", 0x0B); // Cyan

    // Test memory access
    let test_ptr = 0x1000 as *mut u32;
    unsafe {
        *test_ptr = 0xDEADBEEF;
        let value = *test_ptr;
        if value == 0xDEADBEEF {
            write_to_vga(b"[DEBUG] Stage 2: Memory access working", 0x0A); // Green
        } else {
            write_to_vga(b"[ERROR] Stage 2: Memory access failed", 0x0C); // Red
        }
    }

    // Initialize basic systems step by step
    write_to_vga(b"[DEBUG] Stage 3: Initializing basic systems...", 0x0E); // Yellow

    // Minimal kernel loop with heartbeat
    let mut counter = 0u32;
    loop {
        counter = counter.wrapping_add(1);

        // Update heartbeat every ~1M iterations
        if counter % 1000000 == 0 {
            unsafe {
                let heartbeat_pos = (79 * 2) as isize; // Top right corner
                let heartbeat_char = if (counter / 1000000) % 2 == 0 {
                    b'*'
                } else {
                    b' '
                };
                *VGA_BUFFER.offset(heartbeat_pos) = heartbeat_char;
                *VGA_BUFFER.offset(heartbeat_pos + 1) = 0x0F; // Bright white
            }
        }

        // Prevent complete lockup
        unsafe {
            core::arch::asm!("pause");
        }
    }
}

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    // Emergency panic handler with VGA output
    write_to_vga(b"[PANIC] Kernel panic occurred!", 0x4C); // Red background

    // Try to extract panic message if possible
    if let Some(location) = info.location() {
        write_to_vga(b"[PANIC] Check debug output for details", 0x4F); // White on red
    }

    // Halt system safely
    loop {
        unsafe {
            core::arch::asm!("hlt");
        }
    }
}
