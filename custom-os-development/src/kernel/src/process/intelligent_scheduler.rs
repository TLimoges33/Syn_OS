//! Intelligent Process Scheduler with AI-Driven Load Balancing
//!
//! Provides advanced scheduling capabilities with consciousness integration,
//! predictive analytics, and adaptive load balancing for optimal system performance.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::sync::atomic::{AtomicU64, AtomicU32, Ordering};
use spin::{Mutex, RwLock};

use crate::process_lifecycle::{ProcessId, ProcessState, Priority, ProcessError};
use crate::process::migration::{ProcessMigrationManager, MigrationStrategy, CoreStats};
use syn_ai::ConsciousnessInterface;

/// AI-driven scheduling algorithms
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SchedulingAlgorithm {
    /// Traditional round-robin scheduling
    RoundRobin,
    /// Priority-based scheduling
    Priority,
    /// Completely Fair Scheduler (CFS)
    CompletelyFair,
    /// AI-driven consciousness-aware scheduling
    ConsciousnessAware,
    /// Predictive scheduling based on workload patterns
    Predictive,
    /// Adaptive hybrid algorithm
    AdaptiveHybrid,
}

/// Workload pattern classification
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WorkloadPattern {
    CPUIntensive,
    IOIntensive,
    Interactive,
    Batch,
    RealTime,
    Consciousness,
    Mixed,
    Unknown,
}

/// Process classification for intelligent scheduling
#[derive(Debug, Clone)]
pub struct ProcessClassification {
    pub pid: ProcessId,
    pub workload_pattern: WorkloadPattern,
    pub cpu_burst_prediction: f32,
    pub io_wait_prediction: f32,
    pub consciousness_requirement: f32,
    pub priority_recommendation: Priority,
    pub affinity_recommendation: Option<u32>,
    pub prediction_confidence: f32,
    pub last_classification: u64,
}

/// Load balancing strategy
#[derive(Debug, Clone)]
pub struct LoadBalancingStrategy {
    pub strategy_id: u32,
    pub name: String,
    pub algorithm: SchedulingAlgorithm,
    pub cpu_weight: f32,
    pub memory_weight: f32,
    pub io_weight: f32,
    pub consciousness_weight: f32,
    pub migration_threshold: f32,
    pub prediction_horizon: u64,
    pub enabled: bool,
}

/// Scheduling decision result
#[derive(Debug, Clone)]
pub struct SchedulingDecision {
    pub decision_id: u64,
    pub timestamp: u64,
    pub selected_process: ProcessId,
    pub target_core: u32,
    pub algorithm_used: SchedulingAlgorithm,
    pub decision_confidence: f32,
    pub predicted_execution_time: u64,
    pub reasoning: String,
    pub consciousness_factor: f32,
}

/// Performance prediction model
#[derive(Debug, Clone)]
pub struct PerformancePrediction {
    pub pid: ProcessId,
    pub predicted_cpu_usage: f32,
    pub predicted_memory_usage: f32,
    pub predicted_io_operations: u32,
    pub predicted_execution_time: u64,
    pub prediction_accuracy: f32,
    pub model_version: u32,
    pub features_used: Vec<String>,
}

/// AI learning data for scheduler improvement
#[derive(Debug, Clone)]
pub struct SchedulerLearningData {
    pub sample_id: u64,
    pub timestamp: u64,
    pub process_features: Vec<f32>,
    pub system_state: Vec<f32>,
    pub decision_made: SchedulingDecision,
    pub actual_performance: Option<PerformancePrediction>,
    pub success_metric: f32,
}

/// Intelligent scheduler with AI capabilities
pub struct IntelligentScheduler {
    ready_queues: RwLock<BTreeMap<Priority, Vec<ProcessId>>>,
    process_classifications: RwLock<BTreeMap<ProcessId, ProcessClassification>>,
    load_balancing_strategies: RwLock<Vec<LoadBalancingStrategy>>,
    scheduling_history: Mutex<Vec<SchedulingDecision>>,
    learning_data: Mutex<Vec<SchedulerLearningData>>,
    performance_predictions: RwLock<BTreeMap<ProcessId, PerformancePrediction>>,
    consciousness_interface: ConsciousnessInterface,
    migration_manager: ProcessMigrationManager,
    current_algorithm: AtomicU32,
    next_decision_id: AtomicU64,
    next_sample_id: AtomicU64,
    time_slice: u64,
    learning_enabled: bool,
    prediction_enabled: bool,
}

