#!/usr/bin/env python3
"""
Risk Assessment Methodology Framework
ISO 27001 compliant risk assessment implementation for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import hashlib


class RiskCategory(Enum):
    """Risk categories"""
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"
    ENVIRONMENTAL = "environmental"


class ThreatSource(Enum):
    """Threat source types"""
    INTERNAL_MALICIOUS = "internal_malicious"
    INTERNAL_ACCIDENTAL = "internal_accidental"
    EXTERNAL_MALICIOUS = "external_malicious"
    EXTERNAL_ACCIDENTAL = "external_accidental"
    NATURAL_DISASTER = "natural_disaster"
    TECHNICAL_FAILURE = "technical_failure"
    SUPPLY_CHAIN = "supply_chain"


class RiskLevel(Enum):
    """Risk levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class TreatmentStrategy(Enum):
    """Risk treatment strategies"""
    MITIGATE = "mitigate"
    ACCEPT = "accept"
    TRANSFER = "transfer"
    AVOID = "avoid"


@dataclass
class ThreatScenario:
    """Threat scenario definition"""
    scenario_id: str
    title: str
    description: str
    threat_source: ThreatSource
    threat_actor: str
    attack_vector: str
    vulnerability_exploited: str
    impact_description: str
    likelihood_factors: List[str]
    impact_factors: List[str]
    existing_controls: List[str]
    control_effectiveness: str


@dataclass
class RiskAssessment:
    """Risk assessment record"""
    risk_id: str
    asset_id: str
    asset_name: str
    threat_scenario: ThreatScenario
    risk_category: RiskCategory
    inherent_likelihood: int  # 1-5 scale
    inherent_impact: int      # 1-5 scale
    inherent_risk_score: int  # likelihood * impact
    inherent_risk_level: RiskLevel
    existing_controls: List[str]
    control_effectiveness: float  # 0.0-1.0
    residual_likelihood: int
    residual_impact: int
    residual_risk_score: int
    residual_risk_level: RiskLevel
    treatment_strategy: TreatmentStrategy
    treatment_plan: str
    treatment_owner: str
    treatment_due_date: float
    treatment_cost: float
    treatment_status: str
    last_reviewed: float
    next_review: float
    assessor: str
    approved_by: str
    approval_date: float


@dataclass
class RiskTreatmentPlan:
    """Risk treatment plan"""
    plan_id: str
    risk_id: str
    treatment_strategy: TreatmentStrategy
    treatment_description: str
    implementation_steps: List[str]
    required_resources: List[str]
    estimated_cost: float
    timeline: str
    success_criteria: List[str]
    responsible_party: str
    approval_required: bool
    approved: bool = False
    implementation_status: str = "planned"
    completion_percentage: float = 0.0


