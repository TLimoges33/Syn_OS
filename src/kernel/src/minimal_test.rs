// Minimal test kernel to debug serial output
#![no_std]
#![no_main]

use core::fmt::Write;
use core::panic::PanicInfo;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // Try immediate serial output
    let mut serial = unsafe { uart_16550::SerialPort::new(0x3F8) };
    serial.init();

    // Write directly to serial
    writeln!(serial, "=== MINIMAL TEST KERNEL ===").ok();
    writeln!(serial, "Serial port initialized successfully").ok();
    writeln!(serial, "About to panic for testing...").ok();

    // Intentionally panic to test our panic handler
    panic!("Intentional panic to test serial output");
}

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    let mut serial = unsafe { uart_16550::SerialPort::new(0x3F8) };
    serial.init();

    writeln!(serial, "=== PANIC HANDLER CALLED ===").ok();
    writeln!(serial, "Panic info: {}", info).ok();
    writeln!(serial, "=== END PANIC HANDLER ===").ok();

    loop {}
}
