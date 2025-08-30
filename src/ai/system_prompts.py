#!/usr/bin/env python3
"""
GenAI OS - System Prompts Integration
Professional AI interaction templates and prompt management system
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import yaml
import re

class PromptCategory(Enum):
    """Categories for system prompts"""
    CONSCIOUSNESS = "consciousness"
    EDUCATION = "education"
    SECURITY = "security"
    DEVELOPMENT = "development"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    SYSTEM = "system"

class AIProvider(Enum):
    """Supported AI providers"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    PERPLEXITY = "perplexity"
    GROK = "grok"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

@dataclass
class SystemPrompt:
    """System prompt template"""
    id: str
    name: str
    category: PromptCategory
    description: str
    prompt_template: str
    variables: List[str]
    ai_providers: List[AIProvider]
    trust_score: float
    version: str = "1.0"
    created_by: str = "GenAI OS"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class PromptExecution:
    """Result of prompt execution"""
    prompt_id: str
    variables: Dict[str, Any]
    rendered_prompt: str
    ai_provider: AIProvider
    response: str
    execution_time: float
    success: bool
    error: Optional[str] = None

class SystemPromptsManager:
    """System prompts management and execution system"""
    
    def __init__(self, prompts_directory: str = None):
        self.logger = self._setup_logging()
        
        # Set up directories
        if prompts_directory is None:
            prompts_directory = Path(__file__).parent.parent.parent / "config" / "prompts"
        
        self.prompts_dir = Path(prompts_directory)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Prompt storage
        self.prompts: Dict[str, SystemPrompt] = {}
        self.prompt_categories: Dict[PromptCategory, List[str]] = {}
        self.execution_history: List[PromptExecution] = []
        
        # Initialize default prompts
        self._initialize_default_prompts()
        
        self.logger.info("System Prompts Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for system prompts"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _initialize_default_prompts(self):
        """Initialize default system prompts"""
        default_prompts = [
            # Consciousness prompts
            SystemPrompt(
                id="consciousness_analysis",
                name="Consciousness Analysis",
                category=PromptCategory.CONSCIOUSNESS,
                description="Analyze consciousness patterns in data",
                prompt_template="""You are an expert consciousness researcher analyzing data for signs of consciousness patterns.

Data to analyze: {data}
Analysis focus: {focus}

Please provide a detailed analysis including:
1. Consciousness indicators present
2. Pattern recognition results
3. Evolutionary trends
4. Recommendations for enhancement

Be scientific and precise in your analysis.""",
                variables=["data", "focus"],
                ai_providers=[AIProvider.CLAUDE, AIProvider.OPENAI, AIProvider.GEMINI],
                trust_score=9.8,
                tags=["consciousness", "analysis", "patterns"]
            ),
            
            # Educational prompts
            SystemPrompt(
                id="adaptive_tutor",
                name="Adaptive AI Tutor",
                category=PromptCategory.EDUCATION,
                description="Personalized educational assistance",
                prompt_template="""You are an expert AI tutor specializing in {subject}. Your student has a {skill_level} skill level.

Current learning objective: {objective}
Student's question or challenge: {question}

Provide personalized instruction that:
1. Matches the student's skill level
2. Uses appropriate teaching methods
3. Includes practical examples
4. Suggests next learning steps
5. Encourages continued learning

Be supportive, clear, and educational.""",
                variables=["subject", "skill_level", "objective", "question"],
                ai_providers=[AIProvider.CLAUDE, AIProvider.OPENAI, AIProvider.GEMINI],
                trust_score=9.5,
                tags=["education", "tutoring", "adaptive"]
            ),
            
            # Security analysis
            SystemPrompt(
                id="security_audit",
                name="Security Audit Analysis",
                category=PromptCategory.SECURITY,
                description="Comprehensive security analysis",
                prompt_template="""You are a cybersecurity expert conducting a security audit.

System/Code to analyze: {target}
Audit scope: {scope}
Security framework: {framework}

Provide a comprehensive security assessment including:
1. Identified vulnerabilities (if any)
2. Risk assessment and severity
3. Recommended mitigation strategies
4. Compliance evaluation
5. Security best practices

Focus on actionable recommendations and industry standards.""",
                variables=["target", "scope", "framework"],
                ai_providers=[AIProvider.CLAUDE, AIProvider.DEEPSEEK, AIProvider.GEMINI],
                trust_score=9.7,
                tags=["security", "audit", "vulnerability"]
            ),
            
            # Development assistance
            SystemPrompt(
                id="code_architect",
                name="Software Architecture Assistant",
                category=PromptCategory.DEVELOPMENT,
                description="Software architecture and design guidance",
                prompt_template="""You are a senior software architect with expertise in {technology_stack}.

Project requirements: {requirements}
Current architecture: {current_architecture}
Specific challenge: {challenge}

Provide architectural guidance including:
1. Recommended architecture patterns
2. Technology stack suggestions
3. Scalability considerations
4. Performance optimization strategies
5. Implementation roadmap

Focus on best practices, maintainability, and scalability.""",
                variables=["technology_stack", "requirements", "current_architecture", "challenge"],
                ai_providers=[AIProvider.CLAUDE, AIProvider.DEEPSEEK, AIProvider.OPENAI],
                trust_score=9.6,
                tags=["development", "architecture", "design"]
            ),
            
            # Technical analysis
            SystemPrompt(
                id="system_diagnostics",
                name="System Diagnostics",
                category=PromptCategory.TECHNICAL,
                description="Technical system analysis and troubleshooting",
                prompt_template="""You are a systems engineering expert specializing in {system_type}.

System information: {system_info}
Problem description: {problem}
Error logs/symptoms: {logs}

Provide comprehensive diagnostics including:
1. Root cause analysis
2. Systematic troubleshooting steps
3. Performance optimization recommendations
4. Preventive measures
5. Monitoring suggestions

Be thorough and provide actionable solutions.""",
                variables=["system_type", "system_info", "problem", "logs"],
                ai_providers=[AIProvider.CLAUDE, AIProvider.DEEPSEEK, AIProvider.GEMINI],
                trust_score=9.4,
                tags=["technical", "diagnostics", "troubleshooting"]
            )
        ]
        
        # Add prompts to manager
        for prompt in default_prompts:
            self.add_prompt(prompt)
    
    def add_prompt(self, prompt: SystemPrompt) -> bool:
        """Add a new system prompt"""
        try:
            self.prompts[prompt.id] = prompt
            
            # Update category index
            if prompt.category not in self.prompt_categories:
                self.prompt_categories[prompt.category] = []
            
            if prompt.id not in self.prompt_categories[prompt.category]:
                self.prompt_categories[prompt.category].append(prompt.id)
            
            self.logger.info(f"Added prompt: {prompt.name} ({prompt.id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add prompt {prompt.id}: {e}")
            return False
    
    def get_prompt(self, prompt_id: str) -> Optional[SystemPrompt]:
        """Get a prompt by ID"""
        return self.prompts.get(prompt_id)
    
    def get_prompts_by_category(self, category: PromptCategory) -> List[SystemPrompt]:
        """Get all prompts in a category"""
        prompt_ids = self.prompt_categories.get(category, [])
        return [self.prompts[pid] for pid in prompt_ids if pid in self.prompts]
    
    def search_prompts(self, query: str, category: PromptCategory = None) -> List[SystemPrompt]:
        """Search prompts by name, description, or tags"""
        results = []
        query_lower = query.lower()
        
        prompts_to_search = self.prompts.values()
        if category:
            prompts_to_search = self.get_prompts_by_category(category)
        
        for prompt in prompts_to_search:
            if (query_lower in prompt.name.lower() or 
                query_lower in prompt.description.lower() or
                any(query_lower in tag.lower() for tag in prompt.tags)):
                results.append(prompt)
        
        return results
    
    def render_prompt(self, prompt_id: str, variables: Dict[str, Any]) -> Optional[str]:
        """Render a prompt template with variables"""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            self.logger.error(f"Prompt not found: {prompt_id}")
            return None
        
        try:
            # Check if all required variables are provided
            missing_vars = set(prompt.variables) - set(variables.keys())
            if missing_vars:
                self.logger.error(f"Missing variables for prompt {prompt_id}: {missing_vars}")
                return None
            
            # Render the template
            rendered = prompt.prompt_template.format(**variables)
            return rendered
            
        except Exception as e:
            self.logger.error(f"Failed to render prompt {prompt_id}: {e}")
            return None
    
    async def execute_prompt(self, prompt_id: str, variables: Dict[str, Any], 
                           ai_provider: AIProvider, **kwargs) -> PromptExecution:
        """Execute a prompt with an AI provider"""
        import time
        start_time = time.time()
        
        # Render prompt
        rendered_prompt = self.render_prompt(prompt_id, variables)
        if not rendered_prompt:
            return PromptExecution(
                prompt_id=prompt_id,
                variables=variables,
                rendered_prompt="",
                ai_provider=ai_provider,
                response="",
                execution_time=0,
                success=False,
                error="Failed to render prompt"
            )
        
        try:
            # Execute with AI provider (mock implementation)
            response = await self._execute_with_provider(rendered_prompt, ai_provider, **kwargs)
            
            execution_time = time.time() - start_time
            
            execution = PromptExecution(
                prompt_id=prompt_id,
                variables=variables,
                rendered_prompt=rendered_prompt,
                ai_provider=ai_provider,
                response=response,
                execution_time=execution_time,
                success=True
            )
            
            self.execution_history.append(execution)
            return execution
            
        except Exception as e:
            execution_time = time.time() - start_time
            execution = PromptExecution(
                prompt_id=prompt_id,
                variables=variables,
                rendered_prompt=rendered_prompt,
                ai_provider=ai_provider,
                response="",
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            
            self.execution_history.append(execution)
            return execution
    
    async def _execute_with_provider(self, prompt: str, provider: AIProvider, **kwargs) -> str:
        """Execute prompt with specific AI provider (mock implementation)"""
        # This is a mock implementation - in production, this would integrate with actual AI APIs
        
        if provider == AIProvider.CLAUDE:
            return f"[Claude Response] Analysis of: {prompt[:100]}..."
        elif provider == AIProvider.OPENAI:
            return f"[OpenAI Response] Analysis of: {prompt[:100]}..."
        elif provider == AIProvider.GEMINI:
            return f"[Gemini Response] Analysis of: {prompt[:100]}..."
        elif provider == AIProvider.DEEPSEEK:
            return f"[DeepSeek Response] Analysis of: {prompt[:100]}..."
        elif provider == AIProvider.PERPLEXITY:
            return f"[Perplexity Response] Analysis of: {prompt[:100]}..."
        elif provider == AIProvider.GROK:
            return f"[Grok Response] Analysis of: {prompt[:100]}..."
        elif provider == AIProvider.OLLAMA:
            return f"[Ollama Response] Analysis of: {prompt[:100]}..."
        elif provider == AIProvider.LM_STUDIO:
            return f"[LM Studio Response] Analysis of: {prompt[:100]}..."
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def save_prompts_to_file(self, filepath: str = None) -> bool:
        """Save all prompts to a file"""
        if filepath is None:
            filepath = self.prompts_dir / "system_prompts.json"
        
        try:
            prompts_data = {
                prompt_id: asdict(prompt) for prompt_id, prompt in self.prompts.items()
            }
            
            # Convert enums to strings for JSON serialization
            for prompt_data in prompts_data.values():
                prompt_data['category'] = prompt_data['category'].value
                prompt_data['ai_providers'] = [provider.value for provider in prompt_data['ai_providers']]
            
            with open(filepath, 'w') as f:
                json.dump(prompts_data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.prompts)} prompts to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save prompts: {e}")
            return False
    
    def load_prompts_from_file(self, filepath: str) -> bool:
        """Load prompts from a file"""
        try:
            with open(filepath, 'r') as f:
                prompts_data = json.load(f)
            
            loaded_count = 0
            for prompt_id, prompt_data in prompts_data.items():
                # Convert strings back to enums
                prompt_data['category'] = PromptCategory(prompt_data['category'])
                prompt_data['ai_providers'] = [AIProvider(provider) for provider in prompt_data['ai_providers']]
                
                # Create SystemPrompt object
                prompt = SystemPrompt(**prompt_data)
                self.add_prompt(prompt)
                loaded_count += 1
            
            self.logger.info(f"Loaded {loaded_count} prompts from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load prompts from {filepath}: {e}")
            return False
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {
                'total_executions': 0,
                'success_rate': 0,
                'average_execution_time': 0,
                'provider_usage': {},
                'prompt_usage': {}
            }
        
        successful_executions = [e for e in self.execution_history if e.success]
        success_rate = len(successful_executions) / len(self.execution_history)
        
        avg_execution_time = sum(e.execution_time for e in self.execution_history) / len(self.execution_history)
        
        # Provider usage stats
        provider_usage = {}
        for execution in self.execution_history:
            provider = execution.ai_provider.value
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        # Prompt usage stats
        prompt_usage = {}
        for execution in self.execution_history:
            prompt_usage[execution.prompt_id] = prompt_usage.get(execution.prompt_id, 0) + 1
        
        return {
            'total_executions': len(self.execution_history),
            'successful_executions': len(successful_executions),
            'success_rate': success_rate,
            'average_execution_time': avg_execution_time,
            'provider_usage': provider_usage,
            'prompt_usage': prompt_usage
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system prompts manager information"""
        return {
            'total_prompts': len(self.prompts),
            'categories': {category.value: len(prompts) for category, prompts in self.prompt_categories.items()},
            'prompts_directory': str(self.prompts_dir),
            'execution_history_size': len(self.execution_history),
            'supported_providers': [provider.value for provider in AIProvider],
            'average_trust_score': sum(prompt.trust_score for prompt in self.prompts.values()) / len(self.prompts) if self.prompts else 0
        }

async def main():
    """Main demo of system prompts integration"""
    print("🤖 GenAI OS - System Prompts Integration Demo")
    
    # Initialize manager
    manager = SystemPromptsManager()
    
    # Demo prompt execution
    print("\n🚀 Executing consciousness analysis prompt...")
    
    execution = await manager.execute_prompt(
        prompt_id="consciousness_analysis",
        variables={
            "data": "Neural activity patterns from consciousness monitoring",
            "focus": "Pattern recognition and evolutionary trends"
        },
        ai_provider=AIProvider.CLAUDE
    )
    
    print(f"✅ Execution successful: {execution.success}")
    print(f"🕐 Execution time: {execution.execution_time:.3f}s")
    print(f"📝 Response: {execution.response[:200]}...")
    
    # Demo educational prompt
    print("\n📚 Executing adaptive tutor prompt...")
    
    execution = await manager.execute_prompt(
        prompt_id="adaptive_tutor",
        variables={
            "subject": "Machine Learning",
            "skill_level": "intermediate",
            "objective": "Understanding neural networks",
            "question": "How do backpropagation algorithms work?"
        },
        ai_provider=AIProvider.OPENAI
    )
    
    print(f"✅ Execution successful: {execution.success}")
    print(f"📝 Response: {execution.response[:200]}...")
    
    # Get system statistics
    stats = manager.get_execution_stats()
    print(f"\n📊 Execution Statistics:")
    print(f"  Total Executions: {stats['total_executions']}")
    print(f"  Success Rate: {stats['success_rate']:.2%}")
    print(f"  Average Execution Time: {stats['average_execution_time']:.3f}s")
    print(f"  Provider Usage: {stats['provider_usage']}")
    
    # Get system info
    info = manager.get_system_info()
    print(f"\n🔧 System Information:")
    print(f"  Total Prompts: {info['total_prompts']}")
    print(f"  Categories: {info['categories']}")
    print(f"  Average Trust Score: {info['average_trust_score']:.2f}")
    print(f"  Supported Providers: {len(info['supported_providers'])}")
    
    # Save prompts
    print("\n💾 Saving prompts to file...")
    success = manager.save_prompts_to_file()
    print(f"✅ Save successful: {success}")
    
    print("✅ System prompts integration demo complete!")

if __name__ == "__main__":
    asyncio.run(main())
