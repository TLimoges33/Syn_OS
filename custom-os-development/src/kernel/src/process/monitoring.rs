//! Real-Time Process Monitoring Dashboard
//!
//! Provides comprehensive real-time monitoring capabilities with consciousness integration
//! for system-wide process observation, performance tracking, and intelligent alerting.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::sync::atomic::{AtomicU64, AtomicU32, Ordering};
use spin::{Mutex, RwLock};

use crate::process_lifecycle::{ProcessId, ProcessState, ProcessError};
use crate::process::debugging::{ProcessProfile, DebugEvent};
use crate::process::migration::{MigrationStats, CoreStats};
use syn_ai::ConsciousnessInterface;

/// System-wide monitoring metrics
#[derive(Debug, Clone)]
pub struct SystemMetrics {
    pub total_processes: u32,
    pub running_processes: u32,
    pub blocked_processes: u32,
    pub zombie_processes: u32,
    pub cpu_utilization: f32,
    pub memory_utilization: f32,
    pub load_average_1m: f32,
    pub load_average_5m: f32,
    pub load_average_15m: f32,
    pub context_switches_per_sec: f32,
    pub interrupts_per_sec: f32,
    pub consciousness_score: f32,
    pub timestamp: u64,
}

/// Process monitoring metrics
#[derive(Debug, Clone)]
pub struct ProcessMetrics {
    pub pid: ProcessId,
    pub name: String,
    pub state: ProcessState,
    pub cpu_usage: f32,
    pub memory_usage: usize,
    pub memory_percentage: f32,
    pub thread_count: u32,
    pub open_files: u32,
    pub network_connections: u32,
    pub parent_pid: Option<ProcessId>,
    pub children_count: u32,
    pub priority: i32,
    pub nice_value: i32,
    pub consciousness_state: f32,
    pub last_activity: u64,
    pub creation_time: u64,
}

/// Alert types for monitoring
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AlertType {
    HighCPUUsage,
    HighMemoryUsage,
    ProcessHanging,
    MemoryLeak,
    ThrashingDetected,
    ConsciousnessAnomaly,
    SecurityThreat,
    PerformanceDegradation,
    ResourceExhaustion,
    UnresponsiveProcess,
}

/// Monitoring alert
#[derive(Debug, Clone)]
pub struct MonitoringAlert {
    pub alert_id: u32,
    pub alert_type: AlertType,
    pub severity: AlertSeverity,
    pub pid: Option<ProcessId>,
    pub message: String,
    pub details: String,
    pub timestamp: u64,
    pub acknowledged: bool,
    pub auto_resolved: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum AlertSeverity {
    Info = 1,
    Warning = 2,
    Error = 3,
    Critical = 4,
    Emergency = 5,
}

/// Dashboard widget configuration
#[derive(Debug, Clone)]
pub struct DashboardWidget {
    pub widget_id: u32,
    pub widget_type: WidgetType,
    pub title: String,
    pub refresh_interval: u64,
    pub data_retention: u64,
    pub enabled: bool,
    pub position: (u32, u32),
    pub size: (u32, u32),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WidgetType {
    SystemOverview,
    ProcessList,
    CPUGraph,
    MemoryGraph,
    NetworkGraph,
    ConsciousnessMap,
    AlertPanel,
    PerformanceHeatmap,
    ProcessTree,
    ResourceUsage,
}

/// Historical data point for trending
#[derive(Debug, Clone)]
pub struct DataPoint {
    pub timestamp: u64,
    pub value: f32,
    pub metadata: Option<String>,
}

/// Time series data for dashboard charts
#[derive(Debug, Clone)]
pub struct TimeSeries {
    pub name: String,
    pub data_points: Vec<DataPoint>,
    pub max_points: usize,
    pub aggregation_interval: u64,
}

impl TimeSeries {
    pub fn new(name: String, max_points: usize, aggregation_interval: u64) -> Self {
        Self {
            name,
            data_points: Vec::new(),
            max_points,
            aggregation_interval,
        }
    }

