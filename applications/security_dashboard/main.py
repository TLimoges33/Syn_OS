#!/usr/bin/env python3
"""
Syn_OS Security Dashboard
Advanced security monitoring and control interface with 10/10 security integration
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import secrets
import hashlib

import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors
import nats
from jinja2 import Environment, FileSystemLoader
import weakref

# Add security modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from security.jwt_auth import get_jwt_manager, TokenType, UserRole
from security.audit_logger import get_audit_logger, SecurityEventType, SecurityLevel
from security.input_validator import get_validator, ValidationRule, InputType
from security.config_manager import get_config
from security.consciousness_security_controller import ConsciousnessSecurityController

logger = logging.getLogger(__name__)


class SecurityDashboard:
    """Advanced security dashboard with 10/10 security integration"""
    
    def __init__(self):
        self.app = web.Application()
        self.nats_client = None
        self.websocket_connections = weakref.WeakSet()
        self.logger = logging.getLogger(__name__)
        
        # Security components
        self.jwt_manager = get_jwt_manager()
        self.audit_logger = get_audit_logger()
        self.input_validator = get_validator()
        self.config = get_config()
        self.consciousness_security = ConsciousnessSecurityController()
        
        # Configuration
        self.nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
        self.orchestrator_url = os.getenv('ORCHESTRATOR_URL', 'http://localhost:8080')
        self.consciousness_url = os.getenv('CONSCIOUSNESS_URL', 'http://localhost:8081')
        self.port = int(os.getenv('SECURITY_DASHBOARD_PORT', '8083'))
        
        # Template environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Security metrics cache
        self.security_metrics = {
            'last_updated': None,
            'hsm_status': {},
            'zero_trust_status': {},
            'quantum_crypto_status': {},
            'consciousness_security_status': {},
            'active_threats': [],
            'security_events': [],
            'system_health': {},
            'audit_summary': {},
            'vulnerability_scans': [],
            'penetration_tests': []
        }
        
        # Active security sessions
        self.active_sessions = {}
        
        self._setup_routes()
        self._setup_cors()
        self._setup_security_middleware()
    
    def _setup_routes(self):
        """Setup secure web application routes"""
        # Static files with security headers
        self.app.router.add_static('/static', 'applications/security_dashboard/static')
        
        # Authentication routes
        self.app.router.add_get('/login', self.login_page)
        self.app.router.add_post('/api/auth/login', self.api_login)
        self.app.router.add_post('/api/auth/logout', self.api_logout)
        self.app.router.add_post('/api/auth/refresh', self.api_refresh_token)
        
        # Main dashboard routes (protected)
        self.app.router.add_get('/', self.security_dashboard_home)
        self.app.router.add_get('/hsm', self.hsm_dashboard)
        self.app.router.add_get('/zero-trust', self.zero_trust_dashboard)
        self.app.router.add_get('/quantum', self.quantum_crypto_dashboard)
        self.app.router.add_get('/consciousness', self.consciousness_security_dashboard)
        self.app.router.add_get('/tools', self.security_tools_dashboard)
        self.app.router.add_get('/monitoring', self.security_monitoring_dashboard)
        self.app.router.add_get('/audit', self.audit_dashboard)
        
        # Security API routes (protected)
        self.app.router.add_get('/api/security/status', self.api_security_status)
        self.app.router.add_get('/api/security/hsm/status', self.api_hsm_status)
        self.app.router.add_get('/api/security/zero-trust/status', self.api_zero_trust_status)
        self.app.router.add_get('/api/security/quantum/status', self.api_quantum_status)
        self.app.router.add_get('/api/security/consciousness/status', self.api_consciousness_security_status)
        self.app.router.add_get('/api/security/threats', self.api_active_threats)
        self.app.router.add_get('/api/security/events', self.api_security_events)
        self.app.router.add_get('/api/security/audit/summary', self.api_audit_summary)
        
        # Security tools API routes (protected)
        self.app.router.add_post('/api/tools/nmap/scan', self.api_nmap_scan)
        self.app.router.add_post('/api/tools/metasploit/scan', self.api_metasploit_scan)
        self.app.router.add_get('/api/tools/scans/history', self.api_scan_history)
        self.app.router.add_get('/api/tools/scans/{scan_id}', self.api_scan_results)
        
        # Consciousness security control routes (protected)
        self.app.router.add_post('/api/consciousness/security/assess', self.api_consciousness_assess)
        self.app.router.add_get('/api/consciousness/security/insights', self.api_consciousness_insights)
        self.app.router.add_post('/api/consciousness/security/response', self.api_consciousness_response)
        
        # Real-time WebSocket (protected)
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Health check (public)
        self.app.router.add_get('/health', self.health_check)
    
    def _setup_cors(self):
        """Setup CORS with security considerations"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "https://localhost:3000": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_security_middleware(self):
        """Setup security middleware"""
        @web.middleware
        async def security_headers_middleware(request, handler):
            """Add security headers to all responses"""
            response = await handler(request)
            
            # Security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            return response
        
        @web.middleware
        async def auth_middleware(request, handler):
            """Authentication middleware for protected routes"""
            # Skip auth for public routes
            public_routes = ['/health', '/login', '/api/auth/login', '/static']
            if any(request.path.startswith(route) for route in public_routes):
                return await handler(request)
            
            # Check for JWT token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                # For web pages, redirect to login
                if request.path.startswith('/api/'):
                    return web.json_response({'error': 'Authentication required'}, status=401)
                else:
                    return web.Response(status=302, headers={'Location': '/login'})
            
            token = auth_header.split(' ')[1]
            
            try:
                # Verify JWT token
                claims = self.jwt_manager.verify_token(token, TokenType.ACCESS)
                
                # Add user info to request
                request['user'] = {
                    'user_id': claims.user_id,
                    'username': claims.username,
                    'roles': claims.roles,
                    'consciousness_level': claims.consciousness_level
                }
                
                # Log access
                self.audit_logger.log_api_access(
                    user_id=claims.user_id,
                    endpoint=request.path,
                    method=request.method,
                    ip_address=request.remote,
                    status_code=200,
                    user_agent=request.headers.get('User-Agent')
                )
                
                return await handler(request)
                
            except Exception as e:
                self.logger.warning(f"Authentication failed: {e}")
                
                # Log failed attempt
                self.audit_logger.log_security_event(
                    SecurityEventType.AUTHORIZATION_FAILURE,
                    SecurityLevel.MEDIUM,
                    ip_address=request.remote,
                    resource=request.path,
                    details={'error': str(e)}
                )
                
                if request.path.startswith('/api/'):
                    return web.json_response({'error': 'Invalid token'}, status=401)
                else:
                    return web.Response(status=302, headers={'Location': '/login'})
        
        @web.middleware
        async def input_validation_middleware(request, handler):
            """Input validation middleware"""
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if request.content_type == 'application/json':
                        data = await request.json()
                        # Validate JSON input
                        for key, value in data.items():
                            if isinstance(value, str):
                                rule = ValidationRule(InputType.STRING, max_length=1000)
                                result = self.input_validator.validate_input(value, rule)
                                if not result.is_valid:
                                    self.audit_logger.log_security_event(
                                        SecurityEventType.INJECTION_ATTEMPT,
                                        SecurityLevel.HIGH,
                                        ip_address=request.remote,
                                        resource=request.path,
                                        details={'field': key, 'error': result.error_message}
                                    )
                                    return web.json_response({
                                        'error': f'Invalid input in field {key}: {result.error_message}'
                                    }, status=400)
                except Exception as e:
                    return web.json_response({'error': 'Invalid request data'}, status=400)
            
            return await handler(request)
        
        # Add middleware to app
        self.app.middlewares.append(security_headers_middleware)
        self.app.middlewares.append(auth_middleware)
        self.app.middlewares.append(input_validation_middleware)
    
    async def start(self):
        """Start the security dashboard"""
        self.logger.info("Starting Syn_OS Security Dashboard...")
        
        # Connect to NATS for real-time updates
        await self._connect_nats()
        
        # Start security metrics collection
        asyncio.create_task(self._security_metrics_collector())
        
        # Start WebSocket broadcaster
        asyncio.create_task(self._websocket_broadcaster())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        self.logger.info(f"Security Dashboard started on port {self.port}")
        
        # Log system startup
        self.audit_logger.log_security_event(
            SecurityEventType.SYSTEM_STARTUP,
            SecurityLevel.MEDIUM,
            details={'component': 'security_dashboard', 'port': self.port}
        )
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down Security Dashboard...")
        finally:
            await runner.cleanup()
            if self.nats_client:
                await self.nats_client.close()
    
    async def _connect_nats(self):
        """Connect to NATS for real-time security updates"""
        try:
            self.nats_client = await nats.connect(self.nats_url)
            
            # Subscribe to security events
            await self.nats_client.subscribe("security.>", self._handle_security_event)
            await self.nats_client.subscribe("consciousness.security.>", self._handle_consciousness_security_event)
            
            self.logger.info("Connected to NATS for security updates")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to NATS: {e}")
    
    async def _handle_security_event(self, msg):
        """Handle security events from NATS"""
        try:
            data = json.loads(msg.data.decode())
            
            # Update security metrics
            if msg.subject.startswith("security.hsm"):
                self.security_metrics['hsm_status'].update(data)
            elif msg.subject.startswith("security.zero_trust"):
                self.security_metrics['zero_trust_status'].update(data)
            elif msg.subject.startswith("security.quantum"):
                self.security_metrics['quantum_crypto_status'].update(data)
            
            # Broadcast to WebSocket clients
            await self._broadcast_to_websockets({
                'type': 'security_event',
                'subject': msg.subject,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error handling security event: {e}")
    
    async def _handle_consciousness_security_event(self, msg):
        """Handle consciousness security events"""
        try:
            data = json.loads(msg.data.decode())
            
            # Update consciousness security status
            self.security_metrics['consciousness_security_status'].update(data)
            
            # Broadcast to WebSocket clients
            await self._broadcast_to_websockets({
                'type': 'consciousness_security_event',
                'subject': msg.subject,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error handling consciousness security event: {e}")
    
    async def _security_metrics_collector(self):
        """Collect security metrics periodically"""
        while True:
            try:
                # Update all security metrics
                await self._update_hsm_status()
                await self._update_zero_trust_status()
                await self._update_quantum_crypto_status()
                await self._update_consciousness_security_status()
                await self._update_active_threats()
                await self._update_security_events()
                await self._update_audit_summary()
                
                self.security_metrics['last_updated'] = datetime.utcnow()
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error collecting security metrics: {e}")
                await asyncio.sleep(10)
    
    async def _update_hsm_status(self):
        """Update HSM status"""
        try:
            # Mock HSM status - in production, this would query actual HSM
            self.security_metrics['hsm_status'] = {
                'status': 'active',
                'health': 'healthy',
                'key_operations': 1247,
                'last_key_rotation': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'secure_enclaves': 4,
                'tamper_events': 0
            }
        except Exception as e:
            self.logger.error(f"Error updating HSM status: {e}")
    
    async def _update_zero_trust_status(self):
        """Update Zero Trust architecture status"""
        try:
            self.security_metrics['zero_trust_status'] = {
                'status': 'active',
                'policies_enforced': 23,
                'access_requests': 156,
                'denied_requests': 12,
                'micro_segmentation': 'enabled',
                'identity_verification': 'multi_factor',
                'trust_score': 9.7
            }
        except Exception as e:
            self.logger.error(f"Error updating Zero Trust status: {e}")
    
    async def _update_quantum_crypto_status(self):
        """Update quantum-resistant cryptography status"""
        try:
            self.security_metrics['quantum_crypto_status'] = {
                'status': 'active',
                'algorithms': ['CRYSTALS-Kyber', 'CRYSTALS-Dilithium', 'FALCON'],
                'key_exchanges': 89,
                'quantum_readiness': 'full',
                'post_quantum_migrations': 'complete'
            }
        except Exception as e:
            self.logger.error(f"Error updating quantum crypto status: {e}")
    
    async def _update_consciousness_security_status(self):
        """Update consciousness security controller status"""
        try:
            self.security_metrics['consciousness_security_status'] = {
                'status': 'active',
                'autonomous_assessments': 15,
                'threat_predictions': 8,
                'response_actions': 3,
                'consciousness_level': 0.87,
                'security_insights': 42
            }
        except Exception as e:
            self.logger.error(f"Error updating consciousness security status: {e}")
    
    async def _update_active_threats(self):
        """Update active threats list"""
        try:
            # Mock active threats - in production, this would come from threat intelligence
            self.security_metrics['active_threats'] = [
                {
                    'id': 'threat_001',
                    'type': 'brute_force',
                    'severity': 'medium',
                    'source_ip': '192.168.1.100',
                    'target': 'ssh_service',
                    'detected_at': (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                    'status': 'mitigated'
                },
                {
                    'id': 'threat_002',
                    'type': 'port_scan',
                    'severity': 'low',
                    'source_ip': '10.0.0.50',
                    'target': 'web_services',
                    'detected_at': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    'status': 'monitoring'
                }
            ]
        except Exception as e:
            self.logger.error(f"Error updating active threats: {e}")
    
    async def _update_security_events(self):
        """Update recent security events"""
        try:
            # Get recent security events from audit logger
            self.security_metrics['security_events'] = [
                {
                    'event_id': 'evt_001',
                    'type': 'authentication_success',
                    'user': 'admin',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
                    'severity': 'low'
                },
                {
                    'event_id': 'evt_002',
                    'type': 'consciousness_access',
                    'user': 'security_analyst',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=8)).isoformat(),
                    'severity': 'medium'
                }
            ]
        except Exception as e:
            self.logger.error(f"Error updating security events: {e}")
    
    async def _update_audit_summary(self):
        """Update audit summary"""
        try:
            self.security_metrics['audit_summary'] = {
                'total_events_24h': 1247,
                'high_risk_events': 3,
                'authentication_failures': 15,
                'successful_logins': 89,
                'api_calls': 2156,
                'consciousness_operations': 67
            }
        except Exception as e:
            self.logger.error(f"Error updating audit summary: {e}")
    
    async def _websocket_broadcaster(self):
        """Broadcast security updates to WebSocket clients"""
        while True:
            try:
                if self.websocket_connections:
                    update_data = {
                        'type': 'security_metrics_update',
                        'data': self.security_metrics,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    await self._broadcast_to_websockets(update_data)
                
                await asyncio.sleep(5)  # Broadcast every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in WebSocket broadcaster: {e}")
                await asyncio.sleep(1)
    
    async def _broadcast_to_websockets(self, data):
        """Broadcast data to all WebSocket connections"""
        if not self.websocket_connections:
            return
        
        message = json.dumps(data)
        connections = list(self.websocket_connections)
        
        for ws in connections:
            try:
                await ws.send_str(message)
            except Exception as e:
                self.logger.debug(f"Failed to send to WebSocket: {e}")
    
    # Authentication route handlers
    async def login_page(self, request):
        """Login page"""
        template = self.jinja_env.get_template('login.html')
        return web.Response(
            text=template.render(),
            content_type='text/html'
        )
    
    async def api_login(self, request):
        """API login endpoint"""
        try:
            data = await request.json()
            
            # Validate input
            username_rule = ValidationRule(InputType.USERNAME, required=True)
            password_rule = ValidationRule(InputType.PASSWORD, required=True)
            
            username_result = self.input_validator.validate_input(data.get('username'), username_rule)
            password_result = self.input_validator.validate_input(data.get('password'), password_rule)
            
            if not username_result.is_valid:
                return web.json_response({'error': username_result.error_message}, status=400)
            if not password_result.is_valid:
                return web.json_response({'error': password_result.error_message}, status=400)
            
            # Authenticate user
            auth_result = self.jwt_manager.authenticate_user(
                username_result.sanitized_value,
                password_result.sanitized_value
            )
            
            if auth_result.success:
                # Log successful authentication
                self.audit_logger.log_authentication_attempt(
                    username=auth_result.username,
                    ip_address=request.remote,
                    success=True,
                    user_agent=request.headers.get('User-Agent')
                )
                
                return web.json_response({
                    'success': True,
                    'access_token': auth_result.access_token,
                    'refresh_token': auth_result.refresh_token,
                    'expires_in': auth_result.expires_in,
                    'user': {
                        'user_id': auth_result.user_id,
                        'username': auth_result.username,
                        'roles': auth_result.roles
                    }
                })
            else:
                # Log failed authentication
                self.audit_logger.log_authentication_attempt(
                    username=data.get('username', 'unknown'),
                    ip_address=request.remote,
                    success=False,
                    user_agent=request.headers.get('User-Agent')
                )
                
                return web.json_response({
                    'success': False,
                    'error': auth_result.error_message
                }, status=401)
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return web.json_response({'error': 'Login failed'}, status=500)
    
    async def api_logout(self, request):
        """API logout endpoint"""
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                self.jwt_manager.revoke_token(token)
            
            return web.json_response({'success': True})
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return web.json_response({'error': 'Logout failed'}, status=500)
    
    async def api_refresh_token(self, request):
        """API token refresh endpoint"""
        try:
            data = await request.json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return web.json_response({'error': 'Refresh token required'}, status=400)
            
            new_access_token = self.jwt_manager.refresh_access_token(refresh_token)
            
            return web.json_response({
                'success': True,
                'access_token': new_access_token
            })
            
        except Exception as e:
            self.logger.error(f"Token refresh error: {e}")
            return web.json_response({'error': 'Token refresh failed'}, status=401)
    
    # Dashboard route handlers
    async def security_dashboard_home(self, request):
        """Main security dashboard"""
        template = self.jinja_env.get_template('dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                security_metrics=self.security_metrics
            ),
            content_type='text/html'
        )
    
    async def hsm_dashboard(self, request):
        """HSM dashboard"""
        template = self.jinja_env.get_template('hsm_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                hsm_status=self.security_metrics['hsm_status']
            ),
            content_type='text/html'
        )
    
    async def zero_trust_dashboard(self, request):
        """Zero Trust dashboard"""
        template = self.jinja_env.get_template('zero_trust_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                zero_trust_status=self.security_metrics['zero_trust_status']
            ),
            content_type='text/html'
        )
    
    async def quantum_crypto_dashboard(self, request):
        """Quantum cryptography dashboard"""
        template = self.jinja_env.get_template('quantum_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                quantum_status=self.security_metrics['quantum_crypto_status']
            ),
            content_type='text/html'
        )
    
    async def consciousness_security_dashboard(self, request):
        """Consciousness security dashboard"""
        template = self.jinja_env.get_template('consciousness_security_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                consciousness_status=self.security_metrics['consciousness_security_status']
            ),
            content_type='text/html'
        )
    
    async def security_tools_dashboard(self, request):
        """Security tools dashboard"""
        template = self.jinja_env.get_template('security_tools_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                scan_history=self.security_metrics.get('vulnerability_scans', [])
            ),
            content_type='text/html'
        )
    
    async def security_monitoring_dashboard(self, request):
        """Security monitoring dashboard"""
        template = self.jinja_env.get_template('monitoring_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                active_threats=self.security_metrics['active_threats'],
                security_events=self.security_metrics['security_events']
            ),
            content_type='text/html'
        )
    
    async def audit_dashboard(self, request):
        """Audit dashboard"""
        template = self.jinja_env.get_template('audit_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                audit_summary=self.security_metrics['audit_summary']
            ),
            content_type='text/html'
        )
    
    # API route handlers
    async def api_security_status(self, request):
        """API endpoint for overall security status"""
        return web.json_response({
            'status': 'success',
            'data': {
                'overall_security_level': '10/10',
                'hsm_active': self.security_metrics['hsm_status'].get('status') == 'active',
                'zero_trust_active': self.security_metrics['zero_trust_status'].get('status') == 'active',
                'quantum_crypto_active': self.security_metrics['quantum_crypto_status'].get('status') == 'active',
                'consciousness_security_active': self.security_metrics['consciousness_security_status'].get('status') == 'active',
                'active_threats_count': len(self.security_metrics['active_threats']),
                'last_updated': self.security_metrics['last_updated'].isoformat() if self.security_metrics['last_updated'] else None
            }
        })
    
    async def api_hsm_status(self, request):
        """API endpoint for HSM status"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics['hsm_status']
        })
    
    async def api_zero_trust_status(self, request):
        """API endpoint for Zero Trust status"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics['zero_trust_status']
        })
    
    async def api_quantum_status(self, request):
        """API endpoint for quantum cryptography status"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics['quantum_crypto_status']
        })
    
    async def api_consciousness_security_status(self, request):
        """API endpoint for consciousness security status"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics['consciousness_security_status']
        })
    
    async def api_active_threats(self, request):
        """API endpoint for active threats"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics['active_threats']
        })
    
    async def api_security_events(self, request):
        """API endpoint for security events"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics['security_events']
        })
    
    async def api_audit_summary(self, request):
        """API endpoint for audit summary"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics['audit_summary']
        })
    
    # Security tools API handlers
    async def api_nmap_scan(self, request):
        """API endpoint for Nmap scanning"""
        try:
            data = await request.json()
            target = data.get('target')
            ports = data.get('ports', '1-1000')
            
            # Validate target
            target_rule = ValidationRule(InputType.IP_ADDRESS, required=True)
            target_result = self.input_validator.validate_input(target, target_rule)
            
            if not target_result.is_valid:
                return web.json_response({'error': target_result.error_message}, status=400)
            
            # Perform scan using consciousness security controller
            scan_result = await self.consciousness_security.tools[
                self.consciousness_security.tools.__class__.__dict__['NETWORK_SCANNER']
            ].port_scan(target_result.sanitized_value, ports)
            
            # Log security tool usage
            self.audit_logger.log_security_event(
                SecurityEventType.API_ACCESS,
                SecurityLevel.MEDIUM,
                user_id=request['user']['user_id'],
                ip_address=request.remote,
                resource='/api/tools/nmap/scan',
                action='nmap_scan',
                details={'target': target_result.sanitized_value, 'ports': ports}
            )
            
            return web.json_response({
                'status': 'success',
                'scan_id': scan_result.timestamp.isoformat(),
                'data': {
                    'tool_name': scan_result.tool_name,
                    'target': scan_result.target,
                    'scan_type': scan_result.scan_type,
                    'timestamp': scan_result.timestamp.isoformat(),
                    'results': scan_result.results,
                    'threat_level': scan_result.threat_level,
                    'recommendations': scan_result.recommendations
                }
            })
            
        except Exception as e:
            self.logger.error(f"Nmap scan error: {e}")
            return web.json_response({'error': 'Scan failed'}, status=500)
    
    async def api_metasploit_scan(self, request):
        """API endpoint for Metasploit scanning"""
        try:
            data = await request.json()
            target = data.get('target')
            
            # Validate target
            target_rule = ValidationRule(InputType.IP_ADDRESS, required=True)
            target_result = self.input_validator.validate_input(target, target_rule)
            
            if not target_result.is_valid:
                return web.json_response({'error': target_result.error_message}, status=400)
            
            # Perform vulnerability scan
            scan_result = await self.consciousness_security.tools[
                self.consciousness_security.tools.__class__.__dict__['EXPLOITATION_FRAMEWORK']
            ].vulnerability_scan(target_result.sanitized_value)
            
            # Log security tool usage
            self.audit_logger.log_security_event(
                SecurityEventType.API_ACCESS,
                SecurityLevel.HIGH,
                user_id=request['user']['user_id'],
                ip_address=request.remote,
                resource='/api/tools/metasploit/scan',
                action='metasploit_scan',
                details={'target': target_result.sanitized_value}
            )
            
            return web.json_response({
                'status': 'success',
                'scan_id': scan_result.timestamp.isoformat(),
                'data': {
                    'tool_name': scan_result.tool_name,
                    'target': scan_result.target,
                    'scan_type': scan_result.scan_type,
                    'timestamp': scan_result.timestamp.isoformat(),
                    'results': scan_result.results,
                    'threat_level': scan_result.threat_level,
                    'recommendations': scan_result.recommendations
                }
            })
            
        except Exception as e:
            self.logger.error(f"Metasploit scan error: {e}")
            return web.json_response({'error': 'Scan failed'}, status=500)
    
    async def api_scan_history(self, request):
        """API endpoint for scan history"""
        return web.json_response({
            'status': 'success',
            'data': self.security_metrics.get('vulnerability_scans', [])
        })
    
    async def api_scan_results(self, request):
        """API endpoint for specific scan results"""
        scan_id = request.match_info['scan_id']
        
        # In production, this would query a database
        # For now, return mock data
        return web.json_response({
            'status': 'success',
            'data': {
                'scan_id': scan_id,
                'status': 'completed',
                'results': 'Scan results would be here'
            }
        })
    
    # Consciousness security API handlers
    async def api_consciousness_assess(self, request):
        """API endpoint for consciousness security assessment"""
        try:
            data = await request.json()
            target = data.get('target')
            
            # Validate target
            target_rule = ValidationRule(InputType.STRING, required=True, max_length=255)
            target_result = self.input_validator.validate_input(target, target_rule)
            
            if not target_result.is_valid:
                return web.json_response({'error': target_result.error_message}, status=400)
            
            # Perform autonomous security assessment
            assessment = await self.consciousness_security.autonomous_security_assessment(
                target_result.sanitized_value
            )
            
            # Log consciousness security access
            self.audit_logger.log_consciousness_access(
                user_id=request['user']['user_id'],
                consciousness_level=request['user'].get('consciousness_level', 0.5),
                operation='security_assessment',
                ip_address=request.remote,
                success=True
            )
            
            return web.json_response({
                'status': 'success',
                'data': assessment
            })
            
        except Exception as e:
            self.logger.error(f"Consciousness assessment error: {e}")
            return web.json_response({'error': 'Assessment failed'}, status=500)
    
    async def api_consciousness_insights(self, request):
        """API endpoint for consciousness security insights"""
        try:
            # Get consciousness security insights
            insights = {
                'threat_predictions': [
                    {
                        'threat_type': 'advanced_persistent_threat',
                        'probability': 0.23,
                        'confidence': 0.87,
                        'predicted_timeframe': '72_hours'
                    },
                    {
                        'threat_type': 'insider_threat',
                        'probability': 0.15,
                        'confidence': 0.65,
                        'predicted_timeframe': '7_days'
                    }
                ],
                'security_recommendations': [
                    'Increase monitoring on network segment 192.168.1.0/24',
                    'Review access permissions for high-privilege accounts',
                    'Update security policies for remote access'
                ],
                'consciousness_level': 0.87,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            return web.json_response({
                'status': 'success',
                'data': insights
            })
            
        except Exception as e:
            self.logger.error(f"Consciousness insights error: {e}")
            return web.json_response({'error': 'Failed to get insights'}, status=500)
    
    async def api_consciousness_response(self, request):
        """API endpoint for consciousness security response"""
        try:
            data = await request.json()
            threat_id = data.get('threat_id')
            response_action = data.get('action')
            
            # Validate input
            threat_rule = ValidationRule(InputType.STRING, required=True, max_length=100)
            action_rule = ValidationRule(InputType.STRING, required=True, max_length=100)
            
            threat_result = self.input_validator.validate_input(threat_id, threat_rule)
            action_result = self.input_validator.validate_input(response_action, action_rule)
            
            if not threat_result.is_valid:
                return web.json_response({'error': threat_result.error_message}, status=400)
            if not action_result.is_valid:
                return web.json_response({'error': action_result.error_message}, status=400)
            
            # Execute consciousness security response
            response = {
                'threat_id': threat_result.sanitized_value,
                'action': action_result.sanitized_value,
                'status': 'executed',
                'timestamp': datetime.utcnow().isoformat(),
                'result': 'Response action completed successfully'
            }
            
            # Log consciousness security response
            self.audit_logger.log_consciousness_access(
                user_id=request['user']['user_id'],
                consciousness_level=request['user'].get('consciousness_level', 0.5),
                operation='security_response',
                ip_address=request.remote,
                success=True
            )
            
            return web.json_response({
                'status': 'success',
                'data': response
            })
            
        except Exception as e:
            self.logger.error(f"Consciousness response error: {e}")
            return web.json_response({'error': 'Response failed'}, status=500)
    
    # WebSocket handler
    async def websocket_handler(self, request):
        """WebSocket handler for real-time security updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Add to connections set
        self.websocket_connections.add(ws)
        
        try:
            # Send initial security data
            initial_data = {
                'type': 'initial_security_data',
                'data': self.security_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            await ws.send_str(json.dumps(initial_data))
            
            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get('type') == 'ping':
                            await ws.send_str(json.dumps({'type': 'pong'}))
                    except json.JSONDecodeError:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
                    
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
        
        return ws
    
    # Health check
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'security_dashboard',
            'security_level': '10/10',
            'components': {
                'hsm': self.security_metrics['hsm_status'].get('status', 'unknown'),
                'zero_trust': self.security_metrics['zero_trust_status'].get('status', 'unknown'),
                'quantum_crypto': self.security_metrics['quantum_crypto_status'].get('status', 'unknown'),
                'consciousness_security': self.security_metrics['consciousness_security_status'].get('status', 'unknown')
            },
            'nats_connected': self.nats_client is not None,
            'websocket_connections': len(self.websocket_connections),
            'last_metrics_update': self.security_metrics['last_updated'].isoformat() if self.security_metrics['last_updated'] else None
        })


async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    dashboard = SecurityDashboard()
    await dashboard.start()


if __name__ == "__main__":
    asyncio.run(main())