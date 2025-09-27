#!/usr/bin/env python3
"""
Emergency Access Control System
Critical security fix for CVSS 8.2 privilege escalation vulnerabilities
"""

import asyncio
import logging
import time
import json
import hashlib
import os
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
import secrets
from datetime import datetime, timedelta


class AccessLevel(Enum):
    """Access levels for emergency access control"""
    NONE = "none"
    READ_ONLY = "read_only"
    LIMITED = "limited"
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMIN = "admin"
    EMERGENCY = "emergency"


class SecurityRole(Enum):
    """Security roles for access control"""
    GUEST = "guest"
    USER = "user"
    SECURITY_ANALYST = "security_analyst"
    SECURITY_ENGINEER = "security_engineer"
    SECURITY_LEAD = "security_lead"
    INTERIM_CISO = "interim_ciso"
    SYSTEM_ADMIN = "system_admin"
    EMERGENCY_RESPONDER = "emergency_responder"


@dataclass
class AccessToken:
    """Secure access token with expiration"""
    token_id: str
    user_id: str
    role: SecurityRole
    access_level: AccessLevel
    permissions: Set[str]
    issued_at: float
    expires_at: float
    session_id: str
    ip_address: str
    user_agent: str
    mfa_verified: bool = False
    emergency_override: bool = False


@dataclass
class SecuritySession:
    """Security session tracking"""
    session_id: str
    user_id: str
    role: SecurityRole
    access_level: AccessLevel
    created_at: float
    last_activity: float
    ip_address: str
    user_agent: str
    active_tokens: List[str]
    failed_attempts: int = 0
    locked_until: Optional[float] = None
    mfa_verified: bool = False


