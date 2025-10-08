//! Continuous AI Monitoring Infrastructure
//!
//! Real-time performance tracking, drift detection, and model health assessment
//! for deployed AI models in SynOS with comprehensive alerting and dashboard integration.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::sync::atomic::{AtomicU64, AtomicU32, Ordering};
use spin::{RwLock, Mutex};
use serde::{Serialize, Deserialize};

use crate::ai::mlops::{ModelVersion, DeploymentConfig, MLOpsError};
use crate::process::monitoring::{AlertType, AlertSeverity, MonitoringAlert};

/// AI model performance metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIModelMetrics {
    pub model_id: String,
    pub deployment_id: String,
    pub timestamp: u64,
    pub inference_metrics: InferenceMetrics,
    pub resource_metrics: ResourceMetrics,
    pub quality_metrics: QualityMetrics,
    pub drift_metrics: DriftMetrics,
    pub fairness_metrics: FairnessMetrics,
}

/// Inference performance metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InferenceMetrics {
    pub requests_per_second: f64,
    pub average_latency_ms: f64,
    pub p50_latency_ms: f64,
    pub p95_latency_ms: f64,
    pub p99_latency_ms: f64,
    pub max_latency_ms: f64,
    pub error_rate: f64,
    pub success_rate: f64,
    pub timeout_rate: f64,
    pub concurrent_requests: u32,
    pub queue_depth: u32,
    pub batch_size_avg: f32,
    pub throughput_mb_s: f64,
}

/// Resource utilization metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceMetrics {
    pub cpu_utilization: f64,
    pub memory_usage_mb: u64,
    pub memory_utilization: f64,
    pub gpu_utilization: f64,
    pub gpu_memory_mb: u64,
    pub npu_utilization: f64,
    pub disk_io_mb_s: f64,
    pub network_io_mb_s: f64,
    pub temperature_celsius: f32,
    pub power_watts: f32,
}

/// Model quality metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityMetrics {
    pub accuracy: f64,
    pub precision: f64,
    pub recall: f64,
    pub f1_score: f64,
    pub auc_roc: f64,
    pub confidence_score: f64,
    pub prediction_entropy: f64,
    pub calibration_error: f64,
    pub feature_importance_stability: f64,
}

/// Data and concept drift metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DriftMetrics {
    pub data_drift_score: f64,
    pub concept_drift_score: f64,
    pub feature_drift_scores: BTreeMap<String, f64>,
    pub population_stability_index: f64,
    pub kolmogorov_smirnov_statistic: f64,
    pub jensen_shannon_divergence: f64,
    pub drift_detection_timestamp: u64,
    pub drift_severity: DriftSeverity,
}

/// Fairness and bias metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FairnessMetrics {
    pub demographic_parity: f64,
    pub equalized_odds: f64,
    pub calibration: f64,
    pub individual_fairness: f64,
    pub counterfactual_fairness: f64,
    pub bias_metrics: BTreeMap<String, f64>, // Group-specific metrics
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum DriftSeverity {
    None,
    Low,
    Medium,
    High,
    Critical,
}

/// Monitoring configuration for AI models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringConfig {
    pub model_id: String,
    pub monitoring_enabled: bool,
    pub collection_interval_ms: u64,
    pub alerting_enabled: bool,
    pub drift_detection_enabled: bool,
    pub fairness_monitoring_enabled: bool,
    pub thresholds: MonitoringThresholds,
    pub retention_policy: RetentionPolicy,
}

/// Monitoring thresholds and limits
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringThresholds {
    pub max_latency_ms: f64,
    pub min_accuracy: f64,
    pub max_error_rate: f64,
    pub max_cpu_utilization: f64,
    pub max_memory_utilization: f64,
    pub drift_warning_threshold: f64,
    pub drift_critical_threshold: f64,
    pub fairness_threshold: f64,
}

/// Data retention policy
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RetentionPolicy {
    pub raw_metrics_days: u32,
    pub aggregated_metrics_days: u32,
    pub alerts_days: u32,
    pub drift_snapshots_days: u32,
}

