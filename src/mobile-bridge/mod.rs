//! SynOS Mobile Bridge Module - V1.8 "Mobile Companion"
//!
//! WebSocket-based bidirectional communication bridge for mobile apps.
//! Enables real-time monitoring, remote tool execution, and push notifications.
//!
//! # Features
//! - **Real-time Events:** Stream system status, scans, vulnerabilities to mobile
//! - **Remote Commands:** Execute security tools from mobile device
//! - **Push Notifications:** FCM/APNS for security alerts
//! - **Session Management:** JWT authentication, permissions, device tracking
//! - **Integration:** Works with V1.4 (Neural Audio), V1.6 (Cloud Security), V1.7 (AI Tutor)

pub mod websocket_bridge;

// Re-export main types
pub use websocket_bridge::{
    MobileWebSocketBridge,
    Session,
    SessionId,
    DeviceType,
    DeviceInfo,
    Permission,
    MobileEvent,
    MobileCommand,
    CommandResponse,
    Severity,
    LogLevel,
    PushNotification,
    PushNotificationService,
    NotificationPriority,
};

/// Quick-start: Create mobile bridge instance
pub fn create_bridge() -> MobileWebSocketBridge {
    MobileWebSocketBridge::new()
}

/// Quick-start: Create push notification service
pub fn create_push_service(fcm_api_key: String) -> PushNotificationService {
    PushNotificationService::new(fcm_api_key)
}

/// Example usage and demonstration
pub async fn demo() {
    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║          SynOS Mobile Bridge v1.8 - Demonstration          ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");

    // Create bridge
    let bridge = MobileWebSocketBridge::new();

    // Simulate mobile device connecting
    println!("1️⃣  Mobile device connecting...\n");
    let device_info = DeviceInfo {
        name: "iPhone 14 Pro".to_string(),
        device_type: DeviceType::IPhone,
        os_version: "17.0".to_string(),
        app_version: "1.0.0".to_string(),
    };

    match bridge.authenticate("demo_jwt_token", device_info).await {
        Ok(session) => {
            println!("✅ Session created: {:?}", session.id);
            println!("   User: {}", session.user_id);
            println!("   Device: {} ({:?})", session.device_name, session.device_type);
            println!("   Permissions: {} granted\n", session.permissions.len());

            // Send system status event
            println!("2️⃣  Sending system status update...\n");
            let event = MobileEvent::SystemStatus {
                cpu_usage: 45.2,
                memory_usage: 62.8,
                disk_usage: 38.5,
                network_active: true,
                uptime_seconds: 86400,
            };

            if let Err(e) = bridge.send_event(&session.id, event).await {
                println!("❌ Failed to send event: {}", e);
            } else {
                println!("✅ System status event sent");
            }

            // Send security alert
            println!("\n3️⃣  Sending security alert...\n");
            let alert = MobileEvent::SecurityAlert {
                alert_id: "alert-001".to_string(),
                severity: Severity::High,
                source: "IDS".to_string(),
                message: "Potential SQL injection attempt detected".to_string(),
                timestamp: chrono::Utc::now(),
                requires_action: true,
            };

            if let Err(e) = bridge.send_event(&session.id, alert).await {
                println!("❌ Failed to send alert: {}", e);
            } else {
                println!("✅ Security alert sent");
            }

            // Simulate command from mobile
            println!("\n4️⃣  Mobile device executing tool...\n");
            let command = MobileCommand::ExecuteTool {
                tool: "nmap".to_string(),
                target: "192.168.1.0/24".to_string(),
                args: vec!["-sn".to_string()],
            };

            let response = bridge.handle_command(&session.id, command).await;
            println!("📬 Command response:");
            println!("   Success: {}", response.success);
            if let Some(data) = response.data {
                println!("   Data: {}", data);
            }

            // Broadcast to all sessions
            println!("\n5️⃣  Broadcasting vulnerability discovery...\n");
            let vuln_event = MobileEvent::VulnerabilityDiscovered {
                id: "vuln-001".to_string(),
                severity: Severity::Critical,
                title: "SQL Injection in login form".to_string(),
                description: "User input not sanitized".to_string(),
                affected_service: "web-server:80".to_string(),
                cvss_score: Some(9.8),
            };

            bridge.broadcast_event(vuln_event).await;
            println!("✅ Broadcasted to {} active sessions", bridge.active_sessions().await);

            // Clean up
            println!("\n6️⃣  Disconnecting session...\n");
            bridge.disconnect(&session.id).await;
            println!("✅ Session disconnected");
        }
        Err(e) => {
            println!("❌ Authentication failed: {}", e);
        }
    }

    println!("\n╔══════════════════════════════════════════════════════════════╗");
    println!("║                    Demo Complete!                           ║");
    println!("╚══════════════════════════════════════════════════════════════╝");
}
