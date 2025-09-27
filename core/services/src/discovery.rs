//! # Service Discovery Module
//! 
//! Provides service registration, discovery, and management capabilities for SynOS services.

use crate::{ServiceResult, ServiceConfig, ServiceStatus};
use crate::nats::NatsClient;
use crate::events::{Event, EventType, EventPriority};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use tracing::{info, warn, debug};

/// Service registration information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceRegistration {
    pub service_id: String,
    pub service_name: String,
    pub version: String,
    pub status: ServiceStatus,
    pub endpoints: HashMap<String, String>,
    pub metadata: HashMap<String, String>,
    pub health_check_url: Option<String>,
    pub registered_at: DateTime<Utc>,
    pub last_heartbeat: DateTime<Utc>,
    pub tags: Vec<String>,
}

impl ServiceRegistration {
    /// Create a new service registration
    pub fn new(config: &ServiceConfig) -> Self {
        let now = Utc::now();
        Self {
            service_id: config.service_id.clone(),
            service_name: config.service_name.clone(),
            version: config.version.clone(),
            status: ServiceStatus::Starting,
            endpoints: HashMap::new(),
            metadata: HashMap::new(),
            health_check_url: None,
            registered_at: now,
            last_heartbeat: now,
            tags: Vec::new(),
        }
    }

    /// Update heartbeat timestamp
    pub fn update_heartbeat(&mut self) {
        self.last_heartbeat = Utc::now();
    }

    /// Check if service registration is stale
    pub fn is_stale(&self, timeout: std::time::Duration) -> bool {
        let elapsed = Utc::now() - self.last_heartbeat;
        elapsed.num_seconds() > timeout.as_secs() as i64
    }

    /// Add an endpoint
    pub fn add_endpoint(&mut self, name: String, url: String) {
        self.endpoints.insert(name, url);
    }

    /// Add metadata
    pub fn add_metadata(&mut self, key: String, value: String) {
        self.metadata.insert(key, value);
    }

    /// Add a tag
    pub fn add_tag(&mut self, tag: String) {
        if !self.tags.contains(&tag) {
            self.tags.push(tag);
        }
    }
}

/// Service discovery client
#[derive(Clone)]
pub struct ServiceDiscovery {
    nats_client: NatsClient,
    config: ServiceConfig,
    services: Arc<RwLock<HashMap<String, ServiceRegistration>>>,
    registration: Arc<RwLock<Option<ServiceRegistration>>>,
    heartbeat_task: Arc<RwLock<Option<tokio::task::JoinHandle<()>>>>,
}

impl ServiceDiscovery {
    /// Create a new service discovery client
    pub async fn new(nats_client: NatsClient, config: ServiceConfig) -> ServiceResult<Self> {
        let discovery = Self {
            nats_client: nats_client.clone(),
            config,
            services: Arc::new(RwLock::new(HashMap::new())),
            registration: Arc::new(RwLock::new(None)),
            heartbeat_task: Arc::new(RwLock::new(None)),
        };

        // Subscribe to service registration events
        discovery.setup_subscriptions().await?;

        Ok(discovery)
    }

    /// Register this service with the discovery system
    pub async fn register_service(
        &self,
        mut registration: ServiceRegistration,
    ) -> ServiceResult<()> {
        info!("Registering service: {}", registration.service_id);

        registration.status = ServiceStatus::Running;
        registration.update_heartbeat();

        // Store registration
        {
            let mut reg = self.registration.write().await;
            *reg = Some(registration.clone());
        }

        // Publish registration event
        let event = Event::service_lifecycle(
            EventType::ServiceRegistered,
            registration.service_id.clone(),
            ServiceStatus::Running,
        )
        .with_data("registration".to_string(), serde_json::to_value(&registration)?)
        .with_priority(EventPriority::High);

        self.nats_client.publish_event(&event).await?;

        // Start heartbeat task
        self.start_heartbeat_task().await;

        info!("Service registered successfully: {}", registration.service_id);
        Ok(())
    }

