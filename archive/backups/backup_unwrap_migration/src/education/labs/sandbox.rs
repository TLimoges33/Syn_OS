/// Sandbox Manager for Safe Lab Execution
/// Provides isolated environments for educational labs

use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Sandbox configuration
#[derive(Debug, Clone)]
pub struct SandboxConfig {
    pub max_memory_mb: u64,
    pub max_cpu_percent: u8,
    pub network_enabled: bool,
    pub filesystem_isolation: bool,
    pub time_limit_secs: u64,
}

impl Default for SandboxConfig {
    fn default() -> Self {
        Self {
            max_memory_mb: 512,
            max_cpu_percent: 50,
            network_enabled: true,
            filesystem_isolation: true,
            time_limit_secs: 3600, // 1 hour
        }
    }
}

/// Sandbox instance
#[derive(Debug)]
pub struct Sandbox {
    pub sandbox_id: u64,
    pub student_id: u64,
    pub lab_id: u64,
    pub config: SandboxConfig,
    pub processes: Vec<u64>, // PIDs running in sandbox
    pub start_time: u64,
    pub memory_used_mb: u64,
    pub cpu_usage_percent: u8,
}

/// Sandbox manager
pub struct SandboxManager {
    sandboxes: BTreeMap<u64, Sandbox>,
    next_sandbox_id: u64,
    student_sandboxes: BTreeMap<u64, Vec<u64>>, // student_id -> sandbox_ids
}

impl SandboxManager {
    /// Create new sandbox manager
    pub fn new() -> Self {
        Self {
            sandboxes: BTreeMap::new(),
            next_sandbox_id: 1,
            student_sandboxes: BTreeMap::new(),
        }
    }

    /// Create sandbox for lab
    pub fn create_sandbox(&mut self, student_id: u64, lab_id: u64) -> Result<u64, &'static str> {
        let sandbox_id = self.next_sandbox_id;
        self.next_sandbox_id += 1;

        let sandbox = Sandbox {
            sandbox_id,
            student_id,
            lab_id,
            config: SandboxConfig::default(),
            processes: Vec::new(),
            start_time: 0, // Would use actual timestamp
            memory_used_mb: 0,
            cpu_usage_percent: 0,
        };

        self.sandboxes.insert(sandbox_id, sandbox);

        // Track student's sandboxes
        self.student_sandboxes.entry(student_id)
            .or_insert_with(Vec::new)
            .push(sandbox_id);

        // Initialize isolated environment
        self.setup_isolation(sandbox_id)?;

