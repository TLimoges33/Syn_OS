#!/usr/bin/env python3
"""
Secure JWT Authentication System for Syn_OS
Implements strong JWT token generation, validation, and management
"""

import jwt
import secrets
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import bcrypt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .config_manager import get_config, SecurityConfig

logger = logging.getLogger('synapticos.security.jwt_auth')


class TokenType(Enum):
    """JWT token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    API = "api"
    CONSCIOUSNESS = "consciousness"


class UserRole(Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    USER = "user"
    CONSCIOUSNESS = "consciousness"
    API_CLIENT = "api_client"
    READONLY = "readonly"


@dataclass
class TokenClaims:
    """JWT token claims structure"""
    user_id: str
    username: str
    roles: List[str]
    token_type: str
    issued_at: int
    expires_at: int
    jti: str  # JWT ID for revocation
    consciousness_level: Optional[float] = None
    api_permissions: Optional[List[str]] = None


@dataclass
class AuthenticationResult:
    """Authentication result"""
    success: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    roles: Optional[List[str]] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    error_message: Optional[str] = None


class JWTSecurityError(Exception):
    """JWT security related errors"""
    pass


class SecureJWTManager:
    """Secure JWT token manager with strong cryptography"""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or get_config().get_security_config()
        self.revoked_tokens: set = set()  # In production, use Redis/database
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        
        # Initialize RSA keys for stronger security
        self._initialize_keys()
        
        # Validate configuration
        self._validate_security_config()
    
    def _initialize_keys(self):
        """Initialize RSA key pair for JWT signing"""
        try:
            # Generate RSA key pair for production
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            
            # Serialize keys
            self.private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            self.public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            logger.info("RSA key pair initialized for JWT signing")
            
        except Exception as e:
            logger.error(f"Failed to initialize RSA keys: {e}")
            # Fallback to HMAC with strong secret
            self.private_key = None
            self.public_key = None
    
    def _validate_security_config(self):
        """Validate security configuration"""
        if len(self.config.jwt_secret_key) < 32:
            raise JWTSecurityError("JWT secret key must be at least 32 characters")
        
        if self.config.jwt_algorithm not in ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']:
            raise JWTSecurityError(f"Unsupported JWT algorithm: {self.config.jwt_algorithm}")
        
        logger.info("JWT security configuration validated")
    
    def _get_signing_key(self) -> str:
        """Get the appropriate signing key based on algorithm"""
        if self.config.jwt_algorithm.startswith('RS') and self.private_key:
            return self.private_pem.decode('utf-8')
        else:
            return self.config.jwt_secret_key
    
    def _get_verification_key(self) -> str:
        """Get the appropriate verification key based on algorithm"""
        if self.config.jwt_algorithm.startswith('RS') and self.public_key:
            return self.public_pem.decode('utf-8')
        else:
            return self.config.jwt_secret_key
    
    def _check_rate_limiting(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        if identifier not in self.failed_attempts:
            return True
        
        # Clean old attempts
        cutoff_time = datetime.now() - self.lockout_duration
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if attempt > cutoff_time
        ]
        
        # Check if still locked out
        if len(self.failed_attempts[identifier]) >= self.max_failed_attempts:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        return True
    
    def _record_failed_attempt(self, identifier: str):
        """Record a failed authentication attempt"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(datetime.now())
        logger.warning(f"Failed authentication attempt recorded for {identifier}")
    
    def _generate_jti(self) -> str:
        """Generate a unique JWT ID"""
        return secrets.token_urlsafe(16)
    
    def create_access_token(
        self,
        user_id: str,
        username: str,
        roles: List[str],
        consciousness_level: Optional[float] = None,
        api_permissions: Optional[List[str]] = None
    ) -> str:
        """Create a secure access token"""
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(hours=self.config.jwt_expiration_hours)
            jti = self._generate_jti()
            
            claims = TokenClaims(
                user_id=user_id,
                username=username,
                roles=roles,
                token_type=TokenType.ACCESS.value,
                issued_at=int(now.timestamp()),
                expires_at=int(expires_at.timestamp()),
                jti=jti,
                consciousness_level=consciousness_level,
                api_permissions=api_permissions
            )
            
            # Create JWT payload
            payload = asdict(claims)
            payload.update({
                'iat': claims.issued_at,
                'exp': claims.expires_at,
                'iss': 'syn_os_auth',
                'aud': 'syn_os_api'
            })
            
            # Sign token
            signing_key = self._get_signing_key()
            token = jwt.encode(
                payload,
                signing_key,
                algorithm=self.config.jwt_algorithm
            )
            
            logger.info(f"Access token created for user {username} (ID: {user_id})")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise JWTSecurityError(f"Token creation failed: {e}")
    
    def create_refresh_token(self, user_id: str, username: str) -> str:
        """Create a secure refresh token"""
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(days=self.config.jwt_refresh_expiration_days)
            jti = self._generate_jti()
            
            payload = {
                'user_id': user_id,
                'username': username,
                'token_type': TokenType.REFRESH.value,
                'iat': int(now.timestamp()),
                'exp': int(expires_at.timestamp()),
                'jti': jti,
                'iss': 'syn_os_auth',
                'aud': 'syn_os_refresh'
            }
            
            signing_key = self._get_signing_key()
            token = jwt.encode(
                payload,
                signing_key,
                algorithm=self.config.jwt_algorithm
            )
            
            logger.info(f"Refresh token created for user {username}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise JWTSecurityError(f"Refresh token creation failed: {e}")
    
    def verify_token(self, token: str, token_type: Optional[TokenType] = None) -> TokenClaims:
        """Verify and decode a JWT token"""
        try:
            # Decode token
            verification_key = self._get_verification_key()
            payload = jwt.decode(
                token,
                verification_key,
                algorithms=[self.config.jwt_algorithm],
                audience=['syn_os_api', 'syn_os_refresh'],
                issuer='syn_os_auth'
            )
            
            # Check if token is revoked
            jti = payload.get('jti')
            if jti and jti in self.revoked_tokens:
                raise JWTSecurityError("Token has been revoked")
            
            # Validate token type if specified
            if token_type and payload.get('token_type') != token_type.value:
                raise JWTSecurityError(f"Invalid token type: expected {token_type.value}")
            
            # Create claims object
            claims = TokenClaims(
                user_id=payload['user_id'],
                username=payload['username'],
                roles=payload.get('roles', []),
                token_type=payload['token_type'],
                issued_at=payload['iat'],
                expires_at=payload['exp'],
                jti=payload['jti'],
                consciousness_level=payload.get('consciousness_level'),
                api_permissions=payload.get('api_permissions')
            )
            
            logger.debug(f"Token verified for user {claims.username}")
            return claims
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise JWTSecurityError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise JWTSecurityError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise JWTSecurityError(f"Token verification failed: {e}")
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a JWT token"""
        try:
            claims = self.verify_token(token)
            self.revoked_tokens.add(claims.jti)
            logger.info(f"Token revoked for user {claims.username} (JTI: {claims.jti})")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        try:
            # Verify refresh token
            claims = self.verify_token(refresh_token, TokenType.REFRESH)
            
            # Create new access token
            # Note: In production, fetch current user roles from database
            new_token = self.create_access_token(
                user_id=claims.user_id,
                username=claims.username,
                roles=['user']  # Fetch from database
            )
            
            logger.info(f"Access token refreshed for user {claims.username}")
            return new_token
            
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise JWTSecurityError(f"Token refresh failed: {e}")
    
    def authenticate_user(self, username: str, password: str) -> AuthenticationResult:
        """Authenticate user and return tokens"""
        try:
            # Check rate limiting
            if not self._check_rate_limiting(username):
                return AuthenticationResult(
                    success=False,
                    error_message="Too many failed attempts. Please try again later."
                )
            
            # In production, verify against database
            # For now, implement basic validation
            if not self._verify_user_credentials(username, password):
                self._record_failed_attempt(username)
                return AuthenticationResult(
                    success=False,
                    error_message="Invalid username or password"
                )
            
            # Get user details (from database in production)
            user_id = self._get_user_id(username)
            roles = self._get_user_roles(username)
            
            # Create tokens
            access_token = self.create_access_token(
                user_id=user_id,
                username=username,
                roles=roles
            )
            
            refresh_token = self.create_refresh_token(
                user_id=user_id,
                username=username
            )
            
            logger.info(f"User {username} authenticated successfully")
            
            return AuthenticationResult(
                success=True,
                user_id=user_id,
                username=username,
                roles=roles,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.config.jwt_expiration_hours * 3600
            )
            
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {e}")
            return AuthenticationResult(
                success=False,
                error_message="Authentication failed"
            )
    
    def _verify_user_credentials(self, username: str, password: str) -> bool:
        """Verify user credentials (placeholder - implement with database)"""
        # This is a placeholder - in production, verify against database
        # with proper password hashing
        if username == "admin" and password == "secure_admin_password":
            return True
        return False
    
    def _get_user_id(self, username: str) -> str:
        """Get user ID (placeholder - implement with database)"""
        # Placeholder - fetch from database
        return f"user_{hashlib.sha256(username.encode()).hexdigest()[:8]}"
    
    def _get_user_roles(self, username: str) -> List[str]:
        """Get user roles (placeholder - implement with database)"""
        # Placeholder - fetch from database
        if username == "admin":
            return [UserRole.ADMIN.value]
        return [UserRole.USER.value]
    
    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get token information without full verification"""
        try:
            # Decode without verification to get info
            payload = jwt.decode(token, options={"verify_signature": False})
            
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'roles': payload.get('roles', []),
                'token_type': payload.get('token_type'),
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp'),
                'jti': payload.get('jti'),
                'is_expired': payload.get('exp', 0) < datetime.now(timezone.utc).timestamp()
            }
        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return {}


# Global JWT manager instance
jwt_manager = SecureJWTManager()


def get_jwt_manager() -> SecureJWTManager:
    """Get the global JWT manager instance"""
    return jwt_manager


def require_auth(roles: Optional[List[str]] = None):
    """Decorator for requiring authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented with your web framework
            # (FastAPI, Flask, etc.) to extract and verify tokens
            pass
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test the JWT system
    manager = SecureJWTManager()
    
    # Test authentication
    result = manager.authenticate_user("admin", "secure_admin_password")
    if result.success and result.access_token:
        print("✅ Authentication successful")
        print(f"Access Token: {result.access_token[:50]}...")
        
        # Test token verification
        try:
            claims = manager.verify_token(result.access_token)
            print(f"✅ Token verified for user: {claims.username}")
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
    else:
        print(f"❌ Authentication failed: {result.error_message}")