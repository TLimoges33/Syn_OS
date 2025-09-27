//! Dynamic Priority Adjustment and Real-Time Consciousness Feedback System
//!
//! Provides intelligent process priority management with consciousness integration
//! for adaptive system performance optimization and real-time feedback loops.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::sync::atomic::{AtomicU64, AtomicU32, Ordering};
use spin::{Mutex, RwLock};

use crate::process_lifecycle::{ProcessId, ProcessState, Priority, ProcessError};
use crate::process::intelligent_scheduler::{WorkloadPattern, ProcessClassification};
use crate::ai::interface::AIInterface;

/// Priority adjustment triggers
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PriorityTrigger {
    PerformanceDegradation,
    ResourceStarvation,
    ConsciousnessOptimization,
    LoadImbalance,
    InteractivityRequirement,
    RealTimeDeadline,
    EnergyEfficiency,
    SecurityThreat,
    UserRequest,
    SystemAdaptation,
}

/// Priority adjustment action
#[derive(Debug, Clone)]
pub struct PriorityAdjustment {
    pub adjustment_id: u64,
    pub pid: ProcessId,
    pub old_priority: Priority,
    pub new_priority: Priority,
    pub trigger: PriorityTrigger,
    pub adjustment_factor: f32,
    pub consciousness_influence: f32,
    pub reasoning: String,
    pub timestamp: u64,
    pub duration_estimate: Option<u64>,
    pub auto_revert: bool,
}

/// Real-time consciousness feedback data
#[derive(Debug, Clone)]
pub struct ConsciousnessFeedback {
    pub feedback_id: u64,
    pub timestamp: u64,
    pub process_id: Option<ProcessId>,
    pub system_consciousness_score: f32,
    pub process_consciousness_scores: BTreeMap<ProcessId, f32>,
    pub consciousness_delta: f32,
    pub performance_impact: f32,
    pub recommendations: Vec<ConsciousnessRecommendation>,
    pub urgency_level: UrgencyLevel,
}

