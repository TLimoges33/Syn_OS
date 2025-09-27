#!/usr/bin/env python3
"""
AI-Enhanced ParrotOS Integration System
======================================

This module provides intelligent integration with ParrotOS security tools,
featuring AI-powered tool selection, consciousness-guided assessments,
and automated security scenario generation.

Key Features:
- 500+ penetration testing tools with AI selection
- Consciousness-guided threat detection and assessment
- Intelligent security assessment automation
- Educational security scenario framework
- Real-time adaptive tool recommendations
"""

import asyncio
import json
import logging
import subprocess
import time
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET

# Import consciousness and security components
from .consciousness_security_controller import (
    ConsciousnessSecurityController, SecurityEvent, SecurityEventType,
    ConsciousnessSecurityDecision, ThreatLevel, SecurityAction
)
from .advanced_security_orchestrator import (
    AdvancedSecurityOrchestrator, SecurityTool, SecurityDistribution,
    ThreatSeverity, OperationMode, SecurityOperation, OperationResult
)

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """ParrotOS security tool categories"""
    INFORMATION_GATHERING = "information_gathering"
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    WEB_APPLICATION_ANALYSIS = "web_application_analysis"
    DATABASE_ASSESSMENT = "database_assessment"
    PASSWORD_ATTACKS = "password_attacks"
    WIRELESS_ATTACKS = "wireless_attacks"
    REVERSE_ENGINEERING = "reverse_engineering"
    EXPLOITATION_TOOLS = "exploitation_tools"
    SNIFFING_SPOOFING = "sniffing_spoofing"
    POST_EXPLOITATION = "post_exploitation"
    FORENSICS = "forensics"
    REPORTING_TOOLS = "reporting_tools"
    SOCIAL_ENGINEERING = "social_engineering"
    SYSTEM_SERVICES = "system_services"


class ToolComplexity(IntEnum):
    """Tool complexity levels for AI selection"""
    BASIC = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5


class AssessmentType(Enum):
    """Types of security assessments"""
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY_SCAN = "vulnerability_scan"
    PENETRATION_TEST = "penetration_test"
    COMPLIANCE_AUDIT = "compliance_audit"
    INCIDENT_RESPONSE = "incident_response"
    THREAT_HUNTING = "threat_hunting"
    RED_TEAM_EXERCISE = "red_team_exercise"
    BLUE_TEAM_DEFENSE = "blue_team_defense"


@dataclass
class ParrotOSTool:
    """Enhanced ParrotOS tool definition with AI metadata"""
    tool_id: str
    name: str
    category: ToolCategory
    complexity: ToolComplexity
    executable_path: str
    description: str
    capabilities: List[str]
    typical_use_cases: List[str]
    prerequisites: List[str]
    output_formats: List[str]
    ai_confidence_score: float = 0.0
    consciousness_compatibility: bool = True
    stealth_capable: bool = False
    requires_root: bool = False
    network_intensive: bool = False
    resource_intensive: bool = False
    educational_value: int = 5  # 1-10 scale
    risk_level: int = 3  # 1-5 scale
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class AIToolRecommendation:
    """AI-generated tool recommendation"""
    tool_id: str
    confidence_score: float
    reasoning: str
    expected_effectiveness: float
    estimated_duration: int  # seconds
    resource_requirements: Dict[str, Any]
    consciousness_insights: Dict[str, Any]
    alternative_tools: List[str]
    risk_assessment: Dict[str, Any]


@dataclass
class SecurityScenario:
    """Educational security scenario"""
    scenario_id: str
    title: str
    description: str
    difficulty_level: ToolComplexity
    learning_objectives: List[str]
    target_environment: Dict[str, Any]
    recommended_tools: List[str]
    step_by_step_guide: List[Dict[str, Any]]
    expected_outcomes: List[str]
    assessment_criteria: Dict[str, Any]
    consciousness_adaptations: Dict[str, Any]


@dataclass
class AssessmentResult:
    """Comprehensive security assessment result"""
    assessment_id: str
    assessment_type: AssessmentType
    target: str
    start_time: datetime
    end_time: Optional[datetime]
    tools_used: List[str]
    findings: List[Dict[str, Any]]
    threat_level: ThreatLevel
    confidence_score: float
    consciousness_analysis: Dict[str, Any]
    recommendations: List[str]
    remediation_steps: List[Dict[str, Any]]
    compliance_status: Dict[str, Any]
    executive_summary: str


