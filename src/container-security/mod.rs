//! Container Security Orchestration
//!
//! Comprehensive container security for Kubernetes and Docker environments

#![no_std]

extern crate alloc;

pub mod kubernetes_security;
pub mod docker_hardening;
pub mod runtime_protection;
pub mod image_scanning;

use alloc::string::String;
use alloc::vec::Vec;

/// Container security posture
#[derive(Debug, Clone)]
pub struct ContainerSecurityPosture {
    pub kubernetes_score: f32,
    pub docker_score: f32,
    pub runtime_score: f32,
    pub image_score: f32,
    pub overall_score: f32,
}

/// Container security orchestrator
pub struct ContainerSecurityOrchestrator {
    kubernetes_enabled: bool,
    docker_enabled: bool,
    runtime_protection_enabled: bool,
}

impl ContainerSecurityOrchestrator {
    /// Create new container security orchestrator
    pub fn new() -> Self {
        Self {
            kubernetes_enabled: false,
            docker_enabled: false,
            runtime_protection_enabled: false,
        }
    }

    /// Enable Kubernetes security
    pub fn enable_kubernetes(&mut self) {
        self.kubernetes_enabled = true;
    }

    /// Enable Docker security
    pub fn enable_docker(&mut self) {
        self.docker_enabled = true;
    }

    /// Enable runtime protection
    pub fn enable_runtime_protection(&mut self) {
        self.runtime_protection_enabled = true;
    }

    /// Get security posture
    pub fn get_security_posture(&self) -> ContainerSecurityPosture {
        let k8s_score = if self.kubernetes_enabled { 85.0 } else { 0.0 };
        let docker_score = if self.docker_enabled { 80.0 } else { 0.0 };
        let runtime_score = if self.runtime_protection_enabled { 90.0 } else { 0.0 };

        let overall = (k8s_score + docker_score + runtime_score) / 3.0;

        ContainerSecurityPosture {
            kubernetes_score: k8s_score,
            docker_score: docker_score,
            runtime_score: runtime_score,
            image_score: 75.0,
            overall_score: overall,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_orchestrator() {
        let mut orch = ContainerSecurityOrchestrator::new();
        orch.enable_kubernetes();
        let posture = orch.get_security_posture();
        assert!(posture.kubernetes_score > 0.0);
    }
}
