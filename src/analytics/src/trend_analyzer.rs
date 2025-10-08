//! Trend Analysis with Forecasting
//!
//! Analyzes metric trends and provides forecasting capabilities

use crate::{MetricPoint, MetricType, TrendDirection, TrendAnalysis, Result, AnalyticsError};
use chrono::{DateTime, Utc, Duration};

/// Trend analyzer for time series data
pub struct TrendAnalyzer {
    window_size: usize,
    forecast_points: usize,
}

impl TrendAnalyzer {
    pub fn new(window_size: usize, forecast_points: usize) -> Self {
        Self {
            window_size,
            forecast_points,
        }
    }

    /// Analyze trend from metric points
    pub fn analyze(&self, metrics: &[MetricPoint]) -> Result<TrendAnalysis> {
        if metrics.is_empty() {
            return Err(AnalyticsError::AnalysisError("No metrics provided".to_string()));
        }

        let metric_type = metrics[0].metric_type.clone();
        let values: Vec<f64> = metrics.iter().map(|m| m.value).collect();

        // Calculate linear regression
        let (slope, intercept, r_squared) = self.linear_regression(&values);

        // Determine trend direction
        let direction = self.determine_direction(slope, r_squared);

        // Calculate change rate (percentage)
        let change_rate = if values[0] != 0.0 {
            ((values[values.len() - 1] - values[0]) / values[0]) * 100.0
        } else {
            0.0
        };

        // Generate forecast
        let forecast = self.forecast(&values, slope, intercept);

        Ok(TrendAnalysis {
            metric_type,
            direction,
            change_rate,
            confidence: r_squared,
            forecast,
            analyzed_at: Utc::now(),
        })
    }

    /// Linear regression calculation
    fn linear_regression(&self, values: &[f64]) -> (f64, f64, f64) {
        let n = values.len() as f64;
        let x: Vec<f64> = (0..values.len()).map(|i| i as f64).collect();

        // Calculate means
        let mean_x = x.iter().sum::<f64>() / n;
        let mean_y = values.iter().sum::<f64>() / n;

        // Calculate slope
        let numerator: f64 = x.iter().zip(values.iter())
            .map(|(xi, yi)| (xi - mean_x) * (yi - mean_y))
            .sum();

        let denominator: f64 = x.iter()
            .map(|xi| (xi - mean_x).powi(2))
            .sum();

        let slope = if denominator != 0.0 {
            numerator / denominator
        } else {
            0.0
        };

        // Calculate intercept
        let intercept = mean_y - slope * mean_x;

        // Calculate R-squared
        let ss_tot: f64 = values.iter()
            .map(|yi| (yi - mean_y).powi(2))
            .sum();

        let ss_res: f64 = x.iter().zip(values.iter())
            .map(|(xi, yi)| {
                let predicted = slope * xi + intercept;
                (yi - predicted).powi(2)
            })
            .sum();

        let r_squared = if ss_tot != 0.0 {
            1.0 - (ss_res / ss_tot)
        } else {
            0.0
        };

        (slope, intercept, r_squared)
    }

    /// Determine trend direction
    fn determine_direction(&self, slope: f64, r_squared: f64) -> TrendDirection {
        const SLOPE_THRESHOLD: f64 = 0.1;
        const VOLATILE_THRESHOLD: f64 = 0.3;

        if r_squared < VOLATILE_THRESHOLD {
            TrendDirection::Volatile
        } else if slope > SLOPE_THRESHOLD {
            TrendDirection::Increasing
        } else if slope < -SLOPE_THRESHOLD {
            TrendDirection::Decreasing
        } else {
            TrendDirection::Stable
        }
    }

    /// Generate forecast points
    fn forecast(&self, values: &[f64], slope: f64, intercept: f64) -> Vec<f64> {
        let start_x = values.len() as f64;
        (0..self.forecast_points)
            .map(|i| {
                let x = start_x + i as f64;
                slope * x + intercept
            })
            .collect()
    }

    /// Moving average calculation
    pub fn moving_average(&self, values: &[f64], window: usize) -> Vec<f64> {
        if values.len() < window {
            return vec![];
        }

        values.windows(window)
            .map(|w| w.iter().sum::<f64>() / window as f64)
            .collect()
    }

    /// Exponential moving average
    pub fn exponential_moving_average(&self, values: &[f64], alpha: f64) -> Vec<f64> {
        if values.is_empty() {
            return vec![];
        }

        let mut ema = Vec::with_capacity(values.len());
        ema.push(values[0]);

        for i in 1..values.len() {
            let new_ema = alpha * values[i] + (1.0 - alpha) * ema[i - 1];
            ema.push(new_ema);
        }

        ema
    }

