/// SynOS Phase 5 Process Management
/// Complete user space process management framework

// Use existing modules in the process directory
use super::elf_loader;
use super::user_memory;
use super::pcb;
use super::phase5_scheduler;
use super::context_switch;

// Re-export main types
pub use pcb::{ProcessControlBlock, ProcessId, ThreadId, Priority, ProcessState, ProcessError};
pub use elf_loader::{ElfLoader, ElfError, LoadedSegment};
pub use user_memory::{UserSpaceMemory, MemoryError, MemoryRegion, MemoryProtection};
pub use phase5_scheduler::{ProcessScheduler, SchedulerError, SchedulerStats, init_scheduler, create_process, schedule_process, get_next_process};

use alloc::string::String;
use alloc::vec::Vec;

/// Process manager - high-level interface for process operations
pub struct ProcessManager {
    initialized: bool,
}

impl ProcessManager {
    /// Create a new process manager
    pub fn new() -> Self {
        Self {
            initialized: false,
        }
    }

    /// Initialize the process management subsystem
    pub fn init(&mut self, num_cores: usize) -> Result<(), ProcessError> {
        if self.initialized {
            return Ok(());
        }

        // Initialize the scheduler
        init_scheduler(num_cores);
        self.initialized = true;

        Ok(())
    }

    /// Load and create a new process from ELF binary
    pub fn load_process(
        &mut self,
        name: String,
        elf_data: &[u8],
        args: Vec<String>,
        env: Vec<(String, String)>,
        parent_pid: Option<ProcessId>,
    ) -> Result<ProcessId, ProcessError> {
        if !self.initialized {
            return Err(ProcessError::InvalidState);
        }

        // Load ELF binary
        let mut elf_loader = ElfLoader::new();
        let elf_info = elf_loader.load_elf(elf_data)
            .map_err(|_| ProcessError::InvalidState)?;

        // Create process
        let pid = create_process(name.clone(), elf_info.entry_point, parent_pid)?;

        // Set up process memory and load segments
        {
            let mut scheduler_guard = ProcessScheduler::get();
            if let Some(ref mut scheduler) = *scheduler_guard {
                if let Some(process) = scheduler.get_process_mut(pid) {
                    // Set up process memory layout
                    process.setup_memory_layout(&elf_info.segments)?;

                    // Set command line arguments
                    process.command_line = args;

                    // Set environment variables
                    for (key, value) in env {
                        process.set_env(key, value);
                    }

                    // Set process name
                    process.name = name;
                }
            }
        }

        // Schedule the process
        schedule_process(pid).map_err(|_| ProcessError::InvalidState)?;

        Ok(pid)
    }

    /// Create a simple test process
    pub fn create_test_process(&mut self, name: String) -> Result<ProcessId, ProcessError> {
        if !self.initialized {
            return Err(ProcessError::InvalidState);
        }

        // Create a minimal process for testing
        let pid = create_process(name, 0x400000, None)?;
        schedule_process(pid).map_err(|_| ProcessError::InvalidState)?;

        Ok(pid)
    }

    /// Get process information
    pub fn get_process_info(&self, pid: ProcessId) -> Option<ProcessInfo> {
        let scheduler_guard = ProcessScheduler::get();
        if let Some(ref scheduler) = *scheduler_guard {
            if let Some(process) = scheduler.get_process(pid) {
                return Some(ProcessInfo {
                    pid: process.pid,
                    parent_pid: process.parent_pid,
                    name: process.name.clone(),
                    state: process.state,
                    priority: process.priority,
                    memory_usage: process.get_memory_usage(),
                    cpu_time_user: process.stats.cpu_time_user,
                    cpu_time_kernel: process.stats.cpu_time_kernel,
                });
            }
        }
        None
    }

    /// List all processes
    pub fn list_processes(&self) -> Vec<ProcessInfo> {
        let mut processes = Vec::new();
        let scheduler_guard = ProcessScheduler::get();

        if let Some(ref scheduler) = *scheduler_guard {
            let stats = scheduler.get_stats();
            // For now, just return basic stats info
            // In a full implementation, we'd iterate through all processes
        }

        processes
    }

    /// Terminate a process
    pub fn terminate_process(&mut self, pid: ProcessId, exit_code: i32) -> Result<(), ProcessError> {
        let mut scheduler_guard = ProcessScheduler::get();
        if let Some(ref mut scheduler) = *scheduler_guard {
            if let Some(process) = scheduler.get_process_mut(pid) {
                process.terminate(exit_code);
                return Ok(());
            }
        }
        Err(ProcessError::ProcessNotFound)
    }

    /// Get scheduler statistics
    pub fn get_scheduler_stats(&self) -> Option<SchedulerStats> {
        let scheduler_guard = ProcessScheduler::get();
        if let Some(ref scheduler) = *scheduler_guard {
            Some(scheduler.get_stats().clone())
        } else {
            None
        }
    }
}

/// Process information structure
#[derive(Debug, Clone)]
pub struct ProcessInfo {
    pub pid: ProcessId,
    pub parent_pid: Option<ProcessId>,
    pub name: String,
    pub state: ProcessState,
    pub priority: Priority,
    pub memory_usage: u64,
    pub cpu_time_user: u64,
    pub cpu_time_kernel: u64,
}

/// Global process manager instance
static mut PROCESS_MANAGER: Option<ProcessManager> = None;

/// Initialize global process manager
pub fn init_process_manager(num_cores: usize) -> Result<(), ProcessError> {
    unsafe {
        if (*(&raw const PROCESS_MANAGER)).is_none() {
            let mut manager = ProcessManager::new();
            manager.init(num_cores)?;
            PROCESS_MANAGER = Some(manager);
        }
    }
    Ok(())
}

/// Get reference to global process manager
pub fn get_process_manager() -> Option<&'static mut ProcessManager> {
    unsafe { (*(&raw mut PROCESS_MANAGER)).as_mut() }
}

/// High-level process creation function
pub fn spawn_process(
    name: String,
    elf_data: &[u8],
    args: Vec<String>,
    env: Vec<(String, String)>,
) -> Result<ProcessId, ProcessError> {
    if let Some(manager) = get_process_manager() {
        manager.load_process(name, elf_data, args, env, None)
    } else {
        Err(ProcessError::InvalidState)
    }
}

/// Create test process (for debugging/testing)
pub fn spawn_test_process(name: String) -> Result<ProcessId, ProcessError> {
    if let Some(manager) = get_process_manager() {
        manager.create_test_process(name)
    } else {
        Err(ProcessError::InvalidState)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_manager_creation() {
        let manager = ProcessManager::new();
        assert!(!manager.initialized);
    }

    #[test]
    fn test_process_manager_init() {
        let mut manager = ProcessManager::new();
        assert!(manager.init(4).is_ok());
        assert!(manager.initialized);
    }
}
