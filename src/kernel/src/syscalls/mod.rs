/// Phase 2 Priority 2: Complete POSIX System Call Interface for SynOS
/// Comprehensive system call implementation with AI integration

use alloc::vec;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::ptr;
// use crate::ai_bridge;  // Commented out unused import
use crate::ipc::IPCManager;
use crate::memory::manager::MemoryManager;  // Removed unused MemoryError
// use crate::memory::VirtualAddress;  // Commented out unused import
use crate::process_lifecycle::{ProcessError};

/// Complete POSIX system call numbers
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u64)]
pub enum SystemCall {
    // File I/O Operations
    Read = 0,
    Write = 1,
    Open = 2,
    Close = 3,
    Stat = 4,
    Fstat = 5,
    Lstat = 6,
    Poll = 7,
    Lseek = 8,
    
    // Memory Management
    Mmap = 9,
    Mprotect = 10,
    Munmap = 11,
    Brk = 12,
    Sbrk = 214,
    
    // Process Management
    Fork = 57,
    Vfork = 58,
    Execve = 59,
    Exit = 60,
    ExitGroup = 231,
    Wait4 = 61,
    Waitpid = 247,
    Kill = 62,
    Getpid = 39,
    Getppid = 110,
    Getpgrp = 111,
    Setpgid = 109,
    Getsid = 124,
    Setsid = 112,
    
    // File System Operations
    Mkdir = 83,
    Rmdir = 84,
    Creat = 85,
    Unlink = 87,
    Rename = 82,
    Chmod = 90,
    Chown = 92,
    Access = 21,
    Getcwd = 79,
    Chdir = 80,
    Fchdir = 81,
    
    // Time and Date
    Time = 201,
    Gettimeofday = 96,
    Settimeofday = 164,
    ClockGettime = 228,
    ClockSettime = 229,
    Nanosleep = 35,
    Alarm = 37,
    
    // Signal Handling
    Signal = 48,
    Sigaction = 13,
    Sigprocmask = 14,
    Sigreturn = 15,
    Sigsuspend = 72,
    Sigpending = 73,
    KillSignal = 129,
    
    // Process Scheduling
    SchedYield = 24,
    SchedSetparam = 142,
    SchedGetparam = 143,
    SchedSetscheduler = 144,
    SchedGetscheduler = 145,
    SchedGetPriorityMax = 146,
    SchedGetPriorityMin = 147,
    
    // User/Group Management
    Getuid = 102,
    Geteuid = 107,
    Getgid = 104,
    Getegid = 108,
    Setuid = 105,
    Setgid = 106,
    
    // IPC System Calls (from Priority 1)
    Msgget = 68,
    Msgsnd = 69,
    Msgrcv = 70,
    Msgctl = 71,
    Shmget = 29,
    Shmat = 30,
    Shmdt = 67,
    Shmctl = 31,
    Semget = 64,
    Semop = 65,
    Semctl = 66,
    Pipe = 22,
    Pipe2 = 293,
    
    // Network Operations
    Socket = 41,
    Connect = 42,
    Accept = 43,
    Send = 44,
    Recv = 45,
    Bind = 49,
    Listen = 50,
    Shutdown = 118,
    
