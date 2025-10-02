use anyhow::{Context, Result};
use clap::{Arg, Command};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{error, info, warn};
use uuid::Uuid;

mod consciousness;
mod ai_runtime;
mod personal_context;
mod security_orchestration;
mod vector_db;

use consciousness::ConsciousnessEngine;
use ai_runtime::AIRuntimeManager;
use personal_context::PersonalContextEngine;
use security_orchestration::SecurityOrchestrator;
use vector_db::VectorDatabase;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SynOSConfig {
    pub consciousness: ConsciousnessConfig,
    pub ai_runtime: AIRuntimeConfig,
    pub security: SecurityConfig,
    pub networking: NetworkingConfig,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ConsciousnessConfig {
    pub enabled: bool,
    pub neural_darwinism: bool,
    pub population_size: usize,
    pub mutation_rate: f64,
    pub selection_pressure: f64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AIRuntimeConfig {
    pub tensorflow_lite: bool,
    pub onnx_runtime: bool,
    pub pytorch_mobile: bool,
    pub hardware_acceleration: bool,
    pub gpu_support: bool,
    pub npu_support: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SecurityConfig {
    pub orchestration_enabled: bool,
    pub tools: Vec<String>,
    pub ai_analysis: bool,
    pub threat_intelligence: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct NetworkingConfig {
    pub bind_address: String,
    pub port: u16,
    pub tls_enabled: bool,
}

impl Default for SynOSConfig {
    fn default() -> Self {
        Self {
            consciousness: ConsciousnessConfig {
                enabled: true,
                neural_darwinism: true,
                population_size: 1000,
                mutation_rate: 0.1,
                selection_pressure: 0.7,
            },
            ai_runtime: AIRuntimeConfig {
                tensorflow_lite: true,
                onnx_runtime: true,
                pytorch_mobile: true,
                hardware_acceleration: true,
                gpu_support: true,
                npu_support: true,
            },
            security: SecurityConfig {
                orchestration_enabled: true,
                tools: vec![
                    "nmap".to_string(),
                    "metasploit".to_string(),
                    "burpsuite".to_string(),
                    "wireshark".to_string(),
                ],
                ai_analysis: true,
                threat_intelligence: true,
            },
            networking: NetworkingConfig {
                bind_address: "0.0.0.0".to_string(),
                port: 8080,
                tls_enabled: true,
            },
        }
    }
}

#[derive(Debug)]
pub struct SynOSAIDaemon {
    id: Uuid,
    config: Arc<RwLock<SynOSConfig>>,
    consciousness: Arc<ConsciousnessEngine>,
    ai_runtime: Arc<AIRuntimeManager>,
    personal_context: Arc<PersonalContextEngine>,
    security_orchestrator: Arc<SecurityOrchestrator>,
    vector_db: Arc<VectorDatabase>,
}

impl SynOSAIDaemon {
    pub async fn new(config: SynOSConfig) -> Result<Self> {
        let id = Uuid::new_v4();
        let config = Arc::new(RwLock::new(config));

        info!("🤖 Initializing SynOS AI Daemon {}", id);

        // Initialize core AI components
        let consciousness = Arc::new(
            ConsciousnessEngine::new(config.read().await.consciousness.clone()).await?
        );

        let ai_runtime = Arc::new(
            AIRuntimeManager::new(config.read().await.ai_runtime.clone()).await?
        );

        let vector_db = Arc::new(
            VectorDatabase::new().await?
        );

        let personal_context = Arc::new(
            PersonalContextEngine::new(vector_db.clone()).await?
        );

        let security_orchestrator = Arc::new(
            SecurityOrchestrator::new(
                config.read().await.security.clone(),
                ai_runtime.clone()
            ).await?
        );

        Ok(Self {
            id,
            config,
            consciousness,
            ai_runtime,
            personal_context,
            security_orchestrator,
            vector_db,
        })
    }

    pub async fn run(&self) -> Result<()> {
        info!("🚀 Starting SynOS AI Daemon services...");

        // Start consciousness engine
        if self.config.read().await.consciousness.enabled {
            info!("🧠 Starting Neural Darwinism consciousness system...");
            let consciousness_clone = self.consciousness.clone();
            tokio::spawn(async move {
                if let Err(e) = consciousness_clone.run().await {
                    error!("Consciousness engine error: {}", e);
                }
            });
        }

        // Start AI runtime
        info!("⚡ Starting AI runtime manager...");
        let runtime_clone = self.ai_runtime.clone();
        tokio::spawn(async move {
            if let Err(e) = runtime_clone.run().await {
                error!("AI runtime error: {}", e);
            }
        });

        // Start security orchestrator
        if self.config.read().await.security.orchestration_enabled {
            info!("🛡️  Starting security orchestrator...");
            let security_clone = self.security_orchestrator.clone();
            tokio::spawn(async move {
                if let Err(e) = security_clone.run().await {
                    error!("Security orchestrator error: {}", e);
                }
            });
        }

        // Start personal context engine
        info!("📚 Starting Personal Context Engine with RAG...");
        let context_clone = self.personal_context.clone();
        tokio::spawn(async move {
            if let Err(e) = context_clone.run().await {
                error!("Personal context engine error: {}", e);
            }
        });

        // Main daemon loop
        loop {
            // Health check and status reporting
            self.health_check().await?;

            // Process consciousness updates
            if let Err(e) = self.process_consciousness_updates().await {
                warn!("Consciousness update error: {}", e);
            }

            tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
        }
    }

    async fn health_check(&self) -> Result<()> {
        // Check consciousness system
        if self.config.read().await.consciousness.enabled {
            self.consciousness.health_check().await
                .context("Consciousness health check failed")?;
        }

        // Check AI runtime
        self.ai_runtime.health_check().await
            .context("AI runtime health check failed")?;

        // Check security orchestrator
        if self.config.read().await.security.orchestration_enabled {
            self.security_orchestrator.health_check().await
                .context("Security orchestrator health check failed")?;
        }

        Ok(())
    }

    async fn process_consciousness_updates(&self) -> Result<()> {
        if !self.config.read().await.consciousness.enabled {
            return Ok(());
        }

        // Get consciousness state
        let consciousness_state = self.consciousness.get_state().await?;

        // Update personal context with consciousness insights
        self.personal_context.update_consciousness_context(consciousness_state.clone()).await?;

        // Update security orchestrator with consciousness-driven priorities
        self.security_orchestrator.update_consciousness_priorities(consciousness_state).await?;

        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_target(false)
        .with_thread_ids(true)
        .with_level(true)
        .with_ansi(true)
        .init();

    let matches = Command::new("synos-ai-daemon")
        .version("2.0.0")
        .author("SynOS Development Team")
        .about("SynOS AI Consciousness Engine Daemon")
        .arg(
            Arg::new("config")
                .short('c')
                .long("config")
                .value_name("FILE")
                .help("Configuration file path")
                .default_value("/etc/synos/ai-engine.toml")
        )
        .arg(
            Arg::new("daemon")
                .short('d')
                .long("daemon")
                .help("Run as daemon")
                .action(clap::ArgAction::SetTrue)
        )
        .get_matches();

    let config_path = matches.get_one::<String>("config")
        .map(PathBuf::from)
        .unwrap();

    // Load configuration
    let config = if config_path.exists() {
        let config_str = tokio::fs::read_to_string(&config_path).await
            .context("Failed to read config file")?;
        toml::from_str(&config_str)
            .context("Failed to parse config file")?
    } else {
        warn!("Config file not found, using defaults");
        SynOSConfig::default()
    };

    info!("🎯 SynOS AI Daemon v2.0.0 starting...");
    info!("📁 Config: {}", config_path.display());
    info!("🆔 Daemon ID: {}", Uuid::new_v4());

    // Create and run daemon
    let daemon = SynOSAIDaemon::new(config).await?;
    daemon.run().await?;

    Ok(())
}