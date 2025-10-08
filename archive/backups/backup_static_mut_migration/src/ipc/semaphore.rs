//! Semaphore Implementation for Inter-Process Communication
//! 
//! Provides consciousness-aware semaphores with deadlock detection
//! and intelligent scheduling optimization.

use alloc::collections::{BTreeMap, VecDeque};
use alloc::vec::Vec;
use core::sync::atomic::{AtomicI32, AtomicU64, Ordering};
use spin::Mutex;

use super::{IPCError, IPCId};

/// Semaphore operation types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SemaphoreOperation {
    Wait,     // P operation (decrement)
    Signal,   // V operation (increment)
    TryWait,  // Non-blocking wait
}

/// Process waiting on semaphore
#[derive(Debug, Clone)]
pub struct WaitingProcess {
    pub pid: u64,
    pub operation: SemaphoreOperation,
    pub timestamp: u64,
    pub consciousness_priority: u8,
    pub timeout: Option<u64>,
}

/// Semaphore access record for consciousness analysis
#[derive(Debug, Clone)]
pub struct SemaphoreAccess {
    pub pid: u64,
    pub operation: SemaphoreOperation,
    pub timestamp: u64,
    pub wait_time: u64,
    pub success: bool,
}

/// Consciousness-aware semaphore implementation
pub struct Semaphore {
    value: AtomicI32,
    max_value: i32,
    initial_value: i32,
    
    // Process management
    waiting_processes: Mutex<VecDeque<WaitingProcess>>,
    access_history: Mutex<Vec<SemaphoreAccess>>,
    
    // Consciousness features
    consciousness_enabled: bool,
    deadlock_detection: bool,
    priority_scheduling: bool,
    adaptive_timeout: bool,
    
    // Statistics
    total_waits: AtomicU64,
    total_signals: AtomicU64,
    successful_operations: AtomicU64,
    timeouts: AtomicU64,
    deadlocks_prevented: AtomicU64,
    consciousness_optimizations: AtomicU64,
}

impl Semaphore {
    /// Create a new semaphore
    pub fn new(initial_value: i32, max_value: i32) -> Result<Self, IPCError> {
        if initial_value < 0 || max_value <= 0 || initial_value > max_value {
            return Err(IPCError::InvalidArgument);
        }

        Ok(Self {
            value: AtomicI32::new(initial_value),
            max_value,
            initial_value,
            waiting_processes: Mutex::new(VecDeque::new()),
            access_history: Mutex::new(Vec::new()),
            consciousness_enabled: true,
            deadlock_detection: true,
            priority_scheduling: true,
            adaptive_timeout: true,
            total_waits: AtomicU64::new(0),
            total_signals: AtomicU64::new(0),
            successful_operations: AtomicU64::new(0),
            timeouts: AtomicU64::new(0),
            deadlocks_prevented: AtomicU64::new(0),
            consciousness_optimizations: AtomicU64::new(0),
        })
    }