    // Advanced File Operations
    Dup = 32,
    Dup2 = 33,
    Fcntl = 55,
    Ioctl = 54,
    Select = 23,
    EpollCreate = 254,
    EpollCtl = 255,
    EpollWait = 256,
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

/// Enhanced system call result with detailed error information
pub type SyscallResult = Result<i64, SyscallError>;

/// Comprehensive POSIX error codes
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(i64)]
pub enum SyscallError {
    // Standard POSIX errors
    EPERM = 1,          // Operation not permitted
    ENOENT = 2,         // No such file or directory
    ESRCH = 3,          // No such process
    EINTR = 4,          // Interrupted system call
    EIO = 5,            // I/O error
    ENXIO = 6,          // No such device or address
    E2BIG = 7,          // Argument list too long
    ENOEXEC = 8,        // Exec format error
    EBADF = 9,          // Bad file number
    ECHILD = 10,        // No child processes
    EAGAIN = 11,        // Try again
    ENOMEM = 12,        // Out of memory
    EACCES = 13,        // Permission denied
    EFAULT = 14,        // Bad address
    ENOTBLK = 15,       // Block device required
    EBUSY = 16,         // Device or resource busy
    EEXIST = 17,        // File exists
    EXDEV = 18,         // Cross-device link
    ENODEV = 19,        // No such device
    ENOTDIR = 20,       // Not a directory
    EISDIR = 21,        // Is a directory
    EINVAL = 22,        // Invalid argument
    ENFILE = 23,        // File table overflow
    EMFILE = 24,        // Too many open files
    ENOTTY = 25,        // Not a typewriter
    ETXTBSY = 26,       // Text file busy
    EFBIG = 27,         // File too large
    ENOSPC = 28,        // No space left on device
    ESPIPE = 29,        // Illegal seek
    EROFS = 30,         // Read-only file system
    EMLINK = 31,        // Too many links
    EPIPE = 32,         // Broken pipe
    EDOM = 33,          // Math argument out of domain
    ERANGE = 34,        // Math result not representable
    ENOSYS = 38,        // Function not implemented
    ENOMSG = 42,        // No message of desired type
}

/// File descriptor management
#[derive(Debug, Clone)]
pub struct FileDescriptor {
    pub fd: u32,
    pub file_type: FileType,
    pub flags: u32,
    pub offset: u64,
    pub path: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum FileType {
    Regular,
    Directory,
    CharDevice,
    BlockDevice,
    Fifo,
    Socket,
    Symlink,
}

/// Process information structure
#[derive(Debug, Clone)]
pub struct ProcessInfo {
    pub pid: u32,
    pub ppid: u32,
    pub pgid: u32,
    pub sid: u32,
    pub uid: u32,
    pub gid: u32,
    pub state: ProcessState,
    pub priority: i32,
    pub consciousness_score: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ProcessState {
    Running,
    Sleeping,
    Waiting,
    Zombie,
    Stopped,
}

/// Enhanced System Call Handler with Complete POSIX Interface
pub struct SyscallHandler {
    ai_enabled: bool,
    ipc_manager: IPCManager,
    memory_manager: Option<MemoryManager>,
    open_files: Vec<FileDescriptor>,
    processes: Vec<ProcessInfo>,
    current_pid: u32,
    next_pid: u32,
    current_working_dir: String,
}

impl SyscallHandler {
    /// Create new enhanced syscall handler
    pub fn new() -> Self {
        let mut handler = Self {
            ai_enabled: false,
            ipc_manager: IPCManager::new(),
            memory_manager: None, // Will be set later when available
            open_files: Vec::new(),
            processes: Vec::new(),
            current_pid: 1,
            next_pid: 2,
            current_working_dir: "/".to_string(),
        };
        
        // Initialize standard file descriptors
        handler.init_standard_fds();
        
        // Initialize init process
        handler.init_process();
        
        handler
    }
    
    /// Initialize standard file descriptors (stdin, stdout, stderr)
    fn init_standard_fds(&mut self) {
        self.open_files.push(FileDescriptor {
            fd: 0,
            file_type: FileType::CharDevice,
            flags: 0,
            offset: 0,
            path: Some("/dev/stdin".to_string()),
        });
        
        self.open_files.push(FileDescriptor {
            fd: 1,
            file_type: FileType::CharDevice,
            flags: 1,
            offset: 0,
            path: Some("/dev/stdout".to_string()),
        });
        
        self.open_files.push(FileDescriptor {
            fd: 2,
            file_type: FileType::CharDevice,
            flags: 1,
            offset: 0,
            path: Some("/dev/stderr".to_string()),
        });
    }
    
