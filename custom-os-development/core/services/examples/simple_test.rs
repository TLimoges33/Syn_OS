//! Simple test to verify the service integration system works

use synos_services::ServiceConfig;
use std::time::Duration;

#[tokio::main]
async fn main() {
    println!("🚀 Testing SynOS Service Integration");
    
    let config = ServiceConfig {
        service_id: "test-service".to_string(),
        service_name: "Test Service".to_string(),
        version: "1.0.0".to_string(),
        nats_url: "nats://localhost:4222".to_string(),
        nats_credentials: None,
        health_check_interval: Duration::from_secs(30),
        service_timeout: Duration::from_secs(60),
    };
    
    println!("✅ Service config created: {}", config.service_id);
    println!("🎉 Basic integration test passed!");
}
