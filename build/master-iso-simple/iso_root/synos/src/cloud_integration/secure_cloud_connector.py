#!/usr/bin/env python3
"""
Secure Cloud Connectivity Architecture for Syn_OS
Provides encrypted, consciousness-aware cloud integration with zero-trust security
"""

import asyncio
import logging
import time
import json
import ssl
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import websockets
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
from src.hardware_security.tpm_security_engine import TPMSecurityEngine
from src.security.audit_logger import AuditLogger


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITAL_OCEAN = "digital_ocean"
    CUSTOM = "custom"


class ConnectionType(Enum):
    """Types of cloud connections"""
    REST_API = "rest_api"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MQTT = "mqtt"
    CUSTOM_PROTOCOL = "custom_protocol"


class SecurityLevel(Enum):
    """Security levels for cloud connections"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    CONSCIOUSNESS_AWARE = "consciousness_aware"


@dataclass
class CloudEndpoint:
    """Cloud endpoint configuration"""
    endpoint_id: str
    provider: CloudProvider
    connection_type: ConnectionType
    url: str
    region: str
    security_level: SecurityLevel
    consciousness_required: float
    encryption_key: Optional[bytes] = None
    certificates: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConnectionCredentials:
    """Cloud connection credentials"""
    access_key: str
    secret_key: str
    session_token: Optional[str] = None
    certificate_path: Optional[str] = None
    private_key_path: Optional[str] = None
    consciousness_signature: Optional[bytes] = None


@dataclass
class CloudRequest:
    """Cloud API request"""
    request_id: str
    endpoint_id: str
    method: str
    path: str
    headers: Dict[str, str]
    data: Optional[bytes] = None
    consciousness_level: float = 0.0
    timeout: int = 30


@dataclass
class CloudResponse:
    """Cloud API response"""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    data: bytes
    processing_time: float
    consciousness_verified: bool
    encryption_used: bool


class SecureCloudConnector:
    """
    Secure cloud connectivity with consciousness-aware authentication
    Provides encrypted, zero-trust cloud integration
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus, tpm_engine: TPMSecurityEngine):
        """Initialize secure cloud connector"""
        self.consciousness_bus = consciousness_bus
        self.tmp_engine = tpm_engine
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Connection management
        self.endpoints: Dict[str, CloudEndpoint] = {}
        self.active_connections: Dict[str, Any] = {}
        self.credentials: Dict[str, ConnectionCredentials] = {}
        
        # Security configuration
        self.master_key: Optional[bytes] = None
        self.session_keys: Dict[str, bytes] = {}
        
        # Performance tracking
        self.request_count = 0
        self.successful_requests = 0
        self.total_response_time = 0.0
        self.encryption_overhead = 0.0
        
        # SSL context
        self.ssl_context = self._create_ssl_context()
        
        # Initialize connector
        asyncio.create_task(self._initialize_connector())
    
    async def _initialize_connector(self):
        """Initialize the cloud connector"""
        try:
            self.logger.info("Initializing secure cloud connector...")
            
            # Generate master encryption key
            await self._generate_master_key()
            
            # Load default cloud endpoints
            await self._load_default_endpoints()
            
            self.logger.info("Secure cloud connector initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing cloud connector: {e}")
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create secure SSL context"""
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Enhanced security settings
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        return context
    
    async def _generate_master_key(self):
        """Generate master encryption key using TPM"""
        try:
            # Get current consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            if consciousness_state.overall_consciousness_level >= 0.7:
                # Use TPM for high-security key generation
                random_bytes = await self.tpm_engine.generate_secure_random(32)
                if random_bytes:
                    self.master_key = random_bytes
                    self.logger.info("Generated TPM-backed master key")
                    return
            
            # Fallback to system random
            self.master_key = secrets.token_bytes(32)
            self.logger.info("Generated system random master key")
            
        except Exception as e:
            self.logger.error(f"Error generating master key: {e}")
            self.master_key = secrets.token_bytes(32)
    
    async def _load_default_endpoints(self):
        """Load default cloud endpoints"""
        
        # AWS endpoints
        self.endpoints["aws_api"] = CloudEndpoint(
            endpoint_id="aws_api",
            provider=CloudProvider.AWS,
            connection_type=ConnectionType.REST_API,
            url="https://api.aws.amazon.com",
            region="us-east-1",
            security_level=SecurityLevel.ENHANCED,
            consciousness_required=0.6
        )
        
        # Azure endpoints
        self.endpoints["azure_api"] = CloudEndpoint(
            endpoint_id="azure_api",
            provider=CloudProvider.AZURE,
            connection_type=ConnectionType.REST_API,
            url="https://management.azure.com",
            region="eastus",
            security_level=SecurityLevel.ENHANCED,
            consciousness_required=0.6
        )
        
        # GCP endpoints
        self.endpoints["gcp_api"] = CloudEndpoint(
            endpoint_id="gcp_api",
            provider=CloudProvider.GCP,
            connection_type=ConnectionType.REST_API,
            url="https://compute.googleapis.com",
            region="us-central1",
            security_level=SecurityLevel.ENHANCED,
            consciousness_required=0.6
        )
        
        # Custom Syn_OS cloud endpoint
        self.endpoints["synos_cloud"] = CloudEndpoint(
            endpoint_id="synos_cloud",
            provider=CloudProvider.CUSTOM,
            connection_type=ConnectionType.WEBSOCKET,
            url="wss://cloud.syn-os.ai",
            region="global",
            security_level=SecurityLevel.CONSCIOUSNESS_AWARE,
            consciousness_required=0.8
        )
        
        self.logger.info(f"Loaded {len(self.endpoints)} default endpoints")
    
    async def register_endpoint(self, endpoint: CloudEndpoint) -> bool:
        """Register a new cloud endpoint"""
        try:
            # Validate endpoint
            if not await self._validate_endpoint(endpoint):
                return False
            
            # Store endpoint
            self.endpoints[endpoint.endpoint_id] = endpoint
            
            # Generate session key for endpoint
            session_key = secrets.token_bytes(32)
            self.session_keys[endpoint.endpoint_id] = session_key
            
            # Log registration
            await self.audit_logger.log_system_event(
                event_type="cloud_endpoint_registered",
                details={
                    "endpoint_id": endpoint.endpoint_id,
                    "provider": endpoint.provider.value,
                    "security_level": endpoint.security_level.value,
                    "consciousness_required": endpoint.consciousness_required
                }
            )
            
            self.logger.info(f"Registered cloud endpoint: {endpoint.endpoint_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering endpoint: {e}")
            return False
    
    async def _validate_endpoint(self, endpoint: CloudEndpoint) -> bool:
        """Validate cloud endpoint configuration"""
        try:
            # Check URL format
            if not endpoint.url.startswith(('https://', 'wss://')):
                self.logger.error(f"Endpoint {endpoint.endpoint_id} must use HTTPS or WSS")
                return False
            
            # Check consciousness requirement
            if endpoint.consciousness_required < 0.0 or endpoint.consciousness_required > 1.0:
                self.logger.error(f"Invalid consciousness requirement: {endpoint.consciousness_required}")
                return False
            
            # Test connectivity (basic)
            try:
                async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(ssl=self.ssl_context),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as session:
                    async with session.get(endpoint.url.replace('wss://', 'https://')) as response:
                        if response.status >= 500:
                            self.logger.warning(f"Endpoint {endpoint.endpoint_id} returned {response.status}")
            except:
                self.logger.warning(f"Could not validate connectivity to {endpoint.endpoint_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating endpoint: {e}")
            return False
    
    async def set_credentials(self, endpoint_id: str, credentials: ConnectionCredentials) -> bool:
        """Set credentials for cloud endpoint"""
        try:
            if endpoint_id not in self.endpoints:
                self.logger.error(f"Endpoint {endpoint_id} not found")
                return False
            
            endpoint = self.endpoints[endpoint_id]
            
            # Encrypt credentials if high security level
            if endpoint.security_level in [SecurityLevel.MAXIMUM, SecurityLevel.CONSCIOUSNESS_AWARE]:
                encrypted_credentials = await self._encrypt_credentials(credentials)
                self.credentials[endpoint_id] = encrypted_credentials
            else:
                self.credentials[endpoint_id] = credentials
            
            self.logger.info(f"Set credentials for endpoint: {endpoint_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting credentials: {e}")
            return False
    
    async def _encrypt_credentials(self, credentials: ConnectionCredentials) -> ConnectionCredentials:
        """Encrypt sensitive credential data"""
        try:
            if not self.master_key:
                raise ValueError("Master key not available")
            
            # Encrypt access key
            encrypted_access_key = self._encrypt_data(credentials.access_key.encode(), self.master_key)
            
            # Encrypt secret key
            encrypted_secret_key = self._encrypt_data(credentials.secret_key.encode(), self.master_key)
            
            # Create encrypted credentials
            encrypted_credentials = ConnectionCredentials(
                access_key=base64.b64encode(encrypted_access_key).decode(),
                secret_key=base64.b64encode(encrypted_secret_key).decode(),
                session_token=credentials.session_token,
                certificate_path=credentials.certificate_path,
                private_key_path=credentials.private_key_path,
                consciousness_signature=credentials.consciousness_signature
            )
            
            return encrypted_credentials
            
        except Exception as e:
            self.logger.error(f"Error encrypting credentials: {e}")
            raise
    
    def _encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using AES-GCM"""
        # Generate random IV
        iv = secrets.token_bytes(12)
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Return IV + tag + ciphertext
        return iv + encryptor.tag + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using AES-GCM"""
        # Extract IV, tag, and ciphertext
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def make_request(self, request: CloudRequest) -> CloudResponse:
        """Make secure cloud request with consciousness verification"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Get endpoint
            if request.endpoint_id not in self.endpoints:
                raise ValueError(f"Endpoint {request.endpoint_id} not found")
            
            endpoint = self.endpoints[request.endpoint_id]
            
            # Check consciousness level requirement
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            current_consciousness = consciousness_state.overall_consciousness_level
            
            if current_consciousness < endpoint.consciousness_required:
                raise ValueError(
                    f"Insufficient consciousness level: {current_consciousness} < {endpoint.consciousness_required}"
                )
            
            # Get credentials
            if request.endpoint_id not in self.credentials:
                raise ValueError(f"No credentials for endpoint {request.endpoint_id}")
            
            credentials = self.credentials[request.endpoint_id]
            
            # Prepare request with security enhancements
            enhanced_request = await self._enhance_request_security(request, endpoint, credentials, consciousness_state)
            
            # Make the actual request
            if endpoint.connection_type == ConnectionType.REST_API:
                response = await self._make_rest_request(enhanced_request, endpoint)
            elif endpoint.connection_type == ConnectionType.WEBSOCKET:
                response = await self._make_websocket_request(enhanced_request, endpoint)
            else:
                raise ValueError(f"Unsupported connection type: {endpoint.connection_type}")
            
            # Process response
            processed_response = await self._process_response(response, endpoint, consciousness_state)
            
            # Update performance metrics
            processing_time = time.time() - start_time
            self.successful_requests += 1
            self.total_response_time += processing_time
            
            # Log successful request
            await self.audit_logger.log_system_event(
                event_type="cloud_request_success",
                details={
                    "request_id": request.request_id,
                    "endpoint_id": request.endpoint_id,
                    "method": request.method,
                    "status_code": processed_response.status_code,
                    "processing_time": processing_time,
                    "consciousness_level": current_consciousness
                }
            )
            
            return processed_response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            self.logger.error(f"Cloud request error: {e}")
            
            # Log failed request
            await self.audit_logger.log_system_event(
                event_type="cloud_request_error",
                details={
                    "request_id": request.request_id,
                    "endpoint_id": request.endpoint_id,
                    "error": str(e),
                    "processing_time": processing_time
                }
            )
            
            # Return error response
            return CloudResponse(
                request_id=request.request_id,
                status_code=500,
                headers={},
                data=json.dumps({"error": str(e)}).encode(),
                processing_time=processing_time,
                consciousness_verified=False,
                encryption_used=False
            )
    
    async def _enhance_request_security(self, request: CloudRequest, endpoint: CloudEndpoint, 
                                      credentials: ConnectionCredentials, 
                                      consciousness_state: ConsciousnessState) -> CloudRequest:
        """Enhance request with security features"""
        
        enhanced_headers = request.headers.copy()
        
        # Add consciousness signature
        consciousness_signature = await self._create_consciousness_signature(consciousness_state)
        enhanced_headers['X-Consciousness-Signature'] = base64.b64encode(consciousness_signature).decode()
        enhanced_headers['X-Consciousness-Level'] = str(consciousness_state.overall_consciousness_level)
        
        # Add timestamp and nonce for replay protection
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)
        enhanced_headers['X-Timestamp'] = timestamp
        enhanced_headers['X-Nonce'] = nonce
        
        # Add authentication headers based on provider
        if endpoint.provider == CloudProvider.AWS:
            enhanced_headers.update(await self._create_aws_auth_headers(credentials, request, timestamp))
        elif endpoint.provider == CloudProvider.AZURE:
            enhanced_headers.update(await self._create_azure_auth_headers(credentials, request))
        elif endpoint.provider == CloudProvider.GCP:
            enhanced_headers.update(await self._create_gcp_auth_headers(credentials, request))
        elif endpoint.provider == CloudProvider.CUSTOM:
            enhanced_headers.update(await self._create_custom_auth_headers(credentials, request, consciousness_state))
        
        # Encrypt request data if required
        enhanced_data = request.data
        if endpoint.security_level in [SecurityLevel.MAXIMUM, SecurityLevel.CONSCIOUSNESS_AWARE] and request.data:
            session_key = self.session_keys.get(endpoint.endpoint_id, self.master_key)
            enhanced_data = self._encrypt_data(request.data, session_key)
            enhanced_headers['X-Data-Encrypted'] = 'true'
        
        return CloudRequest(
            request_id=request.request_id,
            endpoint_id=request.endpoint_id,
            method=request.method,
            path=request.path,
            headers=enhanced_headers,
            data=enhanced_data,
            consciousness_level=request.consciousness_level,
            timeout=request.timeout
        )
    
    async def _create_consciousness_signature(self, consciousness_state: ConsciousnessState) -> bytes:
        """Create consciousness-based signature"""
        try:
            # Create consciousness fingerprint
            consciousness_data = {
                "level": consciousness_state.overall_consciousness_level,
                "populations": consciousness_state.neural_populations,
                "attention": consciousness_state.attention_focus,
                "timestamp": consciousness_state.timestamp
            }
            
            consciousness_json = json.dumps(consciousness_data, sort_keys=True)
            consciousness_hash = hashlib.sha256(consciousness_json.encode()).digest()
            
            # Sign with TPM if available
            if self.tpm_engine and consciousness_state.overall_consciousness_level >= 0.8:
                # Use TPM for signing (simplified - would use actual TPM signing)
                signature = hashlib.sha256(consciousness_hash + self.master_key).digest()
            else:
                # Use master key for signing
                signature = hashlib.sha256(consciousness_hash + self.master_key).digest()
            
            return signature
            
        except Exception as e:
            self.logger.error(f"Error creating consciousness signature: {e}")
            return hashlib.sha256(b"fallback_signature").digest()
    
    async def _create_aws_auth_headers(self, credentials: ConnectionCredentials, 
                                     request: CloudRequest, timestamp: str) -> Dict[str, str]:
        """Create AWS authentication headers"""
        # Simplified AWS Signature Version 4 implementation
        # In production, use boto3 or proper AWS SDK
        
        access_key = credentials.access_key
        if credentials.access_key.startswith('base64:'):
            # Decrypt if encrypted
            encrypted_data = base64.b64decode(credentials.access_key[7:])
            access_key = self._decrypt_data(encrypted_data, self.master_key).decode()
        
        return {
            'Authorization': f'AWS4-HMAC-SHA256 Credential={access_key}/{timestamp[:8]}/us-east-1/service/aws4_request',
            'X-Amz-Date': timestamp,
            'X-Amz-Content-Sha256': hashlib.sha256(request.data or b'').hexdigest()
        }
    
    async def _create_azure_auth_headers(self, credentials: ConnectionCredentials, 
                                       request: CloudRequest) -> Dict[str, str]:
        """Create Azure authentication headers"""
        return {
            'Authorization': f'Bearer {credentials.access_key}',
            'Content-Type': 'application/json'
        }
    
    async def _create_gcp_auth_headers(self, credentials: ConnectionCredentials, 
                                     request: CloudRequest) -> Dict[str, str]:
        """Create GCP authentication headers"""
        return {
            'Authorization': f'Bearer {credentials.access_key}',
            'Content-Type': 'application/json'
        }
    
    async def _create_custom_auth_headers(self, credentials: ConnectionCredentials, 
                                        request: CloudRequest, 
                                        consciousness_state: ConsciousnessState) -> Dict[str, str]:
        """Create custom Syn_OS authentication headers"""
        
        # Create custom authentication token
        auth_data = {
            "access_key": credentials.access_key,
            "consciousness_level": consciousness_state.overall_consciousness_level,
            "timestamp": int(time.time())
        }
        
        auth_json = json.dumps(auth_data, sort_keys=True)
        auth_signature = hashlib.sha256(auth_json.encode() + self.master_key).digest()
        
        return {
            'Authorization': f'SynOS {base64.b64encode(auth_signature).decode()}',
            'X-SynOS-Auth': base64.b64encode(auth_json.encode()).decode(),
            'Content-Type': 'application/json'
        }
    
    async def _make_rest_request(self, request: CloudRequest, endpoint: CloudEndpoint) -> CloudResponse:
        """Make REST API request"""
        
        url = f"{endpoint.url}{request.path}"
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=self.ssl_context),
            timeout=aiohttp.ClientTimeout(total=request.timeout)
        ) as session:
            
            async with session.request(
                method=request.method,
                url=url,
                headers=request.headers,
                data=request.data
            ) as response:
                
                response_data = await response.read()
                
                return CloudResponse(
                    request_id=request.request_id,
                    status_code=response.status,
                    headers=dict(response.headers),
                    data=response_data,
                    processing_time=0.0,  # Will be set by caller
                    consciousness_verified=True,
                    encryption_used=request.headers.get('X-Data-Encrypted') == 'true'
                )
    
    async def _make_websocket_request(self, request: CloudRequest, endpoint: CloudEndpoint) -> CloudResponse:
        """Make WebSocket request"""
        
        try:
            # Create WebSocket message
            message = {
                "id": request.request_id,
                "method": request.method,
                "path": request.path,
                "headers": request.headers,
                "data": base64.b64encode(request.data).decode() if request.data else None
            }
            
            # Connect to WebSocket
            async with websockets.connect(
                endpoint.url,
                ssl=self.ssl_context,
                extra_headers=request.headers
            ) as websocket:
                
                # Send request
                await websocket.send(json.dumps(message))
                
                # Receive response
                response_text = await asyncio.wait_for(websocket.recv(), timeout=request.timeout)
                response_data = json.loads(response_text)
                
                return CloudResponse(
                    request_id=request.request_id,
                    status_code=response_data.get('status', 200),
                    headers=response_data.get('headers', {}),
                    data=base64.b64decode(response_data.get('data', '')) if response_data.get('data') else b'',
                    processing_time=0.0,
                    consciousness_verified=True,
                    encryption_used=request.headers.get('X-Data-Encrypted') == 'true'
                )
                
        except Exception as e:
            self.logger.error(f"WebSocket request error: {e}")
            raise
    
    async def _process_response(self, response: CloudResponse, endpoint: CloudEndpoint, 
                              consciousness_state: ConsciousnessState) -> CloudResponse:
        """Process and validate cloud response"""
        
        # Decrypt response data if encrypted
        if response.encryption_used and response.data:
            try:
                session_key = self.session_keys.get(endpoint.endpoint_id, self.master_key)
                decrypted_data = self._decrypt_data(response.data, session_key)
                response.data = decrypted_data
            except Exception as e:
                self.logger.error(f"Error decrypting response: {e}")
        
        # Verify consciousness signature if present
        consciousness_verified = True
        if 'X-Consciousness-Signature' in response.headers:
            try:
                signature = base64.b64decode(response.headers['X-Consciousness-Signature'])
                expected_signature = await self._create_consciousness_signature(consciousness_state)
                consciousness_verified = signature == expected_signature
            except Exception as e:
                self.logger.error(f"Error verifying consciousness signature: {e}")
                consciousness_verified = False
        
        response.consciousness_verified = consciousness_verified
        
        return response
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all cloud connections"""
        
        status = {
            "endpoints": len(self.endpoints),
            "active_connections": len(self.active_connections),
            "credentials_configured": len(self.credentials),
            "performance_metrics": {
                "total_requests": self.request_count,
                "successful_requests": self.successful_requests,
                "success_rate": self.successful_requests / max(1, self.request_count),
                "average_response_time": self.total_response_time / max(1, self.successful_requests)
            },
            "endpoints_detail": [
                {
                    "endpoint_id": endpoint.endpoint_id,
                    "provider": endpoint.provider.value,
                    "connection_type": endpoint.connection_type.value,
                    "security_level": endpoint.security_level.value,
                    "consciousness_required": endpoint.consciousness_required,
                    "has_credentials": endpoint.endpoint_id in self.credentials
                }
                for endpoint in self.endpoints.values()
            ]
        }
        
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cloud connector"""
        
        try:
            # Test basic functionality
            test_endpoint = CloudEndpoint(
                endpoint_id="health_test",
                provider=CloudProvider.CUSTOM,
                connection_type=ConnectionType.REST_API,
                url="https://httpbin.org",
                region="global",
                security_level=SecurityLevel.BASIC,
                consciousness_required=0.0
            )
            
            # Register test endpoint
            await self.register_endpoint(test_endpoint)
            
            # Set test credentials
            test_credentials = ConnectionCredentials(
                access_key="test",
                secret_key="test"
            )
            await self.set_credentials("health_test", test_credentials)
            
            # Make test request
            test_request = CloudRequest(
                request_id="health_check",
                endpoint_id="health_test",
                method="GET",
                path="/get",
                headers={"User-Agent": "SynOS-CloudConnector/1.0"}
            )
            
            response = await self.make_request(test_request)
            
            # Clean up test endpoint
            if "health_test" in self.endpoints:
                del self.endpoints["health_test"]
            if "health_test" in self.credentials:
                del self.credentials["health_test"]
            
            return {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "test_response_code": response.status_code,
                "master_key_available": self.master_key is not None,
                "ssl_context_valid": self.ssl_context is not None,
                "connection_status": self.get_connection_status()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "master_key_available": self.master_key is not None,
                "ssl_context_valid": self.ssl_context is not None
            }
    
    async def shutdown(self):
        """Shutdown cloud connector"""
        self.logger.info("Shutting down secure cloud connector...")
        
        # Close active connections
        for connection in self.active_connections.values():
            try:
                if hasattr(connection, 'close'):
                    await connection.close()
            except:
                pass
        
        # Clear sensitive data
        self.master_key = None
        self.session_keys.clear()
        self.credentials.clear()
        
        self.logger.info("Secure cloud connector shutdown complete")


# Example usage and testing
async def main():
    """Example usage of Secure Cloud Connector"""
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    from src.hardware_security.tpm_security_engine import TPMSecurityEngine
    
    # Initialize components
    consciousness_bus = ConsciousnessBus()
    tpm_engine = TPMSecurityEngine(consciousness_bus)
    cloud_connector = SecureCloudConnector(consciousness_bus, tpm_engine)
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Health check
    health = await cloud_connector.health_check()
    print(f"Health check: {health}")
    
    if health["status"] == "healthy":
        # Test cloud request
        request = CloudRequest(
            request_id="test_001",
            endpoint_id="synos_cloud",
            method="GET",
            path="/api/v1/status",
            headers={"User-Agent": "SynOS/1.0"}
        )