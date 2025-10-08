/// Process scheduler for SynOS kernel
/// Implements round-robin scheduling with priority support

use super::{ProcessId, ProcessManager, Priority};
use alloc::collections::VecDeque;

/// Scheduling algorithms
#[derive(Debug, Clone, Copy)]
pub enum SchedulingAlgorithm {
    RoundRobin,
    PriorityBased,
    Multilevel,
}

/// Time slice for round-robin scheduling (in timer ticks)
pub const DEFAULT_TIME_SLICE: u32 = 10;

/// Scheduler configuration
pub struct SchedulerConfig {
    pub algorithm: SchedulingAlgorithm,
    pub time_slice: u32,
    pub priority_boost_interval: u32,
}

impl Default for SchedulerConfig {
    fn default() -> Self {
        SchedulerConfig {
            algorithm: SchedulingAlgorithm::RoundRobin,
            time_slice: DEFAULT_TIME_SLICE,
            priority_boost_interval: 100, // Boost priorities every 100 ticks
        }
    }
}

/// Process scheduler
pub struct Scheduler {
    config: SchedulerConfig,
    ready_queues: [VecDeque<ProcessId>; 4], // One queue per priority level
    current_time_slice: u32,
    total_ticks: u32,
    last_priority_boost: u32,
}

impl Scheduler {
    /// Create a new scheduler
    pub fn new(config: SchedulerConfig) -> Self {
        Scheduler {
            config,
            ready_queues: [
                VecDeque::new(), // Low priority
                VecDeque::new(), // Normal priority
                VecDeque::new(), // High priority
                VecDeque::new(), // Realtime priority
            ],
            current_time_slice: 0,
            total_ticks: 0,
            last_priority_boost: 0,
        }
    }

    /// Add a process to the ready queue
    pub fn add_ready_process(&mut self, pid: ProcessId, priority: Priority) {
        let queue_index = priority as usize;
        self.ready_queues[queue_index].push_back(pid);
    }

    /// Remove a process from all ready queues
    pub fn remove_process(&mut self, pid: ProcessId) {
        for queue in &mut self.ready_queues {
            queue.retain(|&p| p != pid);
        }
    }

    /// Select the next process to run
    pub fn select_next_process(&mut self) -> Option<ProcessId> {
        match self.config.algorithm {
            SchedulingAlgorithm::RoundRobin => self.round_robin_select(),
            SchedulingAlgorithm::PriorityBased => self.priority_select(),
            SchedulingAlgorithm::Multilevel => self.multilevel_select(),
        }
    }

    /// Round-robin scheduling implementation
    fn round_robin_select(&mut self) -> Option<ProcessId> {
        // Simple round-robin across all priorities
        for queue in self.ready_queues.iter_mut().rev() {
            if let Some(pid) = queue.pop_front() {
                queue.push_back(pid); // Put it at the end for next time
                return Some(pid);
            }
        }
        None
    }

    /// Priority-based scheduling implementation
    fn priority_select(&mut self) -> Option<ProcessId> {
        // Always select from highest priority queue first
        for queue in self.ready_queues.iter_mut().rev() {
            if let Some(pid) = queue.pop_front() {
                return Some(pid);
            }
        }
        None
    }

    /// Multilevel feedback queue implementation
    fn multilevel_select(&mut self) -> Option<ProcessId> {
        // Check realtime queue first
        if let Some(pid) = self.ready_queues[3].pop_front() {
            return Some(pid);
        }

        // Then check other queues with time slicing
        for (priority, queue) in self.ready_queues.iter_mut().enumerate().rev() {
            if priority == 3 { continue; } // Skip realtime (already checked)

            if let Some(pid) = queue.pop_front() {
                // Longer time slices for higher priorities
                let time_slice = match priority {
                    2 => self.config.time_slice * 2, // High priority
                    1 => self.config.time_slice,     // Normal priority
                    0 => self.config.time_slice / 2, // Low priority
                    _ => self.config.time_slice,
                };

                self.current_time_slice = time_slice;
                return Some(pid);
            }
        }
        None
    }

    /// Handle timer tick for scheduling decisions
    pub fn timer_tick(&mut self, process_manager: &mut ProcessManager) -> Option<ProcessId> {
        self.total_ticks += 1;

        // Check if we need to boost priorities (prevent starvation)
        if self.total_ticks - self.last_priority_boost >= self.config.priority_boost_interval {
            self.priority_boost(process_manager);
            self.last_priority_boost = self.total_ticks;
        }

        // Handle time slice expiration
        if self.current_time_slice > 0 {
            self.current_time_slice -= 1;

            // Time slice expired, consider preemption
            if self.current_time_slice == 0 {
                return self.handle_preemption(process_manager);
            }
        }

        None // No scheduling decision needed
    }

