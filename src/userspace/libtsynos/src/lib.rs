//! libtsynos - Userspace library for SynOS system calls
//!
//! This library provides safe Rust wrappers around all 43 SynOS system calls,
//! enabling userspace applications to interact with the kernel.

#![no_std]

use core::arch::asm;

/// SynOS syscall numbers
#[repr(u64)]
#[derive(Debug, Clone, Copy)]
pub enum SyscallNumber {
    // Core System Calls (0-9)
    Exit = 0,
    Write = 1,
    Read = 2,
    Open = 3,
    Close = 4,
    Fork = 5,
    Exec = 6,
    Wait = 7,
    GetPid = 8,
    Sleep = 9,

    // Networking Calls (10-19)
    Socket = 10,
    Bind = 11,
    Listen = 12,
    Accept = 13,
    Connect = 14,
    Send = 15,
    Recv = 16,
    SendTo = 17,
    RecvFrom = 18,
    GetSockOpt = 19,

    // Security & Threat Detection (20-26)
    ThreatDetect = 20,
    ThreatLog = 21,
    ThreatQuery = 22,
    SecurityAudit = 23,
    AccessControl = 24,
    CryptoOp = 25,
    SecureRandom = 26,

    // AI & Consciousness (27-32)
    AiInference = 27,
    AiTrain = 28,
    ConsciousnessQuery = 29,
    ConsciousnessUpdate = 30,
    PatternRecognize = 31,
    DecisionMake = 32,

    // Advanced Features (33-42)
    MemoryMap = 33,
    MemoryUnmap = 34,
    MemoryProtect = 35,
    SignalRegister = 36,
    SignalSend = 37,
    TimeGet = 38,
    TimeSet = 39,
    ProcessPriority = 40,
    ThreadCreate = 41,
    ThreadJoin = 42,
}

/// Generic syscall invocation (up to 6 arguments)
#[inline(always)]
pub unsafe fn syscall0(num: SyscallNumber) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

#[inline(always)]
pub unsafe fn syscall1(num: SyscallNumber, arg1: u64) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        in("rdi") arg1,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

#[inline(always)]
pub unsafe fn syscall2(num: SyscallNumber, arg1: u64, arg2: u64) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        in("rdi") arg1,
        in("rsi") arg2,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

#[inline(always)]
pub unsafe fn syscall3(num: SyscallNumber, arg1: u64, arg2: u64, arg3: u64) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        in("rdi") arg1,
        in("rsi") arg2,
        in("rdx") arg3,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

#[inline(always)]
pub unsafe fn syscall4(num: SyscallNumber, arg1: u64, arg2: u64, arg3: u64, arg4: u64) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        in("rdi") arg1,
        in("rsi") arg2,
        in("rdx") arg3,
        in("r10") arg4,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

#[inline(always)]
pub unsafe fn syscall5(num: SyscallNumber, arg1: u64, arg2: u64, arg3: u64, arg4: u64, arg5: u64) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        in("rdi") arg1,
        in("rsi") arg2,
        in("rdx") arg3,
        in("r10") arg4,
        in("r8") arg5,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

#[inline(always)]
pub unsafe fn syscall6(num: SyscallNumber, arg1: u64, arg2: u64, arg3: u64, arg4: u64, arg5: u64, arg6: u64) -> i64 {
    let ret: i64;
    asm!(
        "syscall",
        in("rax") num as u64,
        in("rdi") arg1,
        in("rsi") arg2,
        in("rdx") arg3,
        in("r10") arg4,
        in("r8") arg5,
        in("r9") arg6,
        lateout("rax") ret,
        options(nostack)
    );
    ret
}

// ============================================================================
// CORE SYSTEM CALLS - Safe Wrappers
// ============================================================================

/// Exit the current process
pub fn exit(code: i32) -> ! {
    unsafe {
        syscall1(SyscallNumber::Exit, code as u64);
    }
    loop {}
}

/// Write to a file descriptor
pub fn write(fd: i32, buf: &[u8]) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::Write,
            fd as u64,
            buf.as_ptr() as u64,
            buf.len() as u64,
        )
    }
}

/// Read from a file descriptor
pub fn read(fd: i32, buf: &mut [u8]) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::Read,
            fd as u64,
            buf.as_mut_ptr() as u64,
            buf.len() as u64,
        )
    }
}

/// Open a file
pub fn open(path: &str, flags: u64) -> i64 {
    unsafe {
        syscall2(
            SyscallNumber::Open,
            path.as_ptr() as u64,
            flags,
        )
    }
}

/// Close a file descriptor
pub fn close(fd: i32) -> i64 {
    unsafe {
        syscall1(SyscallNumber::Close, fd as u64)
    }
}

/// Fork the current process
pub fn fork() -> i64 {
    unsafe {
        syscall0(SyscallNumber::Fork)
    }
}

/// Execute a new program
pub fn exec(path: &str, args: &[&str]) -> i64 {
    unsafe {
        syscall2(
            SyscallNumber::Exec,
            path.as_ptr() as u64,
            args.as_ptr() as u64,
        )
    }
}

