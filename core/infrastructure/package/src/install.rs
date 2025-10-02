use std::sync::Arc;
use std::path::PathBuf;
use tokio::process::Command;
use crate::core::{Package, PackageStatus};
use crate::dependency::DependencyPlan;

/// High-performance package installation engine
pub struct InstallationEngine {
    config: Arc<crate::PackageManagerConfig>,
    database: Arc<tokio::sync::Mutex<sqlx::SqlitePool>>,
    active_installations: Arc<tokio::sync::RwLock<std::collections::HashMap<String, InstallationTask>>>,
}

#[derive(Debug, Clone)]
struct InstallationTask {
    pub package_name: String,
    pub status: PackageStatus,
    pub progress: f32,
    pub start_time: chrono::DateTime<chrono::Utc>,
    pub log: Vec<String>,
}

impl InstallationEngine {
    pub async fn new(config: Arc<crate::PackageManagerConfig>) -> crate::Result<Self> {
        // Create directories if they don't exist
        tokio::fs::create_dir_all(std::path::Path::new(&config.database_path).parent().unwrap()).await?;
        tokio::fs::create_dir_all(&config.cache_dir).await?;
        tokio::fs::create_dir_all(&config.download_dir).await?;
        
        // Initialize database
        let database_pool = sqlx::SqlitePool::connect(&format!("sqlite:{}", config.database_path)).await?;
        
        // Create tables if they don't exist
        sqlx::query(r#"
            CREATE TABLE IF NOT EXISTS installed_packages (
                name TEXT PRIMARY KEY,
                version TEXT NOT NULL,
                source TEXT NOT NULL,
                installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                size_bytes INTEGER DEFAULT 0,
                checksum TEXT,
                metadata TEXT
            )
        "#)
        .execute(&database_pool)
        .await?;
        
        sqlx::query(r#"
            CREATE TABLE IF NOT EXISTS installation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT NOT NULL,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        "#)
        .execute(&database_pool)
        .await?;
        
        Ok(Self {
            config,
            database: Arc::new(tokio::sync::Mutex::new(database_pool)),
            active_installations: Arc::new(tokio::sync::RwLock::new(std::collections::HashMap::new())),
        })
    }
    
    /// Execute installation plan with parallel processing
    pub async fn execute_installation(
        &self,
        root_package: Package,
        plan: DependencyPlan,
    ) -> crate::Result<()> {
        tracing::info!("Starting installation: {}", plan.summary());
        
        // Check for conflicts that prevent installation
        if plan.has_critical_conflicts() || plan.has_errors() {
            return Err(crate::PackageManagerError::InstallationFailed {
                package: root_package.name,
                reason: "Critical dependency conflicts detected".to_string(),
            });
        }
        
        // Create download directory
        let download_dir = PathBuf::from(&self.config.download_dir);
        tokio::fs::create_dir_all(&download_dir).await?;
        
        // Install packages in dependency order
        for package_name in &plan.installation_order {
            if let Some(package) = plan.packages.iter().find(|p| p.name == *package_name) {
                self.install_single_package(package).await?;
            }
        }
        
        tracing::info!("Installation completed successfully for {}", root_package.name);
        Ok(())
    }
    
    async fn install_single_package(&self, package: &Package) -> crate::Result<()> {
        let start_time = chrono::Utc::now();
        
        // Create installation task
        let task = InstallationTask {
            package_name: package.name.clone(),
            status: PackageStatus::Installing,
            progress: 0.0,
            start_time,
            log: Vec::new(),
        };
        
        self.active_installations.write().await.insert(
            package.name.clone(),
            task.clone(),
        );
        
        // Log installation start
        self.log_operation(&package.name, "install", "started", None).await?;
        
        match self.do_install_package(package).await {
            Ok(()) => {
                // Update status to installed
                self.update_task_status(&package.name, PackageStatus::Installed, 100.0).await;
                
                // Record in database
                self.record_installation(package).await?;
                
                // Log success
                self.log_operation(&package.name, "install", "completed", None).await?;
                
                tracing::info!("Successfully installed {}", package.name);
            }
            Err(e) => {
                // Update status to failed
                let error_msg = e.to_string();
                self.update_task_status(&package.name, PackageStatus::Failed(error_msg.clone()), 0.0).await;
                
                // Log failure
                self.log_operation(&package.name, "install", "failed", Some(&error_msg)).await?;
                
                return Err(e);
            }
        }
        
        // Remove from active installations
        self.active_installations.write().await.remove(&package.name);
        
        Ok(())
    }
    
    async fn do_install_package(&self, package: &Package) -> crate::Result<()> {
        match package.source {
            crate::core::PackageSource::SynosOfficial => {
                self.install_synos_package(package).await
            }
            crate::core::PackageSource::UbuntuApt => {
                self.install_apt_package(package).await
            }
            crate::core::PackageSource::ArchPacman => {
                self.install_pacman_package(package).await
            }
            crate::core::PackageSource::Flatpak => {
                self.install_flatpak_package(package).await
            }
            crate::core::PackageSource::Snap => {
                self.install_snap_package(package).await
            }
            crate::core::PackageSource::ConsciousnessEnhanced => {
                self.install_consciousness_package(package).await
            }
            crate::core::PackageSource::Custom(_) => {
                self.install_custom_package(package).await
            }
        }
    }
    
    async fn install_synos_package(&self, package: &Package) -> crate::Result<()> {
        self.update_task_status(&package.name, PackageStatus::Downloading, 10.0).await;
        
        // Download package
        let package_file = self.download_package(package).await?;
        
        self.update_task_status(&package.name, PackageStatus::Downloaded, 50.0).await;
        
        // Verify checksum
        self.verify_package_integrity(&package_file, &package.checksum).await?;
        
        self.update_task_status(&package.name, PackageStatus::Installing, 70.0).await;
        
        // Extract and install
        self.extract_and_install_synos_package(&package_file, package).await?;
        
        self.update_task_status(&package.name, PackageStatus::Installing, 90.0).await;
        
        // Run install script if present
        if let Some(ref script) = package.install_script {
            self.run_install_script(script, package).await?;
        }
        
        Ok(())
    }
    
    async fn install_apt_package(&self, package: &Package) -> crate::Result<()> {
        let output = Command::new("apt-get")
            .args(&["install", "-y", &package.name])
            .output()
            .await?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(crate::PackageManagerError::InstallationFailed {
                package: package.name.clone(),
                reason: format!("apt-get failed: {}", stderr),
            });
        }
        
        Ok(())
    }
    
    async fn install_pacman_package(&self, package: &Package) -> crate::Result<()> {
        let output = Command::new("pacman")
            .args(&["-S", "--noconfirm", &package.name])
            .output()
            .await?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(crate::PackageManagerError::InstallationFailed {
                package: package.name.clone(),
                reason: format!("pacman failed: {}", stderr),
            });
        }
        
        Ok(())
    }
    