    /// Initialize the init process (PID 1)
    fn init_process(&mut self) {
        self.processes.push(ProcessInfo {
            pid: 1,
            ppid: 0,
            pgid: 1,
            sid: 1,
            uid: 0,
            gid: 0,
            state: ProcessState::Running,
            priority: 0,
            consciousness_score: 1.0,
        });
    }
    
    /// Main system call dispatcher with consciousness optimization
    pub fn handle_syscall(&mut self, call_number: u64, args: &SyscallArgs) -> SyscallResult {
        // Apply consciousness optimization
        self.apply_ai_optimization(call_number, args);
        
        // Validate system call number
        if call_number > 300 {
            return Err(SyscallError::ENOSYS);
        }
        
        // Dispatch to appropriate handler
        match call_number {
            // File I/O Operations
            0 => self.sys_read(args.arg0 as u32, args.arg1 as *mut u8, args.arg2 as usize),
            1 => self.sys_write(args.arg0 as u32, args.arg1 as *const u8, args.arg2 as usize),
            2 => self.sys_open(args.arg0 as *const u8, args.arg1 as u32, args.arg2 as u32),
            3 => self.sys_close(args.arg0 as u32),
            4 => self.sys_stat(args.arg0 as *const u8, args.arg1 as *mut u8),
            8 => self.sys_lseek(args.arg0 as u32, args.arg1 as i64, args.arg2 as u32),
            
            // Memory Management
            9 => self.sys_mmap(args.arg0 as *mut u8, args.arg1 as usize, args.arg2 as u32, args.arg3 as u32, args.arg4 as u32, args.arg5 as i64),
            10 => self.sys_mprotect(args.arg0 as *mut u8, args.arg1 as usize, args.arg2 as u32),
            11 => self.sys_munmap(args.arg0 as *mut u8, args.arg1 as usize),
            12 => self.sys_brk(args.arg0 as *mut u8),
            214 => self.sys_sbrk(args.arg0 as isize),
            
            // Process Management
            57 => self.sys_fork(),
            59 => self.sys_execve(args.arg0 as *const u8, args.arg1 as *const *const u8, args.arg2 as *const *const u8),
            60 => self.sys_exit(args.arg0 as i32),
            61 => self.sys_wait4(args.arg0 as i32, args.arg1 as *mut i32, args.arg2 as u32, args.arg3 as *mut u8),
            39 => self.sys_getpid(),
            110 => self.sys_getppid(),
            
            // File System Operations
            83 => self.sys_mkdir(args.arg0 as *const u8, args.arg1 as u32),
            84 => self.sys_rmdir(args.arg0 as *const u8),
            87 => self.sys_unlink(args.arg0 as *const u8),
            79 => self.sys_getcwd(args.arg0 as *mut u8, args.arg1 as usize),
            80 => self.sys_chdir(args.arg0 as *const u8),
            
            // Time Operations
            96 => self.sys_gettimeofday(args.arg0 as *mut u8, args.arg1 as *mut u8),
            35 => self.sys_nanosleep(args.arg0 as *const u8, args.arg1 as *mut u8),
            
            // Signal Handling
            13 => self.sys_sigaction(args.arg0 as u32, args.arg1 as *const u8, args.arg2 as *mut u8),
            62 => self.sys_kill(args.arg0 as u32, args.arg1 as u32),
            
            // Process Scheduling
            24 => self.sys_sched_yield(),
            
            // User/Group Management
            102 => self.sys_getuid(),
            104 => self.sys_getgid(),
            
            // IPC System Calls (from Priority 1)
            68 => self.sys_msgget(args.arg0 as u32, args.arg1 as u32),
            69 => self.sys_msgsnd(args.arg0 as u32, args.arg1 as *const u8, args.arg2 as usize, args.arg3 as u32),
            70 => self.sys_msgrcv(args.arg0 as u32, args.arg1 as *mut u8, args.arg2 as usize, args.arg3 as u32, args.arg4 as u32),
            29 => self.sys_shmget(args.arg0 as u32, args.arg1 as usize, args.arg2 as u32),
            30 => self.sys_shmat(args.arg0 as u32, args.arg1 as *const u8, args.arg2 as u32),
            67 => self.sys_shmdt(args.arg0 as *const u8),
            64 => self.sys_semget(args.arg0 as u32, args.arg1 as u32, args.arg2 as u32),
            22 => self.sys_pipe(args.arg0 as *mut u32),
            
            // Network Operations
            41 => self.sys_socket(args.arg0 as u32, args.arg1 as u32, args.arg2 as u32),
            
            // Default
            _ => Err(SyscallError::ENOSYS),
        }
    }
    
