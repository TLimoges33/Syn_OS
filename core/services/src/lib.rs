//! # SynOS Service Integration Framework
//!
//! Provides comprehensive service integration capabilities for SynOS,
//! including NATS messaging, service discovery, health monitoring, and authentication.

use std::fmt;
use uuid::Uuid;

/// Service configuration
#[derive(Debug, Clone)]
pub struct ServiceConfig {
    pub name: String,
    pub port: u16,
    pub host: String,
    pub service_id: String,
    pub service_name: String,
    pub version: String,
    pub nats_url: String,
    pub nats_credentials: Option<String>,
    pub health_check_interval: std::time::Duration,
    pub service_timeout: std::time::Duration,
}

impl Default for ServiceConfig {
    fn default() -> Self {
        Self {
            name: "synos-service".to_string(),
            port: 8080,
            host: "localhost".to_string(),
            service_id: Uuid::new_v4().to_string(),
            service_name: "synos-service".to_string(),
            version: "1.0.0".to_string(),
            nats_url: "nats://localhost:4222".to_string(),
            nats_credentials: None,
            health_check_interval: std::time::Duration::from_secs(30),
            service_timeout: std::time::Duration::from_secs(60),
        }
    }
}

/// Service status
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum ServiceStatus {
    Healthy,
    Unhealthy,
    Degraded,
    Unknown,
    Starting,
    Running,
    Stopped,
    Failed,
}

impl fmt::Display for ServiceStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ServiceStatus::Healthy => write!(f, "Healthy"),
            ServiceStatus::Unhealthy => write!(f, "Unhealthy"),
            ServiceStatus::Degraded => write!(f, "Degraded"),
            ServiceStatus::Unknown => write!(f, "Unknown"),
            ServiceStatus::Starting => write!(f, "Starting"),
            ServiceStatus::Running => write!(f, "Running"),
            ServiceStatus::Stopped => write!(f, "Stopped"),
            ServiceStatus::Failed => write!(f, "Failed"),
        }
    }
}

/// Service error type
#[derive(Debug)]
pub enum ServiceError {
    ConnectionFailed(String),
    Timeout(String),
    InvalidConfig(String),
    OperationFailed(String),
    NatsError(String),
    AuthError(String),
    TimeoutError(String),
}

impl std::error::Error for ServiceError {}

impl fmt::Display for ServiceError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ServiceError::ConnectionFailed(msg) => write!(f, "Connection failed: {}", msg),
            ServiceError::Timeout(msg) => write!(f, "Timeout: {}", msg),
            ServiceError::InvalidConfig(msg) => write!(f, "Invalid config: {}", msg),
            ServiceError::OperationFailed(msg) => write!(f, "Operation failed: {}", msg),
            ServiceError::NatsError(msg) => write!(f, "NATS error: {}", msg),
            ServiceError::AuthError(msg) => write!(f, "Authentication error: {}", msg),
            ServiceError::TimeoutError(msg) => write!(f, "Timeout error: {}", msg),
        }
    }
}

// From implementations for automatic error conversion
impl From<serde_json::Error> for ServiceError {
    fn from(err: serde_json::Error) -> Self {
        ServiceError::OperationFailed(format!("JSON error: {}", err))
    }
}

impl From<tokio::time::error::Elapsed> for ServiceError {
    fn from(err: tokio::time::error::Elapsed) -> Self {
        ServiceError::TimeoutError(format!("Operation timed out: {}", err))
    }
}

impl From<async_nats::ConnectError> for ServiceError {
    fn from(err: async_nats::ConnectError) -> Self {
        ServiceError::NatsError(format!("NATS connection error: {}", err))
    }
}

impl From<async_nats::PublishError> for ServiceError {
    fn from(err: async_nats::PublishError) -> Self {
        ServiceError::NatsError(format!("NATS publish error: {}", err))
    }
}

impl From<async_nats::SubscribeError> for ServiceError {
    fn from(err: async_nats::SubscribeError) -> Self {
        ServiceError::NatsError(format!("NATS subscribe error: {}", err))
    }
}

