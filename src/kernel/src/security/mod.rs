/// Security Framework for SynOS Kernel
/// Provides comprehensive security context and enforcement

pub mod hardening;
pub mod access_control;
pub mod threat_detection;
pub mod crypto;
pub mod audit;

// Re-export existing security components
pub mod interrupt_security;
pub mod memory_corruption;
pub mod stack_protection;

// Additional security modules
pub mod monitoring;
pub mod encryption;

use alloc::string::String;
use alloc::vec::Vec;
use core::sync::atomic::{AtomicBool, AtomicU64, Ordering};

// Re-export key types
pub use hardening::{SystemHardening, HardeningConfig};
pub use threat_detection::{ThreatDetector, ThreatType, ThreatAlert};
pub use access_control::{AccessController, AccessPolicy};

/// Security configuration
#[derive(Debug, Clone)]
pub struct SecurityConfig {
    pub hardening_enabled: bool,
    pub threat_detection_enabled: bool,
    pub audit_logging_enabled: bool,
    pub crypto_acceleration: bool,
    pub access_control_enabled: bool,
    pub monitoring_enabled: bool,
    pub security_level: SecurityLevel,
}

/// Security level
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub enum SecurityLevel {
    Public = 0,
    Basic = 1,
    Enhanced = 2,
    Paranoid = 3,
    Maximum = 4,
    Internal = 5,
    Confidential = 6,
    Secret = 7,
    TopSecret = 8,
}

/// Security event
#[derive(Debug, Clone)]
pub struct SecurityEvent {
    pub event_id: u64,
    pub event_type: SecurityEventType,
    pub severity: SecuritySeverity,
    pub source: String,
    pub timestamp: u64,
    pub description: String,
    pub data: Vec<u8>,
}

/// Security event types
#[derive(Debug, Clone, PartialEq)]
pub enum SecurityEventType {
    AccessViolation,
    PrivilegeEscalation,
    UnauthorizedAccess,
    ThreatDetected,
    PolicyViolation,
    CryptoFailure,
    AuditFailure,
    SystemCompromise,
}

/// Security severity levels
#[derive(Debug, Clone, Copy, PartialEq, Ord, PartialOrd, Eq)]
pub enum SecuritySeverity {
    Info = 1,
    Warning = 2,
    Critical = 3,
    Emergency = 4,
}

/// Security policy
#[derive(Debug, Clone)]
pub struct SecurityPolicy {
    pub policy_id: u32,
    pub policy_name: String,
    pub policy_type: PolicyType,
    pub enabled: bool,
    pub enforcement_level: EnforcementLevel,
}

/// Policy types
#[derive(Debug, Clone, PartialEq)]
pub enum PolicyType {
    AccessControl,
    DataProtection,
    NetworkSecurity,
    SystemHardening,
    AuditPolicy,
    CryptoPolicy,
}

/// Enforcement levels
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum EnforcementLevel {
    Advisory,
    Warning,
    Blocking,
    Terminating,
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            hardening_enabled: true,
            threat_detection_enabled: true,
            audit_logging_enabled: true,
            crypto_acceleration: true,
            access_control_enabled: true,
            monitoring_enabled: true,
            security_level: SecurityLevel::Enhanced,
        }
    }
}

/// Security context for processes and resources
#[derive(Debug, Clone)]
pub struct SecurityContext {
    pub user_id: u64,
    pub group_id: u64,
    pub capabilities: Vec<SecurityCapability>,
    pub security_level: SecurityLevel,
    pub trusted: bool,
}

/// Security capabilities that can be granted to processes
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SecurityCapability {
    FileRead,
    FileWrite,
    FileExecute,
    NetworkAccess,
    SystemCall,
    ProcessControl,
    MemoryAccess,
    DeviceAccess,
    SecurityAdmin,
}

impl Default for SecurityContext {
    fn default() -> Self {
        Self {
            user_id: 1000, // Default user
            group_id: 1000, // Default group
            capabilities: Vec::new(),
            security_level: SecurityLevel::Public,
            trusted: false,
        }
    }
}

impl SecurityContext {
    /// Create a new security context
    pub fn new(user_id: u64, group_id: u64) -> Self {
        Self {
            user_id,
            group_id,
            capabilities: Vec::new(),
            security_level: SecurityLevel::Public,
            trusted: false,
        }
    }

    /// Add a capability to the security context
    pub fn add_capability(&mut self, capability: SecurityCapability) {
        if !self.capabilities.contains(&capability) {
            self.capabilities.push(capability);
        }
    }

    /// Check if context has a specific capability
    pub fn has_capability(&self, capability: SecurityCapability) -> bool {
        self.capabilities.contains(&capability)
    }

    /// Set security level
    pub fn set_security_level(&mut self, level: SecurityLevel) {
        self.security_level = level;
    }

    /// Set trusted status
    pub fn set_trusted(&mut self, trusted: bool) {
        self.trusted = trusted;
    }
}

/// Security manager for kernel-level security enforcement
pub struct SecurityManager {
    default_context: SecurityContext,
    enforcement_enabled: bool,
}

impl SecurityManager {
    /// Create a new security manager
    pub fn new() -> Self {
        Self {
            default_context: SecurityContext::default(),
            enforcement_enabled: true,
        }
    }

    /// Validate access request
    pub fn validate_access(
        &self,
        context: &SecurityContext,
        required_capability: SecurityCapability,
        required_level: SecurityLevel,
    ) -> bool {
        if !self.enforcement_enabled {
            return true;
        }

        // Check capability
        if !context.has_capability(required_capability) {
            return false;
        }

        // Check security level
        if context.security_level < required_level {
            return false;
        }

        true
    }

    /// Get default security context
    pub fn get_default_context(&self) -> &SecurityContext {
        &self.default_context
    }
}

/// Global security manager instance
static mut SECURITY_MANAGER: Option<SecurityManager> = None;

/// Initialize the security manager
pub fn init_security_manager() {
    unsafe {
        SECURITY_MANAGER = Some(SecurityManager::new());
    }
}

/// Get the global security manager
pub fn get_security_manager() -> Option<&'static SecurityManager> {
    unsafe { SECURITY_MANAGER.as_ref() }
}

// Security tests
#[cfg(test)]
mod tests;
