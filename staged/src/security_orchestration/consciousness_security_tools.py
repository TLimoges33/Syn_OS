#!/usr/bin/env python3
"""
Consciousness-Controlled Security Tools Integration
Ethical security tool orchestration with consciousness-aware safeguards
"""

import asyncio
import logging
import time
import json
import subprocess
import os
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import ipaddress
import socket
import re

from src.consciousness_v2.consciousness_bus import ConsciousnessBus
try:
    from src.security.audit_logger import AuditLogger
except ImportError:
    class AuditLogger:
        async def log_system_event(self, event_type, details):
            pass

# SECURITY FIX: Import input sanitization framework
try:
    from src.security.input_sanitization import input_sanitizer
except ImportError:
    # Fallback if sanitization module not available
    class MockSanitizer:
        def sanitize_command_input(self, input_str):
            return {'valid': True, 'sanitized': input_str, 'reason': 'No sanitizer available', 'risk_level': 'HIGH'}
        def validate_security_tool_params(self, tool_name, params):
            return {'valid': True, 'sanitized_params': params, 'reason': 'No validation available', 'risk_level': 'HIGH'}
    input_sanitizer = MockSanitizer()

from src.learning_gamification.character_system import Character, EthicalAlignment


class ToolCategory(Enum):
    """Security tool categories"""
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY_SCANNING = "vulnerability_scanning"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    FORENSICS = "forensics"
    NETWORK_ANALYSIS = "network_analysis"
    WEB_APPLICATION = "web_application"
    WIRELESS = "wireless"
    SOCIAL_ENGINEERING = "social_engineering"
    CRYPTOGRAPHY = "cryptography"


class AuthorizationLevel(Enum):
    """Authorization levels for tool usage"""
    EDUCATIONAL = "educational"  # Lab environments only
    AUTHORIZED_TESTING = "authorized_testing"  # With explicit permission
    PROFESSIONAL = "professional"  # Professional penetration testing
    RESEARCH = "research"  # Security research with oversight


class ToolRiskLevel(Enum):
    """Risk levels for security tools"""
    LOW = "low"  # Information gathering, passive tools
    MEDIUM = "medium"  # Active scanning, potential detection
    HIGH = "high"  # Exploitation tools, system modification
    CRITICAL = "critical"  # Dangerous tools requiring special authorization


@dataclass
class SecurityTool:
    """Security tool definition"""
    tool_id: str
    name: str
    category: ToolCategory
    risk_level: ToolRiskLevel
    required_authorization: AuthorizationLevel
    required_ethical_score: int
    required_skill_level: int
    command_template: str
    description: str
    legal_warnings: List[str]
    educational_context: str
    prerequisites: List[str]
    output_sanitization: bool = True
    requires_target_validation: bool = True
    max_concurrent_usage: int = 1


@dataclass
class ToolExecution:
    """Tool execution record"""
    execution_id: str
    tool_id: str
    character_id: str
    command: str
    target: str
    authorization_level: str
    ethical_score_at_execution: int
    consciousness_level: float
    started_at: float
    completed_at: Optional[float] = None
    status: str = "running"
    output: str = ""
    sanitized_output: str = ""
    warnings_acknowledged: bool = False


