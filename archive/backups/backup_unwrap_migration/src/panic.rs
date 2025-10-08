/// SynOS Kernel Panic Handler
///
/// Centralized panic handling for the kernel.
/// Replaces individual panic! calls with structured error handling.

use core::panic::PanicInfo;
use crate::serial_println;

/// Kernel panic handler with detailed logging
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    serial_println!("\n╔══════════════════════════════════════════════════════════════╗");
    serial_println!("║                    KERNEL PANIC                              ║");
    serial_println!("╚══════════════════════════════════════════════════════════════╝\n");

    // Print panic message
    if let Some(message) = info.message() {
        serial_println!("  Message: {}", message);
    }

    // Print panic location
    if let Some(location) = info.location() {
        serial_println!("  Location: {}:{}:{}",
            location.file(),
            location.line(),
            location.column()
        );
    }

    // Print system state
    serial_println!("\n[System State]");
    serial_println!("  Architecture: x86_64");
    serial_println!("  Kernel: SynOS v1.0");

    // TODO: Add more diagnostic info
    // - CPU registers dump
    // - Stack trace
    // - Process table state
    // - Memory statistics

    serial_println!("\n[Action]");
    serial_println!("  Halting CPU. System is in an unrecoverable state.");
    serial_println!("  Please collect this log and report at:");
    serial_println!("  https://github.com/TLimoges33/Syn_OS/issues\n");

    // Halt the CPU
    loop {
        x86_64::instructions::hlt();
    }
}

/// Kernel assertion macro with detailed error reporting
#[macro_export]
macro_rules! kernel_assert {
    ($cond:expr) => {
        if !$cond {
            panic!("Kernel assertion failed: {}", stringify!($cond));
        }
    };
    ($cond:expr, $($arg:tt)+) => {
        if !$cond {
            panic!("Kernel assertion failed: {}\n  {}", stringify!($cond), format_args!($($arg)+));
        }
    };
}

/// Kernel debug assertion (only in debug builds)
#[macro_export]
macro_rules! kernel_debug_assert {
    ($($arg:tt)*) => {
        #[cfg(debug_assertions)]
        $crate::kernel_assert!($($arg)*);
    };
}

/// Safe unwrap replacement that panics with context
#[macro_export]
macro_rules! kernel_unwrap {
    ($expr:expr, $context:expr) => {
        match $expr {
            Some(val) => val,
            None => panic!("unwrap failed at {}: {}", $context, stringify!($expr)),
        }
    };
}

/// Safe expect replacement for Option types
#[macro_export]
macro_rules! kernel_expect {
    ($expr:expr, $msg:expr) => {
        match $expr {
            Some(val) => val,
            None => panic!("expect failed: {}", $msg),
        }
    };
}
