//! Inference Engine Module
//! 
//! Handles model inference across different AI frameworks and provides
//! unified inference capabilities.

use super::{ModelConfig, PredictionResult};
use std::collections::HashMap;

/// Main inference engine
pub struct InferenceEngine {
    loaded_models: HashMap<String, Box<dyn InferenceModel>>,
}

/// Trait for inference models
pub trait InferenceModel {
    fn predict(&self, input: &[f32]) -> anyhow::Result<PredictionResult>;
    fn model_name(&self) -> &str;
    fn is_ready(&self) -> bool;
}

impl InferenceEngine {
    pub fn new() -> Self {
        Self {
            loaded_models: HashMap::new(),
        }
    }
    
    pub fn load_model(&mut self, name: String, model: Box<dyn InferenceModel>) {
        self.loaded_models.insert(name, model);
    }
    
    pub async fn infer(&self, model_name: &str, input: &[f32]) -> anyhow::Result<PredictionResult> {
        if let Some(model) = self.loaded_models.get(model_name) {
            model.predict(input)
        } else {
            Err(anyhow::anyhow!("Model not found: {}", model_name))
        }
    }
}
