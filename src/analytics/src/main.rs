//! Security Metrics & Analytics Dashboard CLI
//!
//! Real-time security analytics and visualization

use analytics::*;
use analytics::metrics_collector::{MetricsCollector, SystemMetricsCollector, SecurityMetricsCollector, ConsoleSubscriber};
use analytics::trend_analyzer::{TrendAnalyzer, AdvancedTrendDetector};
use analytics::anomaly_detector::{AnomalyDetector, DetectionAlgorithm, EnsembleDetector};
use analytics::visualization_api::{VisualizationAPI, ApiResponse};
use analytics::time_series::{TimeSeriesManager};

use std::sync::Arc;
use chrono::{Utc, Duration};

fn main() {
    println!("🔐 SynOS Security Metrics & Analytics Dashboard");
    println!("================================================\n");

    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        print_usage();
        return;
    }

    match args[1].as_str() {
        "demo" => run_demo(),
        "collect" => run_collection(),
        "analyze" => run_analysis(),
        "detect" => run_anomaly_detection(),
        "visualize" => run_visualization(),
        "timeseries" => run_timeseries_demo(),
        _ => print_usage(),
    }
}

fn print_usage() {
    println!("Usage: synos-analytics <command>");
    println!("\nCommands:");
    println!("  demo         - Run comprehensive demo");
    println!("  collect      - Demonstrate metrics collection");
    println!("  analyze      - Demonstrate trend analysis");
    println!("  detect       - Demonstrate anomaly detection");
    println!("  visualize    - Demonstrate visualization API");
    println!("  timeseries   - Demonstrate time series management");
}

fn run_demo() {
    println!("🎯 Running Comprehensive Analytics Demo\n");

    // 1. Metrics Collection
    println!("📊 1. Metrics Collection");
    println!("─────────────────────────");
    let collector = Arc::new(MetricsCollector::new(100, 60));
    let system_collector = SystemMetricsCollector::new(collector.clone());
    let security_collector = SecurityMetricsCollector::new(collector.clone());

    // Collect some metrics
    system_collector.collect_all().unwrap();
    security_collector.record_threat("high", "malware").unwrap();
    security_collector.record_threat("medium", "phishing").unwrap();
    security_collector.record_failed_login("admin", "192.168.1.100").unwrap();
    security_collector.record_vulnerability("critical", "CVE-2024-1234").unwrap();
    security_collector.record_compliance("NIST-CSF-2.0", 85.0).unwrap();

    println!("✅ Collected {} metrics\n", collector.buffer_len());

    // 2. Trend Analysis
    println!("📈 2. Trend Analysis");
    println!("─────────────────────");
    let analyzer = TrendAnalyzer::new(10, 5);

    // Create sample trend data
    let trend_metrics: Vec<MetricPoint> = (0..20)
        .map(|i| MetricPoint::new(MetricType::ThreatDetections, (i as f64) * 1.5 + 10.0))
        .collect();

    match analyzer.analyze(&trend_metrics) {
        Ok(trend) => {
            println!("Metric: {:?}", trend.metric_type);
            println!("Direction: {:?}", trend.direction);
            println!("Change Rate: {:.2}%", trend.change_rate);
            println!("Confidence: {:.2}", trend.confidence);
            println!("Forecast (next 5): {:?}\n", trend.forecast);
        }
        Err(e) => println!("❌ Analysis failed: {}\n", e),
    }

    // 3. Anomaly Detection
    println!("🚨 3. Anomaly Detection");
    println!("───────────────────────");
    let mut detector = AnomalyDetector::new(DetectionAlgorithm::Statistical, 3.0);

    // Build baseline
    for i in 0..50 {
        detector.update_baseline(&MetricType::ThreatDetections, 100.0 + (i as f64) % 10.0);
    }

    // Test normal and anomalous values
    let normal = MetricPoint::new(MetricType::ThreatDetections, 105.0);
    let anomaly = MetricPoint::new(MetricType::ThreatDetections, 500.0);

    println!("Testing normal value (105.0):");
    match detector.detect(&normal).unwrap() {
        Some(a) => println!("  ⚠️  Anomaly detected: {:?}", a.severity),
        None => println!("  ✅ No anomaly"),
    }

    println!("Testing anomalous value (500.0):");
    match detector.detect(&anomaly).unwrap() {
        Some(a) => println!("  ⚠️  Anomaly detected: {:?} (confidence: {:.2})", a.severity, a.confidence),
        None => println!("  ✅ No anomaly"),
    }
    println!();

    // 4. Visualization API
    println!("📊 4. Visualization Dashboard");
    println!("─────────────────────────────");
    let mut viz_api = VisualizationAPI::new(1000);

    // Store metrics
    for i in 0..100 {
        let metric = MetricPoint::new(
            MetricType::ThreatDetections,
            50.0 + (i as f64 % 20.0) + (rand::random::<f64>() * 10.0),
        );
        viz_api.store_metric(metric);
    }

    // Get dashboard summary
    let summary = viz_api.get_dashboard_summary();
    if let Some(data) = summary.data {
        println!("Total Threats: {}", data.total_threats);
        println!("Active Alerts: {}", data.active_alerts);
        println!("Compliance Score: {:.2}%", data.compliance_score);
        println!("System Health: {:.2}%", data.system_health);
        println!("Top Threats: {} identified", data.top_threats.len());
    }
    println!();

    // 5. Time Series Management
    println!("⏱️  5. Time Series Storage");
    println!("──────────────────────────");
    let mut ts_manager = TimeSeriesManager::new(24, 30);

    for i in 0..100 {
        let mut point = MetricPoint::new(MetricType::ThreatDetections, i as f64);
        point.timestamp = Utc::now() - Duration::minutes(i);
        ts_manager.add_point(point).unwrap();
    }

    let stats = ts_manager.storage_stats();
    println!("Stored metrics: {:?}", stats);

    let latest = ts_manager.get_latest(&MetricType::ThreatDetections, 5);
    println!("Latest 5 points: {} records", latest.len());

    println!("\n✅ Comprehensive demo complete!");
}

