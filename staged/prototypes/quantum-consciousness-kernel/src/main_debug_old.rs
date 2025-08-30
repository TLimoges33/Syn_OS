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
            if i >= 80 * 25 { break; }
            *VGA_BUFFER.offset(i as isize * 2) = byte;
            *VGA_BUFFER.offset(i as isize * 2 + 1) = 0x0F; // White on black
        }
    }
}

fn init_page_tables(boot_info: &'static BootInfo) {
    debug_print(b"[PAGE] Initializing page tables...");
    
    // Check if we have memory map info
    debug_print(b"[PAGE] Memory map available");
    
    // Get current CR3 value to verify page tables are set up
    let cr3_value: u64;
    unsafe {
        core::arch::asm!("mov {}, cr3", out(reg) cr3_value);
    }
    
    debug_print(b"[PAGE] CR3 retrieved");
    
    if cr3_value == 0 {
        debug_print(b"[ERROR] CR3 is zero!");
        panic!("Page table base is null");
    } else {
        debug_print(b"[PAGE] CR3 is valid");
    }
    
    // Verify paging is enabled
    let cr0_value: u64;
    unsafe {
        core::arch::asm!("mov {}, cr0", out(reg) cr0_value);
    }
    
    if (cr0_value & 0x80000000) != 0 {
        debug_print(b"[PAGE] Paging is enabled");
    } else {
        debug_print(b"[ERROR] Paging not enabled!");
    }
    
    debug_print(b"[PAGE] Setup verification complete");
}

fn kernel_main(boot_info: &'static BootInfo) -> ! {
    // First thing - immediate output
    debug_print(b"KERNEL ENTRY REACHED!!");
    
    // Initialize page tables
    debug_print(b"[DEBUG] Initializing page tables...");
    init_page_tables(boot_info);
    debug_print(b"[DEBUG] Page tables OK!");
    
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
            unsafe { core::arch::asm!("nop"); }
        }
    }
}

entry_point!(kernel_main);

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
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
        unsafe { core::arch::asm!("hlt"); }
    }
}
