/// Process Scheduler for SynOS Phase 5
/// Implements multilevel feedback queue scheduling

use alloc::collections::{BTreeMap, VecDeque};
use alloc::vec::Vec;
use spin::{Mutex, MutexGuard};
use crate::process::pcb::{ProcessControlBlock, ProcessId, ProcessState, Priority, ProcessError};

/// Scheduling quantum in microseconds for each priority level
const SCHEDULING_QUANTA: [u64; 5] = [
    50000,  // Idle: 50ms
    20000,  // Low: 20ms  
    10000,  // Normal: 10ms
    5000,   // High: 5ms
    1000,   // RealTime: 1ms
];

/// Maximum time a process can stay at high priority before demotion
const MAX_HIGH_PRIORITY_TIME: u64 = 100000; // 100ms

/// Process scheduler queue entry
#[derive(Debug, Clone)]
struct SchedulerEntry {
    pid: ProcessId,
    time_at_priority: u64,
    last_scheduled: u64,
}

/// Ready queues for different priority levels
#[derive(Debug)]
struct ReadyQueues {
    idle: VecDeque<SchedulerEntry>,
    low: VecDeque<SchedulerEntry>,
    normal: VecDeque<SchedulerEntry>,
    high: VecDeque<SchedulerEntry>,
    realtime: VecDeque<SchedulerEntry>,
}

impl ReadyQueues {
    fn new() -> Self {
        Self {
            idle: VecDeque::new(),
            low: VecDeque::new(),
            normal: VecDeque::new(),
            high: VecDeque::new(),
            realtime: VecDeque::new(),
        }
    }

    fn get_queue_mut(&mut self, priority: Priority) -> &mut VecDeque<SchedulerEntry> {
        match priority {
            Priority::Idle => &mut self.idle,
            Priority::Low => &mut self.low,
            Priority::Normal => &mut self.normal,
            Priority::High => &mut self.high,
            Priority::RealTime => &mut self.realtime,
        }
    }

    fn get_queue(&self, priority: Priority) -> &VecDeque<SchedulerEntry> {
        match priority {
            Priority::Idle => &self.idle,
            Priority::Low => &self.low,
            Priority::Normal => &self.normal,
            Priority::High => &self.high,
            Priority::RealTime => &self.realtime,
        }
    }

    fn total_processes(&self) -> usize {
        self.idle.len() + self.low.len() + self.normal.len() + 
        self.high.len() + self.realtime.len()
    }
}

/// CPU core scheduler state
#[derive(Debug)]
struct CoreScheduler {
    core_id: usize,
    current_process: Option<ProcessId>,
    ready_queues: ReadyQueues,
    idle_time: u64,
    total_context_switches: u64,
}

impl CoreScheduler {
    fn new(core_id: usize) -> Self {
        Self {
            core_id,
            current_process: None,
            ready_queues: ReadyQueues::new(),
            idle_time: 0,
            total_context_switches: 0,
        }
    }
}

/// Global process scheduler
pub struct ProcessScheduler {
    processes: BTreeMap<ProcessId, ProcessControlBlock>,
    cores: Vec<CoreScheduler>,
    next_pid: ProcessId,
    load_balancer_counter: usize,
    scheduler_stats: SchedulerStats,
}

/// Scheduling statistics
#[derive(Debug, Clone)]
pub struct SchedulerStats {
    pub total_processes: usize,
    pub running_processes: usize,
    pub ready_processes: usize,
    pub blocked_processes: usize,
    pub zombie_processes: usize,
    pub total_context_switches: u64,
    pub average_load: f32,
}

/// Scheduler errors
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SchedulerError {
    ProcessNotFound,
    InvalidCoreId,
    NoProcessToSchedule,
    ProcessAlreadyExists,
    SchedulingError,
}

/// Global process scheduler instance
static SCHEDULER: Mutex<Option<ProcessScheduler>> = Mutex::new(None);

// Safety: ProcessScheduler is only accessed through the global SCHEDULER mutex
// which provides the necessary synchronization for kernel-level operations
unsafe impl Send for ProcessScheduler {}
unsafe impl Sync for ProcessScheduler {}

impl ProcessScheduler {
    /// Initialize the global scheduler
    pub fn init(num_cores: usize) {
        let scheduler = ProcessScheduler::new(num_cores);
        *SCHEDULER.lock() = Some(scheduler);
    }

