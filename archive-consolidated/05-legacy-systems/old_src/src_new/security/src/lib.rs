//! Syn_OS Security Framework
//! 
//! This module provides the security framework for Syn_OS,
//! implementing authentication, cryptography, audit logging,
//! and input validation.

pub mod auth;
pub mod crypto;
pub mod audit;
pub mod validation;
pub mod consciousness_bridge;

// Re-export commonly used items
pub use auth::{authenticate, AuthenticationError, AuthenticationResult};
pub use crypto::{encrypt, decrypt, CryptoError};
pub use audit::{log_event, AuditLevel};
pub use validation::{validate_input, ValidationError};

/// Security framework version
pub const VERSION: &str = "4.3.0";

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
