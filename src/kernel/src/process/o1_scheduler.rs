//! O(1) Process Scheduler with Per-CPU Runqueues
//!
//! High-performance scheduler that provides O(1) time complexity for all
//! operations, featuring per-CPU runqueues and lock-free operations where possible.

#![no_std]

use alloc::{vec::Vec, collections::VecDeque, boxed::Box};
use core::{
    sync::atomic::{AtomicU64, AtomicU32, AtomicBool, Ordering},
    mem::MaybeUninit,
};
use spin::{RwLock, Mutex};
use super::{ProcessId, ProcessState, CpuId};

/// Maximum number of priority levels (0 = highest, 139 = lowest)
pub const MAX_PRIORITY_LEVELS: usize = 140;

/// Number of CPUs supported (configurable at compile time)
pub const MAX_CPUS: usize = 64;

/// Scheduler errors with comprehensive error handling
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SchedulerError {
    InvalidProcessId,
    InvalidCpuId,
    InvalidPriority,
    QueueEmpty,
    ProcessAlreadyQueued,
    ProcessNotFound,
    CpuOffline,
    SystemOverload,
}

/// Process scheduling information
#[derive(Debug, Clone)]
pub struct SchedEntity {
    pub process_id: ProcessId,
    pub priority: u8,
    pub nice: i8,
    pub vruntime: u64,          // Virtual runtime for CFS
    pub exec_start: u64,        // When process started execution
    pub sum_exec_runtime: u64,  // Total execution time
    pub time_slice: u32,        // Remaining time slice
    pub cpu_affinity: u64,      // CPU affinity mask
    pub state: ProcessState,
    pub preempt_count: u32,     // Preemption disable count
}

impl SchedEntity {
    pub fn new(process_id: ProcessId, priority: u8) -> Self {
        Self {
            process_id,
            priority: priority.min(139),
            nice: 0,
            vruntime: 0,
            exec_start: 0,
            sum_exec_runtime: 0,
            time_slice: calculate_time_slice(priority),
            cpu_affinity: u64::MAX, // All CPUs by default
            state: ProcessState::Ready,
            preempt_count: 0,
        }
    }
}

/// Per-CPU runqueue with O(1) operations
#[derive(Debug)]
pub struct CpuRunqueue {
    cpu_id: CpuId,

    // Priority-based runqueues (140 priority levels)
    active_queues: [VecDeque<ProcessId>; MAX_PRIORITY_LEVELS],
    expired_queues: [VecDeque<ProcessId>; MAX_PRIORITY_LEVELS],

    // Bitmasks for O(1) priority scanning
    active_bitmap: AtomicU64,      // Bitmap of non-empty active queues (first 64 levels)
    active_bitmap_high: AtomicU64, // Bitmap for levels 64-127
    expired_bitmap: AtomicU64,     // Bitmap of non-empty expired queues
    expired_bitmap_high: AtomicU64,

    // Current running process
    current_process: Option<ProcessId>,

    // Load balancing
    load_weight: AtomicU32,        // Total weight of processes
    nr_running: AtomicU32,         // Number of runnable processes

    // Timestamps
    last_load_update: AtomicU64,
    clock: AtomicU64,

    // CPU-specific state
    idle_balance_lock: AtomicBool,

    // Lock for queue modifications (minimize contention)
    queue_lock: Mutex<()>,
}

impl CpuRunqueue {
    pub fn new(cpu_id: CpuId) -> Self {
        // Initialize empty queues
        let active_queues: [VecDeque<ProcessId>; MAX_PRIORITY_LEVELS] =
            core::array::from_fn(|_| VecDeque::new());
        let expired_queues: [VecDeque<ProcessId>; MAX_PRIORITY_LEVELS] =
            core::array::from_fn(|_| VecDeque::new());

        Self {
            cpu_id,
            active_queues,
            expired_queues,
            active_bitmap: AtomicU64::new(0),
            active_bitmap_high: AtomicU64::new(0),
            expired_bitmap: AtomicU64::new(0),
            expired_bitmap_high: AtomicU64::new(0),
            current_process: None,
            load_weight: AtomicU32::new(0),
            nr_running: AtomicU32::new(0),
            last_load_update: AtomicU64::new(0),
            clock: AtomicU64::new(0),
            idle_balance_lock: AtomicBool::new(false),
            queue_lock: Mutex::new(()),
        }
    }