impl IntelligentScheduler {
    /// Create a new intelligent scheduler
    pub fn new() -> Self {
        let mut scheduler = Self {
            ready_queues: RwLock::new(BTreeMap::new()),
            process_classifications: RwLock::new(BTreeMap::new()),
            load_balancing_strategies: RwLock::new(Vec::new()),
            scheduling_history: Mutex::new(Vec::new()),
            learning_data: Mutex::new(Vec::new()),
            performance_predictions: RwLock::new(BTreeMap::new()),
            consciousness_interface: ConsciousnessInterface::new(),
            migration_manager: ProcessMigrationManager::new(),
            current_algorithm: AtomicU32::new(SchedulingAlgorithm::AdaptiveHybrid as u32),
            next_decision_id: AtomicU64::new(1),
            next_sample_id: AtomicU64::new(1),
            time_slice: 10000, // 10ms default time slice
            learning_enabled: true,
            prediction_enabled: true,
        };

        scheduler.initialize_default_strategies();
        scheduler
    }

    /// Initialize default load balancing strategies
    fn initialize_default_strategies(&self) {
        let strategies = vec![
            LoadBalancingStrategy {
                strategy_id: 1,
                name: "CPU Optimized".to_string(),
                algorithm: SchedulingAlgorithm::CompletelyFair,
                cpu_weight: 0.6,
                memory_weight: 0.2,
                io_weight: 0.1,
                consciousness_weight: 0.1,
                migration_threshold: 0.15,
                prediction_horizon: 5000,
                enabled: true,
            },
            LoadBalancingStrategy {
                strategy_id: 2,
                name: "Consciousness Optimized".to_string(),
                algorithm: SchedulingAlgorithm::ConsciousnessAware,
                cpu_weight: 0.2,
                memory_weight: 0.2,
                io_weight: 0.1,
                consciousness_weight: 0.5,
                migration_threshold: 0.2,
                prediction_horizon: 10000,
                enabled: true,
            },
            LoadBalancingStrategy {
                strategy_id: 3,
                name: "Interactive Optimized".to_string(),
                algorithm: SchedulingAlgorithm::Predictive,
                cpu_weight: 0.3,
                memory_weight: 0.2,
                io_weight: 0.3,
                consciousness_weight: 0.2,
                migration_threshold: 0.1,
                prediction_horizon: 2000,
                enabled: true,
            },
        ];

        *self.load_balancing_strategies.write() = strategies;
    }

    /// Add a process to the ready queue
    pub fn add_process(&self, pid: ProcessId, priority: Priority) -> Result<(), ProcessError> {
        // Classify the process
        self.classify_process(pid)?;

        // Add to appropriate ready queue
        let mut queues = self.ready_queues.write();
        queues.entry(priority).or_insert_with(Vec::new).push(pid);

        Ok(())
    }

    /// Remove a process from ready queues
    pub fn remove_process(&self, pid: ProcessId) -> Result<(), ProcessError> {
        let mut queues = self.ready_queues.write();

        for (_, queue) in queues.iter_mut() {
            queue.retain(|&p| p != pid);
        }

        // Clean up classification data
        self.process_classifications.write().remove(&pid);
        self.performance_predictions.write().remove(&pid);

        Ok(())
    }

    /// Classify a process based on historical data and patterns
    fn classify_process(&self, pid: ProcessId) -> Result<(), ProcessError> {
        // Gather process characteristics (simplified)
        let cpu_history = self.get_cpu_usage_history(pid);
        let io_history = self.get_io_usage_history(pid);
        let consciousness_score = self.consciousness_interface.get_process_consciousness(pid);

        // Analyze patterns to determine workload type
        let workload_pattern = self.analyze_workload_pattern(&cpu_history, &io_history);

        // Predict resource requirements
        let cpu_burst_prediction = self.predict_cpu_burst(pid, &cpu_history);
        let io_wait_prediction = self.predict_io_wait(pid, &io_history);

        // Determine optimal priority and affinity
        let priority_recommendation = self.recommend_priority(workload_pattern, consciousness_score);
        let affinity_recommendation = self.recommend_affinity(pid, workload_pattern);

        let classification = ProcessClassification {
            pid,
            workload_pattern,
            cpu_burst_prediction,
            io_wait_prediction,
            consciousness_requirement: consciousness_score,
            priority_recommendation,
            affinity_recommendation,
            prediction_confidence: self.calculate_prediction_confidence(pid),
            last_classification: get_current_time(),
        };

        self.process_classifications.write().insert(pid, classification);

        Ok(())
    }

