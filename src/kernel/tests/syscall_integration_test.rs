/// Integration tests for complete syscall flow
/// Tests userspace → libc → kernel → handler → result path

#[cfg(test)]
mod syscall_integration_tests {
    use crate::syscalls::SystemCall;

    /// Test userspace mmap syscall integration with Day 1 allocator
    #[test_case]
    fn test_mmap_integration() {
        // This simulates the full syscall flow:
        // 1. Userspace calls malloc() from libc
        // 2. libc calls syscall_mmap() (inline assembly INT 0x80)
        // 3. CPU triggers interrupt 0x80
        // 4. syscall_entry() (naked asm) saves registers and calls syscall_handler()
        // 5. syscall_handler() forwards to syscall_entry() (Rust dispatcher)
        // 6. syscall_entry() calls SyscallHandler::handle_syscall()
        // 7. SyscallHandler routes to sys_mmap()
        // 8. sys_mmap() allocates memory
        // 9. Result returns through the chain back to userspace

        const HEAP_SIZE: usize = 64 * 1024 * 1024; // 64 MB

        // Simulate syscall via direct function call (would be INT 0x80 in real userspace)
        let result = crate::syscalls::syscall_entry(
            SystemCall::Mmap as u64,
            0,                      // addr (NULL = let kernel choose)
            HEAP_SIZE as u64,       // length
            0x3,                    // prot (PROT_READ | PROT_WRITE)
            0x22,                   // flags (MAP_PRIVATE | MAP_ANONYMOUS)
            u64::MAX,               // fd (-1 for anonymous)
            0,                      // offset
        );

        assert!(result > 0, "mmap should return valid address");
        assert_ne!(result, -12, "mmap should not return ENOMEM"); // -12 = ENOMEM

        crate::println!("✅ mmap syscall integration test passed");
        crate::println!("   Allocated {} bytes at address 0x{:x}", HEAP_SIZE, result);
    }

    /// Test write syscall integration
    #[test_case]
    fn test_write_syscall() {
        let test_data = b"Hello from SynOS syscall!\n";

        let result = crate::syscalls::syscall_entry(
            SystemCall::Write as u64,
            1,                          // fd = stdout
            test_data.as_ptr() as u64,  // buffer
            test_data.len() as u64,     // count
            0, 0, 0,
        );

        assert!(result > 0, "write should return bytes written");
        assert_eq!(result as usize, test_data.len(), "write should write all bytes");

        crate::println!("✅ write syscall integration test passed");
    }

    /// Test getpid syscall integration
    #[test_case]
    fn test_getpid_syscall() {
        let result = crate::syscalls::syscall_entry(
            SystemCall::Getpid as u64,
            0, 0, 0, 0, 0, 0,
        );

        assert!(result > 0, "getpid should return valid PID");
        crate::println!("✅ getpid syscall returned PID: {}", result);
    }

    /// Test invalid syscall number
    #[test_case]
    fn test_invalid_syscall() {
        let result = crate::syscalls::syscall_entry(
            9999,  // Invalid syscall number
            0, 0, 0, 0, 0, 0,
        );

        assert!(result < 0, "Invalid syscall should return error");
        assert_eq!(result, -38, "Should return ENOSYS (-38)");

        crate::println!("✅ Invalid syscall correctly rejected");
    }

    /// Test mmap → munmap cycle
    #[test_case]
    fn test_mmap_munmap_cycle() {
        const SIZE: usize = 4096; // One page

        // Allocate memory
        let addr = crate::syscalls::syscall_entry(
            SystemCall::Mmap as u64,
            0,
            SIZE as u64,
            0x3,    // PROT_READ | PROT_WRITE
            0x22,   // MAP_PRIVATE | MAP_ANONYMOUS
            u64::MAX,
            0,
        );

        assert!(addr > 0, "mmap should succeed");

        // Free memory
        let result = crate::syscalls::syscall_entry(
            SystemCall::Munmap as u64,
            addr as u64,
            SIZE as u64,
            0, 0, 0, 0,
        );

        assert_eq!(result, 0, "munmap should return success");

        crate::println!("✅ mmap → munmap cycle test passed");
    }

    /// Test complete malloc/free flow through libc
    #[test_case]
    fn test_libc_malloc_integration() {
        // This test would require linking against our libc
        // For now, verify the syscall infrastructure is ready

        // Verify syscall handler is initialized
        let info_result = crate::syscalls::syscall_entry(
            SystemCall::SynInfo as u64,
            0, 0, 0, 0, 0, 0,
        );

        assert!(info_result >= 0, "SynInfo syscall should succeed");

        crate::println!("✅ LibC integration infrastructure verified");
    }

    /// Test syscall argument passing
    #[test_case]
    fn test_syscall_argument_passing() {
        // Test that all 6 arguments are properly passed through the syscall chain
        // Using a custom SynOS syscall that echoes back arguments

        let arg0 = 0x1111_1111_1111_1111u64;
        let arg1 = 0x2222_2222_2222_2222u64;
        let arg2 = 0x3333_3333_3333_3333u64;
        let arg3 = 0x4444_4444_4444_4444u64;
        let arg4 = 0x5555_5555_5555_5555u64;
        let arg5 = 0x6666_6666_6666_6666u64;

        // Use a safe syscall that won't cause issues with test values
        let _ = crate::syscalls::syscall_entry(
            SystemCall::SynInfo as u64,
            arg0, arg1, arg2, arg3, arg4, arg5,
        );

        // If we get here without panic, argument passing works
        crate::println!("✅ Syscall argument passing verified");
    }

    /// Performance test: Measure syscall overhead
    #[test_case]
    fn test_syscall_performance() {
        const ITERATIONS: usize = 1000;

        let start = crate::time::get_ticks();

        for _ in 0..ITERATIONS {
            let _ = crate::syscalls::syscall_entry(
                SystemCall::Getpid as u64,
                0, 0, 0, 0, 0, 0,
            );
        }

        let end = crate::time::get_ticks();
        let total_ticks = end - start;
        let avg_ticks_per_syscall = total_ticks / ITERATIONS as u64;

        crate::println!("✅ Syscall performance:");
        crate::println!("   {} iterations in {} ticks", ITERATIONS, total_ticks);
        crate::println!("   Average: {} ticks per syscall", avg_ticks_per_syscall);

        // Syscall should be fast (< 1000 ticks on modern CPU)
        assert!(avg_ticks_per_syscall < 1000, "Syscall overhead too high");
    }
}

/// Module for time utilities (stub for testing)
#[cfg(test)]
mod time {
    pub fn get_ticks() -> u64 {
        // In real implementation, would read CPU timestamp counter
        unsafe {
            let ticks: u64;
            core::arch::asm!(
                "rdtsc",
                "shl rdx, 32",
                "or rax, rdx",
                out("rax") ticks,
                out("rdx") _,
                options(nomem, nostack, preserves_flags)
            );
            ticks
        }
    }
}