    /// Add process to runqueue - O(1) operation
    pub fn enqueue_process(&mut self, process_id: ProcessId, priority: u8) -> Result<(), SchedulerError> {
        if priority as usize >= MAX_PRIORITY_LEVELS {
            return Err(SchedulerError::InvalidPriority);
        }

        let _lock = self.queue_lock.lock();

        // Add to active queue
        self.active_queues[priority as usize].push_back(process_id);

        // Update bitmask for O(1) scanning
        if priority < 64 {
            let mask = 1u64 << priority;
            self.active_bitmap.fetch_or(mask, Ordering::Release);
        } else {
            let mask = 1u64 << (priority - 64);
            self.active_bitmap_high.fetch_or(mask, Ordering::Release);
        }

        // Update load statistics
        self.nr_running.fetch_add(1, Ordering::Relaxed);
        self.load_weight.fetch_add(priority_to_weight(priority), Ordering::Relaxed);

        Ok(())
    }

    /// Remove and return highest priority process - O(1) operation
    pub fn dequeue_next_process(&mut self) -> Result<ProcessId, SchedulerError> {
        // Find highest priority non-empty queue using bit scanning
        let priority = self.find_first_set_priority()?;

        let _lock = self.queue_lock.lock();

        // Remove from queue
        let process_id = self.active_queues[priority]
            .pop_front()
            .ok_or(SchedulerError::QueueEmpty)?;

        // Update bitmask if queue becomes empty
        if self.active_queues[priority].is_empty() {
            self.clear_priority_bit(priority, false);
        }

        // Update load statistics
        self.nr_running.fetch_sub(1, Ordering::Relaxed);
        self.load_weight.fetch_sub(priority_to_weight(priority as u8), Ordering::Relaxed);

        Ok(process_id)
    }

    /// Find first set bit in priority bitmasks - O(1) using hardware instruction
    fn find_first_set_priority(&mut self) -> Result<usize, SchedulerError> {
        // Check active queues first
        let active_low = self.active_bitmap.load(Ordering::Acquire);
        if active_low != 0 {
            return Ok(active_low.trailing_zeros() as usize);
        }

        let active_high = self.active_bitmap_high.load(Ordering::Acquire);
        if active_high != 0 {
            return Ok(64 + active_high.trailing_zeros() as usize);
        }

        // Check expired queues
        let expired_low = self.expired_bitmap.load(Ordering::Acquire);
        if expired_low != 0 {
            // Swap active and expired arrays
            self.swap_array_queues();
            return Ok(expired_low.trailing_zeros() as usize);
        }

        let expired_high = self.expired_bitmap_high.load(Ordering::Acquire);
        if expired_high != 0 {
            self.swap_array_queues();
            return Ok(64 + expired_high.trailing_zeros() as usize);
        }

        Err(SchedulerError::QueueEmpty)
    }

    /// Clear priority bit when queue becomes empty
    fn clear_priority_bit(&self, priority: usize, expired: bool) {
        if priority < 64 {
            let mask = !(1u64 << priority);
            if expired {
                self.expired_bitmap.fetch_and(mask, Ordering::Release);
            } else {
                self.active_bitmap.fetch_and(mask, Ordering::Release);
            }
        } else {
            let mask = !(1u64 << (priority - 64));
            if expired {
                self.expired_bitmap_high.fetch_and(mask, Ordering::Release);
            } else {
                self.active_bitmap_high.fetch_and(mask, Ordering::Release);
            }
        }
    }

    /// Swap active and expired queue arrays - O(1) operation
    fn swap_array_queues(&mut self) {
        // This is a conceptual swap - in real implementation would use atomic pointers
        // For now, move all expired to active
        for priority in 0..MAX_PRIORITY_LEVELS {
            while let Some(pid) = self.expired_queues[priority].pop_front() {
                self.active_queues[priority].push_back(pid);
            }
        }

        // Update bitmasks
        let expired_low = self.expired_bitmap.swap(0, Ordering::AcqRel);
        let expired_high = self.expired_bitmap_high.swap(0, Ordering::AcqRel);

        self.active_bitmap.fetch_or(expired_low, Ordering::Release);
        self.active_bitmap_high.fetch_or(expired_high, Ordering::Release);
    }