    /// Analyze workload pattern from historical data
    fn analyze_workload_pattern(&self, cpu_history: &[f32], io_history: &[f32]) -> WorkloadPattern {
        if cpu_history.is_empty() || io_history.is_empty() {
            return WorkloadPattern::Unknown;
        }

        let avg_cpu: f32 = cpu_history.iter().sum::<f32>() / cpu_history.len() as f32;
        let avg_io: f32 = io_history.iter().sum::<f32>() / io_history.len() as f32;

        // Classify based on resource usage patterns
        match (avg_cpu, avg_io) {
            (cpu, io) if cpu > 80.0 && io < 20.0 => WorkloadPattern::CPUIntensive,
            (cpu, io) if cpu < 30.0 && io > 60.0 => WorkloadPattern::IOIntensive,
            (cpu, io) if cpu < 50.0 && io < 50.0 => WorkloadPattern::Interactive,
            (cpu, io) if cpu > 60.0 && io > 40.0 => WorkloadPattern::Mixed,
            _ => WorkloadPattern::Batch,
        }
    }

    /// Select the next process to run using AI-driven decision making
    pub fn schedule_next(&self) -> Result<Option<SchedulingDecision>, ProcessError> {
        let current_algorithm = self.get_current_algorithm();
        let system_state = self.gather_system_state();

        let decision = match current_algorithm {
            SchedulingAlgorithm::ConsciousnessAware => self.schedule_consciousness_aware(&system_state)?,
            SchedulingAlgorithm::Predictive => self.schedule_predictive(&system_state)?,
            SchedulingAlgorithm::AdaptiveHybrid => self.schedule_adaptive_hybrid(&system_state)?,
            SchedulingAlgorithm::CompletelyFair => self.schedule_completely_fair(&system_state)?,
            SchedulingAlgorithm::Priority => self.schedule_priority_based(&system_state)?,
            SchedulingAlgorithm::RoundRobin => self.schedule_round_robin(&system_state)?,
        };

        if let Some(ref decision) = decision {
            // Record the decision for learning
            self.record_scheduling_decision(decision.clone());

            // Update process predictions
            self.update_performance_predictions(decision.selected_process, decision);
        }

        Ok(decision)
    }

    /// Consciousness-aware scheduling algorithm
    fn schedule_consciousness_aware(&self, system_state: &SystemState) -> Result<Option<SchedulingDecision>, ProcessError> {
        let queues = self.ready_queues.read();
        let classifications = self.process_classifications.read();

        let mut best_candidate: Option<(ProcessId, f32)> = None;

        for (priority, queue) in queues.iter() {
            for &pid in queue {
                if let Some(classification) = classifications.get(&pid) {
                    // Calculate consciousness-aware score
                    let consciousness_score = classification.consciousness_requirement;
                    let priority_score = *priority as u32 as f32;
                    let system_load_factor = 1.0 - (system_state.cpu_utilization / 100.0);

                    let total_score = consciousness_score * 0.5 + priority_score * 0.3 + system_load_factor * 0.2;

                    if best_candidate.is_none() || total_score > best_candidate.as_ref().unwrap().1 {
                        best_candidate = Some((pid, total_score));
                    }
                }
            }
        }

        if let Some((selected_pid, score)) = best_candidate {
            let decision = SchedulingDecision {
                decision_id: self.next_decision_id.fetch_add(1, Ordering::SeqCst),
                timestamp: get_current_time(),
                selected_process: selected_pid,
                target_core: self.select_optimal_core(selected_pid, system_state),
                algorithm_used: SchedulingAlgorithm::ConsciousnessAware,
                decision_confidence: score / 100.0,
                predicted_execution_time: self.predict_execution_time(selected_pid),
                reasoning: format!("Consciousness-aware selection: score {:.2}", score),
                consciousness_factor: score,
            };

            Ok(Some(decision))
        } else {
            Ok(None)
        }
    }

