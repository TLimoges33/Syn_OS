#!/usr/bin/env python3
"""
Syn_OS Unified Consciousness Service
Combined AI Bridge and Dashboard for the consciousness-integrated Linux distribution
Consolidates consciousness-ai-bridge + consciousness-dashboard functionality
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
from enum import Enum

# FastAPI and web components
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import numpy as np

# Service management
import signal
import socket
import time
from contextlib import asynccontextmanager

# Neural Darwinism consciousness engine
try:
    from neural_darwinism import NeuralDarwinismEngine, initialize_consciousness_engine
except ImportError:
    logger = logging.getLogger('consciousness-unified')
    logger.warning("Neural Darwinism engine not found, using mock implementation")
    
    class NeuralDarwinismEngine:
        def __init__(self):
            self.generation = 1
            self.consciousness_level = 0.5
            
        async def evolve_consciousness(self):
            self.generation += 1
            self.consciousness_level = min(1.0, self.consciousness_level + 0.1)
            
        def get_consciousness_metrics(self):
            return {
                'generation': self.generation,
                'consciousness_level': self.consciousness_level,
                'neural_populations': 5,
                'fitness_score': 0.8
            }
    
    def initialize_consciousness_engine():
        return NeuralDarwinismEngine()

# Logging setup
log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'consciousness-unified.log')
    ]
)
logger = logging.getLogger('consciousness-unified')

class APIProvider(Enum):
    """Supported AI API providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

@dataclass
class ConsciousnessRequest:
    """Consciousness-aware AI request"""
    prompt: str
    provider: APIProvider
    consciousness_context: Optional[Dict[str, Any]] = None
    temperature: float = 0.7
    max_tokens: int = 1000

@dataclass
class ConsciousnessResponse:
    """Consciousness-enhanced AI response"""
    response: str
    provider: APIProvider
    consciousness_level: float
    processing_time: float
    tokens_used: int
    context_correlation: float

