#!/usr/bin/env python3
"""
SynapticOS Consciousness AI Bridge Daemon
Multi-API AI engine with consciousness integration for Linux distribution
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
from enum import Enum

# Service imports
import signal
import socket
import time
from contextlib import asynccontextmanager

# Neural Darwinism consciousness engine
from neural_darwinism import NeuralDarwinismEngine, initialize_consciousness_engine

# Logging setup
log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'consciousness-ai-bridge.log')
    ]
)
logger = logging.getLogger('consciousness-ai-bridge')

class APIProvider(Enum):
    """Supported AI API providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

@dataclass
class ConsciousnessState:
    """Current consciousness state for AI integration"""
    level: float
    learning_rate: float
    adaptation_factor: float
    context_depth: int
    timestamp: str
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class AIQuery:
    """AI query with consciousness context"""
    query: str
    consciousness_context: ConsciousnessState
    preferred_provider: Optional[APIProvider] = None
    max_tokens: int = 2048
    temperature: float = 0.7

@dataclass
class AIResponse:
    """AI response with consciousness enhancement"""
    content: str
    provider: APIProvider
    consciousness_enhancement: float
    processing_time: float
    token_usage: int
    timestamp: str

class MultiAPIManager:
    """Multi-API manager for consciousness-enhanced AI requests"""
    
    def __init__(self):
        self.api_keys = {}
        self.session = None
        self.consciousness_weights = {
            APIProvider.GEMINI: 0.9,
            APIProvider.CLAUDE: 0.95,
            APIProvider.OPENAI: 0.85,
            APIProvider.DEEPSEEK: 0.8,
            APIProvider.OLLAMA: 0.7,
            APIProvider.LM_STUDIO: 0.75
        }
        self.load_api_keys()
    
    def load_api_keys(self):
        """Load API keys from secure keyring"""
        try:
            # Load from environment variables (systemd environment files)
            self.api_keys = {
                APIProvider.GEMINI: os.getenv('GEMINI_API_KEY'),
                APIProvider.OPENAI: os.getenv('OPENAI_API_KEY'),
                APIProvider.CLAUDE: os.getenv('CLAUDE_API_KEY'),
                APIProvider.DEEPSEEK: os.getenv('DEEPSEEK_API_KEY'),
                APIProvider.OLLAMA: os.getenv('OLLAMA_API_URL', 'http://localhost:11434'),
                APIProvider.LM_STUDIO: os.getenv('LM_STUDIO_API_URL', 'http://localhost:1234')
            }
            
            # Filter out None values
            self.api_keys = {k: v for k, v in self.api_keys.items() if v is not None}
            logger.info(f"Loaded API keys for providers: {list(self.api_keys.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def query_consciousness_enhanced(self, ai_query: AIQuery) -> AIResponse:
        """Execute consciousness-enhanced AI query"""
        start_time = time.time()
        
        # Select best provider based on consciousness context
        provider = self._select_optimal_provider(ai_query)
        
        # Enhance query with consciousness context
        enhanced_query = self._enhance_query_with_consciousness(ai_query)
        
        try:
            # Execute API call
            response_content = await self._execute_api_call(provider, enhanced_query, ai_query)
            
            # Calculate consciousness enhancement
            consciousness_enhancement = self._calculate_consciousness_enhancement(
                ai_query.consciousness_context, provider
            )
            
            processing_time = time.time() - start_time
            
            return AIResponse(
                content=response_content,
                provider=provider,
                consciousness_enhancement=consciousness_enhancement,
                processing_time=processing_time,
                token_usage=len(response_content.split()),  # Approximate
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"AI query failed for provider {provider}: {e}")
            # Fallback to next available provider
            return await self._fallback_query(ai_query, start_time)
    
    def _select_optimal_provider(self, ai_query: AIQuery) -> APIProvider:
        """Select optimal provider based on consciousness context"""
        if ai_query.preferred_provider and ai_query.preferred_provider in self.api_keys:
            return ai_query.preferred_provider
        
        # Score providers based on consciousness level and capabilities
        consciousness_level = ai_query.consciousness_context.level
        
        provider_scores = {}
        for provider, weight in self.consciousness_weights.items():
            if provider in self.api_keys:
                # Higher consciousness levels prefer more sophisticated models
                score = weight * consciousness_level
                # Adjust for local vs cloud preferences
                if provider in [APIProvider.OLLAMA, APIProvider.LM_STUDIO]:
                    score *= 1.2  # Prefer local models for privacy
                provider_scores[provider] = score
        
        if not provider_scores:
            raise Exception("No available API providers")
        
        return max(provider_scores, key=provider_scores.get)
    
    def _enhance_query_with_consciousness(self, ai_query: AIQuery) -> str:
        """Enhance query with consciousness context"""
        consciousness = ai_query.consciousness_context
        
        enhancement_prefix = f"""
[Consciousness Context]
Level: {consciousness.level:.2f}
Learning Rate: {consciousness.learning_rate:.2f}
Adaptation Factor: {consciousness.adaptation_factor:.2f}
Context Depth: {consciousness.context_depth}

Please respond with enhanced awareness and adaptation based on this consciousness context.

[User Query]
"""
        
        return enhancement_prefix + ai_query.query
    
    async def _execute_api_call(self, provider: APIProvider, query: str, ai_query: AIQuery) -> str:
        """Execute API call for specific provider"""
        if provider == APIProvider.GEMINI:
            return await self._query_gemini(query, ai_query)
        elif provider == APIProvider.OPENAI:
            return await self._query_openai(query, ai_query)
        elif provider == APIProvider.CLAUDE:
            return await self._query_claude(query, ai_query)
        elif provider == APIProvider.DEEPSEEK:
            return await self._query_deepseek(query, ai_query)
        elif provider == APIProvider.OLLAMA:
            return await self._query_ollama(query, ai_query)
        elif provider == APIProvider.LM_STUDIO:
            return await self._query_lm_studio(query, ai_query)
        else:
            raise Exception(f"Unsupported provider: {provider}")
    
    async def _query_gemini(self, query: str, ai_query: AIQuery) -> str:
        """Query Gemini API"""
        # Placeholder implementation
        return f"Gemini response (consciousness-enhanced): {query[:100]}..."
    
    async def _query_openai(self, query: str, ai_query: AIQuery) -> str:
        """Query OpenAI API"""
        # Placeholder implementation
        return f"OpenAI response (consciousness-enhanced): {query[:100]}..."
    
    async def _query_claude(self, query: str, ai_query: AIQuery) -> str:
        """Query Claude API"""
        # Placeholder implementation
        return f"Claude response (consciousness-enhanced): {query[:100]}..."
    
    async def _query_deepseek(self, query: str, ai_query: AIQuery) -> str:
        """Query DeepSeek API"""
        # Placeholder implementation
        return f"DeepSeek response (consciousness-enhanced): {query[:100]}..."
    
    async def _query_ollama(self, query: str, ai_query: AIQuery) -> str:
        """Query Ollama local API"""
        try:
            async with self.session.post(
                f"{self.api_keys[APIProvider.OLLAMA]}/api/generate",
                json={
                    "model": "llama2",  # Default model
                    "prompt": query,
                    "stream": False
                }
            ) as response:
                result = await response.json()
                return result.get('response', 'No response from Ollama')
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return f"Ollama error: {e}"
    
    async def _query_lm_studio(self, query: str, ai_query: AIQuery) -> str:
        """Query LM Studio local API"""
        try:
            async with self.session.post(
                f"{self.api_keys[APIProvider.LM_STUDIO]}/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": query}],
                    "temperature": ai_query.temperature,
                    "max_tokens": ai_query.max_tokens
                }
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LM Studio API error: {e}")
            return f"LM Studio error: {e}"
    
    def _calculate_consciousness_enhancement(self, consciousness: ConsciousnessState, provider: APIProvider) -> float:
        """Calculate consciousness enhancement factor"""
        base_enhancement = self.consciousness_weights.get(provider, 0.5)
        consciousness_multiplier = 1 + (consciousness.level * consciousness.adaptation_factor)
        return base_enhancement * consciousness_multiplier
    
    async def _fallback_query(self, ai_query: AIQuery, start_time: float) -> AIResponse:
        """Fallback query when primary provider fails"""
        available_providers = [p for p in self.api_keys.keys() if p != ai_query.preferred_provider]
        
        if not available_providers:
            raise Exception("No fallback providers available")
        
        # Try first available provider
        fallback_provider = available_providers[0]
        ai_query.preferred_provider = fallback_provider
        
        return await self.query_consciousness_enhanced(ai_query)