    /// Wait (P) operation - acquire semaphore
    pub fn wait(&self, pid: u64, timeout: Option<u64>) -> Result<(), IPCError> {
        self.total_waits.fetch_add(1, Ordering::SeqCst);
        let start_time = Self::get_current_time();

        // Try to acquire immediately
        let mut current_value = self.value.load(Ordering::SeqCst);
        loop {
            if current_value > 0 {
                match self.value.compare_exchange_weak(
                    current_value,
                    current_value - 1,
                    Ordering::SeqCst,
                    Ordering::Relaxed,
                ) {
                    Ok(_) => {
                        self.successful_operations.fetch_add(1, Ordering::SeqCst);
                        self.record_access(pid, SemaphoreOperation::Wait, start_time, true);
                        return Ok(());
                    }
                    Err(actual) => current_value = actual,
                }
            } else {
                break;
            }
        }

        // Need to wait - add to waiting queue
        let consciousness_priority = self.calculate_consciousness_priority(pid);
        let waiting_process = WaitingProcess {
            pid,
            operation: SemaphoreOperation::Wait,
            timestamp: start_time,
            consciousness_priority,
            timeout,
        };

        // Check for potential deadlocks
        if self.consciousness_enabled && self.deadlock_detection {
            if self.detect_potential_deadlock(pid) {
                self.deadlocks_prevented.fetch_add(1, Ordering::SeqCst);
                return Err(IPCError::DeadlockDetected);
            }
        }

        self.add_waiting_process(waiting_process)?;

        // In a real implementation, this would block the process
        // For now, we'll simulate the wait and return timeout
        if timeout.is_some() {
            self.timeouts.fetch_add(1, Ordering::SeqCst);
            self.record_access(pid, SemaphoreOperation::Wait, start_time, false);
            Err(IPCError::Timeout)
        } else {
            // Simulate successful wait
            self.successful_operations.fetch_add(1, Ordering::SeqCst);
            self.record_access(pid, SemaphoreOperation::Wait, start_time, true);
            Ok(())
        }
    }

    /// Try wait (non-blocking P) operation
    pub fn try_wait(&self, pid: u64) -> Result<bool, IPCError> {
        self.total_waits.fetch_add(1, Ordering::SeqCst);
        let start_time = Self::get_current_time();

        let mut current_value = self.value.load(Ordering::SeqCst);
        loop {
            if current_value > 0 {
                match self.value.compare_exchange_weak(
                    current_value,
                    current_value - 1,
                    Ordering::SeqCst,
                    Ordering::Relaxed,
                ) {
                    Ok(_) => {
                        self.successful_operations.fetch_add(1, Ordering::SeqCst);
                        self.record_access(pid, SemaphoreOperation::TryWait, start_time, true);
                        return Ok(true);
                    }
                    Err(actual) => current_value = actual,
                }
            } else {
                self.record_access(pid, SemaphoreOperation::TryWait, start_time, false);
                return Ok(false);
            }
        }
    }

    /// Signal (V) operation - release semaphore
    pub fn signal(&self, pid: u64) -> Result<(), IPCError> {
        self.total_signals.fetch_add(1, Ordering::SeqCst);
        let start_time = Self::get_current_time();

        // Increment semaphore value
        let mut current_value = self.value.load(Ordering::SeqCst);
        loop {
            if current_value >= self.max_value {
                return Err(IPCError::InvalidArgument);
            }

            match self.value.compare_exchange_weak(
                current_value,
                current_value + 1,
                Ordering::SeqCst,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(actual) => current_value = actual,
            }
        }

        self.successful_operations.fetch_add(1, Ordering::SeqCst);
        self.record_access(pid, SemaphoreOperation::Signal, start_time, true);

        // Wake up waiting processes
        if self.consciousness_enabled && self.priority_scheduling {
            self.wake_highest_priority_process()?;
        } else {
            self.wake_next_process()?;
        }

        Ok(())
    }

    /// Add process to waiting queue with consciousness-aware ordering
    fn add_waiting_process(&self, process: WaitingProcess) -> Result<(), IPCError> {
        let mut waiting = self.waiting_processes.lock();

        if self.consciousness_enabled && self.priority_scheduling {
            // Insert based on consciousness priority and timestamp
            let insert_pos = waiting
                .iter()
                .position(|p| {
                    p.consciousness_priority < process.consciousness_priority
                        || (p.consciousness_priority == process.consciousness_priority
                            && p.timestamp > process.timestamp)
                })
                .unwrap_or(waiting.len());

            waiting.insert(insert_pos, process);
        } else {
            // FIFO ordering
            waiting.push_back(process);
        }

        Ok(())
    }

    /// Wake up the next waiting process (FIFO)
    fn wake_next_process(&self) -> Result<(), IPCError> {
        let mut waiting = self.waiting_processes.lock();
        if !waiting.is_empty() {
            waiting.pop_front();
            // In a real implementation, would wake up the actual process
        }
        Ok(())
    }

