//! # System Utilities for SynOS
//! 
//! Core system utilities including ps, ls, cat, grep, and other essential commands

pub mod ps;
pub mod ls;
pub mod cat;
pub mod grep;
pub mod netstat;
pub mod ping;
pub mod tcpdump;
pub mod enhanced_utilities;
pub mod consciousness_integration;

// Re-export utilities
pub use ps::PsCommand;
pub use ls::LsCommand;
pub use cat::CatCommand;
pub use grep::GrepCommand;
pub use netstat::NetstatCommand;
pub use ping::PingCommand;
pub use tcpdump::TcpdumpCommand;

// Re-export enhanced utilities
pub use enhanced_utilities::{FileUtils, SystemUtils, NetworkUtils, TextUtils};
pub use consciousness_integration::ConsciousnessIntegrationManager;
