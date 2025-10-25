//! Complete Process Lifecycle Management
//!
//! Provides comprehensive process management including:
//! - Process creation, execution, and termination
//! - Process hierarchy (parent-child relationships)
//! - Process state transitions
//! - Resource management and cleanup
//! - Signal handling
//! - IPC integration

use alloc::collections::BTreeMap;
use alloc::string::String;
use alloc::vec::Vec;
use alloc::sync::Arc;
use core::sync::atomic::{AtomicU32, AtomicU64, Ordering};
use spin::{Mutex, RwLock};

// Import from process module without circular dependency
// pub use crate::process::{ProcessId, ProcessState, Priority, ProcessError, CpuState};
// use crate::process::pcb::ProcessControlBlock;
// use crate::process::scheduler::ProcessScheduler;
use crate::ipc::IPCId;
// use crate::memory::VirtualAddress;

/// Virtual address type for our kernel
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct VirtualAddress(pub u64);

impl VirtualAddress {
    pub fn new(addr: u64) -> Self {
        Self(addr)
    }
}

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
    NoChildAvailable,
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
            rflags: 0,
            cs: 0,
            ds: 0,
            es: 0,
            fs: 0,
            gs: 0,
            ss: 0,
        }
    }
}

/// Simple process scheduler
pub struct ProcessScheduler {
    ready_queue: Vec<ProcessId>,
    current_index: usize,
}

impl ProcessScheduler {
    pub fn new() -> Self {
        Self {
            ready_queue: Vec::new(),
            current_index: 0,
        }
    }

    pub fn add_process(&mut self, pid: ProcessId) {
        self.ready_queue.push(pid);
    }

    pub fn remove_process(&mut self, pid: ProcessId) {
        self.ready_queue.retain(|&p| p != pid);
    }

    pub fn next_process(&mut self) -> Option<ProcessId> {
        if self.ready_queue.is_empty() {
            return None;
        }

        let pid = self.ready_queue[self.current_index];
        self.current_index = (self.current_index + 1) % self.ready_queue.len();
        Some(pid)
    }
}

/// Global process manager instance
pub static PROCESS_MANAGER: RwLock<Option<ProcessManager>> = RwLock::new(None);

/// Next available process ID
static NEXT_PID: AtomicU32 = AtomicU32::new(1);

/// Signal types
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
#[repr(u8)]
pub enum Signal {
    SIGHUP = 1,
    SIGINT = 2,
    SIGQUIT = 3,
    SIGILL = 4,
    SIGTRAP = 5,
    SIGABRT = 6,
    SIGBUS = 7,
    SIGFPE = 8,
    SIGKILL = 9,
    SIGUSR1 = 10,
    SIGSEGV = 11,
    SIGUSR2 = 12,
    SIGPIPE = 13,
    SIGALRM = 14,
    SIGTERM = 15,
    SIGCHLD = 17,
    SIGCONT = 18,
    SIGSTOP = 19,
    SIGTSTP = 20,
    SIGTTIN = 21,
    SIGTTOU = 22,
}

/// Process creation flags
#[derive(Debug, Clone, Copy)]
pub struct ProcessFlags {
    pub detached: bool,
    pub inherit_handles: bool,
    pub new_session: bool,
    pub suspended: bool,
}

impl Default for ProcessFlags {
    fn default() -> Self {
        Self {
            detached: false,
            inherit_handles: true,
            new_session: false,
            suspended: false,
        }
    }
}

/// Process statistics
#[derive(Debug, Default, Clone)]
pub struct ProcessStats {
    pub cpu_time: u64,
    pub memory_usage: usize,
    pub page_faults: u64,
    pub context_switches: u64,
    pub ipc_operations: u64,
    pub signals_received: u64,
    pub children_spawned: u64,
}

