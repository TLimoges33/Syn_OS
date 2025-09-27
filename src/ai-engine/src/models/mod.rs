//! AI Models Module
//! 
//! Contains neural network models, machine learning components, and AI inference systems
//! used throughout SynapticOS.

pub mod neural;      // Neural network implementations
pub mod inference;   // Inference engines
pub mod learning;    // Learning algorithms
pub mod nlp;         // Natural language processing

pub use neural::NeuralNetwork;
pub use inference::InferenceEngine;

/// Model types supported by the AI engine
#[derive(Debug, Clone, PartialEq)]
pub enum ModelType {
    NeuralNetwork,
    DecisionTree,
    SupportVectorMachine,
    LinearRegression,
    NaturalLanguage,
    ComputerVision,
    Reinforcement,
}

/// Model configuration
#[derive(Debug, Clone)]
pub struct ModelConfig {
    pub model_type: ModelType,
    pub input_dimensions: usize,
    pub output_dimensions: usize,
    pub learning_rate: f32,
    pub batch_size: usize,
    pub epochs: usize,
    pub use_gpu: bool,
}

impl Default for ModelConfig {
    fn default() -> Self {
        Self {
            model_type: ModelType::NeuralNetwork,
            input_dimensions: 128,
            output_dimensions: 64,
            learning_rate: 0.001,
            batch_size: 32,
            epochs: 100,
            use_gpu: false,
        }
    }
}

/// Training data for models
#[derive(Debug, Clone)]
pub struct TrainingData {
    pub inputs: Vec<Vec<f32>>,
    pub targets: Vec<Vec<f32>>,
    pub validation_split: f32,
    pub shuffle: bool,
}

/// Model performance metrics
#[derive(Debug, Default, Clone)]
pub struct ModelMetrics {
    pub accuracy: f32,
    pub precision: f32,
    pub recall: f32,
    pub f1_score: f32,
    pub loss: f32,
    pub training_time_ms: u64,
    pub inference_time_ms: u64,
}

/// Prediction result from a model
#[derive(Debug, Clone)]
pub struct PredictionResult {
    pub predictions: Vec<f32>,
    pub confidence: f32,
    pub model_used: String,
    pub processing_time_ms: u64,
}

/// Initialize the models module
pub fn init() -> anyhow::Result<()> {
    tracing::info!("Initializing AI Models Module");
    Ok(())
}