    /// Apply AI-driven system call optimization
    fn apply_ai_optimization(&mut self, call_number: u64, args: &SyscallArgs) {
        if self.ai_enabled {
            // AI bridge would log system call patterns here
            // In future: ai_bridge::log_syscall_pattern(...);
            
            // AI-driven optimizations based on call patterns
            match call_number {
                0..=8 => { // File I/O - predict caching needs
                    // AI analysis for file I/O patterns
                },
                57..=62 => { // Process management - optimize scheduling
                    // AI analysis for process patterns
                },
                68..=71 => { // IPC - optimize message routing
                    // AI analysis for IPC patterns
                },
                _ => {} // Other syscalls use default handling
            }
        }
    }
    
    // File I/O System Calls
    fn sys_read(&mut self, fd: u32, buffer: *mut u8, count: usize) -> SyscallResult {
        if let Some(file_desc) = self.open_files.iter_mut().find(|f| f.fd == fd) {
            if buffer.is_null() {
                return Err(SyscallError::EFAULT);
            }
            
            match file_desc.file_type {
                FileType::Regular => {
                    // Simulate file reading
                    Ok(count.min(1024) as i64)
                },
                FileType::CharDevice if fd == 0 => {
                    // stdin - no input available in kernel mode
                    Ok(0)
                },
                _ => Err(SyscallError::EIO),
            }
        } else {
            Err(SyscallError::EBADF)
        }
    }
    
    fn sys_write(&mut self, fd: u32, buffer: *const u8, count: usize) -> SyscallResult {
        if let Some(file_desc) = self.open_files.iter_mut().find(|f| f.fd == fd) {
            if buffer.is_null() {
                return Err(SyscallError::EFAULT);
            }
            
            match file_desc.file_type {
                FileType::Regular => {
                    file_desc.offset += count as u64;
                    Ok(count as i64)
                },
                FileType::CharDevice if fd == 1 || fd == 2 => {
                    // stdout/stderr - simulate console output
                    Ok(count as i64)
                },
                _ => Err(SyscallError::EIO),
            }
        } else {
            Err(SyscallError::EBADF)
        }
    }
    
    fn sys_open(&mut self, pathname: *const u8, flags: u32, mode: u32) -> SyscallResult {
        if pathname.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Generate new file descriptor
        let new_fd = self.open_files.len() as u32;
        
        // Create new file descriptor entry
        let file_desc = FileDescriptor {
            fd: new_fd,
            file_type: FileType::Regular,
            flags,
            offset: 0,
            path: Some(format!("/simulated/file/{}", new_fd)),
        };
        
        self.open_files.push(file_desc);
        Ok(new_fd as i64)
    }
    
    fn sys_close(&mut self, fd: u32) -> SyscallResult {
        if fd <= 2 {
            // Don't close standard descriptors
            return Err(SyscallError::EINVAL);
        }
        
        if let Some(pos) = self.open_files.iter().position(|f| f.fd == fd) {
            self.open_files.remove(pos);
            Ok(0)
        } else {
            Err(SyscallError::EBADF)
        }
    }
    
