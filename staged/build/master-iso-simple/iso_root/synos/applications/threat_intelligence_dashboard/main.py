#!/usr/bin/env python3
"""
Comprehensive Threat Intelligence Dashboard with Real-Time Visualization
======================================================================

Advanced threat intelligence dashboard integrating:
- Real-time threat feed aggregation from 50+ OSINT sources
- Global threat intelligence architecture with consciousness integration
- Interactive visualizations and threat correlation analysis
- Real-time streaming updates with WebSocket support
- Advanced threat hunting and investigation capabilities
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
import plotly.graph_objects as go
import plotly.utils
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
import weakref

# Add required modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import threat intelligence components
from security_orchestration.global_threat_intelligence_architecture import (
    GlobalThreatIntelligenceOrchestrator, 
    create_global_threat_intelligence_architecture
)
from security_orchestration.realtime_threat_aggregator import (
    RealTimeThreatAggregator,
    create_realtime_threat_aggregator
)
from security.jwt_auth import get_jwt_manager, TokenType, UserRole
from security.audit_logger import get_audit_logger, SecurityEventType, SecurityLevel
from security.input_validator import get_validator, ValidationRule, InputType

logger = logging.getLogger(__name__)


class ThreatIntelligenceDashboard:
    """
    Comprehensive threat intelligence dashboard with real-time visualization
    Integrates global threat intelligence and real-time threat aggregation
    """
    
    def __init__(self):
        self.app = web.Application()
        self.websocket_connections = weakref.WeakSet()
        self.logger = logging.getLogger(__name__)
        
        # Security components
        self.jwt_manager = get_jwt_manager()
        self.audit_logger = get_audit_logger()
        self.input_validator = get_validator()
        
        # Threat intelligence components
        self.global_threat_orchestrator: Optional[GlobalThreatIntelligenceOrchestrator] = None
        self.realtime_aggregator: Optional[RealTimeThreatAggregator] = None
        
        # Configuration
        self.nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.port = int(os.getenv('THREAT_INTEL_DASHBOARD_PORT', '8084'))
        
        # Template environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Dashboard data cache
        self.dashboard_data = {
            'threat_feeds': {
                'active_sources': 0,
                'items_processed': 0,
                'real_time_threats': [],
                'threat_categories': {},
                'geographic_distribution': {},
                'severity_distribution': {},
                'source_reliability': {}
            },
            'global_intelligence': {
                'active_nodes': 0,
                'correlations_found': 0,
                'predictions_generated': 0,
                'quantum_threats': 0,
                'consciousness_enhanced': 0,
                'global_campaigns': [],
                'threat_trends': {}
            },
            'visualizations': {
                'threat_timeline': None,
                'geographic_heatmap': None,
                'correlation_network': None,
                'severity_pie_chart': None,
                'source_reliability_bar': None,
                'threat_prediction_line': None
            },
            'last_updated': None
        }
        
        self._setup_routes()
        self._setup_cors()
        self._setup_security_middleware()
    
    def _setup_routes(self):
        """Setup dashboard routes"""
        # Static files
        self.app.router.add_static('/static', 'applications/threat_intelligence_dashboard/static')
        
        # Authentication routes
        self.app.router.add_get('/login', self.login_page)
        self.app.router.add_post('/api/auth/login', self.api_login)
        self.app.router.add_post('/api/auth/logout', self.api_logout)
        
        # Main dashboard routes (protected)
        self.app.router.add_get('/', self.main_dashboard)
        self.app.router.add_get('/feeds', self.threat_feeds_dashboard)
        self.app.router.add_get('/intelligence', self.global_intelligence_dashboard)
        self.app.router.add_get('/correlations', self.threat_correlations_dashboard)
        self.app.router.add_get('/hunting', self.threat_hunting_dashboard)
        self.app.router.add_get('/analytics', self.threat_analytics_dashboard)
        
        # API routes (protected)
        self.app.router.add_get('/api/dashboard/overview', self.api_dashboard_overview)
        self.app.router.add_get('/api/threats/feeds/status', self.api_threat_feeds_status)
        self.app.router.add_get('/api/threats/feeds/sources', self.api_threat_feed_sources)
        self.app.router.add_get('/api/threats/real-time', self.api_real_time_threats)
        self.app.router.add_get('/api/intelligence/global/status', self.api_global_intelligence_status)
        self.app.router.add_get('/api/intelligence/correlations', self.api_threat_correlations)
        self.app.router.add_get('/api/intelligence/predictions', self.api_threat_predictions)
        self.app.router.add_get('/api/analytics/visualizations', self.api_visualizations)
        self.app.router.add_post('/api/hunting/search', self.api_threat_hunt_search)
        self.app.router.add_post('/api/intelligence/assess', self.api_assess_threat)
        
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
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_security_middleware(self):
        """Setup security middleware"""
        @web.middleware
        async def security_headers_middleware(request, handler):
            response = await handler(request)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.plot.ly; style-src 'self' 'unsafe-inline'"
            return response
        
        @web.middleware
        async def auth_middleware(request, handler):
            """Authentication middleware for protected routes"""
            public_routes = ['/health', '/login', '/api/auth/login', '/static']
            if any(request.path.startswith(route) for route in public_routes):
                return await handler(request)
            
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                if request.path.startswith('/api/'):
                    return web.json_response({'error': 'Authentication required'}, status=401)
                else:
                    return web.Response(status=302, headers={'Location': '/login'})
            
            token = auth_header.split(' ')[1]
            
            try:
                claims = self.jwt_manager.verify_token(token, TokenType.ACCESS)
                request['user'] = {
                    'user_id': claims.user_id,
                    'username': claims.username,
                    'roles': claims.roles
                }
                return await handler(request)
            except Exception as e:
                self.logger.warning(f"Authentication failed: {e}")
                if request.path.startswith('/api/'):
                    return web.json_response({'error': 'Invalid token'}, status=401)
                else:
                    return web.Response(status=302, headers={'Location': '/login'})
        
        self.app.middlewares.append(security_headers_middleware)
        self.app.middlewares.append(auth_middleware)
    
    async def start(self):
        """Start the threat intelligence dashboard"""
        self.logger.info("Starting Comprehensive Threat Intelligence Dashboard...")
        
        # Initialize threat intelligence components
        await self._initialize_threat_intelligence_systems()
        
        # Start data collection loops
        asyncio.create_task(self._threat_intelligence_collector())
        asyncio.create_task(self._visualization_generator())
        asyncio.create_task(self._websocket_broadcaster())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        self.logger.info(f"Threat Intelligence Dashboard started on port {self.port}")
        
        # Log system startup
        self.audit_logger.log_security_event(
            SecurityEventType.SYSTEM_STARTUP,
            SecurityLevel.MEDIUM,
            details={'component': 'threat_intelligence_dashboard', 'port': self.port}
        )
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down Threat Intelligence Dashboard...")
        finally:
            await runner.cleanup()
            await self._shutdown_threat_intelligence_systems()
    
    async def _initialize_threat_intelligence_systems(self):
        """Initialize threat intelligence components"""
        try:
            self.logger.info("Initializing threat intelligence systems...")
            
            # Initialize global threat intelligence orchestrator
            self.global_threat_orchestrator = create_global_threat_intelligence_architecture()
            await self.global_threat_orchestrator.initialize_architecture("hybrid")
            
            # Initialize real-time threat aggregator
            self.realtime_aggregator = create_realtime_threat_aggregator()
            await self.realtime_aggregator.initialize(self.redis_url)
            
            self.logger.info("Threat intelligence systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize threat intelligence systems: {e}")
            raise
    
    async def _shutdown_threat_intelligence_systems(self):
        """Shutdown threat intelligence components"""
        try:
            if self.global_threat_orchestrator:
                await self.global_threat_orchestrator.shutdown()
            if self.realtime_aggregator:
                await self.realtime_aggregator.shutdown()
            
            self.logger.info("Threat intelligence systems shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error shutting down threat intelligence systems: {e}")
    
    async def _threat_intelligence_collector(self):
        """Collect threat intelligence data periodically"""
        while True:
            try:
                # Update threat feed data
                await self._update_threat_feeds_data()
                
                # Update global intelligence data
                await self._update_global_intelligence_data()
                
                self.dashboard_data['last_updated'] = datetime.utcnow()
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error collecting threat intelligence data: {e}")
                await asyncio.sleep(30)
    
    async def _update_threat_feeds_data(self):
        """Update threat feeds data"""
        try:
            if not self.realtime_aggregator:
                return
            
            # Get aggregation status
            status = self.realtime_aggregator.get_aggregation_status()
            
            self.dashboard_data['threat_feeds'].update({
                'active_sources': status.get('sources_active', 0),
                'items_processed': status.get('processed_items', 0),
                'queue_size': status.get('queue_size', 0),
                'processing_rate': status.get('metrics', {}).get('processing_rate', 0),
                'errors_encountered': status.get('metrics', {}).get('errors_encountered', 0),
                'consciousness_enhancements': status.get('metrics', {}).get('consciousness_enhancements', 0),
                'quantum_threats_detected': status.get('metrics', {}).get('quantum_threats_detected', 0)
            })
            
            # Generate mock real-time threats for demonstration
            self.dashboard_data['threat_feeds']['real_time_threats'] = [
                {
                    'id': f'threat_{i}',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
                    'source': f'source_{i % 5}',
                    'indicator_type': ['ip', 'domain', 'hash', 'url'][i % 4],
                    'indicator_value': f'192.168.1.{100+i}' if i % 4 == 0 else f'malicious-domain-{i}.com',
                    'threat_type': ['malware', 'phishing', 'botnet', 'apt'][i % 4],
                    'severity': ['high', 'medium', 'low'][i % 3],
                    'confidence': 0.7 + (i % 3) * 0.1,
                    'consciousness_score': 0.5 + (i % 5) * 0.1
                }
                for i in range(20)
            ]
            
        except Exception as e:
            self.logger.error(f"Error updating threat feeds data: {e}")
    
    async def _update_global_intelligence_data(self):
        """Update global intelligence data"""
        try:
            if not self.global_threat_orchestrator:
                return
            
            # Get architecture status
            status = self.global_threat_orchestrator.get_architecture_status()
            
            self.dashboard_data['global_intelligence'].update({
                'active_nodes': status.get('active_nodes', 0),
                'correlations_found': status.get('metrics', {}).get('correlations_found', 0),
                'predictions_generated': status.get('metrics', {}).get('predictions_generated', 0),
                'quantum_threats': status.get('metrics', {}).get('quantum_threats_detected', 0),
                'consciousness_enhanced': status.get('metrics', {}).get('consciousness_enhanced_detections', 0),
                'threats_processed': status.get('metrics', {}).get('threats_processed', 0)
            })
            
            # Generate mock global campaigns for demonstration
            self.dashboard_data['global_intelligence']['global_campaigns'] = [
                {
                    'campaign_id': 'apt_campaign_001',
                    'name': 'Advanced Persistent Threat Campaign Alpha',
                    'threat_actors': ['APT28', 'Unknown'],
                    'targets': ['Financial Services', 'Government'],
                    'start_date': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    'indicators_count': 156,
                    'confidence': 0.92,
                    'consciousness_verified': True
                },
                {
                    'campaign_id': 'phishing_campaign_002',
                    'name': 'Global Phishing Campaign Beta',
                    'threat_actors': ['Lazarus Group'],
                    'targets': ['Healthcare', 'Education'],
                    'start_date': (datetime.utcnow() - timedelta(days=15)).isoformat(),
                    'indicators_count': 89,
                    'confidence': 0.85,
                    'consciousness_verified': True
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Error updating global intelligence data: {e}")
    
    async def _visualization_generator(self):
        """Generate visualizations periodically"""
        while True:
            try:
                # Generate threat timeline
                await self._generate_threat_timeline()
                
                # Generate geographic heatmap
                await self._generate_geographic_heatmap()
                
                # Generate correlation network
                await self._generate_correlation_network()
                
                # Generate severity distribution
                await self._generate_severity_distribution()
                
                # Generate source reliability chart
                await self._generate_source_reliability_chart()
                
                # Generate threat prediction chart
                await self._generate_threat_prediction_chart()
                
                await asyncio.sleep(30)  # Update visualizations every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error generating visualizations: {e}")
                await asyncio.sleep(60)
    
    async def _generate_threat_timeline(self):
        """Generate threat timeline visualization"""
        try:
            # Generate sample data
            dates = [datetime.utcnow() - timedelta(hours=i) for i in range(24, 0, -1)]
            threat_counts = np.random.poisson(15, 24)
            high_severity = np.random.poisson(3, 24)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=threat_counts,
                mode='lines+markers',
                name='Total Threats',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=high_severity,
                mode='lines+markers',
                name='High Severity',
                line=dict(color='#d62728', width=2)
            ))
            
            fig.update_layout(
                title='Threat Intelligence Timeline (24 Hours)',
                xaxis_title='Time',
                yaxis_title='Number of Threats',
                template='plotly_dark',
                height=400
            )
            
            self.dashboard_data['visualizations']['threat_timeline'] = fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error generating threat timeline: {e}")
    
    async def _generate_geographic_heatmap(self):
        """Generate geographic threat distribution heatmap"""
        try:
            # Sample geographic data
            countries = ['USA', 'CHN', 'RUS', 'KOR', 'IRN', 'DEU', 'GBR', 'FRA', 'JPN', 'IND']
            threat_counts = np.random.randint(5, 100, len(countries))
            
            fig = go.Figure(data=go.Choropleth(
                locations=countries,
                z=threat_counts,
                locationmode='ISO-3',
                colorscale='Reds',
                colorbar_title='Threat Count'
            ))
            
            fig.update_layout(
                title='Global Threat Geographic Distribution',
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='natural earth'
                ),
                template='plotly_dark',
                height=400
            )
            
            self.dashboard_data['visualizations']['geographic_heatmap'] = fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error generating geographic heatmap: {e}")
    
    async def _generate_correlation_network(self):
        """Generate threat correlation network visualization"""
        try:
            # Create a simple network visualization
            import networkx as nx
            
            G = nx.Graph()
            
            # Add nodes and edges for threat correlations
            threats = [f'Threat_{i}' for i in range(1, 11)]
            for threat in threats:
                G.add_node(threat)
            
            # Add random connections
            for i in range(15):
                threat1, threat2 = np.random.choice(threats, 2, replace=False)
                G.add_edge(threat1, threat2, weight=np.random.random())
            
            pos = nx.spring_layout(G)
            
            edge_trace = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace.extend([x0, x1, None])
                edge_trace.extend([y0, y1, None])
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G.nodes()],
                y=[pos[node][1] for node in G.nodes()],
                mode='markers+text',
                text=list(G.nodes()),
                textposition='middle center',
                marker=dict(size=20, color='lightblue'),
                name='Threats'
            )
            
            edge_trace_scatter = go.Scatter(
                x=edge_trace[::3],
                y=edge_trace[1::3],
                mode='lines',
                line=dict(width=1, color='gray'),
                name='Correlations',
                showlegend=False
            )
            
            fig = go.Figure(data=[edge_trace_scatter, node_trace])
            fig.update_layout(
                title='Threat Correlation Network',
                showlegend=False,
                template='plotly_dark',
                height=400,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            self.dashboard_data['visualizations']['correlation_network'] = fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error generating correlation network: {e}")
    
    async def _generate_severity_distribution(self):
        """Generate severity distribution pie chart"""
        try:
            severities = ['Critical', 'High', 'Medium', 'Low']
            counts = [12, 45, 78, 123]
            colors = ['#d62728', '#ff7f0e', '#ffbb33', '#2ca02c']
            
            fig = go.Figure(data=[go.Pie(
                labels=severities,
                values=counts,
                marker_colors=colors,
                hole=0.3
            )])
            
            fig.update_layout(
                title='Threat Severity Distribution',
                template='plotly_dark',
                height=400
            )
            
            self.dashboard_data['visualizations']['severity_pie_chart'] = fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error generating severity distribution: {e}")
    
    async def _generate_source_reliability_chart(self):
        """Generate source reliability bar chart"""
        try:
            sources = ['CISA', 'AlienVault', 'VirusTotal', 'Shodan', 'GitHub', 'Reddit']
            reliability = [0.98, 0.92, 0.94, 0.88, 0.88, 0.65]
            colors = ['#2ca02c' if r > 0.9 else '#ff7f0e' if r > 0.8 else '#d62728' for r in reliability]
            
            fig = go.Figure(data=[go.Bar(
                x=sources,
                y=reliability,
                marker_color=colors
            )])
            
            fig.update_layout(
                title='Source Reliability Scores',
                xaxis_title='Intelligence Sources',
                yaxis_title='Reliability Score',
                template='plotly_dark',
                height=400
            )
            
            self.dashboard_data['visualizations']['source_reliability_bar'] = fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error generating source reliability chart: {e}")
    
    async def _generate_threat_prediction_chart(self):
        """Generate threat prediction line chart"""
        try:
            # Generate prediction data
            hours = list(range(24))
            current_time = datetime.utcnow()
            times = [current_time + timedelta(hours=h) for h in hours]
            
            baseline_threats = 15 + 5 * np.sin(np.array(hours) * np.pi / 12)
            predicted_threats = baseline_threats + np.random.normal(0, 2, 24)
            confidence_upper = predicted_threats + 3
            confidence_lower = predicted_threats - 3
            
            fig = go.Figure()
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=times + times[::-1],
                y=confidence_upper.tolist() + confidence_lower.tolist()[::-1],
                fill='toself',
                fillcolor='rgba(31, 119, 180, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval',
                showlegend=True
            ))
            
            # Add prediction line
            fig.add_trace(go.Scatter(
                x=times,
                y=predicted_threats,
                mode='lines+markers',
                name='Predicted Threats',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.update_layout(
                title='24-Hour Threat Prediction (Consciousness-Enhanced)',
                xaxis_title='Time',
                yaxis_title='Predicted Threat Count',
                template='plotly_dark',
                height=400
            )
            
            self.dashboard_data['visualizations']['threat_prediction_line'] = fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error generating threat prediction chart: {e}")
    
    async def _websocket_broadcaster(self):
        """Broadcast real-time updates to WebSocket clients"""
        while True:
            try:
                if self.websocket_connections:
                    update_data = {
                        'type': 'threat_intelligence_update',
                        'data': {
                            'threat_feeds': self.dashboard_data['threat_feeds'],
                            'global_intelligence': self.dashboard_data['global_intelligence'],
                            'real_time_threats': self.dashboard_data['threat_feeds']['real_time_threats'][:10]
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
        connections = list(self.websocket_connections)
        
        for ws in connections:
            try:
                await ws.send_str(message)
            except Exception as e:
                self.logger.debug(f"Failed to send to WebSocket: {e}")
    
    # Route handlers
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
            
            if not username_result.is_valid or not password_result.is_valid:
                return web.json_response({'error': 'Invalid credentials'}, status=400)
            
            # Authenticate user
            auth_result = self.jwt_manager.authenticate_user(
                username_result.sanitized_value,
                password_result.sanitized_value
            )
            
            if auth_result.success:
                return web.json_response({
                    'success': True,
                    'access_token': auth_result.access_token,
                    'user': {
                        'user_id': auth_result.user_id,
                        'username': auth_result.username,
                        'roles': auth_result.roles
                    }
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': 'Authentication failed'
                }, status=401)
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return web.json_response({'error': 'Login failed'}, status=500)
    
    async def api_logout(self, request):
        """API logout endpoint"""
        return web.json_response({'success': True})
    
    # Dashboard page handlers
    async def main_dashboard(self, request):
        """Main threat intelligence dashboard"""
        template = self.jinja_env.get_template('main_dashboard.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                dashboard_data=self.dashboard_data
            ),
            content_type='text/html'
        )
    
    async def threat_feeds_dashboard(self, request):
        """Threat feeds dashboard"""
        template = self.jinja_env.get_template('threat_feeds.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                feeds_data=self.dashboard_data['threat_feeds']
            ),
            content_type='text/html'
        )
    
    async def global_intelligence_dashboard(self, request):
        """Global intelligence dashboard"""
        template = self.jinja_env.get_template('global_intelligence.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                intelligence_data=self.dashboard_data['global_intelligence']
            ),
            content_type='text/html'
        )
    
    async def threat_correlations_dashboard(self, request):
        """Threat correlations dashboard"""
        template = self.jinja_env.get_template('threat_correlations.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                correlations_data=self.dashboard_data
            ),
            content_type='text/html'
        )
    
    async def threat_hunting_dashboard(self, request):
        """Threat hunting dashboard"""
        template = self.jinja_env.get_template('threat_hunting.html')
        return web.Response(
            text=template.render(
                user=request['user']
            ),
            content_type='text/html'
        )
    
    async def threat_analytics_dashboard(self, request):
        """Threat analytics dashboard"""
        template = self.jinja_env.get_template('threat_analytics.html')
        return web.Response(
            text=template.render(
                user=request['user'],
                visualizations=self.dashboard_data['visualizations']
            ),
            content_type='text/html'
        )
    
    # API handlers
    async def api_dashboard_overview(self, request):
        """API endpoint for dashboard overview"""
        return web.json_response({
            'status': 'success',
            'data': {
                'summary': {
                    'active_sources': self.dashboard_data['threat_feeds']['active_sources'],
                    'threats_processed': self.dashboard_data['threat_feeds']['items_processed'],
                    'correlations_found': self.dashboard_data['global_intelligence']['correlations_found'],
                    'predictions_generated': self.dashboard_data['global_intelligence']['predictions_generated'],
                    'quantum_threats': self.dashboard_data['global_intelligence']['quantum_threats'],
                    'consciousness_enhanced': self.dashboard_data['global_intelligence']['consciousness_enhanced']
                },
                'last_updated': self.dashboard_data['last_updated'].isoformat() if self.dashboard_data['last_updated'] else None
            }
        })
    
    async def api_threat_feeds_status(self, request):
        """API endpoint for threat feeds status"""
        return web.json_response({
            'status': 'success',
            'data': self.dashboard_data['threat_feeds']
        })
    
    async def api_threat_feed_sources(self, request):
        """API endpoint for threat feed sources"""
        if self.realtime_aggregator:
            status = self.realtime_aggregator.get_aggregation_status()
            return web.json_response({
                'status': 'success',
                'data': status.get('source_status', {})
            })
        else:
            return web.json_response({
                'status': 'error',
                'error': 'Threat aggregator not available'
            }, status=503)
    
    async def api_real_time_threats(self, request):
        """API endpoint for real-time threats"""
        return web.json_response({
            'status': 'success',
            'data': self.dashboard_data['threat_feeds']['real_time_threats']
        })
    
    async def api_global_intelligence_status(self, request):
        """API endpoint for global intelligence status"""
        return web.json_response({
            'status': 'success',
            'data': self.dashboard_data['global_intelligence']
        })
    
    async def api_threat_correlations(self, request):
        """API endpoint for threat correlations"""
        # Mock correlation data
        correlations = [
            {
                'correlation_id': 'corr_001',
                'threat_indicators': ['192.168.1.100', 'malicious-domain.com'],
                'correlation_level': 'strong',
                'confidence_score': 0.92,
                'attack_campaign': 'APT_Campaign_Alpha',
                'consciousness_verified': True
            },
            {
                'correlation_id': 'corr_002',
                'threat_indicators': ['malware_hash_123', '10.0.0.50'],
                'correlation_level': 'moderate',
                'confidence_score': 0.78,
                'attack_campaign': 'Phishing_Campaign_Beta',
                'consciousness_verified': False
            }
        ]
        
        return web.json_response({
            'status': 'success',
            'data': correlations
        })
    
    async def api_threat_predictions(self, request):
        """API endpoint for threat predictions"""
        # Mock prediction data
        predictions = [
            {
                'prediction_id': 'pred_001',
                'threat_type': 'advanced_persistent_threat',
                'probability': 0.23,
                'time_horizon_hours': 72,
                'confidence': 0.87,
                'consciousness_enhanced': True
            },
            {
                'prediction_id': 'pred_002',
                'threat_type': 'insider_threat',
                'probability': 0.15,
                'time_horizon_hours': 168,
                'confidence': 0.65,
                'consciousness_enhanced': True
            }
        ]
        
        return web.json_response({
            'status': 'success',
            'data': predictions
        })
    
    async def api_visualizations(self, request):
        """API endpoint for analytics visualizations"""
        return web.json_response({
            'status': 'success',
            'data': self.dashboard_data['visualizations']
        })
    
    async def api_threat_hunt_search(self, request):
        """API endpoint for threat hunting search"""
        try:
            data = await request.json()
            query = data.get('query', '')
            
            # Validate query
            query_rule = ValidationRule(InputType.STRING, required=True, max_length=500)
            query_result = self.input_validator.validate_input(query, query_rule)
            
            if not query_result.is_valid:
                return web.json_response({'error': query_result.error_message}, status=400)
            
            # Mock search results
            search_results = [
                {
                    'result_id': 'hunt_result_001',
                    'indicator': '192.168.1.100',
                    'indicator_type': 'ip',
                    'threat_type': 'malware_c2',
                    'first_seen': (datetime.utcnow() - timedelta(hours=24)).isoformat(),
                    'last_seen': datetime.utcnow().isoformat(),
                    'sources': ['source_1', 'source_3'],
                    'confidence': 0.89,
                    'consciousness_score': 0.92
                },
                {
                    'result_id': 'hunt_result_002',
                    'indicator': 'malicious-domain.com',
                    'indicator_type': 'domain',
                    'threat_type': 'phishing',
                    'first_seen': (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                    'last_seen': datetime.utcnow().isoformat(),
                    'sources': ['source_2'],
                    'confidence': 0.76,
                    'consciousness_score': 0.88
                }
            ]
            
            # Log threat hunting activity
            self.audit_logger.log_security_event(
                SecurityEventType.API_ACCESS,
                SecurityLevel.MEDIUM,
                user_id=request['user']['user_id'],
                ip_address=request.remote,
                resource='/api/hunting/search',
                action='threat_hunt_search',
                details={'query': query_result.sanitized_value}
            )
            
            return web.json_response({
                'status': 'success',
                'query': query_result.sanitized_value,
                'results': search_results,
                'result_count': len(search_results)
            })
            
        except Exception as e:
            self.logger.error(f"Threat hunt search error: {e}")
            return web.json_response({'error': 'Search failed'}, status=500)
    
    async def api_assess_threat(self, request):
        """API endpoint for threat assessment"""
        try:
            data = await request.json()
            threat_data = data.get('threat_data', {})
            
            if self.global_threat_orchestrator:
                # Process threat through global intelligence
                results = await self.global_threat_orchestrator.process_global_threat_intelligence(
                    threat_data, "synos_global_coordinator_001"
                )
                
                return web.json_response({
                    'status': 'success',
                    'assessment': results
                })
            else:
                return web.json_response({
                    'status': 'error',
                    'error': 'Global threat orchestrator not available'
                }, status=503)
                
        except Exception as e:
            self.logger.error(f"Threat assessment error: {e}")
            return web.json_response({'error': 'Assessment failed'}, status=500)
    
    # WebSocket handler
    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.add(ws)
        
        try:
            # Send initial data
            initial_data = {
                'type': 'initial_threat_intelligence_data',
                'data': self.dashboard_data,
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
            'service': 'threat_intelligence_dashboard',
            'components': {
                'global_threat_orchestrator': 'active' if self.global_threat_orchestrator else 'inactive',
                'realtime_aggregator': 'active' if self.realtime_aggregator else 'inactive',
                'websocket_connections': len(self.websocket_connections)
            },
            'data_freshness': {
                'last_updated': self.dashboard_data['last_updated'].isoformat() if self.dashboard_data['last_updated'] else None
            }
        })


async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    dashboard = ThreatIntelligenceDashboard()
    await dashboard.start()


if __name__ == "__main__":
    asyncio.run(main())