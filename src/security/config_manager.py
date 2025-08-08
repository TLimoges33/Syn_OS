#!/usr/bin/env python3
"""
Secure Configuration Manager for Syn_OS
Handles environment variables, secrets, and secure configuration loading
"""

import os
import logging
import secrets
import hashlib
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger('synapticos.security.config')


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 30
    encryption_key: str = ""
    signing_key: str = ""
    enable_rate_limiting: bool = True
    enable_audit_logging: bool = True
    enable_mtls: bool = True
    session_timeout_minutes: int = 30


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"
    connection_timeout: int = 30
    max_connections: int = 20


@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str
    port: int
    password: str
    ssl: bool = True
    db: int = 0
    max_connections: int = 10


class ConfigurationError(Exception):
    """Configuration related errors"""
    pass


class SecureConfigManager:
    """Secure configuration manager with encryption and validation"""
    
    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or ".env"
        self.config_cache: Dict[str, Any] = {}
        self.encryption_key: Optional[bytes] = None
        self._load_environment()
        self._initialize_encryption()
    
    def _load_environment(self):
        """Load environment variables from .env file if it exists"""
        env_path = Path(self.env_file)
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Only set if not already in environment
                            if key not in os.environ:
                                os.environ[key] = value
                logger.info(f"Loaded environment configuration from {env_path}")
            except Exception as e:
                logger.warning(f"Failed to load environment file {env_path}: {e}")
    
    def _initialize_encryption(self):
        """Initialize encryption for sensitive configuration data"""
        try:
            encryption_key = self.get_required("ENCRYPTION_KEY")
            if len(encryption_key) < 32:
                # Generate a proper key from the provided key
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'syn_os_salt_2024',  # In production, use random salt
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
                self.encryption_key = key
            else:
                self.encryption_key = base64.urlsafe_b64encode(encryption_key.encode()[:32])
            
            logger.info("Encryption system initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize encryption: {e}")
            # Generate a temporary key for development
            self.encryption_key = Fernet.generate_key()
    
    def get_required(self, key: str) -> str:
        """Get a required environment variable, raise error if missing"""
        value = os.getenv(key)
        if value is None:
            raise ConfigurationError(f"Required environment variable '{key}' is not set")
        return value
    
    def get_optional(self, key: str, default: str = "") -> str:
        """Get an optional environment variable with default"""
        return os.getenv(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def get_list(self, key: str, separator: str = ",", default: Optional[list] = None) -> list:
        """Get a list from environment variable"""
        value = os.getenv(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value"""
        if not self.encryption_key:
            raise ConfigurationError("Encryption not initialized")
        
        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        if not self.encryption_key:
            raise ConfigurationError("Encryption not initialized")
        
        try:
            fernet = Fernet(self.encryption_key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ConfigurationError(f"Failed to decrypt value: {e}")
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration with validation"""
        jwt_secret = self.get_required("JWT_SECRET_KEY")
        
        # Validate JWT secret strength
        if len(jwt_secret) < 32:
            logger.warning("JWT secret key is too short, generating secure key")
            jwt_secret = secrets.token_urlsafe(32)
        
        return SecurityConfig(
            jwt_secret_key=jwt_secret,
            jwt_algorithm=self.get_optional("JWT_ALGORITHM", "HS256"),
            jwt_expiration_hours=self.get_int("JWT_EXPIRATION_HOURS", 24),
            jwt_refresh_expiration_days=self.get_int("JWT_REFRESH_EXPIRATION_DAYS", 30),
            encryption_key=self.get_required("ENCRYPTION_KEY"),
            signing_key=self.get_required("SIGNING_KEY"),
            enable_rate_limiting=self.get_bool("ENABLE_RATE_LIMITING", True),
            enable_audit_logging=self.get_bool("ENABLE_AUDIT_LOGGING", True),
            enable_mtls=self.get_bool("ENABLE_MTLS", True),
            session_timeout_minutes=self.get_int("SESSION_TIMEOUT_MINUTES", 30)
        )
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration with validation"""
        return DatabaseConfig(
            host=self.get_required("POSTGRES_HOST"),
            port=self.get_int("POSTGRES_PORT", 5432),
            database=self.get_required("POSTGRES_DB"),
            username=self.get_required("POSTGRES_USER"),
            password=self.get_required("POSTGRES_PASSWORD"),
            ssl_mode=self.get_optional("POSTGRES_SSL_MODE", "require"),
            connection_timeout=self.get_int("POSTGRES_TIMEOUT", 30),
            max_connections=self.get_int("POSTGRES_MAX_CONNECTIONS", 20)
        )
    
    def get_redis_config(self) -> RedisConfig:
        """Get Redis configuration with validation"""
        return RedisConfig(
            host=self.get_required("REDIS_HOST"),
            port=self.get_int("REDIS_PORT", 6379),
            password=self.get_required("REDIS_PASSWORD"),
            ssl=self.get_bool("REDIS_SSL", True),
            db=self.get_int("REDIS_DB", 0),
            max_connections=self.get_int("REDIS_MAX_CONNECTIONS", 10)
        )
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate all configuration settings"""
        validation_results = {}
        
        try:
            # Validate security config
            security_config = self.get_security_config()
            validation_results['security'] = True
            
            # Check JWT secret strength
            if len(security_config.jwt_secret_key) < 32:
                validation_results['jwt_strength'] = False
                logger.error("JWT secret key is too weak")
            else:
                validation_results['jwt_strength'] = True
            
        except Exception as e:
            validation_results['security'] = False
            logger.error(f"Security configuration validation failed: {e}")
        
        try:
            # Validate database config
            db_config = self.get_database_config()
            validation_results['database'] = True
            
            # Check for default passwords
            if db_config.password in ['password', 'postgres', 'admin', '123456']:
                validation_results['db_password_strength'] = False
                logger.error("Database password is too weak")
            else:
                validation_results['db_password_strength'] = True
                
        except Exception as e:
            validation_results['database'] = False
            logger.error(f"Database configuration validation failed: {e}")
        
        try:
            # Validate Redis config
            redis_config = self.get_redis_config()
            validation_results['redis'] = True
            
        except Exception as e:
            validation_results['redis'] = False
            logger.error(f"Redis configuration validation failed: {e}")
        
        return validation_results
    
    def generate_secure_secrets(self) -> Dict[str, str]:
        """Generate secure secrets for initial setup"""
        return {
            'JWT_SECRET_KEY': secrets.token_urlsafe(32),
            'ENCRYPTION_KEY': secrets.token_urlsafe(32),
            'SIGNING_KEY': secrets.token_urlsafe(32),
            'INTERNAL_API_KEY': secrets.token_urlsafe(24),
            'EXTERNAL_API_KEY': secrets.token_urlsafe(24),
            'POSTGRES_PASSWORD': secrets.token_urlsafe(16),
            'REDIS_PASSWORD': secrets.token_urlsafe(16),
            'NATS_PASSWORD': secrets.token_urlsafe(16),
            'PROMETHEUS_PASSWORD': secrets.token_urlsafe(16),
            'GRAFANA_ADMIN_PASSWORD': secrets.token_urlsafe(16),
            'VAULT_TOKEN': secrets.token_urlsafe(24),
            'LM_STUDIO_API_KEY': secrets.token_urlsafe(24),
            'CONSCIOUSNESS_ENCRYPTION_KEY': secrets.token_urlsafe(32)
        }
    
    def create_secure_env_file(self, output_path: str = ".env") -> bool:
        """Create a secure .env file with generated secrets"""
        try:
            secure_secrets = self.generate_secure_secrets()
            
            with open(output_path, 'w') as f:
                f.write("# Syn_OS Secure Environment Configuration\n")
                f.write("# Generated on: " + str(os.popen('date').read().strip()) + "\n")
                f.write("# WARNING: Keep this file secure and never commit to version control\n\n")
                
                # Database Configuration
                f.write("# Database Configuration\n")
                f.write("POSTGRES_HOST=postgres\n")
                f.write("POSTGRES_PORT=5432\n")
                f.write("POSTGRES_DB=syn_os\n")
                f.write("POSTGRES_USER=syn_os_secure\n")
                f.write(f"POSTGRES_PASSWORD={secure_secrets['POSTGRES_PASSWORD']}\n")
                f.write("POSTGRES_SSL_MODE=require\n\n")
                
                # Redis Configuration
                f.write("# Redis Configuration\n")
                f.write("REDIS_HOST=redis\n")
                f.write("REDIS_PORT=6379\n")
                f.write(f"REDIS_PASSWORD={secure_secrets['REDIS_PASSWORD']}\n")
                f.write("REDIS_SSL=true\n\n")
                
                # JWT Configuration
                f.write("# JWT Configuration\n")
                f.write(f"JWT_SECRET_KEY={secure_secrets['JWT_SECRET_KEY']}\n")
                f.write("JWT_ALGORITHM=HS256\n")
                f.write("JWT_EXPIRATION_HOURS=24\n")
                f.write("JWT_REFRESH_EXPIRATION_DAYS=30\n\n")
                
                # API Configuration
                f.write("# API Configuration\n")
                f.write(f"INTERNAL_API_KEY={secure_secrets['INTERNAL_API_KEY']}\n")
                f.write(f"EXTERNAL_API_KEY={secure_secrets['EXTERNAL_API_KEY']}\n\n")
                
                # Encryption Keys
                f.write("# Encryption Configuration\n")
                f.write(f"ENCRYPTION_KEY={secure_secrets['ENCRYPTION_KEY']}\n")
                f.write(f"SIGNING_KEY={secure_secrets['SIGNING_KEY']}\n\n")
                
                # Security Settings
                f.write("# Security Configuration\n")
                f.write("ENABLE_RATE_LIMITING=true\n")
                f.write("ENABLE_AUDIT_LOGGING=true\n")
                f.write("ENABLE_MTLS=true\n")
                f.write("SESSION_TIMEOUT_MINUTES=30\n\n")
                
                # Application Settings
                f.write("# Application Configuration\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("DEBUG=false\n")
                f.write("ENVIRONMENT=production\n")
                f.write("CONSCIOUSNESS_MODE=production\n\n")
                
                # Consciousness System
                f.write("# Consciousness System Configuration\n")
                f.write(f"LM_STUDIO_API_KEY={secure_secrets['LM_STUDIO_API_KEY']}\n")
                f.write(f"CONSCIOUSNESS_ENCRYPTION_KEY={secure_secrets['CONSCIOUSNESS_ENCRYPTION_KEY']}\n")
            
            # Set secure permissions
            os.chmod(output_path, 0o600)
            logger.info(f"Secure environment file created at {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create secure environment file: {e}")
            return False


# Global configuration manager instance
config_manager = SecureConfigManager()


def get_config() -> SecureConfigManager:
    """Get the global configuration manager instance"""
    return config_manager


def validate_system_security() -> bool:
    """Validate system security configuration"""
    validation_results = config_manager.validate_configuration()
    
    all_valid = all(validation_results.values())
    
    if not all_valid:
        logger.error("System security validation failed:")
        for check, result in validation_results.items():
            if not result:
                logger.error(f"  - {check}: FAILED")
    else:
        logger.info("System security validation passed")
    
    return all_valid


if __name__ == "__main__":
    # CLI for generating secure configuration
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        config = SecureConfigManager()
        if config.create_secure_env_file():
            print("✅ Secure .env file generated successfully")
            print("⚠️  Please review and customize the generated values")
            print("🔒 File permissions set to 600 (owner read/write only)")
        else:
            print("❌ Failed to generate secure .env file")
            sys.exit(1)
    else:
        # Validate current configuration
        if validate_system_security():
            print("✅ System security configuration is valid")
        else:
            print("❌ System security configuration has issues")
            sys.exit(1)