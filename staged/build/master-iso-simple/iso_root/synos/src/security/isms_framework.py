#!/usr/bin/env python3
"""
Information Security Management System (ISMS) Framework
ISO 27001 compliant ISMS implementation for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta


class ISMSScope(Enum):
    """ISMS scope boundaries"""
    CORE_SYSTEM = "core_system"
    SECURITY_TOOLS = "security_tools"
    USER_DATA = "user_data"
    NETWORK_INFRASTRUCTURE = "network_infrastructure"
    CLOUD_SERVICES = "cloud_services"
    DEVELOPMENT_ENVIRONMENT = "development_environment"
    PRODUCTION_ENVIRONMENT = "production_environment"


class SecurityPolicyType(Enum):
    """Types of security policies"""
    INFORMATION_SECURITY_POLICY = "information_security_policy"
    ACCESS_CONTROL_POLICY = "access_control_policy"
    INCIDENT_RESPONSE_POLICY = "incident_response_policy"
    RISK_MANAGEMENT_POLICY = "risk_management_policy"
    BUSINESS_CONTINUITY_POLICY = "business_continuity_policy"
    ACCEPTABLE_USE_POLICY = "acceptable_use_policy"
    DATA_PROTECTION_POLICY = "data_protection_policy"
    VULNERABILITY_MANAGEMENT_POLICY = "vulnerability_management_policy"


@dataclass
class ISMSAsset:
    """Information asset in ISMS scope"""
    asset_id: str
    asset_name: str
    asset_type: str
    owner: str
    custodian: str
    classification: str  # Public, Internal, Confidential, Restricted
    location: str
    description: str
    dependencies: List[str]
    security_requirements: Dict[str, str]
    risk_level: str
    last_reviewed: float
    next_review: float


@dataclass
class SecurityPolicy:
    """Security policy document"""
    policy_id: str
    policy_type: SecurityPolicyType
    title: str
    version: str
    effective_date: float
    review_date: float
    owner: str
    approver: str
    scope: List[str]
    purpose: str
    policy_statements: List[str]
    procedures: List[str]
    roles_responsibilities: Dict[str, List[str]]
    compliance_requirements: List[str]
    exceptions: List[str]
    related_policies: List[str]
    approved: bool = False
    published: bool = False


class ISMSFramework:
    """
    Information Security Management System Framework
    Implements ISO 27001 compliant ISMS for Syn_OS
    """
    
    def __init__(self):
        """Initialize ISMS framework"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.isms_directory = "/var/lib/synos/isms"
        self.database_file = f"{self.isms_directory}/isms.db"
        
        # ISMS components
        self.scope_definition: Dict[str, Any] = {}
        self.assets: Dict[str, ISMSAsset] = {}
        self.policies: Dict[str, SecurityPolicy] = {}
        self.risk_register: Dict[str, Any] = {}
        
        # ISMS status
        self.isms_established = False
        self.last_management_review = 0.0
        self.next_management_review = 0.0
        
        # Initialize system
        asyncio.create_task(self._initialize_isms())
    
    async def _initialize_isms(self):
        """Initialize ISMS framework"""
        try:
            self.logger.info("Initializing ISMS framework...")
            
            # Create ISMS directory
            os.makedirs(self.isms_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Define ISMS scope
            await self._define_isms_scope()
            
            # Create security policies
            await self._create_security_policies()
            
            # Initialize asset inventory
            await self._initialize_asset_inventory()
            
            self.logger.info("ISMS framework initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing ISMS: {e}")
    
    async def _initialize_database(self):
        """Initialize ISMS database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Assets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS isms_assets (
                    asset_id TEXT PRIMARY KEY,
                    asset_name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    custodian TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    location TEXT,
                    description TEXT,
                    dependencies TEXT,
                    security_requirements TEXT,
                    risk_level TEXT,
                    last_reviewed REAL,
                    next_review REAL
                )
            ''')
            
            # Policies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_policies (
                    policy_id TEXT PRIMARY KEY,
                    policy_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    version TEXT NOT NULL,
                    effective_date REAL NOT NULL,
                    review_date REAL NOT NULL,
                    owner TEXT NOT NULL,
                    approver TEXT NOT NULL,
                    scope TEXT,
                    purpose TEXT,
                    policy_statements TEXT,
                    procedures TEXT,
                    roles_responsibilities TEXT,
                    compliance_requirements TEXT,
                    exceptions TEXT,
                    related_policies TEXT,
                    approved BOOLEAN NOT NULL DEFAULT 0,
                    published BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            
            # Risk register table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_register (
                    risk_id TEXT PRIMARY KEY,
                    risk_title TEXT NOT NULL,
                    risk_description TEXT,
                    asset_id TEXT,
                    threat_source TEXT,
                    vulnerability TEXT,
                    likelihood INTEGER,
                    impact INTEGER,
                    risk_level TEXT,
                    treatment_plan TEXT,
                    owner TEXT,
                    status TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_type ON isms_assets (asset_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_owner ON isms_assets (owner)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_policies_type ON security_policies (policy_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_risks_level ON risk_register (risk_level)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing ISMS database: {e}")
            raise
    
    async def _define_isms_scope(self):
        """Define ISMS scope and boundaries"""
        try:
            self.scope_definition = {
                "organization": "Syn_OS Development Team",
                "scope_statement": "Information Security Management System for Syn_OS consciousness-aware security operating system",
                "scope_boundaries": {
                    "included": [
                        "Syn_OS core operating system components",
                        "Security orchestration and monitoring tools",
                        "Consciousness processing and AI integration",
                        "User data and authentication systems",
                        "Development and production environments",
                        "Network infrastructure and cloud services",
                        "Third-party integrations and APIs"
                    ],
                    "excluded": [
                        "Third-party vendor internal systems",
                        "End-user personal devices",
                        "Public internet infrastructure",
                        "Physical security of user premises"
                    ]
                },
                "business_context": {
                    "primary_business": "Cybersecurity education and consciousness-aware computing",
                    "key_stakeholders": [
                        "Development team",
                        "Security researchers",
                        "Educational institutions",
                        "Cybersecurity professionals",
                        "End users"
                    ],
                    "regulatory_requirements": [
                        "ISO 27001 Information Security Management",
                        "ISO 9001 Quality Management",
                        "ISO 14001 Environmental Management",
                        "GDPR Data Protection (where applicable)",
                        "SOC 2 Type II (planned)"
                    ]
                },
                "information_assets": [
                    "Source code and intellectual property",
                    "User credentials and authentication data",
                    "Security logs and audit trails",
                    "Consciousness processing algorithms",
                    "Educational content and curricula",
                    "System configuration data",
                    "Vulnerability and threat intelligence"
                ],
                "scope_justification": "This scope encompasses all systems and processes critical to the security and operation of Syn_OS, ensuring comprehensive protection of information assets while maintaining focus on core business objectives.",
                "established_date": time.time(),
                "next_review_date": time.time() + (365 * 24 * 3600),  # Annual review
                "approved_by": "Interim CISO",
                "approval_date": time.time()
            }
            
            # Save scope definition
            scope_file = f"{self.isms_directory}/isms_scope.json"
            with open(scope_file, 'w') as f:
                json.dump(self.scope_definition, f, indent=2)
            
            self.logger.info("ISMS scope defined and documented")
            
        except Exception as e:
            self.logger.error(f"Error defining ISMS scope: {e}")
    
    async def _create_security_policies(self):
        """Create comprehensive security policy framework"""
        try:
            current_time = time.time()
            review_date = current_time + (365 * 24 * 3600)  # Annual review
            
            # 1. Information Security Policy (Master Policy)
            info_sec_policy = SecurityPolicy(
                policy_id="ISP-001",
                policy_type=SecurityPolicyType.INFORMATION_SECURITY_POLICY,
                title="Syn_OS Information Security Policy",
                version="1.0",
                effective_date=current_time,
                review_date=review_date,
                owner="Interim CISO",
                approver="CEO",
                scope=["All Syn_OS systems and personnel"],
                purpose="To establish the framework for information security management within Syn_OS organization",
                policy_statements=[
                    "Information security is a business enabler and critical success factor",
                    "All personnel are responsible for maintaining information security",
                    "Security controls must be proportionate to identified risks",
                    "Continuous improvement of security posture is mandatory",
                    "Compliance with legal and regulatory requirements is required",
                    "Security incidents must be reported and managed promptly",
                    "Regular security awareness training is mandatory for all personnel"
                ],
                procedures=[
                    "Annual risk assessment and treatment planning",
                    "Quarterly security policy review and updates",
                    "Monthly security metrics reporting to management",
                    "Immediate incident response and investigation",
                    "Regular security awareness training delivery",
                    "Continuous monitoring and threat detection"
                ],
                roles_responsibilities={
                    "CEO": ["Overall accountability for information security", "Resource allocation approval"],
                    "Interim CISO": ["ISMS implementation and maintenance", "Security strategy development"],
                    "Security Team": ["Day-to-day security operations", "Incident response execution"],
                    "All Personnel": ["Compliance with security policies", "Incident reporting"]
                },
                compliance_requirements=[
                    "ISO 27001:2013 Information Security Management",
                    "ISO 27002:2013 Code of Practice for Information Security Controls"
                ],
                exceptions=[],
                related_policies=["ACP-001", "IRP-001", "RMP-001"],
                approved=True,
                published=True
            )
            
            # 2. Access Control Policy
            access_control_policy = SecurityPolicy(
                policy_id="ACP-001",
                policy_type=SecurityPolicyType.ACCESS_CONTROL_POLICY,
                title="Access Control and Identity Management Policy",
                version="1.0",
                effective_date=current_time,
                review_date=review_date,
                owner="Security Lead",
                approver="Interim CISO",
                scope=["All Syn_OS systems and applications"],
                purpose="To ensure appropriate access controls are implemented and maintained",
                policy_statements=[
                    "Access to systems must be based on business need and least privilege principle",
                    "All user accounts must be properly authenticated and authorized",
                    "Multi-factor authentication is required for privileged accounts",
                    "Access rights must be regularly reviewed and updated",
                    "Shared accounts are prohibited except for specific approved cases",
                    "Access must be promptly revoked upon role change or termination"
                ],
                procedures=[
                    "User provisioning and de-provisioning process",
                    "Quarterly access rights review",
                    "Privileged access management procedures",
                    "Multi-factor authentication implementation",
                    "Emergency access procedures"
                ],
                roles_responsibilities={
                    "System Administrators": ["User account management", "Access rights implementation"],
                    "Managers": ["Access approval for team members", "Regular access review"],
                    "Users": ["Protecting credentials", "Reporting access issues"]
                },
                compliance_requirements=[
                    "ISO 27001 A.9 Access Control",
                    "ISO 27002 Access Control Guidelines"
                ],
                exceptions=["Emergency responder accounts with override capabilities"],
                related_policies=["ISP-001", "IRP-001"],
                approved=True,
                published=True
            )
            
            # 3. Incident Response Policy
            incident_response_policy = SecurityPolicy(
                policy_id="IRP-001",
                policy_type=SecurityPolicyType.INCIDENT_RESPONSE_POLICY,
                title="Security Incident Response Policy",
                version="1.0",
                effective_date=current_time,
                review_date=review_date,
                owner="Security Lead",
                approver="Interim CISO",
                scope=["All security incidents affecting Syn_OS"],
                purpose="To establish procedures for effective security incident response",
                policy_statements=[
                    "All security incidents must be reported immediately",
                    "Incident response team must be activated for critical incidents",
                    "Evidence preservation is mandatory for all incidents",
                    "Communication must follow established protocols",
                    "Lessons learned must be documented and shared",
                    "Recovery procedures must be tested and validated"
                ],
                procedures=[
                    "Incident detection and reporting",
                    "Incident classification and prioritization",
                    "Response team activation and coordination",
                    "Evidence collection and preservation",
                    "Communication and notification",
                    "Recovery and lessons learned"
                ],
                roles_responsibilities={
                    "Incident Response Team": ["Incident investigation", "Response coordination"],
                    "All Personnel": ["Incident reporting", "Response cooperation"],
                    "Management": ["Resource allocation", "Decision making"]
                },
                compliance_requirements=[
                    "ISO 27001 A.16 Information Security Incident Management"
                ],
                exceptions=[],
                related_policies=["ISP-001", "ACP-001"],
                approved=True,
                published=True
            )
            
            # 4. Risk Management Policy
            risk_management_policy = SecurityPolicy(
                policy_id="RMP-001",
                policy_type=SecurityPolicyType.RISK_MANAGEMENT_POLICY,
                title="Information Security Risk Management Policy",
                version="1.0",
                effective_date=current_time,
                review_date=review_date,
                owner="Risk Manager",
                approver="Interim CISO",
                scope=["All information security risks within ISMS scope"],
                purpose="To establish systematic approach to information security risk management",
                policy_statements=[
                    "Risk management is integral to all business processes",
                    "Risks must be identified, assessed, and treated appropriately",
                    "Risk appetite and tolerance levels must be defined",
                    "Regular risk assessments must be conducted",
                    "Risk treatment plans must be implemented and monitored",
                    "Residual risks must be accepted by appropriate authority"
                ],
                procedures=[
                    "Annual comprehensive risk assessment",
                    "Quarterly risk register review",
                    "Risk treatment planning and implementation",
                    "Risk monitoring and reporting",
                    "Risk acceptance procedures"
                ],
                roles_responsibilities={
                    "Risk Manager": ["Risk assessment coordination", "Risk register maintenance"],
                    "Asset Owners": ["Risk identification", "Treatment implementation"],
                    "Management": ["Risk acceptance", "Resource allocation"]
                },
                compliance_requirements=[
                    "ISO 27001 Clause 6.1 Risk Management",
                    "ISO 27005 Information Security Risk Management"
                ],
                exceptions=[],
                related_policies=["ISP-001"],
                approved=True,
                published=True
            )
            
            # Store policies
            policies = [info_sec_policy, access_control_policy, incident_response_policy, risk_management_policy]
            
            for policy in policies:
                await self._store_policy(policy)
                self.policies[policy.policy_id] = policy
            
            self.logger.info(f"Created {len(policies)} security policies")
            
        except Exception as e:
            self.logger.error(f"Error creating security policies: {e}")
    
    async def _store_policy(self, policy: SecurityPolicy):
        """Store security policy in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_policies
                (policy_id, policy_type, title, version, effective_date, review_date,
                 owner, approver, scope, purpose, policy_statements, procedures,
                 roles_responsibilities, compliance_requirements, exceptions,
                 related_policies, approved, published)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                policy.policy_id, policy.policy_type.value, policy.title, policy.version,
                policy.effective_date, policy.review_date, policy.owner, policy.approver,
                json.dumps(policy.scope), policy.purpose, json.dumps(policy.policy_statements),
                json.dumps(policy.procedures), json.dumps(policy.roles_responsibilities),
                json.dumps(policy.compliance_requirements), json.dumps(policy.exceptions),
                json.dumps(policy.related_policies), policy.approved, policy.published
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing policy: {e}")
    
    async def _initialize_asset_inventory(self):
        """Initialize information asset inventory"""
        try:
            current_time = time.time()
            next_review = current_time + (90 * 24 * 3600)  # Quarterly review
            
            # Define critical information assets
            assets = [
                ISMSAsset(
                    asset_id="AST-001",
                    asset_name="Syn_OS Source Code",
                    asset_type="Software",
                    owner="Development Team Lead",
                    custodian="System Administrator",
                    classification="Confidential",
                    location="Development Repository",
                    description="Complete source code for Syn_OS operating system",
                    dependencies=["AST-002", "AST-003"],
                    security_requirements={
                        "confidentiality": "High",
                        "integrity": "High",
                        "availability": "Medium"
                    },
                    risk_level="High",
                    last_reviewed=current_time,
                    next_review=next_review
                ),
                ISMSAsset(
                    asset_id="AST-002",
                    asset_name="User Authentication Database",
                    asset_type="Database",
                    owner="Security Lead",
                    custodian="Database Administrator",
                    classification="Restricted",
                    location="Production Environment",
                    description="User credentials and authentication data",
                    dependencies=["AST-004"],
                    security_requirements={
                        "confidentiality": "Critical",
                        "integrity": "Critical",
                        "availability": "High"
                    },
                    risk_level="Critical",
                    last_reviewed=current_time,
                    next_review=next_review
                ),
                ISMSAsset(
                    asset_id="AST-003",
                    asset_name="Security Event Logs",
                    asset_type="Data",
                    owner="Security Team",
                    custodian="Security Administrator",
                    classification="Internal",
                    location="Security Operations Center",
                    description="Comprehensive security monitoring and audit logs",
                    dependencies=["AST-004"],
                    security_requirements={
                        "confidentiality": "Medium",
                        "integrity": "High",
                        "availability": "High"
                    },
                    risk_level="Medium",
                    last_reviewed=current_time,
                    next_review=next_review
                ),
                ISMSAsset(
                    asset_id="AST-004",
                    asset_name="Production Infrastructure",
                    asset_type="Infrastructure",
                    owner="Infrastructure Team",
                    custodian="System Administrator",
                    classification="Internal",
                    location="Data Center",
                    description="Production servers and network infrastructure",
                    dependencies=[],
                    security_requirements={
                        "confidentiality": "Medium",
                        "integrity": "High",
                        "availability": "Critical"
                    },
                    risk_level="High",
                    last_reviewed=current_time,
                    next_review=next_review
                )
            ]
            
            # Store assets
            for asset in assets:
                await self._store_asset(asset)
                self.assets[asset.asset_id] = asset
            
            self.logger.info(f"Initialized {len(assets)} information assets")
            
        except Exception as e:
            self.logger.error(f"Error initializing asset inventory: {e}")
    
    async def _store_asset(self, asset: ISMSAsset):
        """Store information asset in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO isms_assets
                (asset_id, asset_name, asset_type, owner, custodian, classification,
                 location, description, dependencies, security_requirements,
                 risk_level, last_reviewed, next_review)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset.asset_id, asset.asset_name, asset.asset_type, asset.owner,
                asset.custodian, asset.classification, asset.location, asset.description,
                json.dumps(asset.dependencies), json.dumps(asset.security_requirements),
                asset.risk_level, asset.last_reviewed, asset.next_review
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing asset: {e}")
    
    async def get_isms_status(self) -> Dict[str, Any]:
        """Get current ISMS implementation status"""
        try:
            return {
                "isms_established": self.isms_established,
                "scope_defined": bool(self.scope_definition),
                "policies_created": len(self.policies),
                "assets_inventoried": len(self.assets),
                "scope_boundaries": len(self.scope_definition.get("scope_boundaries", {}).get("included", [])),
                "compliance_frameworks": len(self.scope_definition.get("business_context", {}).get("regulatory_requirements", [])),
                "last_management_review": self.last_management_review,
                "next_management_review": self.next_management_review,
                "database_file": self.database_file
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ISMS status: {e}")
            return {"error": str(e)}
    
    async def get_security_policies(self) -> List[Dict[str, Any]]:
        """Get all security policies"""
        try:
            policies = []
            for policy in self.policies.values():
                policy_dict = asdict(policy)
                policy_dict["policy_type"] = policy.policy_type.value
                policies.append(policy_dict)
            
            return policies
            
        except Exception as e:
            self.logger.error(f"Error getting security policies: {e}")
            return []
    
    async def get_asset_inventory(self) -> List[Dict[str, Any]]:
        """Get information asset inventory"""
        try:
            assets = []
            for asset in self.assets.values():
                assets.append(asdict(asset))
            
            return assets
            
        except Exception as e:
            self.logger.error(f"Error getting asset inventory: {e}")
            return []


# Global ISMS framework instance
isms_framework = ISMSFramework()