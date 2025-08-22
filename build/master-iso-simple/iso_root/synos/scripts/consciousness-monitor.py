#!/usr/bin/env python3
"""
Syn_OS Consciousness Monitoring Service
Real-time consciousness level detection and learning analytics
"""

import asyncio
import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import websockets
import aiohttp
from aiohttp import web
import aiofiles
import numpy as np
from dataclasses import dataclass, asdict
import signal
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/synaptic-dev/consciousness-logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('consciousness-monitor')

@dataclass
class ConsciousnessReading:
    """Individual consciousness measurement"""
    timestamp: datetime
    user_id: str
    session_id: str
    consciousness_level: float
    cognitive_load: float
    attention_score: float
    learning_velocity: float
    context: str
    raw_metrics: Dict

@dataclass
class LearningSession:
    """Complete learning session analytics"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_readings: int
    avg_consciousness: float
    max_consciousness: float
    min_consciousness: float
    learning_progress: float
    breakthroughs: List[datetime]
    challenges_completed: int

class ConsciousnessDatabase:
    """SQLite database for consciousness data persistence"""
    
    def __init__(self, db_path: str = "/home/synaptic-dev/consciousness-logs/consciousness.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS consciousness_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    user_id TEXT,
                    session_id TEXT,
                    consciousness_level REAL,
                    cognitive_load REAL,
                    attention_score REAL,
                    learning_velocity REAL,
                    context TEXT,
                    raw_metrics TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time REAL,
                    end_time REAL,
                    total_readings INTEGER,
                    avg_consciousness REAL,
                    max_consciousness REAL,
                    min_consciousness REAL,
                    learning_progress REAL,
                    breakthroughs TEXT,
                    challenges_completed INTEGER
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_timestamp 
                ON consciousness_readings(user_id, timestamp)
            ''')
    
    async def store_reading(self, reading: ConsciousnessReading):
        """Store consciousness reading asynchronously"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO consciousness_readings 
                (timestamp, user_id, session_id, consciousness_level, cognitive_load,
                 attention_score, learning_velocity, context, raw_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reading.timestamp.timestamp(),
                reading.user_id,
                reading.session_id,
                reading.consciousness_level,
                reading.cognitive_load,
                reading.attention_score,
                reading.learning_velocity,
                reading.context,
                json.dumps(reading.raw_metrics)
            ))
    
    async def get_session_data(self, session_id: str) -> List[ConsciousnessReading]:
        """Retrieve all readings for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, user_id, session_id, consciousness_level,
                       cognitive_load, attention_score, learning_velocity,
                       context, raw_metrics
                FROM consciousness_readings 
                WHERE session_id = ?
                ORDER BY timestamp
            ''', (session_id,))
            
            readings = []
            for row in cursor.fetchall():
                readings.append(ConsciousnessReading(
                    timestamp=datetime.fromtimestamp(row[0]),
                    user_id=row[1],
                    session_id=row[2],
                    consciousness_level=row[3],
                    cognitive_load=row[4],
                    attention_score=row[5],
                    learning_velocity=row[6],
                    context=row[7],
                    raw_metrics=json.loads(row[8])
                ))
            
            return readings

class ConsciousnessAnalyzer:
    """Advanced consciousness analysis algorithms"""
    
    def __init__(self):
        self.baseline_readings: Dict[str, List[float]] = {}
        self.learning_patterns: Dict[str, List[Tuple[float, float]]] = {}
    
    def analyze_consciousness_level(self, metrics: Dict) -> float:
        """
        Analyze raw metrics to determine consciousness level
        
        Returns consciousness level between 0.0 and 1.0
        """
        try:
            # Simulate consciousness analysis based on multiple factors
            factors = {
                'response_time': metrics.get('response_time', 1000),
                'keystroke_dynamics': metrics.get('keystroke_patterns', []),
                'scroll_behavior': metrics.get('scroll_velocity', 0),
                'focus_duration': metrics.get('focus_time', 0),
                'task_switching': metrics.get('context_switches', 0),
                'error_rate': metrics.get('error_frequency', 0),
                'problem_solving_speed': metrics.get('solution_time', 0)
            }
            
            # Weighted consciousness calculation
            consciousness = 0.0
            
            # Response time factor (faster = higher consciousness)
            if factors['response_time'] < 500:
                consciousness += 0.2
            elif factors['response_time'] < 1000:
                consciousness += 0.15
            else:
                consciousness += 0.1
            
            # Focus duration (longer focus = higher consciousness)
            focus_score = min(factors['focus_duration'] / 60000, 1.0)  # Normalize to 1 minute
            consciousness += focus_score * 0.25
            
            # Error rate (lower = higher consciousness)
            error_score = max(0, 1.0 - factors['error_rate'] / 10)
            consciousness += error_score * 0.2
            
            # Task switching penalty (frequent switching = lower consciousness)
            switching_penalty = min(factors['task_switching'] / 5, 0.15)
            consciousness = max(0, consciousness - switching_penalty)
            
            # Keystroke dynamics analysis
            if factors['keystroke_dynamics']:
                rhythm_score = self._analyze_keystroke_rhythm(factors['keystroke_dynamics'])
                consciousness += rhythm_score * 0.15
            
            # Problem solving speed
            if factors['problem_solving_speed'] > 0:
                speed_score = max(0, 1.0 - factors['problem_solving_speed'] / 300000)  # 5 min baseline
                consciousness += speed_score * 0.2
            
            return min(1.0, consciousness)
            
        except Exception as e:
            logger.error(f"Error analyzing consciousness level: {e}")
            return 0.5  # Default fallback
    
    def _analyze_keystroke_rhythm(self, keystroke_data: List) -> float:
        """Analyze keystroke rhythm patterns for consciousness indicators"""
        if len(keystroke_data) < 5:
            return 0.1
        
        try:
            intervals = [keystroke_data[i+1] - keystroke_data[i] 
                        for i in range(len(keystroke_data)-1)]
            
            # Calculate rhythm consistency
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            # More consistent rhythm indicates higher consciousness
            consistency = max(0, 1.0 - (std_interval / mean_interval))
            return min(0.3, consistency * 0.3)
            
        except:
            return 0.1
    
    def detect_learning_breakthrough(self, readings: List[ConsciousnessReading]) -> bool:
        """Detect sudden consciousness/learning breakthroughs"""
        if len(readings) < 10:
            return False
        
        recent_levels = [r.consciousness_level for r in readings[-10:]]
        previous_levels = [r.consciousness_level for r in readings[-20:-10]]
        
        if len(previous_levels) < 10:
            return False
        
        recent_avg = np.mean(recent_levels)
        previous_avg = np.mean(previous_levels)
        
        # Breakthrough detected if recent average is significantly higher
        improvement = recent_avg - previous_avg
        return improvement > 0.15  # 15% improvement threshold

class ConsciousnessMonitor:
    """Main consciousness monitoring service"""
    
    def __init__(self):
        self.database = ConsciousnessDatabase()
        self.analyzer = ConsciousnessAnalyzer()
        self.active_sessions: Dict[str, List[ConsciousnessReading]] = {}
        self.websocket_connections: set = set()
        self.running = False
        
        # Create logs directory
        logs_dir = Path("/home/synaptic-dev/consciousness-logs")
        logs_dir.mkdir(exist_ok=True)
    
    async def start_monitoring(self):
        """Start the consciousness monitoring service"""
        self.running = True
        logger.info("🧠 Consciousness monitoring service started")
        
        # Start web server and WebSocket server concurrently
        await asyncio.gather(
            self.start_web_server(),
            self.start_websocket_server(),
            self.periodic_analysis()
        )
    
    async def start_web_server(self):
        """Start HTTP API server"""
        app = web.Application()
        
        # API routes
        app.router.add_post('/api/consciousness/reading', self.handle_consciousness_reading)
        app.router.add_get('/api/consciousness/session/{session_id}', self.handle_get_session)
        app.router.add_get('/api/consciousness/analysis/{user_id}', self.handle_get_analysis)
        app.router.add_get('/health', self.handle_health)
        
        # CORS middleware
        app.middlewares.append(self.cors_middleware)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 5000)
        await site.start()
        
        logger.info("🌐 Consciousness API server started on port 5000")
    
    async def start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        async def handle_websocket(websocket, path):
            self.websocket_connections.add(websocket)
            logger.info(f"🔗 New WebSocket connection: {websocket.remote_address}")
            
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_connections.discard(websocket)
                logger.info(f"🔗 WebSocket connection closed: {websocket.remote_address}")
        
        start_server = websockets.serve(handle_websocket, '0.0.0.0', 5001)
        await start_server
        
        logger.info("🔗 WebSocket server started on port 5001")
    
    async def handle_consciousness_reading(self, request):
        """Handle incoming consciousness reading data"""
        try:
            data = await request.json()
            
            # Analyze consciousness level
            consciousness_level = self.analyzer.analyze_consciousness_level(data.get('metrics', {}))
            
            # Create reading object
            reading = ConsciousnessReading(
                timestamp=datetime.now(),
                user_id=data.get('user_id', 'anonymous'),
                session_id=data.get('session_id', 'default'),
                consciousness_level=consciousness_level,
                cognitive_load=data.get('cognitive_load', 0.5),
                attention_score=data.get('attention_score', 0.5),
                learning_velocity=data.get('learning_velocity', 0.0),
                context=data.get('context', 'unknown'),
                raw_metrics=data.get('metrics', {})
            )
            
            # Store reading
            await self.database.store_reading(reading)
            
            # Add to active session
            session_id = reading.session_id
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = []
            self.active_sessions[session_id].append(reading)
            
            # Check for breakthrough
            breakthrough = self.analyzer.detect_learning_breakthrough(
                self.active_sessions[session_id]
            )
            
            # Broadcast to WebSocket clients
            await self.broadcast_reading(reading, breakthrough)
            
            return web.json_response({
                'status': 'success',
                'consciousness_level': consciousness_level,
                'breakthrough_detected': breakthrough,
                'timestamp': reading.timestamp.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing consciousness reading: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_get_session(self, request):
        """Get session consciousness data"""
        session_id = request.match_info['session_id']
        
        try:
            readings = await self.database.get_session_data(session_id)
            
            return web.json_response({
                'session_id': session_id,
                'readings': [asdict(reading) for reading in readings],
                'total_readings': len(readings)
            })
            
        except Exception as e:
            logger.error(f"Error retrieving session data: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_get_analysis(self, request):
        """Get user consciousness analysis"""
        user_id = request.match_info['user_id']
        
        try:
            # Get recent readings for analysis
            # This would be implemented with proper database queries
            analysis = {
                'user_id': user_id,
                'avg_consciousness': 0.7,
                'learning_trend': 'improving',
                'breakthroughs_today': 2,
                'focus_score': 0.8,
                'recommended_difficulty': 'intermediate'
            }
            
            return web.json_response(analysis)
            
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'consciousness-monitor',
            'timestamp': datetime.now().isoformat(),
            'active_sessions': len(self.active_sessions)
        })
    
    async def cors_middleware(self, request, handler):
        """CORS middleware for API requests"""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    async def broadcast_reading(self, reading: ConsciousnessReading, breakthrough: bool):
        """Broadcast consciousness reading to WebSocket clients"""
        if not self.websocket_connections:
            return
        
        message = {
            'type': 'consciousness_reading',
            'data': asdict(reading),
            'breakthrough': breakthrough,
            'timestamp': reading.timestamp.isoformat()
        }
        
        # Broadcast to all connected clients
        disconnected = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected
    
    async def periodic_analysis(self):
        """Periodic analysis and cleanup"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Cleanup old sessions
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, readings in self.active_sessions.items():
                    if readings and (current_time - readings[-1].timestamp) > timedelta(hours=1):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
                    logger.info(f"🧹 Cleaned up expired session: {session_id}")
                
            except Exception as e:
                logger.error(f"Error in periodic analysis: {e}")
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.running = False
        logger.info("🛑 Consciousness monitoring service stopped")

# Signal handlers for graceful shutdown
monitor = ConsciousnessMonitor()

def signal_handler(signum, frame):
    logger.info(f"📧 Received signal {signum}, shutting down...")
    monitor.stop_monitoring()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point"""
    logger.info("🚀 Starting Syn_OS Consciousness Monitoring Service")
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
    finally:
        monitor.stop_monitoring()

if __name__ == '__main__':
    asyncio.run(main())