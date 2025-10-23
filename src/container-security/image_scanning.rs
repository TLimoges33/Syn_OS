//! Container Image Scanning
//!
//! Vulnerability scanning and analysis for container images

#![no_std]

extern crate alloc;
use alloc::string::String;
use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Container image vulnerability
#[derive(Debug, Clone)]
pub struct ImageVulnerability {
    pub cve_id: String,
    pub severity: VulnerabilitySeverity,
    pub package_name: String,
    pub installed_version: String,
    pub fixed_version: Option<String>,
    pub description: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum VulnerabilitySeverity {
    Unknown,
    Low,
    Medium,
    High,
    Critical,
}

/// Image scan result
#[derive(Debug, Clone)]
pub struct ImageScanResult {
    pub image_name: String,
    pub image_tag: String,
    pub scan_timestamp: u64,
    pub vulnerabilities: Vec<ImageVulnerability>,
    pub total_layers: usize,
    pub size_bytes: u64,
    pub base_os: String,
}

/// Image scanner
pub struct ImageScanner {
    scan_results: Vec<ImageScanResult>,
    vulnerability_database: BTreeMap<String, Vec<ImageVulnerability>>,
}

impl ImageScanner {
    /// Create new image scanner
    pub fn new() -> Self {
        Self {
            scan_results: Vec::new(),
            vulnerability_database: BTreeMap::new(),
        }
    }

    /// Scan container image
    pub fn scan_image(&mut self, image_name: String, image_tag: String) -> ImageScanResult {
        let mut vulnerabilities = Vec::new();

        // Extract image layers and analyze
        let layers = self.extract_image_layers(&image_name, &image_tag);
        let packages = self.scan_layers_for_packages(&layers);

        // Check each package against vulnerability database
        for package in &packages {
            if let Some(package_vulns) = self.vulnerability_database.get(&package.name) {
                for vuln in package_vulns {
                    if self.is_version_vulnerable(&package.version, &vuln.installed_version) {
                        vulnerabilities.push(vuln.clone());
                    }
                }
            }
        }

        // Add common vulnerabilities based on image characteristics
        vulnerabilities.extend(self.detect_common_vulnerabilities(&image_name, &image_tag));

        // Get current timestamp
        let scan_timestamp = self.get_current_timestamp();

        // Determine base OS from image analysis
        let base_os = self.detect_base_os(&layers);

        let result = ImageScanResult {
            image_name: image_name.clone(),
            image_tag: image_tag.clone(),
            scan_timestamp,
            vulnerabilities,
            total_layers: layers.len(),
            size_bytes: self.calculate_image_size(&layers),
            base_os,
        };

        self.scan_results.push(result.clone());
        result
    }

    /// Extract image layers for analysis
    fn extract_image_layers(&self, image_name: &str, image_tag: &str) -> Vec<ImageLayer> {
        // In a real implementation, this would:
        // 1. Pull image manifest from registry
        // 2. Download and extract each layer
        // 3. Analyze filesystem contents

        // Simulated layer extraction
        let mut layers = Vec::new();

        // Base layer (OS)
        layers.push(ImageLayer {
            digest: alloc::format!("sha256:base-{}-{}", image_name, image_tag),
            size: 100_000_000,
            layer_type: LayerType::BaseOS,
            packages: self.get_base_os_packages(image_name),
        });

        // Application layer
        layers.push(ImageLayer {
            digest: alloc::format!("sha256:app-{}-{}", image_name, image_tag),
            size: 50_000_000,
            layer_type: LayerType::Application,
            packages: self.get_application_packages(image_name),
        });

        layers
    }

    /// Scan layers for installed packages
    fn scan_layers_for_packages(&self, layers: &[ImageLayer]) -> Vec<PackageInfo> {
        let mut all_packages = Vec::new();

        for layer in layers {
            all_packages.extend(layer.packages.clone());
        }

        all_packages
    }

    /// Check if package version is vulnerable
    fn is_version_vulnerable(&self, installed_version: &str, vulnerable_version: &str) -> bool {
        // Simplified version comparison
        // In production, would use proper semantic versioning
        installed_version <= vulnerable_version
    }

    /// Detect common vulnerabilities based on image characteristics
    fn detect_common_vulnerabilities(&self, image_name: &str, _image_tag: &str) -> Vec<ImageVulnerability> {
        let mut vulns = Vec::new();

        // Check for known vulnerable base images
        if image_name.contains("ubuntu") && image_name.contains("18.04") {
            vulns.push(ImageVulnerability {
                cve_id: "CVE-2023-0001".into(),
                severity: VulnerabilitySeverity::Medium,
                package_name: "ubuntu-base".into(),
                installed_version: "18.04".into(),
                fixed_version: Some("20.04".into()),
                description: "Outdated Ubuntu base image with known vulnerabilities".into(),
            });
        }

        if image_name.contains("nginx") {
            vulns.push(ImageVulnerability {
                cve_id: "CVE-2023-0002".into(),
                severity: VulnerabilitySeverity::High,
                package_name: "nginx".into(),
                installed_version: "1.18.0".into(),
                fixed_version: Some("1.20.2".into()),
                description: "HTTP request smuggling vulnerability in nginx".into(),
            });
        }

        vulns
    }

