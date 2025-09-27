//! Repository management for SynPkg
//! 
//! Handles integration with multiple package repositories including
//! Kali, BlackArch, Parrot, and SynOS-specific repositories

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use anyhow::{Result, anyhow};
use serde::{Deserialize, Serialize};

use crate::core::PackageInfo;

/// Package source enumeration
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum PackageSource {
    Kali,
    BlackArch,
    Parrot,
    SynOS,
    Ubuntu,
    Debian,
}

impl PackageSource {
    pub fn as_str(&self) -> &'static str {
        match self {
            PackageSource::Kali => "kali",
            PackageSource::BlackArch => "blackarch",
            PackageSource::Parrot => "parrot",
            PackageSource::SynOS => "synos",
            PackageSource::Ubuntu => "ubuntu",
            PackageSource::Debian => "debian",
        }
    }
}

/// Repository configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepositoryConfig {
    pub name: String,
    pub source: PackageSource,
    pub url: String,
    pub enabled: bool,
    pub priority: u8,
    pub gpg_key: Option<String>,
    pub components: Vec<String>,
    pub architectures: Vec<String>,
}

/// Individual repository handler
pub struct Repository {
    config: RepositoryConfig,
    package_cache: HashMap<String, PackageInfo>,
    last_update: std::time::SystemTime,
}

impl Repository {
    pub fn new(config: RepositoryConfig) -> Self {
        Self {
            config,
            package_cache: HashMap::new(),
            last_update: std::time::UNIX_EPOCH,
        }
    }

    /// Update repository package database
    pub async fn update(&mut self) -> Result<()> {
        println!("📥 Updating {} repository...", self.config.name);

        // Simulate repository update based on source type
        match self.config.source {
            PackageSource::Kali => self.update_kali_repo().await?,
            PackageSource::BlackArch => self.update_blackarch_repo().await?,
            PackageSource::Parrot => self.update_parrot_repo().await?,
            PackageSource::SynOS => self.update_synos_repo().await?,
            PackageSource::Ubuntu => self.update_ubuntu_repo().await?,
            PackageSource::Debian => self.update_debian_repo().await?,
        }

        self.last_update = std::time::SystemTime::now();
        println!("✅ {} repository updated", self.config.name);
        Ok(())
    }

    /// Search packages in this repository
    pub async fn search(&self, query: &str, category: Option<&str>) -> Result<Vec<PackageInfo>> {
        let mut results = Vec::new();
        
        for (name, info) in &self.package_cache {
            let matches_query = name.contains(query) || 
                               info.description.to_lowercase().contains(&query.to_lowercase());
            
            let matches_category = category.map_or(true, |cat| info.category == cat);
            
            if matches_query && matches_category {
                results.push(info.clone());
            }
        }

        Ok(results)
    }

    /// Find specific package
    pub async fn find_package(&self, name: &str) -> Option<PackageInfo> {
        self.package_cache.get(name).cloned()
    }

    /// Get all packages from this repository
    pub fn get_all_packages(&self) -> Vec<String> {
        self.package_cache.keys().cloned().collect()
    }

    // Repository-specific update methods
    async fn update_kali_repo(&mut self) -> Result<()> {
        // Simulate Kali repository update
        // In reality, this would parse apt repository data
        self.add_sample_kali_packages();
        Ok(())
    }

    async fn update_blackarch_repo(&mut self) -> Result<()> {
        // Simulate BlackArch repository update
        // In reality, this would parse pacman repository data
        self.add_sample_blackarch_packages();
        Ok(())
    }

    async fn update_parrot_repo(&mut self) -> Result<()> {
        // Simulate Parrot repository update
        self.add_sample_parrot_packages();
        Ok(())
    }

    async fn update_synos_repo(&mut self) -> Result<()> {
        // Simulate SynOS repository update
        self.add_sample_synos_packages();
        Ok(())
    }

    async fn update_ubuntu_repo(&mut self) -> Result<()> {
        // Simulate Ubuntu repository update
        self.add_sample_ubuntu_packages();
        Ok(())
    }

    async fn update_debian_repo(&mut self) -> Result<()> {
        // Simulate Debian repository update
        self.add_sample_debian_packages();
        Ok(())
    }