    /// Predictive scheduling algorithm
    fn schedule_predictive(&self, system_state: &SystemState) -> Result<Option<SchedulingDecision>, ProcessError> {
        let queues = self.ready_queues.read();
        let predictions = self.performance_predictions.read();

        let mut best_candidate: Option<(ProcessId, f32)> = None;

        for (priority, queue) in queues.iter() {
            for &pid in queue {
                if let Some(prediction) = predictions.get(&pid) {
                    // Calculate predictive score based on expected performance
                    let cpu_efficiency = 100.0 - prediction.predicted_cpu_usage;
                    let memory_efficiency = 100.0 - prediction.predicted_memory_usage;
                    let execution_speed = 1000.0 / prediction.predicted_execution_time.max(1) as f32;

                    let predictive_score = (cpu_efficiency + memory_efficiency) * 0.4 + execution_speed * 0.2;

                    if best_candidate.is_none() || predictive_score > best_candidate.as_ref().unwrap().1 {
                        best_candidate = Some((pid, predictive_score));
                    }
                }
            }
        }

        if let Some((selected_pid, score)) = best_candidate {
            let decision = SchedulingDecision {
                decision_id: self.next_decision_id.fetch_add(1, Ordering::SeqCst),
                timestamp: get_current_time(),
                selected_process: selected_pid,
                target_core: self.select_optimal_core(selected_pid, system_state),
                algorithm_used: SchedulingAlgorithm::Predictive,
                decision_confidence: score / 100.0,
                predicted_execution_time: self.predict_execution_time(selected_pid),
                reasoning: format!("Predictive selection: score {:.2}", score),
                consciousness_factor: 0.0,
            };

            Ok(Some(decision))
        } else {
            Ok(None)
        }
    }

    /// Adaptive hybrid scheduling algorithm
    fn schedule_adaptive_hybrid(&self, system_state: &SystemState) -> Result<Option<SchedulingDecision>, ProcessError> {
        // Determine best algorithm based on current system state
        let optimal_algorithm = self.select_optimal_algorithm(system_state);

        match optimal_algorithm {
            SchedulingAlgorithm::ConsciousnessAware => self.schedule_consciousness_aware(system_state),
            SchedulingAlgorithm::Predictive => self.schedule_predictive(system_state),
            SchedulingAlgorithm::CompletelyFair => self.schedule_completely_fair(system_state),
            _ => self.schedule_priority_based(system_state),
        }
    }

    /// Select optimal algorithm based on system state
    fn select_optimal_algorithm(&self, system_state: &SystemState) -> SchedulingAlgorithm {
        // Use consciousness insights to determine best algorithm
        let consciousness_activity = self.consciousness_interface.get_system_consciousness_score();

        if consciousness_activity > 70.0 {
            SchedulingAlgorithm::ConsciousnessAware
        } else if system_state.cpu_utilization > 80.0 {
            SchedulingAlgorithm::Predictive
        } else if system_state.interactive_processes > system_state.total_processes / 2 {
            SchedulingAlgorithm::CompletelyFair
        } else {
            SchedulingAlgorithm::Priority
        }
    }

    /// Completely Fair Scheduler implementation
    fn schedule_completely_fair(&self, _system_state: &SystemState) -> Result<Option<SchedulingDecision>, ProcessError> {
        // Simplified CFS implementation
        // In a real implementation, this would use virtual runtime calculations
        let queues = self.ready_queues.read();

        for priority in [Priority::Realtime, Priority::High, Priority::Normal, Priority::Low] {
            if let Some(queue) = queues.get(&priority) {
                if let Some(&selected_pid) = queue.first() {
                    let decision = SchedulingDecision {
                        decision_id: self.next_decision_id.fetch_add(1, Ordering::SeqCst),
                        timestamp: get_current_time(),
                        selected_process: selected_pid,
                        target_core: 0, // Simplified
                        algorithm_used: SchedulingAlgorithm::CompletelyFair,
                        decision_confidence: 0.8,
                        predicted_execution_time: self.time_slice,
                        reasoning: "CFS selection".to_string(),
                        consciousness_factor: 0.0,
                    };

                    return Ok(Some(decision));
                }
            }
        }

        Ok(None)
    }

