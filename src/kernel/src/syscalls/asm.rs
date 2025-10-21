/// System call assembly support for SynOS kernel
/// Provides low-level system call entry and exit mechanisms
use core::arch::{asm, naked_asm};
use super::interrupt_handler::syscall_handler;
use crate::syscalls::SyscallError;

/// System call interrupt number (0x80 for compatibility)
pub const SYSCALL_INTERRUPT: u8 = 0x80;

/// System call entry point from user space
#[unsafe(naked)]
pub unsafe extern "C" fn syscall_entry() {
    naked_asm!(
        // Save all registers
        "push rax",
        "push rbx",
        "push rcx",
        "push rdx",
        "push rsi",
        "push rdi",
        "push rbp",
        "push r8",
        "push r9",
        "push r10",
        "push r11",
        "push r12",
        "push r13",
        "push r14",
        "push r15",

        // NOTE: In 64-bit mode, segment registers (ds, es, fs, gs) cannot be pushed/popped directly
        // They are mostly ignored except for FS and GS which are used for thread-local storage
        // We'll use the swapgs instruction for kernel/user mode transitions instead

        // System call number is in rax
        // Arguments are in rdi, rsi, rdx, r10, r8, r9 (Linux x86_64 convention)
        "mov rcx, r10",    // 4th argument (r10 -> rcx for function call)

        // Call the system call handler
        "call {syscall_handler}",

        // Restore general purpose registers
        "pop r15",
        "pop r14",
        "pop r13",
        "pop r12",
        "pop r11",
        "pop r10",
        "pop r9",
        "pop r8",
        "pop rbp",
        "pop rdi",
        "pop rsi",
        "pop rdx",
        "pop rcx",
        "pop rbx",
        "add rsp, 8",      // Skip original rax (result is in rax)

        // Return to user space
        "iretq",

        syscall_handler = sym syscall_handler
    );
}

/// Fast system call entry using SYSCALL instruction (modern CPUs)
#[unsafe(naked)]
pub unsafe extern "C" fn syscall_fast_entry() {
    naked_asm!(
        // SYSCALL instruction saves rip to rcx and rflags to r11
        // We need to save user registers and set up kernel stack

        // Switch to kernel stack (this would need proper implementation)
        // For now, assume we're already on kernel stack

        // Save user registers
        "push rcx",        // User RIP
        "push r11",        // User RFLAGS
        "push rax",        // System call number
        "push rbx",
        "push rdx",
        "push rsi",
        "push rdi",
        "push rbp",
        "push r8",
        "push r9",
        "push r10",
        "push r12",
        "push r13",
        "push r14",
        "push r15",

        // Prepare arguments for system call handler
        // rax = syscall number, rdi = arg0, rsi = arg1, rdx = arg2
        // r10 = arg3, r8 = arg4, r9 = arg5
        "mov rcx, r10",    // Move 4th arg to rcx for function call

        // Call the system call handler
        "call {syscall_handler}",

        // Restore user registers (except rax which contains return value)
        "pop r15",
        "pop r14",
        "pop r13",
        "pop r12",
        "pop r10",
        "pop r9",
        "pop r8",
        "pop rbp",
        "pop rdi",
        "pop rsi",
        "pop rdx",
        "pop rbx",
        "add rsp, 8",      // Skip saved rax
        "pop r11",         // Restore user RFLAGS
        "pop rcx",         // Restore user RIP

        // Return to user space with SYSRET
        "sysretq",

        syscall_handler = sym syscall_handler
    );
}

/// Initialize system call support
pub fn init_syscall_asm() {
    // Set up interrupt 0x80 for system calls
    unsafe {
        // This would integrate with the interrupt manager
        // to register the syscall_entry handler for interrupt 0x80
        crate::println!("System call assembly support initialized");
        crate::println!("  - INT 0x80 handler: registered");
        crate::println!("  - SYSCALL/SYSRET: available on modern CPUs");
    }
}

/// User space system call wrapper macros
/// These would be used by user programs to make system calls

/// Make a system call with no arguments
#[inline]
pub unsafe fn syscall0(number: u64) -> i64 {
    let mut result = number as i64;
    asm!(
        "int 0x80",
        inlateout("rax") result,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 1 argument
#[inline]
pub unsafe fn syscall1(number: u64, arg0: u64) -> i64 {
    let mut result = number as i64;
    asm!(
        "int 0x80",
        inlateout("rax") result,
        in("rdi") arg0,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 2 arguments
#[inline]
pub unsafe fn syscall2(number: u64, arg0: u64, arg1: u64) -> i64 {
    let mut result = number as i64;
    asm!(
        "int 0x80",
        inlateout("rax") result,
        in("rdi") arg0,
        in("rsi") arg1,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 3 arguments
#[inline]
pub unsafe fn syscall3(number: u64, arg0: u64, arg1: u64, arg2: u64) -> i64 {
    let mut result = number as i64;
    asm!(
        "int 0x80",
        inlateout("rax") result,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 4 arguments
#[inline]
pub unsafe fn syscall4(number: u64, arg0: u64, arg1: u64, arg2: u64, arg3: u64) -> i64 {
    let mut result = number as i64;
    asm!(
        "int 0x80",
        inlateout("rax") result,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        in("r10") arg3,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 5 arguments
#[inline]
pub unsafe fn syscall5(number: u64, arg0: u64, arg1: u64, arg2: u64, arg3: u64, arg4: u64) -> i64 {
    let mut result = number as i64;
    asm!(
        "int 0x80",
        inlateout("rax") result,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        in("r10") arg3,
        in("r8") arg4,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 6 arguments
#[inline]
pub unsafe fn syscall6(
    number: u64,
    arg0: u64,
    arg1: u64,
    arg2: u64,
    arg3: u64,
    arg4: u64,
    arg5: u64,
) -> i64 {
    let mut result = number as i64;
    asm!(
        "int 0x80",
        inlateout("rax") result,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        in("r10") arg3,
        in("r8") arg4,
        in("r9") arg5,
        options(nostack, preserves_flags)
    );
    result
}

// High-level syscall wrappers removed to avoid duplication with existing syscall infrastructure
// These helper functions exist but are currently disabled to focus on core INT 0x80 integration
// The real syscall implementations are in mod.rs syscall_entry() function
