// Syn OS Kernel - Serial Module
// Handles serial port communication for debugging

use uart_16550::SerialPort;
use spin::Mutex;
use lazy_static::lazy_static;
use core::fmt;

// Standard COM1 port address
const COM1_PORT: u16 = 0x3F8;

// Create a global serial port instance
lazy_static! {
    pub static ref SERIAL1: Mutex<SerialPort> = {
        let mut serial_port = unsafe { SerialPort::new(COM1_PORT) };
        serial_port.init();
        Mutex::new(serial_port)
    };
}

// Print to the serial port
#[doc(hidden)]
pub fn _print(args: fmt::Arguments) {
    use core::fmt::Write;
    use x86_64::instructions::interrupts;
    
    // Disable interrupts during printing to prevent deadlocks
    interrupts::without_interrupts(|| {
        SERIAL1.lock().write_fmt(args).unwrap();
    });
}

// Macro for printing to the serial port
#[macro_export]
macro_rules! serial_print {
    ($($arg:tt)*) => ($crate::serial::_print(format_args!($($arg)*)));
}

// Macro for printing a line to the serial port
#[macro_export]
macro_rules! serial_println {
    () => ($crate::serial_print!("\n"));
    ($($arg:tt)*) => ($crate::serial_print!("{}\n", format_args!($($arg)*)));
}

// Simple logging macros for no_std environment
#[macro_export]
macro_rules! log {
    ($level:expr, $fmt:expr) => ($crate::serial_println!("[{}] {}", $level, $fmt));
    ($level:expr, $fmt:expr, $($arg:tt)*) => ($crate::serial_println!("[{}] {}", $level, format_args!($fmt, $($arg)*)));
}

#[macro_export]
macro_rules! info {
    ($fmt:expr) => ($crate::log!("INFO", $fmt));
    ($fmt:expr, $($arg:tt)*) => ($crate::log!("INFO", $fmt, $($arg)*));
}

#[macro_export]
macro_rules! warn {
    ($fmt:expr) => ($crate::log!("WARN", $fmt));
    ($fmt:expr, $($arg:tt)*) => ($crate::log!("WARN", $fmt, $($arg)*));
}

#[macro_export]
macro_rules! error {
    ($fmt:expr) => ($crate::log!("ERROR", $fmt));
    ($fmt:expr, $($arg:tt)*) => ($crate::log!("ERROR", $fmt, $($arg)*));
}

// Initialize the serial port
pub fn init() {
    serial_println!("📞 Serial port initialized");
}
