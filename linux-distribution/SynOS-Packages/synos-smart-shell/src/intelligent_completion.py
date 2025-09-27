#!/usr/bin/env python3
"""
SynOS Intelligent Command Completion Engine
AI-powered shell suggestions based on context and security best practices
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import difflib

import readline
import rlcompleter


class CompletionType(Enum):
    COMMAND = "command"
    ARGUMENT = "argument"
    FILE_PATH = "file_path"
    OPTION = "option"
    VALUE = "value"
    SECURITY_TOOL = "security_tool"


class ContextType(Enum):
    SHELL = "shell"
    SECURITY_ANALYSIS = "security_analysis"
    PENETRATION_TESTING = "penetration_testing"
    INCIDENT_RESPONSE = "incident_response"
    SYSTEM_ADMINISTRATION = "system_administration"


@dataclass
class CompletionSuggestion:
    text: str
    completion_type: CompletionType
    description: str
    confidence: float
    context_relevance: float
    security_score: float
    usage_frequency: int = 0
    last_used: Optional[datetime] = None


@dataclass
class CommandContext:
    current_command: str
    partial_input: str
    cursor_position: int
    working_directory: str
    environment_vars: Dict[str, str]
    recent_commands: List[str]
    active_processes: List[str]
    security_context: ContextType
    timestamp: datetime = field(default_factory=datetime.now)


class SecurityToolRegistry:
    """Registry of security tools with intelligent completions"""

    def __init__(self):
        self.security_tools = {
            # Network Security Tools
            'nmap': {
                'description': 'Network exploration and security auditing',
                'common_options': [
                    '-sS', '-sT', '-sU', '-sV', '-sC', '-O', '-A',
                    '-p', '-P0', '-n', '-T4', '-oA', '-oN', '-oX'
                ],
                'option_descriptions': {
                    '-sS': 'SYN stealth scan',
                    '-sT': 'TCP connect scan',
                    '-sU': 'UDP scan',
                    '-sV': 'Version detection',
                    '-sC': 'Default script scan',
                    '-O': 'OS detection',
                    '-A': 'Aggressive scan',
                    '-p': 'Port specification',
                    '-T4': 'Aggressive timing',
                    '-oA': 'Output in all formats'
                },
                'examples': [
                    'nmap -sS -sV -O 192.168.1.0/24',
                    'nmap -sC -sV target.com',
                    'nmap -p 1-65535 -sS target.com'
                ]
            },

            'synos-security': {
                'description': 'SynOS AI-enhanced security orchestrator',
                'subcommands': [
                    'recon', 'scan', 'exploit', 'correlate', 'monitor', 'anomaly', 'status'
                ],
                'subcommand_options': {
                    'recon': ['--target', '--passive', '--output'],
                    'scan': ['--target', '--policy', '--format'],
                    'exploit': ['--target', '--recommend', '--execute'],
                    'correlate': ['--import-file', '--cluster', '--report'],
                    'monitor': ['--status', '--alerts', '--acknowledge'],
                    'anomaly': ['--stats', '--train', '--false-positive']
                },
                'examples': [
                    'synos-security recon --target example.com --passive',
                    'synos-security scan --target 192.168.1.0/24 --policy adaptive',
                    'synos-security monitor --alerts'
                ]
            },

            'metasploit': {
                'description': 'Penetration testing framework',
                'common_commands': [
                    'use', 'set', 'show', 'run', 'exploit', 'search',
                    'info', 'sessions', 'background'
                ],
                'examples': [
                    'search type:exploit platform:linux',
                    'use exploit/linux/ssh/ssh_login',
                    'set RHOSTS 192.168.1.0/24'
                ]
            },

            'wireshark': {
                'description': 'Network protocol analyzer',
                'common_options': [
                    '-i', '-f', '-c', '-w', '-r', '-Y', '-T'
                ],
                'option_descriptions': {
                    '-i': 'Interface to capture',
                    '-f': 'Capture filter',
                    '-c': 'Packet count limit',
                    '-w': 'Write to file',
                    '-r': 'Read from file',
                    '-Y': 'Display filter',
                    '-T': 'Output format'
                }
            },

            'burpsuite': {
                'description': 'Web application security testing',
                'common_options': ['--project-file', '--config-file'],
                'examples': [
                    'burpsuite --project-file /path/to/project.burp'
                ]
            },

            # System Tools with Security Context
            'systemctl': {
                'description': 'systemd service controller',
                'subcommands': [
                    'start', 'stop', 'restart', 'reload', 'enable',
                    'disable', 'status', 'show', 'list-units'
                ],
                'security_services': [
                    'synos-ai-daemon', 'synos-security.target',
                    'synos-reconnaissance', 'synos-vuln-scanner',
                    'synos-behavior-monitor', 'fail2ban', 'ufw'
                ]
            },

            'journalctl': {
                'description': 'systemd journal viewer',
                'common_options': [
                    '-f', '-u', '-p', '--since', '--until', '-n', '-r'
                ],
                'security_units': [
                    'synos-ai-daemon', 'synos-security.target',
                    'ssh', 'ufw', 'fail2ban'
                ]
            }
        }

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about security tool"""
        return self.security_tools.get(tool_name)

    def get_completions_for_tool(self, tool_name: str, partial_input: str) -> List[CompletionSuggestion]:
        """Get completions specific to security tool"""
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return []

        suggestions = []

        # Complete subcommands
        if 'subcommands' in tool_info:
            for subcommand in tool_info['subcommands']:
                if subcommand.startswith(partial_input):
                    suggestions.append(CompletionSuggestion(
                        text=subcommand,
                        completion_type=CompletionType.COMMAND,
                        description=f"{tool_name} {subcommand} command",
                        confidence=0.9,
                        context_relevance=0.8,
                        security_score=0.9
                    ))

        # Complete options
        if 'common_options' in tool_info:
            for option in tool_info['common_options']:
                if option.startswith(partial_input):
                    description = tool_info.get('option_descriptions', {}).get(
                        option, f"{tool_name} option"
                    )
                    suggestions.append(CompletionSuggestion(
                        text=option,
                        completion_type=CompletionType.OPTION,
                        description=description,
                        confidence=0.8,
                        context_relevance=0.7,
                        security_score=0.8
                    ))

        return suggestions

    def suggest_examples(self, tool_name: str) -> List[str]:
        """Get example commands for tool"""
        tool_info = self.get_tool_info(tool_name)
        if tool_info and 'examples' in tool_info:
            return tool_info['examples']
        return []


