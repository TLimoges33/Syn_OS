/// Vulnerable Applications for Educational Labs
/// Pre-configured vulnerable apps for hands-on practice

use alloc::vec::Vec;
use alloc::collections::BTreeMap;
use alloc::string::String;

/// Vulnerable application types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VulnerableAppType {
    DVWA,           // Damn Vulnerable Web Application
    WebGoat,        // OWASP WebGoat
    JuiceShop,      // OWASP Juice Shop
    VulnHub,        // VulnHub VMs
    HackTheBox,     // HTB-style challenges
    Custom,         // Custom vulnerable apps
}

/// Vulnerability categories
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VulnerabilityCategory {
    SQLInjection,
    XSS,
    CSRF,
    CommandInjection,
    PathTraversal,
    AuthenticationBypass,
    SessionManagement,
    InsecureDeserialization,
}

/// Vulnerable application
#[derive(Debug, Clone)]
pub struct VulnerableApp {
    pub app_id: u64,
    pub app_type: VulnerableAppType,
    pub name: String,
    pub description: String,
    pub vulnerabilities: Vec<VulnerabilityCategory>,
    pub difficulty: super::DifficultyLevel,
    pub port: u16,
    pub credentials: Option<(String, String)>, // (username, password)
}

/// Vulnerable apps manager
pub struct VulnerableAppsManager {
    apps: BTreeMap<u64, VulnerableApp>,
    deployed_apps: BTreeMap<u64, u64>, // sandbox_id -> app_id
    next_app_id: u64,
}

impl VulnerableAppsManager {
    pub fn new() -> Self {
        let mut manager = Self {
            apps: BTreeMap::new(),
            deployed_apps: BTreeMap::new(),
            next_app_id: 1,
        };

        manager.register_default_apps();
        manager
    }

    /// Register default vulnerable applications
    fn register_default_apps(&mut self) {
        // DVWA-like app
        self.register_app(VulnerableApp {
            app_id: self.next_app_id,
            app_type: VulnerableAppType::DVWA,
            name: "SQL Injection Practice".into(),
            description: "Basic SQL injection vulnerabilities".into(),
            vulnerabilities: vec![
                VulnerabilityCategory::SQLInjection,
                VulnerabilityCategory::AuthenticationBypass,
            ],
            difficulty: super::DifficultyLevel::Beginner,
            port: 8080,
            credentials: Some(("admin".into(), "password".into())),
        });
        self.next_app_id += 1;

        // WebGoat-like app
        self.register_app(VulnerableApp {
            app_id: self.next_app_id,
            app_type: VulnerableAppType::WebGoat,
            name: "XSS Playground".into(),
            description: "Cross-site scripting vulnerabilities".into(),
            vulnerabilities: vec![
                VulnerabilityCategory::XSS,
                VulnerabilityCategory::CSRF,
            ],
            difficulty: super::DifficultyLevel::Intermediate,
            port: 8081,
            credentials: Some(("user".into(), "user123".into())),
        });
        self.next_app_id += 1;

        // Advanced command injection app
        self.register_app(VulnerableApp {
            app_id: self.next_app_id,
            app_type: VulnerableAppType::Custom,
            name: "Command Injection Lab".into(),
            description: "OS command injection vulnerabilities".into(),
            vulnerabilities: vec![
                VulnerabilityCategory::CommandInjection,
                VulnerabilityCategory::PathTraversal,
            ],
            difficulty: super::DifficultyLevel::Advanced,
            port: 8082,
            credentials: None,
        });
        self.next_app_id += 1;
    }

    /// Register vulnerable app
    fn register_app(&mut self, app: VulnerableApp) {
        self.apps.insert(app.app_id, app);
    }

    /// Deploy app in sandbox
    pub fn deploy_app(&mut self, sandbox_id: u64, app_id: u64) -> Result<(), &'static str> {
        // Verify app exists
        let _app = self.apps.get(&app_id)
            .ok_or("App not found")?;

        // Deploy to sandbox
        self.deployed_apps.insert(sandbox_id, app_id);

        // Real implementation would:
        // 1. Start Docker container or VM
        // 2. Configure networking
        // 3. Initialize database
        // 4. Set up monitoring

        Ok(())
    }

    /// Undeploy app from sandbox
    pub fn undeploy_app(&mut self, sandbox_id: u64) -> Result<(), &'static str> {
        self.deployed_apps.remove(&sandbox_id)
            .ok_or("No app deployed in sandbox")?;

        // Real implementation would:
        // 1. Stop container/VM
        // 2. Clean up resources
        // 3. Remove network configuration

        Ok(())
    }

    /// Get app by ID
    pub fn get_app(&self, app_id: u64) -> Option<&VulnerableApp> {
        self.apps.get(&app_id)
    }

    /// Get apps by difficulty
    pub fn get_apps_by_difficulty(&self, difficulty: super::DifficultyLevel) -> Vec<&VulnerableApp> {
        self.apps.values()
            .filter(|app| app.difficulty == difficulty)
            .collect()
    }

    /// Get apps by vulnerability type
    pub fn get_apps_by_vulnerability(&self, vuln_type: VulnerabilityCategory) -> Vec<&VulnerableApp> {
        self.apps.values()
            .filter(|app| app.vulnerabilities.contains(&vuln_type))
            .collect()
    }

    /// Get deployed app for sandbox
    pub fn get_deployed_app(&self, sandbox_id: u64) -> Option<&VulnerableApp> {
        if let Some(app_id) = self.deployed_apps.get(&sandbox_id) {
            self.apps.get(app_id)
        } else {
            None
        }
    }

    /// List all available apps
    pub fn list_apps(&self) -> Vec<&VulnerableApp> {
        self.apps.values().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_registration() {
        let manager = VulnerableAppsManager::new();
        assert!(manager.apps.len() >= 3); // At least default apps
    }

    #[test]
    fn test_app_deployment() {
        let mut manager = VulnerableAppsManager::new();

        let app_id = 1;
        let sandbox_id = 100;

        assert!(manager.deploy_app(sandbox_id, app_id).is_ok());
        assert!(manager.get_deployed_app(sandbox_id).is_some());
    }

    #[test]
    fn test_app_filtering() {
        let manager = VulnerableAppsManager::new();

        let beginner_apps = manager.get_apps_by_difficulty(super::DifficultyLevel::Beginner);
        assert!(beginner_apps.len() > 0);

        let sql_apps = manager.get_apps_by_vulnerability(VulnerabilityCategory::SQLInjection);
        assert!(sql_apps.len() > 0);
    }

    #[test]
    fn test_app_undeployment() {
        let mut manager = VulnerableAppsManager::new();

        let sandbox_id = 100;
        manager.deploy_app(sandbox_id, 1).unwrap();

        assert!(manager.undeploy_app(sandbox_id).is_ok());
        assert!(manager.get_deployed_app(sandbox_id).is_none());
    }
}
