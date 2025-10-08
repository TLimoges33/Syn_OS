//! Intelligent Process Affinity Management System
//!
//! This module provides consciousness-aware CPU affinity management for optimal
//! process placement across cores based on performance characteristics and AI patterns.

#![no_std]

use alloc::{collections::BTreeMap, vec::Vec, string::{String, ToString}, format};
use core::{fmt, cmp::Ordering};

/// Represents CPU core characteristics for affinity decisions
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct CoreCharacteristics {
    pub core_id: u32,
    pub performance_level: u8,     // 0-100 performance rating
    pub temperature: u8,           // Current temperature in Celsius
    pub current_load: u8,          // 0-100 current utilization
    pub cache_level: u8,           // Cache hierarchy level
    pub power_efficiency: u8,      // 0-100 power efficiency rating
    pub frequency: u32,            // Current frequency in MHz
}

/// Process characteristics that influence affinity decisions
#[derive(Debug, Clone, PartialEq)]
pub struct ProcessAffinityProfile {
    pub process_id: u64,
    pub cpu_intensity: u8,         // 0-100 CPU usage pattern
    pub memory_intensity: u8,      // 0-100 memory access pattern
    pub cache_sensitivity: u8,     // 0-100 cache miss impact
    pub latency_sensitivity: u8,   // 0-100 response time importance
    pub power_preference: PowerPreference,
    pub consciousness_priority: u8, // 0-100 consciousness system priority
    pub workload_type: WorkloadType,
}

/// Power consumption preferences for affinity management
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum PowerPreference {
    MaxPerformance,
    Balanced,
    PowerSaver,
    Adaptive,
}

/// Workload classification for optimized affinity
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum WorkloadType {
    Interactive,
    Compute,
    Memory,
    Network,
    Background,
    Consciousness,
    Security,
}

/// Affinity optimization strategies
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AffinityStrategy {
    Performance,           // Maximize computational performance
    PowerEfficiency,       // Minimize power consumption
    ThermalAware,         // Balance thermal characteristics
    CacheOptimized,       // Optimize for cache locality
    ConsciousnessGuided,  // Use AI consciousness for decisions
    Adaptive,             // Dynamic strategy selection
}

/// Affinity decision with reasoning
#[derive(Debug, Clone)]
pub struct AffinityDecision {
    pub process_id: u64,
    pub recommended_cores: Vec<u32>,
    pub primary_core: u32,
    pub confidence: u8,           // 0-100 confidence in decision
    pub reasoning: String,
    pub expected_benefit: u8,     // 0-100 expected performance gain
    pub migration_cost: u8,       // 0-100 cost of migration
}

/// Performance metrics for affinity validation
#[derive(Debug, Clone)]
pub struct AffinityMetrics {
    pub process_id: u64,
    pub core_utilization: BTreeMap<u32, u8>,
    pub cache_hit_rates: BTreeMap<u32, f32>,
    pub context_switches: u64,
    pub migration_count: u32,
    pub performance_score: u8,
    pub power_consumption: u32,   // mW
    pub thermal_impact: u8,       // 0-100 thermal contribution
}

/// Main intelligent affinity management system
#[derive(Debug)]
pub struct IntelligentAffinityManager {
    cores: BTreeMap<u32, CoreCharacteristics>,
    process_profiles: BTreeMap<u64, ProcessAffinityProfile>,
    current_affinities: BTreeMap<u64, Vec<u32>>,
    performance_history: BTreeMap<u64, Vec<AffinityMetrics>>,
    strategy: AffinityStrategy,
    optimization_enabled: bool,
    thermal_threshold: u8,
    load_balance_threshold: u8,
}

impl IntelligentAffinityManager {
    /// Create a new intelligent affinity manager
    pub fn new() -> Self {
        Self {
            cores: BTreeMap::new(),
            process_profiles: BTreeMap::new(),
            current_affinities: BTreeMap::new(),
            performance_history: BTreeMap::new(),
            strategy: AffinityStrategy::Adaptive,
            optimization_enabled: true,
            thermal_threshold: 85,
            load_balance_threshold: 80,
        }
    }

    /// Register a CPU core with its characteristics
    pub fn register_core(&mut self, core: CoreCharacteristics) {
        self.cores.insert(core.core_id, core);
    }

    /// Create or update process affinity profile
    pub fn profile_process(&mut self, profile: ProcessAffinityProfile) {
        self.process_profiles.insert(profile.process_id, profile);
    }

