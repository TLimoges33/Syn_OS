/// Process Control Block (PCB) for SynOS Phase 5
/// Manages process state, scheduling, and resources

use alloc::string::String;
use alloc::vec::Vec;
use alloc::collections::BTreeMap;
use core::ptr::NonNull;
use crate::process::user_memory::{UserSpaceMemory, MemoryError};

/// Process identifier type
pub type ProcessId = u32;

/// Thread identifier type  
pub type ThreadId = u32;

/// Process scheduling priority
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Priority {
    Idle = 0,
    Low = 1,
    Normal = 2,
    High = 3,
    RealTime = 4,
}

/// Process state enumeration
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ProcessState {
    Created,        // Process created but not yet scheduled
    Ready,          // Ready to run
    Running,        // Currently executing
    Blocked,        // Waiting for I/O or other event
    Sleeping,       // Sleeping for specified time
    Zombie,         // Terminated but not yet reaped
    Terminated,     // Fully terminated and cleaned up
}

/// CPU register context for process switching
#[derive(Debug, Clone, Copy)]
#[repr(C)]
pub struct CpuContext {
    // General purpose registers
    pub rax: u64,
    pub rbx: u64,
    pub rcx: u64,
    pub rdx: u64,
    pub rsi: u64,
    pub rdi: u64,
    pub rbp: u64,
    pub rsp: u64,
    pub r8: u64,
    pub r9: u64,
    pub r10: u64,
    pub r11: u64,
    pub r12: u64,
    pub r13: u64,
    pub r14: u64,
    pub r15: u64,
    
    // Control registers
    pub rip: u64,
    pub rflags: u64,
    
    // Segment registers
    pub cs: u16,
    pub ss: u16,
    pub ds: u16,
    pub es: u16,
    pub fs: u16,
    pub gs: u16,
}

impl Default for CpuContext {
    fn default() -> Self {
        Self {
            rax: 0, rbx: 0, rcx: 0, rdx: 0,
            rsi: 0, rdi: 0, rbp: 0, rsp: 0,
            r8: 0, r9: 0, r10: 0, r11: 0,
            r12: 0, r13: 0, r14: 0, r15: 0,
            rip: 0, rflags: 0x200, // IF flag set
            cs: 0x23, ss: 0x1b, ds: 0x1b, es: 0x1b, fs: 0x1b, gs: 0x1b, // User mode segments
        }
    }
}

/// File descriptor entry
#[derive(Debug, Clone)]
pub struct FileDescriptor {
    pub fd: i32,
    pub file_type: FileType,
    pub flags: u32,
    pub position: u64,
}

#[derive(Debug, Clone)]
pub enum FileType {
    Regular(String),    // Regular file with path
    Directory(String),  // Directory with path
    Device(String),     // Device file
    Pipe,              // Anonymous pipe
    Socket,            // Network socket
}

/// Process resource limits
#[derive(Debug, Clone)]
pub struct ResourceLimits {
    pub max_memory: u64,        // Maximum memory usage
    pub max_open_files: u32,    // Maximum open file descriptors
    pub max_cpu_time: u64,      // Maximum CPU time in microseconds
    pub max_children: u32,      // Maximum child processes
}

impl Default for ResourceLimits {
    fn default() -> Self {
        Self {
            max_memory: 256 * 1024 * 1024,  // 256MB default
            max_open_files: 256,
            max_cpu_time: u64::MAX,         // Unlimited by default
            max_children: 32,
        }
    }
}

/// Process statistics and accounting
#[derive(Debug, Clone)]
pub struct ProcessStats {
    pub cpu_time_user: u64,     // User mode CPU time (microseconds)
    pub cpu_time_kernel: u64,   // Kernel mode CPU time (microseconds)
    pub memory_peak: u64,       // Peak memory usage
    pub page_faults: u64,       // Number of page faults
    pub context_switches: u64,  // Number of context switches
    pub syscalls: u64,          // Number of system calls made
    pub start_time: u64,        // Process start time (timestamp)
}

impl Default for ProcessStats {
    fn default() -> Self {
        Self {
            cpu_time_user: 0,
            cpu_time_kernel: 0,
            memory_peak: 0,
            page_faults: 0,
            context_switches: 0,
            syscalls: 0,
            start_time: 0, // Should be set to current time when process starts
        }
    }
}

/// Process Control Block - main process structure
#[derive(Debug)]
pub struct ProcessControlBlock {
    // Process identification
    pub pid: ProcessId,
    pub parent_pid: Option<ProcessId>,
    pub process_group_id: ProcessId,
    pub session_id: ProcessId,
    
    // Process state
    pub state: ProcessState,
    pub priority: Priority,
    pub exit_code: Option<i32>,
    
    // CPU context
    pub context: CpuContext,
    pub kernel_stack: Option<NonNull<u8>>,
    
