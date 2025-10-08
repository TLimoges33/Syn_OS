//! Advanced Deadlock Detection for IPC
//!
//! Implements wait-for graph based deadlock detection

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use spin::Mutex;

/// Resource allocation graph node
#[derive(Debug, Clone)]
pub struct ResourceNode {
    pub resource_id: u64,
    pub holder_pid: Option<u64>,
    pub waiters: Vec<u64>,
}

/// Wait-for graph for deadlock detection
pub struct WaitForGraph {
    /// Process -> Resource edges (processes waiting for resources)
    process_to_resource: BTreeMap<u64, Vec<u64>>,
    /// Resource -> Process edges (processes holding resources)
    resource_to_process: BTreeMap<u64, u64>,
    /// All resources being tracked
    resources: BTreeMap<u64, ResourceNode>,
}

impl WaitForGraph {
    /// Create new wait-for graph
    pub fn new() -> Self {
        Self {
            process_to_resource: BTreeMap::new(),
            resource_to_process: BTreeMap::new(),
            resources: BTreeMap::new(),
        }
    }

    /// Add resource to graph
    pub fn add_resource(&mut self, resource_id: u64) {
        self.resources.insert(resource_id, ResourceNode {
            resource_id,
            holder_pid: None,
            waiters: Vec::new(),
        });
    }

    /// Process acquires a resource
    pub fn acquire_resource(&mut self, pid: u64, resource_id: u64) {
        // Update resource holder
        if let Some(resource) = self.resources.get_mut(&resource_id) {
            resource.holder_pid = Some(pid);
            // Remove from waiters if present
            resource.waiters.retain(|&p| p != pid);
        }

        // Update resource mapping
        self.resource_to_process.insert(resource_id, pid);

        // Remove from waiting list
        if let Some(waiting) = self.process_to_resource.get_mut(&pid) {
            waiting.retain(|&r| r != resource_id);
        }
    }

    /// Process releases a resource
    pub fn release_resource(&mut self, pid: u64, resource_id: u64) {
        // Update resource holder
        if let Some(resource) = self.resources.get_mut(&resource_id) {
            if resource.holder_pid == Some(pid) {
                resource.holder_pid = None;
            }
        }

        // Remove resource mapping
        self.resource_to_process.remove(&resource_id);
    }

    /// Process waits for a resource
    pub fn wait_for_resource(&mut self, pid: u64, resource_id: u64) {
        // Add to resource waiters
        if let Some(resource) = self.resources.get_mut(&resource_id) {
            if !resource.waiters.contains(&pid) {
                resource.waiters.push(pid);
            }
        }

        // Add to process waiting list
        self.process_to_resource
            .entry(pid)
            .or_insert_with(Vec::new)
            .push(resource_id);
    }

    /// Detect deadlock for a specific process
    pub fn detect_deadlock(&self, start_pid: u64) -> bool {
        let mut visited = Vec::new();
        self.detect_cycle(start_pid, &mut visited)
    }

    /// Detect cycle in wait-for graph using DFS
    fn detect_cycle(&self, current_pid: u64, visited: &mut Vec<u64>) -> bool {
        // If we've seen this process before, we have a cycle
        if visited.contains(&current_pid) {
            return true;
        }

        visited.push(current_pid);

        // Get resources this process is waiting for
        if let Some(waiting_resources) = self.process_to_resource.get(&current_pid) {
            for &resource_id in waiting_resources {
                // Get the process holding this resource
                if let Some(&holder_pid) = self.resource_to_process.get(&resource_id) {
                    // Recursively check if holder is in a cycle
                    if self.detect_cycle(holder_pid, visited) {
                        return true;
                    }
                }
            }
        }

        // Remove from visited (backtrack)
        visited.pop();
        false
    }

    /// Detect any deadlock in the system
    pub fn detect_any_deadlock(&self) -> Option<Vec<u64>> {
        // Check each process for deadlock
        for &pid in self.process_to_resource.keys() {
            let mut visited = Vec::new();
            if self.detect_cycle(pid, &mut visited) {
                return Some(visited);
            }
        }
        None
    }

    /// Get deadlock prevention recommendation
    pub fn get_deadlock_resolution(&self, deadlocked_processes: &[u64]) -> DeadlockResolution {
        if deadlocked_processes.is_empty() {
            return DeadlockResolution::None;
        }

        // Find process with lowest priority or least resources to abort
        let victim_pid = deadlocked_processes[0];

        DeadlockResolution::AbortProcess {
            victim_pid,
            reason: "Selected as victim for deadlock resolution".into(),
        }
    }