    /// Seasonal decomposition (simple)
    pub fn detect_seasonality(&self, values: &[f64], period: usize) -> Option<Vec<f64>> {
        if values.len() < period * 2 {
            return None;
        }

        let mut seasonal = vec![0.0; period];
        let cycles = values.len() / period;

        for i in 0..period {
            let mut sum = 0.0;
            for cycle in 0..cycles {
                sum += values[cycle * period + i];
            }
            seasonal[i] = sum / cycles as f64;
        }

        Some(seasonal)
    }
}

/// Advanced trend detection
pub struct AdvancedTrendDetector {
    analyzer: TrendAnalyzer,
}

impl AdvancedTrendDetector {
    pub fn new() -> Self {
        Self {
            analyzer: TrendAnalyzer::new(50, 10),
        }
    }

    /// Detect multiple trend types
    pub fn detect_all_trends(&self, metrics: &[MetricPoint]) -> Result<Vec<TrendAnalysis>> {
        let mut trends = Vec::new();

        // Group by metric type
        let mut grouped: std::collections::HashMap<String, Vec<MetricPoint>> =
            std::collections::HashMap::new();

        for metric in metrics {
            let key = format!("{:?}", metric.metric_type);
            grouped.entry(key).or_insert_with(Vec::new).push(metric.clone());
        }

        // Analyze each group
        for (_, group_metrics) in grouped {
            if group_metrics.len() >= 3 {
                if let Ok(trend) = self.analyzer.analyze(&group_metrics) {
                    trends.push(trend);
                }
            }
        }

        Ok(trends)
    }

    /// Detect trend changes (breakpoints)
    pub fn detect_breakpoints(&self, values: &[f64]) -> Vec<usize> {
        let mut breakpoints = Vec::new();
        const THRESHOLD: f64 = 2.0; // Standard deviations

        if values.len() < 3 {
            return breakpoints;
        }

        for i in 1..values.len() - 1 {
            let before = &values[..i];
            let after = &values[i..];

            let mean_before = before.iter().sum::<f64>() / before.len() as f64;
            let mean_after = after.iter().sum::<f64>() / after.len() as f64;

            let std_before = self.calculate_std(before, mean_before);
            let std_after = self.calculate_std(after, mean_after);

            let diff = (mean_after - mean_before).abs();
            let avg_std = (std_before + std_after) / 2.0;

            if avg_std > 0.0 && diff / avg_std > THRESHOLD {
                breakpoints.push(i);
            }
        }

        breakpoints
    }

    fn calculate_std(&self, values: &[f64], mean: f64) -> f64 {
        if values.is_empty() {
            return 0.0;
        }

        let variance = values.iter()
            .map(|v| (v - mean).powi(2))
            .sum::<f64>() / values.len() as f64;

        variance.sqrt()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::MetricType;

    #[test]
    fn test_linear_regression() {
        let analyzer = TrendAnalyzer::new(10, 5);
        let values = vec![1.0, 2.0, 3.0, 4.0, 5.0];

        let (slope, intercept, r_squared) = analyzer.linear_regression(&values);

        assert!((slope - 1.0).abs() < 0.01);
        assert!((r_squared - 1.0).abs() < 0.01); // Perfect fit
    }

    #[test]
    fn test_trend_analysis() {
        let analyzer = TrendAnalyzer::new(10, 5);
        let metrics: Vec<MetricPoint> = (0..10)
            .map(|i| MetricPoint::new(MetricType::ThreatDetections, i as f64))
            .collect();

        let result = analyzer.analyze(&metrics);
        assert!(result.is_ok());

        let trend = result.unwrap();
        assert_eq!(trend.direction, TrendDirection::Increasing);
    }

    #[test]
    fn test_moving_average() {
        let analyzer = TrendAnalyzer::new(10, 5);
        let values = vec![1.0, 2.0, 3.0, 4.0, 5.0];

        let ma = analyzer.moving_average(&values, 3);
        assert_eq!(ma.len(), 3);
        assert_eq!(ma[0], 2.0); // (1+2+3)/3
    }

    #[test]
    fn test_breakpoint_detection() {
        let detector = AdvancedTrendDetector::new();
        let values = vec![1.0, 1.0, 1.0, 10.0, 10.0, 10.0];

        let breakpoints = detector.detect_breakpoints(&values);
        assert!(!breakpoints.is_empty());
    }
}
