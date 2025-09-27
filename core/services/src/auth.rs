//! # Service Authentication Module
//! 
//! Provides JWT-based authentication and authorization for inter-service communication.

use crate::{ServiceError, ServiceResult, ServiceConfig};
use std::collections::HashMap;
use chrono::{DateTime, Utc, Duration};
use serde::{Deserialize, Serialize};
use base64::{Engine as _, engine::general_purpose};
use tracing::{info, warn, debug};

/// JWT token claims
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenClaims {
    /// Subject (service ID)
    pub sub: String,
    
    /// Issued at timestamp
    pub iat: i64,
    
    /// Expiration timestamp
    pub exp: i64,
    
    /// Issuer
    pub iss: String,
    
    /// Audience
    pub aud: String,
    
    /// Service name
    pub service_name: String,
    
    /// Service version
    pub version: String,
    
    /// Permissions/scopes
    pub scopes: Vec<String>,
    
    /// Custom claims
    pub custom: HashMap<String, serde_json::Value>,
}

impl TokenClaims {
    /// Create new token claims
    pub fn new(
        service_id: String,
        service_name: String,
        version: String,
        scopes: Vec<String>,
        validity_duration: Duration,
    ) -> Self {
        let now = Utc::now();
        
        Self {
            sub: service_id,
            iat: now.timestamp(),
            exp: (now + validity_duration).timestamp(),
            iss: "synos-auth".to_string(),
            aud: "synos-services".to_string(),
            service_name,
            version,
            scopes,
            custom: HashMap::new(),
        }
    }

    /// Check if token is expired
    pub fn is_expired(&self) -> bool {
        Utc::now().timestamp() > self.exp
    }

    /// Check if token has a specific scope
    pub fn has_scope(&self, scope: &str) -> bool {
        self.scopes.contains(&scope.to_string())
    }

    /// Add custom claim
    pub fn add_custom_claim(mut self, key: String, value: serde_json::Value) -> Self {
        self.custom.insert(key, value);
        self
    }
}

/// Authentication token
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthToken {
    /// JWT token string
    pub token: String,
    
    /// Token type (Bearer)
    pub token_type: String,
    
    /// Expiration timestamp
    pub expires_at: DateTime<Utc>,
    
    /// Token scopes
    pub scopes: Vec<String>,
}

impl AuthToken {
    /// Create new auth token
    pub fn new(token: String, claims: &TokenClaims) -> Self {
        Self {
            token,
            token_type: "Bearer".to_string(),
            expires_at: DateTime::from_timestamp(claims.exp, 0).unwrap_or_else(Utc::now),
            scopes: claims.scopes.clone(),
        }
    }

    /// Check if token is expired
    pub fn is_expired(&self) -> bool {
        Utc::now() > self.expires_at
    }

    /// Get authorization header value
    pub fn authorization_header(&self) -> String {
        format!("{} {}", self.token_type, self.token)
    }
}

/// Service authentication manager
#[derive(Clone)]
pub struct ServiceAuth {
    config: ServiceConfig,
    signing_key: String,
    current_token: std::sync::Arc<tokio::sync::RwLock<Option<AuthToken>>>,
    token_refresh_task: std::sync::Arc<tokio::sync::RwLock<Option<tokio::task::JoinHandle<()>>>>,
}

impl ServiceAuth {
    /// Create new service authentication manager
    pub fn new(config: ServiceConfig, signing_key: String) -> Self {
        Self {
            config,
            signing_key,
            current_token: std::sync::Arc::new(tokio::sync::RwLock::new(None)),
            token_refresh_task: std::sync::Arc::new(tokio::sync::RwLock::new(None)),
        }
    }

    /// Generate a JWT token for this service
    pub async fn generate_token(&self, scopes: Vec<String>) -> ServiceResult<AuthToken> {
        let validity_duration = Duration::hours(1); // 1 hour validity
        
        let claims = TokenClaims::new(
            self.config.service_id.clone(),
            self.config.service_name.clone(),
            self.config.version.clone(),
            scopes,
            validity_duration,
        );

        // In a real implementation, you would use a proper JWT library like `jsonwebtoken`
        // For now, we'll create a simple base64-encoded token (NOT SECURE FOR PRODUCTION)
        let token_payload = serde_json::to_string(&claims)?;
        let token = general_purpose::URL_SAFE.encode(token_payload.as_bytes());

        info!("Generated JWT token for service: {}", self.config.service_id);
        
        Ok(AuthToken::new(token, &claims))
    }

