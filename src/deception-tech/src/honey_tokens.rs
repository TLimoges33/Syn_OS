//! Honey Token Generation and Management
//!
//! Creates trackable fake data elements (tokens) to detect unauthorized access

use crate::{DeceptionAsset, AssetType, Result, DeceptionError};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use base64::{Engine as _, engine::general_purpose};
use rand::Rng;

/// Honey token types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TokenType {
    APIKey,
    Password,
    DatabaseCredential,
    EncryptionKey,
    AWSAccessKey,
    JWTToken,
    Custom(String),
}

/// Honey token generator
pub struct HoneyTokenGenerator {
    tracking_domain: String,
}

impl HoneyTokenGenerator {
    pub fn new(tracking_domain: String) -> Self {
        Self { tracking_domain }
    }

    /// Generate API key honey token
    pub fn generate_api_key(&self, service_name: &str) -> Result<(String, DeceptionAsset)> {
        let token = self.generate_random_key(32);
        let trackable_token = format!("sk_live_{}", token);

        let asset = DeceptionAsset::new(
            AssetType::HoneyToken,
            format!("{}_api_key", service_name),
            format!("Fake API key for {}", service_name),
            "embedded_in_config".to_string(),
        )
        .with_metadata("token_type".to_string(), "api_key".to_string())
        .with_metadata("token_hash".to_string(), self.hash_token(&trackable_token));

        Ok((trackable_token, asset))
    }

    /// Generate database credential honey token
    pub fn generate_db_credential(&self, db_name: &str) -> Result<(String, String, DeceptionAsset)> {
        let username = format!("admin_{}", self.generate_random_string(6));
        let password = self.generate_random_password();

        let asset = DeceptionAsset::new(
            AssetType::HoneyToken,
            format!("{}_db_creds", db_name),
            format!("Fake database credentials for {}", db_name),
            "config/database.yml".to_string(),
        )
        .with_metadata("username".to_string(), username.clone())
        .with_metadata("db_name".to_string(), db_name.to_string());

        Ok((username, password, asset))
    }

    /// Generate AWS-style access key
    pub fn generate_aws_key(&self) -> Result<(String, String, DeceptionAsset)> {
        let access_key = format!("AKIA{}", self.generate_random_key(16).to_uppercase());
        let secret_key = self.generate_random_key(40);

        let asset = DeceptionAsset::new(
            AssetType::HoneyToken,
            "aws_credentials".to_string(),
            "Fake AWS access credentials".to_string(),
            "~/.aws/credentials".to_string(),
        )
        .with_metadata("access_key".to_string(), access_key.clone());

        Ok((access_key, secret_key, asset))
    }

    /// Generate JWT honey token with tracking
    pub fn generate_jwt_token(&self, subject: &str) -> Result<(String, DeceptionAsset)> {
        let header = r#"{"alg":"HS256","typ":"JWT"}"#;
        let payload = format!(
            r#"{{"sub":"{}","iss":"{}","exp":9999999999}}"#,
            subject, self.tracking_domain
        );

        let header_b64 = general_purpose::URL_SAFE_NO_PAD.encode(header.as_bytes());
        let payload_b64 = general_purpose::URL_SAFE_NO_PAD.encode(payload.as_bytes());

        // Fake signature
        let signature = self.generate_random_key(32);
        let jwt = format!("{}.{}.{}", header_b64, payload_b64, signature);

        let asset = DeceptionAsset::new(
            AssetType::HoneyToken,
            format!("jwt_{}", subject),
            format!("Fake JWT token for {}", subject),
            "stored_in_local_storage".to_string(),
        )
        .with_metadata("token_type".to_string(), "jwt".to_string())
        .with_metadata("subject".to_string(), subject.to_string());

        Ok((jwt, asset))
    }

    /// Generate encryption key honey token
    pub fn generate_encryption_key(&self, key_name: &str) -> Result<(String, DeceptionAsset)> {
        let key = self.generate_random_key(32);
        let hex_key = hex::encode(&key);

        let asset = DeceptionAsset::new(
            AssetType::HoneyToken,
            format!("enc_key_{}", key_name),
            format!("Fake encryption key: {}", key_name),
            ".env".to_string(),
        )
        .with_metadata("key_format".to_string(), "hex".to_string());

        Ok((hex_key, asset))
    }

