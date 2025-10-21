//! Syn_OS Common Utilities
//!
//! This module provides common utilities used across the Syn_OS project.

pub mod config;
pub mod error;
pub mod logging;
pub mod metrics;
pub mod performance_minimal;

// Re-export commonly used items
pub use logging::Logger;
pub use config::Config;
pub use error::Error;

/// Common utilities version
pub const VERSION: &str = "4.5.0";

/// Initialize the common utilities
pub fn init() {
    println!("Initializing Syn_OS Common Utilities v{}", VERSION);

    // Initialize components
    logging::init();
    config::init();

    println!("Common Utilities initialization complete.");
}