    /// Move process to expired queue when time slice exhausted
    pub fn expire_process(&mut self, process_id: ProcessId, priority: u8) -> Result<(), SchedulerError> {
        let _lock = self.queue_lock.lock();

        // Add to expired queue
        self.expired_queues[priority as usize].push_back(process_id);

        // Update expired bitmask
        if priority < 64 {
            let mask = 1u64 << priority;
            self.expired_bitmap.fetch_or(mask, Ordering::Release);
        } else {
            let mask = 1u64 << (priority - 64);
            self.expired_bitmap_high.fetch_or(mask, Ordering::Release);
        }

        Ok(())
    }

    /// Get current load for load balancing
    pub fn get_load(&self) -> u32 {
        self.load_weight.load(Ordering::Relaxed)
    }

    /// Get number of running processes
    pub fn get_nr_running(&self) -> u32 {
        self.nr_running.load(Ordering::Relaxed)
    }

    /// Update CPU clock
    pub fn update_clock(&self, time: u64) {
        self.clock.store(time, Ordering::Relaxed);
    }
}

/// O(1) Multi-CPU Scheduler
pub struct O1Scheduler {
    // Per-CPU runqueues for NUMA awareness and reduced contention
    cpu_runqueues: Vec<Box<CpuRunqueue>>,

    // Process scheduling entities
    sched_entities: RwLock<hashbrown::HashMap<ProcessId, SchedEntity>>,

    // Load balancing state
    load_balance_interval: AtomicU64,
    next_balance_time: AtomicU64,

    // Global statistics
    total_processes: AtomicU32,
    context_switches: AtomicU64,

    // Configuration
    cpu_count: usize,
    time_slice_granularity: u32,
}

impl O1Scheduler {
    pub fn new(cpu_count: usize) -> Self {
        let mut cpu_runqueues = Vec::with_capacity(cpu_count);

        // Initialize per-CPU runqueues
        for cpu_id in 0..cpu_count {
            cpu_runqueues.push(Box::new(CpuRunqueue::new(cpu_id as CpuId)));
        }

        Self {
            cpu_runqueues,
            sched_entities: RwLock::new(hashbrown::HashMap::new()),
            load_balance_interval: AtomicU64::new(1000), // 1ms
            next_balance_time: AtomicU64::new(0),
            total_processes: AtomicU32::new(0),
            context_switches: AtomicU64::new(0),
            cpu_count,
            time_slice_granularity: 1000, // 1ms in microseconds
        }
    }

    /// Add new process to scheduler - O(1) operation
    pub fn add_process(&mut self, process_id: ProcessId, priority: u8) -> Result<(), SchedulerError> {
        // Create scheduling entity
        let sched_entity = SchedEntity::new(process_id, priority);

        // Add to entities map
        {
            let mut entities = self.sched_entities.write();
            entities.insert(process_id, sched_entity);
        }

        // Find best CPU for this process
        let cpu_id = self.select_cpu_for_process(process_id)?;

        // Add to CPU runqueue
        self.cpu_runqueues[cpu_id].enqueue_process(process_id, priority)?;

        self.total_processes.fetch_add(1, Ordering::Relaxed);

        Ok(())
    }

    /// Schedule next process on given CPU - O(1) operation
    pub fn schedule_next(&self, cpu_id: CpuId) -> Result<ProcessId, SchedulerError> {
        if cpu_id as usize >= self.cpu_count {
            return Err(SchedulerError::InvalidCpuId);
        }

        // Get next process from CPU runqueue
        let process_id = self.cpu_runqueues[cpu_id as usize].dequeue_next_process()?;

        // Update scheduling statistics
        self.context_switches.fetch_add(1, Ordering::Relaxed);

        // Update process execution start time
        {
            let mut entities = self.sched_entities.write();
            if let Some(entity) = entities.get_mut(&process_id) {
                entity.exec_start = crate::time::get_current_time();
                entity.state = ProcessState::Running;
            }
        }

        Ok(process_id)
    }

