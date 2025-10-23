//! Environmental Awareness Module
//! 
//! Handles environmental sensing, context awareness, and situation assessment
//! for the consciousness system.

use super::{Stimulus, StimulusType};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

/// Environmental awareness system
pub struct EnvironmentalAwareness {
    sensors: Arc<RwLock<HashMap<String, Box<dyn EnvironmentalSensor + Send + Sync>>>>,
    context_memory: Arc<RwLock<ContextMemory>>,
    awareness_filters: Vec<AwarenessFilter>,
}

/// Context memory for environmental awareness
#[derive(Debug, Default)]
pub struct ContextMemory {
    current_context: EnvironmentalContext,
    context_history: Vec<EnvironmentalContext>,
    attention_focus: Vec<AttentionPoint>,
}

/// Current environmental context
#[derive(Debug, Clone, Default)]
pub struct EnvironmentalContext {
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub system_load: f32,
    pub user_activity: UserActivityLevel,
    pub security_state: SecurityState,
    pub resource_availability: ResourceState,
    pub external_connections: u32,
}

/// User activity levels
#[derive(Debug, Clone, PartialEq)]
pub enum UserActivityLevel {
    Idle,
    LightActivity,
    ModerateActivity,
    HighActivity,
    IntenseActivity,
}

impl Default for UserActivityLevel {
    fn default() -> Self {
        UserActivityLevel::Idle
    }
}

/// Security state assessment
#[derive(Debug, Clone, PartialEq)]
pub enum SecurityState {
    Secure,
    Monitoring,
    Elevated,
    HighAlert,
    Compromised,
}

impl Default for SecurityState {
    fn default() -> Self {
        SecurityState::Secure
    }
}

/// Resource availability state
#[derive(Debug, Clone, Default)]
pub struct ResourceState {
    pub cpu_usage: f32,
    pub memory_usage: f32,
    pub disk_usage: f32,
    pub network_usage: f32,
    pub temperature: f32,
}

/// Points of attention in the environment
#[derive(Debug, Clone)]
pub struct AttentionPoint {
    pub location: String,
    pub intensity: f32,
    pub duration: chrono::Duration,
    pub attention_type: AttentionType,
}

/// Types of attention
#[derive(Debug, Clone)]
pub enum AttentionType {
    SystemResource,
    UserInterface,
    SecurityEvent,
    PerformanceAnomaly,
    ExternalCommunication,
}

/// Filter for processing environmental data
#[derive(Debug, Clone)]
pub struct AwarenessFilter {
    pub name: String,
    pub threshold: f32,
    pub filter_type: FilterType,
    pub enabled: bool,
}

/// Types of awareness filters
#[derive(Debug, Clone)]
pub enum FilterType {
    HighPass,    // Only significant events
    LowPass,     // Only subtle changes
    BandPass,    // Events within a range
    Novelty,     // New or unusual events
    Pattern,     // Pattern-based filtering
}

/// Trait for environmental sensors
pub trait EnvironmentalSensor {
    fn sensor_name(&self) -> &str;
    fn read_sensor(&self) -> anyhow::Result<Vec<Stimulus>>;
    fn is_active(&self) -> bool;
    fn sensitivity(&self) -> f32;
}

impl EnvironmentalAwareness {
    /// Create a new environmental awareness system
    pub fn new() -> Self {
        Self {
            sensors: Arc::new(RwLock::new(HashMap::new())),
            context_memory: Arc::new(RwLock::new(ContextMemory::default())),
            awareness_filters: Self::create_default_filters(),
        }
    }

    /// Initialize with default sensors
    pub async fn initialize(&self) -> anyhow::Result<()> {
        tracing::info!("Initializing Environmental Awareness");
        
        // Register default sensors
        self.register_sensor("system_monitor", Box::new(SystemMonitorSensor::new())).await?;
        self.register_sensor("user_activity", Box::new(UserActivitySensor::new())).await?;
        self.register_sensor("security_monitor", Box::new(SecurityMonitorSensor::new())).await?;
        self.register_sensor("resource_monitor", Box::new(ResourceMonitorSensor::new())).await?;
        
        Ok(())
    }

