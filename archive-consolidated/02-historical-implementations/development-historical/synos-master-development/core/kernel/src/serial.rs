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

// Serial print macros
#[macro_export]
macro_rules! serial_print {
    ($($arg:tt)*) => {
        $crate::serial::_print(format_args!($($arg)*));
    };
}

#[macro_export]
macro_rules! serial_println {
    () => ($crate::serial_print!("\n"));
    ($fmt:expr) => ($crate::serial_print!(concat!($fmt, "\n")));
    ($fmt:expr, $($arg:tt)*) => ($crate::serial_print!(
        concat!($fmt, "\n"), $($arg)*));
}

// Initialize the serial port
pub fn init() {
    serial_println!("📞 Serial port initialized");
}
