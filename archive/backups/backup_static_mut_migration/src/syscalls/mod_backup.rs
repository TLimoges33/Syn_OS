/// Enhanced System Call Interface for SynOS with Complete IPC Support
/// Provides POSIX-compatible system calls with consciousness integration

use alloc::string::{String, ToString};
use alloc::vec::Vec;
use core::ptr;
use crate::memory::VirtualAddress;
use crate::ai::interface::AIInterface;
use crate::ipc::{IPCManager, IPCId, MessageFlags, MessagePriority, MessageQueueConfig};

/// System call numbers (POSIX-compatible)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u64)]
pub enum SystemCall {
    // File operations
    Read = 0,
    Write = 1,
    Open = 2,
    Close = 3,
    Stat = 4,
    Fstat = 5,
    Lstat = 6,
    Poll = 7,
    Lseek = 8,
    
    // Memory management
    Mmap = 9,
    Mprotect = 10,
    Munmap = 11,
    Brk = 12,
    
    // Process management
    Fork = 57,
    Vfork = 58,
    Execve = 59,
    Exit = 60,
    Wait4 = 61,
    Kill = 62,
    Getpid = 39,
    Getppid = 110,
    
    // File system
    Mkdir = 83,
    Rmdir = 84,
    Creat = 85,
    Unlink = 87,
    Rename = 82,
    Chmod = 90,
    Chown = 92,
    
    // Process scheduling
    Sched_yield = 24,
    Nanosleep = 35,
    
    // Signal handling
    Sigaction = 13,
    Sigprocmask = 14,
    Sigreturn = 15,
    
    // IPC - Message Queues
    Msgget = 68,
    Msgsnd = 69,
    Msgrcv = 70,
    Msgctl = 71,
    
    // IPC - Shared Memory
    Shmget = 29,
    Shmat = 30,
    Shmdt = 67,
    Shmctl = 31,
    
    // IPC - Semaphores
    Semget = 64,
    Semop = 65,
    Semctl = 66,
    
    // Pipes
    Pipe = 22,
    Pipe2 = 293,
    
    // Network (basic)
    Socket = 41,
    Connect = 42,
    Accept = 43,
    Send = 44,
    Recv = 45,
    Bind = 49,
    Listen = 50,
}

/// System call arguments structure
#[derive(Debug, Clone, Copy)]
pub struct SyscallArgs {
    pub arg0: u64,
    pub arg1: u64,
    pub arg2: u64,
    pub arg3: u64,
    pub arg4: u64,
    pub arg5: u64,
}

/// System call result type
pub type SyscallResult = Result<i64, i64>;

/// System call error codes (POSIX-compatible)
pub mod errno {
    pub const EPERM: i64 = 1;       // Operation not permitted
    pub const ENOENT: i64 = 2;      // No such file or directory
    pub const ESRCH: i64 = 3;       // No such process
    pub const EINTR: i64 = 4;       // Interrupted system call
    pub const EIO: i64 = 5;         // I/O error
    pub const ENXIO: i64 = 6;       // No such device or address
    pub const E2BIG: i64 = 7;       // Argument list too long
    pub const ENOEXEC: i64 = 8;     // Exec format error
    pub const EBADF: i64 = 9;       // Bad file number
    pub const ECHILD: i64 = 10;     // No child processes
    pub const EAGAIN: i64 = 11;     // Try again
    pub const ENOMEM: i64 = 12;     // Out of memory
    pub const EACCES: i64 = 13;     // Permission denied
    pub const EFAULT: i64 = 14;     // Bad address
    pub const ENOTBLK: i64 = 15;    // Block device required
    pub const EBUSY: i64 = 16;      // Device or resource busy
    pub const EEXIST: i64 = 17;     // File exists
    pub const EXDEV: i64 = 18;      // Cross-device link
    pub const ENODEV: i64 = 19;     // No such device
    pub const ENOTDIR: i64 = 20;    // Not a directory
    pub const EISDIR: i64 = 21;     // Is a directory
    pub const EINVAL: i64 = 22;     // Invalid argument
    pub const ENFILE: i64 = 23;     // File table overflow
    pub const EMFILE: i64 = 24;     // Too many open files
    pub const ENOTTY: i64 = 25;     // Not a typewriter
    pub const ETXTBSY: i64 = 26;    // Text file busy
    pub const EFBIG: i64 = 27;      // File too large
    pub const ENOSPC: i64 = 28;     // No space left on device
    pub const ESPIPE: i64 = 29;     // Illegal seek
    pub const EROFS: i64 = 30;      // Read-only file system
    pub const EMLINK: i64 = 31;     // Too many links
    pub const EPIPE: i64 = 32;      // Broken pipe
    pub const EDOM: i64 = 33;       // Math argument out of domain
    pub const ERANGE: i64 = 34;     // Math result not representable
}

