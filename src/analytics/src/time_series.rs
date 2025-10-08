//! Time Series Data Management
//!
//! Efficient storage and retrieval of time-series metrics

use crate::{MetricPoint, MetricType, Result, AnalyticsError};
use chrono::{DateTime, Utc, Duration};
use std::collections::{HashMap, BTreeMap};
use serde::{Deserialize, Serialize};

/// Time series storage with automatic downsampling
pub struct TimeSeriesStore {
    // Raw data (high resolution, recent)
    raw: BTreeMap<i64, MetricPoint>,
    // Downsampled data (lower resolution, historical)
    hourly: BTreeMap<i64, AggregatedPoint>,
    daily: BTreeMap<i64, AggregatedPoint>,
    // Retention policies
    raw_retention_hours: i64,
    hourly_retention_days: i64,
}

/// Aggregated metric point
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AggregatedPoint {
    pub timestamp: DateTime<Utc>,
    pub min: f64,
    pub max: f64,
    pub mean: f64,
    pub count: usize,
    pub sum: f64,
}

impl TimeSeriesStore {
    pub fn new(raw_retention_hours: i64, hourly_retention_days: i64) -> Self {
        Self {
            raw: BTreeMap::new(),
            hourly: BTreeMap::new(),
            daily: BTreeMap::new(),
            raw_retention_hours,
            hourly_retention_days,
        }
    }

    /// Add metric point
    pub fn add_point(&mut self, point: MetricPoint) -> Result<()> {
        let timestamp_nanos = point.timestamp.timestamp_nanos_opt()
            .ok_or_else(|| AnalyticsError::TimeSeriesError("Invalid timestamp".to_string()))?;

        self.raw.insert(timestamp_nanos, point);
        self.cleanup_old_data()?;

        Ok(())
    }

    /// Get points in time range
    pub fn get_range(&self, start: DateTime<Utc>, end: DateTime<Utc>) -> Vec<MetricPoint> {
        let start_nanos = start.timestamp_nanos_opt().unwrap_or(0);
        let end_nanos = end.timestamp_nanos_opt().unwrap_or(i64::MAX);

        self.raw.range(start_nanos..=end_nanos)
            .map(|(_, point)| point.clone())
            .collect()
    }

    /// Get latest N points
    pub fn get_latest(&self, count: usize) -> Vec<MetricPoint> {
        self.raw.iter()
            .rev()
            .take(count)
            .map(|(_, point)| point.clone())
            .collect()
    }

    /// Downsample to hourly aggregates
    pub fn downsample_to_hourly(&mut self) -> Result<()> {
        let cutoff = Utc::now() - Duration::hours(self.raw_retention_hours);
        let cutoff_nanos = cutoff.timestamp_nanos_opt().unwrap_or(0);

        // Group points by hour
        let mut hourly_groups: HashMap<i64, Vec<f64>> = HashMap::new();

        for (ts, point) in self.raw.range(..cutoff_nanos) {
            let hour_ts = (ts / 3_600_000_000_000) * 3_600_000_000_000; // Round to hour
            hourly_groups.entry(hour_ts).or_insert_with(Vec::new).push(point.value);
        }

        // Create aggregated points
        for (hour_ts, values) in hourly_groups {
            if values.is_empty() {
                continue;
            }

            let min = values.iter().cloned().min_by(|a, b| a.partial_cmp(b).unwrap()).unwrap();
            let max = values.iter().cloned().max_by(|a, b| a.partial_cmp(b).unwrap()).unwrap();
            let sum: f64 = values.iter().sum();
            let count = values.len();
            let mean = sum / count as f64;

            let timestamp = DateTime::from_timestamp_nanos(hour_ts);

            self.hourly.insert(hour_ts, AggregatedPoint {
                timestamp,
                min,
                max,
                mean,
                count,
                sum,
            });
        }

        Ok(())
    }

    /// Downsample to daily aggregates
    pub fn downsample_to_daily(&mut self) -> Result<()> {
        let cutoff = Utc::now() - Duration::days(self.hourly_retention_days);
        let cutoff_nanos = cutoff.timestamp_nanos_opt().unwrap_or(0);

        // Group hourly points by day
        let mut daily_groups: HashMap<i64, Vec<f64>> = HashMap::new();

        for (ts, point) in self.hourly.range(..cutoff_nanos) {
            let day_ts = (ts / 86_400_000_000_000) * 86_400_000_000_000; // Round to day
            daily_groups.entry(day_ts).or_insert_with(Vec::new).push(point.mean);
        }

        // Create daily aggregates
        for (day_ts, values) in daily_groups {
            if values.is_empty() {
                continue;
            }

            let min = values.iter().cloned().min_by(|a, b| a.partial_cmp(b).unwrap()).unwrap();
            let max = values.iter().cloned().max_by(|a, b| a.partial_cmp(b).unwrap()).unwrap();
            let sum: f64 = values.iter().sum();
            let count = values.len();
            let mean = sum / count as f64;

            let timestamp = DateTime::from_timestamp_nanos(day_ts);

            self.daily.insert(day_ts, AggregatedPoint {
                timestamp,
                min,
                max,
                mean,
                count,
                sum,
            });
        }

        Ok(())
    }