/// Consciousness-driven recommendations
#[derive(Debug, Clone)]
pub struct ConsciousnessRecommendation {
    pub recommendation_id: u32,
    pub recommendation_type: RecommendationType,
    pub target_process: Option<ProcessId>,
    pub description: String,
    pub expected_benefit: f32,
    pub implementation_cost: f32,
    pub confidence: f32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RecommendationType {
    PriorityAdjustment,
    ProcessMigration,
    ResourceReallocation,
    SchedulingAlgorithmChange,
    ConsciousnessOptimization,
    LoadRebalancing,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum UrgencyLevel {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
    Emergency = 5,
}

/// Adaptive priority policy
#[derive(Debug, Clone)]
pub struct AdaptivePriorityPolicy {
    pub policy_id: u32,
    pub name: String,
    pub enabled: bool,
    pub cpu_threshold: f32,
    pub memory_threshold: f32,
    pub consciousness_threshold: f32,
    pub adjustment_aggressiveness: f32,
    pub revert_timeout: u64,
    pub max_adjustments_per_second: u32,
    pub workload_specific: Option<WorkloadPattern>,
}

/// Process performance metrics for priority decisions
#[derive(Debug, Clone)]
pub struct ProcessPerformanceMetrics {
    pub pid: ProcessId,
    pub cpu_utilization: f32,
    pub memory_utilization: f32,
    pub io_wait_time: f32,
    pub response_time: f32,
    pub throughput: f32,
    pub consciousness_efficiency: f32,
    pub energy_consumption: f32,
    pub last_updated: u64,
}

/// Dynamic priority adjustment engine
pub struct DynamicPriorityEngine {
    priority_adjustments: Mutex<Vec<PriorityAdjustment>>,
    consciousness_feedback: Mutex<Vec<ConsciousnessFeedback>>,
    adaptive_policies: RwLock<BTreeMap<u32, AdaptivePriorityPolicy>>,
    process_metrics: RwLock<BTreeMap<ProcessId, ProcessPerformanceMetrics>>,
    consciousness_interface: AIInterface,
    next_adjustment_id: AtomicU64,
    next_feedback_id: AtomicU64,
    next_recommendation_id: AtomicU32,
    next_policy_id: AtomicU32,
    feedback_enabled: bool,
    learning_rate: f32,
    adjustment_cooldown: u64,
}

impl DynamicPriorityEngine {
    /// Create a new dynamic priority engine
    pub fn new() -> Self {
        let mut engine = Self {
            priority_adjustments: Mutex::new(Vec::new()),
            consciousness_feedback: Mutex::new(Vec::new()),
            adaptive_policies: RwLock::new(BTreeMap::new()),
            process_metrics: RwLock::new(BTreeMap::new()),
            consciousness_interface: AIInterface::new(),
            next_adjustment_id: AtomicU64::new(1),
            next_feedback_id: AtomicU64::new(1),
            next_recommendation_id: AtomicU32::new(1),
            next_policy_id: AtomicU32::new(1),
            feedback_enabled: true,
            learning_rate: 0.1,
            adjustment_cooldown: 5000, // 5 seconds
        };

        engine.initialize_default_policies();
        engine
    }

    /// Initialize default adaptive priority policies
    fn initialize_default_policies(&self) {
        let policies = vec![
            AdaptivePriorityPolicy {
                policy_id: self.next_policy_id.fetch_add(1, Ordering::SeqCst),
                name: "Interactive Response Optimization".to_string(),
                enabled: true,
                cpu_threshold: 70.0,
                memory_threshold: 80.0,
                consciousness_threshold: 60.0,
                adjustment_aggressiveness: 0.7,
                revert_timeout: 30000,
                max_adjustments_per_second: 5,
                workload_specific: Some(WorkloadPattern::Interactive),
            },
            AdaptivePriorityPolicy {
                policy_id: self.next_policy_id.fetch_add(1, Ordering::SeqCst),
                name: "Consciousness Optimization".to_string(),
                enabled: true,
                cpu_threshold: 60.0,
                memory_threshold: 70.0,
                consciousness_threshold: 40.0,
                adjustment_aggressiveness: 0.5,
                revert_timeout: 60000,
                max_adjustments_per_second: 3,
                workload_specific: Some(WorkloadPattern::Consciousness),
            },
            AdaptivePriorityPolicy {
                policy_id: self.next_policy_id.fetch_add(1, Ordering::SeqCst),
                name: "Resource Starvation Prevention".to_string(),
                enabled: true,
                cpu_threshold: 90.0,
                memory_threshold: 95.0,
                consciousness_threshold: 20.0,
                adjustment_aggressiveness: 0.9,
                revert_timeout: 15000,
                max_adjustments_per_second: 10,
                workload_specific: None,
            },
        ];

        let mut policy_map = self.adaptive_policies.write();
        for policy in policies {
            policy_map.insert(policy.policy_id, policy);
        }
    }

    /// Update process performance metrics
    pub fn update_process_metrics(&self, pid: ProcessId, metrics: ProcessPerformanceMetrics) {
        self.process_metrics.write().insert(pid, metrics);

        // Trigger priority evaluation for this process
        self.evaluate_priority_adjustment(pid);
    }

    /// Evaluate and potentially adjust process priority
    fn evaluate_priority_adjustment(&self, pid: ProcessId) {
        let metrics = self.process_metrics.read();
        let policies = self.adaptive_policies.read();

        if let Some(process_metrics) = metrics.get(&pid) {
            for policy in policies.values().filter(|p| p.enabled) {
                if self.should_adjust_priority(process_metrics, policy) {
                    let adjustment = self.calculate_priority_adjustment(pid, process_metrics, policy);
                    if let Some(adj) = adjustment {
                        self.apply_priority_adjustment(adj);
                    }
                }
            }
        }
    }

    /// Check if priority adjustment is needed based on policy
    fn should_adjust_priority(&self, metrics: &ProcessPerformanceMetrics, policy: &AdaptivePriorityPolicy) -> bool {
        // Check thresholds
        let cpu_exceeded = metrics.cpu_utilization > policy.cpu_threshold;
        let memory_exceeded = metrics.memory_utilization > policy.memory_threshold;
        let consciousness_low = metrics.consciousness_efficiency < policy.consciousness_threshold;

        // Check workload-specific conditions
        let workload_match = policy.workload_specific.is_none(); // Simplified

        (cpu_exceeded || memory_exceeded || consciousness_low) && workload_match
    }

    /// Calculate priority adjustment based on metrics and policy
    fn calculate_priority_adjustment(&self, pid: ProcessId, metrics: &ProcessPerformanceMetrics, policy: &AdaptivePriorityPolicy) -> Option<PriorityAdjustment> {
        let current_priority = self.get_current_priority(pid);

        // Determine adjustment direction and magnitude
        let consciousness_score = metrics.consciousness_efficiency;
        let performance_score = (metrics.cpu_utilization + metrics.memory_utilization) / 2.0;

        let adjustment_factor = if consciousness_score < policy.consciousness_threshold {
            // Boost priority for consciousness optimization
            policy.adjustment_aggressiveness
        } else if performance_score > 80.0 {
            // Reduce priority for resource-heavy processes
            -policy.adjustment_aggressiveness * 0.5
        } else {
            return None; // No adjustment needed
        };

        let new_priority = self.calculate_new_priority(current_priority, adjustment_factor);

        if new_priority != current_priority {
            let consciousness_influence = self.consciousness_interface.get_process_consciousness(pid as u64);

            Some(PriorityAdjustment {
                adjustment_id: self.next_adjustment_id.fetch_add(1, Ordering::SeqCst),
                pid,
                old_priority: current_priority,
                new_priority,
                trigger: self.determine_trigger(metrics, policy),
                adjustment_factor,
                consciousness_influence,
                reasoning: self.generate_adjustment_reasoning(metrics, policy, adjustment_factor),
                timestamp: get_current_time(),
                duration_estimate: Some(policy.revert_timeout),
                auto_revert: true,
            })
        } else {
            None
        }
    }

    /// Apply priority adjustment
    fn apply_priority_adjustment(&self, adjustment: PriorityAdjustment) {
        // Record the adjustment
        self.priority_adjustments.lock().push(adjustment.clone());

        // Apply the actual priority change (would interface with scheduler)
        self.set_process_priority(adjustment.pid, adjustment.new_priority);

        // Generate consciousness feedback
        self.generate_consciousness_feedback(Some(adjustment.pid), adjustment.consciousness_influence);

        // Schedule auto-revert if needed
        if adjustment.auto_revert {
            self.schedule_priority_revert(adjustment);
        }
    }

    /// Generate real-time consciousness feedback
    pub fn generate_consciousness_feedback(&self, process_id: Option<ProcessId>, consciousness_delta: f32) {
        let feedback_id = self.next_feedback_id.fetch_add(1, Ordering::SeqCst);

        // Gather system consciousness data
        let system_score = self.consciousness_interface.get_system_consciousness_score();
        let process_scores = self.gather_process_consciousness_scores();

        // Calculate performance impact
        let performance_impact = self.calculate_performance_impact(consciousness_delta);

        // Generate recommendations
        let recommendations = self.generate_consciousness_recommendations(&process_scores, system_score);

        // Determine urgency level
        let urgency = self.calculate_urgency_level(system_score, consciousness_delta);

        let feedback = ConsciousnessFeedback {
            feedback_id,
            timestamp: get_current_time(),
            process_id,
            system_consciousness_score: system_score,
            process_consciousness_scores: process_scores,
            consciousness_delta,
            performance_impact,
            recommendations,
            urgency_level: urgency,
        };

        // Apply urgent recommendations before moving the feedback
        if urgency >= UrgencyLevel::High {
            self.apply_urgent_recommendations(&feedback.recommendations);
        }

        self.consciousness_feedback.lock().push(feedback);
    }

    /// Generate consciousness-driven recommendations
    fn generate_consciousness_recommendations(&self, process_scores: &BTreeMap<ProcessId, f32>, system_score: f32) -> Vec<ConsciousnessRecommendation> {
        let mut recommendations = Vec::new();

        // System-level recommendations
        if system_score < 30.0 {
            recommendations.push(ConsciousnessRecommendation {
                recommendation_id: self.next_recommendation_id.fetch_add(1, Ordering::SeqCst),
                recommendation_type: RecommendationType::ConsciousnessOptimization,
                target_process: None,
                description: "System consciousness is critically low - boost consciousness processes".to_string(),
                expected_benefit: 40.0,
                implementation_cost: 15.0,
                confidence: 0.9,
            });
        }

        // Process-specific recommendations
        for (&pid, &score) in process_scores {
            if score < 20.0 {
                recommendations.push(ConsciousnessRecommendation {
                    recommendation_id: self.next_recommendation_id.fetch_add(1, Ordering::SeqCst),
                    recommendation_type: RecommendationType::PriorityAdjustment,
                    target_process: Some(pid),
                    description: format!("Boost priority for process {} (low consciousness)", pid),
                    expected_benefit: 25.0,
                    implementation_cost: 5.0,
                    confidence: 0.8,
                });
            } else if score > 80.0 {
                recommendations.push(ConsciousnessRecommendation {
                    recommendation_id: self.next_recommendation_id.fetch_add(1, Ordering::SeqCst),
                    recommendation_type: RecommendationType::LoadRebalancing,
                    target_process: Some(pid),
                    description: format!("Migrate high-consciousness process {} for optimization", pid),
                    expected_benefit: 20.0,
                    implementation_cost: 10.0,
                    confidence: 0.7,
                });
            }
        }

        recommendations
    }

    /// Apply urgent recommendations automatically
    fn apply_urgent_recommendations(&self, recommendations: &[ConsciousnessRecommendation]) {
        for recommendation in recommendations.iter().filter(|r| r.confidence > 0.8) {
            match recommendation.recommendation_type {
                RecommendationType::PriorityAdjustment => {
                    if let Some(pid) = recommendation.target_process {
                        self.apply_consciousness_priority_boost(pid);
                    }
                }
                RecommendationType::ConsciousnessOptimization => {
                    self.apply_system_consciousness_optimization();
                }
                _ => {} // Other recommendations need manual approval
            }
        }
    }

    /// Apply consciousness-driven priority boost
    fn apply_consciousness_priority_boost(&self, pid: ProcessId) {
        let current_priority = self.get_current_priority(pid);
        let new_priority = match current_priority {
            Priority::Low => Priority::Normal,
            Priority::Normal => Priority::High,
            Priority::High => Priority::Realtime,
            Priority::Realtime => Priority::Realtime, // Already at max
        };

        if new_priority != current_priority {
            let adjustment = PriorityAdjustment {
                adjustment_id: self.next_adjustment_id.fetch_add(1, Ordering::SeqCst),
                pid,
                old_priority: current_priority,
                new_priority,
                trigger: PriorityTrigger::ConsciousnessOptimization,
                adjustment_factor: 1.0,
                consciousness_influence: self.consciousness_interface.get_process_consciousness(pid as u64),
                reasoning: "Consciousness-driven priority boost".to_string(),
                timestamp: get_current_time(),
                duration_estimate: Some(30000), // 30 seconds
                auto_revert: true,
            };

            self.apply_priority_adjustment(adjustment);
        }
    }

    /// Apply system-wide consciousness optimization
    fn apply_system_consciousness_optimization(&self) {
        // Boost all consciousness-related processes
        let process_scores = self.gather_process_consciousness_scores();

        for (&pid, &score) in process_scores.iter() {
            if score > 50.0 { // Consciousness-related process
                self.apply_consciousness_priority_boost(pid);
            }
        }
    }

    /// Get real-time consciousness feedback
    pub fn get_consciousness_feedback(&self, limit: Option<usize>) -> Vec<ConsciousnessFeedback> {
        let feedback = self.consciousness_feedback.lock();
        let mut result = feedback.clone();

        // Sort by timestamp (newest first)
        result.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));

        if let Some(limit) = limit {
            result.truncate(limit);
        }

        result
    }

