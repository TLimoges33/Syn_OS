//! # SynOS Service Integration Framework
//! 
//! This crate provides comprehensive service integration capabilities for SynOS,
//! including NATS messaging, service discovery, health monitoring, and authentication.

use std::fmt;

pub mod nats;
pub mod discovery;
pub mod health;
pub mod auth;
pub mod events;

pub use nats::NatsClient;
pub use discovery::{ServiceDiscovery, ServiceRegistration};
pub use health::{HealthMonitor, HealthChecker, ConnectivityChecker, DatabaseChecker, MemoryChecker};
pub use auth::{ServiceAuth, default_service_scopes, admin_service_scopes};
pub use events::{Event, EventType, EventPriority};

/// Service integration errors
#[derive(Debug, thiserror::Error)]
pub enum ServiceError {
    #[error("NATS connection error: {0}")]
    NatsError(String),
    
    #[error("Service discovery error: {0}")]
    DiscoveryError(String),
    
    #[error("Health monitoring error: {0}")]
    HealthError(String),
    
    #[error("Authentication error: {0}")]
    AuthError(String),
    
    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),
    
    #[error("Configuration error: {0}")]
    ConfigError(String),
    
    #[error("Timeout error: {0}")]
    TimeoutError(String),
}

/// Result type for service operations
pub type ServiceResult<T> = Result<T, ServiceError>;

/// Service configuration
#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct ServiceConfig {
    pub service_id: String,
    pub service_name: String,
    pub version: String,
    pub nats_url: String,
    pub nats_credentials: Option<NatsCredentials>,
    pub health_check_interval: std::time::Duration,
    pub service_timeout: std::time::Duration,
}

/// NATS credentials
#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct NatsCredentials {
    pub username: String,
    pub password: String,
}

impl Default for ServiceConfig {
    fn default() -> Self {
        Self {
            service_id: uuid::Uuid::new_v4().to_string(),
            service_name: "synos-service".to_string(),
            version: "1.0.0".to_string(),
            nats_url: "nats://localhost:4222".to_string(),
            nats_credentials: None,
            health_check_interval: std::time::Duration::from_secs(30),
            service_timeout: std::time::Duration::from_secs(10),
        }
    }
}

/// Service status enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Deserialize, serde::Serialize)]
pub enum ServiceStatus {
    Starting,
    Running,
    Stopping,
    Stopped,
    Failed,
    Unhealthy,
}

impl fmt::Display for ServiceStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ServiceStatus::Starting => write!(f, "starting"),
            ServiceStatus::Running => write!(f, "running"),
            ServiceStatus::Stopping => write!(f, "stopping"),
            ServiceStatus::Stopped => write!(f, "stopped"),
            ServiceStatus::Failed => write!(f, "failed"),
            ServiceStatus::Unhealthy => write!(f, "unhealthy"),
        }
    }
}