/// Service result type
pub type ServiceResult<T> = Result<T, ServiceError>;

pub mod nats;
pub mod discovery;
pub mod health;
pub mod auth;
pub mod events;

/// Performance monitoring (inline implementation)
pub mod performance_monitoring {
    //! Service performance monitoring and metrics collection

    use std::collections::HashMap;
    use std::sync::Arc;
    use tokio::sync::RwLock;
    use std::sync::LazyLock;

    /// Performance metrics for a service
    #[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
    pub struct PerformanceMetrics {
        pub cpu_usage: f64,
        pub memory_usage: f64,
        pub request_count: u64,
        pub error_count: u64,
        pub average_response_time: f64,
        pub timestamp: chrono::DateTime<chrono::Utc>,
    }

    impl Default for PerformanceMetrics {
        fn default() -> Self {
            Self {
                cpu_usage: 0.0,
                memory_usage: 0.0,
                request_count: 0,
                error_count: 0,
                average_response_time: 0.0,
                timestamp: chrono::Utc::now(),
            }
        }
    }

    /// Performance monitoring system
    pub struct PerformanceMonitor {
        metrics: Arc<RwLock<HashMap<String, PerformanceMetrics>>>,
    }

    impl PerformanceMonitor {
        pub fn new() -> Self {
            Self {
                metrics: Arc::new(RwLock::new(HashMap::new())),
            }
        }

        pub async fn record_metric(&self, service_id: String, metrics: PerformanceMetrics) {
            let mut m = self.metrics.write().await;
            m.insert(service_id, metrics);
        }

        pub async fn get_metrics(&self, service_id: &str) -> Option<PerformanceMetrics> {
            let m = self.metrics.read().await;
            m.get(service_id).cloned()
        }
    }

    impl Default for PerformanceMonitor {
        fn default() -> Self {
            Self::new()
        }
    }

    /// Global performance monitor instance
    pub static PERFORMANCE_MONITOR: LazyLock<PerformanceMonitor> =
        LazyLock::new(|| PerformanceMonitor::new());
}

/// Scalability framework for horizontal service scaling
pub mod scalability {
    use std::collections::HashMap;
    use std::sync::Arc;
    use tokio::sync::RwLock;
    use std::time::Duration;

    /// Service instance for load balancing
    #[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
    pub struct ServiceInstance {
        pub id: String,
        pub service_type: String,
        pub endpoint: String,
        pub health_score: f64,
        pub load_factor: f64,
        pub last_heartbeat: chrono::DateTime<chrono::Utc>,
        pub metadata: HashMap<String, String>,
    }

    /// Load balancer for distributing requests across service instances
    pub struct LoadBalancer {
        instances: Arc<RwLock<HashMap<String, Vec<ServiceInstance>>>>,
        strategy: LoadBalancingStrategy,
    }

    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    pub enum LoadBalancingStrategy {
        RoundRobin,
        LeastLoaded,
        WeightedRandom,
        HealthBased,
    }

    impl LoadBalancer {
        pub fn new(strategy: LoadBalancingStrategy) -> Self {
            Self {
                instances: Arc::new(RwLock::new(HashMap::new())),
                strategy,
            }
        }

        pub async fn register_instance(&self, instance: ServiceInstance) {
            let mut instances = self.instances.write().await;
            instances.entry(instance.service_type.clone())
                .or_insert_with(Vec::new)
                .push(instance);
        }

