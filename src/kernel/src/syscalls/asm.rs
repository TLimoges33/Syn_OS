/// System call assembly support for SynOS kernel
/// Provides low-level system call entry and exit mechanisms
use core::arch::{asm, naked_asm};

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

        // Save segment registers
        "push ds",
        "push es",
        "push fs",
        "push gs",

        // Set up kernel data segments
        "mov ax, 0x10",    // Kernel data segment
        "mov ds, ax",
        "mov es, ax",
        "mov fs, ax",
        "mov gs, ax",

        // System call number is in rax
        // Arguments are in rdi, rsi, rdx, r10, r8, r9 (Linux x86_64 convention)
        "mov rcx, r10",    // 4th argument (r10 -> rcx for function call)

        // Call the system call handler
        "call {syscall_handler}",

        // Restore segment registers
        "pop gs",
        "pop fs",
        "pop es",
        "pop ds",

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

        syscall_handler = sym crate::syscalls::syscall_handler
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

        syscall_handler = sym crate::syscalls::syscall_handler
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
    let result: i64;
    asm!(
        "int 0x80",
        in("rax") number,
        out("rax") result,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 1 argument
#[inline]
pub unsafe fn syscall1(number: u64, arg0: u64) -> i64 {
    let result: i64;
    asm!(
        "int 0x80",
        in("rax") number,
        in("rdi") arg0,
        out("rax") result,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 2 arguments
#[inline]
pub unsafe fn syscall2(number: u64, arg0: u64, arg1: u64) -> i64 {
    let result: i64;
    asm!(
        "int 0x80",
        in("rax") number,
        in("rdi") arg0,
        in("rsi") arg1,
        out("rax") result,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 3 arguments
#[inline]
pub unsafe fn syscall3(number: u64, arg0: u64, arg1: u64, arg2: u64) -> i64 {
    let result: i64;
    asm!(
        "int 0x80",
        in("rax") number,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        out("rax") result,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 4 arguments
#[inline]
pub unsafe fn syscall4(number: u64, arg0: u64, arg1: u64, arg2: u64, arg3: u64) -> i64 {
    let result: i64;
    asm!(
        "int 0x80",
        in("rax") number,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        in("r10") arg3,
        out("rax") result,
        options(nostack, preserves_flags)
    );
    result
}

/// Make a system call with 5 arguments
#[inline]
pub unsafe fn syscall5(number: u64, arg0: u64, arg1: u64, arg2: u64, arg3: u64, arg4: u64) -> i64 {
    let result: i64;
    asm!(
        "int 0x80",
        in("rax") number,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        in("r10") arg3,
        in("r8") arg4,
        out("rax") result,
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
    let result: i64;
    asm!(
        "int 0x80",
        in("rax") number,
        in("rdi") arg0,
        in("rsi") arg1,
        in("rdx") arg2,
        in("r10") arg3,
        in("r8") arg4,
        in("r9") arg5,
        out("rax") result,
        options(nostack, preserves_flags)
    );
    result
}

/// High-level system call wrappers for kernel use
pub mod kernel_syscalls {
    use super::*;
    use crate::syscalls::{SyscallError, SystemCall};

    /// Write to a file descriptor
    pub fn write(fd: u32, buffer: &[u8]) -> Result<usize, SyscallError> {
        let result = unsafe {
            syscall3(
                SystemCall::Write as u64,
                fd as u64,
                buffer.as_ptr() as u64,
                buffer.len() as u64,
            )
        };

        if result < 0 {
            Err(SyscallError::try_from(result).unwrap_or(SyscallError::InvalidArgument))
        } else {
            Ok(result as usize)
        }
    }

    /// Read from a file descriptor
    pub fn read(fd: u32, buffer: &mut [u8]) -> Result<usize, SyscallError> {
        let result = unsafe {
            syscall3(
                SystemCall::Read as u64,
                fd as u64,
                buffer.as_mut_ptr() as u64,
                buffer.len() as u64,
            )
        };

        if result < 0 {
            Err(SyscallError::try_from(result).unwrap_or(SyscallError::InvalidArgument))
        } else {
            Ok(result as usize)
        }
    }

    /// Get process ID
    pub fn getpid() -> u32 {
        let result = unsafe { syscall0(SystemCall::Getpid as u64) };
        result as u32
    }

    /// Exit the current process
    pub fn exit(status: i32) -> ! {
        unsafe {
            syscall1(SystemCall::Exit as u64, status as u64);
        }
        // This should never return
        loop {
            unsafe { asm!("hlt") };
        }
    }

    /// Yield CPU to other processes
    pub fn sched_yield() -> Result<(), SyscallError> {
        let result = unsafe { syscall0(SystemCall::Sched_yield as u64) };
        if result < 0 {
            Err(SyscallError::try_from(result).unwrap_or(SyscallError::InvalidArgument))
        } else {
            Ok(())
        }
    }

    /// Get SynOS system information
    pub fn syn_info() -> Result<(), SyscallError> {
        let result = unsafe { syscall0(SystemCall::SynInfo as u64) };
        if result < 0 {
            Err(SyscallError::try_from(result).unwrap_or(SyscallError::InvalidArgument))
        } else {
            Ok(())
        }
    }

    /// Get SynOS security information
    pub fn syn_security_info() -> Result<(), SyscallError> {
        let result = unsafe { syscall0(SystemCall::SynSecInfo as u64) };
        if result < 0 {
            Err(SyscallError::try_from(result).unwrap_or(SyscallError::InvalidArgument))
        } else {
            Ok(())
        }
    }

    /// Get SynOS device information
    pub fn syn_device_info() -> Result<(), SyscallError> {
        let result = unsafe { syscall0(SystemCall::SynDeviceInfo as u64) };
        if result < 0 {
            Err(SyscallError::try_from(result).unwrap_or(SyscallError::InvalidArgument))
        } else {
            Ok(())
        }
    }
}

impl TryFrom<i64> for SyscallError {
    type Error = ();

    fn try_from(value: i64) -> Result<Self, Self::Error> {
        match value {
            0 => Ok(SyscallError::Success),
            -1 => Ok(SyscallError::PermissionDenied),
            -2 => Ok(SyscallError::NoSuchFile),
            -3 => Ok(SyscallError::NoSuchProcess),
            -4 => Ok(SyscallError::Interrupted),
            -5 => Ok(SyscallError::IoError),
            -12 => Ok(SyscallError::OutOfMemory),
            -13 => Ok(SyscallError::AccessDenied),
            -16 => Ok(SyscallError::ResourceBusy),
            -22 => Ok(SyscallError::InvalidArgument),
            -38 => Ok(SyscallError::NotImplemented),
            _ => Err(()),
        }
    }
}