fn run_collection() {
    println!("📊 Metrics Collection Demo\n");

    let collector = Arc::new(MetricsCollector::new(100, 60));

    // Add console subscriber
    collector.subscribe(Box::new(ConsoleSubscriber)).unwrap();

    let system_collector = SystemMetricsCollector::new(collector.clone());
    let security_collector = SecurityMetricsCollector::new(collector.clone());

    println!("Collecting system metrics...");
    system_collector.collect_all().unwrap();

    println!("\nCollecting security metrics...");
    security_collector.record_threat("critical", "ransomware").unwrap();
    security_collector.record_threat("high", "phishing").unwrap();
    security_collector.record_failed_login("root", "192.168.1.50").unwrap();

    println!("\nBuffer size: {} metrics", collector.buffer_len());
}

fn run_analysis() {
    println!("📈 Trend Analysis Demo\n");

    let analyzer = TrendAnalyzer::new(20, 10);

    // Generate increasing trend
    println!("Analyzing INCREASING trend:");
    let increasing: Vec<MetricPoint> = (0..30)
        .map(|i| MetricPoint::new(MetricType::ThreatDetections, i as f64 * 2.0))
        .collect();

    if let Ok(trend) = analyzer.analyze(&increasing) {
        println!("  Direction: {:?}", trend.direction);
        println!("  Change Rate: {:.2}%", trend.change_rate);
        println!("  Confidence: {:.2}", trend.confidence);
    }

    // Generate decreasing trend
    println!("\nAnalyzing DECREASING trend:");
    let decreasing: Vec<MetricPoint> = (0..30)
        .map(|i| MetricPoint::new(MetricType::VulnerabilityCount, 100.0 - i as f64 * 2.0))
        .collect();

    if let Ok(trend) = analyzer.analyze(&decreasing) {
        println!("  Direction: {:?}", trend.direction);
        println!("  Change Rate: {:.2}%", trend.change_rate);
        println!("  Confidence: {:.2}", trend.confidence);
    }

    // Moving average
    println!("\nCalculating moving average:");
    let values: Vec<f64> = (0..20).map(|i| i as f64).collect();
    let ma = analyzer.moving_average(&values, 5);
    println!("  Original: {:?}", &values[0..10]);
    println!("  MA(5): {:?}", &ma[0..6]);
}

fn run_anomaly_detection() {
    println!("🚨 Anomaly Detection Demo\n");

    println!("1. Statistical Detection (Z-score)");
    println!("───────────────────────────────────");
    let mut stat_detector = AnomalyDetector::new(DetectionAlgorithm::Statistical, 3.0);

    // Build baseline (normal traffic around 100)
    for i in 0..100 {
        stat_detector.update_baseline(&MetricType::NetworkTraffic, 100.0 + (i % 20) as f64);
    }

    // Test anomalies
    test_anomaly(&stat_detector, MetricType::NetworkTraffic, 105.0, "Normal");
    test_anomaly(&stat_detector, MetricType::NetworkTraffic, 200.0, "Spike");
    test_anomaly(&stat_detector, MetricType::NetworkTraffic, 500.0, "Major Spike");

    println!("\n2. Ensemble Detection (Multiple Algorithms)");
    println!("────────────────────────────────────────────");
    let mut ensemble = EnsembleDetector::new();

    // Build ensemble baseline
    for i in 0..100 {
        ensemble.update_baseline(&MetricType::FailedLogins, 5.0 + (i % 5) as f64);
    }

    test_ensemble_anomaly(&ensemble, MetricType::FailedLogins, 6.0, "Normal");
    test_ensemble_anomaly(&ensemble, MetricType::FailedLogins, 50.0, "Brute Force Attack");
}