        pub async fn get_instance(&self, service_type: &str) -> Option<ServiceInstance> {
            let instances = self.instances.read().await;
            let service_instances = instances.get(service_type)?;

            if service_instances.is_empty() {
                return None;
            }

            match self.strategy {
                LoadBalancingStrategy::RoundRobin => {
                    // Simple round-robin (would need persistent counter in real impl)
                    Some(service_instances[0].clone())
                }
                LoadBalancingStrategy::LeastLoaded => {
                    service_instances.iter()
                        .min_by(|a, b| a.load_factor.partial_cmp(&b.load_factor).unwrap())
                        .cloned()
                }
                LoadBalancingStrategy::HealthBased => {
                    service_instances.iter()
                        .max_by(|a, b| a.health_score.partial_cmp(&b.health_score).unwrap())
                        .cloned()
                }
                LoadBalancingStrategy::WeightedRandom => {
                    // Simplified weighted random
                    let total_weight: f64 = service_instances.iter()
                        .map(|i| i.health_score.max(0.1))
                        .sum();

                    let mut random = (std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap()
                        .as_nanos() % 1000) as f64 / 1000.0;

                    for instance in service_instances {
                        let weight = instance.health_score.max(0.1) / total_weight;
                        if random < weight {
                            return Some(instance.clone());
                        }
                        random -= weight;
                    }

                    // Fallback to first instance
                    Some(service_instances[0].clone())
                }
            }
        }

        pub async fn update_instance_health(&self, service_type: &str, instance_id: &str, health_score: f64) {
            let mut instances = self.instances.write().await;
            if let Some(service_instances) = instances.get_mut(service_type) {
                for instance in service_instances.iter_mut() {
                    if instance.id == instance_id {
                        instance.health_score = health_score;
                        instance.last_heartbeat = chrono::Utc::now();
                        break;
                    }
                }
            }
        }

        pub async fn remove_instance(&self, service_type: &str, instance_id: &str) {
            let mut instances = self.instances.write().await;
            if let Some(service_instances) = instances.get_mut(service_type) {
                service_instances.retain(|i| i.id != instance_id);
            }
        }

        pub async fn get_service_stats(&self, service_type: &str) -> HashMap<String, serde_json::Value> {
            let instances = self.instances.read().await;
            let mut stats = HashMap::new();

            if let Some(service_instances) = instances.get(service_type) {
                stats.insert("instance_count".to_string(), service_instances.len().into());
                stats.insert("healthy_instances".to_string(),
                    service_instances.iter().filter(|i| i.health_score > 0.8).count().into());
                stats.insert("avg_health_score".to_string(),
                    (service_instances.iter().map(|i| i.health_score).sum::<f64>() / service_instances.len() as f64).into());
                stats.insert("avg_load_factor".to_string(),
                    (service_instances.iter().map(|i| i.load_factor).sum::<f64>() / service_instances.len() as f64).into());
            }

            stats
        }
    }

    /// Circuit breaker for resilient service communication
    pub struct CircuitBreaker {
        state: Arc<RwLock<CircuitState>>,
        failure_threshold: u32,
        recovery_timeout: Duration,
        success_threshold: u32,
    }

    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    enum CircuitState {
        Closed,     // Normal operation
        Open,       // Failing, requests rejected
        HalfOpen,   // Testing recovery
    }

    impl CircuitBreaker {
        pub fn new(failure_threshold: u32, recovery_timeout: Duration, success_threshold: u32) -> Self {
            Self {
                state: Arc::new(RwLock::new(CircuitState::Closed)),
                failure_threshold,
                recovery_timeout,
                success_threshold,
            }
        }

        pub async fn call<F, T, E>(&self, operation: F) -> Result<T, CircuitBreakerError<E>>
        where
            F: FnOnce() -> Result<T, E>,
        {
            let current_state = *self.state.read().await;

            match current_state {
                CircuitState::Open => {
                    // Check if we should transition to half-open
                    // Simplified: always allow one request for testing
                    *self.state.write().await = CircuitState::HalfOpen;
                    let result = operation();
                    match result {
                        Ok(value) => {
                            // Success in half-open, close circuit
                            *self.state.write().await = CircuitState::Closed;
                            Ok(value)
                        }
                        Err(error) => {
                            // Still failing, stay open
                            *self.state.write().await = CircuitState::Open;
                            Err(CircuitBreakerError::OperationFailed(error))
                        }
                    }
                }
                CircuitState::HalfOpen => {
                    Err(CircuitBreakerError::CircuitOpen)
                }
                CircuitState::Closed => {
                    let result = operation();
                    match result {
                        Ok(value) => Ok(value),
                        Err(error) => {
                            // Record failure and potentially open circuit
                            // Simplified failure counting
                            Err(CircuitBreakerError::OperationFailed(error))
                        }
                    }
                }
            }
        }