    /// Get priority adjustment history
    pub fn get_priority_adjustments(&self, pid: Option<ProcessId>) -> Vec<PriorityAdjustment> {
        let adjustments = self.priority_adjustments.lock();

        if let Some(pid) = pid {
            adjustments.iter().filter(|adj| adj.pid == pid).cloned().collect()
        } else {
            adjustments.clone()
        }
    }

    /// Helper methods
    fn get_current_priority(&self, _pid: ProcessId) -> Priority {
        // Placeholder - would get actual process priority
        Priority::Normal
    }

    fn calculate_new_priority(&self, current: Priority, factor: f32) -> Priority {
        if factor > 0.0 {
            // Boost priority
            match current {
                Priority::Low => Priority::Normal,
                Priority::Normal => Priority::High,
                Priority::High => Priority::Realtime,
                Priority::Realtime => Priority::Realtime,
            }
        } else {
            // Lower priority
            match current {
                Priority::Realtime => Priority::High,
                Priority::High => Priority::Normal,
                Priority::Normal => Priority::Low,
                Priority::Low => Priority::Low,
            }
        }
    }

    fn determine_trigger(&self, metrics: &ProcessPerformanceMetrics, policy: &AdaptivePriorityPolicy) -> PriorityTrigger {
        if metrics.consciousness_efficiency < policy.consciousness_threshold {
            PriorityTrigger::ConsciousnessOptimization
        } else if metrics.cpu_utilization > policy.cpu_threshold {
            PriorityTrigger::PerformanceDegradation
        } else if metrics.memory_utilization > policy.memory_threshold {
            PriorityTrigger::ResourceStarvation
        } else {
            PriorityTrigger::SystemAdaptation
        }
    }