    pub fn add_point(&mut self, value: f32, metadata: Option<String>) {
        let timestamp = get_current_time();
        let point = DataPoint { timestamp, value, metadata };

        self.data_points.push(point);

        // Maintain max points
        if self.data_points.len() > self.max_points {
            self.data_points.remove(0);
        }
    }

    pub fn get_latest(&self) -> Option<&DataPoint> {
        self.data_points.last()
    }

    pub fn get_average(&self, duration: u64) -> f32 {
        let cutoff = get_current_time() - duration;
        let recent_points: Vec<&DataPoint> = self.data_points.iter()
            .filter(|p| p.timestamp >= cutoff)
            .collect();

        if recent_points.is_empty() {
            return 0.0;
        }

        let sum: f32 = recent_points.iter().map(|p| p.value).sum();
        sum / recent_points.len() as f32
    }
}

/// Real-time monitoring dashboard
pub struct ProcessMonitoringDashboard {
    system_metrics: RwLock<SystemMetrics>,
    process_metrics: RwLock<BTreeMap<ProcessId, ProcessMetrics>>,
    alerts: Mutex<Vec<MonitoringAlert>>,
    widgets: RwLock<BTreeMap<u32, DashboardWidget>>,
    time_series: RwLock<BTreeMap<String, TimeSeries>>,
    consciousness_interface: ConsciousnessInterface,
    next_alert_id: AtomicU32,
    next_widget_id: AtomicU32,
    monitoring_enabled: AtomicU32,
    alert_thresholds: RwLock<BTreeMap<AlertType, f32>>,
    update_interval: u64,
    last_update: AtomicU64,
}

impl ProcessMonitoringDashboard {
    /// Create a new monitoring dashboard
    pub fn new() -> Self {
        let mut dashboard = Self {
            system_metrics: RwLock::new(SystemMetrics::default()),
            process_metrics: RwLock::new(BTreeMap::new()),
            alerts: Mutex::new(Vec::new()),
            widgets: RwLock::new(BTreeMap::new()),
            time_series: RwLock::new(BTreeMap::new()),
            consciousness_interface: ConsciousnessInterface::new(),
            next_alert_id: AtomicU32::new(1),
            next_widget_id: AtomicU32::new(1),
            monitoring_enabled: AtomicU32::new(1),
            alert_thresholds: RwLock::new(BTreeMap::new()),
            update_interval: 1000, // 1 second
            last_update: AtomicU64::new(0),
        };

        dashboard.initialize_default_configuration();
        dashboard
    }

    /// Initialize default dashboard configuration
    fn initialize_default_configuration(&self) {
        // Set default alert thresholds
        let mut thresholds = self.alert_thresholds.write();
        thresholds.insert(AlertType::HighCPUUsage, 80.0);
        thresholds.insert(AlertType::HighMemoryUsage, 85.0);
        thresholds.insert(AlertType::ProcessHanging, 30000.0); // 30 seconds
        thresholds.insert(AlertType::MemoryLeak, 50.0); // 50MB/minute growth
        thresholds.insert(AlertType::ConsciousnessAnomaly, 20.0);

        // Initialize default time series
        let mut time_series = self.time_series.write();
        time_series.insert("cpu_usage".to_string(), TimeSeries::new("CPU Usage".to_string(), 300, 1000));
        time_series.insert("memory_usage".to_string(), TimeSeries::new("Memory Usage".to_string(), 300, 1000));
        time_series.insert("process_count".to_string(), TimeSeries::new("Process Count".to_string(), 300, 1000));
        time_series.insert("consciousness_score".to_string(), TimeSeries::new("Consciousness Score".to_string(), 300, 1000));

        // Create default widgets
        self.create_default_widgets();
    }

