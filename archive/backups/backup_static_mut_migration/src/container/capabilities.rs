/// Linux Capabilities Management
/// Fine-grained privilege control for containers

use alloc::vec::Vec;
use alloc::collections::BTreeSet;

/// Linux capabilities (subset)
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Capability {
    // File capabilities
    CAP_CHOWN,          // Make arbitrary changes to file UIDs and GIDs
    CAP_DAC_OVERRIDE,   // Bypass file read, write, and execute permission checks
    CAP_FOWNER,         // Bypass permission checks on operations that normally require the filesystem UID
    CAP_FSETID,         // Don't clear set-user-ID and set-group-ID mode bits

    // Process capabilities
    CAP_KILL,           // Bypass permission checks for sending signals
    CAP_SETGID,         // Make arbitrary manipulations of process GIDs
    CAP_SETUID,         // Make arbitrary manipulations of process UIDs
    CAP_SETPCAP,        // Modify process capabilities

    // Network capabilities
    CAP_NET_BIND_SERVICE,  // Bind a socket to privileged ports (< 1024)
    CAP_NET_RAW,           // Use RAW and PACKET sockets
    CAP_NET_ADMIN,         // Perform network administration tasks

    // System capabilities
    CAP_SYS_ADMIN,      // Perform system administration operations
    CAP_SYS_BOOT,       // Use reboot() and kexec_load()
    CAP_SYS_CHROOT,     // Use chroot()
    CAP_SYS_MODULE,     // Load and unload kernel modules
    CAP_SYS_NICE,       // Raise process nice value
    CAP_SYS_PTRACE,     // Trace arbitrary processes using ptrace()
    CAP_SYS_RESOURCE,   // Override resource limits
    CAP_SYS_TIME,       // Set system clock

    // Audit capabilities
    CAP_AUDIT_WRITE,    // Write records to kernel auditing log
    CAP_AUDIT_CONTROL,  // Enable and disable kernel auditing
}

/// Capability set manager
pub struct CapabilityManager {
    // Capabilities for each container
    container_caps: alloc::collections::BTreeMap<u64, CapabilitySet>,
}

/// Set of capabilities
#[derive(Debug, Clone)]
pub struct CapabilitySet {
    pub effective: BTreeSet<Capability>,
    pub permitted: BTreeSet<Capability>,
    pub inheritable: BTreeSet<Capability>,
}

impl CapabilityManager {
    pub fn new() -> Self {
        Self {
            container_caps: alloc::collections::BTreeMap::new(),
        }
    }

    /// Get default capabilities for containers (Docker default)
    pub fn get_default_caps(&self) -> CapabilitySet {
        let mut caps = BTreeSet::new();

        // Default container capabilities (safe subset)
        caps.insert(Capability::CAP_CHOWN);
        caps.insert(Capability::CAP_DAC_OVERRIDE);
        caps.insert(Capability::CAP_FOWNER);
        caps.insert(Capability::CAP_FSETID);
        caps.insert(Capability::CAP_KILL);
        caps.insert(Capability::CAP_SETGID);
        caps.insert(Capability::CAP_SETUID);
        caps.insert(Capability::CAP_NET_BIND_SERVICE);
        caps.insert(Capability::CAP_SYS_CHROOT);
        caps.insert(Capability::CAP_AUDIT_WRITE);

        CapabilitySet {
            effective: caps.clone(),
            permitted: caps.clone(),
            inheritable: BTreeSet::new(),
        }
    }

    /// Get minimal capabilities (most restricted)
    pub fn get_minimal_caps(&self) -> CapabilitySet {
        CapabilitySet {
            effective: BTreeSet::new(),
            permitted: BTreeSet::new(),
            inheritable: BTreeSet::new(),
        }
    }

    /// Apply capabilities to container
    pub fn apply_caps(
        &mut self,
        container_id: u64,
        caps: CapabilitySet,
    ) -> Result<(), &'static str> {
        // Real implementation would use capset() syscall
        self.container_caps.insert(container_id, caps);
        Ok(())
    }

    /// Drop specific capability
    pub fn drop_capability(
        &mut self,
        container_id: u64,
        cap: Capability,
    ) -> Result<(), &'static str> {
        let caps = self.container_caps.get_mut(&container_id)
            .ok_or("Container capabilities not found")?;

        caps.effective.remove(&cap);
        caps.permitted.remove(&cap);
        caps.inheritable.remove(&cap);

        Ok(())
    }

    /// Add specific capability
    pub fn add_capability(
        &mut self,
        container_id: u64,
        cap: Capability,
    ) -> Result<(), &'static str> {
        let caps = self.container_caps.get_mut(&container_id)
            .ok_or("Container capabilities not found")?;

        caps.effective.insert(cap);
        caps.permitted.insert(cap);

        Ok(())
    }

    /// Check if container has capability
    pub fn has_capability(&self, container_id: u64, cap: Capability) -> bool {
        if let Some(caps) = self.container_caps.get(&container_id) {
            caps.effective.contains(&cap)
        } else {
            false
        }
    }

    /// Get all dangerous capabilities (should be dropped)
    pub fn get_dangerous_caps(&self) -> Vec<Capability> {
        vec![
            Capability::CAP_SYS_ADMIN,
            Capability::CAP_SYS_MODULE,
            Capability::CAP_SYS_BOOT,
            Capability::CAP_SYS_PTRACE,
            Capability::CAP_SYS_TIME,
            Capability::CAP_NET_ADMIN,
            Capability::CAP_NET_RAW,
        ]
    }

    /// Drop all dangerous capabilities
    pub fn drop_dangerous_caps(&mut self, container_id: u64) -> Result<(), &'static str> {
        let dangerous = self.get_dangerous_caps();

        for cap in dangerous {
            let _ = self.drop_capability(container_id, cap);
        }

        Ok(())
    }

    /// Remove container capabilities
    pub fn remove_container(&mut self, container_id: u64) {
        self.container_caps.remove(&container_id);
    }
}

impl CapabilitySet {
    pub fn new() -> Self {
        Self {
            effective: BTreeSet::new(),
            permitted: BTreeSet::new(),
            inheritable: BTreeSet::new(),
        }
    }

    pub fn has_cap(&self, cap: Capability) -> bool {
        self.effective.contains(&cap)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_caps() {
        let manager = CapabilityManager::new();
        let caps = manager.get_default_caps();

        assert!(caps.effective.contains(&Capability::CAP_CHOWN));
        assert!(caps.effective.contains(&Capability::CAP_NET_BIND_SERVICE));
        assert!(!caps.effective.contains(&Capability::CAP_SYS_ADMIN));
    }

    #[test]
    fn test_dangerous_caps() {
        let manager = CapabilityManager::new();
        let dangerous = manager.get_dangerous_caps();

        assert!(dangerous.contains(&Capability::CAP_SYS_ADMIN));
        assert!(dangerous.contains(&Capability::CAP_SYS_MODULE));
    }

    #[test]
    fn test_cap_management() {
        let mut manager = CapabilityManager::new();
        let caps = manager.get_default_caps();

        manager.apply_caps(1, caps).unwrap();

        assert!(manager.has_capability(1, Capability::CAP_CHOWN));

        manager.drop_capability(1, Capability::CAP_CHOWN).unwrap();

        assert!(!manager.has_capability(1, Capability::CAP_CHOWN));
    }
}
