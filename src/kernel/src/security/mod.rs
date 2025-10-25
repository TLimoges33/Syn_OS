pub mod access_control;
pub mod audit;
pub mod crypto;
/// Security Framework for SynOS Kernel
/// Provides comprehensive security context and enforcement
pub mod hardening;
pub mod threat_detection;

// Re-export existing security components
pub mod interrupt_security;
pub mod memory_corruption;
pub mod stack_protection;

// Additional security modules
pub mod encryption;
pub mod monitoring;

// Newly organized modules
pub mod verification;
pub mod security_panic;
pub mod pqc;

// Phase 5b: Real-Time Threat Response
pub mod realtime;

// Phase 7c: Post-Quantum Cryptography
pub mod post_quantum;

use alloc::string::String;
use alloc::vec::Vec;
use core::sync::atomic::{AtomicBool, AtomicU64, Ordering};

// Re-export key types
pub use access_control::{AccessController, AccessPolicy};
pub use hardening::{HardeningConfig, SystemHardening};
pub use threat_detection::{ThreatAlert, ThreatDetector, ThreatType};

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
            user_id: 1000,  // Default user
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
lazy_static! {
    static ref SECURITY_MANAGER: Mutex<SecurityManager> = Mutex::new(SecurityManager::new());
}

/// Initialize the security manager (for compatibility)
pub fn init_security_manager() {
    // Already initialized via lazy_static
}

/// Get the global security manager (lock-based access)
pub fn with_security_manager<F, R>(f: F) -> R
where
    F: FnOnce(&SecurityManager) -> R,
{
    let manager = SECURITY_MANAGER.lock();
    f(&manager)
}

// Syscall support functions for threat detection
use spin::Mutex;
use lazy_static::lazy_static;

// Global threat detection state
static THREAT_DETECTIONS: AtomicU64 = AtomicU64::new(0);
static EDUCATIONAL_MODE: AtomicBool = AtomicBool::new(false);

lazy_static! {
    static ref THREAT_PATTERNS: Mutex<Vec<(String, Vec<u8>)>> = Mutex::new(Vec::new());
}

/// Analyze memory region for threats
pub fn analyze_memory_threats(addr: usize, size: usize) -> Result<u8, &'static str> {
    if addr == 0 || size == 0 {
        return Err("Invalid memory region");
    }

    // Basic memory safety checks
    let threat_level = unsafe {
        // Check for common threat patterns in memory
        let ptr = addr as *const u8;
        let slice = core::slice::from_raw_parts(ptr, core::cmp::min(size, 256));

        // Look for suspicious patterns
        let mut suspicion = 0u8;

        // Check for shellcode-like patterns
        if slice.windows(3).any(|w| w == [0x90, 0x90, 0x90]) {  // NOP sled
            suspicion = 2;
        }

        // Check for format string vulnerabilities
        if slice.windows(2).any(|w| w == b"%s" || w == b"%n") {
            suspicion = suspicion.max(1);
        }

        suspicion
    };

    if threat_level > 0 {
        THREAT_DETECTIONS.fetch_add(1, Ordering::Relaxed);
    }

    Ok(threat_level)
}

/// Get number of detected threats
pub fn get_threat_count() -> usize {
    THREAT_DETECTIONS.load(Ordering::Relaxed) as usize
}

/// Get number of loaded threat patterns
pub fn get_pattern_count() -> usize {
    THREAT_PATTERNS.lock().len()
}

/// Add custom threat pattern
pub fn add_threat_pattern(name: &str, signature: &[u8]) -> Result<u32, &'static str> {
    if name.is_empty() || signature.is_empty() {
        return Err("Invalid pattern");
    }

    let mut patterns = THREAT_PATTERNS.lock();
    let pattern_id = patterns.len() as u32;
    patterns.push((String::from(name), signature.to_vec()));

    Ok(pattern_id)
}

/// Enable educational mode for threat detection
pub fn enable_educational_mode() -> Result<(), &'static str> {
    EDUCATIONAL_MODE.store(true, Ordering::Relaxed);
    Ok(())
}

/// Get threat detection statistics
pub fn get_threat_statistics() -> (u32, u32) {
    let pattern_count = get_pattern_count() as u32;
    let threats_detected = THREAT_DETECTIONS.load(Ordering::Relaxed) as u32;
    (pattern_count, threats_detected)
}

/// Update threat pattern fitness (Neural Darwinism integration)
pub fn update_pattern_fitness(threat_type: u8) -> Result<(), &'static str> {
    if threat_type >= 10 {
        return Err("Invalid threat type");
    }

    // In real implementation, would update neural fitness scores
    // For now, just validate the threat type
    Ok(())
}

// Security tests
#[cfg(test)]
mod tests;