    // Sample package data for demonstration
    fn add_sample_kali_packages(&mut self) {
        use crate::core::{PackageInfo, SecurityRating};
        
        let packages = vec![
            ("nmap", "7.94", "Network exploration tool and security scanner", "security-scanner"),
            ("metasploit-framework", "6.3.41", "Advanced penetration testing framework", "exploitation"),
            ("wireshark", "4.0.8", "Network protocol analyzer", "network-analysis"),
            ("burpsuite", "2023.10.3", "Web application security testing", "web-security"),
            ("sqlmap", "1.7.8", "Automatic SQL injection and database takeover tool", "web-security"),
            ("john", "1.9.0", "John the Ripper password cracker", "password-cracking"),
            ("hashcat", "6.2.6", "Advanced password recovery utility", "password-cracking"),
            ("aircrack-ng", "1.7", "WiFi security auditing tools", "wireless-security"),
        ];

        for (name, version, desc, category) in packages {
            let package = PackageInfo {
                name: name.to_string(),
                version: version.to_string(),
                description: desc.to_string(),
                source: PackageSource::Kali,
                category: category.to_string(),
                dependencies: vec![],
                conflicts: vec![],
                provides: vec![],
                size: 1024 * 1024, // 1MB default
                architecture: "amd64".to_string(),
                maintainer: "Kali Linux Team".to_string(),
                homepage: Some(format!("https://www.kali.org/tools/{}/", name)),
                license: "GPL".to_string(),
                security_rating: SecurityRating::Trusted,
                consciousness_compatibility: 0.9,
                educational_value: 8,
            };
            self.package_cache.insert(name.to_string(), package);
        }
    }

    fn add_sample_blackarch_packages(&mut self) {
        use crate::core::{PackageInfo, SecurityRating};
        
        let packages = vec![
            ("radare2", "5.8.8", "Reverse engineering framework", "reverse-engineering"),
            ("ghidra", "10.4", "NSA's reverse engineering tool", "reverse-engineering"),
            ("volatility", "2.6.1", "Advanced memory forensics framework", "forensics"),
            ("yara", "4.3.2", "Pattern matching swiss knife for malware researchers", "malware-analysis"),
            ("binwalk", "2.3.4", "Firmware analysis tool", "firmware-analysis"),
            ("autopsy", "4.20.0", "Digital forensics platform", "forensics"),
            ("sleuthkit", "4.12.0", "Digital investigation tools", "forensics"),
        ];

        for (name, version, desc, category) in packages {
            let package = PackageInfo {
                name: name.to_string(),
                version: version.to_string(),
                description: desc.to_string(),
                source: PackageSource::BlackArch,
                category: category.to_string(),
                dependencies: vec![],
                conflicts: vec![],
                provides: vec![],
                size: 2048 * 1024, // 2MB default
                architecture: "x86_64".to_string(),
                maintainer: "BlackArch Team".to_string(),
                homepage: Some(format!("https://blackarch.org/tools.html#{}", name)),
                license: "Various".to_string(),
                security_rating: SecurityRating::Community,
                consciousness_compatibility: 0.8,
                educational_value: 7,
            };
            self.package_cache.insert(name.to_string(), package);
        }
    }

    fn add_sample_parrot_packages(&mut self) {
        use crate::core::{PackageInfo, SecurityRating};
        
        let packages = vec![
            ("anonsurf", "3.2.0", "Anonymous surfing with Tor", "anonymity"),
            ("firejail", "0.9.72", "SUID sandbox program", "security-hardening"),
            ("bleachbit", "4.4.2", "System cleaner and privacy tool", "privacy"),
            ("mat2", "0.13.4", "Metadata removal tool", "privacy"),
            ("onionshare", "2.6", "Secure and anonymous file sharing", "anonymity"),
        ];

        for (name, version, desc, category) in packages {
            let package = PackageInfo {
                name: name.to_string(),
                version: version.to_string(),
                description: desc.to_string(),
                source: PackageSource::Parrot,
                category: category.to_string(),
                dependencies: vec![],
                conflicts: vec![],
                provides: vec![],
                size: 512 * 1024, // 512KB default
                architecture: "amd64".to_string(),
                maintainer: "Parrot Security Team".to_string(),
                homepage: Some("https://parrotsec.org".to_string()),
                license: "GPL-3".to_string(),
                security_rating: SecurityRating::Verified,
                consciousness_compatibility: 0.85,
                educational_value: 8,
            };
            self.package_cache.insert(name.to_string(), package);
        }
    }

