#!/usr/bin/env python3
"""
SynOS Local LLM Integration Engine
Privacy-preserving AI assistance with local model deployment
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import queue

import torch
import transformers
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
    pipeline, GenerationConfig, BitsAndBytesConfig
)
import accelerate
from huggingface_hub import snapshot_download
import psutil


class ModelSize(Enum):
    TINY = "tiny"        # <1B params
    SMALL = "small"      # 1-7B params
    MEDIUM = "medium"    # 7-20B params
    LARGE = "large"      # 20B+ params


class ModelType(Enum):
    GENERAL_CHAT = "general_chat"
    CODE_ASSISTANT = "code_assistant"
    SECURITY_SPECIALIST = "security_specialist"
    INSTRUCTION_FOLLOWING = "instruction_following"


@dataclass
class ModelConfig:
    model_id: str
    model_type: ModelType
    model_size: ModelSize
    local_path: Optional[str] = None
    quantization: Optional[str] = None  # "4bit", "8bit", None
    device: str = "auto"
    max_memory: Optional[Dict[str, str]] = None
    context_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50


@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    session_id: str
    name: str
    model_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    system_prompt: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SystemResourceMonitor:
    """Monitor system resources for optimal model deployment"""

    def __init__(self):
        self.update_interval = 1.0
        self.running = False
        self.metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'gpu_memory_used': 0,
            'gpu_memory_total': 0,
            'available_memory': 0
        }

    def start_monitoring(self):
        """Start resource monitoring"""
        self.running = True
        threading.Thread(target=self._monitor_resources, daemon=True).start()

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.running = False

    def _monitor_resources(self):
        """Monitor system resources continuously"""
        while self.running:
            try:
                # CPU and RAM
                self.metrics['cpu_percent'] = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                self.metrics['memory_percent'] = memory.percent
                self.metrics['available_memory'] = memory.available

                # GPU memory (if available)
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.memory_stats()
                    self.metrics['gpu_memory_used'] = gpu_memory.get('reserved_bytes.all.current', 0)
                    self.metrics['gpu_memory_total'] = torch.cuda.get_device_properties(0).total_memory

                time.sleep(self.update_interval)

            except Exception as e:
                logging.debug(f"Resource monitoring error: {e}")

    def get_optimal_device(self) -> str:
        """Determine optimal device for model deployment"""
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB

            if gpu_memory >= 8:  # 8GB+ GPU
                return "cuda:0"
            elif gpu_memory >= 4:  # 4GB+ GPU
                return "cuda:0"

        # Fallback to CPU
        return "cpu"

    def recommend_quantization(self, model_size: ModelSize) -> Optional[str]:
        """Recommend quantization based on available resources"""
        available_gb = self.metrics['available_memory'] / (1024**3)

        if model_size == ModelSize.LARGE:
            return "4bit" if available_gb < 32 else "8bit"
        elif model_size == ModelSize.MEDIUM:
            return "4bit" if available_gb < 16 else None
        elif model_size == ModelSize.SMALL:
            return "4bit" if available_gb < 8 else None

        return None


class ModelManager:
    """Manage local LLM models and their configurations"""

    def __init__(self, models_dir: str = "/var/lib/synos/llm_models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.available_models = {
            # General Chat Models
            "microsoft/DialoGPT-small": ModelConfig(
                model_id="microsoft/DialoGPT-small",
                model_type=ModelType.GENERAL_CHAT,
                model_size=ModelSize.TINY,
                context_length=1024
            ),
            "microsoft/DialoGPT-medium": ModelConfig(
                model_id="microsoft/DialoGPT-medium",
                model_type=ModelType.GENERAL_CHAT,
                model_size=ModelSize.SMALL,
                context_length=1024
            ),

            # Code Assistant Models
            "Salesforce/codegen-350M-mono": ModelConfig(
                model_id="Salesforce/codegen-350M-mono",
                model_type=ModelType.CODE_ASSISTANT,
                model_size=ModelSize.TINY,
                context_length=2048
            ),
            "Salesforce/codegen-2B-mono": ModelConfig(
                model_id="Salesforce/codegen-2B-mono",
                model_type=ModelType.CODE_ASSISTANT,
                model_size=ModelSize.SMALL,
                context_length=2048
            ),

            # Instruction Following Models
            "microsoft/DialoGPT-large": ModelConfig(
                model_id="microsoft/DialoGPT-large",
                model_type=ModelType.INSTRUCTION_FOLLOWING,
                model_size=ModelSize.SMALL,
                context_length=1024
            ),

            # Lightweight alternatives for resource-constrained systems
            "distilgpt2": ModelConfig(
                model_id="distilgpt2",
                model_type=ModelType.GENERAL_CHAT,
                model_size=ModelSize.TINY,
                context_length=1024
            ),
            "gpt2": ModelConfig(
                model_id="gpt2",
                model_type=ModelType.GENERAL_CHAT,
                model_size=ModelSize.TINY,
                context_length=1024
            )
        }

        self.loaded_models: Dict[str, Any] = {}
        self.resource_monitor = SystemResourceMonitor()

    def get_recommended_models(self) -> List[ModelConfig]:
        """Get models recommended for current system"""
        self.resource_monitor.start_monitoring()
        time.sleep(2)  # Let monitoring stabilize

        available_memory_gb = self.resource_monitor.metrics['available_memory'] / (1024**3)
        device = self.resource_monitor.get_optimal_device()

        recommended = []

        for model_config in self.available_models.values():
            # Estimate memory requirements
            memory_needed = self._estimate_memory_requirements(model_config)

            if memory_needed <= available_memory_gb * 0.8:  # 80% safety margin
                # Update config with optimal settings
                optimized_config = self._optimize_config(model_config, device)
                recommended.append(optimized_config)

        # Sort by preference (smaller, more efficient models first for security context)
        recommended.sort(key=lambda x: (x.model_size.value, x.model_type != ModelType.SECURITY_SPECIALIST))

        return recommended[:5]  # Top 5 recommendations

    def _estimate_memory_requirements(self, config: ModelConfig) -> float:
        """Estimate memory requirements in GB"""
        size_estimates = {
            ModelSize.TINY: 1,
            ModelSize.SMALL: 4,
            ModelSize.MEDIUM: 12,
            ModelSize.LARGE: 32
        }

        base_memory = size_estimates.get(config.model_size, 8)

        # Adjust for quantization
        if config.quantization == "4bit":
            base_memory *= 0.25
        elif config.quantization == "8bit":
            base_memory *= 0.5

        return base_memory

    def _optimize_config(self, config: ModelConfig, device: str) -> ModelConfig:
        """Optimize model config for current system"""
        optimized = ModelConfig(
            model_id=config.model_id,
            model_type=config.model_type,
            model_size=config.model_size,
            local_path=config.local_path,
            quantization=self.resource_monitor.recommend_quantization(config.model_size),
            device=device,
            context_length=config.context_length,
            temperature=0.7,  # Good for security analysis
            top_p=0.9,
            top_k=50
        )

        # Set device-specific optimizations
        if device.startswith("cuda"):
            optimized.max_memory = {"0": "80%"}

        return optimized

    async def download_model(self, model_id: str, progress_callback: Optional[callable] = None) -> str:
        """Download model to local storage"""
        model_path = self.models_dir / model_id.replace("/", "_")

        if model_path.exists():
            logging.info(f"Model {model_id} already exists locally")
            return str(model_path)

        logging.info(f"Downloading model {model_id}...")

        try:
            # Download model using huggingface_hub
            downloaded_path = await asyncio.to_thread(
                snapshot_download,
                repo_id=model_id,
                local_dir=str(model_path),
                local_dir_use_symlinks=False
            )

            logging.info(f"Model downloaded to {downloaded_path}")
            return downloaded_path

        except Exception as e:
            logging.error(f"Failed to download model {model_id}: {e}")
            raise

    async def load_model(self, config: ModelConfig) -> Tuple[Any, Any]:  # Returns (model, tokenizer)
        """Load model and tokenizer with optimal configuration"""
        model_key = f"{config.model_id}_{config.quantization or 'fp16'}"

        if model_key in self.loaded_models:
            logging.info(f"Using cached model {model_key}")
            return self.loaded_models[model_key]

        logging.info(f"Loading model {config.model_id}...")

        try:
            # Configure quantization if requested
            quantization_config = None
            if config.quantization == "4bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16
                )
            elif config.quantization == "8bit":
                quantization_config = BitsAndBytesConfig(load_in_8bit=True)

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                config.local_path or config.model_id,
                trust_remote_code=True
            )

            # Add pad token if missing
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Load model
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16,
                "device_map": config.device if config.device != "auto" else None
            }

            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config

            if config.max_memory:
                model_kwargs["max_memory"] = config.max_memory

            model = AutoModelForCausalLM.from_pretrained(
                config.local_path or config.model_id,
                **model_kwargs
            )

            # Cache loaded model
            self.loaded_models[model_key] = (model, tokenizer)

            logging.info(f"Model {config.model_id} loaded successfully")
            return model, tokenizer

        except Exception as e:
            logging.error(f"Failed to load model {config.model_id}: {e}")
            raise

    def get_model_info(self, model_id: str) -> Optional[ModelConfig]:
        """Get information about available model"""
        return self.available_models.get(model_id)

    def list_available_models(self, model_type: Optional[ModelType] = None) -> List[ModelConfig]:
        """List available models, optionally filtered by type"""
        models = list(self.available_models.values())

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        return models

    def unload_model(self, model_id: str):
        """Unload model from memory"""
        keys_to_remove = [k for k in self.loaded_models.keys() if k.startswith(model_id)]

        for key in keys_to_remove:
            del self.loaded_models[key]
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        logging.info(f"Unloaded model {model_id}")


class ConversationManager:
    """Manage chat sessions and conversation history"""

    def __init__(self, db_path: str = "/var/lib/synos/chat_sessions.db"):
        self.db_path = Path(db_path)
        self.active_sessions: Dict[str, ChatSession] = {}

        # Security-focused system prompts
        self.system_prompts = {
            "security_analyst": """You are a cybersecurity expert assistant integrated into SynOS, an AI-enhanced security operating system. Your role is to help with:

