#!/usr/bin/env python3
"""
SynOS Natural Language Command Interface
Advanced NLP processing for security tool control and OS functions
"""

import asyncio
import json
import logging
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum

import spacy
import nltk
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import openai


class CommandIntent(Enum):
    SCAN = "scan"
    RECONNAISSANCE = "reconnaissance"
    EXPLOIT = "exploit"
    ANALYZE = "analyze"
    MONITOR = "monitor"
    REPORT = "report"
    CONFIGURE = "configure"
    HELP = "help"
    STATUS = "status"
    UNKNOWN = "unknown"


class SecurityContext(Enum):
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    REPORTING = "reporting"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"


@dataclass
class CommandEntity:
    entity_type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class ParsedCommand:
    original_text: str
    intent: CommandIntent
    confidence: float
    entities: List[CommandEntity]
    parameters: Dict[str, Any]
    security_context: SecurityContext
    safety_level: str  # "safe", "caution", "dangerous"
    parsed_at: datetime = field(default_factory=datetime.now)


@dataclass
class CommandExecution:
    command_id: str
    parsed_command: ParsedCommand
    executed_command: str
    output: str
    success: bool
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)


class SafetyValidator:
    """Validates command safety before execution"""

    def __init__(self):
        self.dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'del\s+/s\s+.*',
            r'format\s+c:',
            r'dd\s+if=.*\s+of=/dev/',
            r'mkfs\.',
            r'fdisk.*',
            r'parted.*',
            r'shutdown\s+-h\s+now',
            r'reboot\s+--force',
            r'kill\s+-9\s+1',
            r'killall\s+-9\s+.*'
        ]

        self.caution_patterns = [
            r'sudo\s+.*',
            r'chmod\s+.*',
            r'chown\s+.*',
            r'service\s+.*\s+stop',
            r'systemctl\s+stop\s+.*',
            r'iptables\s+-F',
            r'ufw\s+disable',
            r'setenforce\s+0'
        ]

    def assess_safety(self, command: str) -> str:
        """Assess command safety level"""
        command_lower = command.lower()

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command_lower):
                return "dangerous"

        # Check for caution patterns
        for pattern in self.caution_patterns:
            if re.search(pattern, command_lower):
                return "caution"

        return "safe"

    def requires_confirmation(self, safety_level: str, intent: CommandIntent) -> bool:
        """Check if command requires user confirmation"""
        if safety_level == "dangerous":
            return True

        if safety_level == "caution" and intent in [CommandIntent.CONFIGURE, CommandIntent.EXPLOIT]:
            return True

        return False


