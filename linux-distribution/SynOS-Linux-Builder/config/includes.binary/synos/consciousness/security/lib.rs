//! Syn_OS Security Framework
//! 
//! This module provides the security framework for Syn_OS,
//! implementing authentication, cryptography, audit logging,
//! and input validation.

pub mod audit;
pub mod auth;
pub mod consciousness_bridge;
pub mod crypto;
pub mod ebpf_integration;
pub mod encryption;
pub mod enhanced_monitoring_minimal;
pub mod quantum_auth;
pub mod validation;
pub mod zero_trust;

// Re-export commonly used items
// TODO: Enable these exports once the functions are properly implemented
// pub use auth::{authenticate, AuthenticationError, AuthenticationResult};
// pub use crypto::{encrypt, decrypt, CryptoError};
// pub use audit::{log_event, AuditLevel};
// pub use validation::{validate_input, ValidationError};

pub use audit::AuditLevel;
pub use crypto::CryptoError;
pub use validation::ValidationError;

/// Security framework version
pub const VERSION: &str = "4.3.0";

/// Get current timestamp (simplified for development)
pub fn get_kernel_timestamp() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

/// Initialize the security framework
pub fn init() {
    println!("Initializing Syn_OS Security Framework v{}", VERSION);
    
    // Initialize components
    auth::init();
    crypto::init();
    audit::init();
    validation::init();
    consciousness_bridge::init();
    
    println!("Security Framework initialization complete.");
}
