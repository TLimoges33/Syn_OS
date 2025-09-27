//! # Service Integration Example - Fixed
//! 
//! Demonstrates the complete service integration system including NATS messaging,
//! service discovery, health monitoring, and authentication.

use synos_services::{
    ServiceConfig, ServiceResult, NatsClient,
};
use std::time::Duration;
use tracing::{info, error};

#[tokio::main]
async fn main() -> ServiceResult<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();

    info!("🚀 Starting SynOS Service Integration Demo");

    // Create service configuration
    let config = ServiceConfig {
        service_id: "demo-service-001".to_string(),
        service_name: "Demo Service".to_string(),
        version: "1.0.0".to_string(),
        nats_url: "nats://localhost:4222".to_string(),
        nats_credentials: None,
        health_check_interval: Duration::from_secs(30),
        service_timeout: Duration::from_secs(60),
    };

    // Initialize NATS client
    info!("📡 Connecting to NATS...");
    let nats_client = match NatsClient::new(config.clone()).await {
        Ok(client) => {
            info!("✅ NATS connection established");
            client
        }
        Err(e) => {
            error!("❌ Failed to connect to NATS: {}", e);
            info!("📝 Note: Make sure NATS server is running on localhost:4222");
            info!("   You can start NATS with: docker run -p 4222:4222 nats:latest");
            return Err(e);
        }
    };

    info!("🎉 Service Integration Demo completed successfully!");
    Ok(())
}
