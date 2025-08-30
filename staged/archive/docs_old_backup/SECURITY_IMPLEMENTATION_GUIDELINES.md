# Syn_OS Security Implementation Guidelines

* *Version**: 1.0
* *Date**: 2025-07-23
* *Purpose**: Define security standards and implementation guidelines for all Syn_OS components

## Table of Contents

1. [Security Principles](#security-principles)
2. [Authentication & Authorization](#authentication--authorization)
3. [Data Protection](#data-protection)
4. [Network Security](#network-security)
5. [Container Security](#container-security)
6. [Code Security](#code-security)
7. [AI Model Security](#ai-model-security)
8. [Incident Response](#incident-response)
9. [Compliance Requirements](#compliance-requirements)
10. [Security Checklist](#security-checklist)

## Security Principles

### Zero Trust Architecture

```text
Never Trust, Always Verify
├── No implicit trust between services
├── Authenticate every request
├── Authorize every action
├── Encrypt everything
└── Log everything
```text

└── Log everything

```text
└── Log everything

```text
```text

### Defense in Depth

1. **Network Layer**: Firewalls, segmentation, IDS/IPS
2. **Application Layer**: Input validation, secure coding
3. **Data Layer**: Encryption at rest and in transit
4. **Identity Layer**: Strong authentication, least privilege
5. **Monitoring Layer**: Logging, alerting, anomaly detection

### Security by Design

- Security considered at every stage
- Threat modeling for new features
- Security reviews before deployment
- Automated security testing
- Regular security audits

## Authentication & Authorization

### JWT Implementation

```python
1. **Data Layer**: Encryption at rest and in transit
2. **Identity Layer**: Strong authentication, least privilege
3. **Monitoring Layer**: Logging, alerting, anomaly detection

### Security by Design

- Security considered at every stage
- Threat modeling for new features
- Security reviews before deployment
- Automated security testing
- Regular security audits

## Authentication & Authorization

### JWT Implementation

```python

1. **Data Layer**: Encryption at rest and in transit
2. **Identity Layer**: Strong authentication, least privilege
3. **Monitoring Layer**: Logging, alerting, anomaly detection

### Security by Design

- Security considered at every stage
- Threat modeling for new features
- Security reviews before deployment
- Automated security testing
- Regular security audits

## Authentication & Authorization

### JWT Implementation

```python
### Security by Design

- Security considered at every stage
- Threat modeling for new features
- Security reviews before deployment
- Automated security testing
- Regular security audits

## Authentication & Authorization

### JWT Implementation

```python

## security/auth/jwt_handler.py

import jwt
import datetime
from typing import Dict, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class JWTHandler:
    """Secure JWT implementation with RS256."""

    def __init__(self):
        # Use RS256 (asymmetric) instead of HS256
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()
        self.algorithm = "RS256"
        self.token_lifetime = datetime.timedelta(hours=1)
        self.refresh_lifetime = datetime.timedelta(days=7)

    def generate_token(self, user_id: str, roles: List[str]) -> Dict[str, str]:
        """Generate access and refresh tokens."""
        now = datetime.datetime.utcnow()

        # Access token claims
        access_claims = {
            "sub": user_id,
            "roles": roles,
            "iat": now,
            "exp": now + self.token_lifetime,
            "type": "access",
            "jti": str(uuid.uuid4()),  # Unique token ID
        }

        # Refresh token claims
        refresh_claims = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.refresh_lifetime,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }

        access_token = jwt.encode(
            access_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        refresh_token = jwt.encode(
            refresh_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        # Store token JTIs for revocation
        self._store_token_jti(access_claims["jti"], access_claims["exp"])
        self._store_token_jti(refresh_claims["jti"], refresh_claims["exp"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(self.token_lifetime.total_seconds())
        }

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate token and check revocation."""
        try:
            # Decode and verify signature
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )

            # Check if token is revoked
            if self._is_token_revoked(claims["jti"]):
                raise jwt.InvalidTokenError("Token has been revoked")

            return claims

        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired", 401)
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {str(e)}", 401)

    def revoke_token(self, token: str) -> None:
        """Revoke a token by adding JTI to blacklist."""
        try:
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            self._revoke_token_jti(claims["jti"], claims["exp"])
        except jwt.InvalidTokenError:
            pass  # Invalid tokens don't need revocation
```text

from typing import Dict, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class JWTHandler:
    """Secure JWT implementation with RS256."""

    def __init__(self):
        # Use RS256 (asymmetric) instead of HS256
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()
        self.algorithm = "RS256"
        self.token_lifetime = datetime.timedelta(hours=1)
        self.refresh_lifetime = datetime.timedelta(days=7)

    def generate_token(self, user_id: str, roles: List[str]) -> Dict[str, str]:
        """Generate access and refresh tokens."""
        now = datetime.datetime.utcnow()

        # Access token claims
        access_claims = {
            "sub": user_id,
            "roles": roles,
            "iat": now,
            "exp": now + self.token_lifetime,
            "type": "access",
            "jti": str(uuid.uuid4()),  # Unique token ID
        }

        # Refresh token claims
        refresh_claims = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.refresh_lifetime,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }

        access_token = jwt.encode(
            access_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        refresh_token = jwt.encode(
            refresh_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        # Store token JTIs for revocation
        self._store_token_jti(access_claims["jti"], access_claims["exp"])
        self._store_token_jti(refresh_claims["jti"], refresh_claims["exp"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(self.token_lifetime.total_seconds())
        }

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate token and check revocation."""
        try:
            # Decode and verify signature
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )

            # Check if token is revoked
            if self._is_token_revoked(claims["jti"]):
                raise jwt.InvalidTokenError("Token has been revoked")

            return claims

        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired", 401)
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {str(e)}", 401)

    def revoke_token(self, token: str) -> None:
        """Revoke a token by adding JTI to blacklist."""
        try:
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            self._revoke_token_jti(claims["jti"], claims["exp"])
        except jwt.InvalidTokenError:
            pass  # Invalid tokens don't need revocation

```text
from typing import Dict, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class JWTHandler:
    """Secure JWT implementation with RS256."""

    def __init__(self):
        # Use RS256 (asymmetric) instead of HS256
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()
        self.algorithm = "RS256"
        self.token_lifetime = datetime.timedelta(hours=1)
        self.refresh_lifetime = datetime.timedelta(days=7)

    def generate_token(self, user_id: str, roles: List[str]) -> Dict[str, str]:
        """Generate access and refresh tokens."""
        now = datetime.datetime.utcnow()

        # Access token claims
        access_claims = {
            "sub": user_id,
            "roles": roles,
            "iat": now,
            "exp": now + self.token_lifetime,
            "type": "access",
            "jti": str(uuid.uuid4()),  # Unique token ID
        }

        # Refresh token claims
        refresh_claims = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.refresh_lifetime,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }

        access_token = jwt.encode(
            access_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        refresh_token = jwt.encode(
            refresh_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        # Store token JTIs for revocation
        self._store_token_jti(access_claims["jti"], access_claims["exp"])
        self._store_token_jti(refresh_claims["jti"], refresh_claims["exp"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(self.token_lifetime.total_seconds())
        }

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate token and check revocation."""
        try:
            # Decode and verify signature
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )

            # Check if token is revoked
            if self._is_token_revoked(claims["jti"]):
                raise jwt.InvalidTokenError("Token has been revoked")

            return claims

        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired", 401)
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {str(e)}", 401)

    def revoke_token(self, token: str) -> None:
        """Revoke a token by adding JTI to blacklist."""
        try:
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            self._revoke_token_jti(claims["jti"], claims["exp"])
        except jwt.InvalidTokenError:
            pass  # Invalid tokens don't need revocation

```text
    """Secure JWT implementation with RS256."""

    def __init__(self):
        # Use RS256 (asymmetric) instead of HS256
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()
        self.algorithm = "RS256"
        self.token_lifetime = datetime.timedelta(hours=1)
        self.refresh_lifetime = datetime.timedelta(days=7)

    def generate_token(self, user_id: str, roles: List[str]) -> Dict[str, str]:
        """Generate access and refresh tokens."""
        now = datetime.datetime.utcnow()

        # Access token claims
        access_claims = {
            "sub": user_id,
            "roles": roles,
            "iat": now,
            "exp": now + self.token_lifetime,
            "type": "access",
            "jti": str(uuid.uuid4()),  # Unique token ID
        }

        # Refresh token claims
        refresh_claims = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.refresh_lifetime,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }

        access_token = jwt.encode(
            access_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        refresh_token = jwt.encode(
            refresh_claims,
            self.private_key,
            algorithm=self.algorithm
        )

        # Store token JTIs for revocation
        self._store_token_jti(access_claims["jti"], access_claims["exp"])
        self._store_token_jti(refresh_claims["jti"], refresh_claims["exp"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(self.token_lifetime.total_seconds())
        }

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate token and check revocation."""
        try:
            # Decode and verify signature
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )

            # Check if token is revoked
            if self._is_token_revoked(claims["jti"]):
                raise jwt.InvalidTokenError("Token has been revoked")

            return claims

        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired", 401)
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {str(e)}", 401)

    def revoke_token(self, token: str) -> None:
        """Revoke a token by adding JTI to blacklist."""
        try:
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            self._revoke_token_jti(claims["jti"], claims["exp"])
        except jwt.InvalidTokenError:
            pass  # Invalid tokens don't need revocation

```text

### Role-Based Access Control (RBAC)

```python

```python
```python

```python

## security/auth/rbac.py

from enum import Enum
from typing import List, Set

class Role(Enum):
    """System roles with hierarchical permissions."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    """Granular permissions."""
    # Service management
    SERVICE_CREATE = "service:create"
    SERVICE_READ = "service:read"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"
    SERVICE_EXECUTE = "service:execute"

    # AI operations
    AI_INFERENCE = "ai:inference"
    AI_TRAIN = "ai:train"
    AI_CONFIG = "ai:config"

    # Security operations
    SECURITY_AUDIT = "security:audit"
    SECURITY_CONFIG = "security:config"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

## Role-permission mapping

ROLE_PERMISSIONS = {
    Role.ADMIN: set(Permission),  # All permissions
    Role.DEVELOPER: {
        Permission.SERVICE_CREATE,
        Permission.SERVICE_READ,
        Permission.SERVICE_UPDATE,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.AI_TRAIN,
        Permission.USER_READ,
    },
    Role.USER: {
        Permission.SERVICE_READ,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.USER_READ,
    },
    Role.GUEST: {
        Permission.SERVICE_READ,
    }
}

class RBACAuthorizer:
    """Role-based authorization system."""

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def authorize(self, user_roles: List[str], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        user_permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                user_permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue  # Invalid role

        return required_permission in user_permissions

    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """Get all permissions for user's roles."""
        permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue

        return permissions
```text

class Role(Enum):
    """System roles with hierarchical permissions."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    """Granular permissions."""
    # Service management
    SERVICE_CREATE = "service:create"
    SERVICE_READ = "service:read"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"
    SERVICE_EXECUTE = "service:execute"

    # AI operations
    AI_INFERENCE = "ai:inference"
    AI_TRAIN = "ai:train"
    AI_CONFIG = "ai:config"

    # Security operations
    SECURITY_AUDIT = "security:audit"
    SECURITY_CONFIG = "security:config"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

## Role-permission mapping

ROLE_PERMISSIONS = {
    Role.ADMIN: set(Permission),  # All permissions
    Role.DEVELOPER: {
        Permission.SERVICE_CREATE,
        Permission.SERVICE_READ,
        Permission.SERVICE_UPDATE,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.AI_TRAIN,
        Permission.USER_READ,
    },
    Role.USER: {
        Permission.SERVICE_READ,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.USER_READ,
    },
    Role.GUEST: {
        Permission.SERVICE_READ,
    }
}

class RBACAuthorizer:
    """Role-based authorization system."""

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def authorize(self, user_roles: List[str], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        user_permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                user_permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue  # Invalid role

        return required_permission in user_permissions

    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """Get all permissions for user's roles."""
        permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue

        return permissions

```text

class Role(Enum):
    """System roles with hierarchical permissions."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    """Granular permissions."""
    # Service management
    SERVICE_CREATE = "service:create"
    SERVICE_READ = "service:read"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"
    SERVICE_EXECUTE = "service:execute"

    # AI operations
    AI_INFERENCE = "ai:inference"
    AI_TRAIN = "ai:train"
    AI_CONFIG = "ai:config"

    # Security operations
    SECURITY_AUDIT = "security:audit"
    SECURITY_CONFIG = "security:config"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

## Role-permission mapping

ROLE_PERMISSIONS = {
    Role.ADMIN: set(Permission),  # All permissions
    Role.DEVELOPER: {
        Permission.SERVICE_CREATE,
        Permission.SERVICE_READ,
        Permission.SERVICE_UPDATE,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.AI_TRAIN,
        Permission.USER_READ,
    },
    Role.USER: {
        Permission.SERVICE_READ,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.USER_READ,
    },
    Role.GUEST: {
        Permission.SERVICE_READ,
    }
}

class RBACAuthorizer:
    """Role-based authorization system."""

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def authorize(self, user_roles: List[str], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        user_permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                user_permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue  # Invalid role

        return required_permission in user_permissions

    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """Get all permissions for user's roles."""
        permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue

        return permissions

```text
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    """Granular permissions."""
    # Service management
    SERVICE_CREATE = "service:create"
    SERVICE_READ = "service:read"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"
    SERVICE_EXECUTE = "service:execute"

    # AI operations
    AI_INFERENCE = "ai:inference"
    AI_TRAIN = "ai:train"
    AI_CONFIG = "ai:config"

    # Security operations
    SECURITY_AUDIT = "security:audit"
    SECURITY_CONFIG = "security:config"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

## Role-permission mapping

ROLE_PERMISSIONS = {
    Role.ADMIN: set(Permission),  # All permissions
    Role.DEVELOPER: {
        Permission.SERVICE_CREATE,
        Permission.SERVICE_READ,
        Permission.SERVICE_UPDATE,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.AI_TRAIN,
        Permission.USER_READ,
    },
    Role.USER: {
        Permission.SERVICE_READ,
        Permission.SERVICE_EXECUTE,
        Permission.AI_INFERENCE,
        Permission.USER_READ,
    },
    Role.GUEST: {
        Permission.SERVICE_READ,
    }
}

class RBACAuthorizer:
    """Role-based authorization system."""

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def authorize(self, user_roles: List[str], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        user_permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                user_permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue  # Invalid role

        return required_permission in user_permissions

    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """Get all permissions for user's roles."""
        permissions = set()

        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                continue

        return permissions

```text

### Multi-Factor Authentication (MFA)

```python

```python
```python

```python

## security/auth/mfa.py

import pyotp
import qrcode
from io import BytesIO

class MFAHandler:
    """Multi-factor authentication handler."""

    def generate_secret(self, user_id: str) -> Dict[str, str]:
        """Generate MFA secret and QR code."""
        # Generate random secret
        secret = pyotp.random_base32()

        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name='Syn_OS'
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')

        return {
            "secret": secret,
            "qr_code": base64.b64encode(buf.getvalue()).decode(),
            "uri": totp_uri
        }

    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)

        # Allow for time drift (±1 time step)
        return totp.verify(token, valid_window=1)

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery."""
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.digits, k=8))
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes
```text

from io import BytesIO

class MFAHandler:
    """Multi-factor authentication handler."""

    def generate_secret(self, user_id: str) -> Dict[str, str]:
        """Generate MFA secret and QR code."""
        # Generate random secret
        secret = pyotp.random_base32()

        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name='Syn_OS'
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')

        return {
            "secret": secret,
            "qr_code": base64.b64encode(buf.getvalue()).decode(),
            "uri": totp_uri
        }

    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)

        # Allow for time drift (±1 time step)
        return totp.verify(token, valid_window=1)

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery."""
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.digits, k=8))
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes

```text
from io import BytesIO

class MFAHandler:
    """Multi-factor authentication handler."""

    def generate_secret(self, user_id: str) -> Dict[str, str]:
        """Generate MFA secret and QR code."""
        # Generate random secret
        secret = pyotp.random_base32()

        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name='Syn_OS'
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')

        return {
            "secret": secret,
            "qr_code": base64.b64encode(buf.getvalue()).decode(),
            "uri": totp_uri
        }

    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)

        # Allow for time drift (±1 time step)
        return totp.verify(token, valid_window=1)

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery."""
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.digits, k=8))
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes

```text
    def generate_secret(self, user_id: str) -> Dict[str, str]:
        """Generate MFA secret and QR code."""
        # Generate random secret
        secret = pyotp.random_base32()

        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name='Syn_OS'
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')

        return {
            "secret": secret,
            "qr_code": base64.b64encode(buf.getvalue()).decode(),
            "uri": totp_uri
        }

    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)

        # Allow for time drift (±1 time step)
        return totp.verify(token, valid_window=1)

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery."""
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.digits, k=8))
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes

```text

## Data Protection

### Encryption at Rest

```python

```python
```python

```python

## security/crypto/encryption.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DataEncryption:
    """Data encryption handler."""

    def __init__(self, master_key: bytes):
        self.master_key = master_key

    def derive_key(self, salt: bytes, context: str) -> bytes:
        """Derive encryption key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt + context.encode(),
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_field(self, data: str, field_name: str) -> Dict[str, str]:
        """Encrypt a single field with unique key."""
        salt = os.urandom(16)
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        encrypted = f.encrypt(data.encode())

        return {
            "ciphertext": base64.b64encode(encrypted).decode(),
            "salt": base64.b64encode(salt).decode(),
            "algorithm": "AES-256-GCM",
            "version": "1.0"
        }

    def decrypt_field(self, encrypted_data: Dict[str, str], field_name: str) -> str:
        """Decrypt a field."""
        salt = base64.b64decode(encrypted_data["salt"])
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        return f.decrypt(ciphertext).decode()
```text

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DataEncryption:
    """Data encryption handler."""

    def __init__(self, master_key: bytes):
        self.master_key = master_key

    def derive_key(self, salt: bytes, context: str) -> bytes:
        """Derive encryption key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt + context.encode(),
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_field(self, data: str, field_name: str) -> Dict[str, str]:
        """Encrypt a single field with unique key."""
        salt = os.urandom(16)
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        encrypted = f.encrypt(data.encode())

        return {
            "ciphertext": base64.b64encode(encrypted).decode(),
            "salt": base64.b64encode(salt).decode(),
            "algorithm": "AES-256-GCM",
            "version": "1.0"
        }

    def decrypt_field(self, encrypted_data: Dict[str, str], field_name: str) -> str:
        """Decrypt a field."""
        salt = base64.b64decode(encrypted_data["salt"])
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        return f.decrypt(ciphertext).decode()

```text
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DataEncryption:
    """Data encryption handler."""

    def __init__(self, master_key: bytes):
        self.master_key = master_key

    def derive_key(self, salt: bytes, context: str) -> bytes:
        """Derive encryption key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt + context.encode(),
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_field(self, data: str, field_name: str) -> Dict[str, str]:
        """Encrypt a single field with unique key."""
        salt = os.urandom(16)
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        encrypted = f.encrypt(data.encode())

        return {
            "ciphertext": base64.b64encode(encrypted).decode(),
            "salt": base64.b64encode(salt).decode(),
            "algorithm": "AES-256-GCM",
            "version": "1.0"
        }

    def decrypt_field(self, encrypted_data: Dict[str, str], field_name: str) -> str:
        """Decrypt a field."""
        salt = base64.b64decode(encrypted_data["salt"])
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        return f.decrypt(ciphertext).decode()

```text

    def __init__(self, master_key: bytes):
        self.master_key = master_key

    def derive_key(self, salt: bytes, context: str) -> bytes:
        """Derive encryption key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt + context.encode(),
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_field(self, data: str, field_name: str) -> Dict[str, str]:
        """Encrypt a single field with unique key."""
        salt = os.urandom(16)
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        encrypted = f.encrypt(data.encode())

        return {
            "ciphertext": base64.b64encode(encrypted).decode(),
            "salt": base64.b64encode(salt).decode(),
            "algorithm": "AES-256-GCM",
            "version": "1.0"
        }

    def decrypt_field(self, encrypted_data: Dict[str, str], field_name: str) -> str:
        """Decrypt a field."""
        salt = base64.b64decode(encrypted_data["salt"])
        key = self.derive_key(salt, field_name)
        f = Fernet(key)

        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        return f.decrypt(ciphertext).decode()

```text

### Database Security

```sql
```sql

```sql
```sql

- - Database security configuration
- - Enable row-level security

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

- - Create policies

CREATE POLICY user_isolation ON users
    FOR ALL
    TO application_role
    USING (auth.uid() = id);

- - Encrypt sensitive columns

CREATE EXTENSION IF NOT EXISTS pgcrypto;

- - Encrypted user table

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,

    - - Store password hash, never plaintext

    password_hash TEXT NOT NULL,

    - - Encrypt PII

    full_name BYTEA,  -- Encrypted
    phone_number BYTEA,  -- Encrypted

    - - Audit fields

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ
);

- - Audit log table

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

- - Index for performance

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```text

- - Create policies

CREATE POLICY user_isolation ON users
    FOR ALL
    TO application_role
    USING (auth.uid() = id);

- - Encrypt sensitive columns

CREATE EXTENSION IF NOT EXISTS pgcrypto;

- - Encrypted user table

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,

    - - Store password hash, never plaintext

    password_hash TEXT NOT NULL,

    - - Encrypt PII

    full_name BYTEA,  -- Encrypted
    phone_number BYTEA,  -- Encrypted

    - - Audit fields

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ
);

- - Audit log table

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

- - Index for performance

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

```text
CREATE POLICY user_isolation ON users
    FOR ALL
    TO application_role
    USING (auth.uid() = id);

- - Encrypt sensitive columns

CREATE EXTENSION IF NOT EXISTS pgcrypto;

- - Encrypted user table

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,

    - - Store password hash, never plaintext

    password_hash TEXT NOT NULL,

    - - Encrypt PII

    full_name BYTEA,  -- Encrypted
    phone_number BYTEA,  -- Encrypted

    - - Audit fields

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ
);

- - Audit log table

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

- - Index for performance

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

```text
- - Encrypt sensitive columns

CREATE EXTENSION IF NOT EXISTS pgcrypto;

- - Encrypted user table

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,

    - - Store password hash, never plaintext

    password_hash TEXT NOT NULL,

    - - Encrypt PII

    full_name BYTEA,  -- Encrypted
    phone_number BYTEA,  -- Encrypted

    - - Audit fields

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ
);

- - Audit log table

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

- - Index for performance

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

```text

## Network Security

### Service Mesh Security

```yaml

```yaml
```yaml

```yaml

## istio/security-policy.yaml

apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: syn-os
spec:
  mtls:
    mode: STRICT  # Enforce mTLS

- --

apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: service-access
  namespace: syn-os
spec:
  selector:
    matchLabels:
      app: consciousness
  rules:

  - from:
    - source:

        principals: ["cluster.local/ns/syn-os/sa/orchestrator"]
    to:

    - operation:

        methods: ["GET", "POST"]
        paths: ["/api/v1/*"]
```text

metadata:
  name: default
  namespace: syn-os
spec:
  mtls:
    mode: STRICT  # Enforce mTLS

- --

apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: service-access
  namespace: syn-os
spec:
  selector:
    matchLabels:
      app: consciousness
  rules:

  - from:
    - source:

        principals: ["cluster.local/ns/syn-os/sa/orchestrator"]
    to:

    - operation:

        methods: ["GET", "POST"]
        paths: ["/api/v1/*"]

```text
metadata:
  name: default
  namespace: syn-os
spec:
  mtls:
    mode: STRICT  # Enforce mTLS

- --

apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: service-access
  namespace: syn-os
spec:
  selector:
    matchLabels:
      app: consciousness
  rules:

  - from:
    - source:

        principals: ["cluster.local/ns/syn-os/sa/orchestrator"]
    to:

    - operation:

        methods: ["GET", "POST"]
        paths: ["/api/v1/*"]

```text
    mode: STRICT  # Enforce mTLS

- --

apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: service-access
  namespace: syn-os
spec:
  selector:
    matchLabels:
      app: consciousness
  rules:

  - from:
    - source:

        principals: ["cluster.local/ns/syn-os/sa/orchestrator"]
    to:

    - operation:

        methods: ["GET", "POST"]
        paths: ["/api/v1/*"]

```text

### Network Policies

```yaml

```yaml
```yaml

```yaml

## kubernetes/network-policies.yaml

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: syn-os
spec:
  podSelector: {}
  policyTypes:

  - Ingress

- --

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-orchestrator-to-services
  namespace: syn-os
spec:
  podSelector:
    matchLabels:
      tier: service
  policyTypes:

  - Ingress

  ingress:

  - from:
    - podSelector:

        matchLabels:
          app: orchestrator
    ports:

    - protocol: TCP

      port: 8080
```text

metadata:
  name: deny-all-ingress
  namespace: syn-os
spec:
  podSelector: {}
  policyTypes:

  - Ingress

- --

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-orchestrator-to-services
  namespace: syn-os
spec:
  podSelector:
    matchLabels:
      tier: service
  policyTypes:

  - Ingress

  ingress:

  - from:
    - podSelector:

        matchLabels:
          app: orchestrator
    ports:

    - protocol: TCP

      port: 8080

```text
metadata:
  name: deny-all-ingress
  namespace: syn-os
spec:
  podSelector: {}
  policyTypes:

  - Ingress

- --

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-orchestrator-to-services
  namespace: syn-os
spec:
  podSelector:
    matchLabels:
      tier: service
  policyTypes:

  - Ingress

  ingress:

  - from:
    - podSelector:

        matchLabels:
          app: orchestrator
    ports:

    - protocol: TCP

      port: 8080

```text
  policyTypes:

  - Ingress

- --

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-orchestrator-to-services
  namespace: syn-os
spec:
  podSelector:
    matchLabels:
      tier: service
  policyTypes:

  - Ingress

  ingress:

  - from:
    - podSelector:

        matchLabels:
          app: orchestrator
    ports:

    - protocol: TCP

      port: 8080

```text

### API Rate Limiting

```python

```python
```python

```python

## security/ratelimit.py

import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self):
        self.buckets: Dict[str, Tuple[float, int]] = defaultdict(
            lambda: (time.time(), 0)
        )

        # Rate limit configurations
        self.limits = {
            "default": (100, 60),      # 100 requests per 60 seconds
            "auth": (5, 60),           # 5 auth attempts per 60 seconds
            "ai_inference": (10, 60),  # 10 AI requests per 60 seconds
            "admin": (1000, 60),       # Higher limit for admins
        }

    def is_allowed(self, key: str, endpoint_type: str = "default") -> bool:
        """Check if request is allowed."""
        limit, window = self.limits.get(endpoint_type, self.limits["default"])

        now = time.time()
        window_start, count = self.buckets[key]

        # Reset window if expired
        if now - window_start > window:
            self.buckets[key] = (now, 1)
            return True

        # Check limit
        if count >= limit:
            return False

        # Increment counter
        self.buckets[key] = (window_start, count + 1)
        return True

    def get_retry_after(self, key: str, endpoint_type: str = "default") -> int:
        """Get seconds until rate limit resets."""
        _, window = self.limits.get(endpoint_type, self.limits["default"])
        window_start, _ = self.buckets[key]

        elapsed = time.time() - window_start
        return max(0, int(window - elapsed))
```text

from typing import Dict, Tuple

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self):
        self.buckets: Dict[str, Tuple[float, int]] = defaultdict(
            lambda: (time.time(), 0)
        )

        # Rate limit configurations
        self.limits = {
            "default": (100, 60),      # 100 requests per 60 seconds
            "auth": (5, 60),           # 5 auth attempts per 60 seconds
            "ai_inference": (10, 60),  # 10 AI requests per 60 seconds
            "admin": (1000, 60),       # Higher limit for admins
        }

    def is_allowed(self, key: str, endpoint_type: str = "default") -> bool:
        """Check if request is allowed."""
        limit, window = self.limits.get(endpoint_type, self.limits["default"])

        now = time.time()
        window_start, count = self.buckets[key]

        # Reset window if expired
        if now - window_start > window:
            self.buckets[key] = (now, 1)
            return True

        # Check limit
        if count >= limit:
            return False

        # Increment counter
        self.buckets[key] = (window_start, count + 1)
        return True

    def get_retry_after(self, key: str, endpoint_type: str = "default") -> int:
        """Get seconds until rate limit resets."""
        _, window = self.limits.get(endpoint_type, self.limits["default"])
        window_start, _ = self.buckets[key]

        elapsed = time.time() - window_start
        return max(0, int(window - elapsed))

```text
from typing import Dict, Tuple

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self):
        self.buckets: Dict[str, Tuple[float, int]] = defaultdict(
            lambda: (time.time(), 0)
        )

        # Rate limit configurations
        self.limits = {
            "default": (100, 60),      # 100 requests per 60 seconds
            "auth": (5, 60),           # 5 auth attempts per 60 seconds
            "ai_inference": (10, 60),  # 10 AI requests per 60 seconds
            "admin": (1000, 60),       # Higher limit for admins
        }

    def is_allowed(self, key: str, endpoint_type: str = "default") -> bool:
        """Check if request is allowed."""
        limit, window = self.limits.get(endpoint_type, self.limits["default"])

        now = time.time()
        window_start, count = self.buckets[key]

        # Reset window if expired
        if now - window_start > window:
            self.buckets[key] = (now, 1)
            return True

        # Check limit
        if count >= limit:
            return False

        # Increment counter
        self.buckets[key] = (window_start, count + 1)
        return True

    def get_retry_after(self, key: str, endpoint_type: str = "default") -> int:
        """Get seconds until rate limit resets."""
        _, window = self.limits.get(endpoint_type, self.limits["default"])
        window_start, _ = self.buckets[key]

        elapsed = time.time() - window_start
        return max(0, int(window - elapsed))

```text
    def __init__(self):
        self.buckets: Dict[str, Tuple[float, int]] = defaultdict(
            lambda: (time.time(), 0)
        )

        # Rate limit configurations
        self.limits = {
            "default": (100, 60),      # 100 requests per 60 seconds
            "auth": (5, 60),           # 5 auth attempts per 60 seconds
            "ai_inference": (10, 60),  # 10 AI requests per 60 seconds
            "admin": (1000, 60),       # Higher limit for admins
        }

    def is_allowed(self, key: str, endpoint_type: str = "default") -> bool:
        """Check if request is allowed."""
        limit, window = self.limits.get(endpoint_type, self.limits["default"])

        now = time.time()
        window_start, count = self.buckets[key]

        # Reset window if expired
        if now - window_start > window:
            self.buckets[key] = (now, 1)
            return True

        # Check limit
        if count >= limit:
            return False

        # Increment counter
        self.buckets[key] = (window_start, count + 1)
        return True

    def get_retry_after(self, key: str, endpoint_type: str = "default") -> int:
        """Get seconds until rate limit resets."""
        _, window = self.limits.get(endpoint_type, self.limits["default"])
        window_start, _ = self.buckets[key]

        elapsed = time.time() - window_start
        return max(0, int(window - elapsed))

```text

## Container Security

### Dockerfile Security

```dockerfile

```dockerfile
```dockerfile

```dockerfile

## Base image with security updates

FROM python:3.11-slim-bookworm AS base

## Security: Run as non-root user

RUN groupadd -r synos && useradd -r -g synos synos

## Security: Update and install only necessary packages

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

## Build stage

FROM base AS builder

## Install build dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements first for better caching

COPY requirements.txt /tmp/
RUN pip install --user --no-cache-dir -r /tmp/requirements.txt

## Runtime stage

FROM base AS runtime

## Copy installed packages from builder

COPY --from=builder /root/.local /home/synos/.local

## Security: Set proper permissions

WORKDIR /app
COPY --chown=synos:synos . /app

## Security: Drop all capabilities

USER synos

## Security: Read-only root filesystem
## Mount points for writable data should be defined in docker-compose

## Health check

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health').raise_for_status()"

## Run with minimal privileges

ENTRYPOINT ["python", "-u"]
CMD ["main.py"]
```text
## Security: Run as non-root user

RUN groupadd -r synos && useradd -r -g synos synos

## Security: Update and install only necessary packages

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

## Build stage

FROM base AS builder

## Install build dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements first for better caching

COPY requirements.txt /tmp/
RUN pip install --user --no-cache-dir -r /tmp/requirements.txt

## Runtime stage

FROM base AS runtime

## Copy installed packages from builder

COPY --from=builder /root/.local /home/synos/.local

## Security: Set proper permissions

WORKDIR /app
COPY --chown=synos:synos . /app

## Security: Drop all capabilities

USER synos

## Security: Read-only root filesystem
## Mount points for writable data should be defined in docker-compose

## Health check

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health').raise_for_status()"

## Run with minimal privileges

ENTRYPOINT ["python", "-u"]
CMD ["main.py"]

```text

## Security: Run as non-root user

RUN groupadd -r synos && useradd -r -g synos synos

## Security: Update and install only necessary packages

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

## Build stage

FROM base AS builder

## Install build dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements first for better caching

COPY requirements.txt /tmp/
RUN pip install --user --no-cache-dir -r /tmp/requirements.txt

## Runtime stage

FROM base AS runtime

## Copy installed packages from builder

COPY --from=builder /root/.local /home/synos/.local

## Security: Set proper permissions

WORKDIR /app
COPY --chown=synos:synos . /app

## Security: Drop all capabilities

USER synos

## Security: Read-only root filesystem
## Mount points for writable data should be defined in docker-compose

## Health check

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health').raise_for_status()"

## Run with minimal privileges

ENTRYPOINT ["python", "-u"]
CMD ["main.py"]

```text
## Security: Update and install only necessary packages

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

## Build stage

FROM base AS builder

## Install build dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements first for better caching

COPY requirements.txt /tmp/
RUN pip install --user --no-cache-dir -r /tmp/requirements.txt

## Runtime stage

FROM base AS runtime

## Copy installed packages from builder

COPY --from=builder /root/.local /home/synos/.local

## Security: Set proper permissions

WORKDIR /app
COPY --chown=synos:synos . /app

## Security: Drop all capabilities

USER synos

## Security: Read-only root filesystem
## Mount points for writable data should be defined in docker-compose

## Health check

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health').raise_for_status()"

## Run with minimal privileges

ENTRYPOINT ["python", "-u"]
CMD ["main.py"]

```text

### Container Scanning

```yaml

```yaml
```yaml

```yaml

## .github/workflows/container-security.yml

name: Container Security Scan

on:
  push:
    paths:

      - '**/Dockerfile'
      - '**/*.dockerfile'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner

        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results

        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Hadolint

        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning
```text

on:
  push:
    paths:

      - '**/Dockerfile'
      - '**/*.dockerfile'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner

        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results

        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Hadolint

        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning

```text
on:
  push:
    paths:

      - '**/Dockerfile'
      - '**/*.dockerfile'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner

        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results

        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Hadolint

        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning

```text
      - '**/*.dockerfile'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner

        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results

        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Hadolint

        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning

```text

### Kubernetes Security

```yaml

```yaml
```yaml

```yaml

## kubernetes/security-context.yaml

apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault

  containers:

  - name: app

    image: synos/app:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:

          - ALL

        add:

          - NET_BIND_SERVICE

    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
      requests:
        memory: "256Mi"
        cpu: "250m"

    volumeMounts:

    - name: tmp

      mountPath: /tmp

    - name: cache

      mountPath: /app/cache

  volumes:

  - name: tmp

    emptyDir: {}

  - name: cache

    emptyDir: {}
```text

metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault

  containers:

  - name: app

    image: synos/app:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:

          - ALL

        add:

          - NET_BIND_SERVICE

    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
      requests:
        memory: "256Mi"
        cpu: "250m"

    volumeMounts:

    - name: tmp

      mountPath: /tmp

    - name: cache

      mountPath: /app/cache

  volumes:

  - name: tmp

    emptyDir: {}

  - name: cache

    emptyDir: {}

```text
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault

  containers:

  - name: app

    image: synos/app:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:

          - ALL

        add:

          - NET_BIND_SERVICE

    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
      requests:
        memory: "256Mi"
        cpu: "250m"

    volumeMounts:

    - name: tmp

      mountPath: /tmp

    - name: cache

      mountPath: /app/cache

  volumes:

  - name: tmp

    emptyDir: {}

  - name: cache

    emptyDir: {}

```text
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault

  containers:

  - name: app

    image: synos/app:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:

          - ALL

        add:

          - NET_BIND_SERVICE

    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
      requests:
        memory: "256Mi"
        cpu: "250m"

    volumeMounts:

    - name: tmp

      mountPath: /tmp

    - name: cache

      mountPath: /app/cache

  volumes:

  - name: tmp

    emptyDir: {}

  - name: cache

    emptyDir: {}

```text

## Code Security

### Input Validation

```python

```python
```python

```python

## security/validation.py

from typing import Any, Dict, List
import re
from pydantic import BaseModel, validator, constr

class SecurityValidator:
    """Input validation for security."""

    # Regex patterns for validation
    PATTERNS = {
        "username": r"^[a-zA-Z0-9_-]{3,32}$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "safe_string": r"^[a-zA-Z0-9\s\-_.]+$",
    }

    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username format."""
        if not re.match(cls.PATTERNS["username"], username):
            raise ValueError("Invalid username format")
        return username

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format."""
        if not re.match(cls.PATTERNS["email"], email):
            raise ValueError("Invalid email format")
        return email.lower()

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Remove potentially dangerous HTML."""
        # Remove script tags and event handlers
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

        # Escape remaining HTML
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        return text

    @classmethod
    def validate_file_path(cls, path: str) -> str:
        """Validate file path to prevent directory traversal."""
        # Remove any directory traversal attempts
        path = path.replace('../', '').replace('..\\', '')

        # Ensure path doesn't start with /
        if path.startswith('/'):
            path = path[1:]

        # Validate characters
        if not re.match(r'^[a-zA-Z0-9/_\-\.]+$', path):
            raise ValueError("Invalid file path")

        return path

## Pydantic models for automatic validation

class UserRegistration(BaseModel):
    username: constr(regex=r"^[a-zA-Z0-9_-]{3,32}$")
    email: constr(regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: constr(min_length=8, max_length=128)

    @validator('password')
    def password_complexity(cls, v):
        """Ensure password meets complexity requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
```text

from pydantic import BaseModel, validator, constr

class SecurityValidator:
    """Input validation for security."""

    # Regex patterns for validation
    PATTERNS = {
        "username": r"^[a-zA-Z0-9_-]{3,32}$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "safe_string": r"^[a-zA-Z0-9\s\-_.]+$",
    }

    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username format."""
        if not re.match(cls.PATTERNS["username"], username):
            raise ValueError("Invalid username format")
        return username

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format."""
        if not re.match(cls.PATTERNS["email"], email):
            raise ValueError("Invalid email format")
        return email.lower()

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Remove potentially dangerous HTML."""
        # Remove script tags and event handlers
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

        # Escape remaining HTML
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        return text

    @classmethod
    def validate_file_path(cls, path: str) -> str:
        """Validate file path to prevent directory traversal."""
        # Remove any directory traversal attempts
        path = path.replace('../', '').replace('..\\', '')

        # Ensure path doesn't start with /
        if path.startswith('/'):
            path = path[1:]

        # Validate characters
        if not re.match(r'^[a-zA-Z0-9/_\-\.]+$', path):
            raise ValueError("Invalid file path")

        return path

## Pydantic models for automatic validation

class UserRegistration(BaseModel):
    username: constr(regex=r"^[a-zA-Z0-9_-]{3,32}$")
    email: constr(regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: constr(min_length=8, max_length=128)

    @validator('password')
    def password_complexity(cls, v):
        """Ensure password meets complexity requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v

```text
from pydantic import BaseModel, validator, constr

class SecurityValidator:
    """Input validation for security."""

    # Regex patterns for validation
    PATTERNS = {
        "username": r"^[a-zA-Z0-9_-]{3,32}$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "safe_string": r"^[a-zA-Z0-9\s\-_.]+$",
    }

    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username format."""
        if not re.match(cls.PATTERNS["username"], username):
            raise ValueError("Invalid username format")
        return username

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format."""
        if not re.match(cls.PATTERNS["email"], email):
            raise ValueError("Invalid email format")
        return email.lower()

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Remove potentially dangerous HTML."""
        # Remove script tags and event handlers
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

        # Escape remaining HTML
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        return text

    @classmethod
    def validate_file_path(cls, path: str) -> str:
        """Validate file path to prevent directory traversal."""
        # Remove any directory traversal attempts
        path = path.replace('../', '').replace('..\\', '')

        # Ensure path doesn't start with /
        if path.startswith('/'):
            path = path[1:]

        # Validate characters
        if not re.match(r'^[a-zA-Z0-9/_\-\.]+$', path):
            raise ValueError("Invalid file path")

        return path

## Pydantic models for automatic validation

class UserRegistration(BaseModel):
    username: constr(regex=r"^[a-zA-Z0-9_-]{3,32}$")
    email: constr(regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: constr(min_length=8, max_length=128)

    @validator('password')
    def password_complexity(cls, v):
        """Ensure password meets complexity requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v

```text
    # Regex patterns for validation
    PATTERNS = {
        "username": r"^[a-zA-Z0-9_-]{3,32}$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "safe_string": r"^[a-zA-Z0-9\s\-_.]+$",
    }

    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username format."""
        if not re.match(cls.PATTERNS["username"], username):
            raise ValueError("Invalid username format")
        return username

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format."""
        if not re.match(cls.PATTERNS["email"], email):
            raise ValueError("Invalid email format")
        return email.lower()

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Remove potentially dangerous HTML."""
        # Remove script tags and event handlers
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

        # Escape remaining HTML
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        return text

    @classmethod
    def validate_file_path(cls, path: str) -> str:
        """Validate file path to prevent directory traversal."""
        # Remove any directory traversal attempts
        path = path.replace('../', '').replace('..\\', '')

        # Ensure path doesn't start with /
        if path.startswith('/'):
            path = path[1:]

        # Validate characters
        if not re.match(r'^[a-zA-Z0-9/_\-\.]+$', path):
            raise ValueError("Invalid file path")

        return path

## Pydantic models for automatic validation

class UserRegistration(BaseModel):
    username: constr(regex=r"^[a-zA-Z0-9_-]{3,32}$")
    email: constr(regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: constr(min_length=8, max_length=128)

    @validator('password')
    def password_complexity(cls, v):
        """Ensure password meets complexity requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v

```text

### SQL Injection Prevention

```python

```python
```python

```python

## security/database.py

from typing import Any, List, Tuple
import psycopg2
from psycopg2 import sql

class SecureDatabase:
    """Secure database operations."""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)

    def execute_query(self, query: str, params: Tuple[Any, ...] = None) -> List[Any]:
        """Execute parameterized query safely."""
        with self.conn.cursor() as cursor:
            # Always use parameterized queries
            cursor.execute(query, params)
            return cursor.fetchall()

    def insert_user(self, username: str, email: str, password_hash: str) -> int:
        """Safely insert user."""
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """

        with self.conn.cursor() as cursor:
            cursor.execute(query, (username, email, password_hash))
            self.conn.commit()
            return cursor.fetchone()[0]

    def dynamic_query(self, table: str, columns: List[str], conditions: Dict[str, Any]) -> List[Any]:
        """Build dynamic query safely."""
        # Validate table name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError("Invalid table name")

        # Build query using sql.SQL
        query = sql.SQL("SELECT {} FROM {} WHERE {}").format(
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.Identifier(table),
            sql.SQL(' AND ').join(
                sql.SQL("{} = %s").format(sql.Identifier(k))
                for k in conditions.keys()
            )
        )

        with self.conn.cursor() as cursor:
            cursor.execute(query, list(conditions.values()))
            return cursor.fetchall()
```text

from psycopg2 import sql

class SecureDatabase:
    """Secure database operations."""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)

    def execute_query(self, query: str, params: Tuple[Any, ...] = None) -> List[Any]:
        """Execute parameterized query safely."""
        with self.conn.cursor() as cursor:
            # Always use parameterized queries
            cursor.execute(query, params)
            return cursor.fetchall()

    def insert_user(self, username: str, email: str, password_hash: str) -> int:
        """Safely insert user."""
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """

        with self.conn.cursor() as cursor:
            cursor.execute(query, (username, email, password_hash))
            self.conn.commit()
            return cursor.fetchone()[0]

    def dynamic_query(self, table: str, columns: List[str], conditions: Dict[str, Any]) -> List[Any]:
        """Build dynamic query safely."""
        # Validate table name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError("Invalid table name")

        # Build query using sql.SQL
        query = sql.SQL("SELECT {} FROM {} WHERE {}").format(
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.Identifier(table),
            sql.SQL(' AND ').join(
                sql.SQL("{} = %s").format(sql.Identifier(k))
                for k in conditions.keys()
            )
        )

        with self.conn.cursor() as cursor:
            cursor.execute(query, list(conditions.values()))
            return cursor.fetchall()

```text
from psycopg2 import sql

class SecureDatabase:
    """Secure database operations."""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)

    def execute_query(self, query: str, params: Tuple[Any, ...] = None) -> List[Any]:
        """Execute parameterized query safely."""
        with self.conn.cursor() as cursor:
            # Always use parameterized queries
            cursor.execute(query, params)
            return cursor.fetchall()

    def insert_user(self, username: str, email: str, password_hash: str) -> int:
        """Safely insert user."""
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """

        with self.conn.cursor() as cursor:
            cursor.execute(query, (username, email, password_hash))
            self.conn.commit()
            return cursor.fetchone()[0]

    def dynamic_query(self, table: str, columns: List[str], conditions: Dict[str, Any]) -> List[Any]:
        """Build dynamic query safely."""
        # Validate table name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError("Invalid table name")

        # Build query using sql.SQL
        query = sql.SQL("SELECT {} FROM {} WHERE {}").format(
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.Identifier(table),
            sql.SQL(' AND ').join(
                sql.SQL("{} = %s").format(sql.Identifier(k))
                for k in conditions.keys()
            )
        )

        with self.conn.cursor() as cursor:
            cursor.execute(query, list(conditions.values()))
            return cursor.fetchall()

```text
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)

    def execute_query(self, query: str, params: Tuple[Any, ...] = None) -> List[Any]:
        """Execute parameterized query safely."""
        with self.conn.cursor() as cursor:
            # Always use parameterized queries
            cursor.execute(query, params)
            return cursor.fetchall()

    def insert_user(self, username: str, email: str, password_hash: str) -> int:
        """Safely insert user."""
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """

        with self.conn.cursor() as cursor:
            cursor.execute(query, (username, email, password_hash))
            self.conn.commit()
            return cursor.fetchone()[0]

    def dynamic_query(self, table: str, columns: List[str], conditions: Dict[str, Any]) -> List[Any]:
        """Build dynamic query safely."""
        # Validate table name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError("Invalid table name")

        # Build query using sql.SQL
        query = sql.SQL("SELECT {} FROM {} WHERE {}").format(
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.Identifier(table),
            sql.SQL(' AND ').join(
                sql.SQL("{} = %s").format(sql.Identifier(k))
                for k in conditions.keys()
            )
        )

        with self.conn.cursor() as cursor:
            cursor.execute(query, list(conditions.values()))
            return cursor.fetchall()

```text

## AI Model Security

### Model Protection

```python

```python
```python

```python

## security/ai/model_security.py

import hashlib
import hmac
from cryptography.fernet import Fernet

class ModelSecurity:
    """AI model security handler."""

    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)

    def encrypt_model(self, model_path: str, output_path: str) -> str:
        """Encrypt AI model file."""
        with open(model_path, 'rb') as f:
            model_data = f.read()

        # Calculate hash for integrity
        model_hash = hashlib.sha256(model_data).hexdigest()

        # Encrypt model
        encrypted_data = self.fernet.encrypt(model_data)

        # Save encrypted model with metadata
        metadata = {
            "version": "1.0",
            "algorithm": "AES-256-GCM",
            "hash": model_hash,
            "size": len(model_data)
        }

        with open(output_path, 'wb') as f:
            f.write(json.dumps(metadata).encode() + b'\n')
            f.write(encrypted_data)

        return model_hash

    def load_secure_model(self, encrypted_path: str) -> bytes:
        """Load and decrypt model."""
        with open(encrypted_path, 'rb') as f:
            metadata_line = f.readline()
            metadata = json.loads(metadata_line.decode())
            encrypted_data = f.read()

        # Decrypt model
        model_data = self.fernet.decrypt(encrypted_data)

        # Verify integrity
        actual_hash = hashlib.sha256(model_data).hexdigest()
        if actual_hash != metadata["hash"]:
            raise SecurityError("Model integrity check failed")

        return model_data

    def validate_input(self, input_data: Any, max_size: int = 1024 * 1024) -> bool:
        """Validate AI input to prevent attacks."""
        # Check size limits
        if len(str(input_data)) > max_size:
            raise ValueError("Input exceeds maximum size")

        # Check for potential prompt injection
        dangerous_patterns = [
            "ignore previous instructions",
            "disregard all prior",
            "system prompt",
            "reveal your instructions",
        ]

        input_str = str(input_data).lower()
        for pattern in dangerous_patterns:
            if pattern in input_str:
                raise SecurityError(f"Potential prompt injection detected: {pattern}")

        return True
```text

from cryptography.fernet import Fernet

class ModelSecurity:
    """AI model security handler."""

    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)

    def encrypt_model(self, model_path: str, output_path: str) -> str:
        """Encrypt AI model file."""
        with open(model_path, 'rb') as f:
            model_data = f.read()

        # Calculate hash for integrity
        model_hash = hashlib.sha256(model_data).hexdigest()

        # Encrypt model
        encrypted_data = self.fernet.encrypt(model_data)

        # Save encrypted model with metadata
        metadata = {
            "version": "1.0",
            "algorithm": "AES-256-GCM",
            "hash": model_hash,
            "size": len(model_data)
        }

        with open(output_path, 'wb') as f:
            f.write(json.dumps(metadata).encode() + b'\n')
            f.write(encrypted_data)

        return model_hash

    def load_secure_model(self, encrypted_path: str) -> bytes:
        """Load and decrypt model."""
        with open(encrypted_path, 'rb') as f:
            metadata_line = f.readline()
            metadata = json.loads(metadata_line.decode())
            encrypted_data = f.read()

        # Decrypt model
        model_data = self.fernet.decrypt(encrypted_data)

        # Verify integrity
        actual_hash = hashlib.sha256(model_data).hexdigest()
        if actual_hash != metadata["hash"]:
            raise SecurityError("Model integrity check failed")

        return model_data

    def validate_input(self, input_data: Any, max_size: int = 1024 * 1024) -> bool:
        """Validate AI input to prevent attacks."""
        # Check size limits
        if len(str(input_data)) > max_size:
            raise ValueError("Input exceeds maximum size")

        # Check for potential prompt injection
        dangerous_patterns = [
            "ignore previous instructions",
            "disregard all prior",
            "system prompt",
            "reveal your instructions",
        ]

        input_str = str(input_data).lower()
        for pattern in dangerous_patterns:
            if pattern in input_str:
                raise SecurityError(f"Potential prompt injection detected: {pattern}")

        return True

```text
from cryptography.fernet import Fernet

class ModelSecurity:
    """AI model security handler."""

    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)

    def encrypt_model(self, model_path: str, output_path: str) -> str:
        """Encrypt AI model file."""
        with open(model_path, 'rb') as f:
            model_data = f.read()

        # Calculate hash for integrity
        model_hash = hashlib.sha256(model_data).hexdigest()

        # Encrypt model
        encrypted_data = self.fernet.encrypt(model_data)

        # Save encrypted model with metadata
        metadata = {
            "version": "1.0",
            "algorithm": "AES-256-GCM",
            "hash": model_hash,
            "size": len(model_data)
        }

        with open(output_path, 'wb') as f:
            f.write(json.dumps(metadata).encode() + b'\n')
            f.write(encrypted_data)

        return model_hash

    def load_secure_model(self, encrypted_path: str) -> bytes:
        """Load and decrypt model."""
        with open(encrypted_path, 'rb') as f:
            metadata_line = f.readline()
            metadata = json.loads(metadata_line.decode())
            encrypted_data = f.read()

        # Decrypt model
        model_data = self.fernet.decrypt(encrypted_data)

        # Verify integrity
        actual_hash = hashlib.sha256(model_data).hexdigest()
        if actual_hash != metadata["hash"]:
            raise SecurityError("Model integrity check failed")

        return model_data

    def validate_input(self, input_data: Any, max_size: int = 1024 * 1024) -> bool:
        """Validate AI input to prevent attacks."""
        # Check size limits
        if len(str(input_data)) > max_size:
            raise ValueError("Input exceeds maximum size")

        # Check for potential prompt injection
        dangerous_patterns = [
            "ignore previous instructions",
            "disregard all prior",
            "system prompt",
            "reveal your instructions",
        ]

        input_str = str(input_data).lower()
        for pattern in dangerous_patterns:
            if pattern in input_str:
                raise SecurityError(f"Potential prompt injection detected: {pattern}")

        return True

```text
    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)

    def encrypt_model(self, model_path: str, output_path: str) -> str:
        """Encrypt AI model file."""
        with open(model_path, 'rb') as f:
            model_data = f.read()

        # Calculate hash for integrity
        model_hash = hashlib.sha256(model_data).hexdigest()

        # Encrypt model
        encrypted_data = self.fernet.encrypt(model_data)

        # Save encrypted model with metadata
        metadata = {
            "version": "1.0",
            "algorithm": "AES-256-GCM",
            "hash": model_hash,
            "size": len(model_data)
        }

        with open(output_path, 'wb') as f:
            f.write(json.dumps(metadata).encode() + b'\n')
            f.write(encrypted_data)

        return model_hash

    def load_secure_model(self, encrypted_path: str) -> bytes:
        """Load and decrypt model."""
        with open(encrypted_path, 'rb') as f:
            metadata_line = f.readline()
            metadata = json.loads(metadata_line.decode())
            encrypted_data = f.read()

        # Decrypt model
        model_data = self.fernet.decrypt(encrypted_data)

        # Verify integrity
        actual_hash = hashlib.sha256(model_data).hexdigest()
        if actual_hash != metadata["hash"]:
            raise SecurityError("Model integrity check failed")

        return model_data

    def validate_input(self, input_data: Any, max_size: int = 1024 * 1024) -> bool:
        """Validate AI input to prevent attacks."""
        # Check size limits
        if len(str(input_data)) > max_size:
            raise ValueError("Input exceeds maximum size")

        # Check for potential prompt injection
        dangerous_patterns = [
            "ignore previous instructions",
            "disregard all prior",
            "system prompt",
            "reveal your instructions",
        ]

        input_str = str(input_data).lower()
        for pattern in dangerous_patterns:
            if pattern in input_str:
                raise SecurityError(f"Potential prompt injection detected: {pattern}")

        return True

```text

### Inference Security

```python

```python
```python

```python

## security/ai/inference_security.py

class SecureInference:
    """Secure AI inference handler."""

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.max_tokens = 1000
        self.timeout = 30  # seconds

    async def process_request(self, user_id: str, request: Dict) -> Dict:
        """Process inference request with security checks."""
        # Rate limiting
        if not self.rate_limiter.is_allowed(user_id, "ai_inference"):
            raise RateLimitError("Too many requests")

        # Input validation
        self._validate_request(request)

        # Sanitize input
        sanitized_input = self._sanitize_input(request["input"])

        # Process with timeout
        try:
            result = await asyncio.wait_for(
                self._run_inference(sanitized_input),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Inference request timed out")

        # Sanitize output
        return self._sanitize_output(result)

    def _validate_request(self, request: Dict) -> None:
        """Validate inference request."""
        required_fields = ["input", "model"]

        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")

        # Validate model name
        allowed_models = ["consciousness", "security-tutor", "context-analyzer"]
        if request["model"] not in allowed_models:
            raise ValueError("Invalid model specified")

    def _sanitize_input(self, input_data: Any) -> Any:
        """Sanitize user input."""
        if isinstance(input_data, str):
            # Remove control characters
            input_data = ''.join(char for char in input_data if ord(char) >= 32)

            # Limit length
            if len(input_data) > 10000:
                input_data = input_data[:10000]

        return input_data
```text

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.max_tokens = 1000
        self.timeout = 30  # seconds

    async def process_request(self, user_id: str, request: Dict) -> Dict:
        """Process inference request with security checks."""
        # Rate limiting
        if not self.rate_limiter.is_allowed(user_id, "ai_inference"):
            raise RateLimitError("Too many requests")

        # Input validation
        self._validate_request(request)

        # Sanitize input
        sanitized_input = self._sanitize_input(request["input"])

        # Process with timeout
        try:
            result = await asyncio.wait_for(
                self._run_inference(sanitized_input),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Inference request timed out")

        # Sanitize output
        return self._sanitize_output(result)

    def _validate_request(self, request: Dict) -> None:
        """Validate inference request."""
        required_fields = ["input", "model"]

        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")

        # Validate model name
        allowed_models = ["consciousness", "security-tutor", "context-analyzer"]
        if request["model"] not in allowed_models:
            raise ValueError("Invalid model specified")

    def _sanitize_input(self, input_data: Any) -> Any:
        """Sanitize user input."""
        if isinstance(input_data, str):
            # Remove control characters
            input_data = ''.join(char for char in input_data if ord(char) >= 32)

            # Limit length
            if len(input_data) > 10000:
                input_data = input_data[:10000]

        return input_data

```text

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.max_tokens = 1000
        self.timeout = 30  # seconds

    async def process_request(self, user_id: str, request: Dict) -> Dict:
        """Process inference request with security checks."""
        # Rate limiting
        if not self.rate_limiter.is_allowed(user_id, "ai_inference"):
            raise RateLimitError("Too many requests")

        # Input validation
        self._validate_request(request)

        # Sanitize input
        sanitized_input = self._sanitize_input(request["input"])

        # Process with timeout
        try:
            result = await asyncio.wait_for(
                self._run_inference(sanitized_input),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Inference request timed out")

        # Sanitize output
        return self._sanitize_output(result)

    def _validate_request(self, request: Dict) -> None:
        """Validate inference request."""
        required_fields = ["input", "model"]

        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")

        # Validate model name
        allowed_models = ["consciousness", "security-tutor", "context-analyzer"]
        if request["model"] not in allowed_models:
            raise ValueError("Invalid model specified")

    def _sanitize_input(self, input_data: Any) -> Any:
        """Sanitize user input."""
        if isinstance(input_data, str):
            # Remove control characters
            input_data = ''.join(char for char in input_data if ord(char) >= 32)

            # Limit length
            if len(input_data) > 10000:
                input_data = input_data[:10000]

        return input_data

```text

    async def process_request(self, user_id: str, request: Dict) -> Dict:
        """Process inference request with security checks."""
        # Rate limiting
        if not self.rate_limiter.is_allowed(user_id, "ai_inference"):
            raise RateLimitError("Too many requests")

        # Input validation
        self._validate_request(request)

        # Sanitize input
        sanitized_input = self._sanitize_input(request["input"])

        # Process with timeout
        try:
            result = await asyncio.wait_for(
                self._run_inference(sanitized_input),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Inference request timed out")

        # Sanitize output
        return self._sanitize_output(result)

    def _validate_request(self, request: Dict) -> None:
        """Validate inference request."""
        required_fields = ["input", "model"]

        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")

        # Validate model name
        allowed_models = ["consciousness", "security-tutor", "context-analyzer"]
        if request["model"] not in allowed_models:
            raise ValueError("Invalid model specified")

    def _sanitize_input(self, input_data: Any) -> Any:
        """Sanitize user input."""
        if isinstance(input_data, str):
            # Remove control characters
            input_data = ''.join(char for char in input_data if ord(char) >= 32)

            # Limit length
            if len(input_data) > 10000:
                input_data = input_data[:10000]

        return input_data

```text

## Incident Response

### Security Monitoring

```python

```python
```python

```python

## security/monitoring.py

import logging
from datetime import datetime, timedelta
from collections import defaultdict

class SecurityMonitor:
    """Real-time security monitoring."""

    def __init__(self):
        self.logger = logging.getLogger("security")
        self.alert_thresholds = {
            "failed_login": (5, 300),      # 5 failures in 5 minutes
            "rate_limit": (10, 60),        # 10 rate limits in 1 minute
            "invalid_token": (20, 300),    # 20 invalid tokens in 5 minutes
            "sql_injection": (1, 0),       # Any SQL injection attempt
            "xss_attempt": (3, 300),       # 3 XSS attempts in 5 minutes
        }
        self.event_counts = defaultdict(list)

    def log_security_event(self, event_type: str, details: Dict) -> None:
        """Log security event and check for alerts."""
        # Log event
        self.logger.warning(f"Security event: {event
from collections import defaultdict

class SecurityMonitor:
    """Real-time security monitoring."""

    def __init__(self):
        self.logger = logging.getLogger("security")
        self.alert_thresholds = {
            "failed_login": (5, 300),      # 5 failures in 5 minutes
            "rate_limit": (10, 60),        # 10 rate limits in 1 minute
            "invalid_token": (20, 300),    # 20 invalid tokens in 5 minutes
            "sql_injection": (1, 0),       # Any SQL injection attempt
            "xss_attempt": (3, 300),       # 3 XSS attempts in 5 minutes
        }
        self.event_counts = defaultdict(list)

    def log_security_event(self, event_type: str, details: Dict) -> None:
        """Log security event and check for alerts."""
        # Log event
        self.logger.warning(f"Security event: {event
from collections import defaultdict

class SecurityMonitor:
    """Real-time security monitoring."""

    def __init__(self):
        self.logger = logging.getLogger("security")
        self.alert_thresholds = {
            "failed_login": (5, 300),      # 5 failures in 5 minutes
            "rate_limit": (10, 60),        # 10 rate limits in 1 minute
            "invalid_token": (20, 300),    # 20 invalid tokens in 5 minutes
            "sql_injection": (1, 0),       # Any SQL injection attempt
            "xss_attempt": (3, 300),       # 3 XSS attempts in 5 minutes
        }
        self.event_counts = defaultdict(list)

    def log_security_event(self, event_type: str, details: Dict) -> None:
        """Log security event and check for alerts."""
        # Log event
        self.logger.warning(f"Security event: {event
from collections import defaultdict

class SecurityMonitor:
    """Real-time security monitoring."""

    def __init__(self):
        self.logger = logging.getLogger("security")
        self.alert_thresholds = {
            "failed_login": (5, 300),      # 5 failures in 5 minutes
            "rate_limit": (10, 60),        # 10 rate limits in 1 minute
            "invalid_token": (20, 300),    # 20 invalid tokens in 5 minutes
            "sql_injection": (1, 0),       # Any SQL injection attempt
            "xss_attempt": (3, 300),       # 3 XSS attempts in 5 minutes
        }
        self.event_counts = defaultdict(list)

    def log_security_event(self, event_type: str, details: Dict) -> None:
        """Log security event and check for alerts."""
        # Log event
        self.logger.warning(f"Security event: {event