//! SIEM Integration Layer
//!
//! Connectors for Splunk, Microsoft Sentinel, QRadar, and custom SOAR platforms

#![no_std]

extern crate alloc;

pub mod http_client;
pub mod splunk_bridge;
pub mod sentinel_bridge;
pub mod qradar_bridge;
pub mod custom_soar;

use alloc::string::String;
use alloc::vec::Vec;

/// SIEM event
#[derive(Debug, Clone)]
pub struct SIEMEvent {
    pub event_id: String,
    pub timestamp: u64,
    pub source: String,
    pub event_type: EventType,
    pub severity: EventSeverity,
    pub details: String,
    pub raw_data: Vec<u8>,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum EventType {
    SecurityAlert,
    ThreatDetection,
    ComplianceViolation,
    SystemAnomaly,
    UserActivity,
    NetworkEvent,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum EventSeverity {
    Info,
    Low,
    Medium,
    High,
    Critical,
}

/// SIEM connector trait
pub trait SIEMConnector {
    /// Send event to SIEM platform
    fn send_event(&mut self, event: &SIEMEvent) -> Result<(), &'static str>;

    /// Query events from SIEM
    fn query_events(&self, query: &str) -> Result<Vec<SIEMEvent>, &'static str>;

    /// Get connector status
    fn is_connected(&self) -> bool;

    /// Get connector name
    fn name(&self) -> &str;
}

/// SIEM orchestrator for managing multiple connectors
pub struct SIEMOrchestrator {
    connectors: Vec<Box<dyn SIEMConnector>>,
    event_buffer: Vec<SIEMEvent>,
}

impl SIEMOrchestrator {
    /// Create new SIEM orchestrator
    pub fn new() -> Self {
        Self {
            connectors: Vec::new(),
            event_buffer: Vec::new(),
        }
    }

    /// Add SIEM connector
    pub fn add_connector(&mut self, connector: Box<dyn SIEMConnector>) {
        self.connectors.push(connector);
    }

    /// Send event to all connected SIEMs
    pub fn broadcast_event(&mut self, event: SIEMEvent) -> Result<(), &'static str> {
        self.event_buffer.push(event.clone());

        for connector in &mut self.connectors {
            if connector.is_connected() {
                connector.send_event(&event)?;
            }
        }

        Ok(())
    }

    /// Get active connectors
    pub fn get_active_connectors(&self) -> Vec<&str> {
        self.connectors.iter()
            .filter(|c| c.is_connected())
            .map(|c| c.name())
            .collect()
    }

    /// Get buffered events
    pub fn get_buffered_events(&self) -> &[SIEMEvent] {
        &self.event_buffer
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_siem_orchestrator() {
        let orchestrator = SIEMOrchestrator::new();
        assert_eq!(orchestrator.get_active_connectors().len(), 0);
    }
}