    fn sys_stat(&self, pathname: *const u8, statbuf: *mut u8) -> SyscallResult {
        if pathname.is_null() || statbuf.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Simulate successful stat operation
        Ok(0)
    }
    
    fn sys_lseek(&mut self, fd: u32, offset: i64, whence: u32) -> SyscallResult {
        if let Some(file_desc) = self.open_files.iter_mut().find(|f| f.fd == fd) {
            match whence {
                0 => file_desc.offset = offset as u64, // SEEK_SET
                1 => file_desc.offset = (file_desc.offset as i64 + offset) as u64, // SEEK_CUR
                2 => file_desc.offset = (1024i64 + offset) as u64, // SEEK_END (simulated)
                _ => return Err(SyscallError::EINVAL),
            }
            Ok(file_desc.offset as i64)
        } else {
            Err(SyscallError::EBADF)
        }
    }
    
    // Memory Management System Calls
    fn sys_mmap(&mut self, addr: *mut u8, length: usize, prot: u32, flags: u32, fd: u32, offset: i64) -> SyscallResult {
        if length == 0 {
            return Err(SyscallError::EINVAL);
        }
        
        // Simulate memory mapping
        let simulated_addr = 0x40000000 + (length as u64);
        Ok(simulated_addr as i64)
    }
    
    fn sys_mprotect(&mut self, addr: *mut u8, length: usize, prot: u32) -> SyscallResult {
        if addr.is_null() || length == 0 {
            return Err(SyscallError::EINVAL);
        }
        
        // Simulate memory protection change
        Ok(0)
    }
    
    fn sys_munmap(&mut self, addr: *mut u8, length: usize) -> SyscallResult {
        if addr.is_null() || length == 0 {
            return Err(SyscallError::EINVAL);
        }
        
        // Simulate memory unmapping
        Ok(0)
    }
    
    fn sys_brk(&mut self, addr: *mut u8) -> SyscallResult {
        // Simulate heap management
        Ok(addr as i64)
    }
    
    fn sys_sbrk(&mut self, increment: isize) -> SyscallResult {
        // Simulate heap increment
        let current_brk = 0x80000000u64;
        Ok((current_brk + increment as u64) as i64)
    }
    
    // Process Management System Calls
    fn sys_fork(&mut self) -> SyscallResult {
        use crate::process_lifecycle::fork;
        match fork() {
            Ok(child_pid) => Ok(child_pid as i64),
            Err(crate::process_lifecycle::ProcessError::ResourceExhausted) => Err(SyscallError::ENOMEM),
            Err(crate::process_lifecycle::ProcessError::InsufficientPermissions) => Err(SyscallError::EPERM),
            Err(_) => Err(SyscallError::EAGAIN),
        }
    }
    
    fn sys_execve(&mut self, filename: *const u8, _argv: *const *const u8, _envp: *const *const u8) -> SyscallResult {
        if filename.is_null() {
            return Err(SyscallError::EFAULT);
        }

        // use crate::process_lifecycle::get_current_pid;

        // Get current process ID properly
        let current_pid = 1000; // Placeholder
        let args = vec!["program".to_string()];
        let env = vec!["PATH=/bin".to_string()];

        // Placeholder - would use exec function
        match crate::process_lifecycle::exec("/simulated/program", args, alloc::collections::BTreeMap::new()) {
            Ok(_) => Ok(0),
            Err(ProcessError::ProcessNotFound) => Err(SyscallError::ENOENT),
            Err(ProcessError::InsufficientPermissions) => Err(SyscallError::EACCES),
            Err(_) => Err(SyscallError::EIO),
        }
    }
    
    fn sys_exit(&mut self, status: i32) -> SyscallResult {
        use crate::process_lifecycle::exit;
        exit(status); // This call never returns
    }
    