/// Extended Process Control Block
pub struct Process {
    pub pid: ProcessId,
    pub parent_pid: Option<ProcessId>,
    pub children: Vec<ProcessId>,
    pub state: ProcessState,
    pub priority: Priority,
    pub cpu_state: CpuState,
    pub name: String,
    pub command_line: Vec<String>,
    pub environment: BTreeMap<String, String>,
    pub working_directory: String,
    pub user_id: u32,
    pub group_id: u32,
    pub session_id: u32,
    pub process_group_id: u32,
    pub stats: ProcessStats,
    pub signal_mask: u64,
    pub pending_signals: Vec<Signal>,
    pub signal_handlers: BTreeMap<Signal, SignalHandler>,
    pub exit_code: Option<i32>,
    pub created_at: u64,
    pub started_at: Option<u64>,
    pub terminated_at: Option<u64>,
    pub ipc_resources: Vec<IPCId>,
    pub open_files: Vec<FileHandle>,
    pub memory_map: MemoryMap,
    pub thread_count: u32,
    pub flags: ProcessFlags,
}

/// Signal handler type
#[derive(Debug, Clone)]
pub enum SignalHandler {
    Default,
    Ignore,
    Custom(VirtualAddress),
}

/// File handle for process
#[derive(Debug, Clone)]
pub struct FileHandle {
    pub fd: u32,
    pub path: String,
    pub flags: u32,
    pub offset: u64,
}

/// Process memory map
#[derive(Debug, Clone)]
pub struct MemoryMap {
    pub code_base: VirtualAddress,
    pub code_size: usize,
    pub data_base: VirtualAddress,
    pub data_size: usize,
    pub heap_base: VirtualAddress,
    pub heap_size: usize,
    pub stack_base: VirtualAddress,
    pub stack_size: usize,
    pub shared_segments: Vec<(VirtualAddress, usize)>,
}

impl Process {
    /// Create a new process
    pub fn new(name: String, parent_pid: Option<ProcessId>) -> Self {
        let pid = NEXT_PID.fetch_add(1, Ordering::SeqCst);

        Self {
            pid,
            parent_pid,
            children: Vec::new(),
            state: ProcessState::Ready,
            priority: Priority::Normal,
            cpu_state: CpuState::new(),
            name,
            command_line: Vec::new(),
            environment: BTreeMap::new(),
            working_directory: String::from("/"),
            user_id: 0,
            group_id: 0,
            session_id: pid,
            process_group_id: pid,
            stats: ProcessStats::default(),
            signal_mask: 0,
            pending_signals: Vec::new(),
            signal_handlers: BTreeMap::new(),
            exit_code: None,
            created_at: get_system_time(),
            started_at: None,
            terminated_at: None,
            ipc_resources: Vec::new(),
            open_files: Vec::new(),
            memory_map: MemoryMap::default(),
            thread_count: 1,
            flags: ProcessFlags::default(),
        }
    }

    /// Fork a child process
    pub fn fork(&self) -> Result<Process, ProcessError> {
        let mut child = Self::new(self.name.clone(), Some(self.pid));

        // Copy parent's attributes
        child.priority = self.priority;
        child.environment = self.environment.clone();
        child.working_directory = self.working_directory.clone();
        child.user_id = self.user_id;
        child.group_id = self.group_id;
        child.session_id = self.session_id;
        child.process_group_id = self.process_group_id;
        child.signal_mask = self.signal_mask;

        // Copy signal handlers
        child.signal_handlers = self.signal_handlers.clone();

        // Inherit open files if specified
        if self.flags.inherit_handles {
            child.open_files = self.open_files.clone();
        }

        Ok(child)
    }

    /// Execute a new program
    pub fn exec(&mut self, program: &str, args: Vec<String>, env: BTreeMap<String, String>) -> Result<(), ProcessError> {
        // Clear current process state
        self.name = String::from(program);
        self.command_line = args;
        self.environment = env;

        // Reset signal handlers to default
        self.signal_handlers.clear();

        // Clear IPC resources
        self.ipc_resources.clear();

        // Load new program (would involve ELF loading in real implementation)
        // This is simplified for demonstration
        self.memory_map = MemoryMap::default();
        self.cpu_state = CpuState::new();

        self.started_at = Some(get_system_time());
        self.state = ProcessState::Ready;

        Ok(())
    }

