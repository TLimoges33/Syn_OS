//! Anomaly Detection System
//!
//! ML-based anomaly detection for security metrics

use crate::{MetricPoint, MetricType, Anomaly, AnomalySeverity, Result, AnalyticsError};
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Anomaly detection algorithms
#[derive(Debug, Clone)]
pub enum DetectionAlgorithm {
    /// Statistical (Z-score based)
    Statistical,
    /// Isolation Forest
    IsolationForest,
    /// DBSCAN clustering
    DBSCAN,
    /// Moving Average
    MovingAverage,
}

/// Anomaly detector configuration
pub struct AnomalyDetector {
    algorithm: DetectionAlgorithm,
    sensitivity: f64,
    baseline_window: usize,
    baselines: HashMap<String, Baseline>,
}

#[derive(Clone)]
struct Baseline {
    mean: f64,
    stddev: f64,
    min: f64,
    max: f64,
    samples: Vec<f64>,
}

impl AnomalyDetector {
    pub fn new(algorithm: DetectionAlgorithm, sensitivity: f64) -> Self {
        Self {
            algorithm,
            sensitivity,
            baseline_window: 100,
            baselines: HashMap::new(),
        }
    }

    /// Update baseline with new data
    pub fn update_baseline(&mut self, metric_type: &MetricType, value: f64) {
        let key = format!("{:?}", metric_type);

        let baseline = self.baselines.entry(key.clone()).or_insert_with(|| Baseline {
            mean: 0.0,
            stddev: 0.0,
            min: f64::MAX,
            max: f64::MIN,
            samples: Vec::new(),
        });

        baseline.samples.push(value);

        // Keep only recent samples
        if baseline.samples.len() > self.baseline_window {
            baseline.samples.remove(0);
        }

        // Recalculate statistics
        self.calculate_baseline_stats(&key);
    }

    fn calculate_baseline_stats(&mut self, key: &str) {
        if let Some(baseline) = self.baselines.get_mut(key) {
            if baseline.samples.is_empty() {
                return;
            }

            let n = baseline.samples.len() as f64;
            baseline.mean = baseline.samples.iter().sum::<f64>() / n;

            let variance = baseline.samples.iter()
                .map(|v| (v - baseline.mean).powi(2))
                .sum::<f64>() / n;
            baseline.stddev = variance.sqrt();

            baseline.min = baseline.samples.iter()
                .cloned()
                .min_by(|a, b| a.partial_cmp(b).unwrap())
                .unwrap_or(0.0);

            baseline.max = baseline.samples.iter()
                .cloned()
                .max_by(|a, b| a.partial_cmp(b).unwrap())
                .unwrap_or(0.0);
        }
    }

    /// Detect anomalies in a metric
    pub fn detect(&self, metric: &MetricPoint) -> Result<Option<Anomaly>> {
        let key = format!("{:?}", metric.metric_type);

        let baseline = match self.baselines.get(&key) {
            Some(b) => b,
            None => return Ok(None), // No baseline yet
        };

        match self.algorithm {
            DetectionAlgorithm::Statistical => {
                self.statistical_detection(metric, baseline)
            }
            DetectionAlgorithm::IsolationForest => {
                self.isolation_forest_detection(metric, baseline)
            }
            DetectionAlgorithm::DBSCAN => {
                self.dbscan_detection(metric, baseline)
            }
            DetectionAlgorithm::MovingAverage => {
                self.moving_average_detection(metric, baseline)
            }
        }
    }

    /// Statistical anomaly detection (Z-score)
    fn statistical_detection(&self, metric: &MetricPoint, baseline: &Baseline) -> Result<Option<Anomaly>> {
        if baseline.stddev == 0.0 {
            return Ok(None);
        }

        let z_score = (metric.value - baseline.mean).abs() / baseline.stddev;
        let threshold = self.sensitivity; // e.g., 3.0 for 3 standard deviations

        if z_score > threshold {
            let severity = if z_score > threshold * 2.0 {
                AnomalySeverity::Critical
            } else if z_score > threshold * 1.5 {
                AnomalySeverity::High
            } else if z_score > threshold * 1.2 {
                AnomalySeverity::Medium
            } else {
                AnomalySeverity::Low
            };

            let expected_min = baseline.mean - threshold * baseline.stddev;
            let expected_max = baseline.mean + threshold * baseline.stddev;

            Ok(Some(Anomaly {
                metric_type: metric.metric_type.clone(),
                timestamp: metric.timestamp,
                value: metric.value,
                expected_range: (expected_min, expected_max),
                severity,
                confidence: (z_score / (threshold * 2.0)).min(1.0),
            }))
        } else {
            Ok(None)
        }
    }

    /// Isolation Forest detection (simplified)
    fn isolation_forest_detection(&self, metric: &MetricPoint, baseline: &Baseline) -> Result<Option<Anomaly>> {
        // Simplified: check if value is in isolation
        let samples = &baseline.samples;

        if samples.len() < 10 {
            return Ok(None);
        }

        // Count nearby points
        let threshold = baseline.stddev * 0.5;
        let nearby_count = samples.iter()
            .filter(|&&v| (v - metric.value).abs() < threshold)
            .count();

        let isolation_score = 1.0 - (nearby_count as f64 / samples.len() as f64);

        if isolation_score > 0.9 {
            Ok(Some(Anomaly {
                metric_type: metric.metric_type.clone(),
                timestamp: metric.timestamp,
                value: metric.value,
                expected_range: (baseline.min, baseline.max),
                severity: AnomalySeverity::Medium,
                confidence: isolation_score,
            }))
        } else {
            Ok(None)
        }
    }

    /// DBSCAN clustering detection
    fn dbscan_detection(&self, metric: &MetricPoint, baseline: &Baseline) -> Result<Option<Anomaly>> {
        // Simplified DBSCAN: density-based outlier detection
        let eps = baseline.stddev;
        let min_samples = 3;

        let neighbors = baseline.samples.iter()
            .filter(|&&v| (v - metric.value).abs() <= eps)
            .count();

        if neighbors < min_samples {
            Ok(Some(Anomaly {
                metric_type: metric.metric_type.clone(),
                timestamp: metric.timestamp,
                value: metric.value,
                expected_range: (baseline.mean - eps, baseline.mean + eps),
                severity: AnomalySeverity::Medium,
                confidence: 1.0 - (neighbors as f64 / min_samples as f64),
            }))
        } else {
            Ok(None)
        }
    }

    /// Moving average based detection
    fn moving_average_detection(&self, metric: &MetricPoint, baseline: &Baseline) -> Result<Option<Anomaly>> {
        if baseline.samples.len() < 5 {
            return Ok(None);
        }

        // Calculate moving average from last 5 samples
        let ma: f64 = baseline.samples.iter().rev().take(5).sum::<f64>() / 5.0;
        let deviation = (metric.value - ma).abs();
        let threshold = baseline.stddev * self.sensitivity;

        if deviation > threshold {
            Ok(Some(Anomaly {
                metric_type: metric.metric_type.clone(),
                timestamp: metric.timestamp,
                value: metric.value,
                expected_range: (ma - threshold, ma + threshold),
                severity: AnomalySeverity::Low,
                confidence: (deviation / (threshold * 2.0)).min(1.0),
            }))
        } else {
            Ok(None)
        }
    }

    /// Batch anomaly detection
    pub fn detect_batch(&self, metrics: &[MetricPoint]) -> Result<Vec<Anomaly>> {
        let mut anomalies = Vec::new();

        for metric in metrics {
            if let Some(anomaly) = self.detect(metric)? {
                anomalies.push(anomaly);
            }
        }

        Ok(anomalies)
    }

    /// Get current baselines summary
    pub fn get_baselines(&self) -> HashMap<String, (f64, f64, f64, f64)> {
        self.baselines.iter()
            .map(|(k, v)| (k.clone(), (v.mean, v.stddev, v.min, v.max)))
            .collect()
    }
}

