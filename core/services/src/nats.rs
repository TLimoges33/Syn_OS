//! # NATS Message Bus Integration with Connection Pooling
//!
//! Provides high-level NATS messaging capabilities with async connection pooling for SynOS services.

use crate::{ServiceError, ServiceResult, ServiceConfig};
use crate::events::Event;
use async_nats::Client;
use futures::stream::StreamExt;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tokio::task::JoinHandle;
use tracing::{info, warn, debug};

// Modern lazy static initialization
use std::sync::LazyLock;

/// Connection pool for NATS clients
pub struct NatsConnectionPool {
    clients: Arc<RwLock<HashMap<String, Arc<NatsClient>>>>,
    max_connections: usize,
    connection_timeout: std::time::Duration,
}

impl NatsConnectionPool {
    pub fn new(max_connections: usize) -> Self {
        Self {
            clients: Arc::new(RwLock::new(HashMap::new())),
            max_connections,
            connection_timeout: std::time::Duration::from_secs(30),
        }
    }

    pub async fn get_or_create_client(&self, config: &ServiceConfig) -> ServiceResult<Arc<NatsClient>> {
        let client_key = format!("{}:{}", config.service_id, config.nats_url);

        // Check if client already exists
        {
            let clients = self.clients.read().await;
            if let Some(client) = clients.get(&client_key) {
                return Ok(Arc::clone(client));
            }
        }

        // Check connection limit
        {
            let clients = self.clients.read().await;
            if clients.len() >= self.max_connections {
                return Err(ServiceError::NatsError("Connection pool limit reached".to_string()));
            }
        }

        // Create new client
        let client = Arc::new(NatsClient::new(config.clone()).await?);

        // Store in pool
        {
            let mut clients = self.clients.write().await;
            clients.insert(client_key, Arc::clone(&client));
        }

        Ok(client)
    }

    pub async fn remove_client(&self, service_id: &str, nats_url: &str) {
        let client_key = format!("{}:{}", service_id, nats_url);
        let mut clients = self.clients.write().await;
        if let Some(client) = clients.remove(&client_key) {
            let _ = client.close().await;
        }
    }

    pub async fn get_stats(&self) -> HashMap<String, serde_json::Value> {
        let clients = self.clients.read().await;
        let mut stats = HashMap::new();
        stats.insert("active_connections".to_string(), clients.len().into());
        stats.insert("max_connections".to_string(), self.max_connections.into());
        stats
    }
}

/// Global NATS connection pool
pub static NATS_POOL: LazyLock<NatsConnectionPool> =
    LazyLock::new(|| NatsConnectionPool::new(10));

/// NATS client wrapper for SynOS services with pooling support
#[derive(Clone)]
pub struct NatsClient {
    client: Client,
    config: ServiceConfig,
    subscription_handles: Arc<RwLock<HashMap<String, JoinHandle<()>>>>,
    connected: Arc<RwLock<bool>>,
}

impl NatsClient {
    /// Create a new NATS client
    pub async fn new(config: ServiceConfig) -> ServiceResult<Self> {
        info!("Connecting to NATS at {}", config.nats_url);

        let mut connect_options = async_nats::ConnectOptions::new()
            .name(&format!("synos-{}", config.service_id))
            .retry_on_initial_connect()
            .reconnect_delay_callback(|reconnect_attempts| {
                std::time::Duration::from_millis(std::cmp::min(reconnect_attempts * 100, 5000usize) as u64)
            });

        // Add authentication if provided
        if let Some(creds_file) = &config.nats_credentials {
            // For now, treat creds as a credentials file path
            // In production, this should be loaded properly
            connect_options = connect_options.credentials_file(creds_file)
                .await
                .map_err(|e| ServiceError::NatsError(format!("Failed to load credentials: {}", e)))?;
        }

        let client = connect_options
            .connect(&config.nats_url)
            .await
            .map_err(|e| ServiceError::NatsError(e.to_string()))?;

        info!("Successfully connected to NATS");

        Ok(Self {
            client,
            config,
            subscription_handles: Arc::new(RwLock::new(HashMap::new())),
            connected: Arc::new(RwLock::new(true)),
        })
    }

    /// Publish an event to NATS
    pub async fn publish_event(&self, event: &Event) -> ServiceResult<()> {
        let subject = self.get_subject_for_event(event);
        let payload = serde_json::to_vec(event)?;

        debug!("Publishing event {} to subject {}", event.id, subject);

        self.client
            .publish(subject, payload.into())
            .await
            .map_err(|e| ServiceError::NatsError(e.to_string()))?;

        Ok(())
    }

    /// Publish a raw message to a specific subject
    pub async fn publish(&self, subject: &str, payload: &[u8]) -> ServiceResult<()> {
        debug!("Publishing message to subject {}", subject);

        self.client
            .publish(subject.to_string(), payload.to_vec().into())
            .await
            .map_err(|e| ServiceError::NatsError(e.to_string()))?;

        Ok(())
    }

