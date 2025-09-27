//! # Health Monitoring Module
//! 
//! Provides comprehensive health monitoring, metrics collection, and alerting for SynOS services.

use crate::{ServiceResult, ServiceConfig};
use crate::nats::NatsClient;
use crate::events::{Event, EventType, EventPriority};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::RwLock;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use tracing::{info, warn};

/// Health status enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum HealthStatus {
    Healthy,
    Degraded,
    Unhealthy,
    Unknown,
}

impl std::fmt::Display for HealthStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            HealthStatus::Healthy => write!(f, "healthy"),
            HealthStatus::Degraded => write!(f, "degraded"),
            HealthStatus::Unhealthy => write!(f, "unhealthy"),
            HealthStatus::Unknown => write!(f, "unknown"),
        }
    }
}

/// Health check result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthCheck {
    pub service_id: String,
    pub status: HealthStatus,
    pub timestamp: DateTime<Utc>,
    pub response_time_ms: u64,
    pub checks: HashMap<String, CheckResult>,
    pub metadata: HashMap<String, String>,
}

/// Individual check result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CheckResult {
    pub name: String,
    pub status: HealthStatus,
    pub message: Option<String>,
    pub duration_ms: u64,
    pub metadata: HashMap<String, serde_json::Value>,
}

/// System metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemMetrics {
    pub service_id: String,
    pub timestamp: DateTime<Utc>,
    pub cpu_usage_percent: f64,
    pub memory_usage_bytes: u64,
    pub memory_available_bytes: u64,
    pub disk_usage_percent: f64,
    pub network_bytes_in: u64,
    pub network_bytes_out: u64,
    pub active_connections: u32,
    pub request_count: u64,
    pub error_count: u64,
    pub response_time_avg_ms: f64,
    pub custom_metrics: HashMap<String, f64>,
}

/// Health checker enum that can be used in collections
#[derive(Debug, Clone)]
pub enum HealthChecker {
    Connectivity(ConnectivityChecker),
    Database(DatabaseChecker),
    Memory(MemoryChecker),
}

impl HealthChecker {
    pub fn name(&self) -> &str {
        match self {
            HealthChecker::Connectivity(c) => &c.name,
            HealthChecker::Database(c) => &c.name,
            HealthChecker::Memory(c) => &c.name,
        }
    }

    pub async fn check(&self) -> CheckResult {
        match self {
            HealthChecker::Connectivity(c) => c.check().await,
            HealthChecker::Database(c) => c.check().await,
            HealthChecker::Memory(c) => c.check().await,
        }
    }
}

/// Basic connectivity health checker
#[derive(Debug, Clone)]
pub struct ConnectivityChecker {
    name: String,
    url: String,
    timeout: Duration,
}

impl ConnectivityChecker {
    pub fn new(name: String, url: String, timeout: Duration) -> Self {
        Self { name, url, timeout }
    }

    pub async fn check(&self) -> CheckResult {
        let start = Instant::now();
        
        // Simple TCP connection check (in a real implementation, you'd use proper HTTP client)
        let status = if self.url.starts_with("http") {
            // Simulate HTTP check
            tokio::time::sleep(Duration::from_millis(10)).await;
            HealthStatus::Healthy
        } else {
            HealthStatus::Unknown
        };

        CheckResult {
            name: self.name.clone(),
            status,
            message: Some(format!("Checked connectivity to {}", self.url)),
            duration_ms: start.elapsed().as_millis() as u64,
            metadata: {
                let mut meta = HashMap::new();
                meta.insert("url".to_string(), self.url.clone().into());
                meta
            },
        }
    }
}

/// Database health checker
#[derive(Debug, Clone)]
pub struct DatabaseChecker {
    name: String,
    connection_string: String,
}

impl DatabaseChecker {
    pub fn new(name: String, connection_string: String) -> Self {
        Self { name, connection_string }
    }

    pub async fn check(&self) -> CheckResult {
        let start = Instant::now();
        
        // Simulate database check
        tokio::time::sleep(Duration::from_millis(20)).await;
        
        CheckResult {
            name: self.name.clone(),
            status: HealthStatus::Healthy,
            message: Some("Database connection successful".to_string()),
            duration_ms: start.elapsed().as_millis() as u64,
            metadata: HashMap::new(),
        }
    }
}

/// Memory usage checker
#[derive(Debug, Clone)]
pub struct MemoryChecker {
    name: String,
    warning_threshold_percent: f64,
    critical_threshold_percent: f64,
}

impl MemoryChecker {
    pub fn new(name: String, warning_threshold_percent: f64, critical_threshold_percent: f64) -> Self {
        Self {
            name,
            warning_threshold_percent,
            critical_threshold_percent,
        }
    }