/// Monitoring alert for AI systems
#[derive(Debug, Clone)]
pub struct AIMonitoringAlert {
    pub alert_id: String,
    pub model_id: String,
    pub deployment_id: String,
    pub alert_type: AIAlertType,
    pub severity: AlertSeverity,
    pub message: String,
    pub details: String,
    pub metrics_snapshot: AIModelMetrics,
    pub timestamp: u64,
    pub acknowledged: bool,
    pub resolved: bool,
    pub auto_resolved: bool,
}

/// AI-specific alert types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AIAlertType {
    HighLatency,
    HighErrorRate,
    AccuracyDrop,
    DataDrift,
    ConceptDrift,
    BiasDetected,
    ResourceExhaustion,
    ModelDegradation,
    FeatureCorruption,
    PredictionAnomaly,
    FairnessViolation,
    SecurityThreat,
}

/// Historical trend analysis
#[derive(Debug, Clone)]
pub struct TrendAnalysis {
    pub metric_name: String,
    pub time_window_hours: u32,
    pub trend_direction: TrendDirection,
    pub trend_strength: f64, // -1.0 to 1.0
    pub volatility: f64,
    pub seasonal_patterns: Vec<SeasonalPattern>,
    pub anomaly_count: u32,
    pub forecast: Vec<ForecastPoint>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TrendDirection {
    Improving,
    Degrading,
    Stable,
    Volatile,
}

/// Seasonal pattern detection
#[derive(Debug, Clone)]
pub struct SeasonalPattern {
    pub pattern_type: PatternType,
    pub period_minutes: u32,
    pub amplitude: f64,
    pub confidence: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PatternType {
    Hourly,
    Daily,
    Weekly,
    Custom,
}

/// Forecasting data point
#[derive(Debug, Clone)]
pub struct ForecastPoint {
    pub timestamp: u64,
    pub predicted_value: f64,
    pub confidence_interval_lower: f64,
    pub confidence_interval_upper: f64,
}

/// Health assessment for AI models
#[derive(Debug, Clone)]
pub struct ModelHealthAssessment {
    pub model_id: String,
    pub overall_health_score: f64, // 0.0 to 100.0
    pub health_components: BTreeMap<String, f64>,
    pub health_status: ModelHealthStatus,
    pub last_assessment: u64,
    pub recommendations: Vec<HealthRecommendation>,
    pub risk_factors: Vec<RiskFactor>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ModelHealthStatus {
    Healthy,
    Warning,
    Unhealthy,
    Critical,
    Unknown,
}

/// Health recommendations
#[derive(Debug, Clone)]
pub struct HealthRecommendation {
    pub recommendation_id: String,
    pub priority: RecommendationPriority,
    pub category: RecommendationCategory,
    pub description: String,
    pub impact: String,
    pub effort_level: EffortLevel,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum RecommendationPriority {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RecommendationCategory {
    Performance,
    Accuracy,
    Efficiency,
    Fairness,
    Security,
    Maintainability,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EffortLevel {
    Low,
    Medium,
    High,
}

/// Risk factors for model performance
#[derive(Debug, Clone)]
pub struct RiskFactor {
    pub factor_id: String,
    pub description: String,
    pub risk_level: RiskLevel,
    pub probability: f64,
    pub impact: f64,
    pub mitigation_strategies: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum RiskLevel {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
}

/// Main continuous monitoring manager
pub struct ContinuousAIMonitor {
    monitored_models: RwLock<BTreeMap<String, MonitoringConfig>>,
    metrics_history: RwLock<BTreeMap<String, Vec<AIModelMetrics>>>,
    active_alerts: Mutex<Vec<AIMonitoringAlert>>,
    health_assessments: RwLock<BTreeMap<String, ModelHealthAssessment>>,
    trend_analyses: RwLock<BTreeMap<String, Vec<TrendAnalysis>>>,
    next_alert_id: AtomicU32,
    monitoring_enabled: AtomicU32,
}

impl ContinuousAIMonitor {
    /// Create new continuous monitoring system
    pub fn new() -> Self {
        Self {
            monitored_models: RwLock::new(BTreeMap::new()),
            metrics_history: RwLock::new(BTreeMap::new()),
            active_alerts: Mutex::new(Vec::new()),
            health_assessments: RwLock::new(BTreeMap::new()),
            trend_analyses: RwLock::new(BTreeMap::new()),
            next_alert_id: AtomicU32::new(1),
            monitoring_enabled: AtomicU32::new(1),
        }
    }

    /// Register model for monitoring
    pub fn register_model(&self, model_id: String, config: MonitoringConfig) -> Result<(), MLOpsError> {
        let mut models = self.monitored_models.write();
        models.insert(model_id.clone(), config);

        // Initialize metrics history
        let mut history = self.metrics_history.write();
        history.insert(model_id.clone(), Vec::new());

        crate::println!("Registered model {} for continuous monitoring", model_id);
        Ok(())
    }

    /// Collect metrics for a model
    pub fn collect_metrics(&self, model_id: &str, metrics: AIModelMetrics) -> Result<(), MLOpsError> {
        let models = self.monitored_models.read();
        if let Some(config) = models.get(model_id) {
            if !config.monitoring_enabled {
                return Ok(());
            }

            // Store metrics
            let mut history = self.metrics_history.write();
            if let Some(model_history) = history.get_mut(model_id) {
                model_history.push(metrics.clone());

                // Apply retention policy
                let retention_limit = config.retention_policy.raw_metrics_days as usize * 24 * 60; // minutes
                if model_history.len() > retention_limit {
                    model_history.drain(0..model_history.len() - retention_limit);
                }
            }

            // Check for alerts
            self.check_model_alerts(model_id, &metrics, &config.thresholds)?;

            // Update health assessment
            self.update_health_assessment(model_id, &metrics)?;

            // Perform drift detection if enabled
            if config.drift_detection_enabled {
                self.detect_drift(model_id, &metrics)?;
            }

            Ok(())
        } else {
            Err(MLOpsError::ModelNotFound)
        }
    }

    /// Check for alert conditions
    fn check_model_alerts(&self, model_id: &str, metrics: &AIModelMetrics, thresholds: &MonitoringThresholds) -> Result<(), MLOpsError> {
        let mut alerts = Vec::new();

        // Check latency
        if metrics.inference_metrics.p95_latency_ms > thresholds.max_latency_ms {
            alerts.push(self.create_ai_alert(
                model_id,
                &metrics.deployment_id,
                AIAlertType::HighLatency,
                AlertSeverity::Warning,
                format!("P95 latency is {:.2}ms", metrics.inference_metrics.p95_latency_ms),
                format!("Exceeds threshold of {:.2}ms", thresholds.max_latency_ms),
                metrics.clone(),
            ));
        }

        // Check error rate
        if metrics.inference_metrics.error_rate > thresholds.max_error_rate {
            alerts.push(self.create_ai_alert(
                model_id,
                &metrics.deployment_id,
                AIAlertType::HighErrorRate,
                AlertSeverity::Error,
                format!("Error rate is {:.2}%", metrics.inference_metrics.error_rate * 100.0),
                format!("Exceeds threshold of {:.2}%", thresholds.max_error_rate * 100.0),
                metrics.clone(),
            ));
        }

        // Check accuracy
        if metrics.quality_metrics.accuracy < thresholds.min_accuracy {
            alerts.push(self.create_ai_alert(
                model_id,
                &metrics.deployment_id,
                AIAlertType::AccuracyDrop,
                AlertSeverity::Critical,
                format!("Accuracy dropped to {:.2}%", metrics.quality_metrics.accuracy * 100.0),
                format!("Below threshold of {:.2}%", thresholds.min_accuracy * 100.0),
                metrics.clone(),
            ));
        }

        // Check drift
        if metrics.drift_metrics.data_drift_score > thresholds.drift_critical_threshold {
            alerts.push(self.create_ai_alert(
                model_id,
                &metrics.deployment_id,
                AIAlertType::DataDrift,
                AlertSeverity::Critical,
                format!("Critical data drift detected: {:.3}", metrics.drift_metrics.data_drift_score),
                "Model may need retraining".to_string(),
                metrics.clone(),
            ));
        }

        // Store alerts
        if !alerts.is_empty() {
            let mut active_alerts = self.active_alerts.lock();
            active_alerts.extend(alerts);
        }

        Ok(())
    }

    /// Create AI monitoring alert
    fn create_ai_alert(&self, model_id: &str, deployment_id: &str, alert_type: AIAlertType,
                      severity: AlertSeverity, message: String, details: String,
                      metrics_snapshot: AIModelMetrics) -> AIMonitoringAlert {
        let alert_id = format!("ai_alert_{}", self.next_alert_id.fetch_add(1, Ordering::SeqCst));

        AIMonitoringAlert {
            alert_id,
            model_id: model_id.to_string(),
            deployment_id: deployment_id.to_string(),
            alert_type,
            severity,
            message,
            details,
            metrics_snapshot,
            timestamp: get_current_timestamp(),
            acknowledged: false,
            resolved: false,
            auto_resolved: false,
        }
    }

    /// Update model health assessment
    fn update_health_assessment(&self, model_id: &str, metrics: &AIModelMetrics) -> Result<(), MLOpsError> {
        let mut health_scores = BTreeMap::new();

        // Performance health (0-100)
        let latency_score = ((200.0 - metrics.inference_metrics.p95_latency_ms) / 200.0 * 100.0).max(0.0).min(100.0);
        let error_score = ((1.0 - metrics.inference_metrics.error_rate) * 100.0).max(0.0).min(100.0);
        let performance_score = (latency_score + error_score) / 2.0;
        health_scores.insert("performance".to_string(), performance_score);

        // Quality health
        let accuracy_score = metrics.quality_metrics.accuracy * 100.0;
        let confidence_score = metrics.quality_metrics.confidence_score * 100.0;
        let quality_score = (accuracy_score + confidence_score) / 2.0;
        health_scores.insert("quality".to_string(), quality_score);

        // Resource health
        let cpu_score = ((1.0 - metrics.resource_metrics.cpu_utilization) * 100.0).max(0.0);
        let memory_score = ((1.0 - metrics.resource_metrics.memory_utilization) * 100.0).max(0.0);
        let resource_score = (cpu_score + memory_score) / 2.0;
        health_scores.insert("resources".to_string(), resource_score);

        // Drift health
        let drift_score = ((1.0 - metrics.drift_metrics.data_drift_score) * 100.0).max(0.0).min(100.0);
        health_scores.insert("drift".to_string(), drift_score);

        // Overall health
        let overall_score = health_scores.values().sum::<f64>() / health_scores.len() as f64;

        let health_status = match overall_score {
            s if s >= 90.0 => ModelHealthStatus::Healthy,
            s if s >= 70.0 => ModelHealthStatus::Warning,
            s if s >= 50.0 => ModelHealthStatus::Unhealthy,
            _ => ModelHealthStatus::Critical,
        };

        let assessment = ModelHealthAssessment {
            model_id: model_id.to_string(),
            overall_health_score: overall_score,
            health_components: health_scores,
            health_status,
            last_assessment: get_current_timestamp(),
            recommendations: self.generate_health_recommendations(&metrics),
            risk_factors: self.identify_risk_factors(&metrics),
        };

        let mut assessments = self.health_assessments.write();
        assessments.insert(model_id.to_string(), assessment);

        Ok(())
    }

    /// Generate health recommendations
    fn generate_health_recommendations(&self, metrics: &AIModelMetrics) -> Vec<HealthRecommendation> {
        let mut recommendations = Vec::new();

        // High latency recommendation
        if metrics.inference_metrics.p95_latency_ms > 100.0 {
            recommendations.push(HealthRecommendation {
                recommendation_id: "reduce_latency".to_string(),
                priority: RecommendationPriority::High,
                category: RecommendationCategory::Performance,
                description: "Consider model optimization or scaling".to_string(),
                impact: "Reduce latency by 20-50%".to_string(),
                effort_level: EffortLevel::Medium,
            });
        }

        // Accuracy drop recommendation
        if metrics.quality_metrics.accuracy < 0.85 {
            recommendations.push(HealthRecommendation {
                recommendation_id: "improve_accuracy".to_string(),
                priority: RecommendationPriority::Critical,
                category: RecommendationCategory::Accuracy,
                description: "Model may need retraining with fresh data".to_string(),
                impact: "Restore accuracy to >90%".to_string(),
                effort_level: EffortLevel::High,
            });
        }

        recommendations
    }

    /// Identify risk factors
    fn identify_risk_factors(&self, metrics: &AIModelMetrics) -> Vec<RiskFactor> {
        let mut risk_factors = Vec::new();

        // Data drift risk
        if metrics.drift_metrics.data_drift_score > 0.5 {
            risk_factors.push(RiskFactor {
                factor_id: "data_drift".to_string(),
                description: "Significant data drift detected".to_string(),
                risk_level: RiskLevel::High,
                probability: metrics.drift_metrics.data_drift_score,
                impact: 0.8,
                mitigation_strategies: vec![
                    "Retrain model with recent data".to_string(),
                    "Implement adaptive learning".to_string(),
                ],
            });
        }

        risk_factors
    }

    /// Detect drift in model inputs/outputs
    fn detect_drift(&self, model_id: &str, current_metrics: &AIModelMetrics) -> Result<(), MLOpsError> {
        let history = self.metrics_history.read();
        if let Some(model_history) = history.get(model_id) {
            if model_history.len() < 10 {
                // Need sufficient history for drift detection
                return Ok(());
            }

            // Compare current metrics with baseline (e.g., last week's average)
            let baseline_window = model_history.len().saturating_sub(168).max(0); // Last week
            let baseline_metrics: Vec<&AIModelMetrics> = model_history[baseline_window..].iter().collect();

            if !baseline_metrics.is_empty() {
                let baseline_accuracy: f64 = baseline_metrics.iter().map(|m| m.quality_metrics.accuracy).sum::<f64>() / baseline_metrics.len() as f64;

                let accuracy_drift = (current_metrics.quality_metrics.accuracy - baseline_accuracy).abs() / baseline_accuracy;

                // Update drift metrics (simplified)
                crate::println!("Drift analysis for {}: accuracy drift = {:.3}", model_id, accuracy_drift);

                if accuracy_drift > 0.1 {
                    crate::println!("⚠️  Significant accuracy drift detected for model {}", model_id);
                }
            }
        }

        Ok(())
    }

    /// Generate monitoring report
    pub fn generate_monitoring_report(&self) -> String {
        let models = self.monitored_models.read();
        let active_alerts = self.active_alerts.lock();
        let assessments = self.health_assessments.read();

        let mut report = String::new();

        report.push_str("=== SYNOS AI CONTINUOUS MONITORING REPORT ===\n\n");

        // Summary
        report.push_str("=== MONITORING SUMMARY ===\n");
        report.push_str(&format!("Monitored Models: {}\n", models.len()));
        report.push_str(&format!("Active Alerts: {}\n", active_alerts.len()));

        let healthy_count = assessments.values().filter(|a| a.health_status == ModelHealthStatus::Healthy).count();
        report.push_str(&format!("Healthy Models: {}\n", healthy_count));

        // Model health overview
        report.push_str("\n=== MODEL HEALTH OVERVIEW ===\n");
        for (model_id, assessment) in assessments.iter() {
            report.push_str(&format!("Model: {}\n", model_id));
            report.push_str(&format!("  Health Score: {:.1}/100.0\n", assessment.overall_health_score));
            report.push_str(&format!("  Status: {:?}\n", assessment.health_status));
            report.push_str(&format!("  Recommendations: {}\n", assessment.recommendations.len()));
            report.push_str(&format!("  Risk Factors: {}\n", assessment.risk_factors.len()));
        }

        // Active alerts
        report.push_str("\n=== ACTIVE ALERTS ===\n");
        if active_alerts.is_empty() {
            report.push_str("No active alerts.\n");
        } else {
            for alert in active_alerts.iter().take(10) {
                report.push_str(&format!("[{:?}] {}: {}\n",
                                       alert.severity, alert.message, alert.details));
            }
        }

        report
    }
}

impl Default for InferenceMetrics {
    fn default() -> Self {
        Self {
            requests_per_second: 0.0,
            average_latency_ms: 0.0,
            p50_latency_ms: 0.0,
            p95_latency_ms: 0.0,
            p99_latency_ms: 0.0,
            max_latency_ms: 0.0,
            error_rate: 0.0,
            success_rate: 1.0,
            timeout_rate: 0.0,
            concurrent_requests: 0,
            queue_depth: 0,
            batch_size_avg: 1.0,
            throughput_mb_s: 0.0,
        }
    }
}

impl Default for ResourceMetrics {
    fn default() -> Self {
        Self {
            cpu_utilization: 0.0,
            memory_usage_mb: 0,
            memory_utilization: 0.0,
            gpu_utilization: 0.0,
            gpu_memory_mb: 0,
            npu_utilization: 0.0,
            disk_io_mb_s: 0.0,
            network_io_mb_s: 0.0,
            temperature_celsius: 25.0,
            power_watts: 10.0,
        }
    }
}

impl Default for QualityMetrics {
    fn default() -> Self {
        Self {
            accuracy: 0.85,
            precision: 0.85,
            recall: 0.85,
            f1_score: 0.85,
            auc_roc: 0.85,
            confidence_score: 0.80,
            prediction_entropy: 0.5,
            calibration_error: 0.05,
            feature_importance_stability: 0.90,
        }
    }
}

impl Default for DriftMetrics {
    fn default() -> Self {
        Self {
            data_drift_score: 0.0,
            concept_drift_score: 0.0,
            feature_drift_scores: BTreeMap::new(),
            population_stability_index: 0.0,
            kolmogorov_smirnov_statistic: 0.0,
            jensen_shannon_divergence: 0.0,
            drift_detection_timestamp: 0,
            drift_severity: DriftSeverity::None,
        }
    }
}

impl Default for FairnessMetrics {
    fn default() -> Self {
        Self {
            demographic_parity: 0.95,
            equalized_odds: 0.95,
            calibration: 0.95,
            individual_fairness: 0.95,
            counterfactual_fairness: 0.95,
            bias_metrics: BTreeMap::new(),
        }
    }
}

/// Global continuous monitoring instance
pub static AI_CONTINUOUS_MONITOR: RwLock<Option<ContinuousAIMonitor>> = RwLock::new(None);

/// Initialize continuous AI monitoring
pub fn init_continuous_monitoring() -> Result<(), MLOpsError> {
    let monitor = ContinuousAIMonitor::new();
    *AI_CONTINUOUS_MONITOR.write() = Some(monitor);
    Ok(())
}

/// Get monitoring report
pub fn get_ai_monitoring_report() -> Result<String, MLOpsError> {
    if let Some(monitor) = AI_CONTINUOUS_MONITOR.read().as_ref() {
        Ok(monitor.generate_monitoring_report())
    } else {
        Err(MLOpsError::InvalidConfiguration)
    }
}

/// Helper function to get current timestamp
fn get_current_timestamp() -> u64 {
    static COUNTER: AtomicU64 = AtomicU64::new(0);
    COUNTER.fetch_add(1, Ordering::SeqCst)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_continuous_monitor_creation() {
        let monitor = ContinuousAIMonitor::new();
        assert_eq!(monitor.monitoring_enabled.load(Ordering::Relaxed), 1);
    }

    #[test]
    fn test_model_registration() {
        let monitor = ContinuousAIMonitor::new();

        let config = MonitoringConfig {
            model_id: "test_model".to_string(),
            monitoring_enabled: true,
            collection_interval_ms: 1000,
            alerting_enabled: true,
            drift_detection_enabled: true,
            fairness_monitoring_enabled: true,
            thresholds: MonitoringThresholds {
                max_latency_ms: 100.0,
                min_accuracy: 0.85,
                max_error_rate: 0.05,
                max_cpu_utilization: 0.80,
                max_memory_utilization: 0.80,
                drift_warning_threshold: 0.3,
                drift_critical_threshold: 0.5,
                fairness_threshold: 0.80,
            },
            retention_policy: RetentionPolicy {
                raw_metrics_days: 7,
                aggregated_metrics_days: 30,
                alerts_days: 90,
                drift_snapshots_days: 30,
            },
        };

        let result = monitor.register_model("test_model".to_string(), config);
        assert!(result.is_ok());
    }
}