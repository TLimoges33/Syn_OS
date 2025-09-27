//! Error module
//! 
//! Handles error utilities

use thiserror::Error;

/// Error representation
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

/// Result type alias
pub type Result<T> = std::result::Result<T, Error>;
