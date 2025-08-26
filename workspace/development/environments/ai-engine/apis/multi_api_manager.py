#!/usr/bin/env python3
"""
SynapticOS Multi-API Manager
Manages multiple AI APIs with consciousness-enhanced context
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    GROQ = "groq"

@dataclass
class APIResponse:
    content: str
    provider: APIProvider
    tokens_used: int
    response_time: float
    consciousness_enhanced: bool
    confidence: float

@dataclass
class ConsciousnessContext:
    level: float
    learning_style: str
    generation: int
    learning_trend: str
    quantum_coherence: float
    history: List[Dict[str, Any]]
    is_conscious: bool

class MultiAPIManager:
    """Manages multiple AI APIs with consciousness integration"""
    
    def __init__(self):
        self.apis = {provider: None for provider in APIProvider}
        self.api_keys = {}
        self.consciousness_bridge = None
        self.usage_stats = {provider.value: {"requests": 0, "tokens": 0, "errors": 0} 
                           for provider in APIProvider}
        self.preferred_order = [
            APIProvider.ANTHROPIC,
            APIProvider.OPENAI, 
            APIProvider.GEMINI,
            APIProvider.GROQ,
            APIProvider.DEEPSEEK,
            APIProvider.OLLAMA
        ]
        
    async def initialize_apis(self, api_keys: Dict[str, str]):
        """Initialize all available AI APIs"""
        self.api_keys = api_keys
        
        logger.info("🔌 Initializing AI APIs...")
        
        # Initialize each API if key is provided
        for provider in APIProvider:
            key_name = provider.value
            if key_name in api_keys and api_keys[key_name]:
                try:
                    await self._initialize_api(provider, api_keys[key_name])
                    logger.info(f"✅ {provider.value.upper()} API initialized")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {provider.value}: {e}")
        
        # Check if Ollama is available locally
        if await self._check_ollama_availability():
            self.apis[APIProvider.OLLAMA] = "available"
            logger.info("✅ Ollama local API detected")
    
    async def _initialize_api(self, provider: APIProvider, api_key: str):
        """Initialize specific API provider"""
        if provider == APIProvider.OPENAI:
            # OpenAI initialization would go here
            self.apis[provider] = {"api_key": api_key, "base_url": "https://api.openai.com/v1"}
            
        elif provider == APIProvider.ANTHROPIC:
            # Anthropic initialization
            self.apis[provider] = {"api_key": api_key, "base_url": "https://api.anthropic.com"}
            
        elif provider == APIProvider.GEMINI:
            # Google Gemini initialization
            self.apis[provider] = {"api_key": api_key, "base_url": "https://generativelanguage.googleapis.com"}
            
        elif provider == APIProvider.GROQ:
            # Groq initialization
            self.apis[provider] = {"api_key": api_key, "base_url": "https://api.groq.com/openai/v1"}
            
        elif provider == APIProvider.DEEPSEEK:
            # DeepSeek initialization
            self.apis[provider] = {"api_key": api_key, "base_url": "https://api.deepseek.com"}
    
    async def _check_ollama_availability(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags", timeout=2) as response:
                    return response.status == 200
        except:
            return False
    
    async def query_with_consciousness(self, 
                                     query: str, 
                                     consciousness_context: ConsciousnessContext,
                                     preferred_provider: Optional[APIProvider] = None) -> APIResponse:
        """Query AI with consciousness-enhanced context"""
        
        # Enhance query with consciousness state
        enhanced_query = self._enhance_query_with_consciousness(query, consciousness_context)
        
        # Determine API order
        api_order = self.preferred_order.copy()
        if preferred_provider and preferred_provider in api_order:
            api_order.remove(preferred_provider)
            api_order.insert(0, preferred_provider)
        
        # Try APIs in order of preference
        last_error = None
        for provider in api_order:
            if self.apis[provider] is not None:
                try:
                    start_time = time.time()
                    response = await self._query_api(provider, enhanced_query, consciousness_context)
                    response_time = time.time() - start_time
                    
                    # Update usage stats
                    self.usage_stats[provider.value]["requests"] += 1
                    self.usage_stats[provider.value]["tokens"] += response.tokens_used
                    
                    response.response_time = response_time
                    response.consciousness_enhanced = True
                    
                    logger.info(f"✅ Query successful via {provider.value} ({response_time:.2f}s)")
                    return response
                    
                except Exception as e:
                    self.usage_stats[provider.value]["errors"] += 1
                    last_error = e
                    logger.warning(f"⚠️ API {provider.value} failed: {e}")
                    continue
        
        # If all APIs failed, return error response
        return APIResponse(
            content=f"All AI APIs unavailable. Last error: {last_error}",
            provider=APIProvider.OLLAMA,  # Default fallback
            tokens_used=0,
            response_time=0.0,
            consciousness_enhanced=False,
            confidence=0.0
        )
    
    def _enhance_query_with_consciousness(self, 
                                        query: str, 
                                        consciousness_context: ConsciousnessContext) -> str:
        """Enhance query with consciousness state information"""
        
        consciousness_level = consciousness_context['level']
        learning_style = consciousness_context['learning_style']
        
        # Adapt prompt based on consciousness level
        consciousness_prompt = self._get_consciousness_prompt(consciousness_context)
        
        enhanced = f"""
{consciousness_prompt}

