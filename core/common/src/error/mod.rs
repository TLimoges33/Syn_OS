//! Error module
//! 
//! Handles error utilities

#[cfg(feature = "std")]
use thiserror::Error;

/// Error representation
#[cfg(feature = "std")]
#[derive(Error, Debug)]
pub enum Error {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    
    #[error("Configuration error: {0}")]
    Configuration(String),
    
    #[error("Network error: {0}")]
    Network(String),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// No-std compatible error type
#[cfg(not(feature = "std"))]
#[derive(Debug)]
pub enum Error {
    Configuration(&'static str),
    Network(&'static str),
    Unknown(&'static str),
}

/// Result type alias
pub type Result<T> = std::result::Result<T, Error>;
