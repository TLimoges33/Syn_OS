#!/usr/bin/env python3
"""
Environmental Management System Implementation
ISO 14001 compliant environmental management for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid


class EnvironmentalAspectSignificance(Enum):
    """Environmental aspect significance levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(Enum):
    """Legal compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    NOT_APPLICABLE = "not_applicable"


class ObjectiveStatus(Enum):
    """Environmental objective status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class IncidentSeverity(Enum):
    """Environmental incident severity"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"


@dataclass
class EnvironmentalAspect:
    """Environmental aspect definition"""
    aspect_id: str
    aspect_name: str
    aspect_description: str
    activity: str
    environmental_condition: str  # normal, abnormal, emergency
    environmental_impact: str
    significance_level: EnvironmentalAspectSignificance
    significance_score: float
    control_measures: List[str]
    monitoring_requirements: List[str]
    legal_requirements: List[str]
    responsible_person: str
    review_date: float
    next_review_date: float


@dataclass
class LegalRequirement:
    """Legal and regulatory requirement"""
    requirement_id: str
    requirement_title: str
    requirement_description: str
    regulation_source: str
    jurisdiction: str
    applicable_activities: List[str]
    compliance_status: ComplianceStatus
    compliance_evidence: List[str]
    responsible_person: str
    review_frequency: int  # months
    last_review_date: float
    next_review_date: float
    compliance_actions: List[str]


@dataclass
class EnvironmentalObjective:
    """Environmental objective and target"""
    objective_id: str
    objective_title: str
    objective_description: str
    related_aspects: List[str]
    target_value: float
    current_value: float
    measurement_unit: str
    target_date: float
    status: ObjectiveStatus
    progress_percentage: float
    responsible_person: str
    action_plans: List[str]
    resources_required: List[str]
    monitoring_frequency: str
    success_criteria: List[str]


@dataclass
class EnvironmentalIncident:
    """Environmental incident record"""
    incident_id: str
    incident_title: str
    incident_description: str
    incident_date: float
    location: str
    severity: IncidentSeverity
    environmental_impact: str
    immediate_actions: List[str]
    root_cause_analysis: str
    corrective_actions: List[str]
    preventive_actions: List[str]
    responsible_person: str
    investigation_team: List[str]
    lessons_learned: List[str]
    status: str
    closure_date: float


@dataclass
class EnvironmentalMonitoring:
    """Environmental monitoring data"""
    monitoring_id: str
    parameter_name: str
    measurement_value: float
    measurement_unit: str
    measurement_date: float
    location: str
    monitoring_method: str
    legal_limit: Optional[float]
    internal_limit: Optional[float]
    compliance_status: str
    responsible_person: str
    equipment_used: str
    calibration_date: float
    next_calibration_date: float


class EnvironmentalManagementSystem:
    """
    Environmental Management System
    ISO 14001 compliant environmental management implementation
    """
    
    def __init__(self):
        """Initialize environmental management system"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.ems_directory = "/var/lib/synos/environmental"
        self.database_file = f"{self.ems_directory}/environmental.db"
        self.monitoring_directory = f"{self.ems_directory}/monitoring"
        self.reports_directory = f"{self.ems_directory}/reports"
        self.procedures_directory = f"{self.ems_directory}/procedures"
        
        # System components
        self.environmental_aspects: Dict[str, EnvironmentalAspect] = {}
        self.legal_requirements: Dict[str, LegalRequirement] = {}
        self.environmental_objectives: Dict[str, EnvironmentalObjective] = {}
        self.environmental_incidents: Dict[str, EnvironmentalIncident] = {}
        self.monitoring_data: Dict[str, List[EnvironmentalMonitoring]] = {}
        
        # Environmental policy
        self.environmental_policy = """
        Syn_OS Environmental Policy
        
        Syn_OS is committed to environmental protection and sustainable development 
        in all aspects of our consciousness-aware security operating system development 
        and operations.
        
        Our commitment includes:
        - Preventing pollution and minimizing environmental impact
        - Complying with all applicable environmental laws and regulations
        - Continually improving our environmental performance
        - Considering environmental factors in all business decisions
        - Promoting environmental awareness among all personnel
        - Efficient use of natural resources and energy
        - Responsible waste management and circular economy principles
        - Supporting biodiversity and ecosystem protection
        
        This policy is communicated to all personnel and stakeholders and is 
        available to the public. It is reviewed annually and updated as necessary 
        to reflect our ongoing commitment to environmental excellence.
        
        Management provides the necessary resources to achieve our environmental 
        objectives and targets, and to continually improve the effectiveness of 
        our Environmental Management System.
        """
        
        # Initialize system
        asyncio.create_task(self._initialize_ems())
    
    async def _initialize_ems(self):
        """Initialize environmental management system"""
        try:
            self.logger.info("Initializing Environmental Management System...")
            
            # Create directories
            for directory in [self.ems_directory, self.monitoring_directory, 
                            self.reports_directory, self.procedures_directory]:
                os.makedirs(directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_existing_data()
            
            # Initialize environmental aspects
            await self._initialize_environmental_aspects()
            
            # Initialize legal requirements
            await self._initialize_legal_requirements()
            
            # Initialize environmental objectives
            await self._initialize_environmental_objectives()
            
            # Schedule monitoring tasks
            asyncio.create_task(self._schedule_monitoring_tasks())
            
            self.logger.info("Environmental Management System initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing EMS: {e}")
    
    async def _initialize_database(self):
        """Initialize EMS database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Environmental aspects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_aspects (
                    aspect_id TEXT PRIMARY KEY,
                    aspect_name TEXT NOT NULL,
                    aspect_description TEXT,
                    activity TEXT,
                    environmental_condition TEXT,
                    environmental_impact TEXT,
                    significance_level TEXT,
                    significance_score REAL,
                    control_measures TEXT,
                    monitoring_requirements TEXT,
                    legal_requirements TEXT,
                    responsible_person TEXT,
                    review_date REAL,
                    next_review_date REAL
                )
            ''')
            
            # Legal requirements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS legal_requirements (
                    requirement_id TEXT PRIMARY KEY,
                    requirement_title TEXT NOT NULL,
                    requirement_description TEXT,
                    regulation_source TEXT,
                    jurisdiction TEXT,
                    applicable_activities TEXT,
                    compliance_status TEXT,
                    compliance_evidence TEXT,
                    responsible_person TEXT,
                    review_frequency INTEGER,
                    last_review_date REAL,
                    next_review_date REAL,
                    compliance_actions TEXT
                )
            ''')
            
            # Environmental objectives table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_objectives (
                    objective_id TEXT PRIMARY KEY,
                    objective_title TEXT NOT NULL,
                    objective_description TEXT,
                    related_aspects TEXT,
                    target_value REAL,
                    current_value REAL,
                    measurement_unit TEXT,
                    target_date REAL,
                    status TEXT,
                    progress_percentage REAL,
                    responsible_person TEXT,
                    action_plans TEXT,
                    resources_required TEXT,
                    monitoring_frequency TEXT,
                    success_criteria TEXT
                )
            ''')
            
            # Environmental incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_incidents (
                    incident_id TEXT PRIMARY KEY,
                    incident_title TEXT NOT NULL,
                    incident_description TEXT,
                    incident_date REAL,
                    location TEXT,
                    severity TEXT,
                    environmental_impact TEXT,
                    immediate_actions TEXT,
                    root_cause_analysis TEXT,
                    corrective_actions TEXT,
                    preventive_actions TEXT,
                    responsible_person TEXT,
                    investigation_team TEXT,
                    lessons_learned TEXT,
                    status TEXT,
                    closure_date REAL
                )
            ''')
            
            # Environmental monitoring table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_monitoring (
                    monitoring_id TEXT PRIMARY KEY,
                    parameter_name TEXT NOT NULL,
                    measurement_value REAL,
                    measurement_unit TEXT,
                    measurement_date REAL,
                    location TEXT,
                    monitoring_method TEXT,
                    legal_limit REAL,
                    internal_limit REAL,
                    compliance_status TEXT,
                    responsible_person TEXT,
                    equipment_used TEXT,
                    calibration_date REAL,
                    next_calibration_date REAL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_aspects_significance ON environmental_aspects (significance_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_legal_compliance ON legal_requirements (compliance_status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_objectives_status ON environmental_objectives (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_severity ON environmental_incidents (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_monitoring_date ON environmental_monitoring (measurement_date)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing EMS database: {e}")
            raise
    
    async def _load_existing_data(self):
        """Load existing EMS data"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load environmental aspects
            cursor.execute('SELECT * FROM environmental_aspects')
            for row in cursor.fetchall():
                aspect = EnvironmentalAspect(
                    aspect_id=row[0],
                    aspect_name=row[1],
                    aspect_description=row[2],
                    activity=row[3],
                    environmental_condition=row[4],
                    environmental_impact=row[5],
                    significance_level=EnvironmentalAspectSignificance(row[6]),
                    significance_score=row[7],
                    control_measures=json.loads(row[8]) if row[8] else [],
                    monitoring_requirements=json.loads(row[9]) if row[9] else [],
                    legal_requirements=json.loads(row[10]) if row[10] else [],
                    responsible_person=row[11],
                    review_date=row[12],
                    next_review_date=row[13]
                )
                self.environmental_aspects[aspect.aspect_id] = aspect
            
            # Load legal requirements
            cursor.execute('SELECT * FROM legal_requirements')
            for row in cursor.fetchall():
                requirement = LegalRequirement(
                    requirement_id=row[0],
                    requirement_title=row[1],
                    requirement_description=row[2],
                    regulation_source=row[3],
                    jurisdiction=row[4],
                    applicable_activities=json.loads(row[5]) if row[5] else [],
                    compliance_status=ComplianceStatus(row[6]),
                    compliance_evidence=json.loads(row[7]) if row[7] else [],
                    responsible_person=row[8],
                    review_frequency=row[9],
                    last_review_date=row[10],
                    next_review_date=row[11],
                    compliance_actions=json.loads(row[12]) if row[12] else []
                )
                self.legal_requirements[requirement.requirement_id] = requirement
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.environmental_aspects)} aspects and {len(self.legal_requirements)} legal requirements")
            
        except Exception as e:
            self.logger.error(f"Error loading existing EMS data: {e}")
    
    async def _initialize_environmental_aspects(self):
        """Initialize core environmental aspects"""
        try:
            current_time = time.time()
            
            core_aspects = [
                {
                    "aspect_id": "EA-001",
                    "name": "Energy Consumption",
                    "description": "Electrical energy consumption from data centers and development facilities",
                    "activity": "Software development and testing",
                    "condition": "normal",
                    "impact": "Climate change contribution through greenhouse gas emissions",
                    "significance": EnvironmentalAspectSignificance.HIGH,
                    "score": 8.5,
                    "controls": ["Energy-efficient hardware", "Renewable energy sourcing", "Power management systems"],
                    "monitoring": ["Monthly energy consumption tracking", "Carbon footprint calculation"]
                },
                {
                    "aspect_id": "EA-002",
                    "name": "Electronic Waste",
                    "description": "Disposal of electronic equipment and components",
                    "activity": "Hardware lifecycle management",
                    "condition": "normal",
                    "impact": "Soil and water contamination from hazardous materials",
                    "significance": EnvironmentalAspectSignificance.MEDIUM,
                    "score": 6.0,
                    "controls": ["Certified e-waste recycling", "Equipment lifecycle extension", "Responsible procurement"],
                    "monitoring": ["Quarterly waste audit", "Recycling certification tracking"]
                },
                {
                    "aspect_id": "EA-003",
                    "name": "Data Center Cooling",
                    "description": "Cooling systems for server infrastructure",
                    "activity": "Infrastructure operations",
                    "condition": "normal",
                    "impact": "Energy consumption and potential refrigerant emissions",
                    "significance": EnvironmentalAspectSignificance.HIGH,
                    "score": 7.8,
                    "controls": ["Efficient cooling systems", "Temperature optimization", "Natural cooling utilization"],
                    "monitoring": ["Cooling efficiency metrics", "Refrigerant leak detection"]
                },
                {
                    "aspect_id": "EA-004",
                    "name": "Cloud Infrastructure",
                    "description": "Environmental impact of cloud service usage",
                    "activity": "Cloud-based operations",
                    "condition": "normal",
                    "impact": "Indirect energy consumption and carbon emissions",
                    "significance": EnvironmentalAspectSignificance.MEDIUM,
                    "score": 5.5,
                    "controls": ["Green cloud providers", "Resource optimization", "Efficient architectures"],
                    "monitoring": ["Cloud resource utilization", "Provider sustainability metrics"]
                },
                {
                    "aspect_id": "EA-005",
                    "name": "Transportation",
                    "description": "Business travel and commuting impacts",
                    "activity": "Business operations",
                    "condition": "normal",
                    "impact": "Greenhouse gas emissions from transportation",
                    "significance": EnvironmentalAspectSignificance.LOW,
                    "score": 3.2,
                    "controls": ["Remote work policies", "Virtual meetings", "Sustainable transport options"],
                    "monitoring": ["Travel emissions tracking", "Remote work percentage"]
                }
            ]
            
            for aspect_data in core_aspects:
                if aspect_data["aspect_id"] not in self.environmental_aspects:
                    aspect = EnvironmentalAspect(
                        aspect_id=aspect_data["aspect_id"],
                        aspect_name=aspect_data["name"],
                        aspect_description=aspect_data["description"],
                        activity=aspect_data["activity"],
                        environmental_condition=aspect_data["condition"],
                        environmental_impact=aspect_data["impact"],
                        significance_level=aspect_data["significance"],
                        significance_score=aspect_data["score"],
                        control_measures=aspect_data["controls"],
                        monitoring_requirements=aspect_data["monitoring"],
                        legal_requirements=[],
                        responsible_person="environmental_manager",
                        review_date=current_time,
                        next_review_date=current_time + (365 * 24 * 3600)  # 1 year
                    )
                    
                    await self._store_aspect(aspect)
                    self.environmental_aspects[aspect.aspect_id] = aspect
            
            self.logger.info(f"Initialized {len(core_aspects)} environmental aspects")
            
        except Exception as e:
            self.logger.error(f"Error initializing environmental aspects: {e}")
    
    async def _initialize_legal_requirements(self):
        """Initialize legal and regulatory requirements"""
        try:
            current_time = time.time()
            
            legal_reqs = [
                {
                    "requirement_id": "LR-001",
                    "title": "Energy Efficiency Standards",
                    "description": "Compliance with energy efficiency regulations for IT equipment",
                    "source": "EPA Energy Star Program",
                    "jurisdiction": "United States",
                    "activities": ["Hardware procurement", "Data center operations"],
                    "status": ComplianceStatus.COMPLIANT,
                    "evidence": ["Energy Star certified equipment", "Efficiency monitoring reports"]
                },
                {
                    "requirement_id": "LR-002",
                    "title": "Electronic Waste Regulations",
                    "description": "Proper disposal and recycling of electronic waste",
                    "source": "Resource Conservation and Recovery Act (RCRA)",
                    "jurisdiction": "United States",
                    "activities": ["Equipment disposal", "Hardware lifecycle management"],
                    "status": ComplianceStatus.COMPLIANT,
                    "evidence": ["Certified recycler contracts", "Disposal certificates"]
                },
                {
                    "requirement_id": "LR-003",
                    "title": "Greenhouse Gas Reporting",
                    "description": "Reporting of greenhouse gas emissions above threshold",
                    "source": "EPA Greenhouse Gas Reporting Program",
                    "jurisdiction": "United States",
                    "activities": ["Energy consumption", "Transportation"],
                    "status": ComplianceStatus.UNDER_REVIEW,
                    "evidence": ["Emissions calculations", "Reporting submissions"]
                },
                {
                    "requirement_id": "LR-004",
                    "title": "Hazardous Materials Management",
                    "description": "Safe handling and disposal of hazardous materials",
                    "source": "Occupational Safety and Health Administration (OSHA)",
                    "jurisdiction": "United States",
                    "activities": ["Laboratory operations", "Equipment maintenance"],
                    "status": ComplianceStatus.COMPLIANT,
                    "evidence": ["Safety data sheets", "Training records", "Disposal manifests"]
                }
            ]
            
            for req_data in legal_reqs:
                if req_data["requirement_id"] not in self.legal_requirements:
                    requirement = LegalRequirement(
                        requirement_id=req_data["requirement_id"],
                        requirement_title=req_data["title"],
                        requirement_description=req_data["description"],
                        regulation_source=req_data["source"],
                        jurisdiction=req_data["jurisdiction"],
                        applicable_activities=req_data["activities"],
                        compliance_status=req_data["status"],
                        compliance_evidence=req_data["evidence"],
                        responsible_person="compliance_manager",
                        review_frequency=12,  # annually
                        last_review_date=current_time,
                        next_review_date=current_time + (365 * 24 * 3600),
                        compliance_actions=[]
                    )
                    
                    await self._store_legal_requirement(requirement)
                    self.legal_requirements[requirement.requirement_id] = requirement
            
            self.logger.info(f"Initialized {len(legal_reqs)} legal requirements")
            
        except Exception as e:
            self.logger.error(f"Error initializing legal requirements: {e}")
    
    async def _initialize_environmental_objectives(self):
        """Initialize environmental objectives and targets"""
        try:
            current_time = time.time()
            target_date = current_time + (365 * 24 * 3600)  # 1 year
            
            objectives = [
                {
                    "objective_id": "EO-001",
                    "title": "Reduce Energy Consumption",
                    "description": "Reduce overall energy consumption by 20% compared to baseline",
                    "aspects": ["EA-001", "EA-003"],
                    "target": 20.0,
                    "unit": "percentage_reduction",
                    "actions": ["Implement energy management system", "Upgrade to efficient equipment", "Optimize cooling systems"]
                },
                {
                    "objective_id": "EO-002",
                    "title": "Increase Renewable Energy Usage",
                    "description": "Achieve 50% renewable energy sourcing for all operations",
                    "aspects": ["EA-001"],
                    "target": 50.0,
                    "unit": "percentage",
                    "actions": ["Negotiate renewable energy contracts", "Install on-site solar panels", "Purchase renewable energy certificates"]
                },
                {
                    "objective_id": "EO-003",
                    "title": "Improve E-Waste Recycling",
                    "description": "Achieve 95% recycling rate for all electronic waste",
                    "aspects": ["EA-002"],
                    "target": 95.0,
                    "unit": "percentage",
                    "actions": ["Partner with certified recyclers", "Implement asset tracking", "Extend equipment lifecycles"]
                },
                {
                    "objective_id": "EO-004",
                    "title": "Carbon Footprint Reduction",
                    "description": "Reduce carbon footprint by 30% through efficiency and renewable energy",
                    "aspects": ["EA-001", "EA-003", "EA-004", "EA-005"],
                    "target": 30.0,
                    "unit": "percentage_reduction",
                    "actions": ["Implement carbon management program", "Optimize cloud usage", "Promote remote work"]
                }
            ]
            
            for obj_data in objectives:
                if obj_data["objective_id"] not in self.environmental_objectives:
                    objective = EnvironmentalObjective(
                        objective_id=obj_data["objective_id"],
                        objective_title=obj_data["title"],
                        objective_description=obj_data["description"],
                        related_aspects=obj_data["aspects"],
                        target_value=obj_data["target"],
                        current_value=0.0,
                        measurement_unit=obj_data["unit"],
                        target_date=target_date,
                        status=ObjectiveStatus.PLANNED,
                        progress_percentage=0.0,
                        responsible_person="environmental_manager",
                        action_plans=obj_data["actions"],
                        resources_required=["Budget allocation", "Personnel time", "Technology investments"],
                        monitoring_frequency="monthly",
                        success_criteria=["Target achievement", "Sustained performance", "Stakeholder satisfaction"]
                    )
                    
                    await self._store_objective(objective)
                    self.environmental_objectives[objective.objective_id] = objective
            
            self.logger.info(f"Initialized {len(objectives)} environmental objectives")
            
        except Exception as e:
            self.logger.error(f"Error initializing environmental objectives: {e}")
    
    async def _store_aspect(self, aspect: EnvironmentalAspect):
        """Store environmental aspect in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO environmental_aspects
                (aspect_id, aspect_name, aspect_description, activity, environmental_condition,
                 environmental_impact, significance_level, significance_score, control_measures,
                 monitoring_requirements, legal_requirements, responsible_person, review_date,
                 next_review_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                aspect.aspect_id, aspect.aspect_name, aspect.aspect_description,
                aspect.activity, aspect.environmental_condition, aspect.environmental_impact,
                aspect.significance_level.value, aspect.significance_score,
                json.dumps(aspect.control_measures), json.dumps(aspect.monitoring_requirements),
                json.dumps(aspect.legal_requirements), aspect.responsible_person,
                aspect.review_date, aspect.next_review_date
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing aspect: {e}")
            raise
    
    async def _store_legal_requirement(self, requirement: LegalRequirement):
        """Store legal requirement in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO legal_requirements
                (requirement_id, requirement_title, requirement_description, regulation_source,
                 jurisdiction, applicable_activities, compliance_status, compliance_evidence,
                 responsible_person, review_frequency, last_review_date, next_review_date,
                 compliance_actions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                requirement.requirement_id, requirement.requirement_title,
                requirement.requirement_description, requirement.regulation_source,
                requirement.jurisdiction, json.dumps(requirement.applicable_activities),
                requirement.compliance_status.value, json.dumps(requirement.compliance_evidence),
                requirement.responsible_person, requirement.review_frequency,
                requirement.last_review_date, requirement.next_review_date,
                json.dumps(requirement.compliance_actions)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing legal requirement: {e}")
            raise
    
    async def _store_objective(self, objective: EnvironmentalObjective):
        """Store environmental objective in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO environmental_objectives
                (objective_id, objective_title, objective_description, related_aspects,
                 target_value, current_value, measurement_unit, target_date, status,
                 progress_percentage, responsible_person, action_plans, resources_required,
                 monitoring_frequency, success_criteria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                objective.objective_id, objective.objective_title, objective.objective_description,
                json.dumps(objective.related_aspects), objective.target_value, objective.current_value,
                objective.measurement_unit, objective.target_date, objective.status.value,
                objective.progress_percentage, objective.responsible_person,
                json.dumps(objective.action_plans), json.dumps(objective.resources_required),
                objective.monitoring_frequency, json.dumps(objective.success_criteria)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing objective: {e}")
            raise
    
    async def conduct_environmental_impact_assessment(self) -> Dict[str, Any]:
        """Conduct comprehensive environmental impact assessment"""
        try:
            self.logger.info("Conducting environmental impact assessment...")
            
            assessment_results = {
                "assessment_date": time.time(),
                "assessment_scope": "Complete Syn_OS operations and development activities",
                "methodology": "ISO 14001 environmental aspects identification and evaluation",
                "significant_aspects": [],
                "impact_categories": {},
                "risk_assessment": {},
                "improvement_opportunities": [],
                "compliance_status": {}
            }
            
            # Analyze environmental aspects
            for aspect in self.environmental_aspects.values():
                if aspect.significance_level in [EnvironmentalAspectSignificance.HIGH, EnvironmentalAspectSignificance.CRITICAL]:
                    assessment_results["significant_aspects"].append({
                        "aspect_id": aspect.aspect_id,
                        "aspect_name": aspect.aspect_name,
                        "significance_score": aspect.significance_score,
                        "environmental_impact": aspect.environmental_impact,
                        "control_measures": aspect.control_measures
                    })
            
            # Categorize impacts
            impact_categories = {
                "climate_change": [],
                "resource_depletion": [],
                "pollution": [],
                "waste_generation": [],
                "biodiversity": []
            }
            
            for aspect in self.environmental_aspects.values():
                if "climate change" in aspect.environmental_impact.lower() or "greenhouse gas" in aspect.environmental_impact.lower():
                    impact_categories["climate_change"].append(aspect.aspect_id)
                if "energy" in aspect.environmental_impact.lower() or "resource" in aspect.environmental_impact.lower():
                    impact_categories["resource_depletion"].append(aspect.aspect_id)
                if "contamination" in aspect.environmental_impact.lower() or "pollution" in aspect.environmental_impact.lower():
                    impact_categories["pollution"].append(aspect.aspect_id)
                if "waste" in aspect.environmental_impact.lower():
                    impact_categories["waste_generation"].append(aspect.aspect_id)
            
            assessment_results["impact_categories"] = impact_categories
            
            # Risk assessment
            high_risk_aspects = [a for a in self.environmental_aspects.values() if a.significance_score >= 7.0]
            medium_risk_aspects = [a for a in self.environmental_aspects.values() if 4.0 <= a.significance_score < 7.0]
            low_risk_aspects = [a for a in self.environmental_aspects.values() if a.significance_score < 4.0]
            
            assessment_results["risk_assessment"] = {
                "high_risk_count": len(high_risk_aspects),
                "medium_risk_count": len(medium_risk_aspects),
                "low_risk_count": len(low_risk_aspects),
                "overall_risk_level": "HIGH" if len(high_risk_aspects) > 2 else "MEDIUM" if len(medium_risk_aspects) > 3 else "LOW"
            }
            
            # Improvement opportunities
            assessment_results["improvement_opportunities"] = [
                "Implement renewable energy sourcing",
                "Optimize data center cooling efficiency",
                "Enhance e-waste recycling programs",
                "Develop carbon offset initiatives",
                "Improve energy monitoring systems"
            ]
            
            # Compliance status
            compliant_reqs = sum(1 for req in self.legal_requirements.values() if req.compliance_status == ComplianceStatus.COMPLIANT)
            total_reqs = len(self.legal_requirements)
            
            assessment_results["compliance_status"] = {
                "total_requirements": total_reqs,
                "compliant_requirements": compliant_reqs,
                "compliance_rate": (compliant_reqs / total_reqs * 100) if total_reqs > 0 else 0,
                "non_compliant_requirements": [req.requirement_id for req in self.legal_requirements.values()
                                             if req.compliance_status == ComplianceStatus.NON_COMPLIANT]
            }
            
            return assessment_results
            
        except Exception as e:
            self.logger.error(f"Error conducting environmental impact assessment: {e}")
            return {
                "error": str(e),
                "assessment_date": time.time(),
                "status": "failed"
            }
    
    async def _schedule_monitoring_tasks(self):
        """Schedule environmental monitoring tasks"""
        try:
            while True:
                # Run monitoring every 24 hours
                await asyncio.sleep(24 * 3600)
                
                # Check compliance status
                await self._check_compliance_status()
                
                # Update objective progress
                await self._update_objective_progress()
                
                # Generate monitoring reports
                await self._generate_monitoring_reports()
                
        except Exception as e:
            self.logger.error(f"Error in monitoring tasks: {e}")
    
    async def _check_compliance_status(self):
        """Check legal compliance status"""
        try:
            current_time = time.time()
            
            for requirement in self.legal_requirements.values():
                if requirement.next_review_date <= current_time:
                    self.logger.info(f"Legal requirement due for review: {requirement.requirement_id}")
                    # Could trigger notification system here
                    
        except Exception as e:
            self.logger.error(f"Error checking compliance status: {e}")
    
    async def _update_objective_progress(self):
        """Update environmental objective progress"""
        try:
            for objective in self.environmental_objectives.values():
                if objective.status == ObjectiveStatus.IN_PROGRESS:
                    # Simulate progress update (in real implementation, this would be based on actual measurements)
                    if objective.progress_percentage < 100:
                        objective.progress_percentage = min(100, objective.progress_percentage + 5)
                        await self._store_objective(objective)
                        
        except Exception as e:
            self.logger.error(f"Error updating objective progress: {e}")
    
    async def _generate_monitoring_reports(self):
        """Generate environmental monitoring reports"""
        try:
            report_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
            report_file = f"{self.reports_directory}/environmental_monitoring_{report_time}.json"
            
            report_data = {
                "report_date": time.time(),
                "environmental_aspects": len(self.environmental_aspects),
                "legal_requirements": len(self.legal_requirements),
                "environmental_objectives": len(self.environmental_objectives),
                "compliance_rate": self._calculate_compliance_rate(),
                "significant_aspects": [a.aspect_id for a in self.environmental_aspects.values()
                                      if a.significance_level in [EnvironmentalAspectSignificance.HIGH,
                                                                 EnvironmentalAspectSignificance.CRITICAL]]
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
                
            self.logger.info(f"Generated monitoring report: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating monitoring reports: {e}")
    
    def _calculate_compliance_rate(self) -> float:
        """Calculate overall compliance rate"""
        if not self.legal_requirements:
            return 100.0
            
        compliant_count = sum(1 for req in self.legal_requirements.values()
                            if req.compliance_status == ComplianceStatus.COMPLIANT)
        return (compliant_count / len(self.legal_requirements)) * 100
    
    async def get_ems_metrics(self) -> Dict[str, Any]:
        """Get EMS performance metrics"""
        try:
            # Environmental aspect metrics
            total_aspects = len(self.environmental_aspects)
            significant_aspects = sum(1 for a in self.environmental_aspects.values()
                                    if a.significance_level in [EnvironmentalAspectSignificance.HIGH,
                                                               EnvironmentalAspectSignificance.CRITICAL])
            
            # Legal compliance metrics
            total_requirements = len(self.legal_requirements)
            compliant_requirements = sum(1 for r in self.legal_requirements.values()
                                       if r.compliance_status == ComplianceStatus.COMPLIANT)
            
            # Objective metrics
            total_objectives = len(self.environmental_objectives)
            achieved_objectives = sum(1 for o in self.environmental_objectives.values()
                                    if o.status == ObjectiveStatus.ACHIEVED)
            
            # Calculate overall EMS effectiveness
            aspect_management = (significant_aspects / total_aspects * 100) if total_aspects > 0 else 0
            compliance_rate = (compliant_requirements / total_requirements * 100) if total_requirements > 0 else 0
            objective_achievement = (achieved_objectives / total_objectives * 100) if total_objectives > 0 else 0
            
            overall_effectiveness = (aspect_management + compliance_rate + objective_achievement) / 3
            
            metrics = {
                "overall_effectiveness": round(overall_effectiveness, 2),
                "aspect_metrics": {
                    "total_aspects": total_aspects,
                    "significant_aspects": significant_aspects,
                    "aspect_management_rate": round(aspect_management, 2)
                },
                "compliance_metrics": {
                    "total_requirements": total_requirements,
                    "compliant_requirements": compliant_requirements,
                    "compliance_rate": round(compliance_rate, 2)
                },
                "objective_metrics": {
                    "total_objectives": total_objectives,
                    "achieved_objectives": achieved_objectives,
                    "achievement_rate": round(objective_achievement, 2)
                },
                "environmental_performance": {
                    "energy_efficiency": "monitoring_required",
                    "waste_reduction": "monitoring_required",
                    "carbon_footprint": "monitoring_required",
                    "resource_conservation": "monitoring_required"
                },
                "timestamp": time.time()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting EMS metrics: {e}")
            return {
                "error": str(e),
                "overall_effectiveness": 0.0,
                "timestamp": time.time()
            }


# Global EMS instance
ems_instance = None

async def get_ems_instance():
    """Get global EMS instance"""
    global ems_instance
    if ems_instance is None:
        ems_instance = EnvironmentalManagementSystem()
        await asyncio.sleep(1)  # Allow initialization
    return ems_instance


if __name__ == "__main__":
    async def main():
        """Main function for testing"""
        logging.basicConfig(level=logging.INFO)
        
        # Initialize EMS
        ems = EnvironmentalManagementSystem()
        await asyncio.sleep(3)  # Allow initialization
        
        # Conduct environmental impact assessment
        print("Conducting environmental impact assessment...")
        assessment = await ems.conduct_environmental_impact_assessment()
        print(f"Assessment Results: {json.dumps(assessment, indent=2)}")
        
        # Get EMS metrics
        print("Getting EMS metrics...")
        metrics = await ems.get_ems_metrics()
        print(f"EMS Metrics: {json.dumps(metrics, indent=2)}")
    
    asyncio.run(main())