    /// Analyze optimal affinity for a process using consciousness
    pub fn analyze_optimal_affinity(&self, process_id: u64) -> Option<AffinityDecision> {
        let profile = self.process_profiles.get(&process_id)?;

        match self.strategy {
            AffinityStrategy::Performance => self.analyze_performance_affinity(profile),
            AffinityStrategy::PowerEfficiency => self.analyze_power_efficient_affinity(profile),
            AffinityStrategy::ThermalAware => self.analyze_thermal_aware_affinity(profile),
            AffinityStrategy::CacheOptimized => self.analyze_cache_optimized_affinity(profile),
            AffinityStrategy::ConsciousnessGuided => self.analyze_consciousness_guided_affinity(profile),
            AffinityStrategy::Adaptive => self.analyze_adaptive_affinity(profile),
        }
    }

    /// Performance-focused affinity analysis
    fn analyze_performance_affinity(&self, profile: &ProcessAffinityProfile) -> Option<AffinityDecision> {
        let mut best_cores = Vec::new();
        let mut scores = Vec::new();

        for (core_id, core) in &self.cores {
            let performance_score = self.calculate_performance_score(core, profile);
            scores.push((*core_id, performance_score));
        }

        // Sort by performance score
        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal));

        // Select top cores based on workload requirements
        let core_count = self.determine_optimal_core_count(profile);
        best_cores = scores.into_iter()
            .take(core_count)
            .map(|(core_id, _)| core_id)
            .collect();

        Some(AffinityDecision {
            process_id: profile.process_id,
            recommended_cores: best_cores.clone(),
            primary_core: best_cores.first().copied().unwrap_or(0),
            confidence: 85,
            reasoning: format!("Performance-optimized affinity for {} workload",
                             format!("{:?}", profile.workload_type).to_lowercase()),
            expected_benefit: 75,
            migration_cost: 25,
        })
    }

    /// Power-efficient affinity analysis
    fn analyze_power_efficient_affinity(&self, profile: &ProcessAffinityProfile) -> Option<AffinityDecision> {
        let mut efficient_cores = Vec::new();
        let mut scores = Vec::new();

        for (core_id, core) in &self.cores {
            let efficiency_score = self.calculate_power_efficiency_score(core, profile);
            scores.push((*core_id, efficiency_score));
        }

        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal));

        let core_count = core::cmp::min(self.determine_optimal_core_count(profile), 2);
        efficient_cores = scores.into_iter()
            .take(core_count)
            .map(|(core_id, _)| core_id)
            .collect();

        Some(AffinityDecision {
            process_id: profile.process_id,
            recommended_cores: efficient_cores.clone(),
            primary_core: efficient_cores.first().copied().unwrap_or(0),
            confidence: 80,
            reasoning: "Power-efficient core selection for reduced energy consumption".to_string(),
            expected_benefit: 65,
            migration_cost: 20,
        })
    }

    /// Thermal-aware affinity analysis
    fn analyze_thermal_aware_affinity(&self, profile: &ProcessAffinityProfile) -> Option<AffinityDecision> {
        let mut cool_cores = Vec::new();

        for (core_id, core) in &self.cores {
            if core.temperature < self.thermal_threshold {
                let thermal_score = (self.thermal_threshold - core.temperature) as f32 +
                                  (core.power_efficiency as f32 * 0.5);
                cool_cores.push((*core_id, thermal_score));
            }
        }

        cool_cores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal));

        let selected_cores: Vec<u32> = cool_cores.into_iter()
            .take(self.determine_optimal_core_count(profile))
            .map(|(core_id, _)| core_id)
            .collect();

        Some(AffinityDecision {
            process_id: profile.process_id,
            recommended_cores: selected_cores.clone(),
            primary_core: selected_cores.first().copied().unwrap_or(0),
            confidence: 90,
            reasoning: "Thermal-aware placement to prevent overheating".to_string(),
            expected_benefit: 70,
            migration_cost: 30,
        })
    }

    /// Cache-optimized affinity analysis
    fn analyze_cache_optimized_affinity(&self, profile: &ProcessAffinityProfile) -> Option<AffinityDecision> {
        let mut cache_scores = Vec::new();

        for (core_id, core) in &self.cores {
            let cache_benefit = self.calculate_cache_benefit(core, profile);
            cache_scores.push((*core_id, cache_benefit));
        }

        cache_scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal));

        let selected_cores: Vec<u32> = cache_scores.into_iter()
            .take(self.determine_optimal_core_count(profile))
            .map(|(core_id, _)| core_id)
            .collect();

        Some(AffinityDecision {
            process_id: profile.process_id,
            recommended_cores: selected_cores.clone(),
            primary_core: selected_cores.first().copied().unwrap_or(0),
            confidence: 88,
            reasoning: "Cache locality optimization for memory-intensive workload".to_string(),
            expected_benefit: 80,
            migration_cost: 35,
        })
    }

    /// Consciousness-guided affinity analysis
    fn analyze_consciousness_guided_affinity(&self, profile: &ProcessAffinityProfile) -> Option<AffinityDecision> {
        let consciousness_weight = profile.consciousness_priority as f32 / 100.0;
        let mut consciousness_scores = Vec::new();

        for (core_id, core) in &self.cores {
            let base_score = self.calculate_performance_score(core, profile);
            let consciousness_bonus = consciousness_weight * 50.0;
            let workload_modifier = self.get_workload_consciousness_modifier(profile.workload_type);

            let total_score = base_score + consciousness_bonus * workload_modifier;
            consciousness_scores.push((*core_id, total_score));
        }

        consciousness_scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal));

        let selected_cores: Vec<u32> = consciousness_scores.into_iter()
            .take(self.determine_optimal_core_count(profile))
            .map(|(core_id, _)| core_id)
            .collect();

        Some(AffinityDecision {
            process_id: profile.process_id,
            recommended_cores: selected_cores.clone(),
            primary_core: selected_cores.first().copied().unwrap_or(0),
            confidence: 95,
            reasoning: "AI consciousness-guided optimal placement with workload awareness".to_string(),
            expected_benefit: 90,
            migration_cost: 40,
        })
    }

    /// Adaptive affinity analysis that selects best strategy
    fn analyze_adaptive_affinity(&self, profile: &ProcessAffinityProfile) -> Option<AffinityDecision> {
        let strategies = [
            AffinityStrategy::Performance,
            AffinityStrategy::PowerEfficiency,
            AffinityStrategy::ThermalAware,
            AffinityStrategy::CacheOptimized,
            AffinityStrategy::ConsciousnessGuided,
        ];

        let mut best_decision = None;
        let mut best_score = 0.0;

        for strategy in &strategies {
            if let Some(decision) = match strategy {
                AffinityStrategy::Performance => self.analyze_performance_affinity(profile),
                AffinityStrategy::PowerEfficiency => self.analyze_power_efficient_affinity(profile),
                AffinityStrategy::ThermalAware => self.analyze_thermal_aware_affinity(profile),
                AffinityStrategy::CacheOptimized => self.analyze_cache_optimized_affinity(profile),
                AffinityStrategy::ConsciousnessGuided => self.analyze_consciousness_guided_affinity(profile),
                _ => None,
            } {
                let score = self.evaluate_decision_quality(&decision, profile);
                if score > best_score {
                    best_score = score;
                    best_decision = Some(decision);
                }
            }
        }

        if let Some(mut decision) = best_decision {
            decision.reasoning = format!("Adaptive strategy selection: {}", decision.reasoning);
            decision.confidence = core::cmp::min(decision.confidence + 5, 100);
            Some(decision)
        } else {
            None
        }
    }

    /// Calculate performance score for core-process pairing
    fn calculate_performance_score(&self, core: &CoreCharacteristics, profile: &ProcessAffinityProfile) -> f32 {
        let performance_factor = core.performance_level as f32;
        let load_penalty = core.current_load as f32 * 0.5;
        let frequency_bonus = (core.frequency as f32 / 1000.0) * 0.1;
        let workload_match = self.get_workload_core_match(profile.workload_type, core);

        performance_factor + frequency_bonus + workload_match - load_penalty
    }

    /// Calculate power efficiency score
    fn calculate_power_efficiency_score(&self, core: &CoreCharacteristics, profile: &ProcessAffinityProfile) -> f32 {
        let efficiency_base = core.power_efficiency as f32;
        let load_factor = (100 - core.current_load) as f32 * 0.3;
        let temperature_penalty = if core.temperature > 70 { 20.0 } else { 0.0 };

        efficiency_base + load_factor - temperature_penalty
    }

    /// Calculate cache benefit score
    fn calculate_cache_benefit(&self, core: &CoreCharacteristics, profile: &ProcessAffinityProfile) -> f32 {
        let cache_level_bonus = core.cache_level as f32 * 10.0;
        let sensitivity_factor = profile.cache_sensitivity as f32 * 0.5;
        let load_penalty = core.current_load as f32 * 0.3;

        cache_level_bonus * sensitivity_factor / 100.0 - load_penalty
    }

    /// Get workload-specific consciousness modifier
    fn get_workload_consciousness_modifier(&self, workload_type: WorkloadType) -> f32 {
        match workload_type {
            WorkloadType::Consciousness => 2.0,
            WorkloadType::Security => 1.5,
            WorkloadType::Interactive => 1.2,
            WorkloadType::Compute => 1.0,
            WorkloadType::Memory => 0.8,
            WorkloadType::Network => 0.7,
            WorkloadType::Background => 0.5,
        }
    }

    /// Get workload-core compatibility score
    fn get_workload_core_match(&self, workload_type: WorkloadType, core: &CoreCharacteristics) -> f32 {
        match workload_type {
            WorkloadType::Compute => core.performance_level as f32 * 0.8,
            WorkloadType::Interactive => (core.frequency as f32 / 100.0) * 0.3,
            WorkloadType::Memory => core.cache_level as f32 * 5.0,
            WorkloadType::Consciousness => core.performance_level as f32 * 0.6 + core.power_efficiency as f32 * 0.4,
            _ => 10.0,
        }
    }

    /// Determine optimal number of cores for process
    fn determine_optimal_core_count(&self, profile: &ProcessAffinityProfile) -> usize {
        match profile.workload_type {
            WorkloadType::Compute if profile.cpu_intensity > 80 => 4,
            WorkloadType::Compute => 2,
            WorkloadType::Interactive => 1,
            WorkloadType::Memory => 2,
            WorkloadType::Consciousness => 3,
            WorkloadType::Security => 2,
            _ => 1,
        }
    }

    /// Evaluate decision quality for adaptive strategy
    fn evaluate_decision_quality(&self, decision: &AffinityDecision, profile: &ProcessAffinityProfile) -> f32 {
        let confidence_weight = decision.confidence as f32 * 0.4;
        let benefit_weight = decision.expected_benefit as f32 * 0.4;
        let cost_penalty = decision.migration_cost as f32 * 0.2;

        confidence_weight + benefit_weight - cost_penalty
    }

    /// Apply affinity decision to process
    pub fn apply_affinity(&mut self, decision: AffinityDecision) -> Result<(), AffinityError> {
        if !self.optimization_enabled {
            return Err(AffinityError::OptimizationDisabled);
        }

        // Validate cores exist
        for core_id in &decision.recommended_cores {
            if !self.cores.contains_key(core_id) {
                return Err(AffinityError::InvalidCore(*core_id));
            }
        }

        // Store current affinity
        self.current_affinities.insert(
            decision.process_id,
            decision.recommended_cores.clone()
        );

        // Here would be the actual system call to set CPU affinity
        // For now, we'll simulate success
        Ok(())
    }

    /// Monitor affinity performance and adapt
    pub fn monitor_and_adapt(&mut self, metrics: AffinityMetrics) {
        // Store performance metrics
        self.performance_history
            .entry(metrics.process_id)
            .or_insert_with(Vec::new)
            .push(metrics.clone());

        // Limit history size
        if let Some(history) = self.performance_history.get_mut(&metrics.process_id) {
            if history.len() > 10 {
                history.remove(0);
            }
        }

        // Evaluate if adaptation is needed
        if self.should_adapt_affinity(&metrics) {
            if let Some(profile) = self.process_profiles.get(&metrics.process_id) {
                if let Some(new_decision) = self.analyze_optimal_affinity(metrics.process_id) {
                    let _ = self.apply_affinity(new_decision);
                }
            }
        }
    }

    /// Determine if affinity adaptation is needed
    fn should_adapt_affinity(&self, metrics: &AffinityMetrics) -> bool {
        metrics.performance_score < 60 ||
        metrics.migration_count > 5 ||
        metrics.thermal_impact > 80
    }

    /// Get current system load balance
    pub fn get_load_balance_status(&self) -> LoadBalanceStatus {
        let mut core_loads = Vec::new();
        let mut total_load = 0u32;

        for core in self.cores.values() {
            core_loads.push(core.current_load);
            total_load += core.current_load as u32;
        }

        let average_load = if !self.cores.is_empty() {
            total_load / self.cores.len() as u32
        } else {
            0
        };

        let max_load = core_loads.iter().max().copied().unwrap_or(0);
        let min_load = core_loads.iter().min().copied().unwrap_or(0);
        let load_variance = max_load.saturating_sub(min_load);

        LoadBalanceStatus {
            average_load: average_load as u8,
            max_load,
            min_load,
            load_variance,
            is_balanced: load_variance < 20,
            needs_rebalancing: load_variance > self.load_balance_threshold,
        }
    }

    /// Generate comprehensive affinity report
    pub fn generate_affinity_report(&self) -> AffinityReport {
        let total_processes = self.process_profiles.len();
        let optimized_processes = self.current_affinities.len();
        let optimization_rate = if total_processes > 0 {
            (optimized_processes as f32 / total_processes as f32) * 100.0
        } else {
            0.0
        };

        AffinityReport {
            total_processes,
            optimized_processes,
            optimization_rate,
            load_balance_status: self.get_load_balance_status(),
            strategy: self.strategy,
            thermal_violations: self.count_thermal_violations(),
            performance_gains: self.calculate_average_performance_gain(),
        }
    }

    /// Count thermal violations
    fn count_thermal_violations(&self) -> u32 {
        self.cores.values()
            .filter(|core| core.temperature > self.thermal_threshold)
            .count() as u32
    }

    /// Calculate average performance gain
    fn calculate_average_performance_gain(&self) -> f32 {
        let mut total_gain = 0.0;
        let mut count = 0;

        for history in self.performance_history.values() {
            if let Some(latest) = history.last() {
                total_gain += latest.performance_score as f32;
                count += 1;
            }
        }

        if count > 0 { total_gain / count as f32 } else { 0.0 }
    }
}