    /// Create default dashboard widgets
    fn create_default_widgets(&self) {
        let widgets = vec![
            DashboardWidget {
                widget_id: self.next_widget_id.fetch_add(1, Ordering::SeqCst),
                widget_type: WidgetType::SystemOverview,
                title: "System Overview".to_string(),
                refresh_interval: 1000,
                data_retention: 3600000, // 1 hour
                enabled: true,
                position: (0, 0),
                size: (4, 2),
            },
            DashboardWidget {
                widget_id: self.next_widget_id.fetch_add(1, Ordering::SeqCst),
                widget_type: WidgetType::ProcessList,
                title: "Top Processes".to_string(),
                refresh_interval: 2000,
                data_retention: 300000, // 5 minutes
                enabled: true,
                position: (4, 0),
                size: (4, 4),
            },
            DashboardWidget {
                widget_id: self.next_widget_id.fetch_add(1, Ordering::SeqCst),
                widget_type: WidgetType::CPUGraph,
                title: "CPU Usage History".to_string(),
                refresh_interval: 1000,
                data_retention: 1800000, // 30 minutes
                enabled: true,
                position: (0, 2),
                size: (2, 2),
            },
            DashboardWidget {
                widget_id: self.next_widget_id.fetch_add(1, Ordering::SeqCst),
                widget_type: WidgetType::ConsciousnessMap,
                title: "Consciousness Activity".to_string(),
                refresh_interval: 5000,
                data_retention: 3600000, // 1 hour
                enabled: true,
                position: (2, 2),
                size: (2, 2),
            },
        ];

        let mut widget_map = self.widgets.write();
        for widget in widgets {
            widget_map.insert(widget.widget_id, widget);
        }
    }

    /// Update system metrics
    pub fn update_system_metrics(&self) {
        let current_time = get_current_time();

        // Collect system-wide metrics
        let total_processes = self.count_total_processes();
        let running_processes = self.count_running_processes();
        let blocked_processes = self.count_blocked_processes();
        let zombie_processes = self.count_zombie_processes();

        let cpu_utilization = self.calculate_system_cpu_usage();
        let memory_utilization = self.calculate_system_memory_usage();
        let consciousness_score = self.consciousness_interface.get_system_consciousness_score();

        let metrics = SystemMetrics {
            total_processes,
            running_processes,
            blocked_processes,
            zombie_processes,
            cpu_utilization,
            memory_utilization,
            load_average_1m: self.calculate_load_average(60000),
            load_average_5m: self.calculate_load_average(300000),
            load_average_15m: self.calculate_load_average(900000),
            context_switches_per_sec: self.calculate_context_switches_rate(),
            interrupts_per_sec: self.calculate_interrupt_rate(),
            consciousness_score,
            timestamp: current_time,
        };

        // Update time series
        self.update_time_series("cpu_usage", cpu_utilization);
        self.update_time_series("memory_usage", memory_utilization);
        self.update_time_series("process_count", total_processes as f32);
        self.update_time_series("consciousness_score", consciousness_score);

        // Check for alerts
        self.check_system_alerts(&metrics);

        // Store metrics
        *self.system_metrics.write() = metrics;
        self.last_update.store(current_time, Ordering::SeqCst);
    }

    /// Update process metrics for all processes
    pub fn update_process_metrics(&self) {
        let mut metrics_map = self.process_metrics.write();

        // In a real implementation, this would iterate through actual processes
        // For now, we'll simulate some process data
        for pid in 1..=10 {
            let metrics = ProcessMetrics {
                pid,
                name: format!("process_{}", pid),
                state: ProcessState::Running,
                cpu_usage: (pid as f32 * 5.0) % 100.0,
                memory_usage: (pid as usize * 1024 * 1024) % (512 * 1024 * 1024),
                memory_percentage: ((pid as f32 * 2.0) % 20.0),
                thread_count: (pid % 4) + 1,
                open_files: (pid * 3) % 50,
                network_connections: (pid % 10),
                parent_pid: if pid > 1 { Some(pid - 1) } else { None },
                children_count: if pid < 5 { pid - 1 } else { 0 },
                priority: 0,
                nice_value: 0,
                consciousness_state: self.consciousness_interface.get_process_consciousness(pid),
                last_activity: get_current_time(),
                creation_time: get_current_time() - (pid as u64 * 10000),
            };

            // Check for process-specific alerts
            self.check_process_alerts(&metrics);

            metrics_map.insert(pid, metrics);
        }
    }