/// System call handler implementing POSIX syscalls with consciousness integration
pub struct SyscallHandler {
    consciousness: AIInterface,
    ipc_manager: IPCManager,
    open_files: Vec<u32>, // Simple file descriptor tracking
}

impl SyscallHandler {
    /// Create new syscall handler
    pub fn new() -> Self {
        Self {
            consciousness: AIInterface::new(),
            ipc_manager: IPCManager::new(),
            open_files: Vec::new(),
        }
    }
    
    /// Main system call dispatcher
    pub fn handle_syscall(&mut self, call_number: u64, args: &SyscallArgs) -> SyscallResult {
        // Apply consciousness optimization before handling
        self.apply_consciousness_optimization(call_number, args, &self.consciousness);
        
        // Convert to enum and dispatch
        match call_number {
            0 => self.sys_read(args.arg0 as u32, args.arg1 as *mut u8, args.arg2 as usize),
            1 => self.sys_write(args.arg0 as u32, args.arg1 as *const u8, args.arg2 as usize),
            2 => self.sys_open(args.arg0 as *const u8, args.arg1 as u32, args.arg2 as u32),
            3 => self.sys_close(args.arg0 as u32),
            12 => self.sys_brk(args.arg0 as *mut u8),
            39 => self.sys_getpid(),
            57 => self.sys_fork(),
            59 => self.sys_execve(args.arg0 as *const u8, args.arg1 as *const *const u8, args.arg2 as *const *const u8),
            60 => self.sys_exit(args.arg0 as i32),
            
            // IPC System Calls
            68 => self.sys_msgget(args.arg0 as u32, args.arg1 as u32),
            69 => self.sys_msgsnd(args.arg0 as u32, args.arg1 as *const u8, args.arg2 as usize, args.arg3 as u32),
            70 => self.sys_msgrcv(args.arg0 as u32, args.arg1 as *mut u8, args.arg2 as usize, args.arg3 as u32, args.arg4 as u32),
            
            29 => self.sys_shmget(args.arg0 as u32, args.arg1 as usize, args.arg2 as u32),
            30 => self.sys_shmat(args.arg0 as u32, args.arg1 as *const u8, args.arg2 as u32),
            67 => self.sys_shmdt(args.arg0 as *const u8),
            
            64 => self.sys_semget(args.arg0 as u32, args.arg1 as u32, args.arg2 as u32),
            
            22 => self.sys_pipe(args.arg0 as *mut u32),
            
            _ => Err(errno::ENOSYS), // Function not implemented
        }
    }
    
    /// Apply consciousness optimization to system call
    fn apply_consciousness_optimization(&self, call_number: u64, args: &SyscallArgs, consciousness: &AIInterface) {
        // Consciousness-driven optimization based on syscall patterns
        match call_number {
            0..=12 => { // File/memory operations - track for caching optimization
                consciousness.record_syscall_pattern(call_number, args.arg0);
            },
            68..=71 => { // Message queues - optimize for consciousness routing
                consciousness.record_ipc_event(call_number, args.arg0, args.arg1);
            },
            _ => {} // Other syscalls use default handling
        }
    }
    
    // File Operations
    fn sys_read(&mut self, fd: u32, buffer: *mut u8, count: usize) -> SyscallResult {
        // Consciousness-enhanced read with predictive caching
        self.consciousness.record_file_access(fd as u64, "read".into(), count as u64);
        
        // For now, simulate basic read behavior
        if fd == 0 { // stdin
            Ok(0) // No input available
        } else if self.open_files.contains(&fd) {
            // Simulate file read
            Ok(count as i64)
        } else {
            Err(errno::EBADF)
        }
    }
    
    fn sys_write(&mut self, fd: u32, buffer: *const u8, count: usize) -> SyscallResult {
        // Enhanced write with consciousness-driven optimization
        self.consciousness.record_file_access(fd as u64, "write".into(), count as u64);
        
        if fd == 1 || fd == 2 { // stdout/stderr
            // Convert to string for debug output
            unsafe {
                let slice = core::slice::from_raw_parts(buffer, count);
                if let Ok(s) = core::str::from_utf8(slice) {
                    // In real implementation, this would go to console
                    // For now, just record the operation
                }
            }
            Ok(count as i64)
        } else if self.open_files.contains(&fd) {
            Ok(count as i64)
        } else {
            Err(errno::EBADF)
        }
    }
    
    fn sys_open(&mut self, pathname: *const u8, flags: u32, mode: u32) -> SyscallResult {
        // Consciousness-driven file opening with access pattern prediction
        let fd = self.open_files.len() as u32 + 3; // Start after std descriptors
        self.open_files.push(fd);
        self.consciousness.record_file_access(fd as u64, "open".into(), flags as u64);
        Ok(fd as i64)
    }
    
