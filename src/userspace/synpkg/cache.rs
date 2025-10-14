//! Package cache management for SynPkg
//!
//! Handles local package caching, metadata storage, and cache cleanup

use anyhow::{anyhow, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tokio::fs;

use crate::core::{InstallStatus, PackageInfo};

/// Tracks installed packages and their metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstalledPackageRecord {
    pub name: String,
    pub version: String,
    pub install_date: String,
    pub source_repo: String,
    pub dependencies: Vec<String>,
    pub size_bytes: u64,
    pub executable_path: Option<PathBuf>,
}

/// Package cache statistics
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct CacheStats {
    pub total_packages: usize,
    pub total_size: u64,
    pub categories: HashMap<String, u32>,
    pub recent_installs: Vec<String>,
}

/// Results from cache cleanup operation
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct CleanupResults {
    pub files_removed: u32,
    pub space_freed_bytes: u64,
}

/// Main package cache manager
#[derive(Debug)]
pub struct PackageCache {
    cache_dir: PathBuf,
    installed_packages: HashMap<String, InstalledPackageRecord>,
    database_path: PathBuf,
}

impl PackageCache {
    /// Create new package cache
    pub async fn new(cache_dir: &Path) -> Result<Self> {
        let database_path = cache_dir.join("installed.json");

        let mut cache = Self {
            cache_dir: cache_dir.to_path_buf(),
            installed_packages: HashMap::new(),
            database_path,
        };

        cache.load_database().await?;
        Ok(cache)
    }

    /// Load installed packages database
    async fn load_database(&mut self) -> Result<()> {
        if self.database_path.exists() {
            let content = fs::read_to_string(&self.database_path).await?;
            self.installed_packages = serde_json::from_str(&content)?;
        }
        Ok(())
    }

    /// Save installed packages database
    async fn save_database(&self) -> Result<()> {
        let content = serde_json::to_string_pretty(&self.installed_packages)?;
        fs::write(&self.database_path, content).await?;
        Ok(())
    }

    /// Check if package is installed
    pub async fn is_installed(&self, package_name: &str) -> Result<bool> {
        Ok(self.installed_packages.contains_key(package_name))
    }

    /// Add installed package record
    pub async fn add_package(
        &mut self,
        package: &PackageInfo,
        executable_path: Option<PathBuf>,
    ) -> Result<()> {
        let record = InstalledPackageRecord {
            name: package.name.clone(),
            version: package.version.clone(),
            install_date: chrono::Utc::now().to_rfc3339(),
            source_repo: format!("{:?}", package.source), // Use Debug format
            dependencies: package.dependencies.clone(),
            size_bytes: 0, // Default size since PackageInfo doesn't have size_bytes
            executable_path,
        };

        self.installed_packages.insert(package.name.clone(), record);
        self.save_database().await?;
        Ok(())
    }

    /// Remove installed package record
    pub async fn remove_package(&mut self, package_name: &str) -> Result<bool> {
        let removed = self.installed_packages.remove(package_name).is_some();
        if removed {
            self.save_database().await?;
        }
        Ok(removed)
    }

    /// Get installation status
    pub async fn get_install_status(&self, package_name: &str) -> Result<InstallStatus> {
        if self.installed_packages.contains_key(package_name) {
            Ok(InstallStatus::Installed)
        } else {
            Ok(InstallStatus::NotInstalled)
        }
    }

    /// Get installed package info
    pub async fn get_installed_package(
        &self,
        package_name: &str,
    ) -> Option<&InstalledPackageRecord> {
        self.installed_packages.get(package_name)
    }

    /// List all installed packages
    pub async fn list_installed(&self) -> Vec<&InstalledPackageRecord> {
        self.installed_packages.values().collect()
    }

    /// Get cache statistics
    pub async fn get_stats(&self) -> Result<CacheStats> {
        let total_packages = self.installed_packages.len();
        let total_size = self.installed_packages.values().map(|p| p.size_bytes).sum();

        let category_count: HashMap<String, u32> = HashMap::new();

        let recent_installs = self
            .installed_packages
            .values()
            .map(|p| p.name.clone())
            .take(10)
            .collect();

        Ok(CacheStats {
            total_packages,
            total_size,
            categories: category_count,
            recent_installs,
        })
    }

    /// Clean package cache (remove orphaned files)
    pub async fn clean_cache(&mut self) -> Result<CleanupResults> {
        let files_removed = 0;
        let space_freed = 0;

        // Scan cache directory for orphaned files
        // This would typically check for downloaded packages not in the database

        Ok(CleanupResults {
            files_removed,
            space_freed_bytes: space_freed,
        })
    }

    /// Mark package as installed
    pub async fn mark_installed(&mut self, package_name: &str, version: &str) -> Result<()> {
        let record = InstalledPackageRecord {
            name: package_name.to_string(),
            version: version.to_string(),
            install_date: chrono::Utc::now().to_rfc3339(),
            source_repo: "unknown".to_string(),
            dependencies: Vec::new(),
            size_bytes: 0,
            executable_path: None,
        };

        self.installed_packages
            .insert(package_name.to_string(), record);
        self.save_database().await?;
        Ok(())
    }

    /// Get packages that depend on given package
    pub async fn get_dependents(&self, package_name: &str) -> Result<Vec<String>> {
        let mut dependents = Vec::new();

        for (name, package) in &self.installed_packages {
            if package.dependencies.contains(&package_name.to_string()) {
                dependents.push(name.clone());
            }
        }

        Ok(dependents)
    }

    /// Mark package as removed
    pub async fn mark_removed(&mut self, package_name: &str) -> Result<()> {
        self.installed_packages.remove(package_name);
        self.save_database().await?;
        Ok(())
    }

    /// Refresh cache database
    pub async fn refresh(&mut self) -> Result<()> {
        self.load_database().await?;
        Ok(())
    }

    /// Get upgradable packages
    pub async fn get_upgradable_packages(&self) -> Result<Vec<String>> {
        // This would check for available updates for installed packages
        // For now, return empty list
        Ok(Vec::new())
    }

    /// Get list of installed package names
    pub async fn get_installed_packages(&self) -> Result<Vec<String>> {
        Ok(self.installed_packages.keys().cloned().collect())
    }
}