    /// Remove process from graph (cleanup)
    pub fn remove_process(&mut self, pid: u64) {
        // Remove from waiting lists
        self.process_to_resource.remove(&pid);

        // Release all resources held by this process
        let resources_to_release: Vec<u64> = self.resource_to_process
            .iter()
            .filter(|(_, &holder)| holder == pid)
            .map(|(&res_id, _)| res_id)
            .collect();

        for resource_id in resources_to_release {
            self.release_resource(pid, resource_id);
        }

        // Remove from all waiter lists
        for resource in self.resources.values_mut() {
            resource.waiters.retain(|&p| p != pid);
        }
    }
}

/// Deadlock resolution strategy
#[derive(Debug, Clone)]
pub enum DeadlockResolution {
    None,
    AbortProcess {
        victim_pid: u64,
        reason: alloc::string::String,
    },
    RollbackResource {
        resource_id: u64,
        process_id: u64,
    },
    PreemptResource {
        resource_id: u64,
        from_pid: u64,
        to_pid: u64,
    },
}

/// Global deadlock detector
pub static DEADLOCK_DETECTOR: Mutex<Option<WaitForGraph>> = Mutex::new(None);

/// Initialize deadlock detector
pub fn init_deadlock_detector() {
    let mut detector = DEADLOCK_DETECTOR.lock();
    *detector = Some(WaitForGraph::new());
}

/// Check for deadlock before acquiring resource
pub fn check_deadlock_before_acquire(pid: u64, resource_id: u64) -> Result<(), &'static str> {
    let mut detector = DEADLOCK_DETECTOR.lock();

    if let Some(ref mut graph) = *detector {
        // Temporarily add wait edge
        graph.wait_for_resource(pid, resource_id);

        // Check for deadlock
        if graph.detect_deadlock(pid) {
            // Remove wait edge
            if let Some(waiting) = graph.process_to_resource.get_mut(&pid) {
                waiting.retain(|&r| r != resource_id);
            }
            return Err("Deadlock detected - request denied");
        }

        // Safe to proceed - but don't keep the wait edge yet
        if let Some(waiting) = graph.process_to_resource.get_mut(&pid) {
            waiting.retain(|&r| r != resource_id);
        }
    }

    Ok(())
}

/// Register resource acquisition
pub fn register_resource_acquire(pid: u64, resource_id: u64) {
    let mut detector = DEADLOCK_DETECTOR.lock();

    if let Some(ref mut graph) = *detector {
        graph.acquire_resource(pid, resource_id);
    }
}

/// Register resource release
pub fn register_resource_release(pid: u64, resource_id: u64) {
    let mut detector = DEADLOCK_DETECTOR.lock();

    if let Some(ref mut graph) = *detector {
        graph.release_resource(pid, resource_id);
    }
}

/// Register new IPC resource
pub fn register_ipc_resource(resource_id: u64) {
    let mut detector = DEADLOCK_DETECTOR.lock();

    if let Some(ref mut graph) = *detector {
        graph.add_resource(resource_id);
    }
}

/// Cleanup process resources on termination
pub fn cleanup_process_deadlock_state(pid: u64) {
    let mut detector = DEADLOCK_DETECTOR.lock();

    if let Some(ref mut graph) = *detector {
        graph.remove_process(pid);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_deadlock_detection() {
        let mut graph = WaitForGraph::new();

        // Add resources
        graph.add_resource(1);
        graph.add_resource(2);

        // Process 1 holds resource 1, waits for resource 2
        graph.acquire_resource(1, 1);
        graph.wait_for_resource(1, 2);

        // Process 2 holds resource 2, waits for resource 1
        graph.acquire_resource(2, 2);
        graph.wait_for_resource(2, 1);

        // Should detect deadlock
        assert!(graph.detect_deadlock(1));
        assert!(graph.detect_deadlock(2));
    }

    #[test]
    fn test_no_deadlock() {
        let mut graph = WaitForGraph::new();

        // Add resources
        graph.add_resource(1);
        graph.add_resource(2);

        // Process 1 holds resource 1
        graph.acquire_resource(1, 1);

        // Process 2 waits for resource 1 (no cycle)
        graph.wait_for_resource(2, 1);

        // Should not detect deadlock
        assert!(!graph.detect_deadlock(2));
    }

    #[test]
    fn test_three_process_deadlock() {
        let mut graph = WaitForGraph::new();

        // Add resources
        graph.add_resource(1);
        graph.add_resource(2);
        graph.add_resource(3);

        // P1 holds R1, waits for R2
        graph.acquire_resource(1, 1);
        graph.wait_for_resource(1, 2);

        // P2 holds R2, waits for R3
        graph.acquire_resource(2, 2);
        graph.wait_for_resource(2, 3);

        // P3 holds R3, waits for R1
        graph.acquire_resource(3, 3);
        graph.wait_for_resource(3, 1);

        // All should detect deadlock
        assert!(graph.detect_deadlock(1));
        assert!(graph.detect_deadlock(2));
        assert!(graph.detect_deadlock(3));
    }
}