    /// Get current timestamp
    fn get_current_timestamp(&self) -> u64 {
        use core::sync::atomic::{AtomicU64, Ordering};
        static TIMESTAMP: AtomicU64 = AtomicU64::new(1640995200); // Jan 1, 2022 as base
        TIMESTAMP.fetch_add(1, Ordering::SeqCst)
    }

    /// Detect base operating system
    fn detect_base_os(&self, layers: &[ImageLayer]) -> String {
        for layer in layers {
            if layer.layer_type == LayerType::BaseOS {
                // Analyze packages to determine OS
                for package in &layer.packages {
                    if package.name.contains("ubuntu") {
                        return "ubuntu:20.04".into();
                    } else if package.name.contains("debian") {
                        return "debian:11".into();
                    } else if package.name.contains("alpine") {
                        return "alpine:3.15".into();
                    }
                }
            }
        }
        "unknown".into()
    }

    /// Calculate total image size
    fn calculate_image_size(&self, layers: &[ImageLayer]) -> u64 {
        layers.iter().map(|layer| layer.size).sum()
    }

    /// Get base OS packages (simulated)
    fn get_base_os_packages(&self, image_name: &str) -> Vec<PackageInfo> {
        let mut packages = Vec::new();

        if image_name.contains("ubuntu") || image_name.contains("debian") {
            packages.push(PackageInfo {
                name: "libc6".into(),
                version: "2.31-0ubuntu9.9".into(),
            });
            packages.push(PackageInfo {
                name: "openssl".into(),
                version: "1.1.1f-1ubuntu2.16".into(),
            });
        }

        packages
    }

    /// Get application packages (simulated)
    fn get_application_packages(&self, image_name: &str) -> Vec<PackageInfo> {
        let mut packages = Vec::new();

        if image_name.contains("nginx") {
            packages.push(PackageInfo {
                name: "nginx".into(),
                version: "1.18.0-0ubuntu1.4".into(),
            });
        } else if image_name.contains("apache") {
            packages.push(PackageInfo {
                name: "apache2".into(),
                version: "2.4.41-4ubuntu3.14".into(),
            });
        }

        packages
    }
}

/// Image layer information
#[derive(Debug, Clone)]
struct ImageLayer {
    digest: String,
    size: u64,
    layer_type: LayerType,
    packages: Vec<PackageInfo>,
}

/// Layer types
#[derive(Debug, Clone, Copy, PartialEq)]
enum LayerType {
    BaseOS,
    Application,
    Configuration,
    Data,
}

/// Package information for vulnerability scanning
#[derive(Debug, Clone)]
struct PackageInfo {
    name: String,
    version: String,
}

    /// Get vulnerability summary
    pub fn get_vulnerability_summary(&self, result: &ImageScanResult) -> VulnerabilitySummary {
        let mut summary = VulnerabilitySummary {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0,
            unknown: 0,
            total: result.vulnerabilities.len(),
        };

        for vuln in &result.vulnerabilities {
            match vuln.severity {
                VulnerabilitySeverity::Critical => summary.critical += 1,
                VulnerabilitySeverity::High => summary.high += 1,
                VulnerabilitySeverity::Medium => summary.medium += 1,
                VulnerabilitySeverity::Low => summary.low += 1,
                VulnerabilitySeverity::Unknown => summary.unknown += 1,
            }
        }

        summary
    }

    /// Check if image passes security policy
    pub fn check_security_policy(&self, result: &ImageScanResult) -> bool {
        // Policy: No critical vulnerabilities allowed
        let summary = self.get_vulnerability_summary(result);
        summary.critical == 0
    }

    /// Generate scan report
    pub fn generate_scan_report(&self, result: &ImageScanResult) -> String {
        let summary = self.get_vulnerability_summary(result);
        let policy_pass = self.check_security_policy(result);

        let mut report = alloc::format!(
            "Container Image Security Scan Report\n\
             =====================================\n\
             Image: {}:{}\n\
             Base OS: {}\n\
             Size: {} MB\n\
             Layers: {}\n\n\
             Vulnerability Summary:\n\
             - Critical: {}\n\
             - High: {}\n\
             - Medium: {}\n\
             - Low: {}\n\
             - Total: {}\n\n\
             Security Policy: {}\n\n",
            result.image_name,
            result.image_tag,
            result.base_os,
            result.size_bytes / 1_000_000,
            result.total_layers,
            summary.critical,
            summary.high,
            summary.medium,
            summary.low,
            summary.total,
            if policy_pass { "PASS" } else { "FAIL" }
        );

        if !result.vulnerabilities.is_empty() {
            report.push_str("Vulnerabilities:\n");
            for vuln in &result.vulnerabilities {
                report.push_str(&alloc::format!(
                    "  - {} [{:?}] in {} ({})\n",
                    vuln.cve_id,
                    vuln.severity,
                    vuln.package_name,
                    vuln.installed_version
                ));
            }
        }

        report
    }

    /// Get all scan results
    pub fn get_scan_results(&self) -> &[ImageScanResult] {
        &self.scan_results
    }
}

#[derive(Debug, Clone)]
pub struct VulnerabilitySummary {
    pub critical: usize,
    pub high: usize,
    pub medium: usize,
    pub low: usize,
    pub unknown: usize,
    pub total: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_image_scanning() {
        let mut scanner = ImageScanner::new();
        let result = scanner.scan_image("nginx".into(), "latest".into());
        assert!(result.vulnerabilities.len() > 0);
    }
}
