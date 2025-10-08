//! Real-time Security Metrics Collection

use crate::{MetricPoint, MetricType, Result, AnalyticsError};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use chrono::{DateTime, Utc, Duration};

/// Metrics collector with buffering
pub struct MetricsCollector {
    buffer: Arc<Mutex<Vec<MetricPoint>>>,
    buffer_size: usize,
    flush_interval: Duration,
    subscribers: Arc<Mutex<Vec<Box<dyn MetricSubscriber + Send>>>>,
}

pub trait MetricSubscriber {
    fn on_metric(&mut self, metric: &MetricPoint);
    fn on_flush(&mut self, metrics: &[MetricPoint]);
}

impl MetricsCollector {
    pub fn new(buffer_size: usize, flush_interval_secs: i64) -> Self {
        Self {
            buffer: Arc::new(Mutex::new(Vec::with_capacity(buffer_size))),
            buffer_size,
            flush_interval: Duration::seconds(flush_interval_secs),
            subscribers: Arc::new(Mutex::new(Vec::new())),
        }
    }

    /// Record a metric
    pub fn record(&self, metric: MetricPoint) -> Result<()> {
        let mut buffer = self.buffer.lock()
            .map_err(|e| AnalyticsError::CollectionError(e.to_string()))?;

        // Notify subscribers
        if let Ok(mut subs) = self.subscribers.lock() {
            for sub in subs.iter_mut() {
                sub.on_metric(&metric);
            }
        }

        buffer.push(metric);

        // Auto-flush if buffer is full
        if buffer.len() >= self.buffer_size {
            let to_flush = buffer.clone();
            drop(buffer); // Release lock
            self.flush_metrics(&to_flush)?;
        }

        Ok(())
    }

    /// Record multiple metrics
    pub fn record_batch(&self, metrics: Vec<MetricPoint>) -> Result<()> {
        for metric in metrics {
            self.record(metric)?;
        }
        Ok(())
    }

    /// Manually flush metrics
    pub fn flush(&self) -> Result<()> {
        let buffer = self.buffer.lock()
            .map_err(|e| AnalyticsError::CollectionError(e.to_string()))?;

        let to_flush = buffer.clone();
        drop(buffer);

        self.flush_metrics(&to_flush)?;

        let mut buffer = self.buffer.lock()
            .map_err(|e| AnalyticsError::CollectionError(e.to_string()))?;
        buffer.clear();

        Ok(())
    }

    fn flush_metrics(&self, metrics: &[MetricPoint]) -> Result<()> {
        if let Ok(mut subs) = self.subscribers.lock() {
            for sub in subs.iter_mut() {
                sub.on_flush(metrics);
            }
        }
        Ok(())
    }

    /// Add subscriber
    pub fn subscribe(&self, subscriber: Box<dyn MetricSubscriber + Send>) -> Result<()> {
        let mut subs = self.subscribers.lock()
            .map_err(|e| AnalyticsError::CollectionError(e.to_string()))?;
        subs.push(subscriber);
        Ok(())
    }

    /// Get current buffer size
    pub fn buffer_len(&self) -> usize {
        self.buffer.lock().map(|b| b.len()).unwrap_or(0)
    }
}

/// System metrics collector
pub struct SystemMetricsCollector {
    collector: Arc<MetricsCollector>,
}

impl SystemMetricsCollector {
    pub fn new(collector: Arc<MetricsCollector>) -> Self {
        Self { collector }
    }

    /// Collect all system metrics
    pub fn collect_all(&self) -> Result<()> {
        self.collect_cpu_metrics()?;
        self.collect_memory_metrics()?;
        self.collect_network_metrics()?;
        self.collect_process_metrics()?;
        Ok(())
    }

    fn collect_cpu_metrics(&self) -> Result<()> {
        // Simulate CPU load collection
        let cpu_load = 45.0; // Would be real system call
        let metric = MetricPoint::new(MetricType::SystemLoad, cpu_load)
            .with_tag("component".to_string(), "cpu".to_string());
        self.collector.record(metric)
    }

    fn collect_memory_metrics(&self) -> Result<()> {
        // Simulate memory usage
        let mem_usage = 62.5; // Would be real system call
        let metric = MetricPoint::new(MetricType::SystemLoad, mem_usage)
            .with_tag("component".to_string(), "memory".to_string());
        self.collector.record(metric)
    }