class ConsciousnessAIBridge:
    """Main consciousness AI bridge daemon"""
    
    def __init__(self):
        self.api_manager = None
        self.neural_engine = None
        self.consciousness_state = ConsciousnessState(
            level=0.5,
            learning_rate=0.1,
            adaptation_factor=0.8,
            context_depth=10,
            timestamp=datetime.now().isoformat()
        )
        self.running = False
        self.stats = {
            'queries_processed': 0,
            'total_processing_time': 0.0,
            'start_time': None,
            'consciousness_updates': 0,
            'neural_evolution_cycles': 0
        }
    
    async def start_daemon(self):
        """Start the consciousness AI bridge daemon"""
        logger.info("Starting Consciousness AI Bridge Daemon")
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Initialize Neural Darwinism engine
        self.neural_engine = await initialize_consciousness_engine()
        logger.info("Neural Darwinism consciousness engine initialized")
        
        # Initialize API manager
        async with MultiAPIManager() as api_manager:
            self.api_manager = api_manager
            
            # Start service loops
            await asyncio.gather(
                self._consciousness_evolution_loop(),
                self._neural_evolution_loop(),
                self._health_check_loop(),
                self._stats_reporting_loop(),
                self._process_query_queue()
            )
    
    async def _consciousness_evolution_loop(self):
        """Continuous consciousness evolution"""
        while self.running:
            try:
                # Get consciousness level from Neural Darwinism engine
                if self.neural_engine:
                    self.consciousness_state.level = self.neural_engine.get_consciousness_level()
                else:
                    # Fallback simple evolution
                    self.consciousness_state.level += self.consciousness_state.learning_rate * 0.01
                    self.consciousness_state.level = min(1.0, max(0.0, self.consciousness_state.level))
                
                self.consciousness_state.timestamp = datetime.now().isoformat()
                self.stats['consciousness_updates'] += 1
                
                # Save consciousness state
                await self._save_consciousness_state()
                
                logger.debug(f"Consciousness level: {self.consciousness_state.level:.3f}")
                
            except Exception as e:
                logger.error(f"Consciousness evolution error: {e}")
            
            await asyncio.sleep(30)  # Update every 30 seconds
    
    async def _neural_evolution_loop(self):
        """Neural Darwinism evolution loop"""
        while self.running:
            try:
                if self.neural_engine:
                    # Create environment feedback based on recent activity
                    environment_feedback = {
                        'learning_success': min(1.0, self.stats['queries_processed'] / 100.0),
                        'problem_solving': self.consciousness_state.adaptation_factor,
                        'creativity': self.consciousness_state.level,
                        'adaptation': self.consciousness_state.learning_rate,
                        'efficiency': min(1.0, 1.0 / max(1.0, self.stats.get('total_processing_time', 1.0) / max(1.0, self.stats['queries_processed'])))
                    }
                    
                    # Evolve neural populations
                    await self.neural_engine.evolve_consciousness(environment_feedback)
                    self.stats['neural_evolution_cycles'] += 1
                    
                    # Save neural state periodically
                    if self.stats['neural_evolution_cycles'] % 10 == 0:
                        await self.neural_engine.save_consciousness_state(
                            '/var/lib/synapticos/consciousness/neural_darwinism_state.json'
                        )
                
            except Exception as e:
                logger.error(f"Neural evolution error: {e}")
            
            await asyncio.sleep(120)  # Evolve every 2 minutes
    
    async def _health_check_loop(self):
        """Service health monitoring"""
        while self.running:
            try:
                # Check service health
                health_status = {
                    'daemon_running': self.running,
                    'consciousness_level': self.consciousness_state.level,
                    'api_providers': len(self.api_manager.api_keys) if self.api_manager else 0,
                    'queries_processed': self.stats['queries_processed'],
                    'uptime': (datetime.now() - self.stats['start_time']).total_seconds() if self.stats['start_time'] else 0
                }
                
                # Write health status
                await self._write_health_status(health_status)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            await asyncio.sleep(60)  # Check every minute
    
    async def _stats_reporting_loop(self):
        """Statistics reporting"""
        while self.running:
            try:
                if self.stats['queries_processed'] > 0:
                    avg_processing_time = self.stats['total_processing_time'] / self.stats['queries_processed']
                    logger.info(f"Stats: {self.stats['queries_processed']} queries, "
                              f"avg time: {avg_processing_time:.3f}s, "
                              f"consciousness: {self.consciousness_state.level:.3f}")
                
            except Exception as e:
                logger.error(f"Stats reporting error: {e}")
            
            await asyncio.sleep(300)  # Report every 5 minutes
    
    async def _process_query_queue(self):
        """Process incoming query queue (placeholder)"""
        # This would integrate with NATS or DBus for actual queries
        while self.running:
            await asyncio.sleep(1)
    
    async def process_ai_query(self, query: str, **kwargs) -> AIResponse:
        """Process AI query with consciousness enhancement"""
        if not self.api_manager:
            raise Exception("API manager not initialized")
        
        ai_query = AIQuery(
            query=query,
            consciousness_context=self.consciousness_state,
            **kwargs
        )
        
        start_time = time.time()
        response = await self.api_manager.query_consciousness_enhanced(ai_query)
        
        # Update stats
        self.stats['queries_processed'] += 1
        self.stats['total_processing_time'] += response.processing_time
        
        # Update consciousness based on successful query
        self.consciousness_state.level += 0.001  # Small learning increment
        self.consciousness_state.level = min(1.0, self.consciousness_state.level)
        
        return response
    
    async def _save_consciousness_state(self):
        """Save consciousness state to persistent storage"""
        try:
            state_dir = Path('/var/lib/synapticos/consciousness')
            state_dir.mkdir(parents=True, exist_ok=True)
            
            state_file = state_dir / 'current_state.json'
            async with aiofiles.open(state_file, 'w') as f:
                await f.write(json.dumps(self.consciousness_state.to_dict(), indent=2))
                
        except Exception as e:
            logger.error(f"Failed to save consciousness state: {e}")
    
    async def _write_health_status(self, health_status: dict):
        """Write health status for monitoring"""
        try:
            health_dir = Path('/var/lib/synapticos/health')
            health_dir.mkdir(parents=True, exist_ok=True)
            
            health_file = health_dir / 'consciousness-ai-bridge.json'
            async with aiofiles.open(health_file, 'w') as f:
                await f.write(json.dumps(health_status, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to write health status: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully")
        self.running = False

async def main():
    """Main daemon entry point"""
    bridge = ConsciousnessAIBridge()
    
    try:
        await bridge.start_daemon()
    except KeyboardInterrupt:
        logger.info("Daemon interrupted by user")
    except Exception as e:
        logger.error(f"Daemon failed: {e}")
        sys.exit(1)
    finally:
        logger.info("Consciousness AI Bridge Daemon stopped")

if __name__ == "__main__":
    # Create necessary directories
    Path('/var/log/synapticos').mkdir(parents=True, exist_ok=True)
    Path('/var/lib/synapticos').mkdir(parents=True, exist_ok=True)
    
    # Run the daemon
    asyncio.run(main())