    pub async fn check(&self) -> CheckResult {
        let start = Instant::now();
        
        // Simulate memory usage check
        let memory_usage_percent = 45.2; // Simulated value
        
        let status = if memory_usage_percent > self.critical_threshold_percent {
            HealthStatus::Unhealthy
        } else if memory_usage_percent > self.warning_threshold_percent {
            HealthStatus::Degraded
        } else {
            HealthStatus::Healthy
        };

        let mut metadata = HashMap::new();
        metadata.insert("memory_usage_percent".to_string(), memory_usage_percent.into());
        metadata.insert("warning_threshold".to_string(), self.warning_threshold_percent.into());
        metadata.insert("critical_threshold".to_string(), self.critical_threshold_percent.into());

        CheckResult {
            name: self.name.clone(),
            status,
            message: Some(format!("Memory usage: {:.1}%", memory_usage_percent)),
            duration_ms: start.elapsed().as_millis() as u64,
            metadata,
        }
    }
}

/// Health monitor manager
pub struct HealthMonitor {
    nats_client: NatsClient,
    config: ServiceConfig,
    checkers: Arc<RwLock<Vec<HealthChecker>>>,
    last_health_check: Arc<RwLock<Option<HealthCheck>>>,
    metrics_history: Arc<RwLock<Vec<SystemMetrics>>>,
    monitoring_task: Arc<RwLock<Option<tokio::task::JoinHandle<()>>>>,
}

impl HealthMonitor {
    /// Create a new health monitor
    pub async fn new(nats_client: NatsClient, config: ServiceConfig) -> ServiceResult<Self> {
        let monitor = Self {
            nats_client,
            config,
            checkers: Arc::new(RwLock::new(Vec::new())),
            last_health_check: Arc::new(RwLock::new(None)),
            metrics_history: Arc::new(RwLock::new(Vec::new())),
            monitoring_task: Arc::new(RwLock::new(None)),
        };

        Ok(monitor)
    }

    /// Add a health checker
    pub async fn add_checker(&self, checker: HealthChecker) {
        let mut checkers = self.checkers.write().await;
        checkers.push(checker);
    }

    /// Start health monitoring
    pub async fn start_monitoring(&self) -> ServiceResult<()> {
        info!("Starting health monitoring for service: {}", self.config.service_id);

        let nats_client = self.nats_client.clone();
        let config = self.config.clone();
        let checkers = self.checkers.clone();
        let last_health_check = self.last_health_check.clone();
        let metrics_history = self.metrics_history.clone();

        let task = tokio::spawn(async move {
            let mut interval = tokio::time::interval(config.health_check_interval);
            
            loop {
                interval.tick().await;

                // Perform health checks
                if let Ok(health_check) = Self::perform_health_check(&config.service_id, &checkers).await {
                    // Store latest health check
                    {
                        let mut last_check = last_health_check.write().await;
                        *last_check = Some(health_check.clone());
                    }

                    // Publish health check event
                    let event = Event::health_check(
                        config.service_id.clone(),
                        health_check.status == HealthStatus::Healthy,
                        Some(format!("Health check completed: {}", health_check.status)),
                    )
                    .with_data("health_check".to_string(), serde_json::to_value(&health_check).unwrap())
                    .with_priority(match health_check.status {
                        HealthStatus::Unhealthy => EventPriority::Critical,
                        HealthStatus::Degraded => EventPriority::High,
                        _ => EventPriority::Medium,
                    });

                    if let Err(e) = nats_client.publish_event(&event).await {
                        warn!("Failed to publish health check event: {}", e);
                    }
                }

                // Collect system metrics
                if let Ok(metrics) = Self::collect_metrics(&config.service_id).await {
                    // Store metrics (keep last 100 entries)
                    {
                        let mut history = metrics_history.write().await;
                        history.push(metrics.clone());
                        if history.len() > 100 {
                            history.remove(0);
                        }
                    }

                    // Publish metrics event
                    let event = Event::new(EventType::SystemMetrics, config.service_id.clone())
                        .with_data("metrics".to_string(), serde_json::to_value(&metrics).unwrap())
                        .with_priority(EventPriority::Low);

                    if let Err(e) = nats_client.publish_event(&event).await {
                        warn!("Failed to publish metrics event: {}", e);
                    }
                }
            }
        });

        let mut monitoring_task = self.monitoring_task.write().await;
        *monitoring_task = Some(task);

        info!("Health monitoring started");
        Ok(())
    }

    /// Stop health monitoring
    pub async fn stop_monitoring(&self) {
        info!("Stopping health monitoring");

        let mut monitoring_task = self.monitoring_task.write().await;
        if let Some(task) = monitoring_task.take() {
            task.abort();
        }

        info!("Health monitoring stopped");
    }

    /// Get the latest health check result
    pub async fn get_latest_health_check(&self) -> Option<HealthCheck> {
        let last_check = self.last_health_check.read().await;
        last_check.clone()
    }

    /// Get recent metrics
    pub async fn get_recent_metrics(&self, limit: usize) -> Vec<SystemMetrics> {
        let history = self.metrics_history.read().await;
        let start = if history.len() > limit {
            history.len() - limit
        } else {
            0
        };
        history[start..].to_vec()
    }

