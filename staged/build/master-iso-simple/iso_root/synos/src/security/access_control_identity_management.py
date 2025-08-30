#!/usr/bin/env python3
"""
Access Control and Identity Management System
Enterprise-grade identity and access management for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
import hashlib
import secrets
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import bcrypt
import hmac
import struct
from io import BytesIO


class UserRole(Enum):
    """User role definitions"""
    ADMIN = "admin"
    SECURITY_ANALYST = "security_analyst"
    DEVELOPER = "developer"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    USER = "user"
    GUEST = "guest"


class AccountStatus(Enum):
    """Account status definitions"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    PENDING = "pending"
    EXPIRED = "expired"


class AuthenticationMethod(Enum):
    """Authentication method types"""
    PASSWORD = "password"
    MFA_TOTP = "mfa_totp"
    MFA_SMS = "mfa_sms"
    CERTIFICATE = "certificate"
    BIOMETRIC = "biometric"


@dataclass
class User:
    """User account definition"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    status: AccountStatus
    password_hash: str
    mfa_secret: Optional[str]
    mfa_enabled: bool
    last_login: Optional[float]
    failed_attempts: int
    lockout_time: Optional[float]
    password_expires: float
    created_date: float
    last_modified: float
    attributes: Dict[str, Any]


@dataclass
class Permission:
    """Permission definition"""
    permission_id: str
    name: str
    description: str
    resource: str
    action: str
    conditions: List[str]
    created_date: float


@dataclass
class Role:
    """Role definition with permissions"""
    role_id: str
    name: str
    description: str
    permissions: List[str]
    inherits_from: List[str]
    created_date: float
    last_modified: float


@dataclass
class AccessRequest:
    """Access request for approval workflow"""
    request_id: str
    user_id: str
    requested_role: str
    requested_permissions: List[str]
    business_justification: str
    requester: str
    approver: Optional[str]
    status: str
    request_date: float
    approval_date: Optional[float]
    expiry_date: Optional[float]


@dataclass
class AuthenticationSession:
    """User authentication session"""
    session_id: str
    user_id: str
    authentication_methods: List[AuthenticationMethod]
    session_start: float
    last_activity: float
    ip_address: str
    user_agent: str
    is_privileged: bool
    expires_at: float


class AccessControlIdentityManagement:
    """
    Access Control and Identity Management System
    Implements enterprise-grade identity and access management
    """
    
    def __init__(self):
        """Initialize access control and identity management system"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.acim_directory = "/var/lib/synos/acim"
        self.database_file = f"{self.acim_directory}/acim.db"
        
        # System components
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        self.active_sessions: Dict[str, AuthenticationSession] = {}
        
        # Security configuration
        self.password_policy = {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special": True,
            "password_history": 12,
            "max_age_days": 90,
            "lockout_threshold": 5,
            "lockout_duration": 1800  # 30 minutes
        }
        
        self.session_policy = {
            "max_session_duration": 28800,  # 8 hours
            "idle_timeout": 3600,  # 1 hour
            "concurrent_sessions": 3,
            "privileged_session_timeout": 1800  # 30 minutes
        }
        
        # System metrics
        self.metrics = {
            "total_users": 0,
            "active_users": 0,
            "locked_accounts": 0,
            "active_sessions": 0,
            "failed_logins": 0,
            "successful_logins": 0,
            "mfa_enabled_users": 0,
            "pending_access_requests": 0
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_acim())
    
    async def _initialize_acim(self):
        """Initialize access control and identity management system"""
        try:
            self.logger.info("Initializing Access Control and Identity Management system...")
            
            # Create ACIM directory
            os.makedirs(self.acim_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Create default roles and permissions
            await self._create_default_roles_permissions()
            
            # Create default admin user
            await self._create_default_admin()
            
            # Start session cleanup task
            asyncio.create_task(self._session_cleanup_task())
            
            self.logger.info("Access Control and Identity Management system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing ACIM: {e}")
    
    async def _initialize_database(self):
        """Initialize ACIM database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    mfa_secret TEXT,
                    mfa_enabled BOOLEAN DEFAULT 0,
                    last_login REAL,
                    failed_attempts INTEGER DEFAULT 0,
                    lockout_time REAL,
                    password_expires REAL,
                    created_date REAL NOT NULL,
                    last_modified REAL NOT NULL,
                    attributes TEXT
                )
            ''')
            
            # Roles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    role_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    permissions TEXT,
                    inherits_from TEXT,
                    created_date REAL NOT NULL,
                    last_modified REAL NOT NULL
                )
            ''')
            
            # Permissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    permission_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    conditions TEXT,
                    created_date REAL NOT NULL
                )
            ''')
            
            # Access requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    requested_role TEXT,
                    requested_permissions TEXT,
                    business_justification TEXT,
                    requester TEXT NOT NULL,
                    approver TEXT,
                    status TEXT NOT NULL,
                    request_date REAL NOT NULL,
                    approval_date REAL,
                    expiry_date REAL
                )
            ''')
            
            # Authentication sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    authentication_methods TEXT,
                    session_start REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_privileged BOOLEAN DEFAULT 0,
                    expires_at REAL NOT NULL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_status ON users (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON auth_sessions (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires ON auth_sessions (expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_status ON access_requests (status)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing ACIM database: {e}")
            raise
    
    async def _create_default_roles_permissions(self):
        """Create default roles and permissions"""
        try:
            current_time = time.time()
            
            # Create default permissions
            permissions = [
                Permission("PERM-001", "system.admin", "Full system administration", "system", "admin", [], current_time),
                Permission("PERM-002", "security.read", "Read security information", "security", "read", [], current_time),
                Permission("PERM-003", "security.write", "Modify security settings", "security", "write", [], current_time),
                Permission("PERM-004", "security.admin", "Full security administration", "security", "admin", [], current_time),
                Permission("PERM-005", "user.read", "Read user information", "user", "read", [], current_time),
                Permission("PERM-006", "user.write", "Modify user information", "user", "write", [], current_time),
                Permission("PERM-007", "audit.read", "Read audit logs", "audit", "read", [], current_time),
                Permission("PERM-008", "system.read", "Read system information", "system", "read", [], current_time),
                Permission("PERM-009", "development.read", "Read development resources", "development", "read", [], current_time),
                Permission("PERM-010", "development.write", "Modify development resources", "development", "write", [], current_time)
            ]
            
            for permission in permissions:
                await self._store_permission(permission)
                self.permissions[permission.permission_id] = permission
            
            # Create default roles
            roles = [
                Role("ROLE-001", "admin", "System Administrator", 
                     ["PERM-001", "PERM-002", "PERM-003", "PERM-004", "PERM-005", "PERM-006", "PERM-007", "PERM-008"], 
                     [], current_time, current_time),
                Role("ROLE-002", "security_analyst", "Security Analyst", 
                     ["PERM-002", "PERM-003", "PERM-005", "PERM-007", "PERM-008"], 
                     [], current_time, current_time),
                Role("ROLE-003", "developer", "Developer", 
                     ["PERM-005", "PERM-008", "PERM-009", "PERM-010"], 
                     [], current_time, current_time),
                Role("ROLE-004", "operator", "System Operator", 
                     ["PERM-005", "PERM-008"], 
                     [], current_time, current_time),
                Role("ROLE-005", "auditor", "Security Auditor", 
                     ["PERM-002", "PERM-005", "PERM-007", "PERM-008"], 
                     [], current_time, current_time),
                Role("ROLE-006", "user", "Standard User", 
                     ["PERM-005"], 
                     [], current_time, current_time)
            ]
            
            for role in roles:
                await self._store_role(role)
                self.roles[role.role_id] = role
            
            self.logger.info(f"Created {len(permissions)} permissions and {len(roles)} roles")
            
        except Exception as e:
            self.logger.error(f"Error creating default roles and permissions: {e}")
    
    async def _create_default_admin(self):
        """Create default administrator account"""
        try:
            current_time = time.time()
            password_expires = current_time + (90 * 24 * 3600)  # 90 days
            
            # Generate secure password
            admin_password = secrets.token_urlsafe(16)
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create admin user
            admin_user = User(
                user_id="USER-001",
                username="admin",
                email="admin@synos.local",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                status=AccountStatus.ACTIVE,
                password_hash=password_hash,
                mfa_secret=None,
                mfa_enabled=False,
                last_login=None,
                failed_attempts=0,
                lockout_time=None,
                password_expires=password_expires,
                created_date=current_time,
                last_modified=current_time,
                attributes={"created_by": "system", "is_default": True}
            )
            
            await self._store_user(admin_user)
            self.users[admin_user.user_id] = admin_user
            
            # Save admin credentials securely
            credentials_file = f"{self.acim_directory}/admin_credentials.txt"
            with open(credentials_file, 'w') as f:
                f.write(f"Default Administrator Credentials\n")
                f.write(f"Username: admin\n")
                f.write(f"Password: {admin_password}\n")
                f.write(f"Created: {datetime.fromtimestamp(current_time)}\n")
                f.write(f"Password Expires: {datetime.fromtimestamp(password_expires)}\n")
                f.write(f"\nIMPORTANT: Change this password immediately after first login!\n")
            
            # Set secure permissions on credentials file
            os.chmod(credentials_file, 0o600)
            
            self.logger.info("Default administrator account created")
            
        except Exception as e:
            self.logger.error(f"Error creating default admin: {e}")
    
    async def create_user(self, username: str, email: str, full_name: str, role: UserRole, 
                         password: str, requester: str) -> str:
        """Create new user account"""
        try:
            current_time = time.time()
            user_id = f"USER-{int(current_time)}-{secrets.randbelow(1000):03d}"
            
            # Validate password policy
            if not self._validate_password_policy(password):
                raise ValueError("Password does not meet policy requirements")
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            password_expires = current_time + (self.password_policy["max_age_days"] * 24 * 3600)
            
            # Create user
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                status=AccountStatus.PENDING,
                password_hash=password_hash,
                mfa_secret=None,
                mfa_enabled=False,
                last_login=None,
                failed_attempts=0,
                lockout_time=None,
                password_expires=password_expires,
                created_date=current_time,
                last_modified=current_time,
                attributes={"created_by": requester}
            )
            
            await self._store_user(user)
            self.users[user_id] = user
            
            # Update metrics
            self.metrics["total_users"] += 1
            
            self.logger.info(f"User created: {username} ({user_id})")
            return user_id
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str, ip_address: str, 
                              user_agent: str, mfa_token: Optional[str] = None) -> Optional[str]:
        """Authenticate user and create session"""
        try:
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                self.metrics["failed_logins"] += 1
                return None
            
            # Check account status
            if user.status != AccountStatus.ACTIVE:
                self.logger.warning(f"Authentication attempt for inactive user: {username}")
                return None
            
            # Check lockout
            if user.lockout_time and time.time() < user.lockout_time:
                self.logger.warning(f"Authentication attempt for locked user: {username}")
                return None
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                user.failed_attempts += 1
                
                # Check lockout threshold
                if user.failed_attempts >= self.password_policy["lockout_threshold"]:
                    user.lockout_time = time.time() + self.password_policy["lockout_duration"]
                    user.status = AccountStatus.LOCKED
                    self.metrics["locked_accounts"] += 1
                    self.logger.warning(f"User account locked due to failed attempts: {username}")
                
                await self._store_user(user)
                self.metrics["failed_logins"] += 1
                return None
            
            # Check MFA if enabled
            if user.mfa_enabled and user.mfa_secret:
                if not mfa_token:
                    self.logger.warning(f"MFA token required for user: {username}")
                    return None
                
                if not self._verify_mfa_token(user.mfa_secret, mfa_token):
                    user.failed_attempts += 1
                    await self._store_user(user)
                    self.metrics["failed_logins"] += 1
                    return None
            
            # Reset failed attempts on successful authentication
            user.failed_attempts = 0
            user.lockout_time = None
            user.last_login = time.time()
            
            if user.status == AccountStatus.LOCKED:
                user.status = AccountStatus.ACTIVE
                self.metrics["locked_accounts"] -= 1
            
            await self._store_user(user)
            
            # Create session
            session_id = await self._create_session(user, ip_address, user_agent, mfa_token is not None)
            
            self.metrics["successful_logins"] += 1
            self.logger.info(f"User authenticated successfully: {username}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            return None
    
    async def _create_session(self, user: User, ip_address: str, user_agent: str, 
                            mfa_verified: bool) -> str:
        """Create authentication session"""
        try:
            current_time = time.time()
            session_id = secrets.token_urlsafe(32)
            
            # Determine session duration
            if user.role in [UserRole.ADMIN, UserRole.SECURITY_ANALYST]:
                session_duration = self.session_policy["privileged_session_timeout"]
                is_privileged = True
            else:
                session_duration = self.session_policy["max_session_duration"]
                is_privileged = False
            
            # Authentication methods used
            auth_methods = [AuthenticationMethod.PASSWORD]
            if mfa_verified:
                auth_methods.append(AuthenticationMethod.MFA_TOTP)
            
            # Create session
            session = AuthenticationSession(
                session_id=session_id,
                user_id=user.user_id,
                authentication_methods=auth_methods,
                session_start=current_time,
                last_activity=current_time,
                ip_address=ip_address,
                user_agent=user_agent,
                is_privileged=is_privileged,
                expires_at=current_time + session_duration
            )
            
            await self._store_session(session)
            self.active_sessions[session_id] = session
            
            self.metrics["active_sessions"] += 1
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            raise
    
    async def enable_mfa(self, user_id: str) -> Tuple[str, str]:
        """Enable multi-factor authentication for user"""
        try:
            user = self.users.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Generate MFA secret (32 character base32 string)
            mfa_secret = base64.b32encode(secrets.token_bytes(20)).decode('utf-8').rstrip('=')
            user.mfa_secret = mfa_secret
            user.mfa_enabled = True
            user.last_modified = time.time()
            
            await self._store_user(user)
            
            # Generate provisioning URI for authenticator apps
            provisioning_uri = f"otpauth://totp/Syn_OS:{user.email}?secret={mfa_secret}&issuer=Syn_OS"
            
            # Create simple QR code representation (text-based for now)
            qr_code_data = f"QR Code Data: {provisioning_uri}"
            
            self.metrics["mfa_enabled_users"] += 1
            
            self.logger.info(f"MFA enabled for user: {user.username}")
            
            return mfa_secret, qr_code_data
            
        except Exception as e:
            self.logger.error(f"Error enabling MFA: {e}")
            raise
    
    def _verify_mfa_token(self, secret: str, token: str) -> bool:
        """Verify MFA token using TOTP algorithm"""
        try:
            # Simple TOTP implementation
            current_time = int(time.time()) // 30  # 30-second time window
            
            # Check current time window and adjacent windows for clock drift
            for time_window in [current_time - 1, current_time, current_time + 1]:
                expected_token = self._generate_totp_token(secret, time_window)
                if expected_token == token:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying MFA token: {e}")
            return False
    
    def _generate_totp_token(self, secret: str, time_counter: int) -> str:
        """Generate TOTP token for given time counter"""
        try:
            # Decode base32 secret
            key = base64.b32decode(secret + '=' * (8 - len(secret) % 8))
            
            # Convert time counter to bytes
            time_bytes = struct.pack('>Q', time_counter)
            
            # Generate HMAC-SHA1
            hmac_digest = hmac.new(key, time_bytes, hashlib.sha1).digest()
            
            # Dynamic truncation
            offset = hmac_digest[-1] & 0x0f
            truncated = struct.unpack('>I', hmac_digest[offset:offset + 4])[0]
            truncated &= 0x7fffffff
            
            # Generate 6-digit token
            token = str(truncated % 1000000).zfill(6)
            
            return token
            
        except Exception as e:
            self.logger.error(f"Error generating TOTP token: {e}")
            return "000000"
    
    def _validate_password_policy(self, password: str) -> bool:
        """Validate password against policy"""
        try:
            policy = self.password_policy
            
            # Check length
            if len(password) < policy["min_length"]:
                return False
            
            # Check character requirements
            if policy["require_uppercase"] and not any(c.isupper() for c in password):
                return False
            
            if policy["require_lowercase"] and not any(c.islower() for c in password):
                return False
            
            if policy["require_numbers"] and not any(c.isdigit() for c in password):
                return False
            
            if policy["require_special"] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating password policy: {e}")
            return False
    
    async def _session_cleanup_task(self):
        """Background task to clean up expired sessions"""
        while True:
            try:
                current_time = time.time()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if (session.expires_at < current_time or 
                        session.last_activity + self.session_policy["idle_timeout"] < current_time):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self._remove_session(session_id)
                
                if expired_sessions:
                    self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in session cleanup task: {e}")
                await asyncio.sleep(60)
    
    async def _remove_session(self, session_id: str):
        """Remove session"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                self.metrics["active_sessions"] -= 1
            
            # Remove from database
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM auth_sessions WHERE session_id = ?', (session_id,))
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error removing session: {e}")
    
    async def _store_user(self, user: User):
        """Store user in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users
                (user_id, username, email, full_name, role, status, password_hash, mfa_secret,
                 mfa_enabled, last_login, failed_attempts, lockout_time, password_expires,
                 created_date, last_modified, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id, user.username, user.email, user.full_name, user.role.value,
                user.status.value, user.password_hash, user.mfa_secret, user.mfa_enabled,
                user.last_login, user.failed_attempts, user.lockout_time, user.password_expires,
                user.created_date, user.last_modified, json.dumps(user.attributes)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing user: {e}")
    
    async def _store_role(self, role: Role):
        """Store role in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO roles
                (role_id, name, description, permissions, inherits_from, created_date, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                role.role_id, role.name, role.description, json.dumps(role.permissions),
                json.dumps(role.inherits_from), role.created_date, role.last_modified
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing role: {e}")
    
    async def _store_permission(self, permission: Permission):
        """Store permission in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO permissions
                (permission_id, name, description, resource, action, conditions, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                permission.permission_id, permission.name, permission.description,
                permission.resource, permission.action, json.dumps(permission.conditions),
                permission.created_date
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing permission: {e}")
    
    async def _store_session(self, session: AuthenticationSession):
        """Store session in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            auth_methods = [method.value for method in session.authentication_methods]
            
            cursor.execute('''
                INSERT OR REPLACE INTO auth_sessions
                (session_id, user_id, authentication_methods, session_start, last_activity,
                 ip_address, user_agent, is_privileged, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id, session.user_id, json.dumps(auth_methods),
                session.session_start, session.last_activity, session.ip_address,
                session.user_agent, session.is_privileged, session.expires_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing session: {e}")
    
    async def get_acim_status(self) -> Dict[str, Any]:
        """Get access control and identity management status"""
        try:
            return {
                "system_metrics": self.metrics,
                "user_statistics": {
                    "total_users": len(self.users),
                    "active_users": len([u for u in self.users.values() if u.status == AccountStatus.ACTIVE]),
                    "locked_users": len([u for u in self.users.values() if u.status == AccountStatus.LOCKED]),
                    "mfa_enabled": len([u for u in self.users.values() if u.mfa_enabled]),
                    "password_expiring_soon": len([u for u in self.users.values() 
                                                  if u.password_expires < time.time() + (7 * 24 * 3600)])
                },
                "session_statistics": {
                    "active_sessions": len(self.active_sessions),
                    "privileged_sessions": len([s for s in self.active_sessions.values() if s.is_privileged])
                },
                "security_posture": {
                    "mfa_adoption_rate": (self.metrics["mfa_enabled_users"] / max(self.metrics["total_users"], 1)) * 100,
                    "account_lockout_rate": (self.metrics["locked_accounts"] / max(self.metrics["total_users"], 1)) * 100,
                    "authentication_success_rate": (self.metrics["successful_logins"] / 
                                                   max(self.metrics["successful_logins"] + self.metrics["failed_logins"], 1)) * 100
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ACIM status: {e}")
            return {"error": str(e)}


# Global access control and identity management instance
acim = AccessControlIdentityManagement()