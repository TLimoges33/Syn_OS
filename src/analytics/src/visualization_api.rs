//! Visualization API for Analytics Dashboard
//!
//! REST API endpoints for real-time security metrics visualization

use crate::{MetricPoint, MetricType, MetricStats, Anomaly};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc, Duration, Timelike, Datelike};

/// API response wrapper
#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
    pub timestamp: DateTime<Utc>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            timestamp: Utc::now(),
        }
    }

    pub fn error(message: String) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(message),
            timestamp: Utc::now(),
        }
    }
}

/// Dashboard summary data
#[derive(Debug, Serialize, Deserialize)]
pub struct DashboardSummary {
    pub total_threats: u64,
    pub active_alerts: u64,
    pub compliance_score: f64,
    pub system_health: f64,
    pub top_threats: Vec<ThreatSummary>,
    pub recent_anomalies: Vec<Anomaly>,
    pub trend_indicators: HashMap<String, String>, // metric_name -> direction
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ThreatSummary {
    pub threat_type: String,
    pub count: u64,
    pub severity: String,
    pub last_seen: DateTime<Utc>,
}

/// Time series data for charting
#[derive(Debug, Serialize, Deserialize)]
pub struct TimeSeriesData {
    pub metric_type: String,
    pub timestamps: Vec<DateTime<Utc>>,
    pub values: Vec<f64>,
    pub stats: MetricStats,
}

/// Real-time metrics update
#[derive(Debug, Serialize, Deserialize)]
pub struct RealtimeUpdate {
    pub metric_type: String,
    pub value: f64,
    pub timestamp: DateTime<Utc>,
    pub tags: HashMap<String, String>,
    pub anomaly: Option<Anomaly>,
}

/// Visualization API handler
pub struct VisualizationAPI {
    metrics_store: HashMap<String, Vec<MetricPoint>>,
    max_points: usize,
}

impl VisualizationAPI {
    pub fn new(max_points: usize) -> Self {
        Self {
            metrics_store: HashMap::new(),
            max_points,
        }
    }

    /// Store metric for visualization
    pub fn store_metric(&mut self, metric: MetricPoint) {
        let key = format!("{:?}", metric.metric_type);
        let points = self.metrics_store.entry(key).or_insert_with(Vec::new);

        points.push(metric);

        // Keep only recent points
        if points.len() > self.max_points {
            points.remove(0);
        }
    }

    /// Get dashboard summary
    pub fn get_dashboard_summary(&self) -> ApiResponse<DashboardSummary> {
        let total_threats = self.count_metric(&MetricType::ThreatDetections);
        let active_alerts = self.count_metric(&MetricType::HighSeverityAlerts);
        let compliance_score = self.average_metric(&MetricType::ComplianceScore);
        let system_health = self.calculate_system_health();

        let summary = DashboardSummary {
            total_threats,
            active_alerts,
            compliance_score,
            system_health,
            top_threats: self.get_top_threats(5),
            recent_anomalies: Vec::new(), // Would be populated by anomaly detector
            trend_indicators: self.get_trend_indicators(),
        };

        ApiResponse::success(summary)
    }

    /// Get time series data for specific metric
    pub fn get_time_series(&self, metric_type: &str, duration_hours: i64) -> ApiResponse<TimeSeriesData> {
        let cutoff = Utc::now() - Duration::hours(duration_hours);

        let points = match self.metrics_store.get(metric_type) {
            Some(p) => p.iter()
                .filter(|m| m.timestamp >= cutoff)
                .cloned()
                .collect::<Vec<_>>(),
            None => return ApiResponse::error("Metric type not found".to_string()),
        };

        if points.is_empty() {
            return ApiResponse::error("No data available".to_string());
        }

        let timestamps: Vec<DateTime<Utc>> = points.iter().map(|p| p.timestamp).collect();
        let values: Vec<f64> = points.iter().map(|p| p.value).collect();
        let stats = MetricStats::from_values(&values);

        let data = TimeSeriesData {
            metric_type: metric_type.to_string(),
            timestamps,
            values,
            stats,
        };

        ApiResponse::success(data)
    }

    /// Get real-time metrics stream
    pub fn get_realtime_updates(&self, since: DateTime<Utc>) -> ApiResponse<Vec<RealtimeUpdate>> {
        let mut updates = Vec::new();

        for (metric_type, points) in &self.metrics_store {
            for point in points.iter().filter(|p| p.timestamp > since) {
                updates.push(RealtimeUpdate {
                    metric_type: metric_type.clone(),
                    value: point.value,
                    timestamp: point.timestamp,
                    tags: point.tags.clone(),
                    anomaly: None, // Would be populated if anomaly detected
                });
            }
        }

        updates.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));
        ApiResponse::success(updates)
    }

    /// Get statistics for metric
    pub fn get_metric_stats(&self, metric_type: &str) -> ApiResponse<MetricStats> {
        match self.metrics_store.get(metric_type) {
            Some(points) => {
                let values: Vec<f64> = points.iter().map(|p| p.value).collect();
                ApiResponse::success(MetricStats::from_values(&values))
            }
            None => ApiResponse::error("Metric type not found".to_string()),
        }
    }

    /// Get heatmap data (hour x day)
    pub fn get_heatmap_data(&self, metric_type: &str, days: i64) -> ApiResponse<Vec<Vec<f64>>> {
        let cutoff = Utc::now() - Duration::days(days);

        let points = match self.metrics_store.get(metric_type) {
            Some(p) => p.iter()
                .filter(|m| m.timestamp >= cutoff)
                .cloned()
                .collect::<Vec<_>>(),
            None => return ApiResponse::error("Metric type not found".to_string()),
        };

        // Create 24x7 heatmap (hour x day of week)
        let mut heatmap = vec![vec![0.0; 7]; 24];
        let mut counts = vec![vec![0u32; 7]; 24];

        for point in points {
            let hour = point.timestamp.hour() as usize;
            let day = point.timestamp.weekday().num_days_from_monday() as usize;

            heatmap[hour][day] += point.value;
            counts[hour][day] += 1;
        }

        // Calculate averages
        for hour in 0..24 {
            for day in 0..7 {
                if counts[hour][day] > 0 {
                    heatmap[hour][day] /= counts[hour][day] as f64;
                }
            }
        }

        ApiResponse::success(heatmap)
    }

    /// Get correlation matrix between metrics
    pub fn get_correlation_matrix(&self) -> ApiResponse<HashMap<String, HashMap<String, f64>>> {
        let metric_types: Vec<String> = self.metrics_store.keys().cloned().collect();
        let mut matrix = HashMap::new();

        for type1 in &metric_types {
            let mut row = HashMap::new();

            for type2 in &metric_types {
                let correlation = self.calculate_correlation(type1, type2);
                row.insert(type2.clone(), correlation);
            }

            matrix.insert(type1.clone(), row);
        }

        ApiResponse::success(matrix)
    }

    // Helper methods

    fn count_metric(&self, metric_type: &MetricType) -> u64 {
        let key = format!("{:?}", metric_type);
        self.metrics_store.get(&key)
            .map(|p| p.iter().map(|m| m.value as u64).sum())
            .unwrap_or(0)
    }

    fn average_metric(&self, metric_type: &MetricType) -> f64 {
        let key = format!("{:?}", metric_type);
        self.metrics_store.get(&key)
            .map(|p| {
                if p.is_empty() {
                    0.0
                } else {
                    p.iter().map(|m| m.value).sum::<f64>() / p.len() as f64
                }
            })
            .unwrap_or(0.0)
    }

    fn calculate_system_health(&self) -> f64 {
        // Simplified: 100 - (threat_rate + vulnerability_count)
        let threats = self.count_metric(&MetricType::ThreatDetections) as f64;
        let vulns = self.count_metric(&MetricType::VulnerabilityCount) as f64;

        (100.0 - (threats + vulns).min(100.0)).max(0.0)
    }

    fn get_top_threats(&self, limit: usize) -> Vec<ThreatSummary> {
        // Group threats by tag and count
        let mut threat_counts: HashMap<String, (u64, DateTime<Utc>)> = HashMap::new();

        if let Some(points) = self.metrics_store.get("ThreatDetections") {
            for point in points {
                let threat_type = point.tags.get("type")
                    .cloned()
                    .unwrap_or_else(|| "Unknown".to_string());

                let entry = threat_counts.entry(threat_type.clone())
                    .or_insert((0, point.timestamp));

                entry.0 += point.value as u64;
                if point.timestamp > entry.1 {
                    entry.1 = point.timestamp;
                }
            }
        }

        let mut threats: Vec<ThreatSummary> = threat_counts.iter()
            .map(|(threat_type, (count, last_seen))| ThreatSummary {
                threat_type: threat_type.clone(),
                count: *count,
                severity: if *count > 100 { "High" } else if *count > 10 { "Medium" } else { "Low" }.to_string(),
                last_seen: *last_seen,
            })
            .collect();

        threats.sort_by(|a, b| b.count.cmp(&a.count));
        threats.truncate(limit);
        threats
    }

    fn get_trend_indicators(&self) -> HashMap<String, String> {
        let mut indicators = HashMap::new();

        for (metric_type, points) in &self.metrics_store {
            if points.len() >= 2 {
                let recent = &points[points.len() - 1];
                let previous = &points[points.len() - 2];

                let direction = if recent.value > previous.value * 1.1 {
                    "↑ Increasing"
                } else if recent.value < previous.value * 0.9 {
                    "↓ Decreasing"
                } else {
                    "→ Stable"
                };

                indicators.insert(metric_type.clone(), direction.to_string());
            }
        }

        indicators
    }

    fn calculate_correlation(&self, type1: &str, type2: &str) -> f64 {
        let points1 = match self.metrics_store.get(type1) {
            Some(p) => p,
            None => return 0.0,
        };

        let points2 = match self.metrics_store.get(type2) {
            Some(p) => p,
            None => return 0.0,
        };

        if points1.len() != points2.len() || points1.is_empty() {
            return 0.0;
        }

        let values1: Vec<f64> = points1.iter().map(|p| p.value).collect();
        let values2: Vec<f64> = points2.iter().map(|p| p.value).collect();

        let mean1 = values1.iter().sum::<f64>() / values1.len() as f64;
        let mean2 = values2.iter().sum::<f64>() / values2.len() as f64;

        let covariance: f64 = values1.iter().zip(values2.iter())
            .map(|(v1, v2)| (v1 - mean1) * (v2 - mean2))
            .sum::<f64>() / values1.len() as f64;

        let std1 = (values1.iter().map(|v| (v - mean1).powi(2)).sum::<f64>() / values1.len() as f64).sqrt();
        let std2 = (values2.iter().map(|v| (v - mean2).powi(2)).sum::<f64>() / values2.len() as f64).sqrt();

        if std1 == 0.0 || std2 == 0.0 {
            0.0
        } else {
            covariance / (std1 * std2)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_store_and_retrieve() {
        let mut api = VisualizationAPI::new(100);

        let metric = MetricPoint::new(MetricType::ThreatDetections, 42.0);
        api.store_metric(metric);

        let summary = api.get_dashboard_summary();
        assert!(summary.success);
    }

    #[test]
    fn test_time_series() {
        let mut api = VisualizationAPI::new(100);

        for i in 0..10 {
            let metric = MetricPoint::new(MetricType::ThreatDetections, i as f64);
            api.store_metric(metric);
        }

        let result = api.get_time_series("ThreatDetections", 24);
        assert!(result.success);

        if let Some(data) = result.data {
            assert_eq!(data.values.len(), 10);
        }
    }

    #[test]
    fn test_heatmap() {
        let mut api = VisualizationAPI::new(100);

        for _ in 0..50 {
            let metric = MetricPoint::new(MetricType::ThreatDetections, 10.0);
            api.store_metric(metric);
        }

        let result = api.get_heatmap_data("ThreatDetections", 7);
        assert!(result.success);
    }
}