        Ok(sandbox_id)
    }

    /// Setup sandbox isolation
    fn setup_isolation(&mut self, sandbox_id: u64) -> Result<(), &'static str> {
        let _sandbox = self.sandboxes.get(&sandbox_id)
            .ok_or("Sandbox not found")?;

        // Real implementation would:
        // 1. Create Linux namespaces (PID, NET, MNT, UTS, IPC)
        // 2. Setup cgroups for resource limits
        // 3. Create chroot environment
        // 4. Configure seccomp filters
        // 5. Setup network namespace

        Ok(())
    }

    /// Destroy sandbox
    pub fn destroy_sandbox(&mut self, student_id: u64, lab_id: u64) -> Result<(), &'static str> {
        // Find sandbox
        let sandbox_id = self.sandboxes.iter()
            .find(|(_, s)| s.student_id == student_id && s.lab_id == lab_id)
            .map(|(id, _)| *id)
            .ok_or("Sandbox not found")?;

        // Cleanup processes
        self.cleanup_processes(sandbox_id)?;

        // Remove sandbox
        self.sandboxes.remove(&sandbox_id);

        // Remove from student tracking
        if let Some(sandboxes) = self.student_sandboxes.get_mut(&student_id) {
            sandboxes.retain(|id| *id != sandbox_id);
        }

        Ok(())
    }

    /// Cleanup processes in sandbox
    fn cleanup_processes(&mut self, sandbox_id: u64) -> Result<(), &'static str> {
        let sandbox = self.sandboxes.get(&sandbox_id)
            .ok_or("Sandbox not found")?;

        // Real implementation would terminate all processes
        for _pid in &sandbox.processes {
            // Send SIGKILL to each process
        }

        Ok(())
    }

    /// Execute command in sandbox
    pub fn execute_in_sandbox(&mut self, sandbox_id: u64, command: &str) -> Result<u64, &'static str> {
        let sandbox = self.sandboxes.get_mut(&sandbox_id)
            .ok_or("Sandbox not found")?;

        // Real implementation would:
        // 1. Fork process in sandbox namespaces
        // 2. Apply resource limits
        // 3. Execute command
        // 4. Track PID

        let pid = 1000 + sandbox_id; // Mock PID
        sandbox.processes.push(pid);

        Ok(pid)
    }

    /// Check sandbox resource usage
    pub fn check_resources(&mut self, sandbox_id: u64) -> Result<SandboxResources, &'static str> {
        let sandbox = self.sandboxes.get(&sandbox_id)
            .ok_or("Sandbox not found")?;

        Ok(SandboxResources {
            memory_used_mb: sandbox.memory_used_mb,
            memory_limit_mb: sandbox.config.max_memory_mb,
            cpu_usage_percent: sandbox.cpu_usage_percent,
            cpu_limit_percent: sandbox.config.max_cpu_percent,
            runtime_secs: 0, // Would calculate from start_time
            time_limit_secs: sandbox.config.time_limit_secs,
        })
    }

    /// Enforce resource limits
    pub fn enforce_limits(&mut self, sandbox_id: u64) -> Result<(), &'static str> {
        let sandbox = self.sandboxes.get_mut(&sandbox_id)
            .ok_or("Sandbox not found")?;

        // Check memory limit
        if sandbox.memory_used_mb > sandbox.config.max_memory_mb {
            return Err("Memory limit exceeded");
        }

        // Check CPU limit
        if sandbox.cpu_usage_percent > sandbox.config.max_cpu_percent {
            // Throttle processes
            self.throttle_processes(sandbox_id)?;
        }

        Ok(())
    }

    /// Throttle processes in sandbox
    fn throttle_processes(&mut self, _sandbox_id: u64) -> Result<(), &'static str> {
        // Real implementation would use cgroups to limit CPU
        Ok(())
    }

    /// Get active sandbox count
    pub fn active_count(&self) -> usize {
        self.sandboxes.len()
    }

    /// Get student's sandboxes
    pub fn get_student_sandboxes(&self, student_id: u64) -> Vec<u64> {
        self.student_sandboxes.get(&student_id)
            .cloned()
            .unwrap_or_default()
    }
}

/// Sandbox resource usage
#[derive(Debug, Clone)]
pub struct SandboxResources {
    pub memory_used_mb: u64,
    pub memory_limit_mb: u64,
    pub cpu_usage_percent: u8,
    pub cpu_limit_percent: u8,
    pub runtime_secs: u64,
    pub time_limit_secs: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sandbox_creation() {
        let mut manager = SandboxManager::new();

        let sandbox_id = manager.create_sandbox(1, 100);
        assert!(sandbox_id.is_ok());
    }

    #[test]
    fn test_sandbox_destruction() {
        let mut manager = SandboxManager::new();

        let _sandbox_id = manager.create_sandbox(1, 100).unwrap();
        assert!(manager.destroy_sandbox(1, 100).is_ok());
        assert_eq!(manager.active_count(), 0);
    }

    #[test]
    fn test_command_execution() {
        let mut manager = SandboxManager::new();

        let sandbox_id = manager.create_sandbox(1, 100).unwrap();
        let pid = manager.execute_in_sandbox(sandbox_id, "ls -la");

        assert!(pid.is_ok());
    }

    #[test]
    fn test_resource_limits() {
        let mut manager = SandboxManager::new();

        let sandbox_id = manager.create_sandbox(1, 100).unwrap();
        let resources = manager.check_resources(sandbox_id);

        assert!(resources.is_ok());
    }
}