    async fn install_flatpak_package(&self, package: &Package) -> crate::Result<()> {
        let output = Command::new("flatpak")
            .args(&["install", "-y", &package.name])
            .output()
            .await?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(crate::PackageManagerError::InstallationFailed {
                package: package.name.clone(),
                reason: format!("flatpak failed: {}", stderr),
            });
        }
        
        Ok(())
    }
    
    async fn install_snap_package(&self, package: &Package) -> crate::Result<()> {
        let output = Command::new("snap")
            .args(&["install", &package.name])
            .output()
            .await?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(crate::PackageManagerError::InstallationFailed {
                package: package.name.clone(),
                reason: format!("snap failed: {}", stderr),
            });
        }
        
        Ok(())
    }
    
    async fn install_consciousness_package(&self, package: &Package) -> crate::Result<()> {
        // Special handling for consciousness-enhanced packages
        tracing::info!("Installing consciousness-enhanced package: {}", package.name);
        
        // TODO: Implement consciousness-specific installation logic
        // This might involve AI model deployment, neural network setup, etc.
        
        Ok(())
    }
    
    async fn install_custom_package(&self, package: &Package) -> crate::Result<()> {
        // Custom package installation logic
        tracing::warn!("Installing custom package with default handler: {}", package.name);
        
        if let Some(ref script) = package.install_script {
            self.run_install_script(script, package).await?;
        }
        
        Ok(())
    }
    
    async fn download_package(&self, package: &Package) -> crate::Result<PathBuf> {
        // Mock download for now
        let download_path = PathBuf::from(&self.config.download_dir)
            .join(format!("{}_{}.pkg", package.name, package.version));
        
        // Create empty file for testing
        tokio::fs::write(&download_path, b"mock package data").await?;
        
        Ok(download_path)
    }
    
    async fn verify_package_integrity(&self, _file: &PathBuf, _expected_checksum: &str) -> crate::Result<()> {
        // TODO: Implement actual checksum verification
        Ok(())
    }
    
    async fn extract_and_install_synos_package(&self, _file: &PathBuf, _package: &Package) -> crate::Result<()> {
        // TODO: Implement package extraction and installation
        Ok(())
    }
    
    async fn run_install_script(&self, script: &str, package: &Package) -> crate::Result<()> {
        let output = Command::new("sh")
            .arg("-c")
            .arg(script)
            .env("PACKAGE_NAME", &package.name)
            .env("PACKAGE_VERSION", &package.version)
            .output()
            .await?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(crate::PackageManagerError::InstallationFailed {
                package: package.name.clone(),
                reason: format!("Install script failed: {}", stderr),
            });
        }
        
        Ok(())
    }
    
    async fn update_task_status(&self, package_name: &str, status: PackageStatus, progress: f32) {
        if let Some(task) = self.active_installations.write().await.get_mut(package_name) {
            task.status = status;
            task.progress = progress;
        }
    }
    
    async fn record_installation(&self, package: &Package) -> crate::Result<()> {
        let pool = self.database.lock().await;
        
        sqlx::query(r#"
            INSERT OR REPLACE INTO installed_packages 
            (name, version, source, size_bytes, checksum, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        "#)
        .bind(&package.name)
        .bind(&package.version)
        .bind(package.source.as_str())
        .bind(package.size_bytes as i64)
        .bind(&package.checksum)
        .bind(serde_json::to_string(&package.metadata).unwrap_or_default())
        .execute(&*pool)
        .await?;
        
        Ok(())
    }
    
    async fn log_operation(&self, package_name: &str, operation: &str, status: &str, message: Option<&str>) -> crate::Result<()> {
        let pool = self.database.lock().await;
        
        sqlx::query(r#"
            INSERT INTO installation_log 
            (package_name, operation, status, message)
            VALUES (?, ?, ?, ?)
        "#)
        .bind(package_name)
        .bind(operation)
        .bind(status)
        .bind(message)
        .execute(&*pool)
        .await?;
        
        Ok(())
    }
    
    /// Get installation progress for a package
    pub async fn get_installation_progress(&self, package_name: &str) -> Option<f32> {
        self.active_installations.read().await
            .get(package_name)
            .map(|task| task.progress)
    }
    
    /// Check if a package is currently being installed
    pub async fn is_installing(&self, package_name: &str) -> bool {
        self.active_installations.read().await.contains_key(package_name)
    }
    
    /// Get list of all active installations
    pub async fn get_active_installations(&self) -> Vec<String> {
        self.active_installations.read().await
            .keys()
            .cloned()
            .collect()
    }
}