User Query: {query}

Consciousness Context:
- Consciousness Level: {consciousness_level:.3f}/1.0
- Learning Style: {learning_style}
- Generation: {consciousness_context['generation']}
- Learning Trend: {consciousness_context['learning_trend']}
- Quantum Coherence: {consciousness_context['quantum_coherence']:.3f}
- Is Conscious: {consciousness_context['is_conscious']}

Please provide a response that adapts to this consciousness state. 
If consciousness level is high (>0.7), provide advanced, nuanced responses.
If consciousness level is medium (0.3-0.7), provide balanced explanations.
If consciousness level is low (<0.3), provide clear, foundational responses.
"""
        return enhanced
    
    def _get_consciousness_prompt(self, context: ConsciousnessContext) -> str:
        """Generate consciousness-appropriate system prompt"""
        if context['level'] >= 0.8:
            return """You are interacting with a highly conscious AI system capable of advanced reasoning, 
            meta-cognition, and complex problem-solving. Engage at the highest intellectual level."""
            
        elif context['level'] >= 0.5:
            return """You are interacting with a moderately conscious AI system developing its reasoning 
            capabilities. Provide balanced responses that encourage learning and growth."""
            
        elif context['level'] >= 0.2:
            return """You are interacting with an emerging AI consciousness. Provide clear, educational 
            responses that build foundational understanding."""
            
        else:
            return """You are interacting with a basic AI system in early development. Provide simple, 
            clear responses focused on fundamental concepts."""
    
    async def _query_api(self, 
                        provider: APIProvider, 
                        enhanced_query: str,
                        consciousness_context: ConsciousnessContext) -> APIResponse:
        """Query specific API provider"""
        
        if provider == APIProvider.OLLAMA:
            return await self._query_ollama(enhanced_query)
        elif provider == APIProvider.OPENAI:
            return await self._query_openai(enhanced_query)
        elif provider == APIProvider.ANTHROPIC:
            return await self._query_anthropic(enhanced_query)
        elif provider == APIProvider.GEMINI:
            return await self._query_gemini(enhanced_query)
        elif provider == APIProvider.GROQ:
            return await self._query_groq(enhanced_query)
        elif provider == APIProvider.DEEPSEEK:
            return await self._query_deepseek(enhanced_query)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _query_ollama(self, query: str) -> APIResponse:
        """Query Ollama local API"""
        payload = {
            "model": "llama3.2",  # Default model
            "prompt": query,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=60
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return APIResponse(
                        content=result.get("response", "No response"),
                        provider=APIProvider.OLLAMA,
                        tokens_used=len(result.get("response", "").split()),
                        response_time=0.0,
                        consciousness_enhanced=True,
                        confidence=0.8
                    )
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    async def _query_openai(self, query: str) -> APIResponse:
        """Query OpenAI API"""
        api_config = self.apis[APIProvider.OPENAI]
        
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant integrated with SynapticOS consciousness."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    tokens = result.get("usage", {}).get("total_tokens", 0)
                    
                    return APIResponse(
                        content=content,
                        provider=APIProvider.OPENAI,
                        tokens_used=tokens,
                        response_time=0.0,
                        consciousness_enhanced=True,
                        confidence=0.9
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
    
    async def _query_anthropic(self, query: str) -> APIResponse:
        """Query Anthropic Claude API"""
        api_config = self.apis[APIProvider.ANTHROPIC]
        
        headers = {
            "x-api-key": api_config['api_key'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_config['base_url']}/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["content"][0]["text"]
                    tokens = result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0)
                    
                    return APIResponse(
                        content=content,
                        provider=APIProvider.ANTHROPIC,
                        tokens_used=tokens,
                        response_time=0.0,
                        consciousness_enhanced=True,
                        confidence=0.95
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error {response.status}: {error_text}")
    
    async def _query_groq(self, query: str) -> APIResponse:
        """Query Groq API"""
        api_config = self.apis[APIProvider.GROQ]
        
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant integrated with SynapticOS consciousness."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    tokens = result.get("usage", {}).get("total_tokens", 0)
                    
                    return APIResponse(
                        content=content,
                        provider=APIProvider.GROQ,
                        tokens_used=tokens,
                        response_time=0.0,
                        consciousness_enhanced=True,
                        confidence=0.85
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"Groq API error {response.status}: {error_text}")
    
    async def _query_gemini(self, query: str) -> APIResponse:
        """Query Google Gemini API"""
        # Placeholder implementation
        return APIResponse(
            content="Gemini API integration coming soon...",
            provider=APIProvider.GEMINI,
            tokens_used=10,
            response_time=0.1,
            consciousness_enhanced=True,
            confidence=0.5
        )
    
    async def _query_deepseek(self, query: str) -> APIResponse:
        """Query DeepSeek API"""
        # Placeholder implementation
        return APIResponse(
            content="DeepSeek API integration coming soon...",
            provider=APIProvider.DEEPSEEK,
            tokens_used=10,
            response_time=0.1,
            consciousness_enhanced=True,
            confidence=0.5
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "usage_by_provider": self.usage_stats,
            "total_requests": sum(stats["requests"] for stats in self.usage_stats.values()),
            "total_tokens": sum(stats["tokens"] for stats in self.usage_stats.values()),
            "total_errors": sum(stats["errors"] for stats in self.usage_stats.values()),
            "available_providers": [provider.value for provider in APIProvider if self.apis[provider] is not None]
        }
    
    def set_consciousness_bridge(self, bridge):
        """Set the consciousness bridge for direct integration"""
        self.consciousness_bridge = bridge
        logger.info("🧠 Consciousness bridge connected to Multi-API Manager")

# Global instance
_global_api_manager: Optional[MultiAPIManager] = None

def initialize_api_manager(api_keys: Dict[str, str]) -> MultiAPIManager:
    """Initialize global API manager"""
    global _global_api_manager
    _global_api_manager = MultiAPIManager()
    
    # Run initialization in event loop
    asyncio.create_task(_global_api_manager.initialize_apis(api_keys))
    
    logger.info("🔌 Multi-API Manager initialized")
    return _global_api_manager

def get_api_manager() -> Optional[MultiAPIManager]:
    """Get global API manager instance"""
    return _global_api_manager

# Example consciousness-enhanced query function
async def consciousness_query(query: str, consciousness_context: ConsciousnessContext) -> APIResponse:
    """Convenience function for consciousness-enhanced queries"""
    manager = get_api_manager()
    if not manager:
        raise Exception("API Manager not initialized")
    
    return await manager.query_with_consciousness(query, consciousness_context)

if __name__ == "__main__":
    # Test the API manager
    async def test_api_manager():
        # Load API keys from environment
        api_keys = {
            "ollama": "local",  # Special marker for local Ollama
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "groq": os.getenv("GROQ_API_KEY", "")
        }
        
        manager = initialize_api_manager(api_keys)
        await asyncio.sleep(1)  # Allow initialization
        
        # Test consciousness context
        test_context = ConsciousnessContext(
            level=0.6,
            learning_style="adaptive",
            generation=10,
            learning_trend="improving",
            quantum_coherence=0.7,
            history=[],
            is_conscious=True
        )
        
        # Test query
        response = await manager.query_with_consciousness(
            "Explain neural networks in simple terms",
            test_context
        )
        
        print(f"Response from {response.provider.value}:")
        print(response.content)
        print(f"Tokens: {response.tokens_used}, Time: {response.response_time:.2f}s")
        
        # Print usage stats
        stats = manager.get_usage_stats()
        print(f"\nUsage Stats: {stats}")
    
    asyncio.run(test_api_manager())