    /// Validate and decode a JWT token
    pub async fn validate_token(&self, token: &str) -> ServiceResult<TokenClaims> {
        // In a real implementation, you would use proper JWT validation
        // For now, we'll do simple base64 decoding (NOT SECURE FOR PRODUCTION)
        let decoded = general_purpose::URL_SAFE.decode(token)
            .map_err(|_| ServiceError::AuthError("Invalid token format".to_string()))?;
        
        let token_payload = String::from_utf8(decoded)
            .map_err(|_| ServiceError::AuthError("Invalid token encoding".to_string()))?;
        
        let claims: TokenClaims = serde_json::from_str(&token_payload)?;
        
        // Check expiration
        if claims.is_expired() {
            return Err(ServiceError::AuthError("Token expired".to_string()));
        }

        debug!("Validated token for service: {}", claims.sub);
        
        Ok(claims)
    }

    /// Get current authentication token (generate if needed)
    pub async fn get_current_token(&self) -> ServiceResult<AuthToken> {
        let token = self.current_token.read().await;
        
        if let Some(ref token) = *token {
            if !token.is_expired() {
                return Ok(token.clone());
            }
        }
        
        drop(token); // Release read lock

        // Generate new token
        let scopes = vec![
            "service:read".to_string(),
            "service:write".to_string(),
            "events:publish".to_string(),
            "events:subscribe".to_string(),
        ];
        
        let new_token = self.generate_token(scopes).await?;
        
        // Store new token
        {
            let mut token = self.current_token.write().await;
            *token = Some(new_token.clone());
        }

        info!("Generated new current token for service: {}", self.config.service_id);
        
        Ok(new_token)
    }

    /// Start automatic token refresh
    pub async fn start_token_refresh(&self) -> ServiceResult<()> {
        let config = self.config.clone();
        let current_token = self.current_token.clone();
        let signing_key = self.signing_key.clone();

        let task = tokio::spawn(async move {
            let mut interval = tokio::time::interval(std::time::Duration::from_secs(30 * 60)); // Refresh every 30 minutes
            
            loop {
                interval.tick().await;

                // Check if current token needs refresh (refresh when 10 minutes left)
                let needs_refresh = {
                    let token = current_token.read().await;
                    match token.as_ref() {
                        Some(token) => {
                            let time_left = token.expires_at - Utc::now();
                            time_left.num_minutes() < 10
                        }
                        None => true,
                    }
                };

                if needs_refresh {
                    // Create a temporary auth instance for token generation
                    let temp_auth = ServiceAuth::new(config.clone(), signing_key.clone());
                    
                    match temp_auth.generate_token(vec![
                        "service:read".to_string(),
                        "service:write".to_string(),
                        "events:publish".to_string(),
                        "events:subscribe".to_string(),
                    ]).await {
                        Ok(new_token) => {
                            let mut token = current_token.write().await;
                            *token = Some(new_token);
                            info!("Refreshed authentication token for service: {}", config.service_id);
                        }
                        Err(e) => {
                            warn!("Failed to refresh token: {}", e);
                        }
                    }
                }
            }
        });

        let mut refresh_task = self.token_refresh_task.write().await;
        *refresh_task = Some(task);

        info!("Started token refresh task for service: {}", self.config.service_id);
        
        Ok(())
    }

    /// Stop automatic token refresh
    pub async fn stop_token_refresh(&self) {
        let mut refresh_task = self.token_refresh_task.write().await;
        if let Some(task) = refresh_task.take() {
            task.abort();
            info!("Stopped token refresh task");
        }
    }

    /// Create authentication middleware for requests
    pub async fn create_auth_header(&self) -> ServiceResult<String> {
        let token = self.get_current_token().await?;
        Ok(token.authorization_header())
    }

    /// Authorize a request with required scopes
    pub async fn authorize_request(&self, token: &str, required_scopes: &[String]) -> ServiceResult<TokenClaims> {
        let claims = self.validate_token(token).await?;
        
        // Check if token has all required scopes
        for scope in required_scopes {
            if !claims.has_scope(scope) {
                return Err(ServiceError::AuthError(
                    format!("Missing required scope: {}", scope)
                ));
            }
        }

        debug!("Authorized request for service: {} with scopes: {:?}", claims.sub, required_scopes);
        
        Ok(claims)
    }