class CommandHistoryAnalyzer:
    """Analyze command history for intelligent suggestions"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.command_patterns: Dict[str, int] = {}
        self.context_commands: Dict[ContextType, List[str]] = {}
        self._init_database()
        self._load_history()

    def _init_database(self):
        """Initialize database for command history"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    context TEXT NOT NULL,
                    working_dir TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS completion_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    completion_text TEXT NOT NULL,
                    context TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(completion_text, context)
                )
            """)

            conn.commit()

    def _load_history(self):
        """Load command history and build patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load recent successful commands
                cursor = conn.execute("""
                    SELECT command, context, COUNT(*) as frequency
                    FROM command_history
                    WHERE success = 1 AND timestamp > datetime('now', '-30 days')
                    GROUP BY command, context
                    ORDER BY frequency DESC
                    LIMIT 1000
                """)

                for row in cursor.fetchall():
                    command, context, frequency = row
                    self.command_patterns[command] = frequency

                    # Group by context
                    context_type = ContextType(context) if context in [c.value for c in ContextType] else ContextType.SHELL
                    if context_type not in self.context_commands:
                        self.context_commands[context_type] = []
                    self.context_commands[context_type].append(command)

        except Exception as e:
            logging.debug(f"Could not load command history: {e}")

    def record_command(self, command: str, context: ContextType, success: bool, execution_time: float):
        """Record command execution"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO command_history
                    (command, context, success, execution_time)
                    VALUES (?, ?, ?, ?)
                """, (command, context.value, success, execution_time))
                conn.commit()

                # Update in-memory patterns
                if success:
                    self.command_patterns[command] = self.command_patterns.get(command, 0) + 1

        except Exception as e:
            logging.debug(f"Could not record command: {e}")

    def record_completion_usage(self, completion_text: str, context: ContextType):
        """Record completion usage for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO completion_usage (completion_text, context, usage_count, last_used)
                    VALUES (?, ?, 1, datetime('now'))
                    ON CONFLICT(completion_text, context) DO UPDATE SET
                        usage_count = usage_count + 1,
                        last_used = datetime('now')
                """, (completion_text, context.value))
                conn.commit()
        except Exception as e:
            logging.debug(f"Could not record completion usage: {e}")

    def get_contextual_suggestions(self, context: ContextType, partial_input: str, limit: int = 10) -> List[CompletionSuggestion]:
        """Get suggestions based on context and history"""
        suggestions = []

        # Get commands from this context
        context_commands = self.context_commands.get(context, [])

        for command in context_commands:
            if partial_input and not command.startswith(partial_input):
                continue

            frequency = self.command_patterns.get(command, 0)
            confidence = min(0.9, frequency / 100.0)

            suggestions.append(CompletionSuggestion(
                text=command,
                completion_type=CompletionType.COMMAND,
                description=f"Previous command (used {frequency} times)",
                confidence=confidence,
                context_relevance=0.9,
                security_score=0.7,
                usage_frequency=frequency
            ))

        # Sort by frequency and confidence
        suggestions.sort(key=lambda x: (x.usage_frequency, x.confidence), reverse=True)
        return suggestions[:limit]


