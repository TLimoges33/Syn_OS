use anyhow::{Context, Result};
use clap::{Arg, Command};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{error, info};

mod neural_darwinism;
mod pattern_recognition;
mod decision_engine;

use neural_darwinism::NeuralDarwinismEngine;
use pattern_recognition::PatternRecognizer;
use decision_engine::DecisionEngine;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ConsciousnessConfig {
    pub enabled: bool,
    pub population_size: usize,
    pub mutation_rate: f64,
    pub selection_pressure: f64,
    pub learning_rate: f64,
    pub pattern_threshold: f64,
}

impl Default for ConsciousnessConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            population_size: 1000,
            mutation_rate: 0.1,
            selection_pressure: 0.7,
            learning_rate: 0.01,
            pattern_threshold: 0.85,
        }
    }
}

pub struct ConsciousnessDaemon {
    config: ConsciousnessConfig,
    neural_engine: Arc<RwLock<NeuralDarwinismEngine>>,
    pattern_recognizer: Arc<RwLock<PatternRecognizer>>,
    decision_engine: Arc<RwLock<DecisionEngine>>,
}

impl ConsciousnessDaemon {
    pub fn new(config: ConsciousnessConfig) -> Result<Self> {
        info!("Initializing SynOS Consciousness Daemon...");

        let neural_engine = Arc::new(RwLock::new(
            NeuralDarwinismEngine::new(
                config.population_size,
                config.mutation_rate,
                config.selection_pressure,
            )?
        ));

        let pattern_recognizer = Arc::new(RwLock::new(
            PatternRecognizer::new(config.pattern_threshold)?
        ));

        let decision_engine = Arc::new(RwLock::new(
            DecisionEngine::new(config.learning_rate)?
        ));

        Ok(Self {
            config,
            neural_engine,
            pattern_recognizer,
            decision_engine,
        })
    }

    pub async fn run(&self) -> Result<()> {
        info!("Starting consciousness daemon...");

        // Spawn consciousness evolution task
        let neural_handle = {
            let engine = Arc::clone(&self.neural_engine);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = engine.write().await.evolve_population().await {
                        error!("Evolution error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
                }
            })
        };

        // Spawn pattern recognition task
        let pattern_handle = {
            let recognizer = Arc::clone(&self.pattern_recognizer);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = recognizer.write().await.analyze_patterns().await {
                        error!("Pattern analysis error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
                }
            })
        };

        // Spawn decision engine task
        let decision_handle = {
            let engine = Arc::clone(&self.decision_engine);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = engine.write().await.process_decisions().await {
                        error!("Decision processing error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
                }
            })
        };

        info!("Consciousness daemon running");

        // Wait for shutdown signal
        tokio::signal::ctrl_c().await?;

        info!("Shutting down consciousness daemon...");
        neural_handle.abort();
        pattern_handle.abort();
        decision_handle.abort();

        Ok(())
    }

    pub async fn get_status(&self) -> Result<ConsciousnessStatus> {
        let neural = self.neural_engine.read().await;
        let pattern = self.pattern_recognizer.read().await;
        let decision = self.decision_engine.read().await;

        Ok(ConsciousnessStatus {
            enabled: self.config.enabled,
            neural_generation: neural.get_generation(),
            patterns_recognized: pattern.get_pattern_count(),
            decisions_made: decision.get_decision_count(),
            fitness_score: neural.get_best_fitness(),
        })
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ConsciousnessStatus {
    pub enabled: bool,
    pub neural_generation: u64,
    pub patterns_recognized: usize,
    pub decisions_made: u64,
    pub fitness_score: f64,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_target(false)
        .with_thread_ids(true)
        .with_level(true)
        .init();

    let matches = Command::new("synos-consciousness-daemon")
        .version("1.0.0")
        .author("SynOS Team")
        .about("SynOS Neural Darwinism Consciousness Daemon")
        .arg(
            Arg::new("config")
                .short('c')
                .long("config")
                .value_name("FILE")
                .help("Configuration file path")
        )
        .arg(
            Arg::new("population-size")
                .long("population-size")
                .value_name("SIZE")
                .help("Neural population size")
                .default_value("1000")
        )
        .get_matches();

    let config = if let Some(config_path) = matches.get_one::<String>("config") {
        let content = std::fs::read_to_string(config_path)
            .context("Failed to read config file")?;
        serde_json::from_str(&content)
            .context("Failed to parse config file")?
    } else {
        ConsciousnessConfig::default()
    };

    info!("SynOS Consciousness Daemon v1.0.0");
    info!("Configuration: {:?}", config);

    let daemon = ConsciousnessDaemon::new(config)?;
    daemon.run().await?;

    Ok(())
}
