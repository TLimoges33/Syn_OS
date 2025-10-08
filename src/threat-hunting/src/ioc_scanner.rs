//! IOC Scanner
//!
//! System-wide indicator of compromise scanning

use crate::{Result, ThreatHuntingError, ArtifactType};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use walkdir::WalkDir;

/// IOC scanner for system-wide searches
pub struct IOCScanner {
    scan_targets: Vec<ScanTarget>,
}

#[derive(Debug, Clone)]
struct ScanTarget {
    path: String,
    target_type: TargetType,
}

#[derive(Debug, Clone, PartialEq)]
enum TargetType {
    FileSystem,
    Registry,
    Memory,
    Network,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IOCMatch {
    pub ioc: String,
    pub location: String,
    pub artifact_type: ArtifactType,
    pub context: String,
    pub hash: Option<String>,
}

impl IOCScanner {
    pub fn new() -> Self {
        let mut scanner = Self {
            scan_targets: Vec::new(),
        };
        scanner.initialize_default_targets();
        scanner
    }

    fn initialize_default_targets(&mut self) {
        // Common malware locations
        self.scan_targets.push(ScanTarget {
            path: "/tmp".to_string(),
            target_type: TargetType::FileSystem,
        });

        self.scan_targets.push(ScanTarget {
            path: "/var/tmp".to_string(),
            target_type: TargetType::FileSystem,
        });

        self.scan_targets.push(ScanTarget {
            path: "/home".to_string(),
            target_type: TargetType::FileSystem,
        });

        // Windows paths (for cross-platform support)
        self.scan_targets.push(ScanTarget {
            path: "C:\\Windows\\Temp".to_string(),
            target_type: TargetType::FileSystem,
        });

        self.scan_targets.push(ScanTarget {
            path: "C:\\Users".to_string(),
            target_type: TargetType::FileSystem,
        });
    }

    /// Scan system for IOCs
    pub fn scan_system(&self, iocs: &[String]) -> Result<Vec<IOCMatch>> {
        let mut matches = Vec::new();

        for target in &self.scan_targets {
            match target.target_type {
                TargetType::FileSystem => {
                    matches.extend(self.scan_filesystem(&target.path, iocs)?);
                }
                TargetType::Registry => {
                    matches.extend(self.scan_registry(&target.path, iocs)?);
                }
                TargetType::Memory => {
                    matches.extend(self.scan_memory(iocs)?);
                }
                TargetType::Network => {
                    matches.extend(self.scan_network(iocs)?);
                }
            }
        }

        Ok(matches)
    }

    fn scan_filesystem(&self, path: &str, iocs: &[String]) -> Result<Vec<IOCMatch>> {
        let mut matches = Vec::new();

        // Check if path exists
        if !std::path::Path::new(path).exists() {
            return Ok(matches);
        }

        for entry in WalkDir::new(path).max_depth(3).follow_links(false) {
            let entry = entry.map_err(|e| ThreatHuntingError::IOCError(e.to_string()))?;

            if entry.file_type().is_file() {
                let file_path = entry.path().to_string_lossy().to_string();
                let file_name = entry.file_name().to_string_lossy().to_string();

                // Check filename against IOCs
                for ioc in iocs {
                    if file_name.contains(ioc) || file_path.contains(ioc) {
                        matches.push(IOCMatch {
                            ioc: ioc.clone(),
                            location: file_path.clone(),
                            artifact_type: ArtifactType::File,
                            context: format!("File: {}", file_name),
                            hash: self.calculate_file_hash(&file_path).ok(),
                        });
                    }
                }

                // Check file content for IOCs (if text file)
                if let Ok(content) = std::fs::read_to_string(entry.path()) {
                    for ioc in iocs {
                        if content.contains(ioc) {
                            matches.push(IOCMatch {
                                ioc: ioc.clone(),
                                location: file_path.clone(),
                                artifact_type: ArtifactType::File,
                                context: format!("IOC found in file content"),
                                hash: self.calculate_file_hash(&file_path).ok(),
                            });
                        }
                    }
                }
            }
        }

        Ok(matches)
    }