/// Multi-algorithm ensemble detector
pub struct EnsembleDetector {
    detectors: Vec<AnomalyDetector>,
    voting_threshold: f64,
}

impl EnsembleDetector {
    pub fn new() -> Self {
        let detectors = vec![
            AnomalyDetector::new(DetectionAlgorithm::Statistical, 3.0),
            AnomalyDetector::new(DetectionAlgorithm::IsolationForest, 2.5),
            AnomalyDetector::new(DetectionAlgorithm::MovingAverage, 2.0),
        ];

        Self {
            detectors,
            voting_threshold: 0.5, // 50% of detectors must agree
        }
    }

    /// Update all detector baselines
    pub fn update_baseline(&mut self, metric_type: &MetricType, value: f64) {
        for detector in &mut self.detectors {
            detector.update_baseline(metric_type, value);
        }
    }

    /// Ensemble detection with voting
    pub fn detect(&self, metric: &MetricPoint) -> Result<Option<Anomaly>> {
        let mut detections = Vec::new();

        for detector in &self.detectors {
            if let Some(anomaly) = detector.detect(metric)? {
                detections.push(anomaly);
            }
        }

        let detection_ratio = detections.len() as f64 / self.detectors.len() as f64;

        if detection_ratio >= self.voting_threshold && !detections.is_empty() {
            // Average the anomalies
            let avg_confidence = detections.iter().map(|a| a.confidence).sum::<f64>()
                / detections.len() as f64;

            let severity = self.aggregate_severity(&detections);

            Ok(Some(Anomaly {
                metric_type: metric.metric_type.clone(),
                timestamp: metric.timestamp,
                value: metric.value,
                expected_range: detections[0].expected_range,
                severity,
                confidence: avg_confidence,
            }))
        } else {
            Ok(None)
        }
    }

    fn aggregate_severity(&self, anomalies: &[Anomaly]) -> AnomalySeverity {
        let max_severity = anomalies.iter()
            .map(|a| match a.severity {
                AnomalySeverity::Critical => 4,
                AnomalySeverity::High => 3,
                AnomalySeverity::Medium => 2,
                AnomalySeverity::Low => 1,
            })
            .max()
            .unwrap_or(1);

        match max_severity {
            4 => AnomalySeverity::Critical,
            3 => AnomalySeverity::High,
            2 => AnomalySeverity::Medium,
            _ => AnomalySeverity::Low,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_baseline_update() {
        let mut detector = AnomalyDetector::new(DetectionAlgorithm::Statistical, 3.0);

        for i in 0..10 {
            detector.update_baseline(&MetricType::ThreatDetections, i as f64);
        }

        let baselines = detector.get_baselines();
        assert!(!baselines.is_empty());
    }

    #[test]
    fn test_statistical_detection() {
        let mut detector = AnomalyDetector::new(DetectionAlgorithm::Statistical, 3.0);

        // Build baseline
        for i in 0..20 {
            detector.update_baseline(&MetricType::ThreatDetections, 50.0 + i as f64);
        }

        // Test normal value
        let normal = MetricPoint::new(MetricType::ThreatDetections, 55.0);
        assert!(detector.detect(&normal).unwrap().is_none());

        // Test anomaly
        let anomaly = MetricPoint::new(MetricType::ThreatDetections, 200.0);
        let result = detector.detect(&anomaly).unwrap();
        assert!(result.is_some());
    }

    #[test]
    fn test_ensemble_detector() {
        let mut ensemble = EnsembleDetector::new();

        // Build baseline
        for i in 0..50 {
            ensemble.update_baseline(&MetricType::ThreatDetections, 100.0 + i as f64);
        }

        // Test anomaly
        let anomaly = MetricPoint::new(MetricType::ThreatDetections, 500.0);
        let result = ensemble.detect(&anomaly).unwrap();
        assert!(result.is_some());
    }
}