class EntityExtractor:
    """Extract entities from natural language commands"""

    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy model not found, using basic extraction")
            self.nlp = None

        # Security-specific entity patterns
        self.security_patterns = {
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'domain': r'\b[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}\b',
            'port': r'\bport\s+(\d+)\b',
            'service': r'\b(http|https|ssh|ftp|smtp|dns|telnet|snmp|ldap)\b',
            'file_path': r'[/\\][\w\./\\-]+',
            'vulnerability': r'\b(CVE-\d{4}-\d{4,})\b',
            'network_range': r'\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b'
        }

    def extract_entities(self, text: str) -> List[CommandEntity]:
        """Extract entities from command text"""
        entities = []

        # Extract using regex patterns
        for entity_type, pattern in self.security_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(CommandEntity(
                    entity_type=entity_type,
                    value=match.group(1) if match.groups() else match.group(),
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        # Extract using spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                # Convert spaCy entity types to our types
                entity_type = self._map_spacy_entity(ent.label_)
                if entity_type:
                    entities.append(CommandEntity(
                        entity_type=entity_type,
                        value=ent.text,
                        confidence=0.8,
                        start_pos=ent.start_char,
                        end_pos=ent.end_char
                    ))

        return entities

    def _map_spacy_entity(self, spacy_label: str) -> Optional[str]:
        """Map spaCy entity labels to our entity types"""
        mapping = {
            'ORG': 'organization',
            'PERSON': 'person',
            'GPE': 'location',
            'CARDINAL': 'number',
            'TIME': 'time',
            'DATE': 'date'
        }
        return mapping.get(spacy_label)


class IntentClassifier:
    """Classify user intent from natural language"""

    def __init__(self):
        self.intent_keywords = {
            CommandIntent.SCAN: [
                'scan', 'nmap', 'check', 'discover', 'enumerate', 'probe',
                'port scan', 'vulnerability scan', 'network scan'
            ],
            CommandIntent.RECONNAISSANCE: [
                'recon', 'reconnaissance', 'gather', 'collect', 'osint',
                'information gathering', 'footprinting', 'enumerate'
            ],
            CommandIntent.EXPLOIT: [
                'exploit', 'attack', 'penetrate', 'metasploit', 'payload',
                'shell', 'backdoor', 'compromise'
            ],
            CommandIntent.ANALYZE: [
                'analyze', 'examine', 'investigate', 'correlate', 'review',
                'forensics', 'evidence', 'timeline'
            ],
            CommandIntent.MONITOR: [
                'monitor', 'watch', 'track', 'observe', 'tail',
                'real-time', 'alerts', 'logs'
            ],
            CommandIntent.REPORT: [
                'report', 'generate', 'export', 'summary', 'document',
                'findings', 'results'
            ],
            CommandIntent.CONFIGURE: [
                'configure', 'setup', 'install', 'enable', 'disable',
                'settings', 'config'
            ],
            CommandIntent.STATUS: [
                'status', 'state', 'running', 'active', 'health'
            ],
            CommandIntent.HELP: [
                'help', 'how', 'what', 'explain', 'manual', 'documentation'
            ]
        }

        # Load transformer model for intent classification
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        except Exception as e:
            logging.warning(f"Could not load transformer model: {e}")
            self.classifier = None

    def classify_intent(self, text: str) -> Tuple[CommandIntent, float]:
        """Classify the intent of a command"""
        text_lower = text.lower()

        # Use transformer model if available
        if self.classifier:
            try:
                intent_labels = [intent.value for intent in CommandIntent if intent != CommandIntent.UNKNOWN]
                result = self.classifier(text, intent_labels)

                best_intent = result['labels'][0]
                confidence = result['scores'][0]

                return CommandIntent(best_intent), confidence
            except Exception as e:
                logging.debug(f"Transformer classification failed: {e}")

        # Fallback to keyword-based classification
        best_intent = CommandIntent.UNKNOWN
        best_score = 0.0

        for intent, keywords in self.intent_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight longer keywords more heavily
                    score += len(keyword.split()) / len(keywords)

            if score > best_score:
                best_score = score
                best_intent = intent

        confidence = min(best_score * 2, 1.0)  # Scale to 0-1
        return best_intent, confidence


class ContextManager:
    """Manage security assessment context"""

    def __init__(self):
        self.current_context = SecurityContext.MAINTENANCE
        self.context_history: List[Tuple[SecurityContext, datetime]] = []
        self.active_targets: List[str] = []
        self.session_metadata: Dict[str, Any] = {}

    def update_context(self, new_context: SecurityContext):
        """Update current security context"""
        if new_context != self.current_context:
            self.context_history.append((self.current_context, datetime.now()))
            self.current_context = new_context
            logging.info(f"Context changed to: {new_context.value}")

    def infer_context(self, intent: CommandIntent, entities: List[CommandEntity]) -> SecurityContext:
        """Infer security context from command intent and entities"""

        # Map intents to likely contexts
        intent_context_map = {
            CommandIntent.RECONNAISSANCE: SecurityContext.RECONNAISSANCE,
            CommandIntent.SCAN: SecurityContext.VULNERABILITY_ASSESSMENT,
            CommandIntent.EXPLOIT: SecurityContext.EXPLOITATION,
            CommandIntent.ANALYZE: SecurityContext.POST_EXPLOITATION,
            CommandIntent.REPORT: SecurityContext.REPORTING,
            CommandIntent.MONITOR: SecurityContext.MONITORING
        }

        inferred_context = intent_context_map.get(intent, self.current_context)

        # Check if we have active targets (indicates active assessment)
        if self.active_targets and inferred_context == SecurityContext.MAINTENANCE:
            inferred_context = SecurityContext.VULNERABILITY_ASSESSMENT

        return inferred_context

    def add_target(self, target: str):
        """Add target to active assessment"""
        if target not in self.active_targets:
            self.active_targets.append(target)

    def remove_target(self, target: str):
        """Remove target from active assessment"""
        if target in self.active_targets:
            self.active_targets.remove(target)


class CommandMapper:
    """Map natural language to actual system commands"""

    def __init__(self):
        self.command_templates = {
            # Reconnaissance commands
            (CommandIntent.RECONNAISSANCE, 'domain'): [
                "synos-security recon --target {domain} --passive",
                "whois {domain}",
                "dig {domain} any"
            ],
            (CommandIntent.RECONNAISSANCE, 'ip_address'): [
                "synos-security recon --target {ip_address}",
                "nmap -sn {ip_address}"
            ],

            # Scanning commands
            (CommandIntent.SCAN, 'ip_address'): [
                "synos-security scan --target {ip_address}",
                "nmap -sV -sC {ip_address}"
            ],
            (CommandIntent.SCAN, 'network_range'): [
                "synos-security scan --target {network_range} --policy adaptive",
                "nmap -sn {network_range}"
            ],

            # Monitoring commands
            (CommandIntent.MONITOR, 'service'): [
                "synos-security monitor --alerts",
                "systemctl status {service}"
            ],

            # Status commands
            (CommandIntent.STATUS, None): [
                "synos-security status",
                "systemctl status synos-security.target"
            ],

            # Analysis commands
            (CommandIntent.ANALYZE, 'file_path'): [
                "synos-security correlate --import-file {file_path}",
                "file {file_path}",
                "strings {file_path}"
            ]
        }

    def map_to_commands(self, parsed_command: ParsedCommand) -> List[str]:
        """Map parsed command to executable system commands"""
        commands = []

        # Find relevant entities for this intent
        relevant_entities = self._get_relevant_entities(parsed_command)

        for entity in relevant_entities:
            key = (parsed_command.intent, entity.entity_type)
            if key in self.command_templates:
                templates = self.command_templates[key]
                for template in templates:
                    try:
                        command = template.format(**{entity.entity_type: entity.value})
                        commands.append(command)
                    except KeyError:
                        continue

        # Fallback to generic commands if no specific mapping found
        if not commands:
            commands = self._get_generic_commands(parsed_command)

        return commands

    def _get_relevant_entities(self, parsed_command: ParsedCommand) -> List[CommandEntity]:
        """Get entities relevant to the command intent"""
        relevant_types = {
            CommandIntent.RECONNAISSANCE: ['domain', 'ip_address', 'organization'],
            CommandIntent.SCAN: ['ip_address', 'network_range', 'domain', 'port'],
            CommandIntent.EXPLOIT: ['ip_address', 'port', 'service', 'vulnerability'],
            CommandIntent.MONITOR: ['service', 'file_path'],
            CommandIntent.ANALYZE: ['file_path', 'vulnerability']
        }

        intent_types = relevant_types.get(parsed_command.intent, [])
        return [e for e in parsed_command.entities if e.entity_type in intent_types]

    def _get_generic_commands(self, parsed_command: ParsedCommand) -> List[str]:
        """Generate generic commands based on intent"""
        generic_commands = {
            CommandIntent.STATUS: ["synos-security status"],
            CommandIntent.HELP: ["synos-security --help"],
            CommandIntent.MONITOR: ["synos-security monitor --alerts"],
            CommandIntent.REPORT: ["synos-security status"]
        }

        return generic_commands.get(parsed_command.intent, ["echo 'Command not recognized'"])


class NLPCommandProcessor:
    """Main NLP command processing engine"""

    def __init__(self, db_path: str = "/var/lib/synos/nlp_commands.db"):
        self.db_path = Path(db_path)

        # Initialize components
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()
        self.command_mapper = CommandMapper()
        self.safety_validator = SafetyValidator()

        # Command history
        self.command_history: List[CommandExecution] = []

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for command history"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT UNIQUE NOT NULL,
                    original_text TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    entities TEXT NOT NULL,
                    security_context TEXT NOT NULL,
                    safety_level TEXT NOT NULL,
                    executed_command TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    output TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    async def process_command(self, text: str, user_confirmation: bool = True) -> CommandExecution:
        """Process natural language command"""

        # Parse the command
        parsed_command = await self._parse_command(text)

        # Update context
        new_context = self.context_manager.infer_context(
            parsed_command.intent,
            parsed_command.entities
        )
        self.context_manager.update_context(new_context)
        parsed_command.security_context = new_context

        # Map to system commands
        system_commands = self.command_mapper.map_to_commands(parsed_command)

        if not system_commands:
            return self._create_error_execution(parsed_command, "No executable command found")

        # Take the first/best command
        selected_command = system_commands[0]

        # Validate safety
        safety_level = self.safety_validator.assess_safety(selected_command)
        parsed_command.safety_level = safety_level

        # Check if confirmation is required
        if self.safety_validator.requires_confirmation(safety_level, parsed_command.intent):
            if not user_confirmation:
                return self._create_error_execution(
                    parsed_command,
                    f"Command requires confirmation due to {safety_level} safety level"
                )

        # Execute the command
        execution = await self._execute_command(parsed_command, selected_command)

        # Store in database
        await self._store_execution(execution)

        # Add to history
        self.command_history.append(execution)

        return execution

    async def _parse_command(self, text: str) -> ParsedCommand:
        """Parse natural language command"""

        # Classify intent
        intent, confidence = self.intent_classifier.classify_intent(text)

        # Extract entities
        entities = self.entity_extractor.extract_entities(text)

        # Extract parameters (simple key-value extraction)
        parameters = self._extract_parameters(text, entities)

        return ParsedCommand(
            original_text=text,
            intent=intent,
            confidence=confidence,
            entities=entities,
            parameters=parameters,
            security_context=self.context_manager.current_context,
            safety_level="unknown"
        )

    def _extract_parameters(self, text: str, entities: List[CommandEntity]) -> Dict[str, Any]:
        """Extract command parameters from text"""
        parameters = {}

        # Extract common parameters
        if re.search(r'\b(passive|stealth)\b', text, re.IGNORECASE):
            parameters['mode'] = 'passive'

        if re.search(r'\b(aggressive|active)\b', text, re.IGNORECASE):
            parameters['mode'] = 'aggressive'

        if re.search(r'\b(quick|fast)\b', text, re.IGNORECASE):
            parameters['speed'] = 'fast'

        if re.search(r'\b(detailed|comprehensive)\b', text, re.IGNORECASE):
            parameters['detail'] = 'high'

        # Extract output format
        format_match = re.search(r'\b(json|xml|txt|html|pdf)\b', text, re.IGNORECASE)
        if format_match:
            parameters['format'] = format_match.group().lower()

        return parameters

    async def _execute_command(self, parsed_command: ParsedCommand, command: str) -> CommandExecution:
        """Execute system command"""
        command_id = f"nlp_{int(datetime.now().timestamp() * 1000)}"
        start_time = datetime.now()

        try:
            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return CommandExecution(
                command_id=command_id,
                parsed_command=parsed_command,
                executed_command=command,
                output=result.stdout + result.stderr,
                success=result.returncode == 0,
                execution_time=execution_time
            )

        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            return CommandExecution(
                command_id=command_id,
                parsed_command=parsed_command,
                executed_command=command,
                output="Command timed out after 5 minutes",
                success=False,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return CommandExecution(
                command_id=command_id,
                parsed_command=parsed_command,
                executed_command=command,
                output=f"Execution error: {str(e)}",
                success=False,
                execution_time=execution_time
            )

    def _create_error_execution(self, parsed_command: ParsedCommand, error_message: str) -> CommandExecution:
        """Create error execution result"""
        return CommandExecution(
            command_id=f"error_{int(datetime.now().timestamp() * 1000)}",
            parsed_command=parsed_command,
            executed_command="",
            output=error_message,
            success=False,
            execution_time=0.0
        )

    async def _store_execution(self, execution: CommandExecution):
        """Store command execution in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO command_history
                    (command_id, original_text, intent, confidence, entities,
                     security_context, safety_level, executed_command, success,
                     execution_time, output, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.command_id,
                    execution.parsed_command.original_text,
                    execution.parsed_command.intent.value,
                    execution.parsed_command.confidence,
                    json.dumps([{
                        'type': e.entity_type,
                        'value': e.value,
                        'confidence': e.confidence
                    } for e in execution.parsed_command.entities]),
                    execution.parsed_command.security_context.value,
                    execution.parsed_command.safety_level,
                    execution.executed_command,
                    execution.success,
                    execution.execution_time,
                    execution.output,
                    execution.timestamp
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store execution: {e}")

    def get_command_suggestions(self, partial_text: str) -> List[str]:
        """Get command suggestions based on partial input"""
        suggestions = []

        # Intent-based suggestions
        text_lower = partial_text.lower()

        if any(word in text_lower for word in ['scan', 'check']):
            suggestions.extend([
                "scan my network for vulnerabilities",
                "scan 192.168.1.0/24 for open ports",
                "check if port 80 is open on example.com"
            ])

        if any(word in text_lower for word in ['recon', 'gather']):
            suggestions.extend([
                "gather information about example.com",
                "run reconnaissance on target network",
                "collect OSINT data for domain"
            ])

        if any(word in text_lower for word in ['status', 'show']):
            suggestions.extend([
                "show system status",
                "status of security services",
                "show recent alerts"
            ])

        return suggestions[:10]  # Return top 10 suggestions

    def get_recent_commands(self, limit: int = 10) -> List[CommandExecution]:
        """Get recent command executions"""
        return self.command_history[-limit:]

    def get_context_info(self) -> Dict[str, Any]:
        """Get current context information"""
        return {
            'current_context': self.context_manager.current_context.value,
            'active_targets': self.context_manager.active_targets,
            'context_history': [
                {'context': ctx.value, 'timestamp': ts.isoformat()}
                for ctx, ts in self.context_manager.context_history[-5:]
            ]
        }


async def main():
    """Example usage of NLP Command Processor"""
    logging.basicConfig(level=logging.INFO)

    processor = NLPCommandProcessor()

    # Example commands
    test_commands = [
        "scan my network for vulnerabilities",
        "gather information about google.com",
        "show me the status of security services",
        "run reconnaissance on 192.168.1.0/24",
        "analyze the log file /var/log/auth.log",
        "monitor network activity in real-time"
    ]

    print("🗣️ SynOS Natural Language Command Interface")
    print("=" * 50)

    for command in test_commands:
        print(f"\n💬 Command: '{command}'")

        execution = await processor.process_command(command, user_confirmation=True)

        print(f"🎯 Intent: {execution.parsed_command.intent.value}")
        print(f"🎲 Confidence: {execution.parsed_command.confidence:.2f}")
        print(f"📍 Context: {execution.parsed_command.security_context.value}")
        print(f"🔒 Safety: {execution.parsed_command.safety_level}")
        print(f"⚡ Executed: {execution.executed_command}")
        print(f"✅ Success: {execution.success}")

        if execution.parsed_command.entities:
            print("🏷️ Entities:")
            for entity in execution.parsed_command.entities:
                print(f"   - {entity.entity_type}: {entity.value}")

    # Show context info
    context_info = processor.get_context_info()
    print(f"\n📊 Current Context: {context_info['current_context']}")
    print(f"🎯 Active Targets: {context_info['active_targets']}")


if __name__ == "__main__":
    asyncio.run(main())