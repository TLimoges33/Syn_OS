use alloc::collections::{BTreeMap, VecDeque};
use spin::{RwLock, Mutex};
use core::sync::atomic::{AtomicU64, Ordering};
use alloc::string::{String, ToString};
use alloc::vec::Vec;
use alloc::format;

/// Security monitoring events
#[derive(Debug, Clone)]
pub enum SecurityEvent {
    AuthenticationAttempt {
        username: String,
        success: bool,
        source_ip: String,
        timestamp: u64,
    },
    AuthorizationFailure {
        user_id: u32,
        resource: String,
        action: String,
        timestamp: u64,
    },
    SuspiciousActivity {
        event_type: String,
        details: String,
        severity: ThreatLevel,
        timestamp: u64,
    },
    SystemAccess {
        user_id: u32,
        resource: String,
        access_type: String,
        timestamp: u64,
    },
    DataAccess {
        user_id: u32,
        data_type: String,
        operation: String,
        timestamp: u64,
    },
}

/// Threat severity levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum ThreatLevel {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
}

/// Security monitoring service - real-time threat detection
pub struct SecurityMonitor {
    events: Arc<RwLock<VecDeque<SecurityEvent>>>,
    threat_counters: Arc<RwLock<HashMap<String, AtomicU64>>>,
    failed_login_attempts: Arc<RwLock<HashMap<String, (u32, u64)>>>, // IP -> (count, last_attempt)
    active_sessions: Arc<RwLock<HashMap<u32, SessionInfo>>>, // user_id -> session_info
    max_events: usize,
}

#[derive(Debug, Clone)]
struct SessionInfo {
    login_time: u64,
    last_activity: u64,
    source_ip: String,
    session_id: String,
}

impl SecurityMonitor {
    /// Create new security monitor
    pub fn new() -> Self {
        Self {
            events: Arc::new(RwLock::new(VecDeque::new())),
            threat_counters: Arc::new(RwLock::new(HashMap::new())),
            failed_login_attempts: Arc::new(RwLock::new(HashMap::new())),
            active_sessions: Arc::new(RwLock::new(HashMap::new())),
            max_events: 10000, // Keep last 10k events
        }
    }
    
    /// Record security event
    pub fn record_event(&self, event: SecurityEvent) {
        let mut events = self.events.write().unwrap();
        
        // Maintain event buffer size
        if events.len() >= self.max_events {
            events.pop_front();
        }
        
        // Analyze event for threats
        self.analyze_event(&event);
        
        events.push_back(event);
    }
    
    /// Analyze event for potential threats
    fn analyze_event(&self, event: &SecurityEvent) {
        match event {
            SecurityEvent::AuthenticationAttempt { username, success, source_ip, timestamp } => {
                if !success {
                    self.track_failed_login(source_ip, *timestamp);
                    
                    // Check for brute force attack
                    if self.is_brute_force_attack(source_ip) {
                        self.record_event(SecurityEvent::SuspiciousActivity {
                            event_type: "brute_force_attack".to_string(),
                            details: format!("Multiple failed login attempts from IP: {}", source_ip),
                            severity: ThreatLevel::High,
                            timestamp: *timestamp,
                        });
                    }
                } else {
                    // Successful login - clear failed attempts
                    let mut failed_logins = self.failed_login_attempts.write().unwrap();
                    failed_logins.remove(source_ip);
                }
            },
            
            SecurityEvent::AuthorizationFailure { user_id, resource, action, timestamp } => {
                // Track authorization failures
                let counter_key = format!("authz_failure_user_{}", user_id);
                self.increment_threat_counter(&counter_key);
                
                // Check for privilege escalation attempts
                if action.contains("admin") || action.contains("root") || action.contains("sudo") {
                    self.record_event(SecurityEvent::SuspiciousActivity {
                        event_type: "privilege_escalation_attempt".to_string(),
                        details: format!("User {} attempted {} on {}", user_id, action, resource),
                        severity: ThreatLevel::High,
                        timestamp: *timestamp,
                    });
                }
            },
            
            SecurityEvent::DataAccess { user_id, data_type, operation, timestamp } => {
                // Monitor sensitive data access
                if data_type.contains("sensitive") || data_type.contains("classified") {
                    let counter_key = format!("sensitive_access_user_{}", user_id);
                    self.increment_threat_counter(&counter_key);
                    
                    // Alert on bulk data operations
                    if operation == "bulk_export" || operation == "mass_download" {
                        self.record_event(SecurityEvent::SuspiciousActivity {
                            event_type: "data_exfiltration_attempt".to_string(),
                            details: format!("User {} performing {} on {}", user_id, operation, data_type),
                            severity: ThreatLevel::Critical,
                            timestamp: *timestamp,
                        });
                    }
                }
            },
            
            _ => {} // Other events don't need special analysis
        }
    }
    