class RiskAssessmentMethodology:
    """
    Risk Assessment Methodology Framework
    Implements ISO 27001 compliant risk assessment for Syn_OS
    """
    
    def __init__(self):
        """Initialize risk assessment methodology"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.risk_directory = "/var/lib/synos/risk"
        self.database_file = f"{self.risk_directory}/risk_assessment.db"
        
        # Risk components
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.threat_scenarios: Dict[str, ThreatScenario] = {}
        self.treatment_plans: Dict[str, RiskTreatmentPlan] = {}
        
        # Risk matrices and criteria
        self.likelihood_criteria = {}
        self.impact_criteria = {}
        self.risk_matrix = {}
        self.risk_appetite = {}
        
        # Assessment status
        self.methodology_established = False
        self.last_assessment = 0.0
        self.next_assessment = 0.0
        
        # Initialize system
        asyncio.create_task(self._initialize_methodology())
    
    async def _initialize_methodology(self):
        """Initialize risk assessment methodology"""
        try:
            self.logger.info("Initializing risk assessment methodology...")
            
            # Create risk directory
            os.makedirs(self.risk_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Define risk criteria
            await self._define_risk_criteria()
            
            # Create threat scenarios
            await self._create_threat_scenarios()
            
            # Initialize risk register
            await self._initialize_risk_register()
            
            self.methodology_established = True
            self.logger.info("Risk assessment methodology initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing risk methodology: {e}")
    
    async def _initialize_database(self):
        """Initialize risk assessment database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Risk assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_assessments (
                    risk_id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    asset_name TEXT NOT NULL,
                    threat_scenario TEXT NOT NULL,
                    risk_category TEXT NOT NULL,
                    inherent_likelihood INTEGER NOT NULL,
                    inherent_impact INTEGER NOT NULL,
                    inherent_risk_score INTEGER NOT NULL,
                    inherent_risk_level TEXT NOT NULL,
                    existing_controls TEXT,
                    control_effectiveness REAL,
                    residual_likelihood INTEGER NOT NULL,
                    residual_impact INTEGER NOT NULL,
                    residual_risk_score INTEGER NOT NULL,
                    residual_risk_level TEXT NOT NULL,
                    treatment_strategy TEXT NOT NULL,
                    treatment_plan TEXT,
                    treatment_owner TEXT,
                    treatment_due_date REAL,
                    treatment_cost REAL,
                    treatment_status TEXT,
                    last_reviewed REAL,
                    next_review REAL,
                    assessor TEXT,
                    approved_by TEXT,
                    approval_date REAL
                )
            ''')
            
            # Threat scenarios table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_scenarios (
                    scenario_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    threat_source TEXT NOT NULL,
                    threat_actor TEXT,
                    attack_vector TEXT,
                    vulnerability_exploited TEXT,
                    impact_description TEXT,
                    likelihood_factors TEXT,
                    impact_factors TEXT,
                    existing_controls TEXT,
                    control_effectiveness TEXT
                )
            ''')
            
            # Treatment plans table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS treatment_plans (
                    plan_id TEXT PRIMARY KEY,
                    risk_id TEXT NOT NULL,
                    treatment_strategy TEXT NOT NULL,
                    treatment_description TEXT,
                    implementation_steps TEXT,
                    required_resources TEXT,
                    estimated_cost REAL,
                    timeline TEXT,
                    success_criteria TEXT,
                    responsible_party TEXT,
                    approval_required BOOLEAN,
                    approved BOOLEAN DEFAULT 0,
                    implementation_status TEXT DEFAULT 'planned',
                    completion_percentage REAL DEFAULT 0.0
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_risks_level ON risk_assessments (residual_risk_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_risks_category ON risk_assessments (risk_category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scenarios_source ON threat_scenarios (threat_source)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing risk database: {e}")
            raise
    
    async def _define_risk_criteria(self):
        """Define risk assessment criteria and matrices"""
        try:
            # Likelihood criteria (1-5 scale)
            self.likelihood_criteria = {
                1: {
                    "level": "Very Low",
                    "description": "Extremely unlikely to occur (< 1% probability)",
                    "frequency": "Once in 10+ years",
                    "qualitative": "Rare occurrence with multiple preventive controls"
                },
                2: {
                    "level": "Low", 
                    "description": "Unlikely to occur (1-10% probability)",
                    "frequency": "Once in 5-10 years",
                    "qualitative": "Infrequent occurrence with adequate controls"
                },
                3: {
                    "level": "Medium",
                    "description": "Possible to occur (10-50% probability)",
                    "frequency": "Once in 1-5 years",
                    "qualitative": "Occasional occurrence with some controls"
                },
                4: {
                    "level": "High",
                    "description": "Likely to occur (50-90% probability)",
                    "frequency": "Once per year",
                    "qualitative": "Frequent occurrence with limited controls"
                },
                5: {
                    "level": "Very High",
                    "description": "Almost certain to occur (> 90% probability)",
                    "frequency": "Multiple times per year",
                    "qualitative": "Regular occurrence with inadequate controls"
                }
            }
            
            # Impact criteria (1-5 scale)
            self.impact_criteria = {
                1: {
                    "level": "Very Low",
                    "financial": "< $10,000",
                    "operational": "Minimal disruption (< 1 hour)",
                    "reputation": "No public awareness",
                    "compliance": "Minor non-compliance",
                    "safety": "No safety impact"
                },
                2: {
                    "level": "Low",
                    "financial": "$10,000 - $100,000",
                    "operational": "Minor disruption (1-8 hours)",
                    "reputation": "Limited local awareness",
                    "compliance": "Regulatory notice",
                    "safety": "Minor safety concern"
                },
                3: {
                    "level": "Medium",
                    "financial": "$100,000 - $1,000,000",
                    "operational": "Moderate disruption (8-24 hours)",
                    "reputation": "Regional media coverage",
                    "compliance": "Regulatory investigation",
                    "safety": "Moderate safety impact"
                },
                4: {
                    "level": "High",
                    "financial": "$1,000,000 - $10,000,000",
                    "operational": "Major disruption (1-7 days)",
                    "reputation": "National media coverage",
                    "compliance": "Regulatory enforcement action",
                    "safety": "Significant safety impact"
                },
                5: {
                    "level": "Very High",
                    "financial": "> $10,000,000",
                    "operational": "Severe disruption (> 7 days)",
                    "reputation": "International media coverage",
                    "compliance": "Criminal prosecution",
                    "safety": "Life-threatening safety impact"
                }
            }
            
            # Risk matrix (likelihood x impact = risk score)
            self.risk_matrix = {
                (1, 1): {"score": 1, "level": RiskLevel.NEGLIGIBLE},
                (1, 2): {"score": 2, "level": RiskLevel.LOW},
                (1, 3): {"score": 3, "level": RiskLevel.LOW},
                (1, 4): {"score": 4, "level": RiskLevel.MEDIUM},
                (1, 5): {"score": 5, "level": RiskLevel.MEDIUM},
                (2, 1): {"score": 2, "level": RiskLevel.LOW},
                (2, 2): {"score": 4, "level": RiskLevel.LOW},
                (2, 3): {"score": 6, "level": RiskLevel.MEDIUM},
                (2, 4): {"score": 8, "level": RiskLevel.MEDIUM},
                (2, 5): {"score": 10, "level": RiskLevel.HIGH},
                (3, 1): {"score": 3, "level": RiskLevel.LOW},
                (3, 2): {"score": 6, "level": RiskLevel.MEDIUM},
                (3, 3): {"score": 9, "level": RiskLevel.MEDIUM},
                (3, 4): {"score": 12, "level": RiskLevel.HIGH},
                (3, 5): {"score": 15, "level": RiskLevel.HIGH},
                (4, 1): {"score": 4, "level": RiskLevel.MEDIUM},
                (4, 2): {"score": 8, "level": RiskLevel.MEDIUM},
                (4, 3): {"score": 12, "level": RiskLevel.HIGH},
                (4, 4): {"score": 16, "level": RiskLevel.HIGH},
                (4, 5): {"score": 20, "level": RiskLevel.CRITICAL},
                (5, 1): {"score": 5, "level": RiskLevel.MEDIUM},
                (5, 2): {"score": 10, "level": RiskLevel.HIGH},
                (5, 3): {"score": 15, "level": RiskLevel.HIGH},
                (5, 4): {"score": 20, "level": RiskLevel.CRITICAL},
                (5, 5): {"score": 25, "level": RiskLevel.CRITICAL}
            }
            
            # Risk appetite and tolerance
            self.risk_appetite = {
                "critical": {
                    "tolerance": 0,
                    "action": "Immediate treatment required",
                    "escalation": "CEO and Board notification"
                },
                "high": {
                    "tolerance": 5,
                    "action": "Treatment plan required within 30 days",
                    "escalation": "Executive management notification"
                },
                "medium": {
                    "tolerance": 15,
                    "action": "Treatment plan required within 90 days",
                    "escalation": "Senior management notification"
                },
                "low": {
                    "tolerance": 50,
                    "action": "Treatment plan optional",
                    "escalation": "Management awareness"
                },
                "negligible": {
                    "tolerance": 100,
                    "action": "Accept with monitoring",
                    "escalation": "No escalation required"
                }
            }
            
            # Save criteria to file
            criteria_file = f"{self.risk_directory}/risk_criteria.json"
            criteria_data = {
                "likelihood_criteria": self.likelihood_criteria,
                "impact_criteria": self.impact_criteria,
                "risk_matrix": {f"{k[0]},{k[1]}": {"score": v["score"], "level": v["level"].value} 
                              for k, v in self.risk_matrix.items()},
                "risk_appetite": self.risk_appetite
            }
            
            with open(criteria_file, 'w') as f:
                json.dump(criteria_data, f, indent=2)
            
            self.logger.info("Risk assessment criteria defined")
            
        except Exception as e:
            self.logger.error(f"Error defining risk criteria: {e}")
    
    async def _create_threat_scenarios(self):
        """Create comprehensive threat scenarios"""
        try:
            scenarios = [
                ThreatScenario(
                    scenario_id="TS-001",
                    title="Advanced Persistent Threat (APT) Attack",
                    description="Sophisticated nation-state or criminal group conducts long-term covert attack",
                    threat_source=ThreatSource.EXTERNAL_MALICIOUS,
                    threat_actor="Nation-state APT group",
                    attack_vector="Spear phishing, zero-day exploits, lateral movement",
                    vulnerability_exploited="Unpatched systems, weak authentication, insufficient monitoring",
                    impact_description="Data exfiltration, system compromise, intellectual property theft",
                    likelihood_factors=[
                        "High-value target (security OS)",
                        "Nation-state interest in cybersecurity research",
                        "Limited threat intelligence sharing",
                        "Complex attack surface"
                    ],
                    impact_factors=[
                        "Source code and IP theft",
                        "User data compromise",
                        "Reputation damage",
                        "Regulatory penalties"
                    ],
                    existing_controls=[
                        "Network segmentation",
                        "Endpoint detection and response",
                        "Security awareness training",
                        "Incident response procedures"
                    ],
                    control_effectiveness="Medium"
                ),
                ThreatScenario(
                    scenario_id="TS-002",
                    title="Insider Threat - Malicious Employee",
                    description="Authorized user with legitimate access conducts malicious activities",
                    threat_source=ThreatSource.INTERNAL_MALICIOUS,
                    threat_actor="Disgruntled employee or contractor",
                    attack_vector="Abuse of privileged access, data exfiltration, sabotage",
                    vulnerability_exploited="Excessive privileges, insufficient monitoring, weak controls",
                    impact_description="Data theft, system sabotage, competitive advantage loss",
                    likelihood_factors=[
                        "Access to sensitive systems",
                        "Financial or personal motivations",
                        "Insufficient background checks",
                        "Limited user activity monitoring"
                    ],
                    impact_factors=[
                        "Intellectual property theft",
                        "System availability impact",
                        "Customer trust loss",
                        "Legal and regulatory issues"
                    ],
                    existing_controls=[
                        "Background checks",
                        "Least privilege access",
                        "User activity monitoring",
                        "Separation of duties"
                    ],
                    control_effectiveness="Medium"
                ),
                ThreatScenario(
                    scenario_id="TS-003",
                    title="Ransomware Attack",
                    description="Malicious software encrypts systems and demands ransom payment",
                    threat_source=ThreatSource.EXTERNAL_MALICIOUS,
                    threat_actor="Cybercriminal ransomware group",
                    attack_vector="Email phishing, RDP exploitation, supply chain compromise",
                    vulnerability_exploited="Unpatched systems, weak passwords, insufficient backups",
                    impact_description="System encryption, business disruption, ransom demands",
                    likelihood_factors=[
                        "High-profile target",
                        "Valuable data and systems",
                        "Remote work vulnerabilities",
                        "Ransomware-as-a-Service availability"
                    ],
                    impact_factors=[
                        "Complete system unavailability",
                        "Data loss or corruption",
                        "Recovery costs",
                        "Reputation damage"
                    ],
                    existing_controls=[
                        "Regular backups",
                        "Endpoint protection",
                        "Network segmentation",
                        "User awareness training"
                    ],
                    control_effectiveness="High"
                ),
                ThreatScenario(
                    scenario_id="TS-004",
                    title="Supply Chain Compromise",
                    description="Third-party vendor or software component is compromised",
                    threat_source=ThreatSource.SUPPLY_CHAIN,
                    threat_actor="Nation-state or sophisticated criminal group",
                    attack_vector="Compromised software updates, hardware implants, vendor access",
                    vulnerability_exploited="Insufficient vendor security, weak supply chain controls",
                    impact_description="Backdoor access, data compromise, system integrity loss",
                    likelihood_factors=[
                        "Complex supply chain",
                        "Multiple third-party dependencies",
                        "Limited vendor security oversight",
                        "Attractive target for attackers"
                    ],
                    impact_factors=[
                        "Widespread system compromise",
                        "Difficult detection and remediation",
                        "Customer trust impact",
                        "Regulatory scrutiny"
                    ],
                    existing_controls=[
                        "Vendor security assessments",
                        "Code signing verification",
                        "Supply chain monitoring",
                        "Incident response procedures"
                    ],
                    control_effectiveness="Medium"
                ),
                ThreatScenario(
                    scenario_id="TS-005",
                    title="Cloud Infrastructure Breach",
                    description="Compromise of cloud services and infrastructure",
                    threat_source=ThreatSource.EXTERNAL_MALICIOUS,
                    threat_actor="Cybercriminal or nation-state group",
                    attack_vector="Credential stuffing, API exploitation, misconfigurations",
                    vulnerability_exploited="Weak cloud security, misconfigured services, shared responsibility gaps",
                    impact_description="Data exposure, service disruption, unauthorized access",
                    likelihood_factors=[
                        "Cloud service complexity",
                        "Shared responsibility model gaps",
                        "Rapid cloud adoption",
                        "Insufficient cloud security expertise"
                    ],
                    impact_factors=[
                        "Large-scale data exposure",
                        "Service availability impact",
                        "Compliance violations",
                        "Customer data compromise"
                    ],
                    existing_controls=[
                        "Cloud security posture management",
                        "Identity and access management",
                        "Encryption at rest and in transit",
                        "Cloud monitoring and logging"
                    ],
                    control_effectiveness="Medium"
                )
            ]
            
            # Store threat scenarios
            for scenario in scenarios:
                await self._store_threat_scenario(scenario)
                self.threat_scenarios[scenario.scenario_id] = scenario
            
            self.logger.info(f"Created {len(scenarios)} threat scenarios")
            
        except Exception as e:
            self.logger.error(f"Error creating threat scenarios: {e}")
    
    async def _store_threat_scenario(self, scenario: ThreatScenario):
        """Store threat scenario in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_scenarios
                (scenario_id, title, description, threat_source, threat_actor,
                 attack_vector, vulnerability_exploited, impact_description,
                 likelihood_factors, impact_factors, existing_controls, control_effectiveness)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scenario.scenario_id, scenario.title, scenario.description,
                scenario.threat_source.value, scenario.threat_actor,
                scenario.attack_vector, scenario.vulnerability_exploited,
                scenario.impact_description, json.dumps(scenario.likelihood_factors),
                json.dumps(scenario.impact_factors), json.dumps(scenario.existing_controls),
                scenario.control_effectiveness
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing threat scenario: {e}")
    
    async def _initialize_risk_register(self):
        """Initialize risk register with initial assessments"""
        try:
            current_time = time.time()
            next_review = current_time + (90 * 24 * 3600)  # Quarterly review
            
            # Create initial risk assessments for critical assets
            initial_risks = [
                {
                    "asset_id": "AST-001",
                    "asset_name": "Syn_OS Source Code",
                    "scenario_id": "TS-001",
                    "category": RiskCategory.TECHNICAL,
                    "inherent_likelihood": 4,
                    "inherent_impact": 5
                },
                {
                    "asset_id": "AST-002", 
                    "asset_name": "User Authentication Database",
                    "scenario_id": "TS-003",
                    "category": RiskCategory.OPERATIONAL,
                    "inherent_likelihood": 3,
                    "inherent_impact": 4
                },
                {
                    "asset_id": "AST-003",
                    "asset_name": "Security Event Logs",
                    "scenario_id": "TS-002",
                    "category": RiskCategory.COMPLIANCE,
                    "inherent_likelihood": 2,
                    "inherent_impact": 3
                },
                {
                    "asset_id": "AST-004",
                    "asset_name": "Production Infrastructure",
                    "scenario_id": "TS-005",
                    "category": RiskCategory.OPERATIONAL,
                    "inherent_likelihood": 3,
                    "inherent_impact": 4
                }
            ]
            
            for i, risk_data in enumerate(initial_risks, 1):
                risk_id = f"RISK-{i:03d}"
                scenario = self.threat_scenarios[risk_data["scenario_id"]]
                
                # Calculate inherent risk
                inherent_score = risk_data["inherent_likelihood"] * risk_data["inherent_impact"]
                inherent_level = self.risk_matrix[(risk_data["inherent_likelihood"], risk_data["inherent_impact"])]["level"]
                
                # Calculate residual risk (assuming 50% control effectiveness)
                control_effectiveness = 0.5
                residual_likelihood = max(1, int(risk_data["inherent_likelihood"] * (1 - control_effectiveness)))
                residual_impact = risk_data["inherent_impact"]  # Impact typically doesn't change
                residual_score = residual_likelihood * residual_impact
                residual_level = self.risk_matrix[(residual_likelihood, residual_impact)]["level"]
                
                # Determine treatment strategy
                if residual_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                    treatment_strategy = TreatmentStrategy.MITIGATE
                elif residual_level == RiskLevel.MEDIUM:
                    treatment_strategy = TreatmentStrategy.MITIGATE
                else:
                    treatment_strategy = TreatmentStrategy.ACCEPT
                
                risk_assessment = RiskAssessment(
                    risk_id=risk_id,
                    asset_id=risk_data["asset_id"],
                    asset_name=risk_data["asset_name"],
                    threat_scenario=scenario,
                    risk_category=risk_data["category"],
                    inherent_likelihood=risk_data["inherent_likelihood"],
                    inherent_impact=risk_data["inherent_impact"],
                    inherent_risk_score=inherent_score,
                    inherent_risk_level=inherent_level,
                    existing_controls=scenario.existing_controls,
                    control_effectiveness=control_effectiveness,
                    residual_likelihood=residual_likelihood,
                    residual_impact=residual_impact,
                    residual_risk_score=residual_score,
                    residual_risk_level=residual_level,
                    treatment_strategy=treatment_strategy,
                    treatment_plan=f"Implement additional controls to reduce {residual_level.value} risk",
                    treatment_owner="Security Team",
                    treatment_due_date=current_time + (30 * 24 * 3600),
                    treatment_cost=50000.0,
                    treatment_status="planned",
                    last_reviewed=current_time,
                    next_review=next_review,
                    assessor="Risk Manager",
                    approved_by="Interim CISO",
                    approval_date=current_time
                )
                
                await self._store_risk_assessment(risk_assessment)
                self.risk_assessments[risk_id] = risk_assessment
            
            self.logger.info(f"Initialized risk register with {len(initial_risks)} risk assessments")
            
        except Exception as e:
            self.logger.error(f"Error initializing risk register: {e}")
    
    async def _store_risk_assessment(self, assessment: RiskAssessment):
        """Store risk assessment in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO risk_assessments
                (risk_id, asset_id, asset_name, threat_scenario, risk_category,
                 inherent_likelihood, inherent_impact, inherent_risk_score, inherent_risk_level,
                 existing_controls, control_effectiveness, residual_likelihood, residual_impact,
                 residual_risk_score, residual_risk_level, treatment_strategy, treatment_plan,
                 treatment_owner, treatment_due_date, treatment_cost, treatment_status,
                 last_reviewed, next_review, assessor, approved_by, approval_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                assessment.risk_id, assessment.asset_id, assessment.asset_name,
                assessment.threat_scenario.scenario_id, assessment.risk_category.value,
                assessment.inherent_likelihood, assessment.inherent_impact,
                assessment.inherent_risk_score, assessment.inherent_risk_level.value,
                json.dumps(assessment.existing_controls), assessment.control_effectiveness,
                assessment.residual_likelihood, assessment.residual_impact,
                assessment.residual_risk_score, assessment.residual_risk_level.value,
                assessment.treatment_strategy.value, assessment.treatment_plan,
                assessment.treatment_owner, assessment.treatment_due_date,
                assessment.treatment_cost, assessment.treatment_status,
                assessment.last_reviewed, assessment.next_review,
                assessment.assessor, assessment.approved_by, assessment.approval_date
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing risk assessment: {e}")
    
    def calculate_risk_score(self, likelihood: int, impact: int) -> Tuple[int, RiskLevel]:
        """Calculate risk score and level"""
        try:
            if (likelihood, impact) in self.risk_matrix:
                matrix_entry = self.risk_matrix[(likelihood, impact)]
                return matrix_entry["score"], matrix_entry["level"]
            else:
                # Default calculation if not in matrix
                score = likelihood * impact
                if score >= 20:
                    level = RiskLevel.CRITICAL
                elif score >= 12:
                    level = RiskLevel.HIGH
                elif score >= 6:
                    level = RiskLevel.MEDIUM
                elif score >= 2:
                    level = RiskLevel.LOW
                else:
                    level = RiskLevel.NEGLIGIBLE
                return score, level
                
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {e}")
            return 0, RiskLevel.NEGLIGIBLE
    
    async def get_methodology_status(self) -> Dict[str, Any]:
        """Get risk assessment methodology status"""
        try:
            return {
                "methodology_established": self.methodology_established,
                "threat_scenarios": len(self.threat_scenarios),
                "risk_assessments": len(self.risk_assessments),
                "treatment_plans": len(self.treatment_plans),
                "last_assessment": self.last_assessment,
                "next_assessment": self.next_assessment,
                "risk_directory": self.risk_directory,
                "database_file": self.database_file
            }
            
        except Exception as e:
            self.logger.error(f"Error getting methodology status: {e}")
            return {"error": str(e)}
    
    async def get_risk_register(self) -> List[Dict[str, Any]]:
        """Get all risk assessments"""
        try:
            risks = []
            for risk in self.risk_assessments.values():
                risk_dict = asdict(risk)
                risk_dict["risk_category"] = risk.risk_category.value
                risk_dict["inherent_risk_level"] = risk.inherent_risk_level.value
                risk_dict["residual_risk_level"] = risk.residual_risk_level.value
                risk_dict["treatment_strategy"] = risk.treatment_strategy.value
                risk_dict["threat_scenario"] = asdict(risk.threat_scenario)
                risk_dict["threat_scenario"]["threat_source"] = risk.threat_scenario.threat_source.value
                risks.append(risk_dict)
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Error getting risk register: {e}")
            return []
    
    async def get_threat_scenarios(self) -> List[Dict[str, Any]]:
        """Get all threat scenarios"""
        try:
            scenarios = []
            for scenario in self.threat_scenarios.values():
                scenario_dict = asdict(scenario)
                scenario_dict["threat_source"] = scenario.threat_source.value
                scenarios.append(scenario_dict)
            
            return scenarios
            
        except Exception as e:
            self.logger.error(f"Error getting threat scenarios: {e}")
            return []


# Global risk assessment methodology instance
risk_assessment_methodology = RiskAssessmentMethodology()