    /// Handle preemption when time slice expires
    fn handle_preemption(&mut self, process_manager: &mut ProcessManager) -> Option<ProcessId> {
        // If there's a current process, move it back to ready queue
        if let Some(current) = process_manager.current_process() {
            let current_pid = current.id;
            let current_priority = current.priority;

            // Demote priority in multilevel feedback queue
            if matches!(self.config.algorithm, SchedulingAlgorithm::Multilevel) {
                let new_priority = match current_priority {
                    Priority::Realtime => Priority::Realtime, // Don't demote realtime
                    Priority::High => Priority::Normal,
                    Priority::Normal => Priority::Low,
                    Priority::Low => Priority::Low, // Already at lowest
                };

                if let Some(process) = process_manager.get_process_mut(current_pid) {
                    process.priority = new_priority;
                }

                self.add_ready_process(current_pid, new_priority);
            } else {
                self.add_ready_process(current_pid, current_priority);
            }
        }

        // Select next process
        self.select_next_process()
    }

    /// Boost priorities to prevent starvation
    fn priority_boost(&mut self, process_manager: &mut ProcessManager) {
        // Move all processes to higher priority queues
        for priority in 0..3 {
            while let Some(pid) = self.ready_queues[priority].pop_front() {
                // Boost priority by one level
                let new_priority = match priority {
                    0 => Priority::Normal,
                    1 => Priority::High,
                    2 => Priority::Realtime,
                    _ => Priority::Realtime,
                };

                // Update process priority
                if let Some(process) = process_manager.get_process_mut(pid) {
                    process.priority = new_priority;
                }

                self.ready_queues[new_priority as usize].push_back(pid);
            }
        }
    }

    /// Schedule the next process to run
    pub fn schedule(&mut self, process_manager: &mut ProcessManager) -> Option<ProcessId> {
        // Update ready queues with any newly ready processes
        self.update_ready_queues(process_manager);

        // Select next process
        let next_pid = self.select_next_process();

        // Reset time slice for new process
        if next_pid.is_some() {
            self.current_time_slice = self.config.time_slice;
        }

        next_pid
    }

    /// Update ready queues with processes that became ready
    fn update_ready_queues(&mut self, process_manager: &ProcessManager) {
        let ready_processes = process_manager.ready_processes();

        for pid in ready_processes {
            if let Some(process) = process_manager.get_process(pid) {
                // Only add if not already in a queue
                let already_queued = self.ready_queues
                    .iter()
                    .any(|queue| queue.contains(&pid));

                if !already_queued {
                    self.add_ready_process(pid, process.priority);
                }
            }
        }
    }

    /// Get scheduler statistics
    pub fn stats(&self) -> SchedulerStats {
        let mut total_processes = 0;
        let queue_lengths: [usize; 4] = [
            self.ready_queues[0].len(),
            self.ready_queues[1].len(),
            self.ready_queues[2].len(),
            self.ready_queues[3].len(),
        ];

        for &length in &queue_lengths {
            total_processes += length;
        }

        SchedulerStats {
            algorithm: self.config.algorithm,
            total_ready_processes: total_processes,
            queue_lengths,
            current_time_slice: self.current_time_slice,
            total_ticks: self.total_ticks,
        }
    }
}

/// Scheduler statistics
#[derive(Debug)]
pub struct SchedulerStats {
    pub algorithm: SchedulingAlgorithm,
    pub total_ready_processes: usize,
    pub queue_lengths: [usize; 4], // [Low, Normal, High, Realtime]
    pub current_time_slice: u32,
    pub total_ticks: u32,
}

use lazy_static::lazy_static;
use spin::Mutex;

/// Global scheduler instance
lazy_static! {
    static ref SCHEDULER: Mutex<Scheduler> = Mutex::new(Scheduler::new(SchedulerConfig::default()));
}

/// Initialize the scheduler (for compatibility)
pub fn init(config: SchedulerConfig) {
    *SCHEDULER.lock() = Scheduler::new(config);
}

/// Execute a function with access to the scheduler
pub fn with_scheduler<F, R>(f: F) -> R
where
    F: FnOnce(&mut Scheduler) -> R,
{
    let mut scheduler = SCHEDULER.lock();
    f(&mut scheduler)
}

/// Main scheduling function called by timer interrupt
pub fn schedule_next() -> Option<ProcessId> {
    with_scheduler(|scheduler| {
        let process_manager = super::process_manager();
        scheduler.schedule(process_manager)
    })
}

/// Handle timer tick for scheduling
pub fn timer_tick() -> Option<ProcessId> {
    with_scheduler(|scheduler| {
        let process_manager = super::process_manager();
        scheduler.timer_tick(process_manager)
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scheduler_creation() {
        let config = SchedulerConfig::default();
        let scheduler = Scheduler::new(config);

        let stats = scheduler.stats();
        assert_eq!(stats.total_ready_processes, 0);
        assert_eq!(stats.current_time_slice, 0);
    }

    #[test]
    fn test_ready_queue_management() {
        let config = SchedulerConfig::default();
        let mut scheduler = Scheduler::new(config);

        scheduler.add_ready_process(1, Priority::Normal);
        scheduler.add_ready_process(2, Priority::High);

        let stats = scheduler.stats();
        assert_eq!(stats.total_ready_processes, 2);
        assert_eq!(stats.queue_lengths[1], 1); // Normal priority
        assert_eq!(stats.queue_lengths[2], 1); // High priority
    }
}