    /// Track failed login attempts per IP
    fn track_failed_login(&self, source_ip: &str, timestamp: u64) {
        let mut failed_logins = self.failed_login_attempts.write().unwrap();
        let entry = failed_logins.entry(source_ip.to_string()).or_insert((0, 0));
        
        // Reset counter if last attempt was more than 1 hour ago
        if timestamp - entry.1 > 3600 {
            entry.0 = 1;
        } else {
            entry.0 += 1;
        }
        entry.1 = timestamp;
    }
    
    /// Check if IP is performing brute force attack
    fn is_brute_force_attack(&self, source_ip: &str) -> bool {
        let failed_logins = self.failed_login_attempts.read().unwrap();
        if let Some((count, last_attempt)) = failed_logins.get(source_ip) {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
            // More than 5 failed attempts in the last hour
            *count > 5 && (now - last_attempt) < 3600
        } else {
            false
        }
    }
    
    /// Increment threat counter
    fn increment_threat_counter(&self, counter_key: &str) {
        let mut counters = self.threat_counters.write().unwrap();
        let counter = counters.entry(counter_key.to_string())
            .or_insert_with(|| AtomicU64::new(0));
        counter.fetch_add(1, Ordering::SeqCst);
    }
    
    /// Get threat level for user
    pub fn get_threat_level(&self, user_id: u32) -> ThreatLevel {
        let counters = self.threat_counters.read().unwrap();
        
        let mut total_threats = 0u64;
        
        // Check various threat indicators
        if let Some(authz_failures) = counters.get(&format!("authz_failure_user_{}", user_id)) {
            total_threats += authz_failures.load(Ordering::SeqCst);
        }
        
        if let Some(sensitive_access) = counters.get(&format!("sensitive_access_user_{}", user_id)) {
            total_threats += sensitive_access.load(Ordering::SeqCst) * 2; // Weight sensitive access higher
        }
        
        // Classify threat level
        match total_threats {
            0..=2 => ThreatLevel::Low,
            3..=5 => ThreatLevel::Medium,
            6..=10 => ThreatLevel::High,
            _ => ThreatLevel::Critical,
        }
    }
    
    /// Get recent events by type
    pub fn get_events_by_type(&self, event_type: &str, limit: usize) -> Vec<SecurityEvent> {
        let events = self.events.read().unwrap();
        events.iter()
            .filter(|event| {
                match event {
                    SecurityEvent::SuspiciousActivity { event_type: et, .. } => et == event_type,
                    SecurityEvent::AuthenticationAttempt { .. } => event_type == "authentication",
                    SecurityEvent::AuthorizationFailure { .. } => event_type == "authorization",
                    SecurityEvent::SystemAccess { .. } => event_type == "system_access",
                    SecurityEvent::DataAccess { .. } => event_type == "data_access",
                }
            })
            .take(limit)
            .cloned()
            .collect()
    }
    
    /// Get events by severity
    pub fn get_events_by_severity(&self, min_severity: ThreatLevel, limit: usize) -> Vec<SecurityEvent> {
        let events = self.events.read().unwrap();
        events.iter()
            .filter(|event| {
                match event {
                    SecurityEvent::SuspiciousActivity { severity, .. } => *severity >= min_severity,
                    _ => false, // Only suspicious activities have severity
                }
            })
            .take(limit)
            .cloned()
            .collect()
    }
    
    /// Get active sessions count
    pub fn get_active_sessions_count(&self) -> usize {
        let sessions = self.active_sessions.read().unwrap();
        sessions.len()
    }
    
    /// Register user session
    pub fn register_session(&self, user_id: u32, session_id: String, source_ip: String) {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let session_info = SessionInfo {
            login_time: now,
            last_activity: now,
            source_ip,
            session_id,
        };
        
        let mut sessions = self.active_sessions.write().unwrap();
        sessions.insert(user_id, session_info);
    }
    
    /// Update session activity
    pub fn update_session_activity(&self, user_id: u32) {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let mut sessions = self.active_sessions.write().unwrap();
        
        if let Some(session) = sessions.get_mut(&user_id) {
            session.last_activity = now;
        }
    }
    
    /// Remove expired sessions
    pub fn cleanup_expired_sessions(&self, session_timeout_seconds: u64) {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let mut sessions = self.active_sessions.write().unwrap();
        
        sessions.retain(|_, session| {
            now - session.last_activity < session_timeout_seconds
        });
    }
    
