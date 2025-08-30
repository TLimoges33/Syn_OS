#![no_std]
#![no_main]

use bootloader::{entry_point, BootInfo};
use core::panic::PanicInfo;

// Serial port for debugging (COM1)
const SERIAL_PORT: u16 = 0x3F8;
const VGA_BUFFER: *mut u8 = 0xb8000 as *mut u8;

// Write to both VGA and serial for maximum visibility
fn debug_print(message: &[u8]) {
    // Serial output
    for &byte in message {
        unsafe {
            // Simple serial write without checking ready flag
            core::arch::asm!("out dx, al", in("dx") SERIAL_PORT, in("al") byte);
        }
    }

    // VGA output
    unsafe {
        for (i, &byte) in message.iter().enumerate() {
            if i >= 80 * 25 {
                break;
            }
            *VGA_BUFFER.offset(i as isize * 2) = byte;
            *VGA_BUFFER.offset(i as isize * 2 + 1) = 0x0F; // White on black
        }
    }
}

fn kernel_main(boot_info: &'static BootInfo) -> ! {
    // First thing - immediate output
    debug_print(b"KERNEL ENTRY REACHED!!");

    // Simple loop to show we're working
    let mut counter = 0u8;
    loop {
        // Update counter on screen
        unsafe {
            *VGA_BUFFER.offset(79 * 2) = b'0' + (counter % 10);
            *VGA_BUFFER.offset(79 * 2 + 1) = 0x0C; // Red
        }

        counter = counter.wrapping_add(1);

        // Delay
        for _ in 0..1000000 {
            unsafe {
                core::arch::asm!("nop");
            }
        }
    }
}

entry_point!(kernel_main);

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    debug_print(b"PANIC OCCURRED!!");

    // Show panic on screen
    unsafe {
        let panic_msg = b"PANIC!";
        for (i, &byte) in panic_msg.iter().enumerate() {
            *VGA_BUFFER.offset((80 + i) as isize * 2) = byte;
            *VGA_BUFFER.offset((80 + i) as isize * 2 + 1) = 0x4F; // White on red
        }
    }

    loop {
        unsafe {
            core::arch::asm!("hlt");
        }
    }
}