    /// Unregister this service
    pub async fn unregister_service(&self) -> ServiceResult<()> {
        let registration = {
            let mut reg = self.registration.write().await;
            reg.take()
        };

        if let Some(mut registration) = registration {
            info!("Unregistering service: {}", registration.service_id);

            registration.status = ServiceStatus::Stopped;

            // Publish unregistration event
            let event = Event::service_lifecycle(
                EventType::ServiceUnregistered,
                registration.service_id.clone(),
                ServiceStatus::Stopped,
            )
            .with_data("registration".to_string(), serde_json::to_value(&registration)?)
            .with_priority(EventPriority::High);

            self.nats_client.publish_event(&event).await?;

            // Stop heartbeat task
            self.stop_heartbeat_task().await;

            info!("Service unregistered successfully: {}", registration.service_id);
        }

        Ok(())
    }

    /// Discover services by name
    pub async fn discover_services(&self, service_name: &str) -> Vec<ServiceRegistration> {
        let services = self.services.read().await;
        services
            .values()
            .filter(|reg| reg.service_name == service_name && reg.status == ServiceStatus::Running)
            .cloned()
            .collect()
    }

    /// Get all registered services
    pub async fn get_all_services(&self) -> Vec<ServiceRegistration> {
        let services = self.services.read().await;
        services.values().cloned().collect()
    }

    /// Get service by ID
    pub async fn get_service(&self, service_id: &str) -> Option<ServiceRegistration> {
        let services = self.services.read().await;
        services.get(service_id).cloned()
    }

    /// Find services by tags
    pub async fn find_services_by_tags(&self, tags: &[String]) -> Vec<ServiceRegistration> {
        let services = self.services.read().await;
        services
            .values()
            .filter(|reg| {
                reg.status == ServiceStatus::Running
                    && tags.iter().any(|tag| reg.tags.contains(tag))
            })
            .cloned()
            .collect()
    }

    /// Update service status
    pub async fn update_service_status(&self, status: ServiceStatus) -> ServiceResult<()> {
        let mut registration = self.registration.write().await;
        
        if let Some(ref mut reg) = *registration {
            reg.status = status;
            reg.update_heartbeat();

            // Publish status update event
            let event = Event::service_lifecycle(
                match status {
                    ServiceStatus::Running => EventType::ServiceStarted,
                    ServiceStatus::Stopped => EventType::ServiceStopped,
                    ServiceStatus::Failed => EventType::ServiceFailed,
                    _ => EventType::ServiceStarted, // Default
                },
                reg.service_id.clone(),
                status,
            )
            .with_data("registration".to_string(), serde_json::to_value(&*reg)?)
            .with_priority(EventPriority::High);

            self.nats_client.publish_event(&event).await?;

            info!("Updated service status to: {}", status);
        }

        Ok(())
    }

    /// Get service discovery statistics
    pub async fn get_stats(&self) -> HashMap<String, serde_json::Value> {
        let mut stats = HashMap::new();
        
        let services = self.services.read().await;
        let registration = self.registration.read().await;

        stats.insert("total_services".to_string(), services.len().into());
        stats.insert("registered".to_string(), registration.is_some().into());
        
        if let Some(ref reg) = *registration {
            stats.insert("service_id".to_string(), reg.service_id.clone().into());
            stats.insert("service_status".to_string(), format!("{}", reg.status).into());
            stats.insert("uptime_seconds".to_string(), 
                (Utc::now() - reg.registered_at).num_seconds().into());
        }

        // Service status breakdown
        let mut status_counts = HashMap::new();
        for service in services.values() {
            let status = format!("{}", service.status);
            let count = status_counts.get(&status).unwrap_or(&0) + 1;
            status_counts.insert(status, count);
        }
        stats.insert("service_status_counts".to_string(), 
            serde_json::to_value(status_counts).unwrap());

        stats
    }

    // Private methods

    async fn setup_subscriptions(&self) -> ServiceResult<()> {
        debug!("Setting up service discovery subscriptions");

        let services_clone = self.services.clone();
        let service_timeout = self.config.service_timeout;

        // Subscribe to service registration events using a subject pattern
        let subject_pattern = "services.lifecycle.>".to_string();

        self.nats_client
            .subscribe_events(subject_pattern, move |event| {
                let services_clone = services_clone.clone();
                
                tokio::spawn(async move {
                    if let Err(e) = Self::handle_service_event(services_clone, event, service_timeout).await {
                        warn!("Failed to handle service event: {}", e);
                    }
                });
            })
            .await?;

        info!("Service discovery subscriptions established");
        Ok(())
    }

