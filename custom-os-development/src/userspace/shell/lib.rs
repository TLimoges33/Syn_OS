//! # SynShell Library
//! 
//! Library components for the SynOS Security-Focused Shell

#![no_std]

extern crate alloc;

use alloc::{string::{String, ToString}, vec::Vec, format};

// Re-export the main shell module
pub mod shell;
pub use shell::*;

// Stub implementations for now - these will be replaced with the actual module files
pub mod builtins_stub;
pub mod environment_stub;
pub mod external_stub;
pub mod history_stub;
pub mod parser_stub;

pub use builtins_stub::*;
pub use environment_stub::*;
pub use external_stub::*;
pub use history_stub::*;
pub use parser_stub::*;