    /// Check for system-level alerts
    fn check_system_alerts(&self, metrics: &SystemMetrics) {
        let thresholds = self.alert_thresholds.read();

        // Check CPU usage
        if let Some(&threshold) = thresholds.get(&AlertType::HighCPUUsage) {
            if metrics.cpu_utilization > threshold {
                self.create_alert(
                    AlertType::HighCPUUsage,
                    AlertSeverity::Warning,
                    None,
                    format!("System CPU usage is {}%", metrics.cpu_utilization),
                    format!("CPU usage exceeded threshold of {}%", threshold),
                );
            }
        }

        // Check memory usage
        if let Some(&threshold) = thresholds.get(&AlertType::HighMemoryUsage) {
            if metrics.memory_utilization > threshold {
                self.create_alert(
                    AlertType::HighMemoryUsage,
                    AlertSeverity::Error,
                    None,
                    format!("System memory usage is {}%", metrics.memory_utilization),
                    format!("Memory usage exceeded threshold of {}%", threshold),
                );
            }
        }

        // Check consciousness anomalies
        if let Some(&threshold) = thresholds.get(&AlertType::ConsciousnessAnomaly) {
            if metrics.consciousness_score < threshold {
                self.create_alert(
                    AlertType::ConsciousnessAnomaly,
                    AlertSeverity::Warning,
                    None,
                    format!("Low consciousness score: {:.2}", metrics.consciousness_score),
                    "System consciousness is operating below optimal levels".to_string(),
                );
            }
        }
    }

    /// Check for process-specific alerts
    fn check_process_alerts(&self, metrics: &ProcessMetrics) {
        let thresholds = self.alert_thresholds.read();

        // Check process CPU usage
        if let Some(&threshold) = thresholds.get(&AlertType::HighCPUUsage) {
            if metrics.cpu_usage > threshold {
                self.create_alert(
                    AlertType::HighCPUUsage,
                    AlertSeverity::Warning,
                    Some(metrics.pid),
                    format!("Process {} CPU usage is {}%", metrics.pid, metrics.cpu_usage),
                    format!("Process {} ({}) exceeded CPU threshold", metrics.pid, metrics.name),
                );
            }
        }

        // Check for hanging processes
        if let Some(&threshold) = thresholds.get(&AlertType::ProcessHanging) {
            let idle_time = get_current_time() - metrics.last_activity;
            if idle_time > threshold as u64 && metrics.state == ProcessState::Running {
                self.create_alert(
                    AlertType::ProcessHanging,
                    AlertSeverity::Error,
                    Some(metrics.pid),
                    format!("Process {} appears to be hanging", metrics.pid),
                    format!("Process has been inactive for {} ms", idle_time),
                );
            }
        }
    }

    /// Create a new monitoring alert
    fn create_alert(&self, alert_type: AlertType, severity: AlertSeverity, pid: Option<ProcessId>, message: String, details: String) {
        let alert_id = self.next_alert_id.fetch_add(1, Ordering::SeqCst);

        let alert = MonitoringAlert {
            alert_id,
            alert_type,
            severity,
            pid,
            message,
            details,
            timestamp: get_current_time(),
            acknowledged: false,
            auto_resolved: false,
        };

        let mut alerts = self.alerts.lock();
        alerts.push(alert);

        // Maintain alert history (keep last 1000 alerts)
        if alerts.len() > 1000 {
            alerts.remove(0);
        }
    }

    /// Update time series data
    fn update_time_series(&self, series_name: &str, value: f32) {
        let mut time_series = self.time_series.write();
        if let Some(series) = time_series.get_mut(series_name) {
            series.add_point(value, None);
        }
    }

    /// Get current system metrics
    pub fn get_system_metrics(&self) -> SystemMetrics {
        self.system_metrics.read().clone()
    }