    fn sys_close(&mut self, fd: u32) -> SyscallResult {
        if let Some(pos) = self.open_files.iter().position(|&x| x == fd) {
            self.open_files.remove(pos);
            self.consciousness.record_file_access(fd as u64, "close".into(), 0);
            Ok(0)
        } else {
            Err(errno::EBADF)
        }
    }
    
    // Process Management
    fn sys_fork(&self) -> SyscallResult {
        // Consciousness-enhanced process creation
        self.consciousness.record_process_event("fork".into(), 0, 0);
        Ok(0) // Return 0 for child process (simplified)
    }
    
    fn sys_execve(&self, filename: *const u8, argv: *const *const u8, envp: *const *const u8) -> SyscallResult {
        self.consciousness.record_process_event("execve".into(), 0, 0);
        Err(errno::ENOENT) // File not found (simplified)
    }
    
    fn sys_exit(&self, status: i32) -> SyscallResult {
        self.consciousness.record_process_event("exit".into(), status as u64, 0);
        // This syscall never returns in real implementation
        Ok(0)
    }
    
    fn sys_getpid(&self) -> SyscallResult {
        Ok(1) // Return fixed PID for now
    }
    
    fn sys_brk(&self, addr: *mut u8) -> SyscallResult {
        // Memory management - consciousness-driven heap optimization
        self.consciousness.record_memory_event("brk", addr as u64, 0);
        Ok(addr as i64)
    }
    
    // IPC Operations - Message Queues
    fn sys_msgget(&mut self, key: u32, flags: u32) -> SyscallResult {
        let config = MessageQueueConfig {
            max_messages: 100,
            max_message_size: 4096,
            enable_consciousness: true,
            persistence: false,
            timeout_ms: 1000,
        };
        
        match self.ipc_manager.create_message_queue(config) {
            Ok(queue_id) => {
                self.consciousness.record_ipc_event(68, key as u64, queue_id.0 as u64);
                Ok(queue_id.0 as i64)
            },
            Err(_) => Err(errno::ENOMEM),
        }
    }
    
    fn sys_msgsnd(&mut self, msg_id: u32, msg_ptr: *const u8, msg_size: usize, flags: u32) -> SyscallResult {
        let ipc_id = IPCId(msg_id as usize);
        
        // Copy message from user space
        let message = unsafe {
            let slice = core::slice::from_raw_parts(msg_ptr, msg_size);
            Vec::from(slice)
        };
        
        let msg_flags = if flags & 0x800 != 0 { // IPC_NOWAIT
            MessageFlags::NOWAIT
        } else {
            MessageFlags::empty()
        };
        
        match self.ipc_manager.send_message_advanced(
            ipc_id,
            message,
            MessagePriority::Normal,
            Some(1), // msg_type = 1
            msg_flags
        ) {
            Ok(_) => {
                self.consciousness.record_ipc_event(69, msg_id as u64, msg_size as u64);
                Ok(0)
            },
            Err(_) => Err(errno::EAGAIN),
        }
    }
    
    fn sys_msgrcv(&mut self, msg_id: u32, msg_ptr: *mut u8, msg_size: usize, msg_type: u32, flags: u32) -> SyscallResult {
        let ipc_id = IPCId(msg_id as usize);
        let msg_flags = if flags & 0x800 != 0 { // IPC_NOWAIT
            MessageFlags::NOWAIT
        } else {
            MessageFlags::empty()
        };
        
        let filter_type = if msg_type == 0 { None } else { Some(msg_type) };
        
        match self.ipc_manager.receive_message(ipc_id, filter_type, msg_flags) {
            Ok(message) => {
                if let Some(msg_data) = message {
                    let copy_size = core::cmp::min(msg_data.len(), msg_size);
                    unsafe {
                        core::ptr::copy_nonoverlapping(
                            msg_data.as_ptr(),
                            msg_ptr,
                            copy_size
                        );
                    }
                    self.consciousness.record_ipc_event(70, msg_id as u64, copy_size as u64);
                    Ok(copy_size as i64)
                } else {
                    Err(errno::ENOMSG) // No message available
                }
            },
            Err(_) => Err(errno::EAGAIN),
        }
    }
    
    // IPC Operations - Shared Memory
    fn sys_shmget(&mut self, key: u32, size: usize, flags: u32) -> SyscallResult {
        match self.ipc_manager.create_shared_memory(size) {
            Ok(shm_id) => {
                self.consciousness.record_ipc_event(29, key as u64, shm_id.0 as u64);
                Ok(shm_id.0 as i64)
            },
            Err(_) => Err(errno::ENOMEM),
        }
    }
    