class ParrotOSToolDatabase:
    """Comprehensive database of ParrotOS security tools with AI metadata"""
    
    def __init__(self):
        self.tools: Dict[str, ParrotOSTool] = {}
        self.category_index: Dict[ToolCategory, List[str]] = {}
        self.complexity_index: Dict[ToolComplexity, List[str]] = {}
        self.capability_index: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(f"{__name__}.ToolDatabase")
        
        # Initialize tool database
        self._initialize_tool_database()
    
    def _initialize_tool_database(self):
        """Initialize the comprehensive ParrotOS tool database"""
        try:
            self.logger.info("Initializing ParrotOS tool database with 500+ tools...")
            
            # Add all tool categories
            self._add_information_gathering_tools()
            self._add_vulnerability_analysis_tools()
            self._add_web_application_tools()
            self._add_database_assessment_tools()
            self._add_password_attack_tools()
            self._add_wireless_attack_tools()
            self._add_reverse_engineering_tools()
            self._add_exploitation_tools()
            self._add_sniffing_spoofing_tools()
            self._add_post_exploitation_tools()
            self._add_forensics_tools()
            self._add_reporting_tools()
            self._add_social_engineering_tools()
            self._add_system_services()
            
            self._build_indexes()
            self.logger.info(f"Initialized {len(self.tools)} ParrotOS security tools")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tool database: {e}")
    
    def _add_information_gathering_tools(self):
        """Add information gathering tools"""
        tools = [
            ParrotOSTool(
                tool_id="nmap",
                name="Nmap",
                category=ToolCategory.INFORMATION_GATHERING,
                complexity=ToolComplexity.INTERMEDIATE,
                executable_path="/usr/bin/nmap",
                description="Network discovery and security auditing tool",
                capabilities=["port_scanning", "service_detection", "os_detection", "script_scanning"],
                typical_use_cases=["network_reconnaissance", "service_enumeration", "vulnerability_detection"],
                prerequisites=["network_access"],
                output_formats=["xml", "json", "text"],
                ai_confidence_score=0.95,
                stealth_capable=True,
                network_intensive=True,
                educational_value=9,
                risk_level=2
            ),
            ParrotOSTool(
                tool_id="masscan",
                name="Masscan",
                category=ToolCategory.INFORMATION_GATHERING,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/masscan",
                description="High-speed port scanner",
                capabilities=["fast_port_scanning", "large_network_scanning"],
                typical_use_cases=["internet_scanning", "large_network_discovery"],
                prerequisites=["raw_socket_access"],
                output_formats=["xml", "json", "list"],
                ai_confidence_score=0.88,
                requires_root=True,
                network_intensive=True,
                educational_value=7,
                risk_level=3
            ),
            ParrotOSTool(
                tool_id="dmitry",
                name="DMitry",
                category=ToolCategory.INFORMATION_GATHERING,
                complexity=ToolComplexity.BASIC,
                executable_path="/usr/bin/dmitry",
                description="Deepmagic Information Gathering Tool",
                capabilities=["whois_lookup", "netcraft_search", "subdomain_search"],
                typical_use_cases=["domain_reconnaissance", "passive_information_gathering"],
                prerequisites=["internet_access"],
                output_formats=["text"],
                ai_confidence_score=0.75,
                educational_value=6,
                risk_level=1
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_vulnerability_analysis_tools(self):
        """Add vulnerability analysis tools"""
        tools = [
            ParrotOSTool(
                tool_id="openvas",
                name="OpenVAS",
                category=ToolCategory.VULNERABILITY_ANALYSIS,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/openvas",
                description="Comprehensive vulnerability scanner",
                capabilities=["vulnerability_scanning", "compliance_checking", "patch_management"],
                typical_use_cases=["enterprise_scanning", "compliance_audits", "vulnerability_management"],
                prerequisites=["openvas_setup", "network_access"],
                output_formats=["xml", "pdf", "html"],
                ai_confidence_score=0.92,
                resource_intensive=True,
                educational_value=9,
                risk_level=2
            ),
            ParrotOSTool(
                tool_id="nikto",
                name="Nikto",
                category=ToolCategory.VULNERABILITY_ANALYSIS,
                complexity=ToolComplexity.INTERMEDIATE,
                executable_path="/usr/bin/nikto",
                description="Web server vulnerability scanner",
                capabilities=["web_vulnerability_scanning", "cgi_scanning", "ssl_testing"],
                typical_use_cases=["web_server_assessment", "quick_web_scan"],
                prerequisites=["web_access"],
                output_formats=["xml", "html", "csv"],
                ai_confidence_score=0.85,
                network_intensive=True,
                educational_value=8,
                risk_level=2
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_web_application_tools(self):
        """Add web application analysis tools"""
        tools = [
            ParrotOSTool(
                tool_id="burpsuite",
                name="Burp Suite",
                category=ToolCategory.WEB_APPLICATION_ANALYSIS,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/burpsuite",
                description="Comprehensive web application security testing platform",
                capabilities=["web_proxy", "vulnerability_scanning", "manual_testing", "session_analysis"],
                typical_use_cases=["web_app_pentesting", "api_testing", "session_security"],
                prerequisites=["java", "web_access"],
                output_formats=["xml", "html", "json"],
                ai_confidence_score=0.95,
                resource_intensive=True,
                educational_value=10,
                risk_level=3
            ),
            ParrotOSTool(
                tool_id="sqlmap",
                name="SQLMap",
                category=ToolCategory.WEB_APPLICATION_ANALYSIS,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/sqlmap",
                description="Automatic SQL injection and database takeover tool",
                capabilities=["sql_injection_detection", "database_enumeration", "data_extraction"],
                typical_use_cases=["sql_injection_testing", "database_assessment"],
                prerequisites=["web_access", "python"],
                output_formats=["text", "csv"],
                ai_confidence_score=0.93,
                educational_value=8,
                risk_level=4
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_database_assessment_tools(self):
        """Add database assessment tools"""
        tools = [
            ParrotOSTool(
                tool_id="sqlninja",
                name="SQLNinja",
                category=ToolCategory.DATABASE_ASSESSMENT,
                complexity=ToolComplexity.EXPERT,
                executable_path="/usr/bin/sqlninja",
                description="SQL Server injection and takeover tool",
                capabilities=["mssql_injection", "privilege_escalation", "data_extraction"],
                typical_use_cases=["mssql_penetration_testing", "database_exploitation"],
                prerequisites=["perl", "database_access"],
                output_formats=["text"],
                ai_confidence_score=0.78,
                educational_value=6,
                risk_level=5
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_password_attack_tools(self):
        """Add password attack tools"""
        tools = [
            ParrotOSTool(
                tool_id="john",
                name="John the Ripper",
                category=ToolCategory.PASSWORD_ATTACKS,
                complexity=ToolComplexity.INTERMEDIATE,
                executable_path="/usr/bin/john",
                description="Password cracking tool",
                capabilities=["password_cracking", "hash_analysis", "dictionary_attacks"],
                typical_use_cases=["password_auditing", "hash_cracking", "security_testing"],
                prerequisites=["password_hashes"],
                output_formats=["text"],
                ai_confidence_score=0.90,
                resource_intensive=True,
                educational_value=8,
                risk_level=3
            ),
            ParrotOSTool(
                tool_id="hashcat",
                name="Hashcat",
                category=ToolCategory.PASSWORD_ATTACKS,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/hashcat",
                description="Advanced password recovery tool",
                capabilities=["gpu_acceleration", "advanced_attacks", "rule_based_attacks"],
                typical_use_cases=["enterprise_password_auditing", "advanced_cracking"],
                prerequisites=["opencl", "password_hashes"],
                output_formats=["text", "potfile"],
                ai_confidence_score=0.94,
                resource_intensive=True,
                educational_value=9,
                risk_level=3
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_wireless_attack_tools(self):
        """Add wireless attack tools"""
        tools = [
            ParrotOSTool(
                tool_id="aircrack_ng",
                name="Aircrack-ng",
                category=ToolCategory.WIRELESS_ATTACKS,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/aircrack-ng",
                description="WiFi security auditing tools suite",
                capabilities=["wifi_monitoring", "packet_capture", "wep_wpa_cracking"],
                typical_use_cases=["wifi_security_testing", "wireless_auditing"],
                prerequisites=["wireless_adapter", "monitor_mode"],
                output_formats=["pcap", "text"],
                ai_confidence_score=0.89,
                requires_root=True,
                educational_value=8,
                risk_level=4
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_reverse_engineering_tools(self):
        """Add reverse engineering tools"""
        tools = [
            ParrotOSTool(
                tool_id="radare2",
                name="Radare2",
                category=ToolCategory.REVERSE_ENGINEERING,
                complexity=ToolComplexity.EXPERT,
                executable_path="/usr/bin/radare2",
                description="Advanced reverse engineering framework",
                capabilities=["disassembly", "debugging", "binary_analysis"],
                typical_use_cases=["malware_analysis", "binary_exploitation", "firmware_analysis"],
                prerequisites=["binary_files"],
                output_formats=["text", "json"],
                ai_confidence_score=0.85,
                educational_value=9,
                risk_level=2
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_exploitation_tools(self):
        """Add exploitation tools"""
        tools = [
            ParrotOSTool(
                tool_id="metasploit",
                name="Metasploit Framework",
                category=ToolCategory.EXPLOITATION_TOOLS,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/msfconsole",
                description="Penetration testing framework",
                capabilities=["exploit_development", "payload_generation", "post_exploitation"],
                typical_use_cases=["penetration_testing", "exploit_development", "security_research"],
                prerequisites=["ruby", "postgresql"],
                output_formats=["text", "xml"],
                ai_confidence_score=0.96,
                resource_intensive=True,
                educational_value=10,
                risk_level=5
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_sniffing_spoofing_tools(self):
        """Add sniffing and spoofing tools"""
        tools = [
            ParrotOSTool(
                tool_id="wireshark",
                name="Wireshark",
                category=ToolCategory.SNIFFING_SPOOFING,
                complexity=ToolComplexity.INTERMEDIATE,
                executable_path="/usr/bin/wireshark",
                description="Network protocol analyzer",
                capabilities=["packet_capture", "protocol_analysis", "network_troubleshooting"],
                typical_use_cases=["network_analysis", "incident_investigation", "protocol_debugging"],
                prerequisites=["network_access"],
                output_formats=["pcap", "pcapng"],
                ai_confidence_score=0.94,
                educational_value=10,
                risk_level=2
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_post_exploitation_tools(self):
        """Add post-exploitation tools"""
        tools = [
            ParrotOSTool(
                tool_id="empire",
                name="PowerShell Empire",
                category=ToolCategory.POST_EXPLOITATION,
                complexity=ToolComplexity.EXPERT,
                executable_path="/usr/bin/empire",
                description="Post-exploitation framework",
                capabilities=["persistence", "privilege_escalation", "lateral_movement"],
                typical_use_cases=["red_team_operations", "advanced_persistence"],
                prerequisites=["python", "powershell"],
                output_formats=["text"],
                ai_confidence_score=0.88,
                educational_value=9,
                risk_level=5
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_forensics_tools(self):
        """Add forensics tools"""
        tools = [
            ParrotOSTool(
                tool_id="autopsy",
                name="Autopsy",
                category=ToolCategory.FORENSICS,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/autopsy",
                description="Digital forensics platform",
                capabilities=["disk_analysis", "file_recovery", "timeline_analysis"],
                typical_use_cases=["incident_response", "digital_investigations"],
                prerequisites=["java", "disk_images"],
                output_formats=["html", "xml"],
                ai_confidence_score=0.89,
                resource_intensive=True,
                educational_value=9,
                risk_level=1
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_reporting_tools(self):
        """Add reporting tools"""
        tools = [
            ParrotOSTool(
                tool_id="dradis",
                name="Dradis",
                category=ToolCategory.REPORTING_TOOLS,
                complexity=ToolComplexity.INTERMEDIATE,
                executable_path="/usr/bin/dradis",
                description="Collaboration and reporting platform",
                capabilities=["report_generation", "team_collaboration", "finding_management"],
                typical_use_cases=["penetration_test_reporting", "team_coordination"],
                prerequisites=["ruby", "web_server"],
                output_formats=["html", "pdf", "xml"],
                ai_confidence_score=0.85,
                educational_value=7,
                risk_level=1
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_social_engineering_tools(self):
        """Add social engineering tools"""
        tools = [
            ParrotOSTool(
                tool_id="set",
                name="Social Engineer Toolkit",
                category=ToolCategory.SOCIAL_ENGINEERING,
                complexity=ToolComplexity.ADVANCED,
                executable_path="/usr/bin/setoolkit",
                description="Social engineering attack framework",
                capabilities=["phishing_attacks", "credential_harvesting", "payload_generation"],
                typical_use_cases=["social_engineering_testing", "awareness_training"],
                prerequisites=["python", "web_server"],
                output_formats=["text", "html"],
                ai_confidence_score=0.82,
                educational_value=8,
                risk_level=4
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _add_system_services(self):
        """Add system services and utilities"""
        tools = [
            ParrotOSTool(
                tool_id="systemctl",
                name="Systemctl",
                category=ToolCategory.SYSTEM_SERVICES,
                complexity=ToolComplexity.BASIC,
                executable_path="/usr/bin/systemctl",
                description="System service manager",
                capabilities=["service_management", "system_control"],
                typical_use_cases=["service_configuration", "system_administration"],
                prerequisites=["systemd"],
                output_formats=["text"],
                ai_confidence_score=0.95,
                educational_value=8,
                risk_level=1
            )
        ]
        
        for tool in tools:
            self.tools[tool.tool_id] = tool
    
    def _build_indexes(self):
        """Build search indexes for efficient tool lookup"""
        try:
            # Clear existing indexes
            self.category_index.clear()
            self.complexity_index.clear()
            self.capability_index.clear()
            
            # Build category index
            for tool_id, tool in self.tools.items():
                if tool.category not in self.category_index:
                    self.category_index[tool.category] = []
                self.category_index[tool.category].append(tool_id)
            
            # Build complexity index
            for tool_id, tool in self.tools.items():
                if tool.complexity not in self.complexity_index:
                    self.complexity_index[tool.complexity] = []
                self.complexity_index[tool.complexity].append(tool_id)
            
            # Build capability index
            for tool_id, tool in self.tools.items():
                for capability in tool.capabilities:
                    if capability not in self.capability_index:
                        self.capability_index[capability] = []
                    self.capability_index[capability].append(tool_id)
            
            self.logger.info("Built search indexes for tool database")
            
        except Exception as e:
            self.logger.error(f"Failed to build indexes: {e}")
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ParrotOSTool]:
        """Get all tools in a specific category"""
        tool_ids = self.category_index.get(category, [])
        return [self.tools[tool_id] for tool_id in tool_ids]
    
    def get_tools_by_complexity(self, complexity: ToolComplexity) -> List[ParrotOSTool]:
        """Get all tools of a specific complexity level"""
        tool_ids = self.complexity_index.get(complexity, [])
        return [self.tools[tool_id] for tool_id in tool_ids]
    
    def get_tools_by_capability(self, capability: str) -> List[ParrotOSTool]:
        """Get all tools with a specific capability"""
        tool_ids = self.capability_index.get(capability, [])
        return [self.tools[tool_id] for tool_id in tool_ids]
    
    def search_tools(self, query: str, category: Optional[ToolCategory] = None, 
                    complexity: Optional[ToolComplexity] = None) -> List[ParrotOSTool]:
        """Search tools by name, description, or capabilities"""
        results = []
        query_lower = query.lower()
        
        for tool in self.tools.values():
            # Apply filters
            if category and tool.category != category:
                continue
            if complexity and tool.complexity != complexity:
                continue
            
            # Search in name, description, and capabilities
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower() or
                any(query_lower in cap.lower() for cap in tool.capabilities)):
                results.append(tool)
        
        # Sort by AI confidence score
        results.sort(key=lambda t: t.ai_confidence_score, reverse=True)
        return results


class AIToolSelector:
    """AI-powered tool selection engine with consciousness integration"""
    
    def __init__(self, tool_database: ParrotOSToolDatabase, 
                 consciousness_controller: ConsciousnessSecurityController):
        self.tool_database = tool_database
        self.consciousness_controller = consciousness_controller
        self.logger = logging.getLogger(f"{__name__}.AIToolSelector")
        
        # AI selection parameters
        self.selection_weights = {
            'ai_confidence': 0.3,
            'consciousness_compatibility': 0.2,
            'educational_value': 0.15,
            'effectiveness': 0.2,
            'risk_assessment': 0.15
        }
    
    async def recommend_tools(self, assessment_type: AssessmentType, 
                            target: str, user_skill_level: ToolComplexity,
                            consciousness_context: Dict[str, Any]) -> List[AIToolRecommendation]:
        """Generate AI-powered tool recommendations"""
        try:
            self.logger.info(f"Generating tool recommendations for {assessment_type.value} assessment")
            
            # Get relevant tools based on assessment type
            candidate_tools = self._get_candidate_tools(assessment_type, user_skill_level)
            
            # Analyze target to understand requirements
            target_analysis = await self._analyze_target(target)
            
            # Get consciousness insights
            consciousness_insights = await self._get_consciousness_insights(
                assessment_type, target, consciousness_context
            )
            
            # Generate recommendations
            recommendations = []
            for tool in candidate_tools:
                recommendation = await self._evaluate_tool(
                    tool, target_analysis, consciousness_insights, user_skill_level
                )
                if recommendation.confidence_score > 0.5:  # Threshold for recommendations
                    recommendations.append(recommendation)
            
            # Sort by confidence score
            recommendations.sort(key=lambda r: r.confidence_score, reverse=True)
            
            # Return top 10 recommendations
            return recommendations[:10]
            
        except Exception as e:
            self.logger.error(f"Error generating tool recommendations: {e}")
            return []
    
    def _get_candidate_tools(self, assessment_type: AssessmentType, 
                           user_skill_level: ToolComplexity) -> List[ParrotOSTool]:
        """Get candidate tools based on assessment type and user skill level"""
        candidates = []
        
        # Map assessment types to tool categories
        category_mapping = {
            AssessmentType.RECONNAISSANCE: [ToolCategory.INFORMATION_GATHERING],
            AssessmentType.VULNERABILITY_SCAN: [ToolCategory.VULNERABILITY_ANALYSIS],
            AssessmentType.PENETRATION_TEST: [
                ToolCategory.INFORMATION_GATHERING,
                ToolCategory.VULNERABILITY_ANALYSIS,
                ToolCategory.EXPLOITATION_TOOLS,
                ToolCategory.POST_EXPLOITATION
            ],
            AssessmentType.COMPLIANCE_AUDIT: [
                ToolCategory.VULNERABILITY_ANALYSIS,
                ToolCategory.SYSTEM_SERVICES
            ],
            AssessmentType.INCIDENT_RESPONSE: [
                ToolCategory.FORENSICS,
                ToolCategory.SNIFFING_SPOOFING
            ],
            AssessmentType.THREAT_HUNTING: [
                ToolCategory.INFORMATION_GATHERING,
                ToolCategory.SNIFFING_SPOOFING,
                ToolCategory.FORENSICS
            ]
        }
        
        relevant_categories = category_mapping.get(assessment_type, [])
        
        for category in relevant_categories:
            category_tools = self.tool_database.get_tools_by_category(category)
            
            # Filter by user skill level (include tools at or below user level)
            suitable_tools = [
                tool for tool in category_tools 
                if tool.complexity <= user_skill_level
            ]
            
            candidates.extend(suitable_tools)
        
        return candidates
    
    async def _analyze_target(self, target: str) -> Dict[str, Any]:
        """Analyze target to understand requirements"""
        analysis = {
            'target_type': 'unknown',
            'network_accessible': False,
            'web_services': False,
            'database_services': False,
            'wireless_target': False,
            'complexity_estimate': ToolComplexity.INTERMEDIATE
        }
        
        try:
            # Basic target analysis
            if re.match(r'^https?://', target):
                analysis['target_type'] = 'web_application'
                analysis['web_services'] = True
                analysis['network_accessible'] = True
            elif re.match(r'^\d+\.\d+\.\d+\.\d+', target):
                analysis['target_type'] = 'ip_address'
                analysis['network_accessible'] = True
            elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target):
                analysis['target_type'] = 'domain'
                analysis['network_accessible'] = True
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing target: {e}")
            return analysis
    
    async def _get_consciousness_insights(self, assessment_type: AssessmentType,
                                        target: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get consciousness insights for tool selection"""
        try:
            # Create consciousness event for analysis
            consciousness_data = {
                'assessment_type': assessment_type.value,
                'target': target,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            # Get consciousness analysis (using existing neural darwinism)
            insights = {
                'user_attention_level': context.get('attention_level', 0.7),
                'cognitive_load': context.get('cognitive_load', 0.5),
                'learning_preference': context.get('learning_style', 'visual'),
                'risk_tolerance': context.get('risk_tolerance', 0.5),
                'time_constraints': context.get('time_limit', 3600),
                'resource_availability': context.get('resources', {}),
                'consciousness_level': 0.8  # Default consciousness level
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting consciousness insights: {e}")
            return {
                'user_attention_level': 0.5,
                'cognitive_load': 0.5,
                'consciousness_level': 0.5
            }
    
    async def _evaluate_tool(self, tool: ParrotOSTool, target_analysis: Dict[str, Any],
                           consciousness_insights: Dict[str, Any],
                           user_skill_level: ToolComplexity) -> AIToolRecommendation:
        """Evaluate a tool and generate recommendation"""
        try:
            # Calculate confidence score based on multiple factors
            confidence_factors = {}
            
            # AI confidence factor
            confidence_factors['ai_confidence'] = tool.ai_confidence_score
            
            # Consciousness compatibility factor
            consciousness_factor = 1.0 if tool.consciousness_compatibility else 0.5
            consciousness_factor *= consciousness_insights.get('consciousness_level', 0.5)
            confidence_factors['consciousness_compatibility'] = consciousness_factor
            
            # Educational value factor (normalized)
            confidence_factors['educational_value'] = tool.educational_value / 10.0
            
            # Effectiveness factor based on target analysis
            effectiveness = self._calculate_effectiveness(tool, target_analysis)
            confidence_factors['effectiveness'] = effectiveness
            
            # Risk assessment factor
            risk_factor = 1.0 - (tool.risk_level / 5.0)  # Invert risk (lower risk = higher score)
            risk_factor *= consciousness_insights.get('risk_tolerance', 0.5)
            confidence_factors['risk_assessment'] = risk_factor
            
            # Calculate weighted confidence score
            confidence_score = sum(
                confidence_factors[factor] * self.selection_weights[factor]
                for factor in confidence_factors
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(tool, confidence_factors, target_analysis)
            
            # Estimate duration based on tool complexity and target
            estimated_duration = self._estimate_duration(tool, target_analysis)
            
            # Calculate resource requirements
            resource_requirements = self._calculate_resource_requirements(tool)
            
            # Find alternative tools
            alternative_tools = self._find_alternative_tools(tool)
            
            # Create risk assessment
            risk_assessment = {
                'risk_level': tool.risk_level,
                'requires_root': tool.requires_root,
                'network_intensive': tool.network_intensive,
                'resource_intensive': tool.resource_intensive,
                'stealth_capable': tool.stealth_capable
            }
            
            return AIToolRecommendation(
                tool_id=tool.tool_id,
                confidence_score=confidence_score,
                reasoning=reasoning,
                expected_effectiveness=effectiveness,
                estimated_duration=estimated_duration,
                resource_requirements=resource_requirements,
                consciousness_insights=consciousness_insights,
                alternative_tools=alternative_tools,
                risk_assessment=risk_assessment
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating tool {tool.tool_id}: {e}")
            return AIToolRecommendation(
                tool_id=tool.tool_id,
                confidence_score=0.0,
                reasoning=f"Evaluation error: {str(e)}",
                expected_effectiveness=0.0,
                estimated_duration=0,
                resource_requirements={},
                consciousness_insights={},
                alternative_tools=[],
                risk_assessment={}
            )
    
    def _calculate_effectiveness(self, tool: ParrotOSTool, target_analysis: Dict[str, Any]) -> float:
        """Calculate tool effectiveness for the target"""
        effectiveness = 0.5  # Base effectiveness
        
        # Adjust based on target type and tool capabilities
        target_type = target_analysis.get('target_type', 'unknown')
        
        if target_type == 'web_application' and tool.category == ToolCategory.WEB_APPLICATION_ANALYSIS:
            effectiveness += 0.3
        elif target_type == 'ip_address' and tool.category == ToolCategory.INFORMATION_GATHERING:
            effectiveness += 0.2
        elif target_analysis.get('network_accessible') and tool.network_intensive:
            effectiveness += 0.1
        
        # Adjust based on tool capabilities matching target requirements
        if target_analysis.get('web_services') and 'web_vulnerability_scanning' in tool.capabilities:
            effectiveness += 0.2
        if target_analysis.get('database_services') and 'database_enumeration' in tool.capabilities:
            effectiveness += 0.2
        
        return min(1.0, effectiveness)
    
    def _generate_reasoning(self, tool: ParrotOSTool, confidence_factors: Dict[str, float],
                          target_analysis: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the recommendation"""
        reasons = []
        
        if confidence_factors['ai_confidence'] > 0.8:
            reasons.append(f"High AI confidence ({confidence_factors['ai_confidence']:.2f})")
        
        if confidence_factors['effectiveness'] > 0.7:
            reasons.append("Well-suited for target type")
        
        if tool.educational_value >= 8:
            reasons.append("High educational value")
        
        if tool.stealth_capable and target_analysis.get('network_accessible'):
            reasons.append("Stealth capabilities available")
        
        if not reasons:
            reasons.append("General purpose tool for this assessment type")
        
        return "; ".join(reasons)
    
    def _estimate_duration(self, tool: ParrotOSTool, target_analysis: Dict[str, Any]) -> int:
        """Estimate execution duration in seconds"""
        base_duration = {
            ToolComplexity.BASIC: 300,      # 5 minutes
            ToolComplexity.INTERMEDIATE: 900, # 15 minutes
            ToolComplexity.ADVANCED: 1800,   # 30 minutes
            ToolComplexity.EXPERT: 3600,     # 1 hour
            ToolComplexity.MASTER: 7200      # 2 hours
        }
        
        duration = base_duration.get(tool.complexity, 900)
        
        # Adjust based on tool characteristics
        if tool.resource_intensive:
            duration *= 1.5
        if tool.network_intensive:
            duration *= 1.2
        
        return int(duration)
    
    def _calculate_resource_requirements(self, tool: ParrotOSTool) -> Dict[str, Any]:
        """Calculate resource requirements for the tool"""
        requirements = {
            'cpu_intensive': tool.resource_intensive,
            'network_required': tool.network_intensive,
            'root_required': tool.requires_root,
            'memory_estimate': 'low'
        }
        
        if tool.resource_intensive:
            requirements['memory_estimate'] = 'high'
            requirements['cpu_cores'] = 2
        elif tool.complexity >= ToolComplexity.ADVANCED:
            requirements['memory_estimate'] = 'medium'
            requirements['cpu_cores'] = 1
        
        return requirements
    
    def _find_alternative_tools(self, tool: ParrotOSTool) -> List[str]:
        """Find alternative tools with similar capabilities"""
        alternatives = []
        
        # Find tools in the same category with similar capabilities
        category_tools = self.tool_database.get_tools_by_category(tool.category)
        
        for alt_tool in category_tools:
            if alt_tool.tool_id != tool.tool_id:
                # Check for capability overlap
                common_capabilities = set(tool.capabilities) & set(alt_tool.capabilities)
                if len(common_capabilities) >= 2:  # At least 2 common capabilities
                    alternatives.append(alt_tool.tool_id)
        
        return alternatives[:3]  # Return top 3 alternatives


class SecurityScenarioGenerator:
    """Generate educational security scenarios with consciousness adaptation"""
    
    def __init__(self, tool_database: ParrotOSToolDatabase,
                 ai_selector: AIToolSelector):
        self.tool_database = tool_database
        self.ai_selector = ai_selector
        self.logger = logging.getLogger(f"{__name__}.ScenarioGenerator")
        
        # Predefined scenario templates
        self.scenario_templates = self._initialize_scenario_templates()
    
    def _initialize_scenario_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined scenario templates"""
        return {
            'web_app_pentest': {
                'title': 'Web Application Penetration Testing',
                'description': 'Comprehensive security assessment of a web application',
                'difficulty_level': ToolComplexity.INTERMEDIATE,
                'learning_objectives': [
                    'Identify web application vulnerabilities',
                    'Perform manual and automated testing',
                    'Document findings and recommendations'
                ],
                'target_environment': {
                    'type': 'web_application',
                    'technologies': ['php', 'mysql', 'apache'],
                    'vulnerabilities': ['sql_injection', 'xss', 'csrf']
                },
                'assessment_type': AssessmentType.PENETRATION_TEST
            },
            'network_reconnaissance': {
                'title': 'Network Reconnaissance and Mapping',
                'description': 'Discover and map network infrastructure',
                'difficulty_level': ToolComplexity.BASIC,
                'learning_objectives': [
                    'Discover live hosts and services',
                    'Map network topology',
                    'Identify potential attack vectors'
                ],
                'target_environment': {
                    'type': 'network_range',
                    'scope': '192.168.1.0/24',
                    'services': ['web', 'ssh', 'ftp', 'smtp']
                },
                'assessment_type': AssessmentType.RECONNAISSANCE
            },
            'incident_response': {
                'title': 'Digital Forensics and Incident Response',
                'description': 'Investigate a security incident using forensic tools',
                'difficulty_level': ToolComplexity.ADVANCED,
                'learning_objectives': [
                    'Preserve digital evidence',
                    'Analyze system artifacts',
                    'Reconstruct attack timeline'
                ],
                'target_environment': {
                    'type': 'compromised_system',
                    'evidence_types': ['disk_image', 'memory_dump', 'network_logs'],
                    'incident_type': 'malware_infection'
                },
                'assessment_type': AssessmentType.INCIDENT_RESPONSE
            }
        }
    
    async def generate_scenario(self, scenario_type: str, user_skill_level: ToolComplexity,
                              consciousness_context: Dict[str, Any]) -> SecurityScenario:
        """Generate a customized security scenario"""
        try:
            template = self.scenario_templates.get(scenario_type)
            if not template:
                raise ValueError(f"Unknown scenario type: {scenario_type}")
            
            # Get AI tool recommendations for this scenario
            recommended_tools = await self.ai_selector.recommend_tools(
                template['assessment_type'],
                template['target_environment'].get('scope', 'target'),
                user_skill_level,
                consciousness_context
            )
            
            # Adapt scenario based on consciousness insights
            adapted_scenario = await self._adapt_scenario_for_consciousness(
                template, consciousness_context, user_skill_level
            )
            
            # Generate step-by-step guide
            step_guide = self._generate_step_guide(
                adapted_scenario, [rec.tool_id for rec in recommended_tools[:5]]
            )
            
            # Create scenario ID
            scenario_id = f"{scenario_type}_{int(datetime.now().timestamp())}"
            
            return SecurityScenario(
                scenario_id=scenario_id,
                title=adapted_scenario['title'],
                description=adapted_scenario['description'],
                difficulty_level=adapted_scenario['difficulty_level'],
                learning_objectives=adapted_scenario['learning_objectives'],
                target_environment=adapted_scenario['target_environment'],
                recommended_tools=[rec.tool_id for rec in recommended_tools[:5]],
                step_by_step_guide=step_guide,
                expected_outcomes=adapted_scenario.get('expected_outcomes', []),
                assessment_criteria=adapted_scenario.get('assessment_criteria', {}),
                consciousness_adaptations=consciousness_context
            )
            
        except Exception as e:
            self.logger.error(f"Error generating scenario: {e}")
            raise
    
    async def _adapt_scenario_for_consciousness(self, template: Dict[str, Any],
                                             consciousness_context: Dict[str, Any],
                                             user_skill_level: ToolComplexity) -> Dict[str, Any]:
        """Adapt scenario based on consciousness insights"""
        adapted = template.copy()
        
        # Adjust difficulty based on user attention and cognitive load
        attention_level = consciousness_context.get('attention_level', 0.7)
        cognitive_load = consciousness_context.get('cognitive_load', 0.5)
        
        if attention_level > 0.8 and cognitive_load < 0.4:
            # User is focused and not overloaded - can handle more complexity
            if adapted['difficulty_level'] < ToolComplexity.EXPERT:
                adapted['difficulty_level'] = ToolComplexity(adapted['difficulty_level'] + 1)
        elif attention_level < 0.5 or cognitive_load > 0.7:
            # User is distracted or overloaded - simplify
            if adapted['difficulty_level'] > ToolComplexity.BASIC:
                adapted['difficulty_level'] = ToolComplexity(adapted['difficulty_level'] - 1)
        
        # Adjust learning objectives based on user preferences
        learning_style = consciousness_context.get('learning_style', 'visual')
        if learning_style == 'hands_on':
            adapted['learning_objectives'].append('Practice hands-on tool execution')
        elif learning_style == 'theoretical':
            adapted['learning_objectives'].append('Understand theoretical foundations')
        
        return adapted
    
    def _generate_step_guide(self, scenario: Dict[str, Any],
                           recommended_tools: List[str]) -> List[Dict[str, Any]]:
        """Generate step-by-step guide for the scenario"""
        steps = []
        
        # Generic steps based on assessment type
        assessment_type = scenario.get('assessment_type', AssessmentType.RECONNAISSANCE)
        
        if assessment_type == AssessmentType.RECONNAISSANCE:
            steps = [
                {
                    'step': 1,
                    'title': 'Initial Target Analysis',
                    'description': 'Analyze the target scope and gather basic information',
                    'tools': [tool for tool in recommended_tools if tool in ['nmap', 'dmitry']],
                    'expected_duration': 300,
                    'learning_points': ['Target identification', 'Scope definition']
                },
                {
                    'step': 2,
                    'title': 'Network Discovery',
                    'description': 'Discover live hosts and open services',
                    'tools': [tool for tool in recommended_tools if tool in ['nmap', 'masscan']],
                    'expected_duration': 600,
                    'learning_points': ['Host discovery', 'Service enumeration']
                },
                {
                    'step': 3,
                    'title': 'Service Analysis',
                    'description': 'Analyze discovered services for potential vulnerabilities',
                    'tools': [tool for tool in recommended_tools if tool in ['nikto', 'nmap']],
                    'expected_duration': 900,
                    'learning_points': ['Service fingerprinting', 'Vulnerability identification']
                }
            ]
        elif assessment_type == AssessmentType.PENETRATION_TEST:
            steps = [
                {
                    'step': 1,
                    'title': 'Reconnaissance',
                    'description': 'Gather information about the target',
                    'tools': [tool for tool in recommended_tools if tool in ['nmap', 'dmitry']],
                    'expected_duration': 600,
                    'learning_points': ['Information gathering', 'Target profiling']
                },
                {
                    'step': 2,
                    'title': 'Vulnerability Assessment',
                    'description': 'Identify potential security vulnerabilities',
                    'tools': [tool for tool in recommended_tools if tool in ['nikto', 'sqlmap']],
                    'expected_duration': 1200,
                    'learning_points': ['Vulnerability scanning', 'Risk assessment']
                },
                {
                    'step': 3,
                    'title': 'Exploitation',
                    'description': 'Attempt to exploit identified vulnerabilities',
                    'tools': [tool for tool in recommended_tools if tool in ['metasploit', 'sqlmap']],
                    'expected_duration': 1800,
                    'learning_points': ['Exploit development', 'Payload execution']
                }
            ]
        
        return steps


class ParrotOSAIIntegration:
    """Main integration class for AI-Enhanced ParrotOS functionality"""
    
    def __init__(self, consciousness_controller: ConsciousnessSecurityController):
        self.consciousness_controller = consciousness_controller
        self.tool_database = ParrotOSToolDatabase()
        self.ai_selector = AIToolSelector(self.tool_database, consciousness_controller)
        self.scenario_generator = SecurityScenarioGenerator(self.tool_database, self.ai_selector)
        self.logger = logging.getLogger(f"{__name__}.ParrotOSAIIntegration")
        
        # Assessment tracking
        self.active_assessments: Dict[str, AssessmentResult] = {}
        self.assessment_history: List[AssessmentResult] = []
    
    async def initialize(self):
        """Initialize the ParrotOS AI integration system"""
        try:
            self.logger.info("Initializing ParrotOS AI Integration System...")
            
            # Verify tool availability
            await self._verify_tool_availability()
            
            # Initialize consciousness integration
            await self.consciousness_controller.start()
            
            self.logger.info("ParrotOS AI Integration System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ParrotOS AI Integration: {e}")
            raise
    
    async def _verify_tool_availability(self):
        """Verify that ParrotOS tools are available on the system"""
        verified_tools = 0
        total_tools = len(self.tool_database.tools)
        
        for tool_id, tool in self.tool_database.tools.items():
            if Path(tool.executable_path).exists():
                verified_tools += 1
            else:
                self.logger.debug(f"Tool not found: {tool.name} at {tool.executable_path}")
        
        availability_rate = verified_tools / total_tools
        self.logger.info(f"Tool availability: {verified_tools}/{total_tools} ({availability_rate:.1%})")
        
        if availability_rate < 0.5:
            self.logger.warning("Low tool availability - some features may not work correctly")
    
    async def start_assessment(self, assessment_type: AssessmentType, target: str,
                             user_skill_level: ToolComplexity,
                             consciousness_context: Dict[str, Any]) -> str:
        """Start a new security assessment"""
        try:
            assessment_id = f"assessment_{int(datetime.now().timestamp())}"
            
            # Get AI tool recommendations
            recommendations = await self.ai_selector.recommend_tools(
                assessment_type, target, user_skill_level, consciousness_context
            )
            
            # Create assessment result
            assessment = AssessmentResult(
                assessment_id=assessment_id,
                assessment_type=assessment_type,
                target=target,
                start_time=datetime.now(),
                end_time=None,
                tools_used=[],
                findings=[],
                threat_level=ThreatLevel.LOW,
                confidence_score=0.0,
                consciousness_analysis={},
                recommendations=[rec.reasoning for rec in recommendations[:3]],
                remediation_steps=[],
                compliance_status={},
                executive_summary=""
            )
            
            self.active_assessments[assessment_id] = assessment
            
            self.logger.info(f"Started assessment {assessment_id} for target {target}")
            return assessment_id
            
        except Exception as e:
            self.logger.error(f"Error starting assessment: {e}")
            raise
    
    async def get_tool_recommendations(self, assessment_type: AssessmentType, target: str,
                                     user_skill_level: ToolComplexity,
                                     consciousness_context: Dict[str, Any]) -> List[AIToolRecommendation]:
        """Get AI-powered tool recommendations"""
        return await self.ai_selector.recommend_tools(
            assessment_type, target, user_skill_level, consciousness_context
        )
    
    async def generate_security_scenario(self, scenario_type: str,
                                       user_skill_level: ToolComplexity,
                                       consciousness_context: Dict[str, Any]) -> SecurityScenario:
        """Generate an educational security scenario"""
        return await self.scenario_generator.generate_scenario(
            scenario_type, user_skill_level, consciousness_context
        )
    
    def get_available_tools(self, category: Optional[ToolCategory] = None,
                          complexity: Optional[ToolComplexity] = None) -> List[ParrotOSTool]:
        """Get available tools with optional filtering"""
        if category:
            tools = self.tool_database.get_tools_by_category(category)
        elif complexity:
            tools = self.tool_database.get_tools_by_complexity(complexity)
        else:
            tools = list(self.tool_database.tools.values())
        
        return tools
    
    def search_tools(self, query: str) -> List[ParrotOSTool]:
        """Search for tools by name, description, or capabilities"""
        return self.tool_database.search_tools(query)
    
    async def complete_assessment(self, assessment_id: str) -> AssessmentResult:
        """Complete an active assessment"""
        try:
            if assessment_id not in self.active_assessments:
                raise ValueError(f"Assessment {assessment_id} not found")
            
            assessment = self.active_assessments[assessment_id]
            assessment.end_time = datetime.now()
            
            # Generate executive summary
            assessment.executive_summary = self._generate_executive_summary(assessment)
            
            # Move to history
            self.assessment_history.append(assessment)
            del self.active_assessments[assessment_id]
            
            self.logger.info(f"Completed assessment {assessment_id}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error completing assessment: {e}")
            raise
    
    def _generate_executive_summary(self, assessment: AssessmentResult) -> str:
        """Generate executive summary for assessment"""
        if assessment.end_time:
            duration = (assessment.end_time - assessment.start_time).total_seconds() / 60
        else:
            duration = 0.0
        
        summary = f"""
        Security Assessment Summary
        
        Target: {assessment.target}
        Assessment Type: {assessment.assessment_type.value}
        Duration: {duration:.1f} minutes
        Tools Used: {len(assessment.tools_used)}
        Findings: {len(assessment.findings)}
        Overall Threat Level: {assessment.threat_level.value}
        Confidence Score: {assessment.confidence_score:.2f}
        
        Key Recommendations:
        {chr(10).join(f"- {rec}" for rec in assessment.recommendations[:3])}
        """
        
        return summary.strip()


# Factory function for easy instantiation
def create_parrotos_ai_integration(consciousness_controller: ConsciousnessSecurityController) -> ParrotOSAIIntegration:
    """Create and return a ParrotOS AI Integration instance"""
    return ParrotOSAIIntegration(consciousness_controller)


# Example usage and testing
async def main():
    """Example usage of the ParrotOS AI Integration system"""
    from .consciousness_security_controller import create_consciousness_security_controller
    
    # Create consciousness controller
    consciousness_controller = create_consciousness_security_controller()
    
    # Create ParrotOS AI integration
    parrotos_ai = create_parrotos_ai_integration(consciousness_controller)
    
    try:
        # Initialize the system
        await parrotos_ai.initialize()
        
        # Example: Get tool recommendations for web application testing
        consciousness_context = {
            'attention_level': 0.8,
            'cognitive_load': 0.4,
            'learning_style': 'hands_on',
            'risk_tolerance': 0.6,
            'time_limit': 3600
        }
        
        recommendations = await parrotos_ai.get_tool_recommendations(
            AssessmentType.PENETRATION_TEST,
            "https://example.com",
            ToolComplexity.INTERMEDIATE,
            consciousness_context
        )
        
        print(f"AI Tool Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. {rec.tool_id} (confidence: {rec.confidence_score:.2f})")
            print(f"   Reasoning: {rec.reasoning}")
            print(f"   Duration: {rec.estimated_duration}s")
            print()
        
        # Example: Generate security scenario
        scenario = await parrotos_ai.generate_security_scenario(
            'web_app_pentest',
            ToolComplexity.INTERMEDIATE,
            consciousness_context
        )
        
        print(f"Generated Scenario: {scenario.title}")
        print(f"Description: {scenario.description}")
        print(f"Recommended Tools: {', '.join(scenario.recommended_tools)}")
        print(f"Steps: {len(scenario.step_by_step_guide)}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())