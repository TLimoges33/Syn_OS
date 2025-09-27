/*
 * SynOS Current Process Tracking
 * Maintains the current executing process context
 */

use crate::process::{ProcessId, Process, ProcessError};
use crate::memory::virtual_memory::PageTable;
use spin::{Mutex, MutexGuard};
use alloc::collections::BTreeMap;
use core::sync::atomic::{AtomicU32, Ordering};

// Global current process state
static CURRENT_PID: AtomicU32 = AtomicU32::new(1);
static PROCESS_TABLE: Mutex<ProcessTable> = Mutex::new(ProcessTable::new());

/// Process table that tracks all active processes
pub struct ProcessTable {
    processes: BTreeMap<ProcessId, Process>,
    next_pid: ProcessId,
}

impl ProcessTable {
    const fn new() -> Self {
        Self {
            processes: BTreeMap::new(),
            next_pid: 1,
        }
    }

    /// Allocate a new process ID
    pub fn allocate_pid(&mut self) -> ProcessId {
        let pid = self.next_pid;
        self.next_pid += 1;
        pid
    }

    /// Add a process to the table
    pub fn add_process(&mut self, process: Process) -> Result<(), ProcessError> {
        let pid = process.pid();
        if self.processes.contains_key(&pid) {
            return Err(ProcessError::ProcessExists);
        }
        self.processes.insert(pid, process);
        Ok(())
    }

    /// Get a process by PID
    pub fn get_process(&self, pid: ProcessId) -> Option<&Process> {
        self.processes.get(&pid)
    }

    /// Get a mutable process by PID
    pub fn get_process_mut(&mut self, pid: ProcessId) -> Option<&mut Process> {
        self.processes.get_mut(&pid)
    }

    /// Remove a process from the table
    pub fn remove_process(&mut self, pid: ProcessId) -> Option<Process> {
        self.processes.remove(&pid)
    }

    /// Get all process IDs
    pub fn all_pids(&self) -> alloc::vec::Vec<ProcessId> {
        self.processes.keys().copied().collect()
    }
}

/// Get the current process ID
pub fn get_current_pid() -> ProcessId {
    CURRENT_PID.load(Ordering::SeqCst)
}

/// Set the current process ID (used during context switch)
pub fn set_current_pid(pid: ProcessId) {
    CURRENT_PID.store(pid, Ordering::SeqCst);
}

/// Get the current process
pub fn get_current_process() -> Result<ProcessId, ProcessError> {
    let pid = get_current_pid();
    let table = PROCESS_TABLE.lock();

    if table.get_process(pid).is_some() {
        Ok(pid)
    } else {
        Err(ProcessError::ProcessNotFound)
    }
}

/// Get a lock on the process table
pub fn get_process_table() -> MutexGuard<'static, ProcessTable> {
    PROCESS_TABLE.lock()
}

/// Initialize the process tracking system
pub fn init_process_tracking() {
    // Create the initial kernel process (PID 1)
    let kernel_process = Process::new_kernel_process();
    let mut table = PROCESS_TABLE.lock();

    if let Err(e) = table.add_process(kernel_process) {
        panic!("Failed to initialize kernel process: {:?}", e);
    }

    set_current_pid(1);

    // Initialize idle process (PID 0) if needed
    let idle_process = Process::new_idle_process();
    if let Err(e) = table.add_process(idle_process) {
        panic!("Failed to initialize idle process: {:?}", e);
    }
}

/// Create a new process and add it to the table
pub fn create_process(parent_pid: ProcessId) -> Result<ProcessId, ProcessError> {
    let mut table = get_process_table();

    // Verify parent exists
    if table.get_process(parent_pid).is_none() {
        return Err(ProcessError::ProcessNotFound);
    }

    let pid = table.allocate_pid();
    let process = Process::new_user_process(pid, parent_pid)?;

    table.add_process(process)?;
    Ok(pid)
}

/// Fork the current process
pub fn fork_current_process() -> Result<ProcessId, ProcessError> {
    let current_pid = get_current_pid();
    let mut table = get_process_table();

    // Get the current process
    let current_process = table.get_process(current_pid)
        .ok_or(ProcessError::ProcessNotFound)?
        .clone();

    // Allocate new PID
    let child_pid = table.allocate_pid();

    // Create child process as copy of parent
    let mut child_process = current_process;
    child_process.set_pid(child_pid);
    child_process.set_parent_pid(current_pid);

    // Add child to table
    table.add_process(child_process)?;

    Ok(child_pid)
}

/// Exit the current process
pub fn exit_current_process(exit_code: i32) -> Result<(), ProcessError> {
    let current_pid = get_current_pid();
    let mut table = get_process_table();

    // Remove from process table
    if let Some(mut process) = table.remove_process(current_pid) {
        process.set_exit_code(exit_code);

        // TODO: Notify parent process
        // TODO: Clean up resources
        // TODO: Schedule next process

        Ok(())
    } else {
        Err(ProcessError::ProcessNotFound)
    }
}

/// Wait for a child process to exit
pub fn wait_for_child(child_pid: Option<ProcessId>) -> Result<(ProcessId, i32), ProcessError> {
    let current_pid = get_current_pid();
    let table = get_process_table();

    // For now, return a simulated result
    // TODO: Implement proper process waiting with blocking
    match child_pid {
        Some(pid) => {
            if table.get_process(pid).is_some() {
                Ok((pid, 0)) // Simulated successful exit
            } else {
                Err(ProcessError::ProcessNotFound)
            }
        }
        None => {
            // Wait for any child
            Ok((current_pid + 1, 0)) // Simulated result
        }
    }
}

/// Get process statistics
pub fn get_process_stats() -> (usize, ProcessId) {
    let table = get_process_table();
    (table.processes.len(), table.next_pid)
}