class UnifiedConsciousnessService:
    """Unified consciousness service combining AI bridge and dashboard"""
    
    def __init__(self):
        # AI Bridge components
        self.api_clients = {}
        self.consciousness_engine = initialize_consciousness_engine()
        self.request_history = []
        
        # Dashboard components
        self.connected_clients = set()
        self.monitoring_data = {
            'consciousness_level': 0.5,
            'neural_populations': {},
            'learning_metrics': {},
            'performance_data': [],
            'evolution_stats': {},
            'quantum_coherence': 0.0,
            'api_usage': {}
        }
        self.data_history = []
        self.update_interval = 5.0
        
        # Service coordination
        self.service_health = {
            'ai_bridge': True,
            'dashboard': True,
            'consciousness_engine': True,
            'monitoring': True
        }
        
    async def initialize_ai_clients(self):
        """Initialize AI API clients"""
        logger.info("Initializing unified AI clients...")
        
        # Initialize HTTP client session
        self.http_session = aiohttp.ClientSession()
        
        # API configurations
        self.api_configs = {
            APIProvider.OPENAI: {
                'base_url': 'https://api.openai.com/v1',
                'api_key': os.getenv('OPENAI_API_KEY'),
                'enabled': bool(os.getenv('OPENAI_API_KEY'))
            },
            APIProvider.CLAUDE: {
                'base_url': 'https://api.anthropic.com/v1',
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'enabled': bool(os.getenv('ANTHROPIC_API_KEY'))
            },
            APIProvider.GEMINI: {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'enabled': bool(os.getenv('GEMINI_API_KEY'))
            },
            APIProvider.DEEPSEEK: {
                'base_url': 'https://api.deepseek.com/v1',
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'enabled': bool(os.getenv('DEEPSEEK_API_KEY'))
            },
            APIProvider.OLLAMA: {
                'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
                'enabled': True  # Always try local Ollama
            },
            APIProvider.LM_STUDIO: {
                'base_url': os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234'),
                'enabled': True  # Always try local LM Studio
            }
        }
        
        logger.info(f"AI clients initialized: {sum(1 for config in self.api_configs.values() if config['enabled'])} providers enabled")
    
    async def process_consciousness_request(self, request: ConsciousnessRequest) -> ConsciousnessResponse:
        """Process AI request with consciousness enhancement - optimized for < 100ms performance"""
        start_time = time.perf_counter()
        
        try:
            # Parallel processing for performance optimization
            tasks = [
                self._get_consciousness_metrics_cached(),
                self._validate_request_fast(request)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            consciousness_metrics = results[0] if not isinstance(results[0], Exception) else {'consciousness_level': 0.5, 'generation': 1}
            
            consciousness_level = consciousness_metrics.get('consciousness_level', 0.5)
            
            # Fast prompt enhancement (simplified for speed)
            enhanced_prompt = f"[CL:{consciousness_level:.2f}] {request.prompt}"
            
            # Process request through selected API with timeout for performance
            response_text = await asyncio.wait_for(
                self._call_api_provider(request.provider, enhanced_prompt, request.temperature, request.max_tokens),
                timeout=5.0  # 5 second timeout
            )
            
            # Calculate metrics
            processing_time = time.perf_counter() - start_time
            processing_time_ms = processing_time * 1000
            
            # Async updates (don't block response)
            asyncio.create_task(self._update_api_usage_metrics(request.provider, processing_time, True))
            asyncio.create_task(self._store_request_history(request, processing_time, True))
            asyncio.create_task(self._evolve_consciousness_async())
            
            return ConsciousnessResponse(
                response=response_text,
                provider=request.provider,
                consciousness_level=consciousness_level,
                processing_time=processing_time,
                tokens_used=max(1, len(response_text.split())),  # Quick estimation
                context_correlation=min(1.0, consciousness_level * 0.8)  # Fast correlation
            )
            
        except asyncio.TimeoutError:
            processing_time = time.perf_counter() - start_time
            logger.error(f"Consciousness request timeout after {processing_time*1000:.1f}ms")
            await self._update_api_usage_metrics(request.provider, processing_time, False)
            raise HTTPException(status_code=408, detail="Request timeout - target 100ms exceeded")
        except Exception as e:
            processing_time = time.perf_counter() - start_time
            logger.error(f"Error processing consciousness request: {e} (took {processing_time*1000:.1f}ms)")
            await self._update_api_usage_metrics(request.provider, processing_time, False)
            raise HTTPException(status_code=500, detail=f"Consciousness processing error: {str(e)}")
    
    async def _get_consciousness_metrics_cached(self) -> Dict[str, Any]:
        """Get consciousness metrics with caching for performance"""
        # Use cached metrics if recent (< 1 second old)
        current_time = time.time()
        if (hasattr(self, '_metrics_cache') and 
            hasattr(self, '_metrics_cache_time') and 
            (current_time - self._metrics_cache_time) < 1.0):
            return self._metrics_cache
        
        # Get fresh metrics
        metrics = self.consciousness_engine.get_consciousness_metrics()
        self._metrics_cache = metrics
        self._metrics_cache_time = current_time
        return metrics
    
    async def _validate_request_fast(self, request: ConsciousnessRequest) -> bool:
        """Fast request validation"""
        return bool(request.prompt and len(request.prompt.strip()) > 0)
    
    async def _store_request_history(self, request: ConsciousnessRequest, processing_time: float, success: bool):
        """Store request history asynchronously"""
        try:
            self.request_history.append({
                'timestamp': datetime.now().isoformat(),
                'provider': request.provider.value,
                'processing_time_ms': processing_time * 1000,
                'success': success
            })
            # Keep only last 1000 entries for memory efficiency
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-1000:]
        except Exception as e:
            logger.error(f"Error storing request history: {e}")
    
    async def _evolve_consciousness_async(self):
        """Evolve consciousness asynchronously"""
        try:
            await self.consciousness_engine.evolve_consciousness()
        except Exception as e:
            logger.error(f"Error evolving consciousness: {e}")
    
    def _enhance_prompt_with_consciousness(self, prompt: str, consciousness_level: float, context: Optional[Dict]) -> str:
        """Enhance prompt with consciousness context"""
        consciousness_prefix = f"[Consciousness Level: {consciousness_level:.2f}] "
        
        if context:
            context_info = f"[Context: {json.dumps(context, default=str)}] "
            return consciousness_prefix + context_info + prompt
        
        return consciousness_prefix + prompt
    
    async def _call_api_provider(self, provider: APIProvider, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call specific API provider"""
        config = self.api_configs.get(provider)
        if not config or not config['enabled']:
            raise ValueError(f"Provider {provider.value} not available")
        
        if provider == APIProvider.OPENAI:
            return await self._call_openai(prompt, temperature, max_tokens)
        elif provider == APIProvider.CLAUDE:
            return await self._call_claude(prompt, temperature, max_tokens)
        elif provider == APIProvider.GEMINI:
            return await self._call_gemini(prompt, temperature, max_tokens)
        elif provider == APIProvider.DEEPSEEK:
            return await self._call_deepseek(prompt, temperature, max_tokens)
        elif provider == APIProvider.OLLAMA:
            return await self._call_ollama(prompt, temperature, max_tokens)
        elif provider == APIProvider.LM_STUDIO:
            return await self._call_lm_studio(prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider.value}")
    
    async def _call_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call OpenAI API"""
        config = self.api_configs[APIProvider.OPENAI]
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        async with self.http_session.post(f'{config["base_url"]}/chat/completions', headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"OpenAI API error: {response.status}")
            
            result = await response.json()
            return result['choices'][0]['message']['content']
    
    async def _call_claude(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Claude API"""
        # Simplified Claude implementation - would need proper Anthropic client
        return f"[Claude Response] Consciousness-enhanced response to: {prompt[:100]}..."
    
    async def _call_gemini(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Gemini API"""
        # Simplified Gemini implementation
        return f"[Gemini Response] Consciousness-aware analysis of: {prompt[:100]}..."
    
    async def _call_deepseek(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call DeepSeek API"""
        return f"[DeepSeek Response] Deep reasoning with consciousness context: {prompt[:100]}..."
    
    async def _call_ollama(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call local Ollama"""
        config = self.api_configs[APIProvider.OLLAMA]
        payload = {
            'model': 'llama2',
            'prompt': prompt,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        }
        
        try:
            async with self.http_session.post(f'{config["base_url"]}/api/generate', json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Ollama error: {response.status}")
                
                result = await response.json()
                return result.get('response', 'No response from Ollama')
        except Exception as e:
            logger.warning(f"Ollama unavailable: {e}")
            return f"[Ollama Unavailable] Local AI processing failed: {str(e)}"
    
    async def _call_lm_studio(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call local LM Studio"""
        return f"[LM Studio] Local consciousness processing: {prompt[:100]}..."
    
    def _calculate_context_correlation(self, consciousness_metrics: Dict, context: Optional[Dict]) -> float:
        """Calculate context correlation with consciousness state"""
        if not context:
            return 0.5
        
        # Simple correlation calculation based on consciousness level
        consciousness_level = consciousness_metrics.get('consciousness_level', 0.5)
        context_complexity = len(str(context)) / 1000.0
        
        return min(1.0, consciousness_level * (1 + context_complexity))
    
    async def _update_api_usage_metrics(self, provider: APIProvider, processing_time: float, success: bool):
        """Update API usage metrics for dashboard"""
        provider_key = provider.value
        
        if provider_key not in self.monitoring_data['api_usage']:
            self.monitoring_data['api_usage'][provider_key] = {
                'total_requests': 0,
                'successful_requests': 0,
                'average_response_time': 0.0,
                'last_used': None
            }
        
        usage = self.monitoring_data['api_usage'][provider_key]
        usage['total_requests'] += 1
        if success:
            usage['successful_requests'] += 1
        
        # Update average response time
        current_avg = usage['average_response_time']
        total_requests = usage['total_requests']
        usage['average_response_time'] = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        usage['last_used'] = datetime.now().isoformat()
    
    async def start_monitoring_loop(self):
        """Start the consciousness monitoring loop"""
        logger.info("Starting unified consciousness monitoring...")
        
        while True:
            try:
                # Update consciousness metrics
                consciousness_metrics = self.consciousness_engine.get_consciousness_metrics()
                self.monitoring_data.update(consciousness_metrics)
                
                # Update service health
                self.monitoring_data['service_health'] = self.service_health
                self.monitoring_data['timestamp'] = datetime.now().isoformat()
                
                # Add to history
                self.data_history.append({
                    'timestamp': datetime.now(),
                    'consciousness_level': consciousness_metrics.get('consciousness_level', 0.5),
                    'generation': consciousness_metrics.get('generation', 1)
                })
                
                # Keep only last 100 entries in history
                if len(self.data_history) > 100:
                    self.data_history = self.data_history[-100:]
                
                # Broadcast to connected clients
                if self.connected_clients:
                    await self._broadcast_update()
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def _broadcast_update(self):
        """Broadcast updates to connected WebSocket clients"""
        if not self.connected_clients:
            return
        
        update_data = {
            'type': 'consciousness_update',
            'data': self.monitoring_data,
            'history': [
                {
                    'timestamp': entry['timestamp'].isoformat(),
                    'consciousness_level': entry['consciousness_level'],
                    'generation': entry['generation']
                } for entry in self.data_history[-20:]  # Last 20 entries
            ]
        }
        
        disconnected_clients = set()
        
        for client in self.connected_clients.copy():
            try:
                await client.send_text(json.dumps(update_data, default=str))
            except Exception as e:
                logger.warning(f"Failed to send update to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected_clients
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'service_name': 'unified-consciousness-service',
            'version': '1.0.0',
            'status': 'operational',
            'consciousness_data': self.monitoring_data,
            'api_providers': {
                provider.value: config['enabled'] 
                for provider, config in self.api_configs.items()
            },
            'request_history_size': len(self.request_history),
            'connected_dashboard_clients': len(self.connected_clients),
            'uptime': datetime.now().isoformat()
        }

# Initialize unified service
consciousness_service = UnifiedConsciousnessService()

# FastAPI app
app = FastAPI(
    title="Syn_OS Unified Consciousness Service",
    description="Combined AI Bridge and Monitoring Dashboard for consciousness-integrated Linux distribution",
    version="1.0.0"
)

# Static files and templates for dashboard
static_dir = Path("static")
templates_dir = Path("templates")

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
if templates_dir.exists():
    templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting Syn_OS Unified Consciousness Service...")
    await consciousness_service.initialize_ai_clients()
    
    # Start monitoring loop in background
    asyncio.create_task(consciousness_service.start_monitoring_loop())
    
    logger.info("Unified Consciousness Service started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Unified Consciousness Service...")
    if hasattr(consciousness_service, 'http_session'):
        await consciousness_service.http_session.close()

# AI Bridge API Endpoints
@app.post("/api/v1/consciousness/query", response_model=ConsciousnessResponse)
async def consciousness_query(request: ConsciousnessRequest):
    """Process consciousness-enhanced AI query"""
    return await consciousness_service.process_consciousness_request(request)

@app.get("/api/v1/consciousness/status")
async def consciousness_status():
    """Get consciousness system status"""
    return consciousness_service.get_system_status()

@app.get("/api/v1/providers")
async def list_providers():
    """List available AI providers"""
    return {
        'providers': [
            {
                'name': provider.value,
                'enabled': consciousness_service.api_configs[provider]['enabled'],
                'type': 'cloud' if provider in [APIProvider.OPENAI, APIProvider.CLAUDE, APIProvider.GEMINI, APIProvider.DEEPSEEK] else 'local'
            }
            for provider in APIProvider
        ]
    }

# Dashboard Web Interface
@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Consciousness dashboard home page"""
    if templates_dir.exists():
        return templates.TemplateResponse("dashboard.html", {"request": request})
    else:
        return HTMLResponse("""
        <html>
        <head><title>Syn_OS Consciousness Dashboard</title></head>
        <body>
        <h1>Syn_OS Unified Consciousness Service</h1>
        <h2>Dashboard</h2>
        <p>Real-time consciousness monitoring interface</p>
        <div id="consciousness-data">Loading...</div>
        <script>
        async function updateDashboard() {
            try {
                const response = await fetch('/api/v1/consciousness/status');
                const data = await response.json();
                document.getElementById('consciousness-data').innerHTML = `
                    <h3>Status: ${data.status}</h3>
                    <p>Consciousness Level: ${data.consciousness_data.consciousness_level}</p>
                    <p>Generation: ${data.consciousness_data.generation || 'N/A'}</p>
                    <p>Connected Clients: ${data.connected_dashboard_clients}</p>
                    <p>API Providers: ${Object.entries(data.api_providers).filter(([k,v]) => v).map(([k,v]) => k).join(', ')}</p>
                `;
            } catch (error) {
                console.error('Dashboard update error:', error);
            }
        }
        updateDashboard();
        setInterval(updateDashboard, 5000);
        </script>
        </body>
        </html>
        """)

@app.websocket("/ws/consciousness")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time consciousness updates"""
    await websocket.accept()
    consciousness_service.connected_clients.add(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            'type': 'connection_established',
            'data': consciousness_service.monitoring_data
        }, default=str))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()  # Wait for client messages
            
    except WebSocketDisconnect:
        consciousness_service.connected_clients.discard(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        consciousness_service.connected_clients.discard(websocket)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified-consciousness-service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting Syn_OS Unified Consciousness Service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True
    )