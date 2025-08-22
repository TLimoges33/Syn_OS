// Pattern Recognition Module

extern crate alloc;

use alloc::string::String;
use alloc::vec::Vec;
use alloc::collections::BTreeMap;
use alloc::format;

/// Pattern data point
#[derive(Debug, Clone)]
pub struct DataPoint {
    pub values: Vec<f32>,
    pub label: Option<String>,
    pub timestamp: u64,
}

/// Recognized pattern
#[derive(Debug, Clone)]
pub struct Pattern {
    pub id: String,
    pub pattern_type: PatternType,
    pub confidence: f32,
    pub features: Vec<f32>,
    pub metadata: BTreeMap<String, String>,
}

/// Pattern types
#[derive(Debug, Clone)]
pub enum PatternType {
    Sequential,
    Spatial,
    Temporal,
    Anomaly,
    Cluster,
}

/// Pattern recognition engine
pub struct PatternRecognizer {
    known_patterns: Vec<Pattern>,
    learning_buffer: Vec<DataPoint>,
    recognition_threshold: f32,
}

impl PatternRecognizer {
    /// Create new pattern recognizer
    pub fn new() -> Self {
        Self {
            known_patterns: Vec::new(),
            learning_buffer: Vec::new(),
            recognition_threshold: 0.8,
        }
    }
    
    /// Add training data
    pub fn add_training_data(&mut self, data: DataPoint) {
        self.learning_buffer.push(data);
        
        // Simple learning - if buffer gets too large, create pattern
        if self.learning_buffer.len() > 10 {
            self.learn_patterns();
        }
    }
    
    /// Learn patterns from buffer
    fn learn_patterns(&mut self) {
        if self.learning_buffer.len() < 5 {
            return;
        }
        
        // Simple pattern creation - average the features
        let mut avg_features = Vec::new();
        if !self.learning_buffer.is_empty() {
            let feature_count = self.learning_buffer[0].values.len();
            avg_features.resize(feature_count, 0.0);
            
            for data in &self.learning_buffer {
                for (i, &val) in data.values.iter().enumerate() {
                    if i < avg_features.len() {
                        avg_features[i] += val;
                    }
                }
            }
        
            for feature in &mut avg_features {
                *feature /= self.learning_buffer.len() as f32;
            }
        }
        
        let pattern = Pattern {
            id: format!("pattern_{}", self.known_patterns.len()),
            pattern_type: PatternType::Cluster,
            confidence: 0.75,
            features: avg_features,
            metadata: BTreeMap::new(),
        };
        
        self.known_patterns.push(pattern);
        self.learning_buffer.clear();
    }
    
    /// Recognize pattern in data
    pub fn recognize(&self, data: &DataPoint) -> Option<Pattern> {
        let mut best_match = None;
        let mut best_similarity = 0.0;
        
        for pattern in &self.known_patterns {
            let similarity = self.calculate_similarity(&data.values, &pattern.features);
            if similarity > best_similarity && similarity >= self.recognition_threshold {
                best_similarity = similarity;
                best_match = Some(pattern.clone());
            }
        }
        
        best_match
    }
    
    /// Calculate similarity between two feature vectors
    fn calculate_similarity(&self, features1: &[f32], features2: &[f32]) -> f32 {
        if features1.len() != features2.len() {
            return 0.0;
        }
        
        // Simple cosine similarity
        let mut dot_product = 0.0;
        let mut norm1 = 0.0;
        let mut norm2 = 0.0;
        
        for (a, b) in features1.iter().zip(features2.iter()) {
            dot_product += a * b;
            norm1 += a * a;
            norm2 += b * b;
        }
        
        if norm1 == 0.0 || norm2 == 0.0 {
            return 0.0;
        }
        
        // Simple approximation for sqrt in no-std environment
        fn simple_sqrt(x: f32) -> f32 {
            if x <= 0.0 {
                return 0.0;
            }
            // Newton's method approximation
            let mut z = x;
            for _ in 0..10 {
                z = (z + x / z) / 2.0;
            }
            z
        }
        
        dot_product / (simple_sqrt(norm1) * simple_sqrt(norm2))
    }
    
    /// Get known patterns
    pub fn get_patterns(&self) -> &[Pattern] {
        &self.known_patterns
    }
    
    /// Set recognition threshold
    pub fn set_threshold(&mut self, threshold: f32) {
        self.recognition_threshold = threshold.clamp(0.0, 1.0);
    }
    
    /// Detect anomalies
    pub fn detect_anomaly(&self, data: &DataPoint) -> bool {
        // If no patterns match with high confidence, it might be an anomaly
        for pattern in &self.known_patterns {
            let similarity = self.calculate_similarity(&data.values, &pattern.features);
            if similarity > 0.6 {
                return false; // Not an anomaly
            }
        }
        true // Potential anomaly
    }
}

/// Global pattern recognizer
static mut GLOBAL_RECOGNIZER: Option<PatternRecognizer> = None;

/// Initialize pattern recognition module
pub fn init() {
    unsafe {
        GLOBAL_RECOGNIZER = Some(PatternRecognizer::new());
    }
}

/// Add training data globally
pub fn add_training_data(data: DataPoint) {
    unsafe {
        let recognizer_ptr = &raw mut GLOBAL_RECOGNIZER;
        if let Some(recognizer) = &mut *recognizer_ptr {
            recognizer.add_training_data(data);
        }
    }
}

/// Recognize pattern globally
pub fn recognize_pattern(data: &DataPoint) -> Option<Pattern> {
    unsafe {
        let recognizer_ptr = &raw const GLOBAL_RECOGNIZER;
        if let Some(recognizer) = &*recognizer_ptr {
            recognizer.recognize(data)
        } else {
            None
        }
    }
}

/// Detect anomaly globally
pub fn detect_anomaly(data: &DataPoint) -> bool {
    unsafe {
        let recognizer_ptr = &raw const GLOBAL_RECOGNIZER;
        if let Some(recognizer) = &*recognizer_ptr {
            recognizer.detect_anomaly(data)
        } else {
            false
        }
    }
}