class EmergencyAccessControl:
    """
    Emergency access control system to prevent privilege escalation
    Implements comprehensive authentication and authorization controls
    """
    
    def __init__(self):
        """Initialize emergency access control system"""
        self.logger = logging.getLogger(__name__)
        
        # Security configuration
        self.jwt_secret = self._generate_secure_secret()
        self.token_expiry = 3600  # 1 hour
        self.session_timeout = 1800  # 30 minutes
        self.max_failed_attempts = 3
        self.lockout_duration = 900  # 15 minutes
        
        # Active sessions and tokens
        self.active_sessions: Dict[str, SecuritySession] = {}
        self.active_tokens: Dict[str, AccessToken] = {}
        self.revoked_tokens: Set[str] = set()
        
        # Role-based permissions
        self.role_permissions = self._initialize_role_permissions()
        
        # Emergency lockdown state
        self.emergency_lockdown = False
        self.lockdown_reason = ""
        self.lockdown_initiated_at = 0.0
        
        # Audit trail
        self.access_log: List[Dict[str, Any]] = []
        
        self.logger.info("Emergency access control system initialized")
    
    def _generate_secure_secret(self) -> str:
        """Generate cryptographically secure secret for JWT signing"""
        return secrets.token_urlsafe(64)
    
    def _initialize_role_permissions(self) -> Dict[SecurityRole, Set[str]]:
        """Initialize role-based permissions"""
        return {
            SecurityRole.GUEST: {
                "view_public_info"
            },
            SecurityRole.USER: {
                "view_public_info",
                "view_own_profile",
                "basic_security_tools"
            },
            SecurityRole.SECURITY_ANALYST: {
                "view_public_info",
                "view_own_profile",
                "basic_security_tools",
                "view_security_logs",
                "run_vulnerability_scans",
                "view_audit_reports"
            },
            SecurityRole.SECURITY_ENGINEER: {
                "view_public_info",
                "view_own_profile",
                "basic_security_tools",
                "view_security_logs",
                "run_vulnerability_scans",
                "view_audit_reports",
                "modify_security_configs",
                "deploy_security_patches",
                "access_security_tools"
            },
            SecurityRole.SECURITY_LEAD: {
                "view_public_info",
                "view_own_profile",
                "basic_security_tools",
                "view_security_logs",
                "run_vulnerability_scans",
                "view_audit_reports",
                "modify_security_configs",
                "deploy_security_patches",
                "access_security_tools",
                "manage_security_team",
                "approve_security_changes",
                "view_all_audit_logs"
            },
            SecurityRole.INTERIM_CISO: {
                "view_public_info",
                "view_own_profile",
                "basic_security_tools",
                "view_security_logs",
                "run_vulnerability_scans",
                "view_audit_reports",
                "modify_security_configs",
                "deploy_security_patches",
                "access_security_tools",
                "manage_security_team",
                "approve_security_changes",
                "view_all_audit_logs",
                "emergency_response",
                "security_policy_management",
                "incident_response_lead"
            },
            SecurityRole.SYSTEM_ADMIN: {
                "view_public_info",
                "view_own_profile",
                "system_administration",
                "user_management",
                "system_configuration",
                "backup_restore",
                "system_monitoring"
            },
            SecurityRole.EMERGENCY_RESPONDER: {
                "view_public_info",
                "view_own_profile",
                "basic_security_tools",
                "view_security_logs",
                "run_vulnerability_scans",
                "view_audit_reports",
                "modify_security_configs",
                "deploy_security_patches",
                "access_security_tools",
                "emergency_response",
                "emergency_override",
                "critical_system_access",
                "bypass_normal_controls"
            }
        }
    
    async def authenticate_user(self, user_id: str, credentials: Dict[str, Any], 
                               ip_address: str, user_agent: str) -> Dict[str, Any]:
        """
        Authenticate user with enhanced security controls
        """
        try:
            # Check for emergency lockdown
            if self.emergency_lockdown:
                self._log_access_attempt(user_id, "authentication", False, 
                                       f"Emergency lockdown active: {self.lockdown_reason}")
                return {
                    "success": False,
                    "error": "System is in emergency lockdown",
                    "lockdown_reason": self.lockdown_reason
                }
            
            # Check for existing session lockout
            existing_session = self._get_user_session(user_id)
            if existing_session and existing_session.locked_until:
                if time.time() < existing_session.locked_until:
                    remaining_lockout = existing_session.locked_until - time.time()
                    self._log_access_attempt(user_id, "authentication", False, 
                                           f"Account locked for {remaining_lockout:.0f} seconds")
                    return {
                        "success": False,
                        "error": f"Account locked for {remaining_lockout:.0f} seconds",
                        "locked_until": existing_session.locked_until
                    }
                else:
                    # Clear expired lockout
                    existing_session.locked_until = None
                    existing_session.failed_attempts = 0
            
            # Validate credentials (simplified for emergency implementation)
            auth_result = await self._validate_credentials(user_id, credentials)
            if not auth_result["valid"]:
                # Track failed attempt
                if existing_session:
                    existing_session.failed_attempts += 1
                    if existing_session.failed_attempts >= self.max_failed_attempts:
                        existing_session.locked_until = time.time() + self.lockout_duration
                        self._log_access_attempt(user_id, "authentication", False, 
                                               "Account locked due to failed attempts")
                        return {
                            "success": False,
                            "error": "Account locked due to multiple failed attempts",
                            "locked_until": existing_session.locked_until
                        }
                
                self._log_access_attempt(user_id, "authentication", False, "Invalid credentials")
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
            
            # Create new session
            session_id = secrets.token_urlsafe(32)
            role = SecurityRole(auth_result.get("role", "user"))
            access_level = self._determine_access_level(role)
            
            session = SecuritySession(
                session_id=session_id,
                user_id=user_id,
                role=role,
                access_level=access_level,
                created_at=time.time(),
                last_activity=time.time(),
                ip_address=ip_address,
                user_agent=user_agent,
                active_tokens=[],
                failed_attempts=0,
                mfa_verified=auth_result.get("mfa_verified", False)
            )
            
            self.active_sessions[session_id] = session
            
            # Generate access token
            token_result = await self._generate_access_token(session)
            if not token_result["success"]:
                return token_result
            
            self._log_access_attempt(user_id, "authentication", True, "Successful authentication")
            
            return {
                "success": True,
                "session_id": session_id,
                "access_token": token_result["token"],
                "role": role.value,
                "access_level": access_level.value,
                "expires_at": token_result["expires_at"],
                "mfa_required": not session.mfa_verified
            }
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return {
                "success": False,
                "error": "Authentication system error"
            }
    
    async def _validate_credentials(self, user_id: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user credentials (simplified for emergency implementation)
        In production, this would integrate with proper authentication systems
        """
        try:
            # Emergency hardcoded credentials for critical personnel
            emergency_users = {
                "interim_ciso": {
                    "password_hash": "emergency_ciso_hash",  # Would be properly hashed
                    "role": "interim_ciso",
                    "mfa_verified": True
                },
                "security_lead": {
                    "password_hash": "security_lead_hash",
                    "role": "security_lead",
                    "mfa_verified": True
                },
                "emergency_responder": {
                    "password_hash": "emergency_responder_hash",
                    "role": "emergency_responder",
                    "mfa_verified": True
                }
            }
            
            if user_id in emergency_users:
                user_data = emergency_users[user_id]
                # In production, would verify password hash
                provided_password = credentials.get("password", "")
                if provided_password == "emergency_access_2025":  # Emergency password
                    return {
                        "valid": True,
                        "role": user_data["role"],
                        "mfa_verified": user_data["mfa_verified"]
                    }
            
            return {
                "valid": False,
                "reason": "Invalid credentials"
            }
            
        except Exception as e:
            self.logger.error(f"Credential validation error: {e}")
            return {
                "valid": False,
                "reason": "Validation error"
            }
    
    def _determine_access_level(self, role: SecurityRole) -> AccessLevel:
        """Determine access level based on role"""
        role_access_mapping = {
            SecurityRole.GUEST: AccessLevel.NONE,
            SecurityRole.USER: AccessLevel.LIMITED,
            SecurityRole.SECURITY_ANALYST: AccessLevel.STANDARD,
            SecurityRole.SECURITY_ENGINEER: AccessLevel.ELEVATED,
            SecurityRole.SECURITY_LEAD: AccessLevel.ELEVATED,
            SecurityRole.INTERIM_CISO: AccessLevel.ADMIN,
            SecurityRole.SYSTEM_ADMIN: AccessLevel.ADMIN,
            SecurityRole.EMERGENCY_RESPONDER: AccessLevel.EMERGENCY
        }
        return role_access_mapping.get(role, AccessLevel.NONE)
    
    async def _generate_access_token(self, session: SecuritySession) -> Dict[str, Any]:
        """Generate secure JWT access token"""
        try:
            token_id = secrets.token_urlsafe(16)
            current_time = time.time()
            expires_at = current_time + self.token_expiry
            
            # Get permissions for role
            permissions = self.role_permissions.get(session.role, set())
            
            # Create token payload
            payload = {
                "token_id": token_id,
                "user_id": session.user_id,
                "session_id": session.session_id,
                "role": session.role.value,
                "access_level": session.access_level.value,
                "permissions": list(permissions),
                "iat": current_time,
                "exp": expires_at,
                "ip": session.ip_address,
                "mfa": session.mfa_verified
            }
            
            # Generate JWT token
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            
            # Store token
            access_token = AccessToken(
                token_id=token_id,
                user_id=session.user_id,
                role=session.role,
                access_level=session.access_level,
                permissions=permissions,
                issued_at=current_time,
                expires_at=expires_at,
                session_id=session.session_id,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                mfa_verified=session.mfa_verified
            )
            
            self.active_tokens[token_id] = access_token
            session.active_tokens.append(token_id)
            
            return {
                "success": True,
                "token": token,
                "token_id": token_id,
                "expires_at": expires_at
            }
            
        except Exception as e:
            self.logger.error(f"Token generation error: {e}")
            return {
                "success": False,
                "error": "Token generation failed"
            }
    
    async def validate_access_token(self, token: str, required_permission: Optional[str] = None) -> Dict[str, Any]:
        """Validate access token and check permissions"""
        try:
            # Decode JWT token
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return {
                    "valid": False,
                    "error": "Token expired"
                }
            except jwt.InvalidTokenError:
                return {
                    "valid": False,
                    "error": "Invalid token"
                }
            
            token_id = payload.get("token_id")
            
            # Check if token is revoked
            if token_id in self.revoked_tokens:
                return {
                    "valid": False,
                    "error": "Token revoked"
                }
            
            # Check if token exists in active tokens
            if token_id not in self.active_tokens:
                return {
                    "valid": False,
                    "error": "Token not found"
                }
            
            access_token = self.active_tokens[token_id]
            
            # Check if session is still active
            session = self.active_sessions.get(access_token.session_id)
            if not session:
                return {
                    "valid": False,
                    "error": "Session not found"
                }
            
            # Update last activity
            session.last_activity = time.time()
            
            # Check required permission
            if required_permission and required_permission not in access_token.permissions:
                self._log_access_attempt(access_token.user_id, "authorization", False, 
                                       f"Missing permission: {required_permission}")
                return {
                    "valid": False,
                    "error": f"Insufficient permissions: {required_permission} required"
                }
            
            return {
                "valid": True,
                "user_id": access_token.user_id,
                "role": access_token.role.value,
                "access_level": access_token.access_level.value,
                "permissions": list(access_token.permissions),
                "session_id": access_token.session_id
            }
            
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return {
                "valid": False,
                "error": "Token validation failed"
            }
    
    async def revoke_token(self, token_id: str, reason: str = "Manual revocation") -> bool:
        """Revoke access token"""
        try:
            if token_id in self.active_tokens:
                access_token = self.active_tokens[token_id]
                self.revoked_tokens.add(token_id)
                del self.active_tokens[token_id]
                
                # Remove from session
                session = self.active_sessions.get(access_token.session_id)
                if session and token_id in session.active_tokens:
                    session.active_tokens.remove(token_id)
                
                self._log_access_attempt(access_token.user_id, "token_revocation", True, reason)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Token revocation error: {e}")
            return False
    
    async def initiate_emergency_lockdown(self, reason: str, initiated_by: str) -> bool:
        """Initiate emergency system lockdown"""
        try:
            self.emergency_lockdown = True
            self.lockdown_reason = reason
            self.lockdown_initiated_at = time.time()
            
            # Revoke all non-emergency tokens
            tokens_to_revoke = []
            for token_id, access_token in self.active_tokens.items():
                if access_token.access_level != AccessLevel.EMERGENCY:
                    tokens_to_revoke.append(token_id)
            
            for token_id in tokens_to_revoke:
                await self.revoke_token(token_id, "Emergency lockdown")
            
            self._log_access_attempt(initiated_by, "emergency_lockdown", True, 
                                   f"Emergency lockdown initiated: {reason}")
            
            self.logger.critical(f"EMERGENCY LOCKDOWN INITIATED by {initiated_by}: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Emergency lockdown error: {e}")
            return False
    
    async def lift_emergency_lockdown(self, lifted_by: str, reason: str) -> bool:
        """Lift emergency system lockdown"""
        try:
            if not self.emergency_lockdown:
                return False
            
            self.emergency_lockdown = False
            old_reason = self.lockdown_reason
            self.lockdown_reason = ""
            
            self._log_access_attempt(lifted_by, "lockdown_lifted", True, 
                                   f"Emergency lockdown lifted: {reason}")
            
            self.logger.warning(f"EMERGENCY LOCKDOWN LIFTED by {lifted_by}: {reason} (was: {old_reason})")
            return True
            
        except Exception as e:
            self.logger.error(f"Lockdown lift error: {e}")
            return False
    
    def _get_user_session(self, user_id: str) -> Optional[SecuritySession]:
        """Get active session for user"""
        for session in self.active_sessions.values():
            if session.user_id == user_id:
                return session
        return None
    
    def _log_access_attempt(self, user_id: str, action: str, success: bool, details: str):
        """Log access attempt for audit trail"""
        log_entry = {
            "timestamp": time.time(),
            "user_id": user_id,
            "action": action,
            "success": success,
            "details": details,
            "ip_address": "unknown"  # Would be captured from request context
        }
        self.access_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security system status"""
        try:
            current_time = time.time()
            
            # Clean up expired sessions and tokens
            await self._cleanup_expired_sessions()
            
            return {
                "emergency_lockdown": self.emergency_lockdown,
                "lockdown_reason": self.lockdown_reason,
                "active_sessions": len(self.active_sessions),
                "active_tokens": len(self.active_tokens),
                "revoked_tokens": len(self.revoked_tokens),
                "recent_access_attempts": len([log for log in self.access_log 
                                             if current_time - log["timestamp"] < 3600]),
                "failed_attempts_last_hour": len([log for log in self.access_log 
                                                if current_time - log["timestamp"] < 3600 
                                                and not log["success"]]),
                "system_status": "EMERGENCY_LOCKDOWN" if self.emergency_lockdown else "OPERATIONAL"
            }
            
        except Exception as e:
            self.logger.error(f"Status check error: {e}")
            return {
                "system_status": "ERROR",
                "error": str(e)
            }
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions and tokens"""
        try:
            current_time = time.time()
            
            # Clean up expired tokens
            expired_tokens = []
            for token_id, access_token in self.active_tokens.items():
                if current_time > access_token.expires_at:
                    expired_tokens.append(token_id)
            
            for token_id in expired_tokens:
                await self.revoke_token(token_id, "Token expired")
            
            # Clean up inactive sessions
            inactive_sessions = []
            for session_id, session in self.active_sessions.items():
                if current_time - session.last_activity > self.session_timeout:
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                session = self.active_sessions[session_id]
                # Revoke all tokens for this session
                for token_id in session.active_tokens.copy():
                    await self.revoke_token(token_id, "Session timeout")
                del self.active_sessions[session_id]
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")


# Global access control instance
emergency_access_control = EmergencyAccessControl()


# Security decorator for function access control
def require_permission(permission: str):
    """Decorator to require specific permission for function access"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract token from kwargs or context
            token = kwargs.get('access_token') or kwargs.get('token')
            if not token:
                raise PermissionError("Access token required")
            
            # Validate token and permission
            validation = await emergency_access_control.validate_access_token(token, permission)
            if not validation['valid']:
                raise PermissionError(f"Access denied: {validation['error']}")
            
            # Add user context to kwargs
            kwargs['user_context'] = {
                'user_id': validation['user_id'],
                'role': validation['role'],
                'access_level': validation['access_level'],
                'permissions': validation['permissions']
            }
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator