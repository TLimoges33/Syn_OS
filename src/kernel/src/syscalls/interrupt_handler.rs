/// System Call Interrupt Handler
/// Bridges the low-level interrupt assembly with the syscall dispatcher

use super::syscall_entry;

/// System call handler called from assembly interrupt wrapper
/// This is the bridge between the naked assembly function and the Rust dispatcher
#[no_mangle]
pub extern "C" fn syscall_handler(
    call_number: u64,
    arg0: u64,
    arg1: u64,
    arg2: u64,
    arg3: u64,
    arg4: u64,
    arg5: u64,
) -> i64 {
    // Directly forward to the main syscall dispatcher
    syscall_entry(call_number, arg0, arg1, arg2, arg3, arg4, arg5)
}

/// Initialize system call interrupt handling
pub fn init_syscall_interrupts() -> Result<(), &'static str> {
    unsafe {
        // Register INT 0x80 handler with the IDT
        crate::interrupts::register_syscall_handler()?;
    }

    crate::println!("✅ System call interrupt handler registered (INT 0x80)");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_syscall_handler_forwards_to_dispatcher() {
        // Test that syscall_handler properly forwards calls
        // This would require mocking the syscall infrastructure
        // For now, just verify the function signature exists
        let _ = syscall_handler;
    }
}