    /// Get current process metrics
    pub fn get_process_metrics(&self) -> Vec<ProcessMetrics> {
        self.process_metrics.read().values().cloned().collect()
    }

    /// Get process metrics for a specific process
    pub fn get_process_metrics_by_pid(&self, pid: ProcessId) -> Option<ProcessMetrics> {
        self.process_metrics.read().get(&pid).cloned()
    }

    /// Get active alerts
    pub fn get_active_alerts(&self) -> Vec<MonitoringAlert> {
        self.alerts.lock().iter()
            .filter(|alert| !alert.acknowledged && !alert.auto_resolved)
            .cloned()
            .collect()
    }

    /// Get all alerts
    pub fn get_all_alerts(&self) -> Vec<MonitoringAlert> {
        self.alerts.lock().clone()
    }

    /// Acknowledge an alert
    pub fn acknowledge_alert(&self, alert_id: u32) -> Result<(), ProcessError> {
        let mut alerts = self.alerts.lock();
        if let Some(alert) = alerts.iter_mut().find(|a| a.alert_id == alert_id) {
            alert.acknowledged = true;
            Ok(())
        } else {
            Err(ProcessError::ProcessNotFound)
        }
    }

    /// Get time series data
    pub fn get_time_series(&self, series_name: &str) -> Option<TimeSeries> {
        self.time_series.read().get(series_name).cloned()
    }

    /// Generate dashboard report
    pub fn generate_dashboard_report(&self) -> String {
        let metrics = self.get_system_metrics();
        let process_metrics = self.get_process_metrics();
        let active_alerts = self.get_active_alerts();

        let mut report = String::new();

        report.push_str("=== SYSOS MONITORING DASHBOARD ===\n");
        report.push_str(&format!("Timestamp: {}\n", metrics.timestamp));
        report.push_str(&format!("Update Interval: {}ms\n\n", self.update_interval));

        report.push_str("=== SYSTEM OVERVIEW ===\n");
        report.push_str(&format!("Total Processes: {}\n", metrics.total_processes));
        report.push_str(&format!("Running: {} | Blocked: {} | Zombie: {}\n",
            metrics.running_processes, metrics.blocked_processes, metrics.zombie_processes));
        report.push_str(&format!("CPU Usage: {:.2}%\n", metrics.cpu_utilization));
        report.push_str(&format!("Memory Usage: {:.2}%\n", metrics.memory_utilization));
        report.push_str(&format!("Load Average: {:.2} {:.2} {:.2}\n",
            metrics.load_average_1m, metrics.load_average_5m, metrics.load_average_15m));
        report.push_str(&format!("Consciousness Score: {:.2}\n", metrics.consciousness_score));

        report.push_str("\n=== TOP PROCESSES ===\n");
        let mut sorted_processes = process_metrics;
        sorted_processes.sort_by(|a, b| b.cpu_usage.partial_cmp(&a.cpu_usage).unwrap());

        for process in sorted_processes.iter().take(10) {
            report.push_str(&format!("PID {} ({}): CPU {:.1}% | MEM {:.1}% | State {:?}\n",
                process.pid, process.name, process.cpu_usage, process.memory_percentage, process.state));
        }

        report.push_str("\n=== ACTIVE ALERTS ===\n");
        if active_alerts.is_empty() {
            report.push_str("No active alerts.\n");
        } else {
            for alert in &active_alerts {
                report.push_str(&format!("[{:?}] {}: {}\n",
                    alert.severity, alert.message, alert.details));
            }
        }

        report
    }

    /// Helper methods for metric calculations
    fn count_total_processes(&self) -> u32 {
        self.process_metrics.read().len() as u32
    }

    fn count_running_processes(&self) -> u32 {
        self.process_metrics.read().values()
            .filter(|p| p.state == ProcessState::Running)
            .count() as u32
    }

    fn count_blocked_processes(&self) -> u32 {
        self.process_metrics.read().values()
            .filter(|p| p.state == ProcessState::Blocked)
            .count() as u32
    }