    /// Send a signal to this process
    pub fn send_signal(&mut self, signal: Signal) -> Result<(), ProcessError> {
        // Check if signal is blocked
        if (self.signal_mask & (1 << signal as u64)) != 0 {
            return Ok(());
        }

        // Handle special signals immediately
        match signal {
            Signal::SIGKILL => {
                self.terminate(128 + signal as i32);
                return Ok(());
            }
            Signal::SIGSTOP => {
                self.state = ProcessState::Blocked;
                return Ok(());
            }
            Signal::SIGCONT => {
                if self.state == ProcessState::Blocked {
                    self.state = ProcessState::Ready;
                }
                return Ok(());
            }
            _ => {}
        }

        // Queue signal for handling
        self.pending_signals.push(signal);
        self.stats.signals_received += 1;

        Ok(())
    }

    /// Handle pending signals
    pub fn handle_signals(&mut self) -> Result<(), ProcessError> {
        while let Some(signal) = self.pending_signals.pop() {
            let handler = self.signal_handlers.get(&signal)
                .unwrap_or(&SignalHandler::Default);

            match handler {
                SignalHandler::Default => self.handle_default_signal(signal)?,
                SignalHandler::Ignore => {},
                SignalHandler::Custom(addr) => {
                    // Would invoke custom signal handler at given address
                    // This requires context switching to user mode
                }
            }
        }

        Ok(())
    }

    /// Handle default signal behavior
    fn handle_default_signal(&mut self, signal: Signal) -> Result<(), ProcessError> {
        match signal {
            Signal::SIGTERM | Signal::SIGINT | Signal::SIGQUIT => {
                self.terminate(128 + signal as i32);
            }
            Signal::SIGCHLD => {
                // Reap zombie children
                self.reap_children();
            }
            _ => {}
        }

        Ok(())
    }

    /// Terminate the process
    pub fn terminate(&mut self, exit_code: i32) {
        self.state = ProcessState::Terminated;
        self.exit_code = Some(exit_code);
        self.terminated_at = Some(get_system_time());

        // Release all resources
        self.cleanup_resources();
    }

    /// Clean up process resources
    fn cleanup_resources(&mut self) {
        // Close all open files
        self.open_files.clear();

        // Release IPC resources
        self.ipc_resources.clear();

        // Free memory (would involve actual memory deallocation)
        self.memory_map = MemoryMap::default();
    }

    /// Reap zombie child processes
    fn reap_children(&mut self) {
        self.children.retain(|&child_pid| {
            // Check if child is zombie and clean it up
            // This would interact with the process manager
            true
        });
    }

    /// Wait for child process to terminate
    pub fn wait_for_child(&mut self, child_pid: Option<ProcessId>) -> Result<(ProcessId, i32), ProcessError> {
        if self.children.is_empty() {
            return Err(ProcessError::ProcessNotFound);
        }

        // Block until a child terminates
        self.state = ProcessState::Blocked;

        // This would be implemented with proper blocking/waking mechanism
        // For now, return a placeholder
        Ok((0, 0))
    }
}

impl Default for MemoryMap {
    fn default() -> Self {
        Self {
            code_base: VirtualAddress::new(0x400000),
            code_size: 0,
            data_base: VirtualAddress::new(0x600000),
            data_size: 0,
            heap_base: VirtualAddress::new(0x800000),
            heap_size: 0,
            stack_base: VirtualAddress::new(0x7fff0000),
            stack_size: 0x10000,
            shared_segments: Vec::new(),
        }
    }
}

/// Process Manager
pub struct ProcessManager {
    processes: BTreeMap<ProcessId, Arc<Mutex<Process>>>,
    scheduler: ProcessScheduler,
    current_process: Option<ProcessId>,
    zombie_processes: Vec<ProcessId>,
    process_groups: BTreeMap<u32, Vec<ProcessId>>,
    sessions: BTreeMap<u32, Vec<ProcessId>>,
}

impl ProcessManager {
    /// Create a new process manager
    pub fn new() -> Self {
        Self {
            processes: BTreeMap::new(),
            scheduler: ProcessScheduler::new(),
            current_process: None,
            zombie_processes: Vec::new(),
            process_groups: BTreeMap::new(),
            sessions: BTreeMap::new(),
        }
    }