    /// Generate trackable canary token (web beacon)
    pub fn generate_canary_token(&self, description: &str) -> Result<(String, DeceptionAsset)> {
        let token_id = self.generate_random_string(16);
        let canary_url = format!("https://{}/canary/{}.png", self.tracking_domain, token_id);

        let asset = DeceptionAsset::new(
            AssetType::HoneyToken,
            format!("canary_{}", token_id),
            description.to_string(),
            "embedded_in_document".to_string(),
        )
        .with_metadata("tracking_url".to_string(), canary_url.clone())
        .with_metadata("token_id".to_string(), token_id);

        Ok((canary_url, asset))
    }

    // Helper methods

    fn generate_random_key(&self, length: usize) -> String {
        let mut rng = rand::thread_rng();
        (0..length)
            .map(|_| format!("{:x}", rng.gen::<u8>()))
            .collect::<String>()
            .chars()
            .take(length)
            .collect()
    }

    fn generate_random_string(&self, length: usize) -> String {
        use rand::distributions::Alphanumeric;
        rand::thread_rng()
            .sample_iter(&Alphanumeric)
            .take(length)
            .map(char::from)
            .collect()
    }

    fn generate_random_password(&self) -> String {
        let mut rng = rand::thread_rng();
        let specials = "!@#$%^&*";

        format!(
            "{}{}{}{}",
            self.generate_random_string(4),
            rng.gen_range(1000..9999),
            specials.chars().nth(rng.gen_range(0..specials.len())).unwrap(),
            self.generate_random_string(3)
        )
    }

    fn hash_token(&self, token: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(token.as_bytes());
        format!("{:x}", hasher.finalize())
    }
}

/// Honey token validator (checks if token was used)
pub struct HoneyTokenValidator {
    known_tokens: std::collections::HashMap<String, uuid::Uuid>,
}

impl HoneyTokenValidator {
    pub fn new() -> Self {
        Self {
            known_tokens: std::collections::HashMap::new(),
        }
    }

    /// Register a honey token
    pub fn register_token(&mut self, token_hash: String, asset_id: uuid::Uuid) {
        self.known_tokens.insert(token_hash, asset_id);
    }

    /// Check if a token is a honey token
    pub fn is_honey_token(&self, token: &str) -> Option<uuid::Uuid> {
        let mut hasher = Sha256::new();
        hasher.update(token.as_bytes());
        let hash = format!("{:x}", hasher.finalize());

        self.known_tokens.get(&hash).copied()
    }

    /// Validate and alert on usage
    pub fn validate_token_usage(&self, token: &str) -> Option<String> {
        if let Some(asset_id) = self.is_honey_token(token) {
            Some(format!(
                "⚠️  HONEY TOKEN DETECTED! Asset ID: {} | Token used in unauthorized context",
                asset_id
            ))
        } else {
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_api_key_generation() {
        let generator = HoneyTokenGenerator::new("tracking.synos.local".to_string());
        let (token, asset) = generator.generate_api_key("stripe").unwrap();

        assert!(token.starts_with("sk_live_"));
        assert_eq!(asset.asset_type, AssetType::HoneyToken);
    }

    #[test]
    fn test_db_credential_generation() {
        let generator = HoneyTokenGenerator::new("tracking.synos.local".to_string());
        let (username, password, asset) = generator.generate_db_credential("production").unwrap();

        assert!(username.starts_with("admin_"));
        assert!(!password.is_empty());
        assert_eq!(asset.location, "config/database.yml");
    }

    #[test]
    fn test_jwt_generation() {
        let generator = HoneyTokenGenerator::new("tracking.synos.local".to_string());
        let (jwt, asset) = generator.generate_jwt_token("admin").unwrap();

        let parts: Vec<&str> = jwt.split('.').collect();
        assert_eq!(parts.len(), 3); // header.payload.signature
    }

    #[test]
    fn test_token_validation() {
        let mut validator = HoneyTokenValidator::new();
        let test_token = "sk_live_test123456";
        let asset_id = uuid::Uuid::new_v4();

        let mut hasher = Sha256::new();
        hasher.update(test_token.as_bytes());
        let hash = format!("{:x}", hasher.finalize());

        validator.register_token(hash, asset_id);

        assert!(validator.is_honey_token(test_token).is_some());
        assert!(validator.is_honey_token("different_token").is_none());
    }
}
