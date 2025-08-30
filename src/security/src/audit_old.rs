use alloc::collections::BTreeMap;
use alloc::string::{String, ToString};
use alloc::vec::Vec;
use alloc::format;
use spin::Mutex;
use core::fmt;

/// Audit log levels
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AuditLevel {
    Info,
    Warning,
    Error,
    Critical,
}

impl fmt::Display for AuditLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AuditLevel::Info => write!(f, "INFO"),
            AuditLevel::Warning => write!(f, "WARN"),
            AuditLevel::Error => write!(f, "ERROR"),
            AuditLevel::Critical => write!(f, "CRITICAL"),
        }
    }
}

/// Audit log entry
#[derive(Debug, Clone)]
pub struct AuditEntry {
    pub timestamp: u64,
    pub level: AuditLevel,
    pub component: String,
    pub user_id: Option<u32>,
    pub session_id: Option<String>,
    pub action: String,
    pub resource: String,
    pub result: String,
    pub details: BTreeMap<String, String>,
}

/// Audit logger - kernel memory based for now
pub struct AuditLogger {
    log_path: String,
    // In real kernel, this would be a ring buffer or kernel log system
}

impl AuditLogger {
    /// Create new audit logger
    pub fn new(log_path: &str) -> Result<Self, std::io::Error> {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(log_path)?;
        
        let log_file = Arc::new(Mutex::new(BufWriter::new(file)));
        
        Ok(Self {
            log_file,
            log_path: log_path.to_string(),
            buffer_size: 4096,
        })
    }
    
    /// Log audit entry
    pub fn log(&self, entry: AuditEntry) -> Result<(), std::io::Error> {
        let log_line = self.format_entry(&entry);
        
        let mut writer = self.log_file.lock().unwrap();
        writeln!(writer, "{}", log_line)?;
        writer.flush()?;
        
        Ok(())
    }
    