/// Wait for a child process
pub fn wait(pid: i32) -> i64 {
    unsafe {
        syscall1(SyscallNumber::Wait, pid as u64)
    }
}

/// Get current process ID
pub fn getpid() -> i64 {
    unsafe {
        syscall0(SyscallNumber::GetPid)
    }
}

/// Sleep for specified milliseconds
pub fn sleep(ms: u64) -> i64 {
    unsafe {
        syscall1(SyscallNumber::Sleep, ms)
    }
}

// ============================================================================
// NETWORKING SYSTEM CALLS
// ============================================================================

pub const SOCK_STREAM: u32 = 1;
pub const SOCK_DGRAM: u32 = 2;
pub const AF_INET: u32 = 2;
pub const AF_INET6: u32 = 10;

/// Create a socket
pub fn socket(domain: u32, socket_type: u32, protocol: u32) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::Socket,
            domain as u64,
            socket_type as u64,
            protocol as u64,
        )
    }
}

/// Bind a socket to an address
pub fn bind(sockfd: i32, addr: &[u8]) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::Bind,
            sockfd as u64,
            addr.as_ptr() as u64,
            addr.len() as u64,
        )
    }
}

/// Listen on a socket
pub fn listen(sockfd: i32, backlog: i32) -> i64 {
    unsafe {
        syscall2(
            SyscallNumber::Listen,
            sockfd as u64,
            backlog as u64,
        )
    }
}

/// Accept a connection
pub fn accept(sockfd: i32) -> i64 {
    unsafe {
        syscall1(SyscallNumber::Accept, sockfd as u64)
    }
}

/// Connect to a remote address
pub fn connect(sockfd: i32, addr: &[u8]) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::Connect,
            sockfd as u64,
            addr.as_ptr() as u64,
            addr.len() as u64,
        )
    }
}

/// Send data on a socket
pub fn send(sockfd: i32, buf: &[u8], flags: u32) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::Send,
            sockfd as u64,
            buf.as_ptr() as u64,
            buf.len() as u64,
            flags as u64,
        )
    }
}

/// Receive data from a socket
pub fn recv(sockfd: i32, buf: &mut [u8], flags: u32) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::Recv,
            sockfd as u64,
            buf.as_mut_ptr() as u64,
            buf.len() as u64,
            flags as u64,
        )
    }
}

/// Send data to a specific address
pub fn sendto(sockfd: i32, buf: &[u8], flags: u32, addr: &[u8]) -> i64 {
    unsafe {
        syscall5(
            SyscallNumber::SendTo,
            sockfd as u64,
            buf.as_ptr() as u64,
            buf.len() as u64,
            flags as u64,
            addr.as_ptr() as u64,
        )
    }
}

/// Receive data from any address
pub fn recvfrom(sockfd: i32, buf: &mut [u8], flags: u32, addr: &mut [u8]) -> i64 {
    unsafe {
        syscall5(
            SyscallNumber::RecvFrom,
            sockfd as u64,
            buf.as_mut_ptr() as u64,
            buf.len() as u64,
            flags as u64,
            addr.as_mut_ptr() as u64,
        )
    }
}

/// Get socket options
pub fn getsockopt(sockfd: i32, level: u32, optname: u32) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::GetSockOpt,
            sockfd as u64,
            level as u64,
            optname as u64,
        )
    }
}

// ============================================================================
// SECURITY & THREAT DETECTION
// ============================================================================

/// Detect threats in the system
pub fn threat_detect(data: &[u8]) -> i64 {
    unsafe {
        syscall2(
            SyscallNumber::ThreatDetect,
            data.as_ptr() as u64,
            data.len() as u64,
        )
    }
}

/// Log a security threat
pub fn threat_log(threat_id: u64, severity: u32, message: &str) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::ThreatLog,
            threat_id,
            severity as u64,
            message.as_ptr() as u64,
            message.len() as u64,
        )
    }
}

/// Query threat database
pub fn threat_query(query: &str, results: &mut [u8]) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::ThreatQuery,
            query.as_ptr() as u64,
            query.len() as u64,
            results.as_mut_ptr() as u64,
            results.len() as u64,
        )
    }
}

/// Perform security audit
pub fn security_audit(target: &str, audit_type: u32) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::SecurityAudit,
            target.as_ptr() as u64,
            target.len() as u64,
            audit_type as u64,
        )
    }
}

/// Check access control
pub fn access_control(resource: &str, action: u32, user: u32) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::AccessControl,
            resource.as_ptr() as u64,
            resource.len() as u64,
            action as u64,
            user as u64,
        )
    }
}

/// Perform cryptographic operation
pub fn crypto_op(op: u32, data: &[u8], key: &[u8]) -> i64 {
    unsafe {
        syscall5(
            SyscallNumber::CryptoOp,
            op as u64,
            data.as_ptr() as u64,
            data.len() as u64,
            key.as_ptr() as u64,
            key.len() as u64,
        )
    }
}

