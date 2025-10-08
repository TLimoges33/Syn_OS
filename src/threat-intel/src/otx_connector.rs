//! AlienVault OTX (Open Threat Exchange) Connector

use crate::{IOC, IOCType, OTXPulse, OTXIndicator, ThreatSeverity, Result, ThreatIntelError};
use reqwest::blocking::Client;
use serde_json::Value;
use chrono::{DateTime, Utc};

pub struct OTXConnector {
    api_key: String,
    base_url: String,
    client: Client,
}

impl OTXConnector {
    pub fn new(api_key: String) -> Self {
        Self {
            api_key,
            base_url: "https://otx.alienvault.com/api/v1".to_string(),
            client: Client::new(),
        }
    }

    /// Fetch subscribed pulses
    pub fn fetch_subscribed_pulses(&self, limit: usize) -> Result<Vec<OTXPulse>> {
        let url = format!("{}/pulses/subscribed", self.base_url);

        let response = self.client
            .get(&url)
            .header("X-OTX-API-KEY", &self.api_key)
            .query(&[("limit", limit.to_string())])
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("OTX API error: {}", response.status())
            ));
        }

        let data: Value = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        let pulses = data.get("results")
            .and_then(|v| v.as_array())
            .ok_or_else(|| ThreatIntelError::ApiError("Invalid OTX response".to_string()))?;

        Ok(pulses.iter()
            .filter_map(|p| self.parse_pulse(p).ok())
            .collect())
    }

    /// Search pulses by keyword
    pub fn search_pulses(&self, query: &str) -> Result<Vec<OTXPulse>> {
        let url = format!("{}/search/pulses", self.base_url);

        let response = self.client
            .get(&url)
            .header("X-OTX-API-KEY", &self.api_key)
            .query(&[("q", query)])
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("OTX API error: {}", response.status())
            ));
        }

        let data: Value = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        let pulses = data.get("results")
            .and_then(|v| v.as_array())
            .ok_or_else(|| ThreatIntelError::ApiError("Invalid OTX response".to_string()))?;

        Ok(pulses.iter()
            .filter_map(|p| self.parse_pulse(p).ok())
            .collect())
    }

    /// Get IP reputation
    pub fn get_ip_reputation(&self, ip: &str) -> Result<Value> {
        let url = format!("{}/indicators/IPv4/{}/general", self.base_url, ip);

        let response = self.client
            .get(&url)
            .header("X-OTX-API-KEY", &self.api_key)
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("OTX API error: {}", response.status())
            ));
        }

        response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))
    }

    /// Get domain reputation
    pub fn get_domain_reputation(&self, domain: &str) -> Result<Value> {
        let url = format!("{}/indicators/domain/{}/general", self.base_url, domain);

        let response = self.client
            .get(&url)
            .header("X-OTX-API-KEY", &self.api_key)
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("OTX API error: {}", response.status())
            ));
        }

        response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))
    }

    fn parse_pulse(&self, value: &Value) -> Result<OTXPulse> {
        let id = value.get("id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let name = value.get("name")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let description = value.get("description")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let author_name = value.get("author_name")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let created = value.get("created")
            .and_then(|v| v.as_str())
            .and_then(|s| DateTime::parse_from_rfc3339(s).ok())
            .map(|dt| dt.with_timezone(&Utc))
            .unwrap_or_else(Utc::now);

        let modified = value.get("modified")
            .and_then(|v| v.as_str())
            .and_then(|s| DateTime::parse_from_rfc3339(s).ok())
            .map(|dt| dt.with_timezone(&Utc))
            .unwrap_or_else(Utc::now);

        let indicators = value.get("indicators")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|i| self.parse_indicator(i).ok())
                    .collect()
            })
            .unwrap_or_default();

        let tags = value.get("tags")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|t| t.as_str().map(String::from))
                    .collect()
            })
            .unwrap_or_default();

        Ok(OTXPulse {
            id,
            name,
            description,
            author_name,
            created,
            modified,
            indicators,
            tags,
        })
    }

    fn parse_indicator(&self, value: &Value) -> Result<OTXIndicator> {
        Ok(OTXIndicator {
            indicator: value.get("indicator")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            indicator_type: value.get("type")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            description: value.get("description")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
        })
    }

    /// Convert OTX pulse to IOCs
    pub fn pulse_to_iocs(&self, pulse: &OTXPulse) -> Vec<IOC> {
        pulse.indicators.iter()
            .filter_map(|indicator| {
                let ioc_type = match indicator.indicator_type.as_str() {
                    "IPv4" | "IPv6" => IOCType::IPAddress,
                    "domain" | "hostname" => IOCType::Domain,
                    "URL" => IOCType::URL,
                    "FileHash-MD5" | "FileHash-SHA1" | "FileHash-SHA256" => IOCType::FileHash,
                    "email" => IOCType::EmailAddress,
                    "CVE" => IOCType::CVE,
                    "Mutex" => IOCType::Mutex,
                    _ => return None,
                };

                let mut ioc = IOC::new(ioc_type, indicator.indicator.clone(), "OTX".to_string());
                ioc.description = format!("{}: {}", pulse.name, indicator.description);
                ioc.first_seen = pulse.created;
                ioc.last_seen = pulse.modified;
                ioc.tags = pulse.tags.clone();
                ioc.references.push(format!("https://otx.alienvault.com/pulse/{}", pulse.id));
                ioc.severity = ThreatSeverity::Medium;
                ioc.confidence = 0.7;

                Some(ioc)
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_otx_connector_creation() {
        let connector = OTXConnector::new("test-api-key".to_string());
        assert_eq!(connector.base_url, "https://otx.alienvault.com/api/v1");
    }
}
