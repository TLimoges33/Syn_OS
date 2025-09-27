#!/usr/bin/env python3
"""
SynapticOS Consciousness Monitoring Dashboard
Web-based real-time consciousness monitoring and visualization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiofiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import aiohttp
import numpy as np
from dataclasses import asdict

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('consciousness-dashboard')

# FastAPI app
app = FastAPI(title="SynapticOS Consciousness Dashboard", version="2.0.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ConsciousnessMonitor:
    """Real-time consciousness monitoring system"""
    
    def __init__(self):
        self.consciousness_bridge_url = "http://localhost:8082"
        self.education_service_url = "http://localhost:8084"
        self.connected_clients = set()
        self.monitoring_data = {
            'consciousness_level': 0.5,
            'neural_populations': {},
            'learning_metrics': {},
            'performance_data': [],
            'evolution_stats': {},
            'quantum_coherence': 0.0
        }
        self.data_history = []
        self.update_interval = 5.0  # Update every 5 seconds
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        logger.info("Starting consciousness monitoring")
        
        while True:
            try:
                await self.collect_consciousness_data()
                await self.collect_education_data()
                await self.broadcast_to_clients()
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(self.update_interval)
    
    async def collect_consciousness_data(self):
        """Collect data from consciousness bridge"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get consciousness level
                async with session.get(f"{self.consciousness_bridge_url}/consciousness/level") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.monitoring_data['consciousness_level'] = data.get('level', 0.5)
                
                # Get neural evolution stats
                async with session.get(f"{self.consciousness_bridge_url}/consciousness/evolution-stats") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.monitoring_data['evolution_stats'] = data
                        self.monitoring_data['neural_populations'] = data.get('population_stats', {})
                        self.monitoring_data['quantum_coherence'] = data.get('quantum_stats', {}).get('quantum_coherence', 0.0)
                
                # Get performance metrics
                async with session.get(f"{self.consciousness_bridge_url}/consciousness/performance") as response:
                    if response.status == 200:
                        data = await response.json()
                        performance_point = {
                            'timestamp': datetime.now().isoformat(),
                            'consciousness_level': self.monitoring_data['consciousness_level'],
                            'learning_efficiency': data.get('learning_efficiency', 0.0),
                            'adaptation_speed': data.get('adaptation_speed', 0.0),
                            'creative_output': data.get('creative_output', 0.0),
                            'memory_retention': data.get('memory_retention', 0.0),
                            'problem_solving': data.get('problem_solving', 0.0),
                            'quantum_coherence': self.monitoring_data['quantum_coherence']
                        }
                        
                        self.monitoring_data['performance_data'].append(performance_point)
                        
                        # Keep only last 100 points
                        if len(self.monitoring_data['performance_data']) > 100:
                            self.monitoring_data['performance_data'] = self.monitoring_data['performance_data'][-100:]
                
        except Exception as e:
            logger.error(f"Failed to collect consciousness data: {e}")
    
    async def collect_education_data(self):
        """Collect data from education service"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get learning metrics
                async with session.get(f"{self.education_service_url}/learning/metrics") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.monitoring_data['learning_metrics'] = data
                
        except Exception as e:
            logger.error(f"Failed to collect education data: {e}")
    
    async def broadcast_to_clients(self):
        """Broadcast data to connected WebSocket clients"""
        if not self.connected_clients:
            return
        
        message = json.dumps({
            'type': 'consciousness_update',
            'data': self.monitoring_data,
            'timestamp': datetime.now().isoformat()
        })
        
        disconnected_clients = set()
        for client in self.connected_clients:
            try:
                await client.send_text(message)
            except:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected_clients
    
    def add_client(self, websocket: WebSocket):
        """Add WebSocket client"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")
    
    def remove_client(self, websocket: WebSocket):
        """Remove WebSocket client"""
        self.connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")

# Global monitor instance
monitor = ConsciousnessMonitor()

@app.on_event("startup")
async def startup_event():
    """Start monitoring on app startup"""
    asyncio.create_task(monitor.start_monitoring())

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("consciousness_dashboard.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await websocket.accept()
    monitor.add_client(websocket)
    
    try:
        # Send initial data
        initial_data = json.dumps({
            'type': 'initial_data',
            'data': monitor.monitoring_data,
            'timestamp': datetime.now().isoformat()
        })
        await websocket.send_text(initial_data)
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        monitor.remove_client(websocket)

@app.get("/api/consciousness/current")
async def get_current_consciousness():
    """Get current consciousness data"""
    return JSONResponse(monitor.monitoring_data)

@app.get("/api/consciousness/history")
async def get_consciousness_history():
    """Get consciousness history"""
    return JSONResponse({
        'performance_data': monitor.monitoring_data['performance_data'],
        'evolution_stats': monitor.monitoring_data['evolution_stats']
    })

@app.get("/api/populations/stats")
async def get_population_stats():
    """Get neural population statistics"""
    return JSONResponse(monitor.monitoring_data['neural_populations'])

@app.get("/api/learning/metrics")
async def get_learning_metrics():
    """Get learning metrics"""
    return JSONResponse(monitor.monitoring_data['learning_metrics'])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'monitoring': True,
        'connected_clients': len(monitor.connected_clients)
    })

