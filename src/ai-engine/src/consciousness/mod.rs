//! Consciousness Engine Module
//! 
//! Implements the Neural Darwinism-based consciousness system for SynapticOS.
//! This is the core differentiator that makes SynapticOS a consciousness-aware OS.

pub mod core;        // Core consciousness logic (from current consciousness.rs)
pub mod awareness;   // Environmental awareness
pub mod decision;    // Decision making processes
pub mod memory;      // Consciousness memory systems

pub use core::ConsciousnessEngine;

/// Consciousness state representation
#[derive(Debug, Clone, PartialEq)]
pub enum ConsciousnessState {
    Dormant,
    Awakening,
    Active,
    Learning,
    Reflecting,
    Error,
}

/// Consciousness metrics for monitoring
#[derive(Debug, Default, Clone)]
pub struct ConsciousnessMetrics {
    pub awareness_level: f32,
    pub decision_confidence: f32,
    pub learning_rate: f32,
    pub memory_coherence: f32,
    pub neural_activity: f32,
    pub processing_speed: f32,
}

/// Environmental stimulus that consciousness can process
#[derive(Debug, Clone)]
pub struct Stimulus {
    pub id: uuid::Uuid,
    pub stimulus_type: StimulusType,
    pub intensity: f32,
    pub data: Vec<u8>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Types of stimuli that can trigger consciousness
#[derive(Debug, Clone)]
pub enum StimulusType {
    SystemEvent,
    UserInteraction,
    AIProcessing,
    SecurityAlert,
    PerformanceMetric,
    ExternalSensor,
}

/// Decision made by consciousness system
#[derive(Debug, Clone)]
pub struct ConsciousDecision {
    pub id: uuid::Uuid,
    pub decision_type: DecisionType,
    pub confidence: f32,
    pub reasoning: String,
    pub actions: Vec<ConsciousAction>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Types of decisions consciousness can make
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum DecisionType {
    ResourceAllocation,
    TaskPrioritization,
    SecurityResponse,
    LearningAdjustment,
    SystemOptimization,
}

/// Actions that consciousness can take
#[derive(Debug, Clone)]
pub enum ConsciousAction {
    AllocateMemory { amount_mb: usize },
    PrioritizeTask { task_id: uuid::Uuid, new_priority: u8 },
    TriggerSecurityResponse { alert_level: u8 },
    AdjustLearningRate { new_rate: f32 },
    OptimizeSystem { optimization_type: String },
}

/// Consciousness configuration
#[derive(Debug, Clone)]
pub struct ConsciousnessConfig {
    pub enable_learning: bool,
    pub awareness_threshold: f32,
    pub decision_confidence_threshold: f32,
    pub memory_retention_hours: u64,
    pub neural_update_interval_ms: u64,
}

impl Default for ConsciousnessConfig {
    fn default() -> Self {
        Self {
            enable_learning: true,
            awareness_threshold: 0.5,
            decision_confidence_threshold: 0.7,
            memory_retention_hours: 24,
            neural_update_interval_ms: 100,
        }
    }
}

/// Initialize the consciousness module
pub fn init() -> anyhow::Result<()> {
    tracing::info!("Initializing Consciousness Module");
    Ok(())
}
