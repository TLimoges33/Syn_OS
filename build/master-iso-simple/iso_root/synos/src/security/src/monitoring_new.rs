// Kernel-compatible monitoring module
use alloc::collections::{BTreeMap, VecDeque};
use alloc::string::{String, ToString};
use alloc::vec::Vec;
use alloc::format;
use spin::{RwLock, Mutex};
use core::sync::atomic::{AtomicU64, Ordering};

/// Authentication attempt monitoring
#[derive(Debug, Clone)]
pub struct AuthenticationAttempt {
    pub username: String,
    pub success: bool,
    pub source_ip: String,
    pub timestamp: u64,
}

/// Authorization event monitoring  
#[derive(Debug, Clone)]
pub struct AuthorizationEvent {
    pub user_id: u32,
    pub resource: String,
    pub action: String,
    pub granted: bool,
}

/// Security incident
#[derive(Debug, Clone)]
pub struct SecurityIncident {
    pub incident_id: u64,
    pub event_type: String,
    pub details: String,
    pub severity: u8,
}

/// Sensitive data access tracking
#[derive(Debug, Clone)]
pub struct SensitiveDataAccess {
    pub user_id: u32,
    pub resource: String,
    pub access_type: String,
    pub timestamp: u64,
}

/// Data classification access
#[derive(Debug, Clone)]
pub struct DataClassificationAccess {
    pub user_id: u32,
    pub data_type: String,
    pub operation: String,
    pub classification_level: u8,
}

/// Security monitoring service
pub struct SecurityMonitor {
    events: Mutex<VecDeque<SecurityIncident>>,
    threat_counters: RwLock<BTreeMap<String, AtomicU64>>,
    failed_logins: RwLock<BTreeMap<String, (u32, u64)>>, // IP -> (count, last_attempt)
}

impl SecurityMonitor {
    /// Create new security monitor
    pub fn new() -> Self {
        Self {
            events: Mutex::new(VecDeque::new()),
            threat_counters: RwLock::new(BTreeMap::new()),
            failed_logins: RwLock::new(BTreeMap::new()),
        }
    }
    
    /// Record authentication attempt
    pub fn record_auth_attempt(&self, attempt: AuthenticationAttempt) {
        if !attempt.success {
            self.increment_threat_counter("failed_auth");
            
            // Track failed login attempts by IP
            let mut failed_logins = self.failed_logins.write();
            let entry = failed_logins.entry(attempt.source_ip.clone())
                .or_insert((0, 0));
            entry.0 += 1;
            entry.1 = attempt.timestamp;
            
            // Generate incident if too many failures
            if entry.0 > 5 {
                self.record_incident(SecurityIncident {
                    incident_id: self.get_next_incident_id(),
                    event_type: "brute_force_attack".to_string(),
                    details: format!("Multiple failed login attempts from {}", attempt.source_ip),
                    severity: 7,
                });
            }
        }
    }
    
    /// Record authorization event
    pub fn record_authz_event(&self, event: AuthorizationEvent) {
        if !event.granted {
            let counter_key = format!("authz_failure_user_{}", event.user_id);
            self.increment_threat_counter(&counter_key);
            
            self.record_incident(SecurityIncident {
                incident_id: self.get_next_incident_id(),
                event_type: "authorization_failure".to_string(),
                details: format!("User {} attempted {} on {}", event.user_id, event.action, event.resource),
                severity: 4,
            });
        }
    }
    
    /// Record sensitive data access
    pub fn record_sensitive_access(&self, access: SensitiveDataAccess) {
        let counter_key = format!("sensitive_access_user_{}", access.user_id);
        self.increment_threat_counter(&counter_key);
        
        self.record_incident(SecurityIncident {
            incident_id: self.get_next_incident_id(),
            event_type: "sensitive_data_access".to_string(),
            details: format!("User {} performing {} on {}", access.user_id, access.access_type, access.resource),
            severity: 3,
        });
    }
    
    /// Get security statistics
    pub fn get_security_stats(&self) -> SecurityStats {
        let counters = self.threat_counters.read();
        let events = self.events.lock();
        
        let mut events_by_type = BTreeMap::new();
        for event in events.iter() {
            *events_by_type.entry(event.event_type.clone()).or_insert(0) += 1;
        }
        
        let mut threat_counters_map = BTreeMap::new();
        for (key, counter) in counters.iter() {
            threat_counters_map.insert(key.clone(), counter.load(Ordering::Relaxed));
        }
        
        SecurityStats {
            total_events: events.len(),
            events_by_type,
            threat_counters: threat_counters_map,
        }
    }
    
    /// Get recent high-severity incidents
    pub fn get_high_severity_incidents(&self, limit: usize) -> Vec<SecurityIncident> {
        let events = self.events.lock();
        events.iter()
            .filter(|incident| incident.severity >= 7)
            .take(limit)
            .cloned()
            .collect()
    }
    
    /// Get recent security events
    pub fn get_recent_events(&self, limit: usize) -> Vec<SecurityIncident> {
        let events = self.events.lock();
        events.iter().take(limit).cloned().collect()
    }
    
    /// Record security incident
    fn record_incident(&self, incident: SecurityIncident) {
        let mut events = self.events.lock();
        events.push_front(incident);
        
        // Keep only last 1000 events in kernel memory
        if events.len() > 1000 {
            events.truncate(1000);
        }
    }
    
    /// Increment threat counter
    fn increment_threat_counter(&self, counter_name: &str) {
        let counters = self.threat_counters.read();
        if let Some(counter) = counters.get(counter_name) {
            counter.fetch_add(1, Ordering::Relaxed);
        } else {
            drop(counters);
            let mut counters = self.threat_counters.write();
            counters.insert(counter_name.to_string(), AtomicU64::new(1));
        }
    }
    
    /// Get next incident ID
    fn get_next_incident_id(&self) -> u64 {
        static INCIDENT_COUNTER: AtomicU64 = AtomicU64::new(1);
        INCIDENT_COUNTER.fetch_add(1, Ordering::Relaxed)
    }
}

/// Security statistics
#[derive(Debug)]
pub struct SecurityStats {
    pub total_events: usize,
    pub events_by_type: BTreeMap<String, usize>,
    pub threat_counters: BTreeMap<String, u64>,
}

/// Global security monitor instance
static SECURITY_MONITOR: Mutex<Option<SecurityMonitor>> = Mutex::new(None);

/// Initialize security monitoring
pub fn init() {
    let monitor = SecurityMonitor::new();
    *SECURITY_MONITOR.lock() = Some(monitor);
}

/// Record authentication attempt globally
pub fn record_authentication_attempt(username: String, success: bool, source_ip: String) {
    let attempt = AuthenticationAttempt {
        username,
        success,
        source_ip,
        timestamp: crate::get_kernel_timestamp(),
    };
    
    if let Some(monitor) = SECURITY_MONITOR.lock().as_ref() {
        monitor.record_auth_attempt(attempt);
    }
}