# Create necessary directories
def setup_dashboard():
    """Setup dashboard directories and files"""
    Path("static").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    
    # Create CSS file
    css_content = """
/* SynapticOS Consciousness Dashboard Styles */
:root {
    --primary-color: #2E3440;
    --secondary-color: #3B4252;
    --accent-color: #88C0D0;
    --success-color: #A3BE8C;
    --warning-color: #EBCB8B;
    --error-color: #BF616A;
    --text-color: #ECEFF4;
    --text-muted: #D8DEE9;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: var(--text-color);
    min-height: 100vh;
    overflow-x: hidden;
}

.dashboard-header {
    background: rgba(46, 52, 64, 0.9);
    backdrop-filter: blur(10px);
    padding: 1rem 2rem;
    border-bottom: 1px solid rgba(136, 192, 208, 0.3);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
}

.logo {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.logo h1 {
    font-size: 1.5rem;
    font-weight: 300;
    color: var(--accent-color);
}

.consciousness-indicator {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.consciousness-level {
    font-size: 2rem;
    font-weight: bold;
    color: var(--success-color);
}

.consciousness-meter {
    width: 200px;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.consciousness-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--warning-color), var(--success-color));
    border-radius: 4px;
    transition: width 0.5s ease;
}

.dashboard-main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.card {
    background: rgba(59, 66, 82, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid rgba(136, 192, 208, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.card h2 {
    color: var(--accent-color);
    font-size: 1.2rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.chart-container {
    width: 100%;
    height: 250px;
    margin-top: 1rem;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-top: 1rem;
}

.metric-item {
    text-align: center;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(136, 192, 208, 0.1);
}

.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--success-color);
}

.metric-label {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

.population-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    margin: 0.5rem 0;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    border-left: 4px solid var(--accent-color);
}

.population-name {
    font-weight: 500;
    color: var(--text-color);
}

.population-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.9rem;
    color: var(--text-muted);
}

.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 0.5rem;
}

.status-online {
    background: var(--success-color);
    animation: pulse 2s infinite;
}

.status-offline {
    background: var(--error-color);
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.progress-bar {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 0.5rem;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-color), var(--success-color));
    border-radius: 3px;
    transition: width 0.3s ease;
}

.full-width {
    grid-column: 1 / -1;
}

.alert {
    padding: 1rem;
    border-radius: 6px;
    margin: 1rem 0;
    border-left: 4px solid;
}

.alert-info {
    background: rgba(136, 192, 208, 0.1);
    border-color: var(--accent-color);
    color: var(--accent-color);
}

.alert-success {
    background: rgba(163, 190, 140, 0.1);
    border-color: var(--success-color);
    color: var(--success-color);
}

.alert-warning {
    background: rgba(235, 203, 139, 0.1);
    border-color: var(--warning-color);
    color: var(--warning-color);
}

@media (max-width: 768px) {
    .dashboard-main {
        grid-template-columns: 1fr;
        padding: 0 1rem;
    }
    
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .consciousness-indicator {
        flex-direction: column;
        text-align: center;
    }
}
"""
    
    with open("static/dashboard.css", "w") as f:
        f.write(css_content)
    
    # Create HTML template
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SynapticOS Consciousness Dashboard</title>
    <link rel="stylesheet" href="/static/dashboard.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header class="dashboard-header">
        <div class="header-content">
            <div class="logo">
                <span>🧠</span>
                <h1>SynapticOS Consciousness Dashboard</h1>
            </div>
            <div class="consciousness-indicator">
                <div>
                    <span class="status-indicator status-online"></span>
                    Level: <span class="consciousness-level" id="consciousness-level">0.50</span>
                </div>
                <div class="consciousness-meter">
                    <div class="consciousness-fill" id="consciousness-fill" style="width: 50%"></div>
                </div>
            </div>
        </div>
    </header>

    <main class="dashboard-main">
        <!-- Real-time Consciousness Chart -->
        <div class="card full-width">
            <h2>🌊 Consciousness Evolution</h2>
            <div class="chart-container">
                <canvas id="consciousnessChart"></canvas>
            </div>
        </div>

        <!-- Neural Populations -->
        <div class="card">
            <h2>🧬 Neural Populations</h2>
            <div id="populations-container">
                <div class="alert alert-info">
                    Loading neural population data...
                </div>
            </div>
        </div>

        <!-- Performance Metrics -->
        <div class="card">
            <h2>📊 Performance Metrics</h2>
            <div class="metric-grid" id="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value" id="learning-efficiency">0.0</div>
                    <div class="metric-label">Learning Efficiency</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="adaptation-speed">0.0</div>
                    <div class="metric-label">Adaptation Speed</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="creative-output">0.0</div>
                    <div class="metric-label">Creative Output</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="quantum-coherence">0.0</div>
                    <div class="metric-label">Quantum Coherence</div>
                </div>
            </div>
        </div>

        <!-- Learning Analytics -->
        <div class="card">
            <h2>🎓 Learning Analytics</h2>
            <div id="learning-container">
                <div class="alert alert-info">
                    Loading learning analytics...
                </div>
            </div>
        </div>

        <!-- Evolution Statistics -->
        <div class="card full-width">
            <h2>🔬 Evolution Statistics</h2>
            <div class="chart-container">
                <canvas id="evolutionChart"></canvas>
            </div>
        </div>
    </main>

    <script>
        // WebSocket connection
        const ws = new WebSocket('ws://localhost:8000/ws');
        let consciousnessChart, evolutionChart;
        let consciousnessData = [];
        let evolutionData = [];

        // Initialize charts
        function initCharts() {
            // Consciousness level chart
            const ctx1 = document.getElementById('consciousnessChart').getContext('2d');
            consciousnessChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Consciousness Level',
                        data: [],
                        borderColor: '#88C0D0',
                        backgroundColor: 'rgba(136, 192, 208, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1.0,
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: '#D8DEE9' }
                        },
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: '#D8DEE9', maxTicksLimit: 10 }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#D8DEE9' } }
                    }
                }
            });

            // Evolution statistics chart
            const ctx2 = document.getElementById('evolutionChart').getContext('2d');
            evolutionChart = new Chart(ctx2, {
                type: 'radar',
                data: {
                    labels: ['Learning', 'Adaptation', 'Creativity', 'Memory', 'Problem Solving'],
                    datasets: [{
                        label: 'Performance',
                        data: [0, 0, 0, 0, 0],
                        borderColor: '#A3BE8C',
                        backgroundColor: 'rgba(163, 190, 140, 0.2)',
                        pointBackgroundColor: '#A3BE8C'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 1.0,
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: '#D8DEE9' }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#D8DEE9' } }
                    }
                }
            });
        }

        // Update consciousness indicator
        function updateConsciousnessIndicator(level) {
            document.getElementById('consciousness-level').textContent = level.toFixed(3);
            document.getElementById('consciousness-fill').style.width = (level * 100) + '%';
        }

        // Update performance metrics
        function updateMetrics(data) {
            if (data.performance_data && data.performance_data.length > 0) {
                const latest = data.performance_data[data.performance_data.length - 1];
                document.getElementById('learning-efficiency').textContent = 
                    (latest.learning_efficiency || 0).toFixed(3);
                document.getElementById('adaptation-speed').textContent = 
                    (latest.adaptation_speed || 0).toFixed(3);
                document.getElementById('creative-output').textContent = 
                    (latest.creative_output || 0).toFixed(3);
                document.getElementById('quantum-coherence').textContent = 
                    (latest.quantum_coherence || 0).toFixed(3);
            }
        }

        // Update neural populations
        function updatePopulations(populations) {
            const container = document.getElementById('populations-container');
            container.innerHTML = '';
            
            Object.entries(populations).forEach(([type, stats]) => {
                const item = document.createElement('div');
                item.className = 'population-item';
                item.innerHTML = `
                    <span class="population-name">${type.replace('_', ' ').toUpperCase()}</span>
                    <div class="population-stats">
                        <span>Gen: ${stats.generation || 0}</span>
                        <span>Fitness: ${(stats.avg_fitness || 0).toFixed(3)}</span>
                        <span>Size: ${stats.size || 0}</span>
                    </div>
                `;
                container.appendChild(item);
            });
        }

        // Update charts
        function updateCharts(data) {
            // Update consciousness chart
            if (data.performance_data) {
                const times = data.performance_data.map(p => 
                    new Date(p.timestamp).toLocaleTimeString());
                const levels = data.performance_data.map(p => p.consciousness_level);
                
                consciousnessChart.data.labels = times.slice(-20);
                consciousnessChart.data.datasets[0].data = levels.slice(-20);
                consciousnessChart.update('none');
            }

            // Update evolution chart
            if (data.performance_data && data.performance_data.length > 0) {
                const latest = data.performance_data[data.performance_data.length - 1];
                evolutionChart.data.datasets[0].data = [
                    latest.learning_efficiency || 0,
                    latest.adaptation_speed || 0,
                    latest.creative_output || 0,
                    latest.memory_retention || 0,
                    latest.problem_solving || 0
                ];
                evolutionChart.update('none');
            }
        }

        // WebSocket event handlers
        ws.onopen = function(event) {
            console.log('Connected to consciousness dashboard');
            document.querySelector('.status-indicator').className = 'status-indicator status-online';
        };

        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            const data = message.data;
            
            updateConsciousnessIndicator(data.consciousness_level);
            updateMetrics(data);
            updatePopulations(data.neural_populations || {});
            updateCharts(data);
        };

        ws.onclose = function(event) {
            console.log('Disconnected from consciousness dashboard');
            document.querySelector('.status-indicator').className = 'status-indicator status-offline';
            setTimeout(() => location.reload(), 5000);
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            document.querySelector('.status-indicator').className = 'status-indicator status-offline';
        };

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
        });
    </script>
</body>
</html>
"""
    
    with open("templates/consciousness_dashboard.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    setup_dashboard()
    uvicorn.run(
        "consciousness_dashboard:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