/// Get secure random bytes
pub fn secure_random(buf: &mut [u8]) -> i64 {
    unsafe {
        syscall2(
            SyscallNumber::SecureRandom,
            buf.as_mut_ptr() as u64,
            buf.len() as u64,
        )
    }
}

// ============================================================================
// AI & CONSCIOUSNESS SYSTEM CALLS
// ============================================================================

/// Perform AI inference
pub fn ai_inference(model_id: u64, input: &[u8], output: &mut [u8]) -> i64 {
    unsafe {
        syscall5(
            SyscallNumber::AiInference,
            model_id,
            input.as_ptr() as u64,
            input.len() as u64,
            output.as_mut_ptr() as u64,
            output.len() as u64,
        )
    }
}

/// Train AI model
pub fn ai_train(model_id: u64, training_data: &[u8], epochs: u32) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::AiTrain,
            model_id,
            training_data.as_ptr() as u64,
            training_data.len() as u64,
            epochs as u64,
        )
    }
}

/// Query consciousness state
pub fn consciousness_query(query: &str, result: &mut [u8]) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::ConsciousnessQuery,
            query.as_ptr() as u64,
            query.len() as u64,
            result.as_mut_ptr() as u64,
            result.len() as u64,
        )
    }
}

/// Update consciousness state
pub fn consciousness_update(update: &[u8]) -> i64 {
    unsafe {
        syscall2(
            SyscallNumber::ConsciousnessUpdate,
            update.as_ptr() as u64,
            update.len() as u64,
        )
    }
}

/// Recognize patterns
pub fn pattern_recognize(data: &[u8], pattern_type: u32) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::PatternRecognize,
            data.as_ptr() as u64,
            data.len() as u64,
            pattern_type as u64,
        )
    }
}

/// Make AI-driven decision
pub fn decision_make(context: &[u8], options: &[u8]) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::DecisionMake,
            context.as_ptr() as u64,
            context.len() as u64,
            options.as_ptr() as u64,
            options.len() as u64,
        )
    }
}

// ============================================================================
// ADVANCED SYSTEM CALLS
// ============================================================================

/// Memory map
pub fn memory_map(addr: u64, length: u64, prot: u32, flags: u32) -> i64 {
    unsafe {
        syscall4(
            SyscallNumber::MemoryMap,
            addr,
            length,
            prot as u64,
            flags as u64,
        )
    }
}

/// Memory unmap
pub fn memory_unmap(addr: u64, length: u64) -> i64 {
    unsafe {
        syscall2(SyscallNumber::MemoryUnmap, addr, length)
    }
}

/// Memory protect
pub fn memory_protect(addr: u64, length: u64, prot: u32) -> i64 {
    unsafe {
        syscall3(
            SyscallNumber::MemoryProtect,
            addr,
            length,
            prot as u64,
        )
    }
}

/// Register signal handler
pub fn signal_register(signal: u32, handler: u64) -> i64 {
    unsafe {
        syscall2(SyscallNumber::SignalRegister, signal as u64, handler)
    }
}

/// Send signal
pub fn signal_send(pid: i32, signal: u32) -> i64 {
    unsafe {
        syscall2(SyscallNumber::SignalSend, pid as u64, signal as u64)
    }
}

/// Get current time
pub fn time_get() -> i64 {
    unsafe {
        syscall0(SyscallNumber::TimeGet)
    }
}

/// Set system time
pub fn time_set(time: u64) -> i64 {
    unsafe {
        syscall1(SyscallNumber::TimeSet, time)
    }
}

/// Set process priority
pub fn process_priority(pid: i32, priority: i32) -> i64 {
    unsafe {
        syscall2(
            SyscallNumber::ProcessPriority,
            pid as u64,
            priority as u64,
        )
    }
}

/// Create a thread
pub fn thread_create(entry: u64, arg: u64) -> i64 {
    unsafe {
        syscall2(SyscallNumber::ThreadCreate, entry, arg)
    }
}

/// Join a thread
pub fn thread_join(tid: i32) -> i64 {
    unsafe {
        syscall1(SyscallNumber::ThreadJoin, tid as u64)
    }
}

// ============================================================================
// PANIC HANDLER
// ============================================================================

// Default panic handler - test binaries override this with their own
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    unsafe {
        // Try to write panic message to stderr (fd 2)
        let msg = b"[PANIC in libtsynos]\n";
        syscall3(SyscallNumber::Write, 2, msg.as_ptr() as u64, msg.len() as u64);
    }
    loop {}
}

// ============================================================================
// UNIT TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_syscall_numbers() {
        assert_eq!(SyscallNumber::Exit as u64, 0);
        assert_eq!(SyscallNumber::Write as u64, 1);
        assert_eq!(SyscallNumber::Socket as u64, 10);
        assert_eq!(SyscallNumber::ThreatDetect as u64, 20);
        assert_eq!(SyscallNumber::AiInference as u64, 27);
        assert_eq!(SyscallNumber::ThreadJoin as u64, 42);
    }
}