    /// Get authentication statistics
    pub async fn get_stats(&self) -> HashMap<String, serde_json::Value> {
        let mut stats = HashMap::new();
        
        let token = self.current_token.read().await;
        
        stats.insert("service_id".to_string(), self.config.service_id.clone().into());
        stats.insert("has_current_token".to_string(), token.is_some().into());
        
        if let Some(ref token) = *token {
            stats.insert("token_expires_at".to_string(), token.expires_at.to_rfc3339().into());
            stats.insert("token_expired".to_string(), token.is_expired().into());
            stats.insert("token_scopes".to_string(), serde_json::to_value(&token.scopes).unwrap());
            
            let time_until_expiry = token.expires_at - Utc::now();
            stats.insert("minutes_until_expiry".to_string(), time_until_expiry.num_minutes().into());
        }

        stats
    }

    /// Revoke current token
    pub async fn revoke_current_token(&self) {
        let mut token = self.current_token.write().await;
        *token = None;
        info!("Revoked current token for service: {}", self.config.service_id);
    }
}

impl Drop for ServiceAuth {
    fn drop(&mut self) {
        // Stop token refresh on drop (best effort)
        if let Ok(rt) = tokio::runtime::Handle::try_current() {
            let auth = self.clone();
            rt.spawn(async move {
                auth.stop_token_refresh().await;
            });
        }
    }
}

/// Authentication middleware for extracting and validating tokens from requests
pub struct AuthMiddleware {
    auth: ServiceAuth,
}

impl AuthMiddleware {
    /// Create new authentication middleware
    pub fn new(auth: ServiceAuth) -> Self {
        Self { auth }
    }

    /// Extract token from authorization header
    pub fn extract_token_from_header(&self, auth_header: &str) -> ServiceResult<String> {
        if !auth_header.starts_with("Bearer ") {
            return Err(ServiceError::AuthError("Invalid authorization header format".to_string()));
        }

        let token = auth_header.strip_prefix("Bearer ").unwrap_or("").trim();
        
        if token.is_empty() {
            return Err(ServiceError::AuthError("Missing token in authorization header".to_string()));
        }

        Ok(token.to_string())
    }

    /// Validate request with required permissions
    pub async fn validate_request(
        &self,
        auth_header: &str,
        required_scopes: &[String],
    ) -> ServiceResult<TokenClaims> {
        let token = self.extract_token_from_header(auth_header)?;
        self.auth.authorize_request(&token, required_scopes).await
    }
}

// Helper function to create default scopes
pub fn default_service_scopes() -> Vec<String> {
    vec![
        "service:read".to_string(),
        "service:write".to_string(),
        "events:publish".to_string(),
        "events:subscribe".to_string(),
        "health:read".to_string(),
    ]
}

pub fn admin_service_scopes() -> Vec<String> {
    vec![
        "service:read".to_string(),
        "service:write".to_string(),
        "service:admin".to_string(),
        "events:publish".to_string(),
        "events:subscribe".to_string(),
        "health:read".to_string(),
        "health:write".to_string(),
        "metrics:read".to_string(),
        "config:read".to_string(),
        "config:write".to_string(),
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_token_claims_creation() {
        let claims = TokenClaims::new(
            "test-service".to_string(),
            "Test Service".to_string(),
            "1.0.0".to_string(),
            vec!["read".to_string(), "write".to_string()],
            Duration::hours(1),
        );

        assert_eq!(claims.sub, "test-service");
        assert_eq!(claims.service_name, "Test Service");
        assert!(claims.has_scope("read"));
        assert!(claims.has_scope("write"));
        assert!(!claims.has_scope("admin"));
        assert!(!claims.is_expired());
    }

    #[tokio::test]
    async fn test_service_auth_token_generation() {
        let config = ServiceConfig::default();
        let auth = ServiceAuth::new(config, "test-key".to_string());

        let token = auth.generate_token(vec!["test".to_string()]).await.unwrap();
        
        assert_eq!(token.token_type, "Bearer");
        assert!(!token.is_expired());
        assert!(token.scopes.contains(&"test".to_string()));
    }

    #[test]
    fn test_auth_middleware_token_extraction() {
        let config = ServiceConfig::default();
        let auth = ServiceAuth::new(config, "test-key".to_string());
        let middleware = AuthMiddleware::new(auth);

        let token = middleware.extract_token_from_header("Bearer abc123").unwrap();
        assert_eq!(token, "abc123");

        let result = middleware.extract_token_from_header("Invalid header");
        assert!(result.is_err());
    }

    #[test]
    fn test_default_scopes() {
        let scopes = default_service_scopes();
        assert!(scopes.contains(&"service:read".to_string()));
        assert!(scopes.contains(&"events:publish".to_string()));

        let admin_scopes = admin_service_scopes();
        assert!(admin_scopes.contains(&"service:admin".to_string()));
        assert!(admin_scopes.contains(&"config:write".to_string()));
    }
}
