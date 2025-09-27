//! # Service Integration Example
//! 
//! Demonstrates the complete service integration system including NATS messaging,
//! service discovery, health monitoring, and authentication.

use synos_services::{
    ServiceConfig, ServiceResult, NatsClient, ServiceDiscovery, HealthMonitor, ServiceAuth,
    ServiceRegistration, ServiceStatus, EventType, EventFilter, Event,
    health::{ConnectivityChecker, MemoryChecker, DatabaseChecker},
    auth::{default_service_scopes, admin_service_scopes},
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

    // Test basic NATS functionality
    test_nats_messaging(&nats_client).await?;

    // Initialize service discovery
    info!("🔍 Initializing service discovery...");
    let discovery = ServiceDiscovery::new(nats_client.clone(), config.clone()).await?;

    // Register service
    let mut registration = ServiceRegistration::new(&config);
    registration.add_endpoint("http".to_string(), "http://localhost:8080".to_string());
    registration.add_endpoint("grpc".to_string(), "grpc://localhost:9090".to_string());
    registration.add_metadata("environment".to_string(), "development".to_string());
    registration.add_metadata("region".to_string(), "local".to_string());
    registration.add_tag("demo".to_string());
    registration.add_tag("rust".to_string());

    discovery.register_service(registration).await?;
    info!("✅ Service registered with discovery system");

    // Initialize authentication
    info!("🔐 Setting up authentication...");
    let auth = ServiceAuth::new(config.clone(), "demo-signing-key".to_string());
    
    // Generate initial token
    let token = auth.generate_token(default_service_scopes()).await?;
    info!("✅ Authentication token generated: {:.20}...", token.token);

    // Start token refresh
    auth.start_token_refresh().await?;

    // Initialize health monitoring
    info!("🏥 Setting up health monitoring...");
    let health_monitor = HealthMonitor::new(nats_client.clone(), config.clone()).await?;

    // Add health checkers
    health_monitor.add_checker(Box::new(
        ConnectivityChecker::new(
            "nats_connectivity".to_string(),
            "nats://localhost:4222".to_string(),
            Duration::from_secs(5),
        )
    )).await;

    health_monitor.add_checker(Box::new(
        MemoryChecker::new("memory_usage".to_string(), 70.0, 90.0)
    )).await;

    health_monitor.add_checker(Box::new(
        DatabaseChecker::new("database".to_string(), "postgres://localhost:5432".to_string())
    )).await;

    // Start health monitoring
    health_monitor.start_monitoring().await?;
    info!("✅ Health monitoring started");

    // Demonstrate service integration features
    demonstrate_service_features(&nats_client, &discovery, &health_monitor, &auth).await?;

    // Run for a demo period
    info!("🔄 Running service integration demo for 2 minutes...");
    tokio::time::sleep(Duration::from_secs(120)).await;

    // Cleanup
    info!("🧹 Cleaning up...");
    
    health_monitor.stop_monitoring().await;
    auth.stop_token_refresh().await;
    discovery.unregister_service().await?;
    nats_client.close().await?;

    info!("✅ Service integration demo completed successfully!");

    Ok(())
}

async fn test_nats_messaging(nats_client: &NatsClient) -> ServiceResult<()> {
    info!("🧪 Testing NATS messaging...");

    // Test basic publish
    let test_event = Event::new(EventType::ServiceStarted, "test-service".to_string())
        .with_data("test_data".to_string(), "Hello from demo!".into());

    nats_client.publish_event(&test_event).await?;
    info!("✅ Published test event: {}", test_event.id);

    // Test event subscription
    let subscription_id = nats_client.subscribe_events(
        EventFilter::new().with_event_types(vec![EventType::ServiceStarted]),
        |event| {
            info!("📥 Received event: {} from {}", event.id, event.source);
            Ok(())
        }
    ).await?;

    info!("✅ Created event subscription: {}", subscription_id);

    // Test raw messaging
    nats_client.publish("test.subject", b"Hello NATS!").await?;
    info!("✅ Published raw message");

    Ok(())
}

async fn demonstrate_service_features(
    nats_client: &NatsClient,
    discovery: &ServiceDiscovery,
    health_monitor: &HealthMonitor,
    auth: &ServiceAuth,
) -> ServiceResult<()> {
    info!("🎯 Demonstrating service integration features...");

    // Test service discovery
    let services = discovery.get_all_services().await;
    info!("📋 Discovered {} services", services.len());
    
    for service in services {
        info!("   - {} ({}): {}", service.service_name, service.service_id, service.status);
    }

    // Test health monitoring
    if let Some(health_check) = health_monitor.get_latest_health_check().await {
        info!("🏥 Latest health check: {} ({} checks)", 
              health_check.status, health_check.checks.len());
        
        for (name, check) in health_check.checks {
            info!("   - {}: {} ({}ms)", name, check.status, check.duration_ms);
        }
    }

    // Test authentication
    let current_token = auth.get_current_token().await?;
    info!("🔐 Current token expires at: {}", current_token.expires_at);
    info!("   Scopes: {:?}", current_token.scopes);

    // Test authorization
    let auth_header = current_token.authorization_header();
    let claims = auth.authorize_request(&current_token.token, &["service:read".to_string()]).await?;
    info!("✅ Successfully authorized request for service: {}", claims.sub);

    // Generate admin token for demonstration
    let admin_token = auth.generate_token(admin_service_scopes()).await?;
    info!("🔑 Generated admin token with {} scopes", admin_token.scopes.len());

    // Publish some demonstration events
    let consciousness_event = Event::consciousness_update(
        "neural-processor".to_string(),
        0.75,
        [("coherence".to_string(), 0.82), ("complexity".to_string(), 0.68)]
            .iter().cloned().collect(),
    );
    nats_client.publish_event(&consciousness_event).await?;
    info!("🧠 Published consciousness update event");

    let security_event = Event::security_threat(
        "security-monitor".to_string(),
        "unusual_activity".to_string(),
        "medium".to_string(),
        [("source_ip".to_string(), "192.168.1.100".into()),
         ("attempt_count".to_string(), 3.into())]
            .iter().cloned().collect(),
    );
    nats_client.publish_event(&security_event).await?;
    info!("🛡️ Published security threat event");

    // Display statistics
    let nats_stats = nats_client.get_stats().await;
    info!("📊 NATS Statistics:");
    for (key, value) in nats_stats {
        info!("   {}: {}", key, value);
    }

    let discovery_stats = discovery.get_stats().await;
    info!("📊 Discovery Statistics:");
    for (key, value) in discovery_stats {
        info!("   {}: {}", key, value);
    }

    let health_stats = health_monitor.get_stats().await;
    info!("📊 Health Statistics:");
    for (key, value) in health_stats {
        info!("   {}: {}", key, value);
    }

    let auth_stats = auth.get_stats().await;
    info!("📊 Auth Statistics:");
    for (key, value) in auth_stats {
        info!("   {}: {}", key, value);
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_service_integration() {
        // This test would run if NATS is available
        // For CI/CD, you'd want to use testcontainers or similar
        
        let config = ServiceConfig::default();
        
        // Test that we can create all components
        let _auth = ServiceAuth::new(config.clone(), "test-key".to_string());
        
        // Additional integration tests would go here
        // when NATS infrastructure is available
    }
}