fn test_anomaly(detector: &AnomalyDetector, metric_type: MetricType, value: f64, label: &str) {
    let metric = MetricPoint::new(metric_type, value);

    match detector.detect(&metric).unwrap() {
        Some(anomaly) => {
            println!("  {} ({:.1}): ⚠️  ANOMALY - {:?} (confidence: {:.2})",
                label, value, anomaly.severity, anomaly.confidence);
        }
        None => {
            println!("  {} ({:.1}): ✅ Normal", label, value);
        }
    }
}

fn test_ensemble_anomaly(detector: &EnsembleDetector, metric_type: MetricType, value: f64, label: &str) {
    let metric = MetricPoint::new(metric_type, value);

    match detector.detect(&metric).unwrap() {
        Some(anomaly) => {
            println!("  {} ({:.1}): 🚨 ANOMALY - {:?} (confidence: {:.2})",
                label, value, anomaly.severity, anomaly.confidence);
        }
        None => {
            println!("  {} ({:.1}): ✅ Normal", label, value);
        }
    }
}

fn run_visualization() {
    println!("📊 Visualization API Demo\n");

    let mut api = VisualizationAPI::new(1000);

    // Generate sample data
    println!("Generating sample metrics...");
    for i in 0..200 {
        let threats = MetricPoint::new(
            MetricType::ThreatDetections,
            50.0 + (i as f64 % 30.0) + rand::random::<f64>() * 20.0
        );
        api.store_metric(threats);

        let vulns = MetricPoint::new(
            MetricType::VulnerabilityCount,
            20.0 + (i as f64 % 10.0)
        );
        api.store_metric(vulns);
    }

    // Dashboard summary
    println!("\n📋 Dashboard Summary:");
    let summary = api.get_dashboard_summary();
    if let Some(data) = summary.data {
        println!("  Total Threats: {}", data.total_threats);
        println!("  System Health: {:.1}%", data.system_health);
        println!("  Trend Indicators:");
        for (metric, trend) in &data.trend_indicators {
            println!("    {}: {}", metric, trend);
        }
    }

    // Time series stats
    println!("\n📈 Time Series Statistics:");
    let stats = api.get_metric_stats("ThreatDetections");
    if let Some(data) = stats.data {
        println!("  Count: {}", data.count);
        println!("  Mean: {:.2}", data.mean);
        println!("  Min: {:.2}", data.min);
        println!("  Max: {:.2}", data.max);
        println!("  95th percentile: {:.2}", data.percentile_95);
    }
}

fn run_timeseries_demo() {
    println!("⏱️  Time Series Management Demo\n");

    let mut manager = TimeSeriesManager::new(24, 30);

    // Add historical data
    println!("Adding time series data...");
    for i in 0..500 {
        let mut point = MetricPoint::new(
            MetricType::ThreatDetections,
            100.0 + (i as f64 % 50.0)
        );
        point.timestamp = Utc::now() - Duration::minutes(i);
        manager.add_point(point).unwrap();
    }

    // Storage stats
    let stats = manager.storage_stats();
    println!("\n📊 Storage Statistics:");
    for (metric, count) in stats {
        println!("  {}: {} points", metric, count);
    }

    // Latest points
    let latest = manager.get_latest(&MetricType::ThreatDetections, 10);
    println!("\n📍 Latest 10 data points:");
    for (i, point) in latest.iter().enumerate() {
        println!("  {}: {:.2} @ {}", i + 1, point.value, point.timestamp.format("%H:%M:%S"));
    }

    // Perform downsampling
    println!("\n🔄 Performing downsampling...");
    manager.downsample_all().unwrap();
    println!("✅ Downsampling complete");
}

// Simple random number generator for demo
mod rand {
    use std::cell::Cell;

    thread_local! {
        static SEED: Cell<u64> = Cell::new(12345);
    }

    pub fn random<T: From<f64>>() -> T {
        SEED.with(|seed| {
            let mut s = seed.get();
            s ^= s << 13;
            s ^= s >> 7;
            s ^= s << 17;
            seed.set(s);
            T::from((s % 1000) as f64 / 1000.0)
        })
    }
}