    fn count_zombie_processes(&self) -> u32 {
        self.process_metrics.read().values()
            .filter(|p| p.state == ProcessState::Terminated)
            .count() as u32
    }

    fn calculate_system_cpu_usage(&self) -> f32 {
        let process_metrics = self.process_metrics.read();
        if process_metrics.is_empty() {
            return 0.0;
        }

        let total_cpu: f32 = process_metrics.values().map(|p| p.cpu_usage).sum();
        total_cpu / process_metrics.len() as f32
    }

    fn calculate_system_memory_usage(&self) -> f32 {
        let process_metrics = self.process_metrics.read();
        process_metrics.values().map(|p| p.memory_percentage).sum()
    }

    fn calculate_load_average(&self, _duration_ms: u64) -> f32 {
        // Simplified load average calculation
        self.process_metrics.read().len() as f32 / 4.0 // Assuming 4 cores
    }

    fn calculate_context_switches_rate(&self) -> f32 {
        // Placeholder - would calculate actual context switch rate
        100.0
    }

    fn calculate_interrupt_rate(&self) -> f32 {
        // Placeholder - would calculate actual interrupt rate
        500.0
    }
}

impl Default for SystemMetrics {
    fn default() -> Self {
        Self {
            total_processes: 0,
            running_processes: 0,
            blocked_processes: 0,
            zombie_processes: 0,
            cpu_utilization: 0.0,
            memory_utilization: 0.0,
            load_average_1m: 0.0,
            load_average_5m: 0.0,
            load_average_15m: 0.0,
            context_switches_per_sec: 0.0,
            interrupts_per_sec: 0.0,
            consciousness_score: 50.0,
            timestamp: 0,
        }
    }
}

/// Global monitoring dashboard instance
pub static MONITORING_DASHBOARD: RwLock<Option<ProcessMonitoringDashboard>> = RwLock::new(None);

/// Initialize the monitoring dashboard
pub fn init_monitoring_dashboard() -> Result<(), ProcessError> {
    let dashboard = ProcessMonitoringDashboard::new();
    *MONITORING_DASHBOARD.write() = Some(dashboard);
    Ok(())
}

/// Update monitoring data
pub fn update_monitoring_data() -> Result<(), ProcessError> {
    if let Some(dashboard) = MONITORING_DASHBOARD.read().as_ref() {
        dashboard.update_system_metrics();
        dashboard.update_process_metrics();
        Ok(())
    } else {
        Err(ProcessError::ProcessNotFound)
    }
}

/// Get dashboard report
pub fn get_monitoring_report() -> Result<String, ProcessError> {
    if let Some(dashboard) = MONITORING_DASHBOARD.read().as_ref() {
        Ok(dashboard.generate_dashboard_report())
    } else {
        Err(ProcessError::ProcessNotFound)
    }
}

/// Helper function
fn get_current_time() -> u64 {
    static COUNTER: AtomicU64 = AtomicU64::new(0);
    COUNTER.fetch_add(1, Ordering::SeqCst)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dashboard_creation() {
        let dashboard = ProcessMonitoringDashboard::new();
        assert!(dashboard.monitoring_enabled.load(Ordering::Relaxed) == 1);
    }

    #[test]
    fn test_time_series() {
        let mut series = TimeSeries::new("test".to_string(), 10, 1000);
        series.add_point(5.0, None);
        series.add_point(10.0, None);

        assert_eq!(series.data_points.len(), 2);
        assert_eq!(series.get_latest().unwrap().value, 10.0);
    }

    #[test]
    fn test_alert_creation() {
        let dashboard = ProcessMonitoringDashboard::new();
        dashboard.create_alert(
            AlertType::HighCPUUsage,
            AlertSeverity::Warning,
            Some(123),
            "Test alert".to_string(),
            "Test details".to_string(),
        );

        let alerts = dashboard.get_active_alerts();
        assert_eq!(alerts.len(), 1);
        assert_eq!(alerts[0].alert_type, AlertType::HighCPUUsage);
    }
}