    async fn handle_service_event(
        services: Arc<RwLock<HashMap<String, ServiceRegistration>>>,
        event: Event,
        service_timeout: std::time::Duration,
    ) -> ServiceResult<()> {
        match event.event_type {
            EventType::ServiceRegistered => {
                if let Some(registration_value) = event.data.get("registration") {
                    if let Ok(registration) = serde_json::from_value::<ServiceRegistration>(registration_value.clone()) {
                        let mut services = services.write().await;
                        services.insert(registration.service_id.clone(), registration);
                        debug!("Added service registration: {}", event.source);
                    }
                }
            }
            EventType::ServiceUnregistered => {
                let mut services = services.write().await;
                services.remove(&event.source);
                debug!("Removed service registration: {}", event.source);
            }
            EventType::ServiceStarted | EventType::ServiceStopped | EventType::ServiceFailed => {
                let mut services = services.write().await;
                if let Some(service) = services.get_mut(&event.source) {
                    if let Some(status_value) = event.data.get("status") {
                        if let Ok(status) = serde_json::from_value::<ServiceStatus>(status_value.clone()) {
                            service.status = status;
                            service.update_heartbeat();
                            debug!("Updated service status: {} -> {}", event.source, status);
                        }
                    }
                }
            }
            _ => {}
        }

        // Clean up stale services
        let mut services = services.write().await;
        let stale_services: Vec<String> = services
            .iter()
            .filter(|(_, reg)| reg.is_stale(service_timeout))
            .map(|(id, _)| id.clone())
            .collect();

        for service_id in stale_services {
            services.remove(&service_id);
            warn!("Removed stale service: {}", service_id);
        }

        Ok(())
    }

    async fn start_heartbeat_task(&self) {
        let nats_client = self.nats_client.clone();
        let registration = self.registration.clone();
        let interval = self.config.health_check_interval;

        let task = tokio::spawn(async move {
            let mut ticker = tokio::time::interval(interval);
            
            loop {
                ticker.tick().await;

                let reg = {
                    let mut registration = registration.write().await;
                    if let Some(ref mut reg) = *registration {
                        reg.update_heartbeat();
                        Some(reg.clone())
                    } else {
                        break; // Service unregistered
                    }
                };

                if let Some(registration) = reg {
                    let event = Event::health_check(
                        registration.service_id.clone(),
                        true,
                        Some("Heartbeat".to_string()),
                    );

                    if let Err(e) = nats_client.publish_event(&event).await {
                        warn!("Failed to send heartbeat: {}", e);
                    }
                }
            }
        });

        let mut heartbeat_task = self.heartbeat_task.write().await;
        *heartbeat_task = Some(task);
    }

    async fn stop_heartbeat_task(&self) {
        let mut heartbeat_task = self.heartbeat_task.write().await;
        if let Some(task) = heartbeat_task.take() {
            task.abort();
        }
    }
}

impl Drop for ServiceDiscovery {
    fn drop(&mut self) {
        // Attempt to unregister on drop (best effort)
        if let Ok(rt) = tokio::runtime::Handle::try_current() {
            let discovery = self.clone();
            rt.spawn(async move {
                let _ = discovery.unregister_service().await;
            });
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_registration_creation() {
        let config = ServiceConfig::default();
        let registration = ServiceRegistration::new(&config);
        
        assert_eq!(registration.service_id, config.service_id);
        assert_eq!(registration.service_name, config.service_name);
        assert_eq!(registration.status, ServiceStatus::Starting);
    }

    #[test]
    fn test_service_registration_stale_check() {
        let mut registration = ServiceRegistration::new(&ServiceConfig::default());
        
        // Fresh registration should not be stale
        assert!(!registration.is_stale(std::time::Duration::from_secs(60)));
        
        // Manually set old timestamp
        registration.last_heartbeat = Utc::now() - chrono::Duration::seconds(120);
        assert!(registration.is_stale(std::time::Duration::from_secs(60)));
    }
}