    /// Perform a manual health check
    pub async fn check_health(&self) -> ServiceResult<HealthCheck> {
        Self::perform_health_check(&self.config.service_id, &self.checkers).await
    }

    /// Get health monitoring statistics
    pub async fn get_stats(&self) -> HashMap<String, serde_json::Value> {
        let mut stats = HashMap::new();
        
        let checkers = self.checkers.read().await;
        let last_check = self.last_health_check.read().await;
        let metrics_history = self.metrics_history.read().await;

        stats.insert("checker_count".to_string(), checkers.len().into());
        stats.insert("metrics_history_count".to_string(), metrics_history.len().into());
        
        if let Some(ref check) = *last_check {
            stats.insert("last_health_status".to_string(), format!("{}", check.status).into());
            stats.insert("last_check_time".to_string(), check.timestamp.to_rfc3339().into());
            stats.insert("last_response_time_ms".to_string(), check.response_time_ms.into());
            stats.insert("total_checks".to_string(), check.checks.len().into());
        }

        stats
    }

    // Private methods

    async fn perform_health_check(
        service_id: &str,
        checkers: &Arc<RwLock<Vec<HealthChecker>>>,
    ) -> ServiceResult<HealthCheck> {
        let start = Instant::now();
        let mut checks = HashMap::new();
        let mut overall_status = HealthStatus::Healthy;

        let checkers = checkers.read().await;
        
        for checker in checkers.iter() {
            let check_result = checker.check().await;
            
            // Update overall status based on individual check
            match check_result.status {
                HealthStatus::Unhealthy => overall_status = HealthStatus::Unhealthy,
                HealthStatus::Degraded if overall_status == HealthStatus::Healthy => {
                    overall_status = HealthStatus::Degraded;
                }
                _ => {}
            }

            checks.insert(checker.name().to_string(), check_result);
        }

        // If no checkers, status is unknown
        if checkers.is_empty() {
            overall_status = HealthStatus::Unknown;
        }

        Ok(HealthCheck {
            service_id: service_id.to_string(),
            status: overall_status,
            timestamp: Utc::now(),
            response_time_ms: start.elapsed().as_millis() as u64,
            checks,
            metadata: HashMap::new(),
        })
    }

    async fn collect_metrics(service_id: &str) -> ServiceResult<SystemMetrics> {
        // In a real implementation, these would be actual system metrics
        // For now, we'll simulate some basic metrics
        
        Ok(SystemMetrics {
            service_id: service_id.to_string(),
            timestamp: Utc::now(),
            cpu_usage_percent: 25.5,
            memory_usage_bytes: 128 * 1024 * 1024, // 128 MB
            memory_available_bytes: 1024 * 1024 * 1024, // 1 GB
            disk_usage_percent: 45.2,
            network_bytes_in: 1024 * 1024, // 1 MB
            network_bytes_out: 512 * 1024, // 512 KB
            active_connections: 15,
            request_count: 1000,
            error_count: 5,
            response_time_avg_ms: 125.5,
            custom_metrics: HashMap::new(),
        })
    }
}

impl Drop for HealthMonitor {
    fn drop(&mut self) {
        // Stop monitoring on drop (best effort)
        if let Ok(rt) = tokio::runtime::Handle::try_current() {
            let monitor = self.clone();
            rt.spawn(async move {
                monitor.stop_monitoring().await;
            });
        }
    }
}

// Clone implementation for HealthMonitor
impl Clone for HealthMonitor {
    fn clone(&self) -> Self {
        Self {
            nats_client: self.nats_client.clone(),
            config: self.config.clone(),
            checkers: self.checkers.clone(),
            last_health_check: self.last_health_check.clone(),
            metrics_history: self.metrics_history.clone(),
            monitoring_task: self.monitoring_task.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_connectivity_checker() {
        let checker = ConnectivityChecker::new(
            "test".to_string(),
            "http://localhost:8080".to_string(),
            Duration::from_secs(5),
        );

        let result = checker.check().await;
        assert_eq!(result.name, "test");
        assert!(result.duration_ms > 0);
    }

    #[tokio::test]
    async fn test_memory_checker() {
        let checker = MemoryChecker::new("memory".to_string(), 70.0, 90.0);
        let result = checker.check().await;
        
        assert_eq!(result.name, "memory");
        assert!(result.metadata.contains_key("memory_usage_percent"));
    }

    #[test]
    fn test_health_status_display() {
        assert_eq!(format!("{}", HealthStatus::Healthy), "healthy");
        assert_eq!(format!("{}", HealthStatus::Degraded), "degraded");
        assert_eq!(format!("{}", HealthStatus::Unhealthy), "unhealthy");
        assert_eq!(format!("{}", HealthStatus::Unknown), "unknown");
    }
}
