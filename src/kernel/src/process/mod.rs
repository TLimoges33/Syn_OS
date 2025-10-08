//! Kernel Process Management
//!
//! Comprehensive process management system including scheduling,
//! context switching, lifecycle management, and thread support.

// Core process modules
pub mod scheduler;
pub mod context_switch;
pub mod pcb;
pub mod cpu;
pub mod current_process;

// Advanced scheduling
pub mod phase5_scheduler;
pub mod intelligent_scheduler;
pub mod o1_scheduler;
pub mod dynamic_priority;

// Process lifecycle
pub mod elf_loader;
pub mod user_memory;
pub mod advanced_manager;
pub mod real_process_manager;

// System integration
pub mod affinity;
pub mod migration;
pub mod monitoring;
pub mod debugging;
pub mod error_handling;

// Safety and security
pub mod safe_context_switch;
pub mod safe_globals;

// Phase 5 integration
pub mod phase5_mod;

use alloc::vec::Vec;
use core::arch::asm;
use core::sync::atomic::{AtomicU32, Ordering};

/// Process ID type
pub type ProcessId = u32;

/// Process states
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProcessState {
    Ready,
    Running,
    Blocked,
    Terminated,
}

/// Process priority levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Priority {
    Low = 0,
    Normal = 1,
    High = 2,
    Realtime = 3,
}

/// Process-related errors
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProcessError {
    ProcessNotFound,
    ProcessExists,
    ResourceExhausted,
    InsufficientPermissions,
    InvalidState,
    MemoryAllocationFailed,
}

/// CPU register state for context switching
#[derive(Debug, Clone, Copy)]
#[repr(C)]
pub struct CpuState {
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
    pub ds: u16,
    pub es: u16,
    pub fs: u16,
    pub gs: u16,
    pub ss: u16,
}

impl CpuState {
    /// Create a new CPU state with default values
    pub fn new() -> Self {
        CpuState {
            rax: 0,
            rbx: 0,
            rcx: 0,
            rdx: 0,
            rsi: 0,
            rdi: 0,
            rbp: 0,
            rsp: 0,
            r8: 0,
            r9: 0,
            r10: 0,
            r11: 0,
            r12: 0,
            r13: 0,
            r14: 0,
            r15: 0,
            rip: 0,
            rflags: 0x202, // Enable interrupts
            cs: 0x08,
            ds: 0x10,
            es: 0x10,
            fs: 0x10,
            gs: 0x10,
            ss: 0x10,
        }
    }

    /// Perform context switch between processes
    pub unsafe fn context_switch(current_state: *mut CpuState, next_state: *const CpuState) {
        // Save current context
        Self::save_context_asm(current_state);

        // Load next context
        Self::restore_context_asm(next_state);
    }

    /// Save current CPU state using inline assembly
    unsafe fn save_context_asm(state: *mut CpuState) {
        asm!(
            "mov [{state} + 0x00], rax",    // rax
            "mov [{state} + 0x08], rbx",    // rbx
            "mov [{state} + 0x10], rcx",    // rcx
            "mov [{state} + 0x18], rdx",    // rdx
            "mov [{state} + 0x20], rsi",    // rsi
            "mov [{state} + 0x28], rdi",    // rdi
            "mov [{state} + 0x30], rbp",    // rbp
            "mov [{state} + 0x38], rsp",    // rsp
            "mov [{state} + 0x40], r8",     // r8
            "mov [{state} + 0x48], r9",     // r9
            "mov [{state} + 0x50], r10",    // r10
            "mov [{state} + 0x58], r11",    // r11
            "mov [{state} + 0x60], r12",    // r12
            "mov [{state} + 0x68], r13",    // r13
            "mov [{state} + 0x70], r14",    // r14
            "mov [{state} + 0x78], r15",    // r15
            "pushfq",
            "pop rax",
            "mov [{state} + 0x88], rax",    // rflags
            state = in(reg) state,
            out("rax") _,
            options(nostack, preserves_flags)
        );
    }

    /// Restore CPU state using inline assembly
    unsafe fn restore_context_asm(state: *const CpuState) {
        asm!(
            "mov rax, [{state} + 0x88]",    // rflags
            "push rax",
            "popfq",
            "mov rax, [{state} + 0x00]",    // rax
            "mov rbx, [{state} + 0x08]",    // rbx
            "mov rcx, [{state} + 0x10]",    // rcx
            "mov rdx, [{state} + 0x18]",    // rdx
            "mov rsi, [{state} + 0x20]",    // rsi
            "mov rdi, [{state} + 0x28]",    // rdi
            "mov rbp, [{state} + 0x30]",    // rbp
            "mov rsp, [{state} + 0x38]",    // rsp
            "mov r8,  [{state} + 0x40]",    // r8
            "mov r9,  [{state} + 0x48]",    // r9
            "mov r10, [{state} + 0x50]",    // r10
            "mov r11, [{state} + 0x58]",    // r11
            "mov r12, [{state} + 0x60]",    // r12
            "mov r13, [{state} + 0x68]",    // r13
            "mov r14, [{state} + 0x70]",    // r14
            "mov r15, [{state} + 0x78]",    // r15
            state = in(reg) state,
            options(nostack)
        );
    }
}

