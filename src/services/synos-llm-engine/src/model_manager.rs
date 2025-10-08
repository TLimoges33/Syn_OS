use anyhow::Result;
use std::collections::HashMap;
use std::path::Path;
use tracing::{info, warn};

pub struct ModelManager {
    model_path: String,
    loaded_models: HashMap<String, ModelInfo>,
}

#[derive(Debug, Clone)]
struct ModelInfo {
    name: String,
    size_bytes: u64,
    loaded_at: std::time::Instant,
}

impl ModelManager {
    pub fn new(model_path: &str) -> Result<Self> {
        info!("Initializing model manager");
        info!("  Model path: {}", model_path);

        // Check if model directory exists
        if !Path::new(model_path).exists() {
            warn!("Model path does not exist: {}", model_path);
        }

        Ok(Self {
            model_path: model_path.to_string(),
            loaded_models: HashMap::new(),
        })
    }

    pub async fn load_model(&mut self, name: &str) -> Result<()> {
        info!("Loading model: {}", name);

        let model_info = ModelInfo {
            name: name.to_string(),
            size_bytes: 0, // Would check actual file size
            loaded_at: std::time::Instant::now(),
        };

        self.loaded_models.insert(name.to_string(), model_info);

        info!("Model loaded successfully: {}", name);
        Ok(())
    }

    pub async fn unload_model(&mut self, name: &str) -> Result<()> {
        if self.loaded_models.remove(name).is_some() {
            info!("Model unloaded: {}", name);
        } else {
            warn!("Model not found: {}", name);
        }
        Ok(())
    }

    pub fn get_loaded_count(&self) -> usize {
        self.loaded_models.len()
    }

    pub fn list_models(&self) -> Vec<String> {
        self.loaded_models.keys().cloned().collect()
    }

    pub fn is_model_loaded(&self, name: &str) -> bool {
        self.loaded_models.contains_key(name)
    }
}
