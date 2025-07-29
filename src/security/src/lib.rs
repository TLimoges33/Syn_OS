pub mod auth;
pub mod crypto;
pub mod validation;
pub mod monitoring;
pub mod audit;

use core::sync::atomic::{AtomicBool, Ordering};

/// Global security subsystem state
static SECURITY_INITIALIZED: AtomicBool = AtomicBool::new(false);

/// Initialize the security subsystem
pub fn init() {
    println!("🔒 Initializing Security Subsystem...");
    
    // Initialize authentication
    auth::init();
    
    // Initialize cryptography
    crypto::init();
    
    // Initialize input validation
    validation::init();
    
    // Initialize monitoring
    monitoring::init();
    
    // Initialize audit logging
    audit::init();
    
    SECURITY_INITIALIZED.store(true, Ordering::SeqCst);
    println!("✅ Security Subsystem initialized");
}

/// Check if security subsystem is initialized
pub fn is_initialized() -> bool {
    SECURITY_INITIALIZED.load(Ordering::SeqCst)
}

/// Security levels for the system
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SecurityLevel {
    Public = 0,
    Restricted = 1,
    Confidential = 2,
    Secret = 3,
    TopSecret = 4,
}

/// Security context for operations
#[derive(Debug, Clone)]
pub struct SecurityContext {
    pub user_id: u32,
    pub process_id: u32,
    pub security_level: SecurityLevel,
    pub capabilities: Vec<Capability>,
    pub isolation_domain: String,
}

/// System capabilities
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Capability {
    ReadMemory,
    WriteMemory,
    ExecuteCode,
    NetworkAccess,
    FileSystemAccess,
    DeviceAccess,
    SystemCall,
    AdminAccess,
}

/// Validate security context for operation
pub fn validate_operation(context: &SecurityContext, required_capability: Capability) -> bool {
    if !is_initialized() {
        return false;
    }
    
    context.capabilities.contains(&required_capability)
}

/// Create a restricted security context
pub fn create_restricted_context(user_id: u32, process_id: u32) -> SecurityContext {
    SecurityContext {
        user_id,
        process_id,
        security_level: SecurityLevel::Restricted,
        capabilities: vec![Capability::ReadMemory, Capability::ExecuteCode],
        isolation_domain: format!("user_{}_process_{}", user_id, process_id),
    }
}