/// Process Control Block (PCB)
#[derive(Clone)]
pub struct Process {
    pub id: ProcessId,
    pub state: ProcessState,
    pub priority: Priority,
    pub cpu_state: CpuState,
    pub memory_base: usize,
    pub memory_size: usize,
    pub parent_id: Option<ProcessId>,
    pub children: Vec<ProcessId>,
    pub exit_code: Option<i32>,
    pub cpu_time_used: u64,
    pub creation_time: u64,
}

impl Process {
    /// Create a new process
    pub fn new(id: ProcessId, entry_point: usize, stack_pointer: usize) -> Self {
        let mut cpu_state = CpuState::new();
        cpu_state.rip = entry_point as u64;
        cpu_state.rsp = stack_pointer as u64;

        Process {
            id,
            state: ProcessState::Ready,
            priority: Priority::Normal,
            cpu_state,
            memory_base: 0,
            memory_size: 0,
            parent_id: None,
            children: Vec::new(),
            exit_code: None,
            cpu_time_used: 0,
            creation_time: 0, // TODO: Use real timestamp
        }
    }

    /// Check if process is ready to run
    pub fn is_ready(&self) -> bool {
        matches!(self.state, ProcessState::Ready)
    }

    /// Check if process is running
    pub fn is_running(&self) -> bool {
        matches!(self.state, ProcessState::Running)
    }

    /// Check if process is terminated
    pub fn is_terminated(&self) -> bool {
        matches!(self.state, ProcessState::Terminated)
    }

    /// Set process state
    pub fn set_state(&mut self, state: ProcessState) {
        self.state = state;
    }

    /// Add a child process
    pub fn add_child(&mut self, child_id: ProcessId) {
        self.children.push(child_id);
    }

    /// Remove a child process
    pub fn remove_child(&mut self, child_id: ProcessId) {
        self.children.retain(|&id| id != child_id);
    }

    /// Get process PID
    pub fn pid(&self) -> ProcessId {
        self.id
    }

    /// Set process PID
    pub fn set_pid(&mut self, pid: ProcessId) {
        self.id = pid;
    }

    /// Set parent PID
    pub fn set_parent_pid(&mut self, parent_pid: ProcessId) {
        self.parent_id = Some(parent_pid);
    }

    /// Set exit code
    pub fn set_exit_code(&mut self, exit_code: i32) {
        self.exit_code = Some(exit_code);
    }

    /// Create a new kernel process (PID 1)
    pub fn new_kernel_process() -> Self {
        Process {
            id: 1,
            state: ProcessState::Running,
            priority: Priority::Realtime,
            cpu_state: CpuState::new(),
            memory_base: 0,
            memory_size: 0,
            parent_id: None,
            children: Vec::new(),
            exit_code: None,
            cpu_time_used: 0,
            creation_time: 0,
        }
    }

    /// Create a new idle process (PID 0)
    pub fn new_idle_process() -> Self {
        Process {
            id: 0,
            state: ProcessState::Ready,
            priority: Priority::Low,
            cpu_state: CpuState::new(),
            memory_base: 0,
            memory_size: 0,
            parent_id: None,
            children: Vec::new(),
            exit_code: None,
            cpu_time_used: 0,
            creation_time: 0,
        }
    }

    /// Create a new user process
    pub fn new_user_process(pid: ProcessId, parent_pid: ProcessId) -> Result<Self, ProcessError> {
        Ok(Process {
            id: pid,
            state: ProcessState::Ready,
            priority: Priority::Normal,
            cpu_state: CpuState::new(),
            memory_base: 0,
            memory_size: 0,
            parent_id: Some(parent_pid),
            children: Vec::new(),
            exit_code: None,
            cpu_time_used: 0,
            creation_time: 0,
        })
    }

    /// Terminate the process with an exit code
    pub fn terminate(&mut self, exit_code: i32) {
        self.state = ProcessState::Terminated;
        self.exit_code = Some(exit_code);
    }
}

/// Process manager for the kernel
pub struct ProcessManager {
    processes: Vec<Process>,
    current_process: Option<ProcessId>,
    next_pid: AtomicU32,
}

impl ProcessManager {
    /// Create a new process manager
    pub fn new() -> Self {
        ProcessManager {
            processes: Vec::new(),
            current_process: None,
            next_pid: AtomicU32::new(1), // PID 0 reserved for kernel
        }
    }

    /// Generate a new unique process ID
    fn next_pid(&self) -> ProcessId {
        self.next_pid.fetch_add(1, Ordering::SeqCst)
    }

    /// Create a new process
    pub fn create_process(&mut self, entry_point: usize, stack_pointer: usize) -> ProcessId {
        let pid = self.next_pid();
        let process = Process::new(pid, entry_point, stack_pointer);
        self.processes.push(process);
        pid
    }