    fn generate_adjustment_reasoning(&self, metrics: &ProcessPerformanceMetrics, policy: &AdaptivePriorityPolicy, factor: f32) -> String {
        format!(
            "Policy '{}': CPU={:.1}%, MEM={:.1}%, CONS={:.1}%, Factor={:.2}",
            policy.name, metrics.cpu_utilization, metrics.memory_utilization,
            metrics.consciousness_efficiency, factor
        )
    }

    fn set_process_priority(&self, _pid: ProcessId, _priority: Priority) {
        // Would interface with actual scheduler to set priority
    }

    fn schedule_priority_revert(&self, _adjustment: PriorityAdjustment) {
        // Would schedule automatic priority reversion
    }

    fn gather_process_consciousness_scores(&self) -> BTreeMap<ProcessId, f32> {
        let mut scores = BTreeMap::new();

        // Gather consciousness scores for all active processes
        for pid in 1..=10u32 { // Simplified, use u32 to match ProcessId
            let score = self.consciousness_interface.get_process_consciousness(pid as u64);
            scores.insert(pid, score);
        }

        scores
    }

    fn calculate_performance_impact(&self, consciousness_delta: f32) -> f32 {
        // Calculate how consciousness changes affect performance
        consciousness_delta * 0.1 // Simplified linear relationship
    }