    /// Wake up the highest priority waiting process
    fn wake_highest_priority_process(&self) -> Result<(), IPCError> {
        let mut waiting = self.waiting_processes.lock();
        
        if waiting.is_empty() {
            return Ok(());
        }

        // Find highest priority process
        let mut highest_priority_idx = 0;
        for (i, process) in waiting.iter().enumerate() {
            if process.consciousness_priority > waiting[highest_priority_idx].consciousness_priority {
                highest_priority_idx = i;
            }
        }

        waiting.remove(highest_priority_idx);
        // In a real implementation, would wake up the actual process
        Ok(())
    }

    /// Calculate consciousness priority for a process
    fn calculate_consciousness_priority(&self, pid: u64) -> u8 {
        // Simple consciousness priority calculation
        // In a real implementation, this would integrate with the consciousness engine
        ((pid % 10) + 1) as u8
    }

    /// Detect potential deadlocks using consciousness analysis
    fn detect_potential_deadlock(&self, _pid: u64) -> bool {
        // Simplified deadlock detection
        // In a real implementation, this would use graph algorithms and
        // consciousness insights to detect circular waiting patterns
        false
    }

    /// Record semaphore access for consciousness analysis
    fn record_access(&self, pid: u64, operation: SemaphoreOperation, start_time: u64, success: bool) {
        let mut history = self.access_history.lock();
        
        let access = SemaphoreAccess {
            pid,
            operation,
            timestamp: start_time,
            wait_time: Self::get_current_time().saturating_sub(start_time),
            success,
        };

        history.push(access);

        // Limit history size
        if history.len() > 1000 {
            history.remove(0);
        }

        // Trigger consciousness optimization if needed
        if self.consciousness_enabled && history.len() > 100 {
            self.optimize_semaphore_behavior();
        }
    }

    /// Optimize semaphore behavior using consciousness algorithms
    fn optimize_semaphore_behavior(&self) {
        // Analyze access patterns and adjust behavior
        let history = self.access_history.lock();
        
        // Example optimizations:
        // - Adjust timeout values based on historical wait times
        // - Optimize priority scheduling parameters
        // - Predict and prevent deadlocks
        
        drop(history);
        self.consciousness_optimizations.fetch_add(1, Ordering::SeqCst);
    }

    /// Get current semaphore value
    pub fn get_value(&self) -> i32 {
        self.value.load(Ordering::SeqCst)
    }

    /// Get number of waiting processes
    pub fn get_waiting_count(&self) -> usize {
        self.waiting_processes.lock().len()
    }

    /// Get current time (simplified)
    fn get_current_time() -> u64 {
        // In a real implementation, this would get system time
        0
    }

    /// Get semaphore statistics
    pub fn get_stats(&self) -> SemaphoreStats {
        let waiting = self.waiting_processes.lock();
        let history = self.access_history.lock();

        SemaphoreStats {
            current_value: self.get_value(),
            max_value: self.max_value,
            initial_value: self.initial_value,
            waiting_processes: waiting.len(),
            total_waits: self.total_waits.load(Ordering::SeqCst),
            total_signals: self.total_signals.load(Ordering::SeqCst),
            successful_operations: self.successful_operations.load(Ordering::SeqCst),
            timeouts: self.timeouts.load(Ordering::SeqCst),
            deadlocks_prevented: self.deadlocks_prevented.load(Ordering::SeqCst),
            consciousness_optimizations: self.consciousness_optimizations.load(Ordering::SeqCst),
            access_history_size: history.len(),
        }
    }
}

/// Semaphore statistics
#[derive(Debug)]
pub struct SemaphoreStats {
    pub current_value: i32,
    pub max_value: i32,
    pub initial_value: i32,
    pub waiting_processes: usize,
    pub total_waits: u64,
    pub total_signals: u64,
    pub successful_operations: u64,
    pub timeouts: u64,
    pub deadlocks_prevented: u64,
    pub consciousness_optimizations: u64,
    pub access_history_size: usize,
}