    /// Get a process by ID
    pub fn get_process(&self, pid: ProcessId) -> Option<&Process> {
        self.processes.iter().find(|p| p.id == pid)
    }

    /// Get a mutable process by ID
    pub fn get_process_mut(&mut self, pid: ProcessId) -> Option<&mut Process> {
        self.processes.iter_mut().find(|p| p.id == pid)
    }

    /// Get the currently running process
    pub fn current_process(&self) -> Option<&Process> {
        if let Some(pid) = self.current_process {
            self.get_process(pid)
        } else {
            None
        }
    }

    /// Get the currently running process (mutable)
    pub fn current_process_mut(&mut self) -> Option<&mut Process> {
        if let Some(pid) = self.current_process {
            self.get_process_mut(pid)
        } else {
            None
        }
    }

    /// Set the current running process
    pub fn set_current_process(&mut self, pid: Option<ProcessId>) {
        // Update state of previous process
        if let Some(current_pid) = self.current_process {
            if let Some(process) = self.get_process_mut(current_pid) {
                if process.is_running() {
                    process.set_state(ProcessState::Ready);
                }
            }
        }

        // Set new current process
        self.current_process = pid;

        // Update state of new process
        if let Some(new_pid) = pid {
            if let Some(process) = self.get_process_mut(new_pid) {
                process.set_state(ProcessState::Running);
            }
        }
    }

    /// Get all ready processes
    pub fn ready_processes(&self) -> Vec<ProcessId> {
        self.processes
            .iter()
            .filter(|p| p.is_ready())
            .map(|p| p.id)
            .collect()
    }

    /// Terminate a process
    pub fn terminate_process(&mut self, pid: ProcessId, exit_code: i32) {
        if let Some(process) = self.get_process_mut(pid) {
            process.terminate(exit_code);

            // If this was the current process, clear it
            if self.current_process == Some(pid) {
                self.current_process = None;
            }
        }
    }

    /// Clean up terminated processes
    pub fn cleanup_terminated(&mut self) {
        self.processes.retain(|p| !p.is_terminated());
    }

    /// Get process count
    pub fn process_count(&self) -> usize {
        self.processes.len()
    }

    /// Get count of processes in each state
    pub fn state_counts(&self) -> (usize, usize, usize, usize) {
        let mut ready = 0;
        let mut running = 0;
        let mut blocked = 0;
        let mut terminated = 0;

        for process in &self.processes {
            match process.state {
                ProcessState::Ready => ready += 1,
                ProcessState::Running => running += 1,
                ProcessState::Blocked => blocked += 1,
                ProcessState::Terminated => terminated += 1,
            }
        }

        (ready, running, blocked, terminated)
    }
}

use spin::Mutex;

/// Global process manager instance (thread-safe)
static PROCESS_MANAGER: Mutex<Option<ProcessManager>> = Mutex::new(None);

/// Initialize the process manager
pub fn init() {
    *PROCESS_MANAGER.lock() = Some(ProcessManager::new());
}

/// Execute a closure with mutable access to the process manager
/// This is the safe way to access the global process manager
pub fn with_process_manager<F, R>(f: F) -> R
where
    F: FnOnce(&mut ProcessManager) -> R,
{
    let mut guard = PROCESS_MANAGER.lock();
    f(guard.as_mut().expect("Process manager not initialized"))
}

/// Get a reference to the process manager (for compatibility)
/// Note: This returns a Mutex guard, not a raw reference
pub fn process_manager() -> spin::MutexGuard<'static, Option<ProcessManager>> {
    PROCESS_MANAGER.lock()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_creation() {
        let mut pm = ProcessManager::new();
        let pid = pm.create_process(0x1000, 0x2000);
        assert_eq!(pid, 1);

        let process = pm.get_process(pid).unwrap();
        assert_eq!(process.id, pid);
        assert_eq!(process.state, ProcessState::Ready);
    }

    #[test]
    fn test_process_state_transition() {
        let mut process = Process::new(1, 0x1000, 0x2000);
        assert!(process.is_ready());

        process.set_state(ProcessState::Running);
        assert!(process.is_running());

        process.terminate(0);
        assert!(process.is_terminated());
        assert_eq!(process.exit_code, Some(0));
    }
}

// Re-export main types
pub use cpu::{CpuId, Cpu};

/// Initialize the process scheduler
pub fn init_scheduler() {
    // Initialize global scheduler
    // TODO: Implement scheduler initialization
}

/// Spawn a new process
pub fn spawn_process(program: &[u8]) -> Result<ProcessId, ProcessError> {
    // TODO: Implement process spawning from program binary
    Ok(1)
}

/// Get the current process ID
pub fn current_process_id() -> ProcessId {
    // TODO: Implement current process ID tracking
    0
}

/// Isolate a process in a sandbox
pub fn isolate_process(pid: ProcessId) -> Result<(), ProcessError> {
    // TODO: Implement process isolation
    Ok(())
}