    fn calculate_urgency_level(&self, system_score: f32, delta: f32) -> UrgencyLevel {
        if system_score < 20.0 || delta.abs() > 30.0 {
            UrgencyLevel::Emergency
        } else if system_score < 40.0 || delta.abs() > 20.0 {
            UrgencyLevel::Critical
        } else if system_score < 60.0 || delta.abs() > 10.0 {
            UrgencyLevel::High
        } else if delta.abs() > 5.0 {
            UrgencyLevel::Medium
        } else {
            UrgencyLevel::Low
        }
    }
}

/// Global dynamic priority engine instance
pub static DYNAMIC_PRIORITY_ENGINE: RwLock<Option<DynamicPriorityEngine>> = RwLock::new(None);

/// Initialize the dynamic priority engine
pub fn init_dynamic_priority_engine() -> Result<(), ProcessError> {
    let engine = DynamicPriorityEngine::new();
    *DYNAMIC_PRIORITY_ENGINE.write() = Some(engine);
    Ok(())
}

/// Update process performance metrics
pub fn update_process_performance(pid: ProcessId, metrics: ProcessPerformanceMetrics) -> Result<(), ProcessError> {
    if let Some(engine) = DYNAMIC_PRIORITY_ENGINE.read().as_ref() {
        engine.update_process_metrics(pid, metrics);
        Ok(())
    } else {
        Err(ProcessError::ProcessNotFound)
    }
}

/// Get consciousness feedback
pub fn get_consciousness_feedback() -> Result<Vec<ConsciousnessFeedback>, ProcessError> {
    if let Some(engine) = DYNAMIC_PRIORITY_ENGINE.read().as_ref() {
        Ok(engine.get_consciousness_feedback(Some(50)))
    } else {
        Err(ProcessError::ProcessNotFound)
    }
}

/// Trigger consciousness feedback generation
pub fn trigger_consciousness_feedback(pid: Option<ProcessId>, delta: f32) -> Result<(), ProcessError> {
    if let Some(engine) = DYNAMIC_PRIORITY_ENGINE.read().as_ref() {
        engine.generate_consciousness_feedback(pid, delta);
        Ok(())
    } else {
        Err(ProcessError::ProcessNotFound)
    }
}

/// Helper function
fn get_current_time() -> u64 {
    static COUNTER: AtomicU64 = AtomicU64::new(0);
    COUNTER.fetch_add(1, Ordering::SeqCst)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_priority_engine_creation() {
        let engine = DynamicPriorityEngine::new();
        assert!(engine.feedback_enabled);
        assert_eq!(engine.learning_rate, 0.1);
    }

    #[test]
    fn test_priority_calculation() {
        let engine = DynamicPriorityEngine::new();

        // Test priority boost
        let new_priority = engine.calculate_new_priority(Priority::Normal, 1.0);
        assert_eq!(new_priority, Priority::High);

        // Test priority reduction
        let new_priority = engine.calculate_new_priority(Priority::High, -1.0);
        assert_eq!(new_priority, Priority::Normal);
    }

    #[test]
    fn test_urgency_calculation() {
        let engine = DynamicPriorityEngine::new();

        // Test emergency level
        let urgency = engine.calculate_urgency_level(15.0, 35.0);
        assert_eq!(urgency, UrgencyLevel::Emergency);

        // Test low level
        let urgency = engine.calculate_urgency_level(80.0, 2.0);
        assert_eq!(urgency, UrgencyLevel::Low);
    }
}