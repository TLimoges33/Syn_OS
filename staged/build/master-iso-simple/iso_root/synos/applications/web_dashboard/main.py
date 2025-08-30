#!/usr/bin/env python3
"""
Syn_OS Web Dashboard

A comprehensive web-based dashboard for monitoring and controlling the
consciousness-aware infrastructure. Provides real-time system monitoring,
service management, consciousness insights, and user analytics.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors
import nats
from jinja2 import Environment, FileSystemLoader
import weakref

# Add the consciousness system to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class WebDashboard:
    """Main web dashboard application"""
    
    def __init__(self):
        self.app = web.Application()
        self.nats_client = None
        self.websocket_connections = weakref.WeakSet()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
        self.orchestrator_url = os.getenv('ORCHESTRATOR_URL', 'http://localhost:8080')
        self.consciousness_url = os.getenv('CONSCIOUSNESS_URL', 'http://localhost:8081')
        self.security_tutor_url = os.getenv('SECURITY_TUTOR_URL', 'http://localhost:8082')
        self.port = int(os.getenv('DASHBOARD_PORT', '3000'))
        
        # Jinja2 template environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # System metrics cache
        self.metrics_cache = {
            'last_updated': None,
            'system_status': {},
            'service_list': [],
            'consciousness_state': {},
            'user_analytics': {}
        }
        
        self._setup_routes()
        self._setup_cors()
    
    def _setup_routes(self):
        """Setup web application routes"""
        # Static files
        self.app.router.add_static('/static', 'applications/web_dashboard/static')
        
        # Main dashboard routes
        self.app.router.add_get('/', self.dashboard_home)
        self.app.router.add_get('/services', self.services_page)
        self.app.router.add_get('/consciousness', self.consciousness_page)
        self.app.router.add_get('/users', self.users_page)
        self.app.router.add_get('/analytics', self.analytics_page)
        
        # API routes
        self.app.router.add_get('/api/system/status', self.api_system_status)
        self.app.router.add_get('/api/services', self.api_services)
        self.app.router.add_get('/api/consciousness/state', self.api_consciousness_state)
        self.app.router.add_get('/api/consciousness/metrics', self.api_consciousness_metrics)
        self.app.router.add_get('/api/users/analytics', self.api_user_analytics)
        self.app.router.add_post('/api/services/{service_name}/{action}', self.api_service_control)
        
        # WebSocket for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Health check
        self.app.router.add_get('/health', self.health_check)
    
    def _setup_cors(self):
        """Setup CORS for API access"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def start(self):
        """Start the web dashboard"""
        self.logger.info("Starting Syn_OS Web Dashboard...")
        
        # Connect to NATS for real-time updates
        await self._connect_nats()
        
        # Start metrics collection
        asyncio.create_task(self._metrics_collector())
        
        # Start WebSocket broadcaster
        asyncio.create_task(self._websocket_broadcaster())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        self.logger.info(f"Web Dashboard started on port {self.port}")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down Web Dashboard...")
        finally:
            await runner.cleanup()
            if self.nats_client:
                await self.nats_client.close()
    
    async def _connect_nats(self):
        """Connect to NATS for real-time updates"""
        try:
            self.nats_client = await nats.connect(self.nats_url)
            
            # Subscribe to system events
            await self.nats_client.subscribe("orchestrator.>", self._handle_orchestrator_event)
            await self.nats_client.subscribe("consciousness.>", self._handle_consciousness_event)
            
            self.logger.info("Connected to NATS for real-time updates")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to NATS: {e}")
    
    async def _handle_orchestrator_event(self, msg):
        """Handle orchestrator events"""
        try:
            data = json.loads(msg.data.decode())
            
            # Update metrics cache
            if msg.subject.startswith("orchestrator.service"):
                await self._update_service_metrics()
            
            # Broadcast to WebSocket clients
            await self._broadcast_to_websockets({
                'type': 'orchestrator_event',
                'subject': msg.subject,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error handling orchestrator event: {e}")
    
    async def _handle_consciousness_event(self, msg):
        """Handle consciousness events"""
        try:
            data = json.loads(msg.data.decode())
            
            # Update consciousness state cache
            if msg.subject == "consciousness.state_change":
                self.metrics_cache['consciousness_state'].update(data.get('data', {}))
            
            # Broadcast to WebSocket clients
            await self._broadcast_to_websockets({
                'type': 'consciousness_event',
                'subject': msg.subject,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error handling consciousness event: {e}")
    
    async def _metrics_collector(self):
        """Collect system metrics periodically"""
        while True:
            try:
                # Collect system status
                await self._update_system_status()
                await self._update_service_metrics()
                await self._update_consciousness_metrics()
                await self._update_user_analytics()
                
                self.metrics_cache['last_updated'] = datetime.utcnow()
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(10)
    
    async def _update_system_status(self):
        """Update system status metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check orchestrator health
                try:
                    async with session.get(f"{self.orchestrator_url}/health", timeout=5) as resp:
                        if resp.status == 200:
                            orchestrator_health = await resp.json()
                        else:
                            orchestrator_health = {'status': 'unhealthy'}
                except:
                    orchestrator_health = {'status': 'unreachable'}
                
                # Check consciousness health
                try:
                    async with session.get(f"{self.consciousness_url}/health", timeout=5) as resp:
                        if resp.status == 200:
                            consciousness_health = await resp.json()
                        else:
                            consciousness_health = {'status': 'unhealthy'}
                except:
                    consciousness_health = {'status': 'unreachable'}
                
                # Check security tutor health
                try:
                    async with session.get(f"{self.security_tutor_url}/health", timeout=5) as resp:
                        if resp.status == 200:
                            security_tutor_health = await resp.json()
                        else:
                            security_tutor_health = {'status': 'unhealthy'}
                except:
                    security_tutor_health = {'status': 'unreachable'}
                
                self.metrics_cache['system_status'] = {
                    'orchestrator': orchestrator_health,
                    'consciousness': consciousness_health,
                    'security_tutor': security_tutor_health,
                    'overall_health': self._calculate_overall_health([
                        orchestrator_health, consciousness_health, security_tutor_health
                    ])
                }
                
        except Exception as e:
            self.logger.error(f"Error updating system status: {e}")
    
    async def _update_service_metrics(self):
        """Update service metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.orchestrator_url}/api/v1/services", timeout=10) as resp:
                    if resp.status == 200:
                        services = await resp.json()
                        self.metrics_cache['service_list'] = services
                    else:
                        self.metrics_cache['service_list'] = []
                        
        except Exception as e:
            self.logger.error(f"Error updating service metrics: {e}")
    
    async def _update_consciousness_metrics(self):
        """Update consciousness metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.consciousness_url}/metrics", timeout=10) as resp:
                    if resp.status == 200:
                        metrics = await resp.json()
                        self.metrics_cache['consciousness_state'].update(metrics)
                        
        except Exception as e:
            self.logger.error(f"Error updating consciousness metrics: {e}")
    
    async def _update_user_analytics(self):
        """Update user analytics"""
        try:
            # This would typically aggregate user data from the security tutor
            # For now, we'll use mock data
            self.metrics_cache['user_analytics'] = {
                'total_users': 42,
                'active_users_today': 15,
                'total_sessions': 128,
                'average_session_length': 18.5,
                'completion_rate': 0.73,
                'top_modules': [
                    {'name': 'Phishing Recognition', 'completions': 35},
                    {'name': 'Password Security', 'completions': 28},
                    {'name': 'Network Security', 'completions': 15}
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error updating user analytics: {e}")
    
    def _calculate_overall_health(self, health_statuses):
        """Calculate overall system health"""
        healthy_count = sum(1 for status in health_statuses if status.get('status') == 'healthy')
        total_count = len(health_statuses)
        
        if healthy_count == total_count:
            return 'healthy'
        elif healthy_count > 0:
            return 'degraded'
        else:
            return 'unhealthy'
    
    async def _websocket_broadcaster(self):
        """Broadcast updates to WebSocket clients"""
        while True:
            try:
                if self.websocket_connections:
                    # Send periodic updates
                    update_data = {
                        'type': 'metrics_update',
                        'data': {
                            'system_status': self.metrics_cache['system_status'],
                            'service_count': len(self.metrics_cache['service_list']),
                            'consciousness_state': self.metrics_cache['consciousness_state'].get('consciousness', {}),
                            'user_analytics': self.metrics_cache['user_analytics']
                        },
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
        
        # Create a list to avoid modification during iteration
        connections = list(self.websocket_connections)
        
        for ws in connections:
            try:
                await ws.send_str(message)
            except Exception as e:
                self.logger.debug(f"Failed to send to WebSocket: {e}")
                # Connection will be automatically removed from WeakSet
    
    # Route handlers
    async def dashboard_home(self, request):
        """Main dashboard page"""
        template = self.jinja_env.get_template('dashboard.html')
        return web.Response(
            text=template.render(
                system_status=self.metrics_cache['system_status'],
                service_count=len(self.metrics_cache['service_list']),
                consciousness_state=self.metrics_cache['consciousness_state'],
                user_analytics=self.metrics_cache['user_analytics']
            ),
            content_type='text/html'
        )
    
    async def services_page(self, request):
        """Services management page"""
        template = self.jinja_env.get_template('services.html')
        return web.Response(
            text=template.render(services=self.metrics_cache['service_list']),
            content_type='text/html'
        )
    
    async def consciousness_page(self, request):
        """Consciousness monitoring page"""
        template = self.jinja_env.get_template('consciousness.html')
        return web.Response(
            text=template.render(consciousness_state=self.metrics_cache['consciousness_state']),
            content_type='text/html'
        )
    
    async def users_page(self, request):
        """Users analytics page"""
        template = self.jinja_env.get_template('users.html')
        return web.Response(
            text=template.render(user_analytics=self.metrics_cache['user_analytics']),
            content_type='text/html'
        )
    
    async def analytics_page(self, request):
        """System analytics page"""
        template = self.jinja_env.get_template('analytics.html')
        return web.Response(
            text=template.render(
                system_status=self.metrics_cache['system_status'],
                services=self.metrics_cache['service_list'],
                consciousness_state=self.metrics_cache['consciousness_state'],
                user_analytics=self.metrics_cache['user_analytics']
            ),
            content_type='text/html'
        )
    
    # API handlers
    async def api_system_status(self, request):
        """API endpoint for system status"""
        return web.json_response(self.metrics_cache['system_status'])
    
    async def api_services(self, request):
        """API endpoint for services list"""
        return web.json_response(self.metrics_cache['service_list'])
    
    async def api_consciousness_state(self, request):
        """API endpoint for consciousness state"""
        return web.json_response(self.metrics_cache['consciousness_state'])
    
    async def api_consciousness_metrics(self, request):
        """API endpoint for consciousness metrics"""
        return web.json_response(self.metrics_cache['consciousness_state'])
    
    async def api_user_analytics(self, request):
        """API endpoint for user analytics"""
        return web.json_response(self.metrics_cache['user_analytics'])
    
    async def api_service_control(self, request):
        """API endpoint for service control"""
        service_name = request.match_info['service_name']
        action = request.match_info['action']
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.orchestrator_url}/api/v1/services/{service_name}/{action}",
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return web.json_response(result)
                    else:
                        return web.json_response(
                            {'error': f'Service control failed: {resp.status}'},
                            status=resp.status
                        )
                        
        except Exception as e:
            return web.json_response(
                {'error': f'Service control error: {str(e)}'},
                status=500
            )
    
    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Add to connections set
        self.websocket_connections.add(ws)
        
        try:
            # Send initial data
            initial_data = {
                'type': 'initial_data',
                'data': {
                    'system_status': self.metrics_cache['system_status'],
                    'services': self.metrics_cache['service_list'],
                    'consciousness_state': self.metrics_cache['consciousness_state'],
                    'user_analytics': self.metrics_cache['user_analytics']
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            await ws.send_str(json.dumps(initial_data))
            
            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        # Handle client requests if needed
                        if data.get('type') == 'ping':
                            await ws.send_str(json.dumps({'type': 'pong'}))
                    except json.JSONDecodeError:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
                    
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
        finally:
            # Connection will be automatically removed from WeakSet
            pass
        
        return ws
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'web_dashboard',
            'nats_connected': self.nats_client is not None,
            'websocket_connections': len(self.websocket_connections),
            'last_metrics_update': self.metrics_cache['last_updated'].isoformat() if self.metrics_cache['last_updated'] else None
        })


async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    dashboard = WebDashboard()
    await dashboard.start()


if __name__ == "__main__":
    asyncio.run(main())