/// Load balance status information
#[derive(Debug, Clone)]
pub struct LoadBalanceStatus {
    pub average_load: u8,
    pub max_load: u8,
    pub min_load: u8,
    pub load_variance: u8,
    pub is_balanced: bool,
    pub needs_rebalancing: bool,
}

/// Comprehensive affinity management report
#[derive(Debug, Clone)]
pub struct AffinityReport {
    pub total_processes: usize,
    pub optimized_processes: usize,
    pub optimization_rate: f32,
    pub load_balance_status: LoadBalanceStatus,
    pub strategy: AffinityStrategy,
    pub thermal_violations: u32,
    pub performance_gains: f32,
}

/// Affinity management errors
#[derive(Debug, Clone, PartialEq)]
pub enum AffinityError {
    InvalidCore(u32),
    ProcessNotFound(u64),
    OptimizationDisabled,
    InsufficientCores,
    ThermalLimitExceeded,
    SystemError(String),
}

impl fmt::Display for AffinityError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AffinityError::InvalidCore(id) => write!(f, "Invalid core ID: {}", id),
            AffinityError::ProcessNotFound(pid) => write!(f, "Process not found: {}", pid),
            AffinityError::OptimizationDisabled => write!(f, "Affinity optimization is disabled"),
            AffinityError::InsufficientCores => write!(f, "Insufficient cores available"),
            AffinityError::ThermalLimitExceeded => write!(f, "Thermal limit exceeded"),
            AffinityError::SystemError(msg) => write!(f, "System error: {}", msg),
        }
    }
}

