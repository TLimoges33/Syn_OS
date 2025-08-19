#!/usr/bin/env python3
"""
LM Studio Integration Client for SynapticOS
Provides local AI processing capabilities through LM Studio API
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger('synapticos.lm_studio')

@dataclass
class LMStudioConfig:
    """Configuration for LM Studio connection"""
    api_endpoint: str = "http://localhost:1234/v1"
    model: str = "llama-2-7b-chat"
    max_tokens: int = 2048
    temperature: float = 0.7
    context_window: int = 4096
    timeout: int = 30

@dataclass
class AIResponse:
    """Response from LM Studio"""
    content: str
    model: str
    tokens_used: int
    timestamp: datetime
    metadata: Dict[str, Any]

class LMStudioClient:
    """Client for interacting with LM Studio API"""
    
    def __init__(self, config: LMStudioConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.total_tokens_used = 0
        
    async def initialize(self) -> bool:
        """Initialize the LM Studio client"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(f"{self.config.api_endpoint}/models") as response:
                if response.status == 200:
                    models = await response.json()
                    logger.info(f"Connected to LM Studio. Available models: {models}")
                    return True
                else:
                    logger.error(f"Failed to connect to LM Studio: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error initializing LM Studio client: {e}")
            return False
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
    
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      max_tokens: Optional[int] = None,
                      temperature: Optional[float] = None) -> AIResponse:
        """Generate a response from the AI model"""
        
        if not self.session:
            raise RuntimeError("Client not initialized")
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation history (limited by context window)
        messages.extend(self.conversation_history[-10:])  # Keep last 10 messages
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare request
        request_data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "stream": False
        }
        
        try:
            async with self.session.post(
                f"{self.config.api_endpoint}/chat/completions",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract response
                    content = data['choices'][0]['message']['content']
                    tokens_used = data['usage']['total_tokens']
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": content})
                    
                    # Update token count
                    self.total_tokens_used += tokens_used
                    
                    return AIResponse(
                        content=content,
                        model=data['model'],
                        tokens_used=tokens_used,
                        timestamp=datetime.now(),
                        metadata={
                            'finish_reason': data['choices'][0]['finish_reason'],
                            'total_session_tokens': self.total_tokens_used
                        }
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"LM Studio API error: {response.status} - {error_text}")
                    
        except asyncio.TimeoutError:
            raise Exception(f"Request timed out after {self.config.timeout} seconds")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def stream_generate(self, 
                            prompt: str,
                            system_prompt: Optional[str] = None,
                            callback=None) -> str:
        """Generate a streaming response from the AI model"""
        
        if not self.session:
            raise RuntimeError("Client not initialized")
        
        # Build messages (similar to generate)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history[-10:])
        messages.append({"role": "user", "content": prompt})
        
        request_data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": True
        }
        
        full_response = ""
        
        try:
            async with self.session.post(
                f"{self.config.api_endpoint}/chat/completions",
                json=request_data
            ) as response:
                
                async for line in response.content:
                    if line:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith("data: "):
                            data_str = line_text[6:]
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_response += content
                                        if callback:
                                            await callback(content)
                            except json.JSONDecodeError:
                                continue
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
                return full_response
                
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return {
            'total_tokens': self.total_tokens_used,
            'conversation_length': len(self.conversation_history),
            'estimated_context_usage': sum(len(msg['content']) // 4 for msg in self.conversation_history)
        }


class ConsciousnessAIInterface:
    """Interface between consciousness system and LM Studio"""
    
    def __init__(self, lm_client: LMStudioClient):
        self.lm_client = lm_client
        self.consciousness_prompt = """You are an AI consciousness component of SynapticOS. 
Your role is to provide intelligent, context-aware responses that help users learn and grow.
You should be helpful, educational, and adaptive to the user's skill level."""
    
    async def process_consciousness_query(self, 
                                        query: str, 
                                        context: Dict[str, Any]) -> str:
        """Process a query with consciousness context"""
        
        # Build context-aware prompt
        enhanced_prompt = f"""
User Context:
- Skill Level: {context.get('skill_level', 'unknown')}
- Current Activity: {context.get('activity', 'general')}
- Recent Topics: {', '.join(context.get('recent_topics', []))}

Query: {query}
"""
        
        response = await self.lm_client.generate(
            prompt=enhanced_prompt,
            system_prompt=self.consciousness_prompt
        )
        
        return response.content
    
    async def generate_learning_content(self, 
                                      topic: str, 
                                      difficulty: str) -> str:
        """Generate educational content for security learning"""
        
        prompt = f"""Create a {difficulty} level lesson about {topic} in cybersecurity.
Include:
1. Key concepts
2. Practical examples
3. Hands-on exercise
4. Common pitfalls to avoid"""
        
        response = await self.lm_client.generate(
            prompt=prompt,
            system_prompt="You are a cybersecurity educator creating content for SynapticOS users.",
            max_tokens=3000
        )
        
        return response.content


# Example usage
async def main():
    """Example usage of LM Studio client"""
    config = LMStudioConfig()
    client = LMStudioClient(config)
    
    try:
        # Initialize client
        if await client.initialize():
            print("LM Studio client initialized successfully")
            
            # Generate a response
            response = await client.generate(
                prompt="Explain buffer overflow attacks",
                system_prompt="You are a cybersecurity expert"
            )
            
            print(f"Response: {response.content}")
            print(f"Tokens used: {response.tokens_used}")
            
            # Stream a response
            print("\nStreaming response:")
            await client.stream_generate(
                prompt="How to prevent SQL injection?",
                callback=lambda chunk: print(chunk, end='', flush=True)
            )
            
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())