    /// Get reference to global scheduler
    pub fn get() -> MutexGuard<'static, Option<ProcessScheduler>> {
        SCHEDULER.lock()
    }

    /// Create a new process scheduler
    fn new(num_cores: usize) -> Self {
        let mut cores = Vec::with_capacity(num_cores);
        for i in 0..num_cores {
            cores.push(CoreScheduler::new(i));
        }

        Self {
            processes: BTreeMap::new(),
            cores,
            next_pid: 1,
            load_balancer_counter: 0,
            scheduler_stats: SchedulerStats {
                total_processes: 0,
                running_processes: 0,
                ready_processes: 0,
                blocked_processes: 0,
                zombie_processes: 0,
                total_context_switches: 0,
                average_load: 0.0,
            },
        }
    }

    /// Create a new process
    pub fn create_process(
        &mut self,
        name: alloc::string::String,
        entry_point: u64,
        parent_pid: Option<ProcessId>,
    ) -> Result<ProcessId, ProcessError> {
        let pid = self.next_pid;
        self.next_pid += 1;

        let pcb = ProcessControlBlock::new(pid, parent_pid, name, entry_point)?;
        
        // Add to parent's children list if parent exists
        if let Some(parent_id) = parent_pid {
            if let Some(parent) = self.processes.get_mut(&parent_id) {
                parent.add_child(pid)?;
            }
        }

        self.processes.insert(pid, pcb);
        self.scheduler_stats.total_processes += 1;

        Ok(pid)
    }

    /// Add process to ready queue
    pub fn schedule_process(&mut self, pid: ProcessId) -> Result<(), SchedulerError> {
        // First check and update process state
        {
            let process = self.processes.get_mut(&pid)
                .ok_or(SchedulerError::ProcessNotFound)?;

            if process.state != ProcessState::Created && process.state != ProcessState::Blocked {
                return Err(SchedulerError::SchedulingError);
            }

            process.set_state(ProcessState::Ready);
        }

        // Now choose core and add to queue
        let core_id = self.choose_cpu_core();
        let current_time = self.get_current_time();
        
        // Get process priority
        let priority = self.processes.get(&pid)
            .ok_or(SchedulerError::ProcessNotFound)?
            .priority;
            
        let core = &mut self.cores[core_id];

        let entry = SchedulerEntry {
            pid,
            time_at_priority: 0,
            last_scheduled: current_time,
        };

        core.ready_queues.get_queue_mut(priority).push_back(entry);
        self.update_stats();

        Ok(())
    }

    /// Get next process to run on specified CPU core
    pub fn get_next_process(&mut self, core_id: usize) -> Result<Option<ProcessId>, SchedulerError> {
        if core_id >= self.cores.len() {
            return Err(SchedulerError::InvalidCoreId);
        }

        let core = &mut self.cores[core_id];

        // Check all priority levels from highest to lowest
        for priority in [Priority::RealTime, Priority::High, Priority::Normal, Priority::Low, Priority::Idle].iter() {
            let queue = core.ready_queues.get_queue_mut(*priority);
            
            if let Some(entry) = queue.pop_front() {
                if let Some(process) = self.processes.get_mut(&entry.pid) {
                    if process.is_schedulable() {
                        process.set_state(ProcessState::Running);
                        process.time_slice_remaining = SCHEDULING_QUANTA[*priority as usize];
                        
                        core.current_process = Some(entry.pid);
                        core.total_context_switches += 1;
                        self.scheduler_stats.total_context_switches += 1;
                        
                        self.update_stats();
                        return Ok(Some(entry.pid));
                    }
                }
            }
        }

        // No process found - CPU will idle
        core.current_process = None;
        core.idle_time += 1000; // Add 1ms to idle time
        Ok(None)
    }

    /// Get process by PID
    pub fn get_process(&self, pid: ProcessId) -> Option<&ProcessControlBlock> {
        self.processes.get(&pid)
    }

    /// Get mutable process by PID
    pub fn get_process_mut(&mut self, pid: ProcessId) -> Option<&mut ProcessControlBlock> {
        self.processes.get_mut(&pid)
    }

    /// Get scheduler statistics
    pub fn get_stats(&self) -> &SchedulerStats {
        &self.scheduler_stats
    }

    // Helper methods

    fn choose_cpu_core(&mut self) -> usize {
        // Simple round-robin load balancing
        let core_id = self.load_balancer_counter % self.cores.len();
        self.load_balancer_counter += 1;
        core_id
    }

    fn update_stats(&mut self) {
        self.scheduler_stats.total_processes = self.processes.len();
        self.scheduler_stats.running_processes = 0;
        self.scheduler_stats.ready_processes = 0;
        self.scheduler_stats.blocked_processes = 0;
        self.scheduler_stats.zombie_processes = 0;

        for process in self.processes.values() {
            match process.state {
                ProcessState::Running => self.scheduler_stats.running_processes += 1,
                ProcessState::Ready => self.scheduler_stats.ready_processes += 1,
                ProcessState::Blocked | ProcessState::Sleeping => self.scheduler_stats.blocked_processes += 1,
                ProcessState::Zombie => self.scheduler_stats.zombie_processes += 1,
                _ => {}
            }
        }

        // Calculate average load across all cores
        let total_load: f32 = (0..self.cores.len())
            .map(|i| self.get_core_load(i))
            .sum();
        
        self.scheduler_stats.average_load = total_load / self.cores.len() as f32;
    }

    fn get_core_load(&self, core_id: usize) -> f32 {
        if core_id >= self.cores.len() {
            return 0.0;
        }

        let core = &self.cores[core_id];
        let total_processes = core.ready_queues.total_processes();
        
        if core.current_process.is_some() {
            (total_processes + 1) as f32
        } else {
            total_processes as f32
        }
    }

    fn get_current_time(&self) -> u64 {
        // TODO: Get actual system time
        42000000 // 42 seconds in microseconds
    }
}

/// Public scheduler interface functions
pub fn init_scheduler(num_cores: usize) {
    ProcessScheduler::init(num_cores);
}

pub fn create_process(
    name: alloc::string::String,
    entry_point: u64,
    parent_pid: Option<ProcessId>,
) -> Result<ProcessId, ProcessError> {
    if let Some(ref mut scheduler) = *ProcessScheduler::get() {
        scheduler.create_process(name, entry_point, parent_pid)
    } else {
        Err(ProcessError::InvalidState)
    }
}

pub fn schedule_process(pid: ProcessId) -> Result<(), SchedulerError> {
    if let Some(ref mut scheduler) = *ProcessScheduler::get() {
        scheduler.schedule_process(pid)
    } else {
        Err(SchedulerError::SchedulingError)
    }
}

pub fn get_next_process(core_id: usize) -> Result<Option<ProcessId>, SchedulerError> {
    if let Some(ref mut scheduler) = *ProcessScheduler::get() {
        scheduler.get_next_process(core_id)
    } else {
        Err(SchedulerError::SchedulingError)
    }
}