    /// Register a new environmental sensor
    pub async fn register_sensor(
        &self,
        name: &str,
        sensor: Box<dyn EnvironmentalSensor + Send + Sync>,
    ) -> anyhow::Result<()> {
        let mut sensors = self.sensors.write().await;
        sensors.insert(name.to_string(), sensor);
        tracing::info!("Registered environmental sensor: {}", name);
        Ok(())
    }

    /// Scan environment and generate stimuli
    pub async fn scan_environment(&self) -> anyhow::Result<Vec<Stimulus>> {
        let sensors = self.sensors.read().await;
        let mut all_stimuli = Vec::new();
        
        // Collect stimuli from all active sensors
        for (name, sensor) in sensors.iter() {
            if sensor.is_active() {
                match sensor.read_sensor() {
                    Ok(mut stimuli) => {
                        tracing::debug!("Sensor {} generated {} stimuli", name, stimuli.len());
                        all_stimuli.append(&mut stimuli);
                    }
                    Err(e) => {
                        tracing::warn!("Sensor {} failed to read: {}", name, e);
                    }
                }
            }
        }
        
        // Apply awareness filters
        let filtered_stimuli = self.apply_filters(all_stimuli).await?;
        
        // Update context memory
        self.update_context(&filtered_stimuli).await?;
        
        Ok(filtered_stimuli)
    }

    /// Apply awareness filters to stimuli
    async fn apply_filters(&self, stimuli: Vec<Stimulus>) -> anyhow::Result<Vec<Stimulus>> {
        let mut filtered = Vec::new();
        let stimuli_len = stimuli.len(); // Capture length before moving
        
        for stimulus in stimuli {
            let mut passes_filters = true;
            
            for filter in &self.awareness_filters {
                if filter.enabled && !self.stimulus_passes_filter(&stimulus, filter) {
                    passes_filters = false;
                    break;
                }
            }
            
            if passes_filters {
                filtered.push(stimulus);
            }
        }
        
        tracing::debug!("Filtered {} stimuli to {} significant events", stimuli_len, filtered.len());
        Ok(filtered)
    }

    /// Check if stimulus passes a filter
    fn stimulus_passes_filter(&self, stimulus: &Stimulus, filter: &AwarenessFilter) -> bool {
        match filter.filter_type {
            FilterType::HighPass => stimulus.intensity >= filter.threshold,
            FilterType::LowPass => stimulus.intensity <= filter.threshold,
            FilterType::BandPass => {
                stimulus.intensity >= filter.threshold * 0.5 && stimulus.intensity <= filter.threshold * 1.5
            }
            FilterType::Novelty => true, // Would implement novelty detection
            FilterType::Pattern => true, // Would implement pattern matching
        }
    }

    /// Update environmental context
    async fn update_context(&self, stimuli: &[Stimulus]) -> anyhow::Result<()> {
        let mut context_memory = self.context_memory.write().await;
        let mut new_context = context_memory.current_context.clone();
        
        new_context.timestamp = chrono::Utc::now();
        
        // Update context based on stimuli
        for stimulus in stimuli {
            match stimulus.stimulus_type {
                StimulusType::SystemEvent => {
                    new_context.system_load += stimulus.intensity * 0.1;
                }
                StimulusType::UserInteraction => {
                    new_context.user_activity = self.determine_user_activity(stimulus.intensity);
                }
                StimulusType::SecurityAlert => {
                    new_context.security_state = self.assess_security_state(stimulus.intensity);
                }
                StimulusType::PerformanceMetric => {
                    self.update_resource_state(&mut new_context.resource_availability, stimulus);
                }
                _ => {}
            }
        }
        
        // Clamp values
        new_context.system_load = new_context.system_load.min(1.0);
        
        // Archive old context and set new one
        let current_context = context_memory.current_context.clone();
        context_memory.context_history.push(current_context);
        if context_memory.context_history.len() > 100 {
            context_memory.context_history.remove(0);
        }
        context_memory.current_context = new_context;
        
        Ok(())
    }