    /// Priority-based scheduling
    fn schedule_priority_based(&self, _system_state: &SystemState) -> Result<Option<SchedulingDecision>, ProcessError> {
        let queues = self.ready_queues.read();

        for priority in [Priority::Realtime, Priority::High, Priority::Normal, Priority::Low] {
            if let Some(queue) = queues.get(&priority) {
                if let Some(&selected_pid) = queue.first() {
                    let decision = SchedulingDecision {
                        decision_id: self.next_decision_id.fetch_add(1, Ordering::SeqCst),
                        timestamp: get_current_time(),
                        selected_process: selected_pid,
                        target_core: 0, // Simplified
                        algorithm_used: SchedulingAlgorithm::Priority,
                        decision_confidence: 0.9,
                        predicted_execution_time: self.time_slice,
                        reasoning: format!("Priority selection: {:?}", priority),
                        consciousness_factor: 0.0,
                    };

                    return Ok(Some(decision));
                }
            }
        }

        Ok(None)
    }

    /// Round-robin scheduling
    fn schedule_round_robin(&self, _system_state: &SystemState) -> Result<Option<SchedulingDecision>, ProcessError> {
        let queues = self.ready_queues.read();

        // Simple round-robin through all ready processes
        for (priority, queue) in queues.iter() {
            if let Some(&selected_pid) = queue.first() {
                let decision = SchedulingDecision {
                    decision_id: self.next_decision_id.fetch_add(1, Ordering::SeqCst),
                    timestamp: get_current_time(),
                    selected_process: selected_pid,
                    target_core: 0, // Simplified
                    algorithm_used: SchedulingAlgorithm::RoundRobin,
                    decision_confidence: 0.7,
                    predicted_execution_time: self.time_slice,
                    reasoning: "Round-robin selection".to_string(),
                    consciousness_factor: 0.0,
                };

                return Ok(Some(decision));
            }
        }

        Ok(None)
    }

    /// Select optimal core for process execution
    fn select_optimal_core(&self, pid: ProcessId, system_state: &SystemState) -> u32 {
        let classifications = self.process_classifications.read();

        if let Some(classification) = classifications.get(&pid) {
            if let Some(affinity) = classification.affinity_recommendation {
                return affinity;
            }
        }

        // Select core with lowest load
        system_state.core_loads.iter()
            .enumerate()
            .min_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
            .map(|(index, _)| index as u32)
            .unwrap_or(0)
    }

    /// Helper methods for data gathering and prediction
    fn get_cpu_usage_history(&self, _pid: ProcessId) -> Vec<f32> {
        // Placeholder - would return actual CPU usage history
        vec![50.0, 55.0, 45.0, 60.0, 52.0]
    }

    fn get_io_usage_history(&self, _pid: ProcessId) -> Vec<f32> {
        // Placeholder - would return actual I/O usage history
        vec![20.0, 25.0, 15.0, 30.0, 22.0]
    }

    fn predict_cpu_burst(&self, _pid: ProcessId, history: &[f32]) -> f32 {
        if history.is_empty() {
            return 50.0;
        }
        history.iter().sum::<f32>() / history.len() as f32
    }

    fn predict_io_wait(&self, _pid: ProcessId, history: &[f32]) -> f32 {
        if history.is_empty() {
            return 20.0;
        }
        history.iter().sum::<f32>() / history.len() as f32
    }

    fn recommend_priority(&self, pattern: WorkloadPattern, consciousness_score: f32) -> Priority {
        match pattern {
            WorkloadPattern::RealTime => Priority::Realtime,
            WorkloadPattern::Interactive => Priority::High,
            WorkloadPattern::Consciousness if consciousness_score > 70.0 => Priority::High,
            WorkloadPattern::CPUIntensive | WorkloadPattern::Mixed => Priority::Normal,
            _ => Priority::Low,
        }
    }

