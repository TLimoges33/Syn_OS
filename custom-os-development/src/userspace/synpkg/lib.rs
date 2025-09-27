//! SynPkg - SynOS Consciousness-Aware Package Manager Library
//! 
//! This library provides the core functionality for the SynPkg package manager,
//! including consciousness-driven package recommendations, multi-repository support,
//! and advanced security validation.

pub mod core;
pub mod repository;
pub mod dependency;
pub mod cache;
pub mod consciousness;
pub mod security;

// Re-export main types for convenience
pub use core::{SynPkgManager, PackageInfo, SecurityRating, InstallStatus};
pub use repository::{Repository, RepositoryManager, PackageSource, RepositoryConfig};
pub use dependency::{DependencyResolver, DependencyResolution, DependencyTree};
pub use cache::{PackageCache, InstalledPackageRecord, CacheStats, CleanupResults};
pub use syn_ai::{ConsciousnessEngine, PackageRecommendation, InstallationContext};
pub use security::{SecurityValidator, SecurityValidationResult, Vulnerability, TrustLevel};

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// SynPkg error types
#[derive(Debug)]
pub enum SynPkgError {
    PackageNotFound {
        package: String,
    },
    RepositoryError {
        message: String,
    },
    DependencyError {
        message: String,
    },
    SecurityError {
        message: String,
    },
    CacheError {
        message: String,
    },
    ConsciousnessError {
        message: String,
    },
    ConfigError {
        message: String,
    },
    NetworkError {
        message: String,
    },
    IoError {
        source: std::io::Error,
    },
    JsonError {
        source: serde_json::Error,
    },
}/// Result type alias for SynPkg operations
pub type Result<T> = std::result::Result<T, SynPkgError>;

/// Initialize logging for SynPkg
pub fn init_logging() -> std::result::Result<(), Box<dyn std::error::Error>> {
    // Simple logging initialization
    Ok(())
}

/// Get SynPkg version information
pub fn version_info() -> String {
    let rustc_version = option_env!("RUSTC_VERSION").unwrap_or("unknown");
    let build_date = option_env!("BUILD_DATE").unwrap_or("unknown");
    
    format!(
        "SynPkg {} - SynOS Consciousness-Aware Package Manager\n\
         Built with Rust {} on {}",
        VERSION,
        rustc_version,
        build_date
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version_constant() {
        assert!(!VERSION.is_empty());
    }

    #[test]
    fn test_version_info() {
        let info = version_info();
        assert!(info.contains("SynPkg"));
        assert!(info.contains(VERSION));
    }
}
