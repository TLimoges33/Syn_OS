//! MISP (Malware Information Sharing Platform) Connector

use crate::{IOC, IOCType, MISPEvent, MISPAttribute, ThreatSeverity, Result, ThreatIntelError};
use reqwest::blocking::Client;
use serde_json::Value;
use chrono::{DateTime, Utc};

pub struct MISPConnector {
    base_url: String,
    api_key: String,
    client: Client,
}

impl MISPConnector {
    pub fn new(base_url: String, api_key: String) -> Self {
        Self {
            base_url,
            api_key,
            client: Client::new(),
        }
    }

    /// Fetch recent events from MISP
    pub fn fetch_events(&self, limit: usize) -> Result<Vec<MISPEvent>> {
        let url = format!("{}/events/index", self.base_url);

        let response = self.client
            .get(&url)
            .header("Authorization", &self.api_key)
            .header("Accept", "application/json")
            .query(&[("limit", limit.to_string())])
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("MISP API error: {}", response.status())
            ));
        }

        let events: Vec<Value> = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        Ok(events.into_iter()
            .filter_map(|e| self.parse_event(e).ok())
            .collect())
    }

    /// Fetch specific event by ID
    pub fn fetch_event(&self, event_id: &str) -> Result<MISPEvent> {
        let url = format!("{}/events/view/{}", self.base_url, event_id);

        let response = self.client
            .get(&url)
            .header("Authorization", &self.api_key)
            .header("Accept", "application/json")
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("MISP API error: {}", response.status())
            ));
        }

        let event: Value = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        self.parse_event(event)
    }

    fn parse_event(&self, value: Value) -> Result<MISPEvent> {
        let event = value.get("Event")
            .ok_or_else(|| ThreatIntelError::ApiError("Invalid event format".to_string()))?;

        let id = event.get("id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let info = event.get("info")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let threat_level_id = event.get("threat_level_id")
            .and_then(|v| v.as_str())
            .and_then(|s| s.parse::<u8>().ok())
            .unwrap_or(3);

        let published = event.get("published")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);

        let timestamp = event.get("timestamp")
            .and_then(|v| v.as_str())
            .and_then(|s| s.parse::<i64>().ok())
            .map(|ts| DateTime::from_timestamp(ts, 0).unwrap_or_else(Utc::now))
            .unwrap_or_else(Utc::now);

        let attributes = event.get("Attribute")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|a| self.parse_attribute(a).ok())
                    .collect()
            })
            .unwrap_or_default();

        Ok(MISPEvent {
            id,
            info,
            threat_level_id,
            published,
            timestamp,
            attributes,
        })
    }

    fn parse_attribute(&self, value: &Value) -> Result<MISPAttribute> {
        Ok(MISPAttribute {
            id: value.get("id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            event_id: value.get("event_id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            category: value.get("category")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            attribute_type: value.get("type")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            value: value.get("value")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            to_ids: value.get("to_ids")
                .and_then(|v| v.as_bool())
                .unwrap_or(false),
        })
    }

    /// Convert MISP event to IOCs
    pub fn event_to_iocs(&self, event: &MISPEvent) -> Vec<IOC> {
        event.attributes.iter()
            .filter_map(|attr| {
                if !attr.to_ids {
                    return None;
                }

                let ioc_type = match attr.attribute_type.as_str() {
                    "ip-src" | "ip-dst" => IOCType::IPAddress,
                    "domain" | "hostname" => IOCType::Domain,
                    "url" => IOCType::URL,
                    "md5" | "sha1" | "sha256" => IOCType::FileHash,
                    "email-src" | "email-dst" => IOCType::EmailAddress,
                    "mutex" => IOCType::Mutex,
                    "regkey" => IOCType::RegistryKey,
                    "vulnerability" => IOCType::CVE,
                    _ => return None,
                };

                let severity = match event.threat_level_id {
                    1 => ThreatSeverity::High,
                    2 => ThreatSeverity::Medium,
                    3 => ThreatSeverity::Low,
                    4 => ThreatSeverity::Info,
                    _ => ThreatSeverity::Medium,
                };

                let mut ioc = IOC::new(ioc_type, attr.value.clone(), "MISP".to_string());
                ioc.severity = severity;
                ioc.description = event.info.clone();
                ioc.first_seen = event.timestamp;
                ioc.last_seen = event.timestamp;

                Some(ioc)
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_misp_connector_creation() {
        let connector = MISPConnector::new(
            "https://misp.local".to_string(),
            "test-api-key".to_string()
        );
        assert_eq!(connector.base_url, "https://misp.local");
    }
}