    // Memory management
    pub memory: UserSpaceMemory,
    
    // File system
    pub working_directory: String,
    pub file_descriptors: BTreeMap<i32, FileDescriptor>,
    pub next_fd: i32,
    
    // Process hierarchy
    pub children: Vec<ProcessId>,
    
    // Resource management
    pub limits: ResourceLimits,
    pub stats: ProcessStats,
    
    // Scheduling
    pub time_slice_remaining: u64,  // Remaining time slice in microseconds
    pub sleep_until: Option<u64>,   // Wake up time for sleeping processes
    
    // Process metadata
    pub name: String,
    pub command_line: Vec<String>,
    pub environment: BTreeMap<String, String>,
    
    // Signal handling (simplified)
    pub pending_signals: u64,      // Bitmask of pending signals
    pub signal_mask: u64,          // Bitmask of blocked signals
}

/// Errors that can occur during process operations
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ProcessError {
    InvalidProcessId,
    ProcessNotFound,
    InsufficientMemory,
    ResourceLimitExceeded,
    InvalidState,
    PermissionDenied,
    InvalidFileDescriptor,
    TooManyOpenFiles,
    MemoryError(MemoryError),
}

impl From<MemoryError> for ProcessError {
    fn from(error: MemoryError) -> Self {
        ProcessError::MemoryError(error)
    }
}

impl ProcessControlBlock {
    /// Create a new process control block
    pub fn new(
        pid: ProcessId,
        parent_pid: Option<ProcessId>,
        name: String,
        entry_point: u64,
    ) -> Result<Self, ProcessError> {
        let memory = UserSpaceMemory::new(pid)?;
        
        let mut context = CpuContext::default();
        context.rip = entry_point;
        
        let mut pcb = Self {
            pid,
            parent_pid,
            process_group_id: pid, // Initially same as PID
            session_id: pid,       // Initially same as PID
            
            state: ProcessState::Created,
            priority: Priority::Normal,
            exit_code: None,
            
            context,
            kernel_stack: None,
            
            memory,
            
            working_directory: String::from("/"),
            file_descriptors: BTreeMap::new(),
            next_fd: 3, // 0, 1, 2 reserved for stdin, stdout, stderr
            
            children: Vec::new(),
            
            limits: ResourceLimits::default(),
            stats: ProcessStats::default(),
            
            time_slice_remaining: 10000, // 10ms default time slice
            sleep_until: None,
            
            name,
            command_line: Vec::new(),
            environment: BTreeMap::new(),
            
            pending_signals: 0,
            signal_mask: 0,
        };
        
        // Set up standard file descriptors
        pcb.setup_standard_fds()?;
        
        Ok(pcb)
    }

    /// Set up the process memory layout
    pub fn setup_memory_layout(&mut self, segments: &[crate::process::elf_loader::LoadedSegment]) -> Result<u64, ProcessError> {
        // Load ELF segments
        self.memory.load_elf_segments(segments)?;
        
        // Set up stack
        let stack_pointer = self.memory.setup_stack()?;
        self.context.rsp = stack_pointer;
        
        Ok(stack_pointer)
    }

    /// Allocate heap memory for the process
    pub fn allocate_heap(&mut self, size: u64) -> Result<u64, ProcessError> {
        let addr = self.memory.allocate_heap(size)?;
        
        // Update peak memory usage
        let current_memory = self.memory.get_memory_stats().total_allocated;
        if current_memory > self.stats.memory_peak {
            self.stats.memory_peak = current_memory;
        }
        
        // Check resource limits
        if current_memory > self.limits.max_memory {
            return Err(ProcessError::ResourceLimitExceeded);
        }
        
        Ok(addr)
    }

    /// Open a file descriptor
    pub fn open_file(&mut self, path: String, flags: u32) -> Result<i32, ProcessError> {
        if self.file_descriptors.len() >= self.limits.max_open_files as usize {
            return Err(ProcessError::TooManyOpenFiles);
        }
        
        let fd = self.next_fd;
        self.next_fd += 1;
        
        let file_desc = FileDescriptor {
            fd,
            file_type: FileType::Regular(path),
            flags,
            position: 0,
        };
        
        self.file_descriptors.insert(fd, file_desc);
        Ok(fd)
    }

    /// Close a file descriptor
    pub fn close_file(&mut self, fd: i32) -> Result<(), ProcessError> {
        self.file_descriptors.remove(&fd)
            .ok_or(ProcessError::InvalidFileDescriptor)?;
        Ok(())
    }

    /// Get file descriptor
    pub fn get_file_descriptor(&self, fd: i32) -> Option<&FileDescriptor> {
        self.file_descriptors.get(&fd)
    }