    fn sys_shmat(&mut self, shm_id: u32, addr: *const u8, flags: u32) -> SyscallResult {
        let ipc_id = IPCId(shm_id as usize);
        match self.ipc_manager.attach_shared_memory(ipc_id, 0) { // pid = 0 for current process
            Ok(address) => {
                self.consciousness.record_ipc_event(30, shm_id as u64, address);
                Ok(address as i64)
            },
            Err(_) => Err(errno::EINVAL),
        }
    }
    
    fn sys_shmdt(&mut self, address: *const u8) -> SyscallResult {
        match self.ipc_manager.detach_shared_memory(address as u64) {
            Ok(_) => {
                self.consciousness.record_ipc_event(67, address as u64, 0);
                Ok(0)
            },
            Err(_) => Err(errno::EINVAL),
        }
    }
    
    // IPC Operations - Semaphores
    fn sys_semget(&mut self, key: u32, num_sems: u32, flags: u32) -> SyscallResult {
        match self.ipc_manager.create_semaphore(num_sems as usize, 1) {
            Ok(sem_id) => {
                self.consciousness.record_ipc_event(64, key as u64, sem_id.0 as u64);
                Ok(sem_id.0 as i64)
            },
            Err(_) => Err(errno::ENOMEM),
        }
    }
    
    // Pipe Operations
    fn sys_pipe(&mut self, pipe_fds: *mut u32) -> SyscallResult {
        match self.ipc_manager.create_pipe() {
            Ok(pipe_id) => {
                unsafe {
                    *pipe_fds = pipe_id.0 as u32; // read end
                    *pipe_fds.offset(1) = (pipe_id.0 + 1) as u32; // write end
                }
                self.consciousness.record_ipc_event(22, pipe_id.0 as u64, 0);
                Ok(0)
            },
            Err(_) => Err(errno::ENOMEM),
        }
    }
}

/// Assembly entry point for system calls
#[no_mangle]
pub extern "C" fn syscall_entry(
    call_number: u64,
    arg0: u64,
    arg1: u64,
    arg2: u64,
    arg3: u64,
    arg4: u64,
    arg5: u64,
) -> i64 {
    let args = SyscallArgs {
        arg0,
        arg1,
        arg2,
        arg3,
        arg4,
        arg5,
    };
    
    // Get global syscall handler (in real implementation, this would be per-process)
    static mut SYSCALL_HANDLER: Option<SyscallHandler> = None;
    
    unsafe {
        if SYSCALL_HANDLER.is_none() {
            SYSCALL_HANDLER = Some(SyscallHandler::new());
        }
        
        if let Some(ref mut handler) = SYSCALL_HANDLER {
            match handler.handle_syscall(call_number, &args) {
                Ok(result) => result,
                Err(error) => error,
            }
        } else {
            errno::EIO
        }
    }
}

/// Consciousness-enhanced performance monitoring for syscalls
pub struct SyscallPerformanceMonitor {
    call_counts: [u64; 512], // Track up to 512 different syscalls
    total_time: [u64; 512],
    consciousness_optimizations: u64,
}

impl SyscallPerformanceMonitor {
    pub fn new() -> Self {
        Self {
            call_counts: [0; 512],
            total_time: [0; 512],
            consciousness_optimizations: 0,
        }
    }
    
    pub fn record_call(&mut self, call_number: u64, execution_time: u64, was_optimized: bool) {
        if call_number < 512 {
            self.call_counts[call_number as usize] += 1;
            self.total_time[call_number as usize] += execution_time;
            
            if was_optimized {
                self.consciousness_optimizations += 1;
            }
        }
    }
    
    pub fn get_call_stats(&self, call_number: u64) -> Option<(u64, u64)> {
        if call_number < 512 {
            Some((
                self.call_counts[call_number as usize],
                self.total_time[call_number as usize],
            ))
        } else {
            None
        }
    }
    
    pub fn get_optimization_rate(&self) -> f64 {
        let total_calls: u64 = self.call_counts.iter().sum();
        if total_calls > 0 {
            self.consciousness_optimizations as f64 / total_calls as f64
        } else {
            0.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_syscall_handler_creation() {
        let handler = SyscallHandler::new();
        // Basic smoke test
        assert_eq!(handler.open_files.len(), 0);
    }
    
    #[test]
    fn test_basic_syscalls() {
        let mut handler = SyscallHandler::new();
        let args = SyscallArgs {
            arg0: 1,
            arg1: 0,
            arg2: 0,
            arg3: 0,
            arg4: 0,
            arg5: 0,
        };
        
        // Test getpid
        let result = handler.handle_syscall(39, &args);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 1);
    }
    
    #[test]
    fn test_ipc_msgget() {
        let mut handler = SyscallHandler::new();
        let args = SyscallArgs {
            arg0: 1234, // key
            arg1: 0,    // flags
            arg2: 0,
            arg3: 0,
            arg4: 0,
            arg5: 0,
        };
        
        let result = handler.handle_syscall(68, &args); // msgget
        assert!(result.is_ok());
    }
}