    /// Format audit entry as JSON for structured logging
    fn format_entry(&self, entry: &AuditEntry) -> String {
        let mut json_parts = vec![
            format!(r#""timestamp":{}"#, entry.timestamp),
            format!(r#""level":"{}""#, entry.level),
            format!(r#""component":"{}""#, self.escape_json(&entry.component)),
            format!(r#""action":"{}""#, self.escape_json(&entry.action)),
            format!(r#""resource":"{}""#, self.escape_json(&entry.resource)),
            format!(r#""result":"{}""#, self.escape_json(&entry.result)),
        ];
        
        if let Some(user_id) = entry.user_id {
            json_parts.push(format!(r#""user_id":{}"#, user_id));
        }
        
        if let Some(session_id) = &entry.session_id {
            json_parts.push(format!(r#""session_id":"{}""#, self.escape_json(session_id)));
        }
        
        if !entry.details.is_empty() {
            let details: Vec<String> = entry.details.iter()
                .map(|(k, v)| format!(r#""{}":"{}""#, self.escape_json(k), self.escape_json(v)))
                .collect();
            json_parts.push(format!(r#""details":{{{}}}"#, details.join(",")));
        }
        
        format!("{{{}}}", json_parts.join(","))
    }
    
    /// Escape JSON strings to prevent injection
    fn escape_json(&self, s: &str) -> String {
        s.chars()
            .map(|c| match c {
                '"' => r#"\""#.to_string(),
                '\\' => r#"\\"#.to_string(),
                '\n' => r#"\n"#.to_string(),
                '\r' => r#"\r"#.to_string(),
                '\t' => r#"\t"#.to_string(),
                c if c.is_control() => format!(r#"\u{:04x}"#, c as u32),
                c => c.to_string(),
            })
            .collect()
    }
    
    /// Log authentication event
    pub fn log_authentication(&self, user_id: Option<u32>, username: &str, success: bool, source_ip: &str) {
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: if success { AuditLevel::Info } else { AuditLevel::Warning },
            component: "authentication".to_string(),
            user_id,
            session_id: None,
            action: "login".to_string(),
            resource: "auth_system".to_string(),
            result: if success { "success" } else { "failure" }.to_string(),
            details: {
                let mut details = HashMap::new();
                details.insert("username".to_string(), username.to_string());
                details.insert("source_ip".to_string(), source_ip.to_string());
                details
            },
        };
        
        let _ = self.log(entry);
    }
    
    /// Log authorization event
    pub fn log_authorization(&self, user_id: u32, session_id: &str, resource: &str, action: &str, allowed: bool) {
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: if allowed { AuditLevel::Info } else { AuditLevel::Warning },
            component: "authorization".to_string(),
            user_id: Some(user_id),
            session_id: Some(session_id.to_string()),
            action: action.to_string(),
            resource: resource.to_string(),
            result: if allowed { "granted" } else { "denied" }.to_string(),
            details: HashMap::new(),
        };
        
        let _ = self.log(entry);
    }
    
    /// Log data access event
    pub fn log_data_access(&self, user_id: u32, session_id: &str, data_type: &str, operation: &str, result: &str) {
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: AuditLevel::Info,
            component: "data_access".to_string(),
            user_id: Some(user_id),
            session_id: Some(session_id.to_string()),
            action: operation.to_string(),
            resource: data_type.to_string(),
            result: result.to_string(),
            details: HashMap::new(),
        };
        
        let _ = self.log(entry);
    }
    
    /// Log security incident
    pub fn log_security_incident(&self, incident_type: &str, severity: AuditLevel, details: &str) {
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: severity,
            component: "security".to_string(),
            user_id: None,
            session_id: None,
            action: "incident".to_string(),
            resource: incident_type.to_string(),
            result: "detected".to_string(),
            details: {
                let mut map = HashMap::new();
                map.insert("details".to_string(), details.to_string());
                map
            },
        };
        
        let _ = self.log(entry);
    }
    
    /// Log system event
    pub fn log_system_event(&self, component: &str, action: &str, result: &str, details: HashMap<String, String>) {
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: AuditLevel::Info,
            component: component.to_string(),
            user_id: None,
            session_id: None,
            action: action.to_string(),
            resource: "system".to_string(),
            result: result.to_string(),
            details,
        };
        
        let _ = self.log(entry);
    }
    
    /// Rotate log files to prevent them from growing too large
    pub fn rotate_logs(&self, max_size_bytes: u64) -> Result<(), std::io::Error> {
        let metadata = std::fs::metadata(&self.log_path)?;
        
        if metadata.len() > max_size_bytes {
            let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
            let backup_path = format!("{}.{}", self.log_path, timestamp);
            
            // Move current log to backup
            std::fs::rename(&self.log_path, backup_path)?;
            
            // Create new log file
            let file = OpenOptions::new()
                .create(true)
                .append(true)
                .open(&self.log_path)?;
            
            let mut writer = self.log_file.lock().unwrap();
            *writer = BufWriter::new(file);
        }
        
        Ok(())
    }
}

/// Audit trail for tracking changes
pub struct AuditTrail {
    logger: AuditLogger,
    enabled: bool,
}

impl AuditTrail {
    /// Create new audit trail
    pub fn new(log_path: &str) -> Result<Self, std::io::Error> {
        let logger = AuditLogger::new(log_path)?;
        Ok(Self {
            logger,
            enabled: true,
        })
    }
    
    /// Enable/disable audit logging
    pub fn set_enabled(&mut self, enabled: bool) {
        self.enabled = enabled;
    }
    
    /// Log a change event
    pub fn log_change(&self, user_id: u32, resource: &str, old_value: &str, new_value: &str) {
        if !self.enabled {
            return;
        }
        
        let mut details = HashMap::new();
        details.insert("old_value".to_string(), old_value.to_string());
        details.insert("new_value".to_string(), new_value.to_string());
        
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: AuditLevel::Info,
            component: "data_change".to_string(),
            user_id: Some(user_id),
            session_id: None,
            action: "modify".to_string(),
            resource: resource.to_string(),
            result: "success".to_string(),
            details,
        };
        
        let _ = self.logger.log(entry);
    }
    
    /// Log a deletion event
    pub fn log_deletion(&self, user_id: u32, resource: &str, identifier: &str) {
        if !self.enabled {
            return;
        }
        
        let mut details = HashMap::new();
        details.insert("identifier".to_string(), identifier.to_string());
        
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: AuditLevel::Warning,
            component: "data_deletion".to_string(),
            user_id: Some(user_id),
            session_id: None,
            action: "delete".to_string(),
            resource: resource.to_string(),
            result: "success".to_string(),
            details,
        };
        
        let _ = self.logger.log(entry);
    }
}

/// Global audit logger instance
static mut GLOBAL_AUDIT_LOGGER: Option<AuditLogger> = None;
static AUDIT_INIT: std::sync::Once = std::sync::Once::new();

/// Get global audit logger
pub fn get_audit_logger() -> Option<&'static AuditLogger> {
    unsafe {
        AUDIT_INIT.call_once(|| {
            if let Ok(logger) = AuditLogger::new("security_audit.log") {
                GLOBAL_AUDIT_LOGGER = Some(logger);
            }
        });
        GLOBAL_AUDIT_LOGGER.as_ref()
    }
}

/// Convenience function to log authentication
pub fn log_authentication(user_id: Option<u32>, username: &str, success: bool, source_ip: &str) {
    if let Some(logger) = get_audit_logger() {
        logger.log_authentication(user_id, username, success, source_ip);
    }
}

/// Convenience function to log authorization
pub fn log_authorization(user_id: u32, session_id: &str, resource: &str, action: &str, allowed: bool) {
    if let Some(logger) = get_audit_logger() {
        logger.log_authorization(user_id, session_id, resource, action, allowed);
    }
}

/// Convenience function to log security incident
pub fn log_security_incident(incident_type: &str, severity: AuditLevel, details: &str) {
    if let Some(logger) = get_audit_logger() {
        logger.log_security_incident(incident_type, severity, details);
    }
}

/// Initialize audit module
pub fn init() {
    let _ = get_audit_logger(); // Initialize global logger
    println!("📋 Audit logging module initialized");
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    
    #[test]
    fn test_audit_logger_creation() {
        let temp_path = "test_audit.log";
        let logger = AuditLogger::new(temp_path);
        assert!(logger.is_ok());
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
    
    #[test]
    fn test_json_escaping() {
        let temp_path = "test_escape.log";
        let logger = AuditLogger::new(temp_path).unwrap();
        
        let test_string = r#"test"with"quotes\and\backslashes"#;
        let escaped = logger.escape_json(test_string);
        assert!(!escaped.contains('"') || escaped.contains(r#"\""#));
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
    
    #[test]
    fn test_audit_entry_logging() {
        let temp_path = "test_entry.log";
        let logger = AuditLogger::new(temp_path).unwrap();
        
        let entry = AuditEntry {
            timestamp: 1640995200, // Fixed timestamp for testing
            level: AuditLevel::Info,
            component: "test".to_string(),
            user_id: Some(123),
            session_id: Some("session123".to_string()),
            action: "test_action".to_string(),
            resource: "test_resource".to_string(),
            result: "success".to_string(),
            details: HashMap::new(),
        };
        
        let result = logger.log(entry);
        assert!(result.is_ok());
        
        // Verify file was written
        let contents = fs::read_to_string(temp_path).unwrap();
        assert!(contents.contains("test_action"));
        assert!(contents.contains("user_id"));
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
    
    #[test]
    fn test_audit_trail() {
        let temp_path = "test_trail.log";
        let trail = AuditTrail::new(temp_path).unwrap();
        
        trail.log_change(123, "user_settings", "old_value", "new_value");
        trail.log_deletion(123, "user_data", "record_456");
        
        // Verify file exists and has content
        let contents = fs::read_to_string(temp_path).unwrap();
        assert!(contents.contains("modify"));
        assert!(contents.contains("delete"));
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
}