class ConsciousnessSecurityTools:
    """
    Consciousness-controlled security tools orchestration system
    Provides ethical, authorized access to cybersecurity tools with comprehensive safeguards
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus, character_system):
        """Initialize consciousness security tools"""
        self.consciousness_bus = consciousness_bus
        self.character_system = character_system
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.tools_directory = "/opt/syn_os/security_tools"
        self.authorized_networks = ["127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
        self.lab_environment_required = True
        
        # Tool definitions
        self.security_tools: Dict[str, SecurityTool] = {}
        self.active_executions: Dict[str, ToolExecution] = {}
        
        # Safety mechanisms
        self.max_concurrent_executions = 5
        self.execution_timeout = 300  # 5 minutes
        self.consciousness_threshold = 0.7
        
        # Initialize system
        asyncio.create_task(self._initialize_security_tools())
    
    async def _initialize_security_tools(self):
        """Initialize security tools system"""
        try:
            self.logger.info("Initializing consciousness-controlled security tools...")
            
            # Create tools directory
            os.makedirs(self.tools_directory, exist_ok=True)
            
            # Initialize tool definitions
            await self._initialize_tool_definitions()
            
            # Verify tool availability
            await self._verify_tool_availability()
            
            self.logger.info("Consciousness security tools initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing security tools: {e}")
    
    async def _initialize_tool_definitions(self):
        """Initialize security tool definitions"""
        try:
            # Reconnaissance Tools
            self.security_tools["nmap_basic"] = SecurityTool(
                tool_id="nmap_basic",
                name="Nmap Basic Scan",
                category=ToolCategory.RECONNAISSANCE,
                risk_level=ToolRiskLevel.LOW,
                required_authorization=AuthorizationLevel.EDUCATIONAL,
                required_ethical_score=0,
                required_skill_level=1,
                command_template="nmap -sn {target}",
                description="Basic network discovery using ping scan",
                legal_warnings=[
                    "Only use on networks you own or have explicit permission to scan",
                    "Unauthorized network scanning may violate computer crime laws",
                    "Always ensure proper authorization before scanning"
                ],
                educational_context="Learn basic network discovery techniques in authorized environments",
                prerequisites=["basic_networking", "ethical_hacking_fundamentals"]
            )
            
            self.security_tools["nmap_port_scan"] = SecurityTool(
                tool_id="nmap_port_scan",
                name="Nmap Port Scan",
                category=ToolCategory.RECONNAISSANCE,
                risk_level=ToolRiskLevel.MEDIUM,
                required_authorization=AuthorizationLevel.AUTHORIZED_TESTING,
                required_ethical_score=10,
                required_skill_level=3,
                command_template="nmap -sS -O {target}",
                description="TCP SYN scan with OS detection",
                legal_warnings=[
                    "CRITICAL: Port scanning without authorization is illegal in many jurisdictions",
                    "Only scan systems you own or have explicit written permission",
                    "Unauthorized scanning can be considered unauthorized access"
                ],
                educational_context="Advanced reconnaissance techniques for authorized penetration testing",
                prerequisites=["passive_reconnaissance", "active_reconnaissance"]
            )
            
            # Vulnerability Scanning Tools
            self.security_tools["nikto_web_scan"] = SecurityTool(
                tool_id="nikto_web_scan",
                name="Nikto Web Vulnerability Scanner",
                category=ToolCategory.WEB_APPLICATION,
                risk_level=ToolRiskLevel.MEDIUM,
                required_authorization=AuthorizationLevel.AUTHORIZED_TESTING,
                required_ethical_score=15,
                required_skill_level=5,
                command_template="nikto -h {target} -Format txt",
                description="Web server vulnerability scanner",
                legal_warnings=[
                    "Web application scanning must be authorized by the application owner",
                    "Unauthorized scanning may trigger security alerts and legal action",
                    "Ensure proper scope and authorization documentation"
                ],
                educational_context="Web application security assessment in controlled environments",
                prerequisites=["web_application_fundamentals", "vulnerability_assessment"]
            )
            
            # Network Analysis Tools
            self.security_tools["wireshark_capture"] = SecurityTool(
                tool_id="wireshark_capture",
                name="Wireshark Packet Capture",
                category=ToolCategory.NETWORK_ANALYSIS,
                risk_level=ToolRiskLevel.LOW,
                required_authorization=AuthorizationLevel.EDUCATIONAL,
                required_ethical_score=20,
                required_skill_level=2,
                command_template="tshark -i {interface} -c 100 -w {output_file}",
                description="Network packet capture and analysis",
                legal_warnings=[
                    "Only capture traffic on networks you own or administer",
                    "Intercepting network traffic may violate privacy laws",
                    "Be aware of data protection regulations"
                ],
                educational_context="Network protocol analysis and troubleshooting",
                prerequisites=["networking_fundamentals", "protocol_analysis"]
            )
            
            # Exploitation Tools (High Risk)
            self.security_tools["metasploit_basic"] = SecurityTool(
                tool_id="metasploit_basic",
                name="Metasploit Framework (Basic)",
                category=ToolCategory.EXPLOITATION,
                risk_level=ToolRiskLevel.HIGH,
                required_authorization=AuthorizationLevel.PROFESSIONAL,
                required_ethical_score=30,
                required_skill_level=10,
                command_template="msfconsole -q -x 'use {module}; set RHOSTS {target}; check; exit'",
                description="Vulnerability exploitation framework (check mode only)",
                legal_warnings=[
                    "DANGER: Exploitation tools are illegal without explicit authorization",
                    "Only use in authorized penetration testing environments",
                    "Unauthorized use can result in criminal charges",
                    "Requires professional oversight and documentation"
                ],
                educational_context="Professional penetration testing methodology",
                prerequisites=["vulnerability_assessment", "exploitation_fundamentals", "legal_compliance"],
                max_concurrent_usage=1
            )
            
            # Social Engineering Tools (Educational)
            self.security_tools["social_engineer_toolkit"] = SecurityTool(
                tool_id="social_engineer_toolkit",
                name="Social Engineer Toolkit (Educational)",
                category=ToolCategory.SOCIAL_ENGINEERING,
                risk_level=ToolRiskLevel.CRITICAL,
                required_authorization=AuthorizationLevel.RESEARCH,
                required_ethical_score=50,
                required_skill_level=15,
                command_template="setoolkit --help",
                description="Social engineering awareness and education tool",
                legal_warnings=[
                    "CRITICAL: Social engineering attacks are illegal without consent",
                    "Only use for authorized security awareness training",
                    "Requires explicit consent from all participants",
                    "Must comply with organizational policies and legal requirements"
                ],
                educational_context="Security awareness training and phishing simulation",
                prerequisites=["social_engineering_awareness", "ethical_compliance", "legal_training"],
                max_concurrent_usage=1
            )
            
            self.logger.info(f"Initialized {len(self.security_tools)} security tool definitions")
            
        except Exception as e:
            self.logger.error(f"Error initializing tool definitions: {e}")
    
    async def _verify_tool_availability(self):
        """Verify that security tools are available on the system"""
        try:
            tool_availability = {}
            
            # Check common security tools
            tools_to_check = {
                "nmap": "nmap --version",
                "nikto": "nikto -Version",
                "wireshark": "tshark --version",
                "metasploit": "msfconsole --version",
                "setoolkit": "which setoolkit"
            }
            
            for tool_name, check_command in tools_to_check.items():
                try:
                    # SECURITY FIX: Use secure subprocess execution
                    command_parts = check_command.split()
                    result = subprocess.run(
                        command_parts,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=False  # Explicitly disable shell
                    )
                    tool_availability[tool_name] = result.returncode == 0
                except Exception:
                    tool_availability[tool_name] = False
            
            self.logger.info(f"Tool availability: {tool_availability}")
            
            # Warn about missing tools
            missing_tools = [tool for tool, available in tool_availability.items() if not available]
            if missing_tools:
                self.logger.warning(f"Missing security tools: {missing_tools}")
            
        except Exception as e:
            self.logger.error(f"Error verifying tool availability: {e}")
    
    async def get_available_tools(self, character_id: str) -> List[Dict[str, Any]]:
        """Get tools available to a character based on their progression"""
        try:
            if character_id not in self.character_system.characters:
                return []
            
            character = self.character_system.characters[character_id]
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            available_tools = []
            
            for tool in self.security_tools.values():
                # Check ethical score requirement
                if character.ethical_score < tool.required_ethical_score:
                    continue
                
                # Check skill level requirement
                required_skills_met = True
                for prereq in tool.prerequisites:
                    if prereq not in character.skills or character.skills[prereq].level < tool.required_skill_level:
                        required_skills_met = False
                        break
                
                if not required_skills_met:
                    continue
                
                # Check consciousness level for high-risk tools
                if (tool.risk_level in [ToolRiskLevel.HIGH, ToolRiskLevel.CRITICAL] and 
                    consciousness_state.get('overall_consciousness_level', 0) < self.consciousness_threshold):
                    continue
                
                available_tools.append({
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "category": tool.category.value,
                    "risk_level": tool.risk_level.value,
                    "required_authorization": tool.required_authorization.value,
                    "description": tool.description,
                    "legal_warnings": tool.legal_warnings,
                    "educational_context": tool.educational_context,
                    "prerequisites": tool.prerequisites
                })
            
            return available_tools
            
        except Exception as e:
            self.logger.error(f"Error getting available tools: {e}")
            return []
    
    async def execute_tool(self, character_id: str, tool_id: str, target: str,
                          parameters: Optional[Dict[str, Any]] = None,
                          acknowledge_warnings: bool = False) -> Dict[str, Any]:
        """Execute a security tool with consciousness-aware safeguards"""
        try:
            # SECURITY FIX: Sanitize all inputs first
            target_validation = input_sanitizer.sanitize_command_input(target)
            if not target_validation['valid']:
                self.logger.warning(f"Invalid target input: {target_validation['reason']}")
                return {
                    "success": False,
                    "error": f"Invalid target: {target_validation['reason']}",
                    "risk_level": target_validation['risk_level']
                }
            
            # Validate parameters if provided
            if parameters:
                param_validation = input_sanitizer.validate_security_tool_params(tool_id, parameters)
                if not param_validation['valid']:
                    self.logger.warning(f"Invalid parameters: {param_validation['reason']}")
                    return {
                        "success": False,
                        "error": f"Invalid parameters: {param_validation['reason']}",
                        "risk_level": param_validation['risk_level']
                    }
                parameters = param_validation['sanitized_params']
            
            # Validate character
            if character_id not in self.character_system.characters:
                return {
                    "success": False,
                    "error": "Character not found"
                }
            
            character = self.character_system.characters[character_id]
            
            # Validate tool
            if tool_id not in self.security_tools:
                return {
                    "success": False,
                    "error": "Tool not found"
                }
            
            tool = self.security_tools[tool_id]
            
            # Check if warnings need acknowledgment
            if tool.legal_warnings and not acknowledge_warnings:
                return {
                    "success": False,
                    "error": "Legal acknowledgment required",
                    "legal_warnings": tool.legal_warnings,
                    "requires_acknowledgment": True
                }
            
            # Validate authorization
            auth_check = await self._check_authorization(character, tool, target)
            if not auth_check["authorized"]:
                return {
                    "success": False,
                    "error": auth_check["reason"]
                }
            
            # Check consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.get('overall_consciousness_level', 0)
            
            if consciousness_level < self.consciousness_threshold and tool.risk_level in [ToolRiskLevel.HIGH, ToolRiskLevel.CRITICAL]:
                return {
                    "success": False,
                    "error": "Insufficient consciousness level for high-risk tool execution"
                }
            
            # Check concurrent execution limits
            if len(self.active_executions) >= self.max_concurrent_executions:
                return {
                    "success": False,
                    "error": "Maximum concurrent executions reached"
                }
            
            # Validate target
            if tool.requires_target_validation:
                target_validation = await self._validate_target(target)
                if not target_validation["valid"]:
                    return {
                        "success": False,
                        "error": f"Invalid target: {target_validation['reason']}"
                    }
            
            # Create execution record
            execution_id = f"{character_id}_{tool_id}_{int(time.time())}"
            execution = ToolExecution(
                execution_id=execution_id,
                tool_id=tool_id,
                character_id=character_id,
                command=self._build_command(tool, target, parameters or {}),
                target=target,
                authorization_level=tool.required_authorization.value,
                ethical_score_at_execution=character.ethical_score,
                consciousness_level=consciousness_level,
                started_at=time.time(),
                warnings_acknowledged=acknowledge_warnings
            )
            
            # Execute tool
            self.active_executions[execution_id] = execution
            
            # Run tool execution in background
            asyncio.create_task(self._execute_tool_async(execution))
            
            # Log execution
            await self.audit_logger.log_system_event(
                event_type="security_tool_executed",
                details={
                    "character_id": character_id,
                    "tool_id": tool_id,
                    "target": target,
                    "ethical_score": character.ethical_score,
                    "consciousness_level": consciousness_level,
                    "authorization_level": tool.required_authorization.value
                }
            )
            
            return {
                "success": True,
                "execution_id": execution_id,
                "message": f"Tool '{tool.name}' execution started",
                "estimated_duration": "1-5 minutes",
                "ethical_reminder": "Remember to use this tool responsibly and ethically!"
            }
            
        except Exception as e:
            self.logger.error(f"Error executing tool: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    async def _check_authorization(self, character: Character, tool: SecurityTool, target: str) -> Dict[str, Any]:
        """Check if character is authorized to use the tool"""
        try:
            # Check ethical score
            if character.ethical_score < tool.required_ethical_score:
                return {
                    "authorized": False,
                    "reason": f"Insufficient ethical score. Required: {tool.required_ethical_score}, Current: {character.ethical_score}"
                }
            
            # Check skill prerequisites
            for prereq in tool.prerequisites:
                if prereq not in character.skills:
                    return {
                        "authorized": False,
                        "reason": f"Missing required skill: {prereq}"
                    }
                
                if character.skills[prereq].level < tool.required_skill_level:
                    return {
                        "authorized": False,
                        "reason": f"Insufficient skill level for {prereq}. Required: {tool.required_skill_level}"
                    }
            
            # Check ethical alignment for high-risk tools
            if tool.risk_level == ToolRiskLevel.CRITICAL and character.alignment != EthicalAlignment.WHITE_HAT:
                return {
                    "authorized": False,
                    "reason": "Critical tools require White Hat ethical alignment"
                }
            
            # Check lab environment requirement
            if self.lab_environment_required and not self._is_lab_environment(target):
                return {
                    "authorized": False,
                    "reason": "Tool execution restricted to lab environments"
                }
            
            return {
                "authorized": True,
                "reason": "Authorization checks passed"
            }
            
        except Exception as e:
            self.logger.error(f"Error checking authorization: {e}")
            return {
                "authorized": False,
                "reason": "Authorization check failed"
            }
    
    def _is_lab_environment(self, target: str) -> bool:
        """Check if target is in an authorized lab environment"""
        try:
            # Check if target is in authorized networks
            target_ip = socket.gethostbyname(target)
            target_addr = ipaddress.ip_address(target_ip)
            
            for network in self.authorized_networks:
                if target_addr in ipaddress.ip_network(network):
                    return True
            
            # Check for common lab domains
            lab_domains = [".local", ".lab", ".test", ".dev", "localhost"]
            if any(domain in target.lower() for domain in lab_domains):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking lab environment: {e}")
            return False
    
    async def _validate_target(self, target: str) -> Dict[str, Any]:
        """Validate target for security tool execution"""
        try:
            # Check for valid format
            if not target or len(target.strip()) == 0:
                return {
                    "valid": False,
                    "reason": "Target cannot be empty"
                }
            
            # Check for dangerous targets
            dangerous_patterns = [
                r".*\.gov$",  # Government domains
                r".*\.mil$",  # Military domains
                r".*\.edu$",  # Educational institutions (unless explicitly authorized)
                r".*bank.*",  # Banking-related
                r".*hospital.*",  # Healthcare
                r".*critical.*"  # Critical infrastructure
            ]
            
            for pattern in dangerous_patterns:
                if re.match(pattern, target, re.IGNORECASE):
                    return {
                        "valid": False,
                        "reason": f"Target matches restricted pattern: {pattern}"
                    }
            
            # Validate IP address or hostname format
            try:
                # Try as IP address
                ipaddress.ip_address(target)
            except ValueError:
                # Try as hostname
                if not re.match(r'^[a-zA-Z0-9.-]+$', target):
                    return {
                        "valid": False,
                        "reason": "Invalid target format"
                    }
            
            return {
                "valid": True,
                "reason": "Target validation passed"
            }
            
        except Exception as e:
            self.logger.error(f"Error validating target: {e}")
            return {
                "valid": False,
                "reason": "Target validation failed"
            }
    
    def _build_command(self, tool: SecurityTool, target: str, parameters: Dict[str, Any]) -> str:
        """Build command string for tool execution"""
        try:
            command = tool.command_template.format(target=target, **parameters)
            
            # Add safety parameters
            if tool.tool_id.startswith("nmap"):
                command += " --max-rate 100 --max-retries 1"
            
            return command
            
        except Exception as e:
            self.logger.error(f"Error building command: {e}")
            return ""
    
    def _parse_secure_command(self, command: str) -> List[str]:
        """Parse and validate command for secure execution"""
        try:
            # SECURITY: Whitelist allowed commands and validate arguments
            import shlex
            
            # Parse command safely
            parts = shlex.split(command)
            if not parts:
                return []
            
            # Whitelist of allowed security tools
            allowed_tools = {
                'nmap': ['nmap'],
                'nikto': ['nikto'],
                'tshark': ['tshark'],
                'msfconsole': ['msfconsole'],
                'setoolkit': ['setoolkit']
            }
            
            base_command = parts[0]
            
            # Check if command is in whitelist
            tool_found = False
            for tool_name, allowed_commands in allowed_tools.items():
                if base_command in allowed_commands:
                    tool_found = True
                    break
            
            if not tool_found:
                self.logger.warning(f"Command not in whitelist: {base_command}")
                return []
            
            # Additional validation for dangerous arguments
            dangerous_args = ['--script', '&&', '||', ';', '|', '>', '<', '`', '$']
            for arg in parts:
                if any(dangerous in arg for dangerous in dangerous_args):
                    self.logger.warning(f"Dangerous argument detected: {arg}")
                    return []
            
            return parts
            
        except Exception as e:
            self.logger.error(f"Error parsing command: {e}")
            return []
    
    async def _execute_tool_async(self, execution: ToolExecution):
        """Execute tool asynchronously with secure command execution"""
        try:
            self.logger.info(f"Executing tool: {execution.tool_id}")
            
            # SECURITY FIX: Parse and validate command instead of shell execution
            command_parts = self._parse_secure_command(execution.command)
            if not command_parts:
                execution.status = "error"
                execution.output = "Invalid or unsafe command detected"
                execution.completed_at = time.time()
                return
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
                output_file = temp_file.name
            
            # Execute command with secure subprocess (no shell=True)
            process = await asyncio.create_subprocess_exec(
                *command_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.tools_directory
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.execution_timeout
                )
                
                execution.output = stdout.decode('utf-8', errors='ignore')
                if stderr:
                    execution.output += f"\nSTDERR:\n{stderr.decode('utf-8', errors='ignore')}"
                
                execution.status = "completed"
                
            except asyncio.TimeoutError:
                process.kill()
                execution.output = "Tool execution timed out"
                execution.status = "timeout"
            
            # Sanitize output
            if self.security_tools[execution.tool_id].output_sanitization:
                execution.sanitized_output = self._sanitize_output(execution.output)
            else:
                execution.sanitized_output = execution.output
            
            execution.completed_at = time.time()
            
            # Clean up temporary file
            try:
                os.unlink(output_file)
            except:
                pass
            
            self.logger.info(f"Tool execution completed: {execution.execution_id}")
            
        except Exception as e:
            execution.status = "error"
            execution.output = f"Execution error: {str(e)}"
            execution.sanitized_output = execution.output
            execution.completed_at = time.time()
            self.logger.error(f"Error in tool execution: {e}")
        
        finally:
            # Remove from active executions after a delay
            await asyncio.sleep(300)  # Keep results for 5 minutes
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
    
    def _sanitize_output(self, output: str) -> str:
        """Sanitize tool output to remove sensitive information"""
        try:
            sanitized = output
            
            # Remove potential sensitive patterns
            sensitive_patterns = [
                (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_ADDRESS]'),  # IP addresses
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email addresses
                (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CREDIT_CARD]'),  # Credit card numbers
                (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # Social Security Numbers
            ]
            
            for pattern, replacement in sensitive_patterns:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Error sanitizing output: {e}")
            return output
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of tool execution"""
        try:
            if execution_id not in self.active_executions:
                return {
                    "success": False,
                    "error": "Execution not found"
                }
            
            execution = self.active_executions[execution_id]
            
            return {
                "success": True,
                "execution_id": execution_id,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "output": execution.sanitized_output if execution.status == "completed" else "Execution in progress...",
                "tool_name": self.security_tools[execution.tool_id].name
            }
            
        except Exception as e:
            self.logger.error(f"Error getting execution status: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    async def cancel_execution(self, execution_id: str, character_id: str) -> Dict[str, Any]:
        """Cancel a running tool execution"""
        try:
            if execution_id not in self.active_executions:
                return {
                    "success": False,
                    "error": "Execution not found"
                }
            
            execution = self.active_executions[execution_id]
            
            # Check ownership
            if execution.character_id != character_id:
                return {
                    "success": False,
                    "error": "Unauthorized to cancel this execution"
                }
            
            # Mark as cancelled
            execution.status = "cancelled"
            execution.completed_at = time.time()
            
            return {
                "success": True,
                "message": "Execution cancelled successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error cancelling execution: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on security tools system"""
        try:
            return {
                "status": "healthy",
                "total_tools": len(self.security_tools),
                "active_executions": len(self.active_executions),
                "consciousness_threshold": self.consciousness_threshold,
                "lab_environment_required": self.lab_environment_required,
                "authorized_networks": self.authorized_networks
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Example usage and testing
async def main():
    """Example usage of Consciousness Security Tools"""
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    from src.learning_gamification.character_system import CharacterSystem
    
    # Initialize components
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.initialize()
    
    character_system = CharacterSystem(consciousness_bus)
    security_tools = ConsciousnessSecurityTools(consciousness_bus, character_system)
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Health check
    health = await security_tools.health_check()
    print(f"Security tools health: {health}")
    
    # Shutdown
    await consciousness_bus.shutdown()


if __name__ == "__main__":
    asyncio.run(main())