1. Security analysis and threat assessment
2. Penetration testing guidance (ethical and authorized only)
3. Vulnerability analysis and remediation
4. Security tool usage and configuration
5. Incident response and forensics

Always prioritize:
- Ethical use and authorized testing only
- Defensive security measures
- Educational context for security concepts
- Privacy and responsible disclosure
- Legal compliance

Respond concisely and focus on practical security guidance.""",

            "code_assistant": """You are a code analysis assistant for SynOS security operations. Help with:

1. Security-focused code review
2. Script development for security automation
3. Configuration file analysis
4. Vulnerability detection in code
5. Security best practices implementation

Focus on:
- Secure coding practices
- Vulnerability prevention
- Performance optimization
- Clear documentation
- Defensive programming techniques""",

            "general_assistant": """You are an AI assistant integrated into SynOS, an advanced security-focused Linux distribution. Help users with:

1. System administration tasks
2. Security tool usage
3. Linux commands and configuration
4. Troubleshooting and diagnostics
5. Educational cybersecurity concepts

Maintain focus on:
- Security best practices
- Educational value
- Practical solutions
- Responsible use of security tools"""
        }

        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for chat sessions"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    system_prompt TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
                )
            """)

            conn.commit()

    def create_session(self, name: str, model_id: str, system_prompt_type: str = "security_analyst") -> str:
        """Create new chat session"""
        session_id = f"session_{int(datetime.now().timestamp() * 1000)}"

        system_prompt = self.system_prompts.get(system_prompt_type, self.system_prompts["general_assistant"])

        session = ChatSession(
            session_id=session_id,
            name=name,
            model_id=model_id,
            system_prompt=system_prompt
        )

        # Add system message
        system_message = ChatMessage(
            role="system",
            content=system_prompt
        )
        session.messages.append(system_message)

        self.active_sessions[session_id] = session
        self._store_session(session)

        return session_id

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add message to chat session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )

        session = self.active_sessions[session_id]
        session.messages.append(message)
        session.updated_at = datetime.now()

        # Store in database
        self._store_message(session_id, message)

        return f"msg_{int(message.timestamp.timestamp() * 1000)}"

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Try to load from database
        return self._load_session(session_id)

    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get conversation history for session"""
        session = self.get_session(session_id)
        if session:
            return session.messages[-limit:]
        return []

    def list_sessions(self) -> List[ChatSession]:
        """List all chat sessions"""
        sessions = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT session_id, name, model_id, system_prompt,
                           created_at, updated_at, metadata
                    FROM chat_sessions
                    ORDER BY updated_at DESC
                    LIMIT 20
                """)

                for row in cursor.fetchall():
                    session = ChatSession(
                        session_id=row[0],
                        name=row[1],
                        model_id=row[2],
                        system_prompt=row[3],
                        created_at=datetime.fromisoformat(row[4]),
                        updated_at=datetime.fromisoformat(row[5]),
                        metadata=json.loads(row[6] or '{}')
                    )
                    sessions.append(session)

        except Exception as e:
            logging.error(f"Failed to list sessions: {e}")

        return sessions

    def _store_session(self, session: ChatSession):
        """Store session in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO chat_sessions
                    (session_id, name, model_id, system_prompt, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id, session.name, session.model_id,
                    session.system_prompt, session.created_at, session.updated_at,
                    json.dumps(session.metadata)
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store session: {e}")

    def _store_message(self, session_id: str, message: ChatMessage):
        """Store message in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO chat_messages
                    (session_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id, message.role, message.content,
                    message.timestamp, json.dumps(message.metadata)
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store message: {e}")

    def _load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load session from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load session
                cursor = conn.execute("""
                    SELECT session_id, name, model_id, system_prompt,
                           created_at, updated_at, metadata
                    FROM chat_sessions WHERE session_id = ?
                """, (session_id,))

                session_row = cursor.fetchone()
                if not session_row:
                    return None

                session = ChatSession(
                    session_id=session_row[0],
                    name=session_row[1],
                    model_id=session_row[2],
                    system_prompt=session_row[3],
                    created_at=datetime.fromisoformat(session_row[4]),
                    updated_at=datetime.fromisoformat(session_row[5]),
                    metadata=json.loads(session_row[6] or '{}')
                )

                # Load messages
                cursor = conn.execute("""
                    SELECT role, content, timestamp, metadata
                    FROM chat_messages WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,))

                for row in cursor.fetchall():
                    message = ChatMessage(
                        role=row[0],
                        content=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        metadata=json.loads(row[3] or '{}')
                    )
                    session.messages.append(message)

                self.active_sessions[session_id] = session
                return session

        except Exception as e:
            logging.error(f"Failed to load session: {e}")
            return None


class LocalLLMEngine:
    """Main local LLM integration engine"""

    def __init__(self):
        self.model_manager = ModelManager()
        self.conversation_manager = ConversationManager()
        self.current_model_config: Optional[ModelConfig] = None
        self.current_model: Optional[Any] = None
        self.current_tokenizer: Optional[Any] = None

        # Generation settings
        self.default_generation_config = GenerationConfig(
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            do_sample=True,
            pad_token_id=None,  # Will be set when model loads
            eos_token_id=None   # Will be set when model loads
        )

    async def initialize(self, model_id: Optional[str] = None) -> bool:
        """Initialize LLM engine with recommended model"""
        try:
            # Get recommended models
            recommended_models = self.model_manager.get_recommended_models()

            if not recommended_models:
                logging.error("No suitable models found for current system")
                return False

            # Use specified model or best recommendation
            if model_id:
                model_config = self.model_manager.get_model_info(model_id)
                if not model_config:
                    logging.error(f"Model {model_id} not found")
                    return False
            else:
                model_config = recommended_models[0]
                logging.info(f"Using recommended model: {model_config.model_id}")

            # Download model if needed
            if not model_config.local_path:
                model_config.local_path = await self.model_manager.download_model(model_config.model_id)

            # Load model
            model, tokenizer = await self.model_manager.load_model(model_config)

            self.current_model_config = model_config
            self.current_model = model
            self.current_tokenizer = tokenizer

            # Update generation config
            self.default_generation_config.pad_token_id = tokenizer.pad_token_id
            self.default_generation_config.eos_token_id = tokenizer.eos_token_id

            logging.info(f"LLM Engine initialized with {model_config.model_id}")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize LLM engine: {e}")
            return False

    async def generate_response(self, session_id: str, user_input: str) -> str:
        """Generate response for user input in chat session"""
        if not self.current_model or not self.current_tokenizer:
            return "Error: LLM not initialized. Please run initialization first."

        try:
            # Add user message to session
            self.conversation_manager.add_message(session_id, "user", user_input)

            # Get conversation history
            messages = self.conversation_manager.get_conversation_history(session_id)

            # Format conversation for model
            conversation_text = self._format_conversation(messages)

            # Generate response
            response = await self._generate_text(conversation_text)

            # Add assistant response to session
            self.conversation_manager.add_message(session_id, "assistant", response)

            return response

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logging.error(error_msg)
            return error_msg

    async def _generate_text(self, input_text: str) -> str:
        """Generate text using current model"""
        try:
            # Tokenize input
            inputs = self.current_tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=self.current_model_config.context_length - 512
            )

            # Move to device
            if self.current_model_config.device.startswith("cuda"):
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate
            with torch.no_grad():
                outputs = self.current_model.generate(
                    **inputs,
                    generation_config=self.default_generation_config,
                    pad_token_id=self.current_tokenizer.pad_token_id
                )

            # Decode response
            input_length = inputs['input_ids'].shape[1]
            generated_tokens = outputs[0][input_length:]
            response = self.current_tokenizer.decode(generated_tokens, skip_special_tokens=True)

            # Clean up response
            response = response.strip()

            return response

        except Exception as e:
            logging.error(f"Text generation failed: {e}")
            raise

    def _format_conversation(self, messages: List[ChatMessage]) -> str:
        """Format conversation history for model input"""
        formatted = ""

        for message in messages:
            if message.role == "system":
                formatted += f"System: {message.content}\n\n"
            elif message.role == "user":
                formatted += f"User: {message.content}\n\n"
            elif message.role == "assistant":
                formatted += f"Assistant: {message.content}\n\n"

        formatted += "Assistant: "
        return formatted

    async def analyze_security_query(self, query: str) -> Dict[str, Any]:
        """Analyze security-related query and provide structured response"""
        session_id = self.conversation_manager.create_session(
            "Security Analysis",
            self.current_model_config.model_id if self.current_model_config else "default",
            "security_analyst"
        )

        # Enhanced security analysis prompt
        analysis_prompt = f"""Analyze this security query and provide a structured response:

Query: {query}

Please analyze:
1. Intent: What is the user trying to accomplish?
2. Risk Level: Low/Medium/High risk assessment
3. Recommendations: Specific actionable steps
4. Tools Needed: Relevant security tools or commands
5. Considerations: Important security and legal considerations

Respond in a clear, structured format."""

        response = await self.generate_response(session_id, analysis_prompt)

        # Try to parse structured response
        analysis = {
            "query": query,
            "response": response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

        return analysis

    async def get_code_assistance(self, code_context: str, request: str) -> str:
        """Get code assistance for security-related development"""
        session_id = self.conversation_manager.create_session(
            "Code Assistant",
            self.current_model_config.model_id if self.current_model_config else "default",
            "code_assistant"
        )

        prompt = f"""Code Context:
```
{code_context}
```

Request: {request}

Please provide secure, well-documented code assistance focusing on security best practices."""

        return await self.generate_response(session_id, prompt)

    def get_system_status(self) -> Dict[str, Any]:
        """Get LLM engine system status"""
        status = {
            "initialized": self.current_model is not None,
            "current_model": self.current_model_config.model_id if self.current_model_config else None,
            "model_type": self.current_model_config.model_type.value if self.current_model_config else None,
            "device": self.current_model_config.device if self.current_model_config else None,
            "quantization": self.current_model_config.quantization if self.current_model_config else None,
            "active_sessions": len(self.conversation_manager.active_sessions),
            "resource_usage": self.model_manager.resource_monitor.metrics
        }

        return status

    def list_available_models(self) -> List[Dict[str, Any]]:
        """List available models with details"""
        models = self.model_manager.list_available_models()
        return [
            {
                "model_id": m.model_id,
                "type": m.model_type.value,
                "size": m.model_size.value,
                "context_length": m.context_length,
                "local_path": m.local_path
            }
            for m in models
        ]

    def create_chat_session(self, name: str, system_prompt_type: str = "security_analyst") -> str:
        """Create new chat session"""
        model_id = self.current_model_config.model_id if self.current_model_config else "default"
        return self.conversation_manager.create_session(name, model_id, system_prompt_type)

    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for session"""
        messages = self.conversation_manager.get_conversation_history(session_id)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
            if msg.role != "system"  # Don't expose system prompts
        ]

    async def shutdown(self):
        """Shutdown LLM engine and cleanup resources"""
        logging.info("Shutting down LLM engine...")

        # Unload current model
        if self.current_model_config:
            self.model_manager.unload_model(self.current_model_config.model_id)

        # Stop resource monitoring
        self.model_manager.resource_monitor.stop_monitoring()

        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logging.info("LLM engine shutdown complete")


async def main():
    """Example usage of Local LLM Engine"""
    logging.basicConfig(level=logging.INFO)

    engine = LocalLLMEngine()

    print("🤖 SynOS Local LLM Integration Engine")
    print("=" * 45)

    # Initialize engine
    print("🚀 Initializing LLM engine...")
    success = await engine.initialize()

    if not success:
        print("❌ Failed to initialize LLM engine")
        return

    # Show system status
    status = engine.get_system_status()
    print(f"✅ Initialized with model: {status['current_model']}")
    print(f"📱 Device: {status['device']}")
    print(f"⚡ Quantization: {status['quantization']}")

    # Create chat session
    session_id = engine.create_chat_session("Security Consultation")
    print(f"💬 Created chat session: {session_id}")

    # Example interactions
    test_queries = [
        "How do I perform a safe network scan of my local network?",
        "What are the key steps in a penetration testing methodology?",
        "Explain the difference between vulnerability scanning and penetration testing"
    ]

    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = await engine.generate_response(session_id, query)
        print(f"🤖 Assistant: {response[:200]}...")

    # Security analysis example
    print(f"\n🔍 Security Analysis Example:")
    security_query = "I want to test my web application for SQL injection vulnerabilities"
    analysis = await engine.analyze_security_query(security_query)
    print(f"📋 Analysis: {analysis['response'][:300]}...")

    # Show final status
    final_status = engine.get_system_status()
    print(f"\n📊 Sessions created: {final_status['active_sessions']}")
    print(f"💾 Memory usage: {final_status['resource_usage']['memory_percent']:.1f}%")

    # Shutdown
    await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())