class FileSystemCompleter:
    """Intelligent file system path completion"""

    def __init__(self):
        self.security_directories = [
            '/var/log', '/etc', '/tmp', '/opt', '/usr/local',
            '/var/lib/synos', '/etc/synos', '/usr/lib/synos'
        ]

        self.security_file_patterns = [
            r'\.log$', r'\.conf$', r'\.config$', r'\.sh$', r'\.py$',
            r'\.xml$', r'\.json$', r'\.pcap$', r'\.cap$'
        ]

    def complete_path(self, partial_path: str, context: ContextType) -> List[CompletionSuggestion]:
        """Complete file system paths with security context"""
        suggestions = []

        try:
            # Expand ~ and environment variables
            expanded_path = os.path.expanduser(os.path.expandvars(partial_path))

            # Get directory and filename parts
            if expanded_path.endswith('/') or not expanded_path:
                directory = expanded_path or '.'
                filename_prefix = ''
            else:
                directory = os.path.dirname(expanded_path) or '.'
                filename_prefix = os.path.basename(expanded_path)

            # List directory contents
            if os.path.isdir(directory):
                try:
                    entries = os.listdir(directory)
                except PermissionError:
                    return suggestions

                for entry in entries:
                    if not entry.startswith('.') and entry.startswith(filename_prefix):
                        full_path = os.path.join(directory, entry)
                        is_dir = os.path.isdir(full_path)

                        # Calculate security relevance
                        security_score = self._calculate_security_relevance(full_path, context)

                        completion_text = entry
                        if is_dir:
                            completion_text += '/'

                        suggestions.append(CompletionSuggestion(
                            text=completion_text,
                            completion_type=CompletionType.FILE_PATH,
                            description=f"{'Directory' if is_dir else 'File'}: {full_path}",
                            confidence=0.8,
                            context_relevance=0.6,
                            security_score=security_score
                        ))

        except Exception as e:
            logging.debug(f"Path completion error: {e}")

        return suggestions

    def _calculate_security_relevance(self, path: str, context: ContextType) -> float:
        """Calculate security relevance score for path"""
        score = 0.5  # Base score

        # Check if in security-relevant directory
        for sec_dir in self.security_directories:
            if path.startswith(sec_dir):
                score += 0.3
                break

        # Check file extension
        for pattern in self.security_file_patterns:
            if re.search(pattern, path):
                score += 0.2
                break

        # Context-specific scoring
        if context == ContextType.SECURITY_ANALYSIS:
            if '/log' in path or '/evidence' in path:
                score += 0.3
        elif context == ContextType.PENETRATION_TESTING:
            if '/tmp' in path or '/opt' in path:
                score += 0.2

        return min(1.0, score)