        pub async fn get_state(&self) -> CircuitState {
            *self.state.read().await
        }
    }

    /// Circuit breaker error types
    #[derive(Debug)]
    pub enum CircuitBreakerError<E> {
        CircuitOpen,
        OperationFailed(E),
    }

    /// Auto-scaling manager for dynamic service scaling
    pub struct AutoScaler {
        service_metrics: Arc<RwLock<HashMap<String, ServiceMetrics>>>,
        scaling_policies: Vec<ScalingPolicy>,
    }

    #[derive(Debug, Clone)]
    pub struct ServiceMetrics {
        pub service_type: String,
        pub current_instances: u32,
        pub target_instances: u32,
        pub avg_response_time: Duration,
        pub request_rate: f64,
        pub error_rate: f64,
        pub last_scaled: chrono::DateTime<chrono::Utc>,
    }

    #[derive(Debug, Clone)]
    pub struct ScalingPolicy {
        pub service_type: String,
        pub min_instances: u32,
        pub max_instances: u32,
        pub scale_up_threshold: f64,    // CPU/memory usage threshold
        pub scale_down_threshold: f64,
        pub cooldown_period: Duration,
    }

    impl AutoScaler {
        pub fn new() -> Self {
            Self {
                service_metrics: Arc::new(RwLock::new(HashMap::new())),
                scaling_policies: Vec::new(),
            }
        }

        pub fn add_policy(&mut self, policy: ScalingPolicy) {
            self.scaling_policies.push(policy);
        }

        pub async fn evaluate_scaling(&self, service_type: &str) -> Option<ScalingDecision> {
            let metrics = self.service_metrics.read().await;
            let service_metrics = metrics.get(service_type)?;

            for policy in &self.scaling_policies {
                if policy.service_type == service_type {
                    let time_since_last_scale = chrono::Utc::now()
                        .signed_duration_since(service_metrics.last_scaled)
                        .to_std()
                        .unwrap_or(Duration::from_secs(0));

                    if time_since_last_scale < policy.cooldown_period {
                        continue; // Still in cooldown
                    }

                    // Simplified scaling logic based on request rate
                    if service_metrics.request_rate > policy.scale_up_threshold
                       && service_metrics.current_instances < policy.max_instances {
                        return Some(ScalingDecision::ScaleUp);
                    }

                    if service_metrics.request_rate < policy.scale_down_threshold
                       && service_metrics.current_instances > policy.min_instances {
                        return Some(ScalingDecision::ScaleDown);
                    }
                }
            }

            None
        }

        pub async fn update_metrics(&self, service_type: &str, metrics: ServiceMetrics) {
            let mut service_metrics = self.service_metrics.write().await;
            service_metrics.insert(service_type.to_string(), metrics);
        }
    }

    /// Scaling decision
    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    pub enum ScalingDecision {
        ScaleUp,
        ScaleDown,
        NoChange,
    }

    /// Global scalability components (using LazyLock from std)
    use std::sync::LazyLock;

    pub static LOAD_BALANCER: LazyLock<LoadBalancer> =
        LazyLock::new(|| LoadBalancer::new(LoadBalancingStrategy::HealthBased));

    pub static AUTO_SCALER: LazyLock<AutoScaler> =
        LazyLock::new(|| AutoScaler::new());
}

pub use nats::NatsClient;
pub use discovery::{ServiceDiscovery, ServiceRegistration};
pub use health::{HealthMonitor, HealthChecker, ConnectivityChecker, DatabaseChecker, MemoryChecker};
pub use auth::{ServiceAuth, default_service_scopes, admin_service_scopes};
pub use events::{Event, EventType, EventPriority};
pub use performance_monitoring::{PerformanceMonitor, PerformanceMetrics, PERFORMANCE_MONITOR};
pub use scalability::{LoadBalancer, CircuitBreaker, AutoScaler, ServiceInstance, LOAD_BALANCER, AUTO_SCALER};
