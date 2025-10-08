//! Network Decoy Deployment System
//!
//! Deploy fake network services and honeypots to detect reconnaissance

use crate::{DeceptionAsset, AssetType, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Network decoy types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum DecoyType {
    SSH,
    HTTP,
    FTP,
    SMB,
    RDP,
    Database,
    Custom(String),
}

/// Network decoy configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkDecoy {
    pub name: String,
    pub decoy_type: DecoyType,
    pub listen_ip: String,
    pub listen_port: u16,
    pub banner: Option<String>,
    pub service_version: String,
    pub response_templates: HashMap<String, String>,
}

impl NetworkDecoy {
    pub fn new(
        name: String,
        decoy_type: DecoyType,
        listen_ip: String,
        listen_port: u16,
    ) -> Self {
        let service_version = Self::default_version(&decoy_type);
        let banner = Self::default_banner(&decoy_type, &service_version);

        Self {
            name,
            decoy_type,
            listen_ip,
            listen_port,
            banner: Some(banner),
            service_version,
            response_templates: HashMap::new(),
        }
    }

    fn default_version(decoy_type: &DecoyType) -> String {
        match decoy_type {
            DecoyType::SSH => "OpenSSH_8.9p1".to_string(),
            DecoyType::HTTP => "Apache/2.4.52".to_string(),
            DecoyType::FTP => "vsftpd 3.0.3".to_string(),
            DecoyType::SMB => "Samba 4.15.2".to_string(),
            DecoyType::RDP => "Microsoft Terminal Services".to_string(),
            DecoyType::Database => "PostgreSQL 14.5".to_string(),
            DecoyType::Custom(name) => format!("{} 1.0", name),
        }
    }

    fn default_banner(decoy_type: &DecoyType, version: &str) -> String {
        match decoy_type {
            DecoyType::SSH => format!("SSH-2.0-{}\r\n", version),
            DecoyType::HTTP => format!("HTTP/1.1 200 OK\r\nServer: {}\r\n\r\n", version),
            DecoyType::FTP => format!("220 ({}) [Welcome]\r\n", version),
            DecoyType::SMB => format!("SMB {} Ready\r\n", version),
            DecoyType::RDP => format!("{} Ready\r\n", version),
            DecoyType::Database => format!("FATAL:  password authentication failed\r\n"),
            DecoyType::Custom(name) => format!("{} Service Ready\r\n", name),
        }
    }
}

/// Decoy deployment manager
pub struct DecoyDeploymentManager {
    decoys: HashMap<String, NetworkDecoy>,
    deployment_configs: HashMap<DecoyType, DecoyConfig>,
}

#[derive(Debug, Clone)]
struct DecoyConfig {
    typical_ports: Vec<u16>,
    interaction_responses: HashMap<String, String>,
}