    /// Cleanup old data based on retention policies
    fn cleanup_old_data(&mut self) -> Result<()> {
        // Clean raw data
        let raw_cutoff = Utc::now() - Duration::hours(self.raw_retention_hours);
        let raw_cutoff_nanos = raw_cutoff.timestamp_nanos_opt().unwrap_or(0);
        self.raw.retain(|ts, _| *ts >= raw_cutoff_nanos);

        // Clean hourly data
        let hourly_cutoff = Utc::now() - Duration::days(self.hourly_retention_days);
        let hourly_cutoff_nanos = hourly_cutoff.timestamp_nanos_opt().unwrap_or(0);
        self.hourly.retain(|ts, _| *ts >= hourly_cutoff_nanos);

        Ok(())
    }

    /// Get statistics for time range
    pub fn get_stats(&self, start: DateTime<Utc>, end: DateTime<Utc>) -> Option<AggregatedPoint> {
        let points = self.get_range(start, end);

        if points.is_empty() {
            return None;
        }

        let values: Vec<f64> = points.iter().map(|p| p.value).collect();
        let min = values.iter().cloned().min_by(|a, b| a.partial_cmp(b).unwrap())?;
        let max = values.iter().cloned().max_by(|a, b| a.partial_cmp(b).unwrap())?;
        let sum: f64 = values.iter().sum();
        let count = values.len();
        let mean = sum / count as f64;

        Some(AggregatedPoint {
            timestamp: Utc::now(),
            min,
            max,
            mean,
            count,
            sum,
        })
    }

    /// Get hourly aggregates
    pub fn get_hourly_range(&self, start: DateTime<Utc>, end: DateTime<Utc>) -> Vec<AggregatedPoint> {
        let start_nanos = start.timestamp_nanos_opt().unwrap_or(0);
        let end_nanos = end.timestamp_nanos_opt().unwrap_or(i64::MAX);

        self.hourly.range(start_nanos..=end_nanos)
            .map(|(_, point)| point.clone())
            .collect()
    }

    /// Get daily aggregates
    pub fn get_daily_range(&self, start: DateTime<Utc>, end: DateTime<Utc>) -> Vec<AggregatedPoint> {
        let start_nanos = start.timestamp_nanos_opt().unwrap_or(0);
        let end_nanos = end.timestamp_nanos_opt().unwrap_or(i64::MAX);

        self.daily.range(start_nanos..=end_nanos)
            .map(|(_, point)| point.clone())
            .collect()
    }

    /// Get total point count
    pub fn total_points(&self) -> usize {
        self.raw.len() + self.hourly.len() + self.daily.len()
    }
}

/// Multi-metric time series manager
pub struct TimeSeriesManager {
    stores: HashMap<String, TimeSeriesStore>,
    raw_retention_hours: i64,
    hourly_retention_days: i64,
}

impl TimeSeriesManager {
    pub fn new(raw_retention_hours: i64, hourly_retention_days: i64) -> Self {
        Self {
            stores: HashMap::new(),
            raw_retention_hours,
            hourly_retention_days,
        }
    }

    /// Add metric point
    pub fn add_point(&mut self, point: MetricPoint) -> Result<()> {
        let key = format!("{:?}", point.metric_type);

        let store = self.stores.entry(key).or_insert_with(|| {
            TimeSeriesStore::new(self.raw_retention_hours, self.hourly_retention_days)
        });

        store.add_point(point)
    }

    /// Get points for metric type
    pub fn get_metric_range(
        &self,
        metric_type: &MetricType,
        start: DateTime<Utc>,
        end: DateTime<Utc>,
    ) -> Vec<MetricPoint> {
        let key = format!("{:?}", metric_type);

        self.stores.get(&key)
            .map(|store| store.get_range(start, end))
            .unwrap_or_default()
    }

    /// Get latest points for metric
    pub fn get_latest(&self, metric_type: &MetricType, count: usize) -> Vec<MetricPoint> {
        let key = format!("{:?}", metric_type);

        self.stores.get(&key)
            .map(|store| store.get_latest(count))
            .unwrap_or_default()
    }

    /// Perform downsampling on all stores
    pub fn downsample_all(&mut self) -> Result<()> {
        for store in self.stores.values_mut() {
            store.downsample_to_hourly()?;
            store.downsample_to_daily()?;
        }
        Ok(())
    }

    /// Get total storage metrics
    pub fn storage_stats(&self) -> HashMap<String, usize> {
        self.stores.iter()
            .map(|(k, v)| (k.clone(), v.total_points()))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_time_series_store() {
        let mut store = TimeSeriesStore::new(24, 30);

        let point = MetricPoint::new(MetricType::ThreatDetections, 42.0);
        assert!(store.add_point(point).is_ok());

        let latest = store.get_latest(1);
        assert_eq!(latest.len(), 1);
    }

    #[test]
    fn test_range_query() {
        let mut store = TimeSeriesStore::new(24, 30);

        for i in 0..10 {
            let mut point = MetricPoint::new(MetricType::ThreatDetections, i as f64);
            point.timestamp = Utc::now() - Duration::minutes(i);
            store.add_point(point).unwrap();
        }

        let start = Utc::now() - Duration::minutes(5);
        let end = Utc::now();
        let range = store.get_range(start, end);

        assert!(!range.is_empty());
    }

    #[test]
    fn test_manager() {
        let mut manager = TimeSeriesManager::new(24, 30);

        let point1 = MetricPoint::new(MetricType::ThreatDetections, 10.0);
        let point2 = MetricPoint::new(MetricType::HighSeverityAlerts, 5.0);

        assert!(manager.add_point(point1).is_ok());
        assert!(manager.add_point(point2).is_ok());

        let stats = manager.storage_stats();
        assert_eq!(stats.len(), 2);
    }
}