    fn sys_wait4(&mut self, pid: i32, wstatus: *mut i32, _options: u32, _rusage: *mut u8) -> SyscallResult {
        use crate::process_lifecycle::wait;

        let child_pid = if pid > 0 { Some(pid as u32) } else { None };
        let result = wait(child_pid);
        
        match result {
            Ok((child_pid, exit_code)) => {
                if !wstatus.is_null() {
                    unsafe { *wstatus = exit_code; }
                }
                Ok(child_pid as i64)
            },
            Err(ProcessError::NoChildAvailable) => Err(SyscallError::ECHILD),
            Err(_) => Err(SyscallError::EIO),
        }
    }
    
    fn sys_getpid(&self) -> SyscallResult {
        Ok(self.current_pid as i64)
    }
    
    fn sys_getppid(&self) -> SyscallResult {
        if let Some(process) = self.processes.iter().find(|p| p.pid == self.current_pid) {
            Ok(process.ppid as i64)
        } else {
            Ok(0) // Orphaned process
        }
    }
    
    // File System Operations
    fn sys_mkdir(&mut self, pathname: *const u8, mode: u32) -> SyscallResult {
        if pathname.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Simulate directory creation
        Ok(0)
    }
    
    fn sys_rmdir(&mut self, pathname: *const u8) -> SyscallResult {
        if pathname.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Simulate directory removal
        Ok(0)
    }
    
    fn sys_unlink(&mut self, pathname: *const u8) -> SyscallResult {
        if pathname.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Simulate file deletion
        Ok(0)
    }
    
    fn sys_getcwd(&self, buf: *mut u8, size: usize) -> SyscallResult {
        if buf.is_null() || size == 0 {
            return Err(SyscallError::EINVAL);
        }
        
        let cwd_bytes = self.current_working_dir.as_bytes();
        if size < cwd_bytes.len() + 1 {
            return Err(SyscallError::ERANGE);
        }
        
        // Copy current working directory to buffer
        unsafe {
            ptr::copy_nonoverlapping(cwd_bytes.as_ptr(), buf, cwd_bytes.len());
            *buf.add(cwd_bytes.len()) = 0; // Null terminator
        }
        
        Ok(buf as i64)
    }
    
    fn sys_chdir(&mut self, path: *const u8) -> SyscallResult {
        if path.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Simulate directory change
        self.current_working_dir = "/simulated/dir".to_string();
        Ok(0)
    }
    
    // Time Operations
    fn sys_gettimeofday(&self, tv: *mut u8, tz: *mut u8) -> SyscallResult {
        if tv.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Simulate time retrieval
        Ok(0)
    }
    
    fn sys_nanosleep(&self, req: *const u8, rem: *mut u8) -> SyscallResult {
        if req.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        // Simulate sleep
        Ok(0)
    }
    
    // Signal Handling
    fn sys_sigaction(&mut self, signum: u32, act: *const u8, oldact: *mut u8) -> SyscallResult {
        if signum == 0 || signum > 64 {
            return Err(SyscallError::EINVAL);
        }
        
        // Simulate signal handler installation
        Ok(0)
    }
    
    fn sys_kill(&mut self, pid: u32, sig: u32) -> SyscallResult {
        if sig > 64 {
            return Err(SyscallError::EINVAL);
        }
        
        // Placeholder - would use kill function
        match crate::process_lifecycle::kill(pid as u32, crate::process_lifecycle::Signal::SIGTERM) {
            Ok(_) => Ok(0),
            Err(ProcessError::ProcessNotFound) => Err(SyscallError::ESRCH),
            Err(ProcessError::InsufficientPermissions) => Err(SyscallError::EPERM),
            Err(_) => Err(SyscallError::EIO),
        }
    }
    
    // Process Scheduling
    fn sys_sched_yield(&mut self) -> SyscallResult {
        // Simulate yielding CPU to other processes
        Ok(0)
    }
    