    /// Generate security report
    pub fn generate_report(&self) -> SecurityReport {
        let events = self.events.read().unwrap();
        let counters = self.threat_counters.read().unwrap();
        let sessions = self.active_sessions.read().unwrap();
        
        let total_events = events.len();
        let mut events_by_type = HashMap::new();
        let mut high_severity_events = 0;
        
        for event in events.iter() {
            let event_type = match event {
                SecurityEvent::AuthenticationAttempt { .. } => "authentication",
                SecurityEvent::AuthorizationFailure { .. } => "authorization_failure",
                SecurityEvent::SuspiciousActivity { severity, .. } => {
                    if *severity >= ThreatLevel::High {
                        high_severity_events += 1;
                    }
                    "suspicious_activity"
                },
                SecurityEvent::SystemAccess { .. } => "system_access",
                SecurityEvent::DataAccess { .. } => "data_access",
            };
            
            *events_by_type.entry(event_type.to_string()).or_insert(0) += 1;
        }
        
        SecurityReport {
            total_events,
            events_by_type,
            high_severity_events,
            active_sessions: sessions.len(),
            threat_counters: counters.iter()
                .map(|(k, v)| (k.clone(), v.load(Ordering::SeqCst)))
                .collect(),
        }
    }
}

/// Security monitoring report
#[derive(Debug)]
pub struct SecurityReport {
    pub total_events: usize,
    pub events_by_type: HashMap<String, usize>,
    pub high_severity_events: usize,
    pub active_sessions: usize,
    pub threat_counters: HashMap<String, u64>,
}

/// Global security monitor instance
static mut GLOBAL_MONITOR: Option<SecurityMonitor> = None;
static MONITOR_INIT: std::sync::Once = std::sync::Once::new();

/// Get global security monitor
pub fn get_security_monitor() -> &'static SecurityMonitor {
    unsafe {
        MONITOR_INIT.call_once(|| {
            GLOBAL_MONITOR = Some(SecurityMonitor::new());
        });
        GLOBAL_MONITOR.as_ref().unwrap()
    }
}

/// Convenience function to record security event
pub fn record_security_event(event: SecurityEvent) {
    get_security_monitor().record_event(event);
}

/// Initialize monitoring module
pub fn init() {
    let _ = get_security_monitor(); // Initialize global monitor
    println!("📊 Security monitoring module initialized");
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_security_monitor_creation() {
        let monitor = SecurityMonitor::new();
        assert_eq!(monitor.get_active_sessions_count(), 0);
    }
    
    #[test]
    fn test_failed_login_tracking() {
        let monitor = SecurityMonitor::new();
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        
        // Record multiple failed attempts
        for i in 0..6 {
            monitor.record_event(SecurityEvent::AuthenticationAttempt {
                username: "testuser".to_string(),
                success: false,
                source_ip: "192.168.1.100".to_string(),
                timestamp: timestamp + i,
            });
        }
        
        assert!(monitor.is_brute_force_attack("192.168.1.100"));
    }
    
    #[test]
    fn test_threat_level_calculation() {
        let monitor = SecurityMonitor::new();
        let user_id = 123;
        
        // Initially low threat
        assert_eq!(monitor.get_threat_level(user_id), ThreatLevel::Low);
        
        // Record some authorization failures
        for _ in 0..4 {
            monitor.record_event(SecurityEvent::AuthorizationFailure {
                user_id,
                resource: "admin_panel".to_string(),
                action: "access".to_string(),
                timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            });
        }
        
        // Should be medium threat now
        assert_eq!(monitor.get_threat_level(user_id), ThreatLevel::Medium);
    }
    
    #[test]
    fn test_session_management() {
        let monitor = SecurityMonitor::new();
        
        monitor.register_session(1, "session123".to_string(), "192.168.1.1".to_string());
        assert_eq!(monitor.get_active_sessions_count(), 1);
        
        monitor.update_session_activity(1);
        assert_eq!(monitor.get_active_sessions_count(), 1);
        
        // Test cleanup (sessions older than 0 seconds should be removed)
        monitor.cleanup_expired_sessions(0);
        assert_eq!(monitor.get_active_sessions_count(), 0);
    }
    
    #[test]
    fn test_security_report_generation() {
        let monitor = SecurityMonitor::new();
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        
        monitor.record_event(SecurityEvent::SuspiciousActivity {
            event_type: "test_threat".to_string(),
            details: "Test threat".to_string(),
            severity: ThreatLevel::High,
            timestamp,
        });
        
        let report = monitor.generate_report();
        assert_eq!(report.total_events, 1);
        assert_eq!(report.high_severity_events, 1);
    }
}