class IntelligentCompleter:
    """Main intelligent completion engine"""

    def __init__(self, db_path: str = "/var/lib/synos/completion.db"):
        self.security_registry = SecurityToolRegistry()
        self.history_analyzer = CommandHistoryAnalyzer(db_path)
        self.filesystem_completer = FileSystemCompleter()

        # System command completions
        self.system_commands = self._load_system_commands()

        # Current context
        self.current_context = ContextType.SHELL

        # Setup readline completion
        self._setup_readline()

    def _load_system_commands(self) -> Dict[str, str]:
        """Load available system commands"""
        commands = {}

        # Get commands from PATH
        try:
            path_dirs = os.environ.get('PATH', '').split(':')
            for path_dir in path_dirs:
                if os.path.isdir(path_dir):
                    try:
                        for cmd in os.listdir(path_dir):
                            cmd_path = os.path.join(path_dir, cmd)
                            if os.access(cmd_path, os.X_OK) and not cmd.startswith('.'):
                                commands[cmd] = cmd_path
                    except PermissionError:
                        continue
        except Exception as e:
            logging.debug(f"Could not load system commands: {e}")

        return commands

    def _setup_readline(self):
        """Setup readline completion"""
        try:
            readline.set_completer(self._readline_completer)
            readline.parse_and_bind("tab: complete")
            readline.set_completer_delims(' \t\n`!@#$%^&*()=+[{]}\\|;:\'",<>?')
        except Exception as e:
            logging.debug(f"Could not setup readline: {e}")

    def _readline_completer(self, text: str, state: int) -> Optional[str]:
        """Readline completer function"""
        if state == 0:
            # Generate completions on first call
            line = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()

            context = CommandContext(
                current_command=line,
                partial_input=text,
                cursor_position=end,
                working_directory=os.getcwd(),
                environment_vars=dict(os.environ),
                recent_commands=[],
                active_processes=[],
                security_context=self.current_context
            )

            self._current_completions = self.get_completions(context)

        try:
            return self._current_completions[state].text
        except (IndexError, AttributeError):
            return None

    def get_completions(self, context: CommandContext) -> List[CompletionSuggestion]:
        """Get intelligent completions for given context"""
        suggestions = []

        # Parse command line
        parts = context.current_command.strip().split()
        if not parts:
            # Complete commands at start of line
            suggestions.extend(self._complete_commands(context.partial_input, context))
        else:
            command = parts[0]

            # Check if completing command name
            if len(parts) == 1 and not context.current_command.endswith(' '):
                suggestions.extend(self._complete_commands(context.partial_input, context))
            else:
                # Complete arguments/options
                suggestions.extend(self._complete_arguments(command, parts[1:], context))

        # Add contextual historical suggestions
        suggestions.extend(
            self.history_analyzer.get_contextual_suggestions(
                context.security_context,
                context.partial_input,
                limit=5
            )
        )

        # Remove duplicates and sort by relevance
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        return self._rank_suggestions(unique_suggestions, context)

    def _complete_commands(self, partial_input: str, context: CommandContext) -> List[CompletionSuggestion]:
        """Complete command names"""
        suggestions = []

        # Security tools first
        for tool_name, tool_info in self.security_registry.security_tools.items():
            if tool_name.startswith(partial_input):
                suggestions.append(CompletionSuggestion(
                    text=tool_name,
                    completion_type=CompletionType.SECURITY_TOOL,
                    description=tool_info['description'],
                    confidence=0.9,
                    context_relevance=0.9,
                    security_score=1.0
                ))

        # System commands
        for cmd_name in self.system_commands:
            if cmd_name.startswith(partial_input):
                # Higher priority for security-related commands
                security_score = 0.8 if any(keyword in cmd_name for keyword in
                    ['ssh', 'ssl', 'gpg', 'openssl', 'iptables', 'ufw', 'fail2ban', 'audit']) else 0.5

                suggestions.append(CompletionSuggestion(
                    text=cmd_name,
                    completion_type=CompletionType.COMMAND,
                    description=f"System command: {cmd_name}",
                    confidence=0.7,
                    context_relevance=0.6,
                    security_score=security_score
                ))

        return suggestions

    def _complete_arguments(self, command: str, args: List[str], context: CommandContext) -> List[CompletionSuggestion]:
        """Complete command arguments and options"""
        suggestions = []

        # Security tool specific completions
        tool_suggestions = self.security_registry.get_completions_for_tool(command, context.partial_input)
        suggestions.extend(tool_suggestions)

        # File path completions
        if context.partial_input.startswith('/') or context.partial_input.startswith('./') or context.partial_input.startswith('~/'):
            path_suggestions = self.filesystem_completer.complete_path(context.partial_input, context.security_context)
            suggestions.extend(path_suggestions)

        # Context-specific argument suggestions
        if command == 'systemctl' and len(args) >= 1:
            service_suggestions = self._complete_systemctl_services(args[0], context.partial_input)
            suggestions.extend(service_suggestions)

        return suggestions

    def _complete_systemctl_services(self, action: str, partial_input: str) -> List[CompletionSuggestion]:
        """Complete systemctl service names"""
        suggestions = []

        # Security-relevant services
        security_services = [
            'synos-ai-daemon', 'synos-security.target', 'synos-reconnaissance',
            'synos-vuln-scanner', 'synos-behavior-monitor', 'ssh', 'ufw', 'fail2ban'
        ]

        for service in security_services:
            if service.startswith(partial_input):
                suggestions.append(CompletionSuggestion(
                    text=service,
                    completion_type=CompletionType.VALUE,
                    description=f"Security service: {service}",
                    confidence=0.9,
                    context_relevance=0.8,
                    security_score=0.9
                ))

        return suggestions

    def _deduplicate_suggestions(self, suggestions: List[CompletionSuggestion]) -> List[CompletionSuggestion]:
        """Remove duplicate suggestions"""
        seen_texts = set()
        unique_suggestions = []

        for suggestion in suggestions:
            if suggestion.text not in seen_texts:
                seen_texts.add(suggestion.text)
                unique_suggestions.append(suggestion)

        return unique_suggestions

    def _rank_suggestions(self, suggestions: List[CompletionSuggestion], context: CommandContext) -> List[CompletionSuggestion]:
        """Rank suggestions by relevance and quality"""

        def calculate_score(suggestion: CompletionSuggestion) -> float:
            # Weighted scoring
            score = (
                suggestion.confidence * 0.3 +
                suggestion.context_relevance * 0.3 +
                suggestion.security_score * 0.2 +
                min(suggestion.usage_frequency / 100.0, 0.2) * 0.2
            )

            # Boost security tools in security contexts
            if (suggestion.completion_type == CompletionType.SECURITY_TOOL and
                context.security_context != ContextType.SHELL):
                score += 0.1

            # Boost exact prefix matches
            if suggestion.text.startswith(context.partial_input):
                score += 0.1

            return score

        suggestions.sort(key=calculate_score, reverse=True)
        return suggestions[:20]  # Return top 20 suggestions

    def update_context(self, new_context: ContextType):
        """Update current security context"""
        self.current_context = new_context
        logging.info(f"Completion context updated to: {new_context.value}")

    def record_command_execution(self, command: str, success: bool, execution_time: float):
        """Record command execution for learning"""
        self.history_analyzer.record_command(command, self.current_context, success, execution_time)

    def record_completion_selection(self, completion_text: str):
        """Record when user selects a completion"""
        self.history_analyzer.record_completion_usage(completion_text, self.current_context)

    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Get simple command suggestions (for external use)"""
        context = CommandContext(
            current_command=partial_command,
            partial_input=partial_command.split()[-1] if partial_command else "",
            cursor_position=len(partial_command),
            working_directory=os.getcwd(),
            environment_vars={},
            recent_commands=[],
            active_processes=[],
            security_context=self.current_context
        )

        suggestions = self.get_completions(context)
        return [s.text for s in suggestions[:10]]

    def get_security_examples(self, tool_name: str) -> List[str]:
        """Get example commands for security tool"""
        return self.security_registry.suggest_examples(tool_name)

    def get_completion_help(self, completion_text: str) -> str:
        """Get help text for completion"""
        tool_info = self.security_registry.get_tool_info(completion_text)

        if tool_info:
            help_text = f"{completion_text}: {tool_info['description']}\n\n"

            if 'examples' in tool_info:
                help_text += "Examples:\n"
                for example in tool_info['examples'][:3]:
                    help_text += f"  {example}\n"

            return help_text

        return f"Command: {completion_text}"


async def main():
    """Example usage of Intelligent Command Completion"""
    logging.basicConfig(level=logging.INFO)

    completer = IntelligentCompleter()

    print("🧠 SynOS Intelligent Command Completion Engine")
    print("=" * 50)

    # Test different completion scenarios
    test_contexts = [
        ("nmap ", ContextType.PENETRATION_TESTING),
        ("synos-security ", ContextType.SECURITY_ANALYSIS),
        ("systemctl start ", ContextType.SYSTEM_ADMINISTRATION),
        ("/var/log/", ContextType.INCIDENT_RESPONSE)
    ]

    for partial_command, context_type in test_contexts:
        print(f"\n🔍 Context: {context_type.value}")
        print(f"💬 Partial command: '{partial_command}'")

        completer.update_context(context_type)

        context = CommandContext(
            current_command=partial_command,
            partial_input=partial_command.split()[-1],
            cursor_position=len(partial_command),
            working_directory="/home/user",
            environment_vars={},
            recent_commands=[],
            active_processes=[],
            security_context=context_type
        )

        suggestions = completer.get_completions(context)

        print("📝 Top suggestions:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion.text} - {suggestion.description}")
            print(f"     Confidence: {suggestion.confidence:.2f}, Security: {suggestion.security_score:.2f}")

    # Show security tool examples
    print(f"\n🛠️ Security Tool Examples:")
    examples = completer.get_security_examples('nmap')
    for example in examples:
        print(f"  • {example}")

    print(f"\n✅ Intelligent completion engine ready!")


if __name__ == "__main__":
    asyncio.run(main())