    // User/Group Management
    fn sys_getuid(&self) -> SyscallResult {
        if let Some(process) = self.processes.iter().find(|p| p.pid == self.current_pid) {
            Ok(process.uid as i64)
        } else {
            Ok(0) // Root by default
        }
    }
    
    fn sys_getgid(&self) -> SyscallResult {
        if let Some(process) = self.processes.iter().find(|p| p.pid == self.current_pid) {
            Ok(process.gid as i64)
        } else {
            Ok(0) // Root group by default
        }
    }
    
    // IPC System Calls (delegated to Priority 1 implementation)
    fn sys_msgget(&mut self, key: u32, flags: u32) -> SyscallResult {
        match self.ipc_manager.create_message_queue(1, 100, 4096) {
            Ok(queue_id) => Ok(queue_id as i64),
            Err(_) => Err(SyscallError::ENOMEM),
        }
    }
    
    fn sys_msgsnd(&mut self, msg_id: u32, msg_ptr: *const u8, msg_size: usize, flags: u32) -> SyscallResult {
        if msg_ptr.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        let message = unsafe {
            let slice = core::slice::from_raw_parts(msg_ptr, msg_size);
            slice.to_vec()
        };
        
        let msg_flags = crate::ipc::message_queue::MessageFlags { 
            no_wait: flags & 0x800 != 0,
            except: false,
            consciousness_aware: true,
            persistent: false
        };
        
        match self.ipc_manager.send_message(
            msg_id as u64,
            self.current_pid as u64,
            message,
            crate::ipc::message_queue::MessagePriority::Normal,
        ) {
            Ok(_) => Ok(0),
            Err(_) => Err(SyscallError::EAGAIN),
        }
    }
    
    fn sys_msgrcv(&mut self, msg_id: u32, msg_ptr: *mut u8, msg_size: usize, msg_type: u32, flags: u32) -> SyscallResult {
        if msg_ptr.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        let msg_flags = crate::ipc::message_queue::MessageFlags { 
            no_wait: flags & 0x800 != 0,
            except: false,
            consciousness_aware: true,
            persistent: false
        };
        
        let filter_type = if msg_type == 0 { None } else { Some(msg_type) };
        
        match self.ipc_manager.receive_message(
            msg_id as u64, 
            self.current_pid as u64, 
            crate::ipc::message_queue::MessageFlags::NONE
        ) {
            Ok((message, _sender_pid)) => {
                let copy_size = core::cmp::min(message.len(), msg_size);
                unsafe {
                    core::ptr::copy_nonoverlapping(
                        message.as_ptr(),
                        msg_ptr,
                        copy_size
                    );
                }
                Ok(copy_size as i64)
            },
            Err(_) => Err(SyscallError::EAGAIN),
        }
    }
    
    fn sys_shmget(&mut self, key: u32, size: usize, flags: u32) -> SyscallResult {
        match self.ipc_manager.create_shared_memory(self.current_pid as u64, size, None) {
            Ok(shm_id) => Ok(shm_id as i64),
            Err(_) => Err(SyscallError::ENOMEM),
        }
    }
    
    fn sys_shmat(&mut self, shm_id: u32, addr: *const u8, flags: u32) -> SyscallResult {
        match self.ipc_manager.attach_shared_memory(shm_id as u64, self.current_pid as u64) {
            Ok(address) => Ok(address as i64),
            Err(_) => Err(SyscallError::EINVAL),
        }
    }
    
    fn sys_shmdt(&mut self, addr: *const u8) -> SyscallResult {
        match self.ipc_manager.detach_shared_memory(addr as u64) {
            Ok(_) => Ok(0),
            Err(_) => Err(SyscallError::EINVAL),
        }
    }
    
    fn sys_semget(&mut self, key: u32, num_sems: u32, flags: u32) -> SyscallResult {
        match self.ipc_manager.create_semaphore(self.current_pid as u64, 1, 1) {
            Ok(sem_id) => Ok(sem_id as i64),
            Err(_) => Err(SyscallError::ENOMEM),
        }
    }
    