    /// Subscribe to events matching a filter
    pub async fn subscribe_events<F>(
        &self,
        subject_pattern: String,
        handler: F,
    ) -> ServiceResult<String>
    where
        F: Fn(Event) + Send + Sync + 'static,
    {
        let subscription_id = uuid::Uuid::new_v4().to_string();

        info!("Creating subscription {} for pattern {}", subscription_id, subject_pattern);

        let subscriber = self
            .client
            .subscribe(subject_pattern.clone())
            .await
            .map_err(|e| ServiceError::NatsError(e.to_string()))?;

        // Store subscription handle
        let handles = self.subscription_handles.clone();
        let handle = tokio::spawn(async move {
            let mut stream = subscriber;
            while let Some(message) = stream.next().await {
                let event_result: Result<Event, _> = serde_json::from_slice(&message.payload);
                match event_result {
                    Ok(event) => {
                        handler(event);
                    }
                    Err(e) => {
                        warn!("Failed to parse event: {}", e);
                    }
                }
            }
        });

        {
            let mut handles_guard = handles.write().await;
            handles_guard.insert(subscription_id.clone(), handle);
        }

        Ok(subscription_id)
    }

    /// Subscribe to a raw subject
    pub async fn subscribe<F>(&self, subject: &str, handler: F) -> ServiceResult<String>
    where
        F: Fn(Vec<u8>) -> ServiceResult<()> + Send + Sync + 'static,
    {
        let subscription_id = uuid::Uuid::new_v4().to_string();
        let subject = subject.to_string();

        info!("Creating raw subscription {} for subject {}", subscription_id, subject);

        let subscriber = self
            .client
            .subscribe(subject)
            .await
            .map_err(|e| ServiceError::NatsError(e.to_string()))?;

        // Store subscription handle
        let handles = self.subscription_handles.clone();
        let handle = tokio::spawn(async move {
            let mut stream = subscriber;

            while let Some(message) = stream.next().await {
                if let Err(e) = handler(message.payload.to_vec()) {
                    warn!("Message handler error: {}", e);
                }
            }
        });

        {
            let mut handles_guard = handles.write().await;
            handles_guard.insert(subscription_id.clone(), handle);
        }

        Ok(subscription_id)
    }

    /// Send a request and wait for response
    pub async fn request(
        &self,
        subject: &str,
        payload: &[u8],
        timeout: std::time::Duration,
    ) -> ServiceResult<Vec<u8>> {
        debug!("Sending request to subject {}", subject);

        let subject = subject.to_string();
        let payload = payload.to_vec();

        let response = tokio::time::timeout(
            timeout,
            self.client.request(subject, payload.into()),
        )
        .await
        .map_err(|_| ServiceError::TimeoutError(format!("Request timed out")))?
        .map_err(|e| ServiceError::NatsError(e.to_string()))?;

        Ok(response.payload.to_vec())
    }

    /// Send an event request and wait for event response
    pub async fn request_event(
        &self,
        event: &Event,
        timeout: std::time::Duration,
    ) -> ServiceResult<Event> {
        let subject = self.get_subject_for_event(event);
        let payload = serde_json::to_vec(event)?;

        let response_payload = self.request(&subject, &payload, timeout).await?;
        let response_event: Event = serde_json::from_slice(&response_payload)?;

        Ok(response_event)
    }

    /// Unsubscribe from a subscription
    pub async fn unsubscribe(&self, subscription_id: &str) -> ServiceResult<()> {
        let mut handles = self.subscription_handles.write().await;

        if let Some(handle) = handles.remove(subscription_id) {
            handle.abort();
            info!("Unsubscribed from {}", subscription_id);
        }

        Ok(())
    }

    /// Get connection status
    pub async fn is_connected(&self) -> bool {
        *self.connected.read().await
    }

    /// Get NATS client statistics
    pub async fn get_stats(&self) -> HashMap<String, serde_json::Value> {
        let mut stats = HashMap::new();

        stats.insert("connected".to_string(), self.is_connected().await.into());
        stats.insert("service_id".to_string(), self.config.service_id.clone().into());
        stats.insert("nats_url".to_string(), self.config.nats_url.clone().into());

        let subscription_count = self.subscription_handles.read().await.len();
        stats.insert("active_subscriptions".to_string(), subscription_count.into());

        stats
    }

    /// Get pooled client (recommended for high-throughput scenarios)
    pub async fn pooled(config: &ServiceConfig) -> ServiceResult<Arc<Self>> {
        NATS_POOL.get_or_create_client(config).await
    }

    /// Close all subscriptions and disconnect
    pub async fn close(&self) -> ServiceResult<()> {
        info!("Closing NATS client for service {}", self.config.service_id);

        // Unsubscribe from all subscriptions
        let subscription_ids: Vec<String> = {
            let handles = self.subscription_handles.read().await;
            handles.keys().cloned().collect()
        };

        for subscription_id in subscription_ids {
            self.unsubscribe(&subscription_id).await?;
        }

        // Mark as disconnected
        *self.connected.write().await = false;

        info!("NATS client closed");
        Ok(())
    }

    // Helper methods

    /// Get NATS subject for an event
    fn get_subject_for_event(&self, event: &Event) -> String {
        use crate::events::EventType;

        match event.event_type {
            EventType::ServiceStarted | EventType::ServiceStopped | EventType::ServiceFailed => {
                format!("services.lifecycle.{}", event.source)
            }
            EventType::ServiceHealthCheck => {
                format!("health.{}", event.source)
            }
            EventType::AIUpdate | EventType::NeuralNetworkUpdate => {
                format!("ai.events.{:?}", event.event_type)
            }
            EventType::SecurityThreat | EventType::SecurityIncident => {
                format!("security.{:?}", event.event_type)
            }
            EventType::SystemMetrics => {
                format!("metrics.{}", event.source)
            }
            _ => {
                format!("events.{:?}", event.event_type)
            }
        }
    }
}
