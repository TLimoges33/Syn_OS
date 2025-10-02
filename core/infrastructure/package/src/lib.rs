pub mod core;
pub mod dependency;
pub mod install;
pub mod repository;
pub mod security;
pub mod consciousness;
pub mod cli;

// Re-export main types
pub use core::{Package, PackageManager, PackageSource, PackageStatus};
pub use dependency::DependencyResolver;
pub use install::InstallationEngine;
pub use repository::RepositoryManager;
pub use security::SecurityValidator;
pub use consciousness::ConsciousnessIntegration;

/// Main result type for the package manager
pub type Result<T> = std::result::Result<T, PackageManagerError>;

/// Core error types for the package manager
#[derive(Debug, thiserror::Error)]
pub enum PackageManagerError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    
    #[error("Network error: {0}")]
    Network(#[from] reqwest::Error),
    
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Dependency conflict: {message}")]
    DependencyConflict { message: String },
    
    #[error("Security validation failed: {reason}")]
    SecurityValidation { reason: String },
    
    #[error("Package not found: {package}")]
    PackageNotFound { package: String },
    
    #[error("Installation failed: {package} - {reason}")]
    InstallationFailed { package: String, reason: String },
    
    #[error("Consciousness integration error: {message}")]
    ConsciousnessError { message: String },
    
    #[error("Configuration error: {message}")]
    Config { message: String },
    
    #[error("Permission denied: {action}")]
    PermissionDenied { action: String },
}

/// Performance metrics for package operations
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct PerformanceMetrics {
    pub operation: String,
    pub duration_ms: u64,
    pub memory_used_mb: u64,
    pub packages_processed: usize,
    pub cache_hit_ratio: f32,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// High-level package manager configuration
#[derive(Debug, Clone, serde::Deserialize)]
pub struct PackageManagerConfig {
    pub database_path: String,
    pub cache_dir: String,
    pub download_dir: String,
    pub max_parallel_downloads: usize,
    pub max_parallel_installs: usize,
    pub enable_consciousness: bool,
    pub security_level: SecurityLevel,
    pub repositories: Vec<RepositoryConfig>,
}

#[derive(Debug, Clone, serde::Deserialize)]
pub struct RepositoryConfig {
    pub name: String,
    pub url: String,
    pub source_type: String,
    pub priority: i32,
    pub enabled: bool,
    pub gpg_key: Option<String>,
}

#[derive(Debug, Clone, serde::Deserialize)]
pub enum SecurityLevel {
    Minimal,
    Standard,
    Enhanced,
    Paranoid,
}

impl Default for PackageManagerConfig {
    fn default() -> Self {
        let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
        Self {
            database_path: format!("{}/.synos/packages.db", home),
            cache_dir: format!("{}/.synos/cache", home),
            download_dir: format!("{}/.synos/downloads", home),
            max_parallel_downloads: 4,
            max_parallel_installs: 2,
            enable_consciousness: true,
            security_level: SecurityLevel::Enhanced,
            repositories: vec![
                RepositoryConfig {
                    name: "synos-main".to_string(),
                    url: "https://packages.synos.dev/main".to_string(),
                    source_type: "synos".to_string(),
                    priority: 100,
                    enabled: true,
                    gpg_key: Some("synos-main.gpg".to_string()),
                },
                RepositoryConfig {
                    name: "ubuntu-main".to_string(),
                    url: "http://archive.ubuntu.com/ubuntu".to_string(),
                    source_type: "apt".to_string(),
                    priority: 50,
                    enabled: true,
                    gpg_key: None,
                },
            ],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_default_config() {
        let config = PackageManagerConfig::default();
        assert!(config.enable_consciousness);
        assert_eq!(config.max_parallel_downloads, 4);
        assert!(!config.repositories.is_empty());
    }
}