    fn collect_network_metrics(&self) -> Result<()> {
        // Simulate network traffic
        let traffic_mbps = 120.0; // Would be real network stats
        let metric = MetricPoint::new(MetricType::NetworkTraffic, traffic_mbps);
        self.collector.record(metric)
    }

    fn collect_process_metrics(&self) -> Result<()> {
        // Simulate process count
        let process_count = 256.0; // Would be real process count
        let metric = MetricPoint::new(MetricType::ProcessCount, process_count);
        self.collector.record(metric)
    }
}

/// Security metrics collector
pub struct SecurityMetricsCollector {
    collector: Arc<MetricsCollector>,
}

impl SecurityMetricsCollector {
    pub fn new(collector: Arc<MetricsCollector>) -> Self {
        Self { collector }
    }

    /// Record threat detection
    pub fn record_threat(&self, severity: &str, threat_type: &str) -> Result<()> {
        let metric = MetricPoint::new(MetricType::ThreatDetections, 1.0)
            .with_tag("severity".to_string(), severity.to_string())
            .with_tag("type".to_string(), threat_type.to_string());
        self.collector.record(metric)
    }

    /// Record failed login attempt
    pub fn record_failed_login(&self, username: &str, ip: &str) -> Result<()> {
        let metric = MetricPoint::new(MetricType::FailedLogins, 1.0)
            .with_tag("username".to_string(), username.to_string())
            .with_tag("ip".to_string(), ip.to_string());
        self.collector.record(metric)
    }

    /// Record vulnerability
    pub fn record_vulnerability(&self, severity: &str, cve: &str) -> Result<()> {
        let metric = MetricPoint::new(MetricType::VulnerabilityCount, 1.0)
            .with_tag("severity".to_string(), severity.to_string())
            .with_tag("cve".to_string(), cve.to_string());
        self.collector.record(metric)
    }

    /// Record compliance score
    pub fn record_compliance(&self, framework: &str, score: f64) -> Result<()> {
        let metric = MetricPoint::new(MetricType::ComplianceScore, score)
            .with_tag("framework".to_string(), framework.to_string());
        self.collector.record(metric)
    }

    /// Record privilege escalation
    pub fn record_privilege_escalation(&self, user: &str, from: &str, to: &str) -> Result<()> {
        let metric = MetricPoint::new(MetricType::PrivilegeEscalations, 1.0)
            .with_tag("user".to_string(), user.to_string())
            .with_tag("from".to_string(), from.to_string())
            .with_tag("to".to_string(), to.to_string());
        self.collector.record(metric)
    }
}

/// Console subscriber (prints metrics)
pub struct ConsoleSubscriber;

impl MetricSubscriber for ConsoleSubscriber {
    fn on_metric(&mut self, metric: &MetricPoint) {
        println!("[METRIC] {:?} = {} @ {}",
            metric.metric_type,
            metric.value,
            metric.timestamp.format("%Y-%m-%d %H:%M:%S")
        );
    }

    fn on_flush(&mut self, metrics: &[MetricPoint]) {
        println!("[FLUSH] Flushing {} metrics", metrics.len());
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_collector() {
        let collector = MetricsCollector::new(100, 60);
        let metric = MetricPoint::new(MetricType::ThreatDetections, 5.0);

        assert!(collector.record(metric).is_ok());
        assert_eq!(collector.buffer_len(), 1);
    }

    #[test]
    fn test_batch_recording() {
        let collector = MetricsCollector::new(100, 60);
        let metrics = vec![
            MetricPoint::new(MetricType::ThreatDetections, 1.0),
            MetricPoint::new(MetricType::ThreatDetections, 2.0),
            MetricPoint::new(MetricType::ThreatDetections, 3.0),
        ];

        assert!(collector.record_batch(metrics).is_ok());
        assert_eq!(collector.buffer_len(), 3);
    }

    #[test]
    fn test_auto_flush() {
        let collector = MetricsCollector::new(2, 60); // Small buffer

        collector.record(MetricPoint::new(MetricType::ThreatDetections, 1.0)).unwrap();
        collector.record(MetricPoint::new(MetricType::ThreatDetections, 2.0)).unwrap();

        // Third record should trigger flush
        collector.record(MetricPoint::new(MetricType::ThreatDetections, 3.0)).unwrap();
    }
}