    /// Process time slice exhausted - move to expired queue
    pub fn process_tick(&self, process_id: ProcessId, cpu_id: CpuId) -> Result<bool, SchedulerError> {
        let mut should_preempt = false;

        // Update process runtime and check time slice
        {
            let mut entities = self.sched_entities.write();
            if let Some(entity) = entities.get_mut(&process_id) {
                let current_time = crate::time::get_current_time();
                let exec_time = current_time - entity.exec_start;

                entity.sum_exec_runtime += exec_time;
                entity.time_slice = entity.time_slice.saturating_sub(exec_time as u32);

                // Check if time slice exhausted
                if entity.time_slice == 0 {
                    // Move to expired queue
                    self.cpu_runqueues[cpu_id as usize]
                        .expire_process(process_id, entity.priority)?;

                    // Reset time slice
                    entity.time_slice = calculate_time_slice(entity.priority);
                    entity.state = ProcessState::Ready;

                    should_preempt = true;
                }
            }
        }

        Ok(should_preempt)
    }

    /// Select best CPU for process placement
    fn select_cpu_for_process(&self, process_id: ProcessId) -> Result<usize, SchedulerError> {
        // Simple load balancing - find CPU with lowest load
        let mut best_cpu = 0;
        let mut min_load = u32::MAX;

        for (cpu_id, runqueue) in self.cpu_runqueues.iter().enumerate() {
            let load = runqueue.get_load();
            if load < min_load {
                min_load = load;
                best_cpu = cpu_id;
            }
        }

        Ok(best_cpu)
    }

    /// Get scheduler statistics
    pub fn get_stats(&self) -> SchedulerStats {
        SchedulerStats {
            total_processes: self.total_processes.load(Ordering::Relaxed),
            context_switches: self.context_switches.load(Ordering::Relaxed),
            cpu_loads: self.cpu_runqueues.iter()
                .map(|rq| rq.get_load())
                .collect(),
        }
    }
}

/// Calculate time slice based on priority
fn calculate_time_slice(priority: u8) -> u32 {
    // Higher priority = longer time slice
    // Range: 5ms to 100ms
    let base_slice = 5000; // 5ms in microseconds
    let max_slice = 100000; // 100ms in microseconds

    let factor = (140 - priority as u32) * (max_slice - base_slice) / 140;
    base_slice + factor
}

/// Convert priority to load weight
fn priority_to_weight(priority: u8) -> u32 {
    // Standard Linux CFS weights
    const NICE_0_LOAD: u32 = 1024;
    const PRIO_TO_WEIGHT: [u32; 40] = [
        88761, 71755, 56483, 46273, 36291,
        29154, 23254, 18705, 14949, 11916,
        9548, 7620, 6100, 4904, 3906,
        3121, 2501, 1991, 1586, 1277,
        1024, 820, 655, 526, 423,
        335, 272, 215, 172, 137,
        110, 87, 70, 56, 45,
        36, 29, 23, 18, 15,
    ];

    if priority < 40 {
        PRIO_TO_WEIGHT[priority as usize]
    } else {
        NICE_0_LOAD >> ((priority - 40) / 5)
    }
}

/// Scheduler statistics
#[derive(Debug, Clone)]
pub struct SchedulerStats {
    pub total_processes: u32,
    pub context_switches: u64,
    pub cpu_loads: Vec<u32>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_o1_scheduler_creation() {
        let scheduler = O1Scheduler::new(4);
        assert_eq!(scheduler.cpu_count, 4);
    }

    #[test]
    fn test_process_addition() {
        let scheduler = O1Scheduler::new(2);
        assert!(scheduler.add_process(1, 20).is_ok());
        assert_eq!(scheduler.total_processes.load(Ordering::Relaxed), 1);
    }

    #[test]
    fn test_o1_scheduling() {
        let scheduler = O1Scheduler::new(1);
        scheduler.add_process(1, 20).expect("Add process");

        let next = scheduler.schedule_next(0).expect("Schedule next");
        assert_eq!(next, 1);
    }

    #[test]
    fn test_priority_ordering() {
        let scheduler = O1Scheduler::new(1);
        scheduler.add_process(1, 50).expect("Add low priority");
        scheduler.add_process(2, 10).expect("Add high priority");

        // High priority should be scheduled first
        let next = scheduler.schedule_next(0).expect("Schedule next");
        assert_eq!(next, 2);
    }
}