use anyhow::{Context, Result};
use axum::{
    extract::State,
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use clap::{Arg, Command};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{error, info};

mod inference_engine;
mod model_manager;
mod prompt_optimizer;

use inference_engine::InferenceEngine;
use model_manager::ModelManager;
use prompt_optimizer::PromptOptimizer;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LlmConfig {
    pub enabled: bool,
    pub model_path: String,
    pub max_tokens: usize,
    pub temperature: f32,
    pub api_port: u16,
}

impl Default for LlmConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            model_path: "/opt/synos/models/llm".to_string(),
            max_tokens: 2048,
            temperature: 0.7,
            api_port: 8081,
        }
    }
}

pub struct LlmEngineState {
    config: LlmConfig,
    inference_engine: Arc<RwLock<InferenceEngine>>,
    model_manager: Arc<RwLock<ModelManager>>,
    prompt_optimizer: Arc<RwLock<PromptOptimizer>>,
}

impl LlmEngineState {
    pub fn new(config: LlmConfig) -> Result<Self> {
        info!("Initializing SynOS LLM Engine...");

        let inference_engine = Arc::new(RwLock::new(
            InferenceEngine::new(config.max_tokens, config.temperature)?
        ));

        let model_manager = Arc::new(RwLock::new(
            ModelManager::new(&config.model_path)?
        ));

        let prompt_optimizer = Arc::new(RwLock::new(
            PromptOptimizer::new()?
        ));

        Ok(Self {
            config,
            inference_engine,
            model_manager,
            prompt_optimizer,
        })
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct InferenceRequest {
    prompt: String,
    max_tokens: Option<usize>,
    temperature: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize)]
struct InferenceResponse {
    text: String,
    tokens_used: usize,
    inference_time_ms: u64,
}

#[derive(Debug, Serialize, Deserialize)]
struct StatusResponse {
    enabled: bool,
    models_loaded: usize,
    requests_processed: u64,
    uptime_seconds: u64,
}

async fn health_check() -> StatusCode {
    StatusCode::OK
}

async fn get_status(State(state): State<Arc<LlmEngineState>>) -> Json<StatusResponse> {
    let model_manager = state.model_manager.read().await;
    let inference_engine = state.inference_engine.read().await;

    Json(StatusResponse {
        enabled: state.config.enabled,
        models_loaded: model_manager.get_loaded_count(),
        requests_processed: inference_engine.get_request_count(),
        uptime_seconds: 0, // Would track actual uptime
    })
}

async fn inference(
    State(state): State<Arc<LlmEngineState>>,
    Json(request): Json<InferenceRequest>,
) -> Result<Json<InferenceResponse>, StatusCode> {
    let start = std::time::Instant::now();

    // Optimize prompt
    let optimized_prompt = {
        let mut optimizer = state.prompt_optimizer.write().await;
        optimizer
            .optimize(&request.prompt)
            .await
            .map_err(|e| {
                error!("Prompt optimization failed: {}", e);
                StatusCode::INTERNAL_SERVER_ERROR
            })?
    };

    // Run inference
    let result = {
        let mut engine = state.inference_engine.write().await;
        engine
            .infer(
                &optimized_prompt,
                request.max_tokens.unwrap_or(state.config.max_tokens),
                request.temperature.unwrap_or(state.config.temperature),
            )
            .await
            .map_err(|e| {
                error!("Inference failed: {}", e);
                StatusCode::INTERNAL_SERVER_ERROR
            })?
    };

    let inference_time = start.elapsed().as_millis() as u64;

    Ok(Json(InferenceResponse {
        text: result,
        tokens_used: request.max_tokens.unwrap_or(state.config.max_tokens),
        inference_time_ms: inference_time,
    }))
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_target(false)
        .with_thread_ids(true)
        .with_level(true)
        .init();

    let matches = Command::new("synos-llm-engine")
        .version("1.0.0")
        .author("SynOS Team")
        .about("SynOS Large Language Model Engine")
        .arg(
            Arg::new("config")
                .short('c')
                .long("config")
                .value_name("FILE")
                .help("Configuration file path")
        )
        .arg(
            Arg::new("port")
                .short('p')
                .long("port")
                .value_name("PORT")
                .help("API server port")
                .default_value("8081")
        )
        .get_matches();

    let config = if let Some(config_path) = matches.get_one::<String>("config") {
        let content = std::fs::read_to_string(config_path)
            .context("Failed to read config file")?;
        serde_json::from_str(&content)
            .context("Failed to parse config file")?
    } else {
        LlmConfig::default()
    };

    info!("SynOS LLM Engine v1.0.0");
    info!("Configuration: {:?}", config);

    let state = Arc::new(LlmEngineState::new(config.clone())?);

    // Build API router
    let app = Router::new()
        .route("/health", get(health_check))
        .route("/status", get(get_status))
        .route("/inference", post(inference))
        .with_state(state);

    let addr = format!("0.0.0.0:{}", config.api_port);
    let listener = tokio::net::TcpListener::bind(&addr).await?;

    info!("LLM Engine API listening on {}", addr);

    axum::serve(listener, app).await?;

    Ok(())
}