    /// Initialize the process manager with init process
    pub fn init(&mut self) -> Result<(), ProcessError> {
        // Create init process (PID 1)
        let init = Process::new(String::from("init"), None);
        let init_pid = init.pid;

        self.processes.insert(init_pid, Arc::new(Mutex::new(init)));
        self.current_process = Some(init_pid);

        Ok(())
    }

    /// Create a new process
    pub fn create_process(&mut self, name: String, flags: ProcessFlags) -> Result<ProcessId, ProcessError> {
        let parent_pid = self.current_process;
        let mut process = Process::new(name, parent_pid);
        process.flags = flags;

        let pid = process.pid;

        // Add to parent's children list
        if let Some(parent_pid) = parent_pid {
            if let Some(parent) = self.processes.get(&parent_pid) {
                parent.lock().children.push(pid);
            }
        }

        // Add to process table
        self.processes.insert(pid, Arc::new(Mutex::new(process)));

        // Add to scheduler
        self.scheduler.add_process(pid);

        Ok(pid)
    }

    /// Fork current process
    pub fn fork(&mut self) -> Result<ProcessId, ProcessError> {
        let current_pid = self.current_process.ok_or(ProcessError::ProcessNotFound)?;
        let current = self.processes.get(&current_pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        let child = current.lock().fork()?;
        let child_pid = child.pid;

        // Add child to parent's children list
        current.lock().children.push(child_pid);

        // Add to process table
        self.processes.insert(child_pid, Arc::new(Mutex::new(child)));

        // Add to scheduler
        self.scheduler.add_process(child_pid);

        Ok(child_pid)
    }

    /// Execute program in current process
    pub fn exec(&mut self, program: &str, args: Vec<String>, env: BTreeMap<String, String>) -> Result<(), ProcessError> {
        let current_pid = self.current_process.ok_or(ProcessError::ProcessNotFound)?;
        let current = self.processes.get(&current_pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        current.lock().exec(program, args, env)
    }

    /// Terminate a process
    pub fn terminate_process(&mut self, pid: ProcessId, exit_code: i32) -> Result<(), ProcessError> {
        let process = self.processes.get(&pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        process.lock().terminate(exit_code);

        // Move to zombie list
        self.zombie_processes.push(pid);

        // Remove from scheduler
        self.scheduler.remove_process(pid);

        // Send SIGCHLD to parent
        if let Some(parent_pid) = process.lock().parent_pid {
            if let Some(parent) = self.processes.get(&parent_pid) {
                parent.lock().send_signal(Signal::SIGCHLD)?;
            }
        }

        Ok(())
    }

    /// Send signal to process
    pub fn send_signal(&mut self, pid: ProcessId, signal: Signal) -> Result<(), ProcessError> {
        let process = self.processes.get(&pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        process.lock().send_signal(signal)
    }

    /// Send signal to process group
    pub fn send_signal_to_group(&mut self, pgid: u32, signal: Signal) -> Result<(), ProcessError> {
        if let Some(pids) = self.process_groups.get(&pgid) {
            for &pid in pids {
                if let Some(process) = self.processes.get(&pid) {
                    process.lock().send_signal(signal)?;
                }
            }
        }

        Ok(())
    }

    /// Wait for child process
    pub fn wait_for_child(&mut self, child_pid: Option<ProcessId>) -> Result<(ProcessId, i32), ProcessError> {
        let current_pid = self.current_process.ok_or(ProcessError::ProcessNotFound)?;
        let current = self.processes.get(&current_pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        current.lock().wait_for_child(child_pid)
    }

    /// Reap zombie processes
    pub fn reap_zombies(&mut self) {
        self.zombie_processes.retain(|&pid| {
            if let Some(process) = self.processes.get(&pid) {
                let proc = process.lock();
                if proc.parent_pid.is_none() || proc.state != ProcessState::Terminated {
                    return true;
                }
            }

            // Remove from process table
            self.processes.remove(&pid);
            false
        });
    }

    /// Get process by PID
    pub fn get_process(&self, pid: ProcessId) -> Option<Arc<Mutex<Process>>> {
        self.processes.get(&pid).cloned()
    }

    /// Get current process
    pub fn current_process(&self) -> Option<Arc<Mutex<Process>>> {
        self.current_process.and_then(|pid| self.get_process(pid))
    }

    /// Schedule next process
    pub fn schedule(&mut self) -> Option<ProcessId> {
        // Handle signals for current process
        if let Some(current) = self.current_process() {
            current.lock().handle_signals().ok();
        }

        // Get next process from scheduler
        let next_pid = self.scheduler.next_process()?;

        // Update current process
        self.current_process = Some(next_pid);

        Some(next_pid)
    }

    /// Create new session
    pub fn create_session(&mut self, pid: ProcessId) -> Result<u32, ProcessError> {
        let process = self.processes.get(&pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        let mut proc = process.lock();

        // Process becomes session leader
        proc.session_id = pid;
        proc.process_group_id = pid;

        // Update session table
        self.sessions.entry(pid).or_insert_with(Vec::new).push(pid);
        self.process_groups.entry(pid).or_insert_with(Vec::new).push(pid);

        Ok(pid)
    }

    /// Set process group
    pub fn set_process_group(&mut self, pid: ProcessId, pgid: u32) -> Result<(), ProcessError> {
        let process = self.processes.get(&pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        let mut proc = process.lock();
        let old_pgid = proc.process_group_id;
        proc.process_group_id = pgid;

        // Update process group table
        if let Some(old_group) = self.process_groups.get_mut(&old_pgid) {
            old_group.retain(|&p| p != pid);
        }

        self.process_groups.entry(pgid).or_insert_with(Vec::new).push(pid);

        Ok(())
    }

    /// Get process statistics
    pub fn get_process_stats(&self, pid: ProcessId) -> Result<ProcessStats, ProcessError> {
        let process = self.processes.get(&pid)
            .ok_or(ProcessError::ProcessNotFound)?;

        Ok(process.lock().stats.clone())
    }

    /// List all processes
    pub fn list_processes(&self) -> Vec<ProcessId> {
        self.processes.keys().copied().collect()
    }

    /// Get process tree
    pub fn get_process_tree(&self) -> BTreeMap<ProcessId, Vec<ProcessId>> {
        let mut tree = BTreeMap::new();

        for (&pid, process) in &self.processes {
            let children = process.lock().children.clone();
            tree.insert(pid, children);
        }

        tree
    }
}

/// Get current system time (placeholder)
fn get_system_time() -> u64 {
    // This would interface with the system timer
    0
}

/// Initialize process management subsystem
pub fn init() -> Result<(), ProcessError> {
    let mut manager = ProcessManager::new();
    manager.init()?;

    *PROCESS_MANAGER.write() = Some(manager);

    Ok(())
}

/// Fork current process
pub fn fork() -> Result<ProcessId, ProcessError> {
    PROCESS_MANAGER.write()
        .as_mut()
        .ok_or(ProcessError::ProcessNotFound)?
        .fork()
}

/// Execute program
pub fn exec(program: &str, args: Vec<String>, env: BTreeMap<String, String>) -> Result<(), ProcessError> {
    PROCESS_MANAGER.write()
        .as_mut()
        .ok_or(ProcessError::ProcessNotFound)?
        .exec(program, args, env)
}

/// Terminate current process
pub fn exit(exit_code: i32) -> ! {
    if let Some(manager) = PROCESS_MANAGER.write().as_mut() {
        if let Some(current_pid) = manager.current_process {
            manager.terminate_process(current_pid, exit_code).ok();
        }
    }

    // Halt the CPU
    loop {
        unsafe {
            core::arch::asm!("hlt");
        }
    }
}

/// Send signal to process
pub fn kill(pid: ProcessId, signal: Signal) -> Result<(), ProcessError> {
    PROCESS_MANAGER.write()
        .as_mut()
        .ok_or(ProcessError::ProcessNotFound)?
        .send_signal(pid, signal)
}

/// Wait for child process
pub fn wait(child_pid: Option<ProcessId>) -> Result<(ProcessId, i32), ProcessError> {
    PROCESS_MANAGER.write()
        .as_mut()
        .ok_or(ProcessError::ProcessNotFound)?
        .wait_for_child(child_pid)
}