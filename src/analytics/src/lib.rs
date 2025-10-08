//! # SynOS Security Metrics & Analytics
//!
//! Real-time security metrics collection, trend analysis, and visualization

pub mod metrics_collector;
pub mod time_series;
pub mod trend_analyzer;
pub mod anomaly_detector;
pub mod visualization_api;

// Re-export commonly used types
pub use metrics_collector::{MetricsCollector, MetricSubscriber, SystemMetricsCollector, SecurityMetricsCollector};
pub use time_series::{TimeSeriesStore, TimeSeriesManager, AggregatedPoint};
pub use trend_analyzer::{TrendAnalyzer, AdvancedTrendDetector};
pub use anomaly_detector::{AnomalyDetector, DetectionAlgorithm, EnsembleDetector};
pub use visualization_api::{VisualizationAPI, ApiResponse, DashboardSummary};

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AnalyticsError {
    #[error("Metric collection failed: {0}")]
    CollectionError(String),
    #[error("Time series error: {0}")]
    TimeSeriesError(String),
    #[error("Analysis failed: {0}")]
    AnalysisError(String),
    #[error("Anomaly detection error: {0}")]
    AnomalyError(String),
}

pub type Result<T> = std::result::Result<T, AnalyticsError>;

/// Security metric types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum MetricType {
    // Threat Metrics
    ThreatDetections,
    HighSeverityAlerts,
    IncidentCount,

    // Performance Metrics
    SystemLoad,
    NetworkTraffic,
    ProcessCount,

    // Security Posture
    VulnerabilityCount,
    PatchLevel,
    ComplianceScore,

    // User Activity
    FailedLogins,
    PrivilegeEscalations,
    FileAccessViolations,

    // Custom
    Custom(String),
}

/// Metric data point
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricPoint {
    pub metric_type: MetricType,
    pub value: f64,
    pub timestamp: DateTime<Utc>,
    pub tags: HashMap<String, String>,
}

impl MetricPoint {
    pub fn new(metric_type: MetricType, value: f64) -> Self {
        Self {
            metric_type,
            value,
            timestamp: Utc::now(),
            tags: HashMap::new(),
        }
    }

    pub fn with_tag(mut self, key: String, value: String) -> Self {
        self.tags.insert(key, value);
        self
    }
}

/// Aggregated metric statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricStats {
    pub count: usize,
    pub min: f64,
    pub max: f64,
    pub mean: f64,
    pub median: f64,
    pub stddev: f64,
    pub percentile_95: f64,
    pub percentile_99: f64,
}

impl MetricStats {
    pub fn from_values(values: &[f64]) -> Self {
        if values.is_empty() {
            return Self {
                count: 0,
                min: 0.0,
                max: 0.0,
                mean: 0.0,
                median: 0.0,
                stddev: 0.0,
                percentile_95: 0.0,
                percentile_99: 0.0,
            };
        }

        let mut sorted = values.to_vec();
        sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());

        let count = values.len();
        let min = sorted[0];
        let max = sorted[count - 1];
        let mean = sorted.iter().sum::<f64>() / count as f64;

        let median = if count % 2 == 0 {
            (sorted[count / 2 - 1] + sorted[count / 2]) / 2.0
        } else {
            sorted[count / 2]
        };

        let variance = values.iter()
            .map(|v| (v - mean).powi(2))
            .sum::<f64>() / count as f64;
        let stddev = variance.sqrt();

        let percentile_95 = sorted[(count as f64 * 0.95) as usize];
        let percentile_99 = sorted[(count as f64 * 0.99) as usize];

        Self {
            count,
            min,
            max,
            mean,
            median,
            stddev,
            percentile_95,
            percentile_99,
        }
    }
}

/// Trend direction
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TrendDirection {
    Increasing,
    Decreasing,
    Stable,
    Volatile,
}

/// Trend analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrendAnalysis {
    pub metric_type: MetricType,
    pub direction: TrendDirection,
    pub change_rate: f64,
    pub confidence: f64,
    pub forecast: Vec<f64>,
    pub analyzed_at: DateTime<Utc>,
}

/// Anomaly detection result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Anomaly {
    pub metric_type: MetricType,
    pub timestamp: DateTime<Utc>,
    pub value: f64,
    pub expected_range: (f64, f64),
    pub severity: AnomalySeverity,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AnomalySeverity {
    Low,
    Medium,
    High,
    Critical,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metric_point_creation() {
        let metric = MetricPoint::new(MetricType::ThreatDetections, 42.0);
        assert_eq!(metric.value, 42.0);
    }

    #[test]
    fn test_metric_stats() {
        let values = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let stats = MetricStats::from_values(&values);

        assert_eq!(stats.count, 5);
        assert_eq!(stats.min, 1.0);
        assert_eq!(stats.max, 5.0);
        assert_eq!(stats.mean, 3.0);
        assert_eq!(stats.median, 3.0);
    }

    #[test]
    fn test_empty_stats() {
        let values: Vec<f64> = vec![];
        let stats = MetricStats::from_values(&values);
        assert_eq!(stats.count, 0);
    }
}