    fn add_sample_synos_packages(&mut self) {
        use crate::core::{PackageInfo, SecurityRating};
        
        let packages = vec![
            ("synos-consciousness", "1.0.0", "SynOS consciousness integration layer", "consciousness"),
            ("synosctl", "1.0.0", "SynOS system control utility", "system-management"),
            ("synos-ai-toolkit", "1.0.0", "AI-powered security toolkit", "ai-security"),
            ("consciousness-monitor", "1.0.0", "System consciousness monitoring", "monitoring"),
            ("synos-shell", "1.0.0", "Consciousness-aware shell", "shell"),
        ];

        for (name, version, desc, category) in packages {
            let package = PackageInfo {
                name: name.to_string(),
                version: version.to_string(),
                description: desc.to_string(),
                source: PackageSource::SynOS,
                category: category.to_string(),
                dependencies: vec![],
                conflicts: vec![],
                provides: vec![],
                size: 4096 * 1024, // 4MB default
                architecture: "amd64".to_string(),
                maintainer: "SynOS Team".to_string(),
                homepage: Some("https://syn-os.org".to_string()),
                license: "SynOS-1.0".to_string(),
                security_rating: SecurityRating::Trusted,
                consciousness_compatibility: 1.0,
                educational_value: 10,
            };
            self.package_cache.insert(name.to_string(), package);
        }
    }

    fn add_sample_ubuntu_packages(&mut self) {
        use crate::core::{PackageInfo, SecurityRating};
        
        let packages = vec![
            ("firefox", "119.0", "Web browser", "web-browser"),
            ("libreoffice", "7.6.2", "Office suite", "office"),
            ("gimp", "2.10.34", "Image editor", "graphics"),
            ("vlc", "3.0.18", "Media player", "multimedia"),
        ];

        for (name, version, desc, category) in packages {
            let package = PackageInfo {
                name: name.to_string(),
                version: version.to_string(),
                description: desc.to_string(),
                source: PackageSource::Ubuntu,
                category: category.to_string(),
                dependencies: vec![],
                conflicts: vec![],
                provides: vec![],
                size: 50 * 1024 * 1024, // 50MB default
                architecture: "amd64".to_string(),
                maintainer: "Ubuntu Developers".to_string(),
                homepage: None,
                license: "Various".to_string(),
                security_rating: SecurityRating::Verified,
                consciousness_compatibility: 0.5,
                educational_value: 5,
            };
            self.package_cache.insert(name.to_string(), package);
        }
    }

    fn add_sample_debian_packages(&mut self) {
        self.add_sample_ubuntu_packages(); // Similar to Ubuntu for now
    }
}

/// Repository manager coordinating multiple repositories
pub struct RepositoryManager {
    repositories: Vec<Repository>,
    config_path: PathBuf,
}

impl RepositoryManager {
    /// Create new repository manager
    pub async fn new(config_dir: &Path) -> Result<Self> {
        let config_path = config_dir.join("repositories.toml");
        
        let repositories = Self::load_default_repositories().await?;
        
        Ok(Self {
            repositories,
            config_path,
        })
    }