impl DecoyDeploymentManager {
    pub fn new() -> Self {
        let mut configs = HashMap::new();

        // SSH decoy configuration
        configs.insert(
            DecoyType::SSH,
            DecoyConfig {
                typical_ports: vec![22, 2222],
                interaction_responses: [
                    ("login_prompt".to_string(), "login: ".to_string()),
                    ("password_prompt".to_string(), "Password: ".to_string()),
                    ("auth_failure".to_string(), "Permission denied, please try again.\r\n".to_string()),
                ].iter().cloned().collect(),
            },
        );

        // HTTP decoy configuration
        configs.insert(
            DecoyType::HTTP,
            DecoyConfig {
                typical_ports: vec![80, 8080, 443, 8443],
                interaction_responses: [
                    ("index".to_string(), r#"<!DOCTYPE html><html><head><title>Production Server</title></head><body><h1>Server Status: Online</h1></body></html>"#.to_string()),
                    ("admin".to_string(), r#"<!DOCTYPE html><html><head><title>Admin Login</title></head><body><form action="/login" method="post"><input name="user" /><input name="pass" type="password" /><button>Login</button></form></body></html>"#.to_string()),
                ].iter().cloned().collect(),
            },
        );

        // Database decoy configuration
        configs.insert(
            DecoyType::Database,
            DecoyConfig {
                typical_ports: vec![5432, 3306, 27017, 1433],
                interaction_responses: [
                    ("auth_fail".to_string(), "FATAL:  password authentication failed for user \"admin\"\r\n".to_string()),
                    ("connection_ok".to_string(), "OK\r\n".to_string()),
                ].iter().cloned().collect(),
            },
        );

        Self {
            decoys: HashMap::new(),
            deployment_configs: configs,
        }
    }

    /// Deploy SSH honeypot
    pub fn deploy_ssh_decoy(&mut self, ip: &str) -> Result<(NetworkDecoy, DeceptionAsset)> {
        let port = 22;
        let decoy = NetworkDecoy::new(
            format!("ssh_decoy_{}", ip.replace('.', "_")),
            DecoyType::SSH,
            ip.to_string(),
            port,
        );

        let asset = DeceptionAsset::new(
            AssetType::NetworkDecoy,
            format!("ssh_{}:{}", ip, port),
            "Fake SSH server honeypot".to_string(),
            format!("{}:{}", ip, port),
        )
        .with_metadata("service".to_string(), "ssh".to_string())
        .with_metadata("port".to_string(), port.to_string());

        self.decoys.insert(decoy.name.clone(), decoy.clone());
        Ok((decoy, asset))
    }

    /// Deploy HTTP/HTTPS decoy
    pub fn deploy_web_decoy(&mut self, ip: &str, port: u16, ssl: bool) -> Result<(NetworkDecoy, DeceptionAsset)> {
        let decoy = NetworkDecoy::new(
            format!("web_decoy_{}_{}", ip.replace('.', "_"), port),
            DecoyType::HTTP,
            ip.to_string(),
            port,
        );

        let asset = DeceptionAsset::new(
            AssetType::NetworkDecoy,
            format!("web_{}:{}", ip, port),
            format!("Fake {} web server", if ssl { "HTTPS" } else { "HTTP" }),
            format!("{}:{}", ip, port),
        )
        .with_metadata("service".to_string(), "http".to_string())
        .with_metadata("ssl".to_string(), ssl.to_string());

        self.decoys.insert(decoy.name.clone(), decoy.clone());
        Ok((decoy, asset))
    }

    /// Deploy database decoy
    pub fn deploy_database_decoy(&mut self, ip: &str, db_type: &str) -> Result<(NetworkDecoy, DeceptionAsset)> {
        let port = match db_type {
            "postgres" => 5432,
            "mysql" => 3306,
            "mongodb" => 27017,
            "mssql" => 1433,
            _ => 5432,
        };

        let decoy = NetworkDecoy::new(
            format!("{}_decoy_{}", db_type, ip.replace('.', "_")),
            DecoyType::Database,
            ip.to_string(),
            port,
        );

        let asset = DeceptionAsset::new(
            AssetType::NetworkDecoy,
            format!("db_{}:{}", ip, port),
            format!("Fake {} database server", db_type),
            format!("{}:{}", ip, port),
        )
        .with_metadata("db_type".to_string(), db_type.to_string());

        self.decoys.insert(decoy.name.clone(), decoy.clone());
        Ok((decoy, asset))
    }

    /// Deploy SMB file share decoy
    pub fn deploy_smb_decoy(&mut self, ip: &str, share_name: &str) -> Result<(NetworkDecoy, DeceptionAsset)> {
        let port = 445;
        let mut decoy = NetworkDecoy::new(
            format!("smb_decoy_{}_{}", ip.replace('.', "_"), share_name),
            DecoyType::SMB,
            ip.to_string(),
            port,
        );

        decoy.response_templates.insert(
            "share_list".to_string(),
            format!("Available shares: {}$, IPC$, ADMIN$", share_name),
        );

        let asset = DeceptionAsset::new(
            AssetType::NetworkDecoy,
            format!("smb_{}:{}", ip, port),
            format!("Fake SMB file share: {}", share_name),
            format!("\\\\{}\\{}", ip, share_name),
        )
        .with_metadata("share_name".to_string(), share_name.to_string());

        self.decoys.insert(decoy.name.clone(), decoy.clone());
        Ok((decoy, asset))
    }

    /// Deploy RDP decoy
    pub fn deploy_rdp_decoy(&mut self, ip: &str, hostname: &str) -> Result<(NetworkDecoy, DeceptionAsset)> {
        let port = 3389;
        let decoy = NetworkDecoy::new(
            format!("rdp_decoy_{}", ip.replace('.', "_")),
            DecoyType::RDP,
            ip.to_string(),
            port,
        );

        let asset = DeceptionAsset::new(
            AssetType::NetworkDecoy,
            format!("rdp_{}:{}", ip, port),
            format!("Fake RDP server: {}", hostname),
            format!("{}:{}", ip, port),
        )
        .with_metadata("hostname".to_string(), hostname.to_string());

        self.decoys.insert(decoy.name.clone(), decoy.clone());
        Ok((decoy, asset))
    }

    /// Get response for interaction
    pub fn get_interaction_response(&self, decoy_name: &str, interaction_type: &str) -> Option<String> {
        let decoy = self.decoys.get(decoy_name)?;

        if let Some(response) = decoy.response_templates.get(interaction_type) {
            return Some(response.clone());
        }

        if let Some(config) = self.deployment_configs.get(&decoy.decoy_type) {
            return config.interaction_responses.get(interaction_type).cloned();
        }

        None
    }

    /// List all deployed decoys
    pub fn list_decoys(&self) -> Vec<&NetworkDecoy> {
        self.decoys.values().collect()
    }

    /// Get decoy by name
    pub fn get_decoy(&self, name: &str) -> Option<&NetworkDecoy> {
        self.decoys.get(name)
    }
}

/// Network scan detector using decoys
pub struct ScanDetector {
    scan_attempts: Vec<ScanAttempt>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanAttempt {
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub source_ip: String,
    pub target_ports: Vec<u16>,
    pub decoys_hit: Vec<String>,
    pub scan_type: ScanType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ScanType {
    PortScan,
    ServiceEnumeration,
    VulnerabilityScan,
    Unknown,
}

impl ScanDetector {
    pub fn new() -> Self {
        Self {
            scan_attempts: Vec::new(),
        }
    }

    /// Record scan attempt
    pub fn record_scan(&mut self, source_ip: String, target_ports: Vec<u16>, decoys_hit: Vec<String>) {
        let scan_type = if target_ports.len() > 10 {
            ScanType::PortScan
        } else if decoys_hit.len() > 3 {
            ScanType::ServiceEnumeration
        } else {
            ScanType::Unknown
        };

        self.scan_attempts.push(ScanAttempt {
            timestamp: chrono::Utc::now(),
            source_ip,
            target_ports,
            decoys_hit,
            scan_type,
        });
    }

    /// Get scan history
    pub fn get_scan_history(&self) -> &[ScanAttempt] {
        &self.scan_attempts
    }

    /// Detect reconnaissance patterns
    pub fn detect_reconnaissance(&self) -> Vec<String> {
        let mut alerts = Vec::new();

        // Group by source IP
        let mut ip_scans: HashMap<String, Vec<&ScanAttempt>> = HashMap::new();
        for attempt in &self.scan_attempts {
            ip_scans.entry(attempt.source_ip.clone())
                .or_insert_with(Vec::new)
                .push(attempt);
        }

        for (ip, scans) in ip_scans {
            if scans.len() >= 3 {
                alerts.push(format!(
                    "⚠️  RECONNAISSANCE DETECTED: {} performed {} scan attempts",
                    ip, scans.len()
                ));
            }

            let total_ports: usize = scans.iter().map(|s| s.target_ports.len()).sum();
            if total_ports > 20 {
                alerts.push(format!(
                    "🚨 PORT SCAN: {} scanned {} total ports across decoys",
                    ip, total_ports
                ));
            }
        }

        alerts
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ssh_decoy_deployment() {
        let mut manager = DecoyDeploymentManager::new();
        let (decoy, asset) = manager.deploy_ssh_decoy("192.168.1.50").unwrap();

        assert_eq!(decoy.decoy_type, DecoyType::SSH);
        assert_eq!(decoy.listen_port, 22);
        assert!(decoy.banner.is_some());
    }

    #[test]
    fn test_web_decoy_deployment() {
        let mut manager = DecoyDeploymentManager::new();
        let (decoy, _) = manager.deploy_web_decoy("192.168.1.51", 8080, false).unwrap();

        assert_eq!(decoy.decoy_type, DecoyType::HTTP);
        assert_eq!(decoy.listen_port, 8080);
    }

    #[test]
    fn test_scan_detection() {
        let mut detector = ScanDetector::new();

        detector.record_scan(
            "10.0.0.5".to_string(),
            vec![22, 80, 443, 3389],
            vec!["ssh_decoy".to_string(), "web_decoy".to_string()],
        );

        detector.record_scan(
            "10.0.0.5".to_string(),
            (1..=100).collect(),
            vec!["ssh_decoy".to_string()],
        );

        let alerts = detector.detect_reconnaissance();
        assert!(!alerts.is_empty());
    }
}