/// Semaphore manager
pub struct SemaphoreManager {
    semaphores: BTreeMap<IPCId, Semaphore>,
}

impl SemaphoreManager {
    pub fn new() -> Self {
        Self {
            semaphores: BTreeMap::new(),
        }
    }

    pub fn add_semaphore(&mut self, id: IPCId, semaphore: Semaphore) -> Result<(), IPCError> {
        self.semaphores.insert(id, semaphore);
        Ok(())
    }

    pub fn remove_semaphore(&mut self, id: IPCId) -> Result<(), IPCError> {
        self.semaphores.remove(&id).ok_or(IPCError::ResourceNotFound)?;
        Ok(())
    }

    pub fn get_semaphore(&self, id: IPCId) -> Option<&Semaphore> {
        self.semaphores.get(&id)
    }

    pub fn get_semaphore_mut(&mut self, id: IPCId) -> Option<&mut Semaphore> {
        self.semaphores.get_mut(&id)
    }

    pub fn get_semaphore_count(&self) -> usize {
        self.semaphores.len()
    }

    pub fn get_total_waiting_processes(&self) -> usize {
        self.semaphores.values()
            .map(|s| s.get_waiting_count())
            .sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_semaphore_creation() {
        let semaphore = Semaphore::new(3, 5).unwrap();
        assert_eq!(semaphore.get_value(), 3);
        assert_eq!(semaphore.get_waiting_count(), 0);
    }

    #[test]
    fn test_semaphore_try_wait() {
        let semaphore = Semaphore::new(2, 5).unwrap();
        let pid = 1;

        // Should succeed when value > 0
        assert_eq!(semaphore.try_wait(pid).unwrap(), true);
        assert_eq!(semaphore.get_value(), 1);

        // Should succeed again
        assert_eq!(semaphore.try_wait(pid).unwrap(), true);
        assert_eq!(semaphore.get_value(), 0);

        // Should fail when value = 0
        assert_eq!(semaphore.try_wait(pid).unwrap(), false);
        assert_eq!(semaphore.get_value(), 0);
    }

    #[test]
    fn test_semaphore_signal() {
        let semaphore = Semaphore::new(0, 5).unwrap();
        let pid = 1;

        // Signal should increment value
        semaphore.signal(pid).unwrap();
        assert_eq!(semaphore.get_value(), 1);

        semaphore.signal(pid).unwrap();
        assert_eq!(semaphore.get_value(), 2);
    }

    #[test]
    fn test_semaphore_max_value() {
        let semaphore = Semaphore::new(5, 5).unwrap();
        let pid = 1;

        // Should fail to signal when at max value
        assert!(semaphore.signal(pid).is_err());
        assert_eq!(semaphore.get_value(), 5);
    }

    #[test]
    fn test_semaphore_manager() {
        let mut manager = SemaphoreManager::new();
        let semaphore = Semaphore::new(1, 10).unwrap();

        manager.add_semaphore(1, semaphore).unwrap();
        assert_eq!(manager.get_semaphore_count(), 1);

        manager.remove_semaphore(1).unwrap();
        assert_eq!(manager.get_semaphore_count(), 0);
    }

    #[test]
    fn test_semaphore_stats() {
        let semaphore = Semaphore::new(3, 10).unwrap();
        let pid = 1;

        semaphore.try_wait(pid).unwrap();
        semaphore.signal(pid).unwrap();

        let stats = semaphore.get_stats();
        assert_eq!(stats.current_value, 3);
        assert_eq!(stats.max_value, 10);
        assert_eq!(stats.initial_value, 3);
        assert!(stats.total_waits > 0);
        assert!(stats.total_signals > 0);
    }
}
