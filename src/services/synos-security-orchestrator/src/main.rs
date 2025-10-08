use anyhow::{Context, Result};
use clap::{Arg, Command};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{error, info};

mod tool_manager;
mod threat_detector;
mod response_coordinator;

use tool_manager::ToolManager;
use threat_detector::ThreatDetector;
use response_coordinator::ResponseCoordinator;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SecurityConfig {
    pub enabled: bool,
    pub tools: Vec<String>,
    pub auto_response: bool,
    pub threat_threshold: f64,
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            tools: vec![
                "nmap".to_string(),
                "metasploit".to_string(),
                "burpsuite".to_string(),
                "wireshark".to_string(),
                "snort".to_string(),
            ],
            auto_response: false,
            threat_threshold: 0.8,
        }
    }
}

pub struct SecurityOrchestrator {
    config: SecurityConfig,
    tool_manager: Arc<RwLock<ToolManager>>,
    threat_detector: Arc<RwLock<ThreatDetector>>,
    response_coordinator: Arc<RwLock<ResponseCoordinator>>,
}

impl SecurityOrchestrator {
    pub fn new(config: SecurityConfig) -> Result<Self> {
        info!("Initializing SynOS Security Orchestrator...");

        let tool_manager = Arc::new(RwLock::new(
            ToolManager::new(config.tools.clone())?
        ));

        let threat_detector = Arc::new(RwLock::new(
            ThreatDetector::new(config.threat_threshold)?
        ));

        let response_coordinator = Arc::new(RwLock::new(
            ResponseCoordinator::new(config.auto_response)?
        ));

        Ok(Self {
            config,
            tool_manager,
            threat_detector,
            response_coordinator,
        })
    }

    pub async fn run(&self) -> Result<()> {
        info!("Starting security orchestrator...");

        // Spawn tool monitoring task
        let tool_handle = {
            let manager = Arc::clone(&self.tool_manager);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = manager.write().await.monitor_tools().await {
                        error!("Tool monitoring error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                }
            })
        };

        // Spawn threat detection task
        let threat_handle = {
            let detector = Arc::clone(&self.threat_detector);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = detector.write().await.scan_for_threats().await {
                        error!("Threat detection error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                }
            })
        };

        // Spawn response coordination task
        let response_handle = {
            let coordinator = Arc::clone(&self.response_coordinator);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = coordinator.write().await.coordinate_responses().await {
                        error!("Response coordination error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
                }
            })
        };

        info!("Security orchestrator running");

        // Wait for shutdown signal
        tokio::signal::ctrl_c().await?;

        info!("Shutting down security orchestrator...");
        tool_handle.abort();
        threat_handle.abort();
        response_handle.abort();

        Ok(())
    }

    pub async fn get_status(&self) -> Result<SecurityStatus> {
        let tools = self.tool_manager.read().await;
        let threats = self.threat_detector.read().await;
        let responses = self.response_coordinator.read().await;

        Ok(SecurityStatus {
            enabled: self.config.enabled,
            tools_active: tools.get_active_count(),
            threats_detected: threats.get_threat_count(),
            responses_executed: responses.get_response_count(),
            last_scan: threats.get_last_scan_time(),
        })
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SecurityStatus {
    pub enabled: bool,
    pub tools_active: usize,
    pub threats_detected: u64,
    pub responses_executed: u64,
    pub last_scan: Option<String>,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_target(false)
        .with_thread_ids(true)
        .with_level(true)
        .init();

    let matches = Command::new("synos-security-orchestrator")
        .version("1.0.0")
        .author("SynOS Team")
        .about("SynOS Security Tool Orchestration Daemon")
        .arg(
            Arg::new("config")
                .short('c')
                .long("config")
                .value_name("FILE")
                .help("Configuration file path")
        )
        .arg(
            Arg::new("auto-response")
                .long("auto-response")
                .help("Enable automatic threat response")
                .action(clap::ArgAction::SetTrue)
        )
        .get_matches();

    let config = if let Some(config_path) = matches.get_one::<String>("config") {
        let content = std::fs::read_to_string(config_path)
            .context("Failed to read config file")?;
        serde_json::from_str(&content)
            .context("Failed to parse config file")?
    } else {
        SecurityConfig::default()
    };

    info!("SynOS Security Orchestrator v1.0.0");
    info!("Configuration: {:?}", config);

    let orchestrator = SecurityOrchestrator::new(config)?;
    orchestrator.run().await?;

    Ok(())
}
