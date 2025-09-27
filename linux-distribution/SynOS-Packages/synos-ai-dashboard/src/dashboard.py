#!/usr/bin/env python3
"""
SynOS AI Dashboard Web Interface
Real-time consciousness monitoring and AI framework management

Features:
- Live consciousness state visualization
- Neural activity monitoring
- System integration status
- Security event dashboard
- Learning progress tracking
- AI service management
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from flask import Flask, render_template, jsonify, request, websocket
    from flask_socketio import SocketIO, emit
    import plotly.graph_objs as go
    import plotly.utils
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    SocketIO = None

# Import our NATS integration
import sys
sys.path.append('/usr/lib/synos')
from nats_integration import ConsciousnessMessageBus

logger = logging.getLogger(__name__)

class AIMetricsCollector:
    """Collects and aggregates AI metrics for dashboard display"""

    def __init__(self):
        self.consciousness_history = []
        self.neural_activity_history = []
        self.learning_events = []
        self.security_events = []
        self.system_metrics = []
        self.max_history_points = 1000

    def add_consciousness_state(self, state: Dict[str, Any]):
        """Add consciousness state data point"""
        timestamp = datetime.now()
        data_point = {
            'timestamp': timestamp.isoformat(),
            'awareness_level': state.get('awareness_level', 0.0),
            'neural_activity': state.get('neural_activity', 0.0),
            'learning_rate': state.get('learning_rate', 0.0),
            'system_integration': state.get('system_integration', 0.0),
            'active_patterns': state.get('active_patterns', [])
        }

        self.consciousness_history.append(data_point)
        self._trim_history(self.consciousness_history)

    def add_neural_activity(self, activity: Dict[str, Any]):
        """Add neural activity data point"""
        timestamp = datetime.now()
        data_point = {
            'timestamp': timestamp.isoformat(),
            'total_groups': activity.get('total_groups', 0),
            'active_groups': activity.get('active_groups', 0),
            'competition_score': activity.get('competition_score', 0.0),
            'adaptation_rate': activity.get('adaptation_rate', 0.0)
        }

        self.neural_activity_history.append(data_point)
        self._trim_history(self.neural_activity_history)

    def add_learning_event(self, event: Dict[str, Any]):
        """Add learning event"""
        timestamp = datetime.now()
        event_data = {
            'timestamp': timestamp.isoformat(),
            'pattern_id': event.get('pattern_id', 'unknown'),
            'success_rate': event.get('success_rate', 0.0),
            'context': event.get('context', {})
        }

        self.learning_events.append(event_data)
        self._trim_history(self.learning_events)

    def add_security_event(self, event: Dict[str, Any]):
        """Add security event"""
        timestamp = datetime.now()
        event_data = {
            'timestamp': timestamp.isoformat(),
            'event_type': event.get('event_type', 'unknown'),
            'severity': event.get('severity', 'info'),
            'description': event.get('description', ''),
            'ai_response': event.get('ai_response', 'none')
        }

        self.security_events.append(event_data)
        self._trim_history(self.security_events)

    def _trim_history(self, history_list: List[Dict]):
        """Trim history to maximum points"""
        if len(history_list) > self.max_history_points:
            history_list[:] = history_list[-self.max_history_points:]

    def get_recent_consciousness_data(self, minutes: int = 60) -> List[Dict]:
        """Get recent consciousness data points"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            point for point in self.consciousness_history
            if datetime.fromisoformat(point['timestamp']) > cutoff
        ]

    def get_neural_activity_summary(self) -> Dict[str, Any]:
        """Get neural activity summary"""
        if not self.neural_activity_history:
            return {}

        recent_activity = self.neural_activity_history[-10:]  # Last 10 points
        return {
            'current_active_groups': recent_activity[-1].get('active_groups', 0) if recent_activity else 0,
            'avg_competition_score': sum(p.get('competition_score', 0) for p in recent_activity) / len(recent_activity) if recent_activity else 0,
            'adaptation_trend': self._calculate_trend([p.get('adaptation_rate', 0) for p in recent_activity])
        }

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get learning progress summary"""
        if not self.learning_events:
            return {}

        recent_events = self.learning_events[-50:]  # Last 50 events
        success_rates = [e.get('success_rate', 0) for e in recent_events]

        return {
            'total_patterns_learned': len(set(e.get('pattern_id') for e in self.learning_events)),
            'avg_success_rate': sum(success_rates) / len(success_rates) if success_rates else 0,
            'learning_trend': self._calculate_trend(success_rates),
            'recent_patterns': list(set(e.get('pattern_id') for e in recent_events[-10:]))
        }

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security events summary"""
        if not self.security_events:
            return {}

        recent_events = self.security_events[-100:]  # Last 100 events
        severity_counts = {}
        for event in recent_events:
            severity = event.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            'total_events': len(recent_events),
            'severity_distribution': severity_counts,
            'ai_responses': len([e for e in recent_events if e.get('ai_response') != 'none']),
            'recent_events': recent_events[-5:]  # Last 5 events
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"

        recent_avg = sum(values[-3:]) / len(values[-3:]) if len(values) >= 3 else values[-1]
        older_avg = sum(values[:-3]) / len(values[:-3]) if len(values) > 3 else values[0]

        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"