    /// Load default repository configurations
    async fn load_default_repositories() -> Result<Vec<Repository>> {
        let mut repositories = Vec::new();

        // Kali Linux repository
        repositories.push(Repository::new(RepositoryConfig {
            name: "Kali Linux".to_string(),
            source: PackageSource::Kali,
            url: "http://http.kali.org/kali".to_string(),
            enabled: true,
            priority: 90,
            gpg_key: Some("kali-archive-keyring".to_string()),
            components: vec!["main".to_string(), "contrib".to_string(), "non-free".to_string()],
            architectures: vec!["amd64".to_string()],
        }));

        // BlackArch repository
        repositories.push(Repository::new(RepositoryConfig {
            name: "BlackArch".to_string(),
            source: PackageSource::BlackArch,
            url: "https://blackarch.org/blackarch".to_string(),
            enabled: true,
            priority: 85,
            gpg_key: Some("blackarch-keyring".to_string()),
            components: vec!["os".to_string()],
            architectures: vec!["x86_64".to_string()],
        }));

        // Parrot Security repository
        repositories.push(Repository::new(RepositoryConfig {
            name: "Parrot Security".to_string(),
            source: PackageSource::Parrot,
            url: "https://deb.parrotsec.org/parrot".to_string(),
            enabled: true,
            priority: 80,
            gpg_key: Some("parrot-archive-keyring".to_string()),
            components: vec!["main".to_string(), "contrib".to_string(), "non-free".to_string()],
            architectures: vec!["amd64".to_string()],
        }));

        // SynOS repository
        repositories.push(Repository::new(RepositoryConfig {
            name: "SynOS Official".to_string(),
            source: PackageSource::SynOS,
            url: "https://packages.syn-os.org".to_string(),
            enabled: true,
            priority: 100,
            gpg_key: Some("synos-archive-keyring".to_string()),
            components: vec!["main".to_string(), "consciousness".to_string()],
            architectures: vec!["amd64".to_string()],
        }));

        // Ubuntu repository (fallback)
        repositories.push(Repository::new(RepositoryConfig {
            name: "Ubuntu".to_string(),
            source: PackageSource::Ubuntu,
            url: "http://archive.ubuntu.com/ubuntu".to_string(),
            enabled: true,
            priority: 50,
            gpg_key: Some("ubuntu-keyring".to_string()),
            components: vec!["main".to_string(), "restricted".to_string(), "universe".to_string(), "multiverse".to_string()],
            architectures: vec!["amd64".to_string()],
        }));

        Ok(repositories)
    }

    /// Update all enabled repositories
    pub async fn update_all(&mut self) -> Result<()> {
        for repo in &mut self.repositories {
            if repo.config.enabled {
                repo.update().await?;
            }
        }
        Ok(())
    }

    /// Search across all repositories
    pub async fn search(&self, query: &str, category: Option<&str>) -> Result<Vec<PackageInfo>> {
        let mut all_results = Vec::new();
        
        for repo in &self.repositories {
            if repo.config.enabled {
                let results = repo.search(query, category).await?;
                all_results.extend(results);
            }
        }

        // Sort by priority and remove duplicates
        all_results.sort_by(|a, b| {
            // Prefer higher priority sources
            let priority_a = self.get_source_priority(a.source);
            let priority_b = self.get_source_priority(b.source);
            priority_b.cmp(&priority_a)
        });

        Ok(all_results)
    }

    /// Find package in repositories (with source preference)
    pub async fn find_package(&self, name: &str, preferred_source: Option<PackageSource>) -> Result<PackageInfo> {
        // Try preferred source first
        if let Some(source) = preferred_source {
            for repo in &self.repositories {
                if repo.config.source == source && repo.config.enabled {
                    if let Some(package) = repo.find_package(name).await {
                        return Ok(package);
                    }
                }
            }
        }

        // Search all repositories by priority
        let mut candidates = Vec::new();
        for repo in &self.repositories {
            if repo.config.enabled {
                if let Some(package) = repo.find_package(name).await {
                    candidates.push((package, repo.config.priority));
                }
            }
        }

        if candidates.is_empty() {
            return Err(anyhow!("Package '{}' not found in any repository", name));
        }

        // Return highest priority match
        candidates.sort_by(|a, b| b.1.cmp(&a.1));
        Ok(candidates[0].0.clone())
    }

    /// Get all available packages
    pub async fn get_all_packages(&self) -> Result<Vec<String>> {
        let mut all_packages = Vec::new();
        for repo in &self.repositories {
            if repo.config.enabled {
                all_packages.extend(repo.get_all_packages());
            }
        }
        all_packages.sort();
        all_packages.dedup();
        Ok(all_packages)
    }

    fn get_source_priority(&self, source: PackageSource) -> u8 {
        for repo in &self.repositories {
            if repo.config.source == source {
                return repo.config.priority;
            }
        }
        0
    }
}
