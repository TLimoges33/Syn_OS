//! abuse.ch Feed Connector (URLhaus, Feodo, SSL Blacklist)

use crate::{IOC, IOCType, AbuseCHEntry, ThreatSeverity, Result, ThreatIntelError};
use reqwest::blocking::Client;
use chrono::{DateTime, Utc};

pub struct AbuseCHConnector {
    client: Client,
}

impl AbuseCHConnector {
    pub fn new() -> Self {
        Self {
            client: Client::new(),
        }
    }

    /// Fetch URLhaus recent URLs
    pub fn fetch_urlhaus_recent(&self, limit: usize) -> Result<Vec<AbuseCHEntry>> {
        let url = "https://urlhaus-api.abuse.ch/v1/urls/recent/";

        let response = self.client
            .get(url)
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("URLhaus API error: {}", response.status())
            ));
        }

        let data: serde_json::Value = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        let urls = data.get("urls")
            .and_then(|v| v.as_array())
            .ok_or_else(|| ThreatIntelError::ApiError("Invalid URLhaus response".to_string()))?;

        Ok(urls.iter()
            .take(limit)
            .filter_map(|u| self.parse_urlhaus_entry(u).ok())
            .collect())
    }

    /// Query URLhaus for specific URL
    pub fn query_urlhaus_url(&self, url: &str) -> Result<Option<AbuseCHEntry>> {
        let api_url = "https://urlhaus-api.abuse.ch/v1/url/";

        let response = self.client
            .post(api_url)
            .form(&[("url", url)])
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("URLhaus API error: {}", response.status())
            ));
        }

        let data: serde_json::Value = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if data.get("query_status").and_then(|v| v.as_str()) == Some("ok") {
            self.parse_urlhaus_entry(&data).map(Some)
        } else {
            Ok(None)
        }
    }

    /// Fetch Feodo Tracker C2 servers
    pub fn fetch_feodo_c2(&self) -> Result<Vec<AbuseCHEntry>> {
        let url = "https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.json";

        let response = self.client
            .get(url)
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("Feodo API error: {}", response.status())
            ));
        }

        let data: serde_json::Value = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        let c2_list = data.as_array()
            .ok_or_else(|| ThreatIntelError::ApiError("Invalid Feodo response".to_string()))?;

        Ok(c2_list.iter()
            .filter_map(|c2| self.parse_feodo_entry(c2).ok())
            .collect())
    }

    /// Fetch SSL Blacklist certificates
    pub fn fetch_ssl_blacklist(&self) -> Result<Vec<AbuseCHEntry>> {
        let url = "https://sslbl.abuse.ch/blacklist/sslblacklist.json";

        let response = self.client
            .get(url)
            .send()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(ThreatIntelError::ApiError(
                format!("SSL Blacklist API error: {}", response.status())
            ));
        }

        let data: Vec<serde_json::Value> = response.json()
            .map_err(|e| ThreatIntelError::ApiError(e.to_string()))?;

        Ok(data.iter()
            .filter_map(|cert| self.parse_ssl_entry(cert).ok())
            .collect())
    }

    fn parse_urlhaus_entry(&self, value: &serde_json::Value) -> Result<AbuseCHEntry> {
        let id = value.get("id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let url = value.get("url")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let malware_family = value.get("threat")
            .and_then(|v| v.as_str())
            .map(String::from);

        let first_seen = value.get("date_added")
            .and_then(|v| v.as_str())
            .and_then(|s| DateTime::parse_from_rfc3339(s).ok())
            .map(|dt| dt.with_timezone(&Utc))
            .unwrap_or_else(Utc::now);

        let tags = value.get("tags")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|t| t.as_str().map(String::from))
                    .collect()
            })
            .unwrap_or_default();

        Ok(AbuseCHEntry {
            id,
            feed_type: "URLhaus".to_string(),
            value: url,
            malware_family,
            first_seen,
            tags,
        })
    }

    fn parse_feodo_entry(&self, value: &serde_json::Value) -> Result<AbuseCHEntry> {
        let ip = value.get("ip_address")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let malware_family = value.get("malware")
            .and_then(|v| v.as_str())
            .map(String::from);

        let first_seen = value.get("first_seen")
            .and_then(|v| v.as_str())
            .and_then(|s| DateTime::parse_from_rfc3339(s).ok())
            .map(|dt| dt.with_timezone(&Utc))
            .unwrap_or_else(Utc::now);

        Ok(AbuseCHEntry {
            id: format!("feodo-{}", ip),
            feed_type: "Feodo".to_string(),
            value: ip,
            malware_family,
            first_seen,
            tags: vec!["c2".to_string(), "botnet".to_string()],
        })
    }

    fn parse_ssl_entry(&self, value: &serde_json::Value) -> Result<AbuseCHEntry> {
        let sha1 = value.get("sha1_hash")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let malware_family = value.get("reason")
            .and_then(|v| v.as_str())
            .map(String::from);

        let first_seen = value.get("listing_date")
            .and_then(|v| v.as_str())
            .and_then(|s| DateTime::parse_from_rfc3339(s).ok())
            .map(|dt| dt.with_timezone(&Utc))
            .unwrap_or_else(Utc::now);

        Ok(AbuseCHEntry {
            id: format!("sslbl-{}", sha1),
            feed_type: "SSL Blacklist".to_string(),
            value: sha1,
            malware_family,
            first_seen,
            tags: vec!["ssl".to_string(), "certificate".to_string()],
        })
    }

    /// Convert abuse.ch entry to IOC
    pub fn entry_to_ioc(&self, entry: &AbuseCHEntry) -> IOC {
        let ioc_type = match entry.feed_type.as_str() {
            "URLhaus" => IOCType::URL,
            "Feodo" => IOCType::IPAddress,
            "SSL Blacklist" => IOCType::FileHash,
            _ => IOCType::Domain,
        };

        let mut ioc = IOC::new(ioc_type, entry.value.clone(), format!("abuse.ch/{}", entry.feed_type));
        ioc.severity = ThreatSeverity::High;
        ioc.first_seen = entry.first_seen;
        ioc.last_seen = entry.first_seen;
        ioc.tags = entry.tags.clone();
        ioc.confidence = 0.9; // abuse.ch has high confidence
        ioc.references.push("https://abuse.ch".to_string());

        if let Some(malware) = &entry.malware_family {
            ioc.description = format!("{} malware: {}", entry.feed_type, malware);
            ioc.tags.push(malware.clone());
        }

        ioc
    }
}

impl Default for AbuseCHConnector {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_abusech_connector_creation() {
        let connector = AbuseCHConnector::new();
        assert!(connector.client.get("https://example.com").build().is_ok());
    }
}