    fn recommend_affinity(&self, _pid: ProcessId, pattern: WorkloadPattern) -> Option<u32> {
        match pattern {
            WorkloadPattern::CPUIntensive => Some(0), // Prefer core 0 for CPU-intensive
            WorkloadPattern::Consciousness => Some(1), // Prefer core 1 for consciousness
            _ => None, // No specific affinity
        }
    }

    fn calculate_prediction_confidence(&self, _pid: ProcessId) -> f32 {
        // Simplified confidence calculation
        0.75
    }

    fn predict_execution_time(&self, pid: ProcessId) -> u64 {
        if let Some(prediction) = self.performance_predictions.read().get(&pid) {
            prediction.predicted_execution_time
        } else {
            self.time_slice
        }
    }

    fn gather_system_state(&self) -> SystemState {
        SystemState {
            cpu_utilization: 45.0, // Placeholder
            memory_utilization: 60.0,
            total_processes: 10,
            interactive_processes: 5,
            core_loads: vec![30.0, 50.0, 40.0, 35.0],
        }
    }

    fn get_current_algorithm(&self) -> SchedulingAlgorithm {
        match self.current_algorithm.load(Ordering::Relaxed) {
            0 => SchedulingAlgorithm::RoundRobin,
            1 => SchedulingAlgorithm::Priority,
            2 => SchedulingAlgorithm::CompletelyFair,
            3 => SchedulingAlgorithm::ConsciousnessAware,
            4 => SchedulingAlgorithm::Predictive,
            _ => SchedulingAlgorithm::AdaptiveHybrid,
        }
    }

    fn record_scheduling_decision(&self, decision: SchedulingDecision) {
        let mut history = self.scheduling_history.lock();
        history.push(decision);

        // Maintain history size
        if history.len() > 10000 {
            history.remove(0);
        }
    }

    fn update_performance_predictions(&self, _pid: ProcessId, _decision: &SchedulingDecision) {
        // Update predictions based on actual performance
        // This would implement machine learning feedback loop
    }
}

/// System state for scheduling decisions
#[derive(Debug, Clone)]
pub struct SystemState {
    pub cpu_utilization: f32,
    pub memory_utilization: f32,
    pub total_processes: u32,
    pub interactive_processes: u32,
    pub core_loads: Vec<f32>,
}

/// Global intelligent scheduler instance
pub static INTELLIGENT_SCHEDULER: RwLock<Option<IntelligentScheduler>> = RwLock::new(None);

/// Initialize the intelligent scheduler
pub fn init_intelligent_scheduler() -> Result<(), ProcessError> {
    let scheduler = IntelligentScheduler::new();
    *INTELLIGENT_SCHEDULER.write() = Some(scheduler);
    Ok(())
}

/// Schedule the next process
pub fn schedule_next_process() -> Result<Option<SchedulingDecision>, ProcessError> {
    if let Some(scheduler) = INTELLIGENT_SCHEDULER.read().as_ref() {
        scheduler.schedule_next()
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
    fn test_scheduler_creation() {
        let scheduler = IntelligentScheduler::new();
        assert!(scheduler.learning_enabled);
        assert!(scheduler.prediction_enabled);
    }

    #[test]
    fn test_process_classification() {
        let scheduler = IntelligentScheduler::new();
        let result = scheduler.classify_process(123);
        assert!(result.is_ok());

        let classifications = scheduler.process_classifications.read();
        assert!(classifications.contains_key(&123));
    }

    #[test]
    fn test_workload_pattern_analysis() {
        let scheduler = IntelligentScheduler::new();

        // Test CPU intensive pattern
        let cpu_history = vec![90.0, 95.0, 88.0, 92.0];
        let io_history = vec![5.0, 8.0, 12.0, 6.0];
        let pattern = scheduler.analyze_workload_pattern(&cpu_history, &io_history);
        assert_eq!(pattern, WorkloadPattern::CPUIntensive);

        // Test I/O intensive pattern
        let cpu_history = vec![20.0, 25.0, 18.0, 22.0];
        let io_history = vec![70.0, 80.0, 65.0, 75.0];
        let pattern = scheduler.analyze_workload_pattern(&cpu_history, &io_history);
        assert_eq!(pattern, WorkloadPattern::IOIntensive);
    }
}