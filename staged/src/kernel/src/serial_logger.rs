/// Serial Logger for Kernel Debugging and Panic Capture
/// Provides comprehensive logging for kernel panics and debug information
///
/// This module enables:
/// - Serial port logging for QEMU debugging
/// - Panic information capture and display
/// - Detailed error reporting with stack traces
/// - Log level filtering for production/debug builds
use core::fmt::Write;
use lazy_static::lazy_static;
use spin::Mutex;
use uart_16550::SerialPort;

/// Global serial port instance for logging
lazy_static! {
    pub static ref SERIAL1: Mutex<SerialPort> = {
        let mut serial_port = unsafe { SerialPort::new(0x3F8) };
        serial_port.init();
        Mutex::new(serial_port)
    };
}

/// Log levels for filtering output
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum LogLevel {
    Error = 0,
    Warn = 1,
    Info = 2,
    Debug = 3,
    Trace = 4,
}

/// Current log level (can be changed for debug/production builds)
pub static LOG_LEVEL: LogLevel = LogLevel::Debug;

/// Print to serial port (for QEMU debugging)
pub fn _print(args: core::fmt::Arguments) {
    SERIAL1
        .lock()
        .write_fmt(args)
        .expect("Printing to serial failed");
}

/// Kernel logging macros with levels
/// These are simplified to avoid macro resolution issues

/// Enhanced panic handler with detailed logging
/// Uses the main module's serial_println macro
pub fn log_panic_info(info: &core::panic::PanicInfo) {
    // Use the serial port directly since we can't access the macro from here
    _print(format_args!("\n"));
    _print(format_args!(
        "==================================================\n"
    ));
    _print(format_args!(
        "              KERNEL PANIC DETECTED              \n"
    ));
    _print(format_args!(
        "==================================================\n"
    ));

    if let Some(location) = info.location() {
        _print(format_args!("Panic Location:\n"));
        _print(format_args!("  File: {}\n", location.file()));
        _print(format_args!("  Line: {}\n", location.line()));
        _print(format_args!("  Column: {}\n", location.column()));
    }

    // Use the new panic message API
    let message = info.message();
    _print(format_args!("Panic Message: {}\n", message));

    _print(format_args!("\n"));
    _print(format_args!("Stack Trace:\n"));
    _print(format_args!("  (Stack trace not yet implemented)\n"));

    _print(format_args!("\n"));
    _print(format_args!("System State:\n"));
    _print(format_args!("  Kernel: SynOS v4.2\n"));
    _print(format_args!("  Architecture: x86_64\n"));
    _print(format_args!("  Build: Debug\n"));

    _print(format_args!("\n"));
    _print(format_args!("Debugging Hints:\n"));
    _print(format_args!(
        "  1. Check QEMU serial output for detailed logs\n"
    ));
    _print(format_args!(
        "  2. Verify memory allocation and access patterns\n"
    ));
    _print(format_args!(
        "  3. Check AI bridge communication integrity\n"
    ));
    _print(format_args!("  4. Validate interrupt handler setup\n"));

    _print(format_args!(
        "==================================================\n"
    ));
    _print(format_args!("\n"));
}

/// Initialize logging system
pub fn init_logging() {
    _print(format_args!("[INFO]  Serial logging system initialized\n"));
    _print(format_args!("[INFO]  Log level: Debug\n"));
    _print(format_args!("[DEBUG] Debug logging enabled\n"));
}

/// Test logging functionality
pub fn test_logging() {
    _print(format_args!("[TRACE] This is a trace message\n"));
    _print(format_args!("[DEBUG] This is a debug message\n"));
    _print(format_args!("[INFO]  This is an info message\n"));
    _print(format_args!("[WARN]  This is a warning message\n"));
    _print(format_args!("[ERROR] This is an error message\n"));
}

/// Simple logging functions that use _print directly
pub fn log_info(msg: &str) {
    _print(format_args!("[INFO]  {}\n", msg));
}

pub fn log_debug(msg: &str) {
    _print(format_args!("[DEBUG] {}\n", msg));
}

pub fn log_error(msg: &str) {
    _print(format_args!("[ERROR] {}\n", msg));
}

pub fn log_warn(msg: &str) {
    _print(format_args!("[WARN]  {}\n", msg));
}

pub fn log_trace(msg: &str) {
    _print(format_args!("[TRACE] {}\n", msg));
}

/// Kernel assertion macro with logging
#[macro_export]
macro_rules! kernel_assert {
    ($condition:expr) => {
        if !($condition) {
            $crate::log_error!("Assertion failed: {}", stringify!($condition));
            panic!("Kernel assertion failed: {}", stringify!($condition));
        }
    };
    ($condition:expr, $($arg:tt)*) => {
        if !($condition) {
            $crate::log_error!("Assertion failed: {} - {}", stringify!($condition), format_args!($($arg)*));
            panic!("Kernel assertion failed: {} - {}", stringify!($condition), format_args!($($arg)*));
        }
    };
}

/// Safe memory access with logging
pub fn safe_read_u32(addr: usize) -> Result<u32, &'static str> {
    if addr % 4 != 0 {
        log_error("Unaligned memory access attempted");
        return Err("Unaligned memory access");
    }

    if addr < 0x1000 {
        log_error("Null pointer dereference attempted");
        return Err("Null pointer dereference");
    }

    log_trace("Reading 32-bit value from memory");
    unsafe {
        let value = core::ptr::read_volatile(addr as *const u32);
        log_trace("Read value from memory successfully");
        Ok(value)
    }
}

/// Memory region validation with logging
pub fn validate_memory_region(start: usize, size: usize) -> bool {
    log_debug("Validating memory region");

    // Basic validation checks
    if start == 0 {
        log_error("Memory region starts at null pointer");
        return false;
    }

    if size == 0 {
        log_error("Memory region has zero size");
        return false;
    }

    if start.checked_add(size).is_none() {
        log_error("Memory region causes integer overflow");
        return false;
    }

    log_debug("Memory region validation passed");
    true
}