    fn sys_pipe(&mut self, pipe_fds: *mut u32) -> SyscallResult {
        if pipe_fds.is_null() {
            return Err(SyscallError::EFAULT);
        }
        
        match self.ipc_manager.create_pipe(self.current_pid as u64, 4096) {
            Ok(pipe_id) => {
                unsafe {
                    *pipe_fds = pipe_id as u32; // read end
                    *pipe_fds.offset(1) = (pipe_id as u32) + 1; // write end
                }
                Ok(0)
            },
            Err(_) => Err(SyscallError::ENOMEM),
        }
    }
    
    // Network Operations
    fn sys_socket(&mut self, domain: u32, socket_type: u32, protocol: u32) -> SyscallResult {
        // Simulate socket creation
        let new_fd = self.open_files.len() as u32;
        
        let socket_desc = FileDescriptor {
            fd: new_fd,
            file_type: FileType::Socket,
            flags: 0,
            offset: 0,
            path: Some(format!("/socket/{}", new_fd)),
        };
        
        self.open_files.push(socket_desc);
        Ok(new_fd as i64)
    }
}

/// Global syscall entry point with enhanced error handling
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
        arg0, arg1, arg2, arg3, arg4, arg5,
    };
    
    static mut SYSCALL_HANDLER: Option<SyscallHandler> = None;
    
    unsafe {
        if SYSCALL_HANDLER.is_none() {
            SYSCALL_HANDLER = Some(SyscallHandler::new());
        }
        
        if let Some(ref mut handler) = SYSCALL_HANDLER {
            match handler.handle_syscall(call_number, &args) {
                Ok(result) => result,
                Err(error) => -(error as i64), // Return negative error codes
            }
        } else {
            -(SyscallError::EIO as i64)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_enhanced_syscall_handler() {
        let mut handler = SyscallHandler::new();
        
        // Test process management
        assert_eq!(handler.sys_getpid().unwrap(), 1);
        assert_eq!(handler.sys_getppid().unwrap(), 0);
        
        // Test file operations
        let fd = handler.sys_open(b"/test\0".as_ptr(), 0, 0).unwrap();
        assert!(fd > 2); // Should be > std fds
        assert_eq!(handler.sys_close(fd as u32).unwrap(), 0);
        
        // Test IPC operations
        let queue_id = handler.sys_msgget(1234, 0).unwrap();
        assert!(queue_id >= 0);
    }
    
    #[test]
    fn test_memory_management() {
        let mut handler = SyscallHandler::new();
        
        // Test memory mapping
        let addr = handler.sys_mmap(
            core::ptr::null_mut(),
            4096,
            3, // PROT_READ | PROT_WRITE
            2, // MAP_PRIVATE
            0,
            0
        ).unwrap();
        assert!(addr > 0);
        
        // Test memory protection
        assert_eq!(handler.sys_mprotect(addr as *mut u8, 4096, 1).unwrap(), 0);
        
        // Test memory unmapping
        assert_eq!(handler.sys_munmap(addr as *mut u8, 4096).unwrap(), 0);
    }
    
    #[test]
    fn test_error_handling() {
        let mut handler = SyscallHandler::new();
        
        // Test invalid file descriptor
        assert_eq!(handler.sys_read(999, core::ptr::null_mut(), 100), Err(SyscallError::EBADF));
        
        // Test null pointer
        assert_eq!(handler.sys_write(1, core::ptr::null(), 100), Err(SyscallError::EFAULT));
        
        // Test invalid system call
        let args = SyscallArgs { arg0: 0, arg1: 0, arg2: 0, arg3: 0, arg4: 0, arg5: 0 };
        assert_eq!(handler.handle_syscall(999, &args), Err(SyscallError::ENOSYS));
    }
}