impl Default for IntelligentAffinityManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Utility functions for affinity management
impl IntelligentAffinityManager {
    /// Enable or disable affinity optimization
    pub fn set_optimization_enabled(&mut self, enabled: bool) {
        self.optimization_enabled = enabled;
    }

    /// Set thermal threshold for protection
    pub fn set_thermal_threshold(&mut self, threshold: u8) {
        self.thermal_threshold = threshold;
    }

    /// Set load balance threshold
    pub fn set_load_balance_threshold(&mut self, threshold: u8) {
        self.load_balance_threshold = threshold;
    }

    /// Change affinity strategy
    pub fn set_strategy(&mut self, strategy: AffinityStrategy) {
        self.strategy = strategy;
    }

    /// Get current affinity for process
    pub fn get_current_affinity(&self, process_id: u64) -> Option<&Vec<u32>> {
        self.current_affinities.get(&process_id)
    }

    /// Remove process from affinity management
    pub fn remove_process(&mut self, process_id: u64) {
        self.process_profiles.remove(&process_id);
        self.current_affinities.remove(&process_id);
        self.performance_history.remove(&process_id);
    }

    /// Get core information
    pub fn get_core_info(&self, core_id: u32) -> Option<&CoreCharacteristics> {
        self.cores.get(&core_id)
    }

    /// Update core characteristics
    pub fn update_core_characteristics(&mut self, core_id: u32, characteristics: CoreCharacteristics) {
        self.cores.insert(core_id, characteristics);
    }
}