    /// Determine user activity level from stimulus intensity
    fn determine_user_activity(&self, intensity: f32) -> UserActivityLevel {
        match intensity {
            i if i < 0.2 => UserActivityLevel::Idle,
            i if i < 0.4 => UserActivityLevel::LightActivity,
            i if i < 0.6 => UserActivityLevel::ModerateActivity,
            i if i < 0.8 => UserActivityLevel::HighActivity,
            _ => UserActivityLevel::IntenseActivity,
        }
    }

    /// Assess security state from stimulus intensity
    fn assess_security_state(&self, intensity: f32) -> SecurityState {
        match intensity {
            i if i < 0.3 => SecurityState::Secure,
            i if i < 0.5 => SecurityState::Monitoring,
            i if i < 0.7 => SecurityState::Elevated,
            i if i < 0.9 => SecurityState::HighAlert,
            _ => SecurityState::Compromised,
        }
    }

    /// Update resource state based on stimulus
    fn update_resource_state(&self, resource_state: &mut ResourceState, stimulus: &Stimulus) {
        // Simple resource state update based on stimulus data
        if !stimulus.data.is_empty() {
            let value = stimulus.data[0] as f32 / 255.0;
            resource_state.cpu_usage = value;
        }
    }

    /// Get current environmental context
    pub async fn get_current_context(&self) -> EnvironmentalContext {
        let context_memory = self.context_memory.read().await;
        context_memory.current_context.clone()
    }

    /// Create default awareness filters
    fn create_default_filters() -> Vec<AwarenessFilter> {
        vec![
            AwarenessFilter {
                name: "significant_events".to_string(),
                threshold: 0.3,
                filter_type: FilterType::HighPass,
                enabled: true,
            },
            AwarenessFilter {
                name: "novelty_detector".to_string(),
                threshold: 0.5,
                filter_type: FilterType::Novelty,
                enabled: true,
            },
        ]
    }
}

/// Default system monitor sensor
pub struct SystemMonitorSensor;

impl SystemMonitorSensor {
    pub fn new() -> Self {
        Self
    }
}

impl EnvironmentalSensor for SystemMonitorSensor {
    fn sensor_name(&self) -> &str {
        "system_monitor"
    }

    fn read_sensor(&self) -> anyhow::Result<Vec<Stimulus>> {
        // Would implement actual system monitoring
        Ok(vec![])
    }

    fn is_active(&self) -> bool {
        true
    }

    fn sensitivity(&self) -> f32 {
        0.5
    }
}

/// User activity sensor
pub struct UserActivitySensor;

impl UserActivitySensor {
    pub fn new() -> Self {
        Self
    }
}

impl EnvironmentalSensor for UserActivitySensor {
    fn sensor_name(&self) -> &str {
        "user_activity"
    }

    fn read_sensor(&self) -> anyhow::Result<Vec<Stimulus>> {
        // Would implement user activity monitoring
        Ok(vec![])
    }

    fn is_active(&self) -> bool {
        true
    }

    fn sensitivity(&self) -> f32 {
        0.3
    }
}

/// Security monitoring sensor
pub struct SecurityMonitorSensor;

impl SecurityMonitorSensor {
    pub fn new() -> Self {
        Self
    }
}

impl EnvironmentalSensor for SecurityMonitorSensor {
    fn sensor_name(&self) -> &str {
        "security_monitor"
    }

    fn read_sensor(&self) -> anyhow::Result<Vec<Stimulus>> {
        // Would implement security monitoring
        Ok(vec![])
    }

    fn is_active(&self) -> bool {
        true
    }

    fn sensitivity(&self) -> f32 {
        0.8
    }
}

/// Resource monitoring sensor
pub struct ResourceMonitorSensor;

impl ResourceMonitorSensor {
    pub fn new() -> Self {
        Self
    }
}

impl EnvironmentalSensor for ResourceMonitorSensor {
    fn sensor_name(&self) -> &str {
        "resource_monitor"
    }

    fn read_sensor(&self) -> anyhow::Result<Vec<Stimulus>> {
        // Would implement resource monitoring
        Ok(vec![])
    }

    fn is_active(&self) -> bool {
        true
    }

    fn sensitivity(&self) -> f32 {
        0.4
    }
}
