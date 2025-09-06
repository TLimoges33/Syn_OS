//! Security module error types
//! 
//! This module provides error handling for security operations in a no-std environment.

use core::fmt;

/// Result type for security operations
pub type SecurityResult<T> = Result<T, SecurityError>;

/// Security operation errors
#[derive(Debug, Clone)]
pub enum SecurityError {
    /// Authentication failed
    AuthenticationFailed,
    /// Authorization denied
    AuthorizationDenied,
    /// Cryptographic operation failed
    CryptographicError,
    /// Invalid input data
    InvalidInput,
    /// Key generation failed
    KeyGenerationFailed,
    /// Validation failed
    ValidationFailed,
    /// Insufficient entropy
    InsufficientEntropy,
    /// Resource exhausted
    ResourceExhausted,
    /// Unknown error with message
    Unknown(&'static str),
}

impl fmt::Display for SecurityError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SecurityError::AuthenticationFailed => write!(f, "Authentication failed"),
            SecurityError::AuthorizationDenied => write!(f, "Authorization denied"),
            SecurityError::CryptographicError => write!(f, "Cryptographic operation failed"),
            SecurityError::InvalidInput => write!(f, "Invalid input data"),
            SecurityError::KeyGenerationFailed => write!(f, "Key generation failed"),
            SecurityError::ValidationFailed => write!(f, "Validation failed"),
            SecurityError::InsufficientEntropy => write!(f, "Insufficient entropy"),
            SecurityError::ResourceExhausted => write!(f, "Resource exhausted"),
            SecurityError::Unknown(msg) => write!(f, "Unknown error: {}", msg),
        }
    }
}

impl From<&'static str> for SecurityError {
    fn from(msg: &'static str) -> Self {
        SecurityError::Unknown(msg)
    }
}

// Macro to create errors easily
#[macro_export]
macro_rules! security_error {
    ($msg:expr) => {
        $crate::error::SecurityError::Unknown($msg)
    };
}