class SynOSAIDashboard:
    """Main dashboard application class"""

    def __init__(self, host: str = "localhost", port: int = 8080):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask and required dependencies not available")

        self.app = Flask(__name__, template_folder='/usr/share/synos/dashboard/templates',
                        static_folder='/usr/share/synos/dashboard/static')
        self.app.config['SECRET_KEY'] = 'synos-ai-dashboard-secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        self.host = host
        self.port = port
        self.metrics_collector = AIMetricsCollector()
        self.message_bus = None

        self._setup_routes()
        self._setup_websocket_handlers()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')

        @self.app.route('/api/consciousness/current')
        def get_current_consciousness():
            """Get current consciousness state"""
            recent_data = self.metrics_collector.get_recent_consciousness_data(minutes=1)
            if recent_data:
                return jsonify(recent_data[-1])
            return jsonify({})

        @self.app.route('/api/consciousness/history')
        def get_consciousness_history():
            """Get consciousness history"""
            minutes = int(request.args.get('minutes', 60))
            data = self.metrics_collector.get_recent_consciousness_data(minutes)
            return jsonify(data)

        @self.app.route('/api/neural/summary')
        def get_neural_summary():
            """Get neural activity summary"""
            return jsonify(self.metrics_collector.get_neural_activity_summary())

        @self.app.route('/api/learning/summary')
        def get_learning_summary():
            """Get learning progress summary"""
            return jsonify(self.metrics_collector.get_learning_summary())

        @self.app.route('/api/security/summary')
        def get_security_summary():
            """Get security events summary"""
            return jsonify(self.metrics_collector.get_security_summary())

        @self.app.route('/api/consciousness/chart')
        def get_consciousness_chart():
            """Get consciousness data formatted for charts"""
            data = self.metrics_collector.get_recent_consciousness_data(minutes=60)

            if not data:
                return jsonify({})

            timestamps = [point['timestamp'] for point in data]
            awareness = [point['awareness_level'] for point in data]
            neural_activity = [point['neural_activity'] for point in data]
            learning_rate = [point['learning_rate'] for point in data]

            chart_data = {
                'timestamps': timestamps,
                'awareness_level': awareness,
                'neural_activity': neural_activity,
                'learning_rate': learning_rate
            }

            return jsonify(chart_data)

        @self.app.route('/api/system/status')
        def get_system_status():
            """Get overall system status"""
            consciousness_data = self.metrics_collector.get_recent_consciousness_data(minutes=5)
            neural_summary = self.metrics_collector.get_neural_activity_summary()
            learning_summary = self.metrics_collector.get_learning_summary()

            # Calculate overall health score
            health_score = 0.0
            if consciousness_data:
                latest = consciousness_data[-1]
                health_score = (
                    latest.get('awareness_level', 0) * 0.3 +
                    latest.get('neural_activity', 0) * 0.3 +
                    latest.get('learning_rate', 0) * 0.2 +
                    latest.get('system_integration', 0) * 0.2
                )

            status = {
                'health_score': health_score,
                'consciousness_active': len(consciousness_data) > 0,
                'neural_groups_active': neural_summary.get('current_active_groups', 0),
                'patterns_learned': learning_summary.get('total_patterns_learned', 0),
                'last_update': consciousness_data[-1]['timestamp'] if consciousness_data else None
            }

            return jsonify(status)

    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""

        @self.socketio.on('connect')
        def handle_connect():
            logger.info("Dashboard client connected")
            emit('status', {'message': 'Connected to SynOS AI Dashboard'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("Dashboard client disconnected")

        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle client request for data update"""
            self._broadcast_current_data()

    def _broadcast_current_data(self):
        """Broadcast current data to all connected clients"""
        try:
            # Get latest data
            consciousness_data = self.metrics_collector.get_recent_consciousness_data(minutes=1)
            neural_summary = self.metrics_collector.get_neural_activity_summary()
            learning_summary = self.metrics_collector.get_learning_summary()
            security_summary = self.metrics_collector.get_security_summary()

            # Prepare data for broadcast
            broadcast_data = {
                'consciousness': consciousness_data[-1] if consciousness_data else {},
                'neural': neural_summary,
                'learning': learning_summary,
                'security': security_summary,
                'timestamp': datetime.now().isoformat()
            }

            self.socketio.emit('data_update', broadcast_data)

        except Exception as e:
            logger.error(f"Failed to broadcast data: {e}")

    async def _message_bus_handler(self, message_data: Dict[str, Any]):
        """Handle incoming messages from NATS bus"""
        try:
            message_type = message_data.get('type', 'unknown')

            if message_type == 'consciousness_state':
                self.metrics_collector.add_consciousness_state(message_data.get('state', {}))
            elif message_type == 'neural_activity':
                self.metrics_collector.add_neural_activity(message_data.get('activity', {}))
            elif message_type == 'learning_event':
                self.metrics_collector.add_learning_event(message_data.get('event', {}))
            elif message_type == 'security_event':
                self.metrics_collector.add_security_event(message_data.get('event', {}))

            # Broadcast update to connected clients
            self._broadcast_current_data()

        except Exception as e:
            logger.error(f"Error handling message bus data: {e}")

    async def start_message_bus(self):
        """Start the NATS message bus connection"""
        try:
            self.message_bus = ConsciousnessMessageBus()
            if await self.message_bus.start():
                # Subscribe to relevant topics
                await self.message_bus.register_consciousness_observer(self._message_bus_handler)
                await self.message_bus.register_security_responder(self._message_bus_handler)
                logger.info("Dashboard connected to NATS message bus")
            else:
                logger.warning("Failed to connect to NATS message bus")
        except Exception as e:
            logger.error(f"Error starting message bus: {e}")

    def run(self, debug: bool = False):
        """Run the dashboard web application"""
        logger.info(f"Starting SynOS AI Dashboard on {self.host}:{self.port}")

        # Start message bus in background
        if self.message_bus:
            try:
                asyncio.create_task(self.start_message_bus())
            except Exception as e:
                logger.error(f"Failed to start message bus: {e}")

        # Run Flask application
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

# Generate sample dashboard HTML template
DASHBOARD_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SynOS AI Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #e0e0e0;
            font-family: 'Liberation Sans', sans-serif;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #00ffff;
            font-size: 2.5rem;
            margin: 0;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid #00ffff44;
            border-radius: 10px;
            padding: 20px;
        }
        .status-card h3 {
            color: #00ffff;
            margin-top: 0;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }
        .metric-value {
            font-weight: bold;
            color: #ffffff;
        }
        .chart-container {
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid #00ffff44;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .health-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .health-good { background-color: #00ff00; }
        .health-warning { background-color: #ffff00; }
        .health-critical { background-color: #ff0000; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 SynOS AI Consciousness Dashboard</h1>
        <p>Neural Darwinism • Real-time AI Monitoring • System Integration</p>
    </div>

    <div class="status-grid">
        <div class="status-card">
            <h3>🧠 Consciousness State</h3>
            <div class="metric">
                <span>Awareness Level:</span>
                <span class="metric-value" id="awareness-level">--</span>
            </div>
            <div class="metric">
                <span>Neural Activity:</span>
                <span class="metric-value" id="neural-activity">--</span>
            </div>
            <div class="metric">
                <span>Learning Rate:</span>
                <span class="metric-value" id="learning-rate">--</span>
            </div>
            <div class="metric">
                <span>System Integration:</span>
                <span class="metric-value" id="system-integration">--</span>
            </div>
        </div>

        <div class="status-card">
            <h3>🔬 Neural Darwinism</h3>
            <div class="metric">
                <span>Active Groups:</span>
                <span class="metric-value" id="active-groups">--</span>
            </div>
            <div class="metric">
                <span>Competition Score:</span>
                <span class="metric-value" id="competition-score">--</span>
            </div>
            <div class="metric">
                <span>Adaptation Trend:</span>
                <span class="metric-value" id="adaptation-trend">--</span>
            </div>
        </div>

        <div class="status-card">
            <h3>📚 Learning Progress</h3>
            <div class="metric">
                <span>Patterns Learned:</span>
                <span class="metric-value" id="patterns-learned">--</span>
            </div>
            <div class="metric">
                <span>Success Rate:</span>
                <span class="metric-value" id="success-rate">--</span>
            </div>
            <div class="metric">
                <span>Learning Trend:</span>
                <span class="metric-value" id="learning-trend">--</span>
            </div>
        </div>

        <div class="status-card">
            <h3>🛡️ Security Status</h3>
            <div class="metric">
                <span>Recent Events:</span>
                <span class="metric-value" id="security-events">--</span>
            </div>
            <div class="metric">
                <span>AI Responses:</span>
                <span class="metric-value" id="ai-responses">--</span>
            </div>
            <div class="metric">
                <span>System Health:</span>
                <span id="system-health">
                    <span class="health-indicator health-good"></span>
                    <span class="metric-value">Operational</span>
                </span>
            </div>
        </div>
    </div>

    <div class="chart-container">
        <h3>Consciousness Activity (Last Hour)</h3>
        <div id="consciousness-chart" style="height: 400px;"></div>
    </div>

    <script>
        // WebSocket connection
        const socket = io();

        socket.on('connect', function() {
            console.log('Connected to SynOS AI Dashboard');
            socket.emit('request_update');
        });

        socket.on('data_update', function(data) {
            updateDashboard(data);
        });

        function updateDashboard(data) {
            // Update consciousness metrics
            if (data.consciousness) {
                document.getElementById('awareness-level').textContent =
                    (data.consciousness.awareness_level * 100).toFixed(1) + '%';
                document.getElementById('neural-activity').textContent =
                    (data.consciousness.neural_activity * 100).toFixed(1) + '%';
                document.getElementById('learning-rate').textContent =
                    (data.consciousness.learning_rate * 100).toFixed(1) + '%';
                document.getElementById('system-integration').textContent =
                    (data.consciousness.system_integration * 100).toFixed(1) + '%';
            }

            // Update neural darwinism metrics
            if (data.neural) {
                document.getElementById('active-groups').textContent =
                    data.neural.current_active_groups || 0;
                document.getElementById('competition-score').textContent =
                    ((data.neural.avg_competition_score || 0) * 100).toFixed(1) + '%';
                document.getElementById('adaptation-trend').textContent =
                    data.neural.adaptation_trend || 'stable';
            }

            // Update learning metrics
            if (data.learning) {
                document.getElementById('patterns-learned').textContent =
                    data.learning.total_patterns_learned || 0;
                document.getElementById('success-rate').textContent =
                    ((data.learning.avg_success_rate || 0) * 100).toFixed(1) + '%';
                document.getElementById('learning-trend').textContent =
                    data.learning.learning_trend || 'stable';
            }

            // Update security metrics
            if (data.security) {
                document.getElementById('security-events').textContent =
                    data.security.total_events || 0;
                document.getElementById('ai-responses').textContent =
                    data.security.ai_responses || 0;
            }
        }

        // Request updates every 5 seconds
        setInterval(function() {
            socket.emit('request_update');
        }, 5000);

        // Initialize chart
        const layout = {
            title: '',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#e0e0e0' },
            xaxis: { color: '#e0e0e0', gridcolor: '#444' },
            yaxis: { color: '#e0e0e0', gridcolor: '#444', range: [0, 1] }
        };

        Plotly.newPlot('consciousness-chart', [], layout);

        // Update chart with consciousness data
        function updateChart() {
            fetch('/api/consciousness/chart')
                .then(response => response.json())
                .then(data => {
                    if (data.timestamps) {
                        const traces = [
                            {
                                x: data.timestamps,
                                y: data.awareness_level,
                                name: 'Awareness',
                                line: { color: '#00ffff' }
                            },
                            {
                                x: data.timestamps,
                                y: data.neural_activity,
                                name: 'Neural Activity',
                                line: { color: '#ff6600' }
                            },
                            {
                                x: data.timestamps,
                                y: data.learning_rate,
                                name: 'Learning Rate',
                                line: { color: '#00ff00' }
                            }
                        ];

                        Plotly.newPlot('consciousness-chart', traces, layout);
                    }
                });
        }

        // Update chart every 10 seconds
        setInterval(updateChart, 10000);
        updateChart(); // Initial load
    </script>
</body>
</html>
'''

def main():
    """Main entry point for dashboard"""
    if not FLASK_AVAILABLE:
        print("ERROR: Flask and required dependencies not installed")
        print("Install with: pip3 install flask flask-socketio plotly")
        return 1

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] Dashboard: %(message)s'
    )

    # Create dashboard application
    dashboard = SynOSAIDashboard(host="0.0.0.0", port=8080)

    try:
        dashboard.run(debug=False)
    except KeyboardInterrupt:
        logger.info("Dashboard shutdown requested")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())