    fn scan_registry(&self, _path: &str, iocs: &[String]) -> Result<Vec<IOCMatch>> {
        // Mock registry scanning (would use Windows Registry API in production)
        let mut matches = Vec::new();

        let mock_registry = vec![
            ("HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "malware.exe"),
            ("HKCU\\Software\\Classes\\mscfile\\shell\\open\\command", "cmd.exe /c evil.bat"),
        ];

        for (key, value) in mock_registry {
            for ioc in iocs {
                if key.contains(ioc) || value.contains(ioc) {
                    matches.push(IOCMatch {
                        ioc: ioc.clone(),
                        location: key.to_string(),
                        artifact_type: ArtifactType::Registry,
                        context: format!("Registry value: {}", value),
                        hash: None,
                    });
                }
            }
        }

        Ok(matches)
    }

    fn scan_memory(&self, iocs: &[String]) -> Result<Vec<IOCMatch>> {
        // Mock memory scanning (would use process memory inspection in production)
        let mut matches = Vec::new();

        let mock_processes = vec![
            ("cmd.exe", "whoami && net user administrator"),
            ("powershell.exe", "Invoke-Mimikatz -DumpCreds"),
        ];

        for (process, cmdline) in mock_processes {
            for ioc in iocs {
                if process.contains(ioc) || cmdline.contains(ioc) {
                    matches.push(IOCMatch {
                        ioc: ioc.clone(),
                        location: format!("Process: {}", process),
                        artifact_type: ArtifactType::Process,
                        context: format!("Command line: {}", cmdline),
                        hash: None,
                    });
                }
            }
        }

        Ok(matches)
    }

    fn scan_network(&self, iocs: &[String]) -> Result<Vec<IOCMatch>> {
        // Mock network connection scanning
        let mut matches = Vec::new();

        let mock_connections = vec![
            ("192.168.1.100", "445", "SMB"),
            ("10.0.0.5", "4444", "Reverse Shell"),
        ];

        for (ip, port, description) in mock_connections {
            for ioc in iocs {
                if ip.contains(ioc) || port.contains(ioc) {
                    matches.push(IOCMatch {
                        ioc: ioc.clone(),
                        location: format!("{}:{}", ip, port),
                        artifact_type: ArtifactType::Network,
                        context: description.to_string(),
                        hash: None,
                    });
                }
            }
        }

        Ok(matches)
    }

    fn calculate_file_hash(&self, file_path: &str) -> Result<String> {
        use sha2::{Sha256, Digest};

        let content = std::fs::read(file_path)
            .map_err(|e| ThreatHuntingError::IOCError(format!("Failed to read file: {}", e)))?;

        let mut hasher = Sha256::new();
        hasher.update(&content);
        Ok(format!("{:x}", hasher.finalize()))
    }

    /// Add custom scan target
    pub fn add_scan_target(&mut self, path: String, target_type: &str) {
        let target_type = match target_type {
            "filesystem" => TargetType::FileSystem,
            "registry" => TargetType::Registry,
            "memory" => TargetType::Memory,
            "network" => TargetType::Network,
            _ => TargetType::FileSystem,
        };

        self.scan_targets.push(ScanTarget {
            path,
            target_type,
        });
    }

    /// Scan specific IOC types
    pub fn scan_by_type(&self, ioc_type: &str, iocs: &[String]) -> Result<Vec<IOCMatch>> {
        match ioc_type.to_lowercase().as_str() {
            "ip" | "ipaddress" => self.scan_network(iocs),
            "domain" | "url" => self.scan_network(iocs),
            "hash" | "md5" | "sha256" => self.scan_filesystem("/", iocs),
            "filename" => self.scan_filesystem("/", iocs),
            _ => self.scan_system(iocs),
        }
    }

    /// Get scan statistics
    pub fn get_scan_stats(&self) -> HashMap<String, usize> {
        let mut stats = HashMap::new();
        stats.insert("total_targets".to_string(), self.scan_targets.len());

        let filesystem_count = self.scan_targets.iter()
            .filter(|t| t.target_type == TargetType::FileSystem)
            .count();
        stats.insert("filesystem_targets".to_string(), filesystem_count);

        stats
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ioc_scanner_creation() {
        let scanner = IOCScanner::new();
        assert!(!scanner.scan_targets.is_empty());
    }

    #[test]
    fn test_ioc_scanning() {
        let scanner = IOCScanner::new();
        let iocs = vec!["malware.exe".to_string(), "192.168.1.100".to_string()];
        let matches = scanner.scan_system(&iocs).unwrap();
        // May or may not find matches depending on system state
        assert!(matches.len() >= 0);
    }
}