    /// Add child process
    pub fn add_child(&mut self, child_pid: ProcessId) -> Result<(), ProcessError> {
        if self.children.len() >= self.limits.max_children as usize {
            return Err(ProcessError::ResourceLimitExceeded);
        }
        
        self.children.push(child_pid);
        Ok(())
    }

    /// Remove child process
    pub fn remove_child(&mut self, child_pid: ProcessId) {
        self.children.retain(|&pid| pid != child_pid);
    }

    /// Set process state
    pub fn set_state(&mut self, new_state: ProcessState) {
        self.state = new_state;
        
        if new_state == ProcessState::Running {
            self.stats.context_switches += 1;
        }
    }

    /// Check if process is schedulable
    pub fn is_schedulable(&self) -> bool {
        matches!(self.state, ProcessState::Ready | ProcessState::Running)
    }

    /// Check if process should wake up
    pub fn should_wake_up(&self, current_time: u64) -> bool {
        if let Some(wake_time) = self.sleep_until {
            current_time >= wake_time
        } else {
            false
        }
    }

    /// Set process to sleep until specified time
    pub fn sleep_until(&mut self, wake_time: u64) {
        self.sleep_until = Some(wake_time);
        self.state = ProcessState::Sleeping;
    }

    /// Wake up sleeping process
    pub fn wake_up(&mut self) {
        if self.state == ProcessState::Sleeping {
            self.sleep_until = None;
            self.state = ProcessState::Ready;
        }
    }

    /// Terminate process with exit code
    pub fn terminate(&mut self, exit_code: i32) {
        self.exit_code = Some(exit_code);
        self.state = ProcessState::Zombie;
    }

    /// Get memory usage statistics
    pub fn get_memory_usage(&self) -> u64 {
        self.memory.get_memory_stats().total_allocated
    }

    /// Update CPU time statistics
    pub fn update_cpu_time(&mut self, user_time: u64, kernel_time: u64) {
        self.stats.cpu_time_user += user_time;
        self.stats.cpu_time_kernel += kernel_time;
    }

    /// Set environment variable
    pub fn set_env(&mut self, key: String, value: String) {
        self.environment.insert(key, value);
    }

    /// Get environment variable
    pub fn get_env(&self, key: &str) -> Option<&String> {
        self.environment.get(key)
    }

    // Helper methods

    fn setup_standard_fds(&mut self) -> Result<(), ProcessError> {
        // stdin (fd 0)
        let stdin = FileDescriptor {
            fd: 0,
            file_type: FileType::Device(String::from("/dev/stdin")),
            flags: 0, // read-only
            position: 0,
        };
        
        // stdout (fd 1)
        let stdout = FileDescriptor {
            fd: 1,
            file_type: FileType::Device(String::from("/dev/stdout")),
            flags: 1, // write-only
            position: 0,
        };
        
        // stderr (fd 2)
        let stderr = FileDescriptor {
            fd: 2,
            file_type: FileType::Device(String::from("/dev/stderr")),
            flags: 1, // write-only
            position: 0,
        };
        
        self.file_descriptors.insert(0, stdin);
        self.file_descriptors.insert(1, stdout);
        self.file_descriptors.insert(2, stderr);
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pcb_creation() {
        let pcb = ProcessControlBlock::new(1, None, String::from("test"), 0x400000);
        assert!(pcb.is_ok());
        
        let pcb = pcb.unwrap();
        assert_eq!(pcb.pid, 1);
        assert_eq!(pcb.state, ProcessState::Created);
        assert_eq!(pcb.file_descriptors.len(), 3); // stdin, stdout, stderr
    }

    #[test]
    fn test_file_descriptor_operations() {
        let mut pcb = ProcessControlBlock::new(1, None, String::from("test"), 0x400000).unwrap();
        
        let fd = pcb.open_file(String::from("/test.txt"), 0).unwrap();
        assert_eq!(fd, 3);
        
        assert!(pcb.get_file_descriptor(fd).is_some());
        assert!(pcb.close_file(fd).is_ok());
        assert!(pcb.get_file_descriptor(fd).is_none());
    }

    #[test]
    fn test_process_states() {
        let mut pcb = ProcessControlBlock::new(1, None, String::from("test"), 0x400000).unwrap();
        
        assert_eq!(pcb.state, ProcessState::Created);
        assert!(!pcb.is_schedulable());
        
        pcb.set_state(ProcessState::Ready);
        assert!(pcb.is_schedulable());
        
        pcb.terminate(0);
        assert_eq!(pcb.state, ProcessState::Zombie);
        assert_eq!(pcb.exit_code, Some(0));
    }
}

// Safety: ProcessControlBlock is designed for kernel-level process management
// and is only accessed through synchronized scheduler operations
unsafe impl Send for ProcessControlBlock {}
unsafe impl Sync for ProcessControlBlock {}
