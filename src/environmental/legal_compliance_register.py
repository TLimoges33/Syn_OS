#!/usr/bin/env python3
"""
Legal Compliance Register
Comprehensive legal and regulatory compliance management system
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


class ComplianceStatus(Enum):
    """Legal compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    NOT_APPLICABLE = "not_applicable"
    PENDING_ASSESSMENT = "pending_assessment"


class RequirementType(Enum):
    """Type of legal requirement"""
    FEDERAL_LAW = "federal_law"
    STATE_LAW = "state_law"
    LOCAL_ORDINANCE = "local_ordinance"
    INTERNATIONAL_TREATY = "international_treaty"
    INDUSTRY_STANDARD = "industry_standard"
    VOLUNTARY_COMMITMENT = "voluntary_commitment"
    PERMIT_CONDITION = "permit_condition"
    CONTRACT_OBLIGATION = "contract_obligation"


class ReviewFrequency(Enum):
    """Review frequency for legal requirements"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    BIANNUALLY = "biannually"
    AS_NEEDED = "as_needed"


@dataclass
class LegalRequirement:
    """Legal requirement definition"""
    requirement_id: str
    requirement_title: str
    requirement_description: str
    requirement_type: RequirementType
    regulation_source: str
    regulation_number: str
    jurisdiction: str
    effective_date: float
    last_updated: float
    applicable_activities: List[str]
    applicable_locations: List[str]
    compliance_obligations: List[str]
    compliance_status: ComplianceStatus
    compliance_evidence: List[str]
    compliance_actions: List[str]
    responsible_person: str
    backup_responsible: str
    review_frequency: ReviewFrequency
    last_review_date: float
    next_review_date: float
    compliance_deadline: Optional[float]
    penalties_for_non_compliance: str
    related_permits: List[str]
    related_aspects: List[str]
    monitoring_requirements: List[str]
    reporting_requirements: List[str]


@dataclass
class ComplianceAssessment:
    """Compliance assessment record"""
    assessment_id: str
    requirement_id: str
    assessment_date: float
    assessor: str
    assessment_method: str
    compliance_status: ComplianceStatus
    compliance_percentage: float
    findings: List[str]
    evidence_reviewed: List[str]
    gaps_identified: List[str]
    corrective_actions: List[str]
    target_completion_date: Optional[float]
    follow_up_required: bool
    next_assessment_date: float
    assessment_notes: str


@dataclass
class ComplianceAction:
    """Compliance action item"""
    action_id: str
    requirement_id: str
    action_title: str
    action_description: str
    action_type: str  # corrective, preventive, improvement
    priority: str  # low, medium, high, critical
    responsible_person: str
    target_completion_date: float
    actual_completion_date: Optional[float]
    status: str  # planned, in_progress, completed, overdue, cancelled
    resources_required: List[str]
    budget_estimate: float
    actual_cost: Optional[float]
    progress_percentage: float
    progress_notes: str
    verification_method: str
    verification_date: Optional[float]
    effectiveness_review: str


class LegalComplianceRegister:
    """
    Legal Compliance Register
    Comprehensive legal and regulatory compliance management
    """
    
    def __init__(self):
        """Initialize legal compliance register"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.compliance_directory = "/var/lib/synos/environmental/compliance"
        self.database_file = f"{self.compliance_directory}/compliance.db"
        self.documents_directory = f"{self.compliance_directory}/documents"
        self.assessments_directory = f"{self.compliance_directory}/assessments"
        self.reports_directory = f"{self.compliance_directory}/reports"
        
        # System components
        self.legal_requirements: Dict[str, LegalRequirement] = {}
        self.compliance_assessments: Dict[str, ComplianceAssessment] = {}
        self.compliance_actions: Dict[str, ComplianceAction] = {}
        
        # Compliance tracking
        self.compliance_calendar: Dict[str, List[str]] = {}  # date -> requirement_ids
        self.overdue_requirements: List[str] = []
        
        # Initialize system
        asyncio.create_task(self._initialize_register())
    
    async def _initialize_register(self):
        """Initialize compliance register"""
        try:
            self.logger.info("Initializing Legal Compliance Register...")
            
            # Create directories
            for directory in [self.compliance_directory, self.documents_directory, 
                            self.assessments_directory, self.reports_directory]:
                os.makedirs(directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_existing_data()
            
            # Initialize core legal requirements
            await self._initialize_legal_requirements()
            
            # Start compliance monitoring
            asyncio.create_task(self._start_compliance_monitoring())
            
            self.logger.info("Legal Compliance Register initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing compliance register: {e}")
    
    async def _initialize_database(self):
        """Initialize compliance database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Legal requirements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS legal_requirements (
                    requirement_id TEXT PRIMARY KEY,
                    requirement_title TEXT NOT NULL,
                    requirement_description TEXT,
                    requirement_type TEXT,
                    regulation_source TEXT,
                    regulation_number TEXT,
                    jurisdiction TEXT,
                    effective_date REAL,
                    last_updated REAL,
                    applicable_activities TEXT,
                    applicable_locations TEXT,
                    compliance_obligations TEXT,
                    compliance_status TEXT,
                    compliance_evidence TEXT,
                    compliance_actions TEXT,
                    responsible_person TEXT,
                    backup_responsible TEXT,
                    review_frequency TEXT,
                    last_review_date REAL,
                    next_review_date REAL,
                    compliance_deadline REAL,
                    penalties_for_non_compliance TEXT,
                    related_permits TEXT,
                    related_aspects TEXT,
                    monitoring_requirements TEXT,
                    reporting_requirements TEXT
                )
            ''')
            
            # Compliance assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    requirement_id TEXT,
                    assessment_date REAL,
                    assessor TEXT,
                    assessment_method TEXT,
                    compliance_status TEXT,
                    compliance_percentage REAL,
                    findings TEXT,
                    evidence_reviewed TEXT,
                    gaps_identified TEXT,
                    corrective_actions TEXT,
                    target_completion_date REAL,
                    follow_up_required BOOLEAN,
                    next_assessment_date REAL,
                    assessment_notes TEXT,
                    FOREIGN KEY (requirement_id) REFERENCES legal_requirements (requirement_id)
                )
            ''')
            
            # Compliance actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_actions (
                    action_id TEXT PRIMARY KEY,
                    requirement_id TEXT,
                    action_title TEXT,
                    action_description TEXT,
                    action_type TEXT,
                    priority TEXT,
                    responsible_person TEXT,
                    target_completion_date REAL,
                    actual_completion_date REAL,
                    status TEXT,
                    resources_required TEXT,
                    budget_estimate REAL,
                    actual_cost REAL,
                    progress_percentage REAL,
                    progress_notes TEXT,
                    verification_method TEXT,
                    verification_date REAL,
                    effectiveness_review TEXT,
                    FOREIGN KEY (requirement_id) REFERENCES legal_requirements (requirement_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requirements_status ON legal_requirements (compliance_status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requirements_review ON legal_requirements (next_review_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assessments_date ON compliance_assessments (assessment_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_status ON compliance_actions (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_due ON compliance_actions (target_completion_date)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing compliance database: {e}")
            raise
    
    async def _load_existing_data(self):
        """Load existing compliance data"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load legal requirements
            cursor.execute('SELECT * FROM legal_requirements')
            for row in cursor.fetchall():
                requirement = LegalRequirement(
                    requirement_id=row[0],
                    requirement_title=row[1],
                    requirement_description=row[2],
                    requirement_type=RequirementType(row[3]),
                    regulation_source=row[4],
                    regulation_number=row[5],
                    jurisdiction=row[6],
                    effective_date=row[7],
                    last_updated=row[8],
                    applicable_activities=json.loads(row[9]) if row[9] else [],
                    applicable_locations=json.loads(row[10]) if row[10] else [],
                    compliance_obligations=json.loads(row[11]) if row[11] else [],
                    compliance_status=ComplianceStatus(row[12]),
                    compliance_evidence=json.loads(row[13]) if row[13] else [],
                    compliance_actions=json.loads(row[14]) if row[14] else [],
                    responsible_person=row[15],
                    backup_responsible=row[16],
                    review_frequency=ReviewFrequency(row[17]),
                    last_review_date=row[18],
                    next_review_date=row[19],
                    compliance_deadline=row[20],
                    penalties_for_non_compliance=row[21],
                    related_permits=json.loads(row[22]) if row[22] else [],
                    related_aspects=json.loads(row[23]) if row[23] else [],
                    monitoring_requirements=json.loads(row[24]) if row[24] else [],
                    reporting_requirements=json.loads(row[25]) if row[25] else []
                )
                self.legal_requirements[requirement.requirement_id] = requirement
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.legal_requirements)} legal requirements")
            
        except Exception as e:
            self.logger.error(f"Error loading existing compliance data: {e}")
    
    async def _initialize_legal_requirements(self):
        """Initialize core legal requirements"""
        try:
            current_time = time.time()
            
            core_requirements = [
                {
                    "requirement_id": "LR-EPA-001",
                    "title": "Clean Air Act Compliance",
                    "description": "Compliance with federal Clean Air Act requirements for air emissions",
                    "type": RequirementType.FEDERAL_LAW,
                    "source": "Environmental Protection Agency",
                    "number": "42 U.S.C. §7401",
                    "jurisdiction": "United States",
                    "activities": ["Data center operations", "Backup generator operations"],
                    "obligations": ["Monitor air emissions", "Report exceedances", "Maintain emission controls"],
                    "monitoring": ["Annual emissions inventory", "Continuous monitoring if applicable"],
                    "reporting": ["Annual emissions report", "Exceedance notifications"]
                },
                {
                    "requirement_id": "LR-EPA-002",
                    "title": "Resource Conservation and Recovery Act (RCRA)",
                    "description": "Proper management and disposal of hazardous waste",
                    "type": RequirementType.FEDERAL_LAW,
                    "source": "Environmental Protection Agency",
                    "number": "42 U.S.C. §6901",
                    "jurisdiction": "United States",
                    "activities": ["Electronic waste disposal", "Battery disposal", "Chemical waste management"],
                    "obligations": ["Proper waste characterization", "Manifest tracking", "Authorized disposal"],
                    "monitoring": ["Waste generation tracking", "Disposal verification"],
                    "reporting": ["Biennial hazardous waste report", "Exception reports"]
                },
                {
                    "requirement_id": "LR-EPA-003",
                    "title": "Clean Water Act Compliance",
                    "description": "Protection of water resources and discharge permits",
                    "type": RequirementType.FEDERAL_LAW,
                    "source": "Environmental Protection Agency",
                    "number": "33 U.S.C. §1251",
                    "jurisdiction": "United States",
                    "activities": ["Facility operations", "Stormwater management"],
                    "obligations": ["Obtain discharge permits", "Monitor discharge quality", "Prevent spills"],
                    "monitoring": ["Discharge monitoring", "Stormwater inspections"],
                    "reporting": ["Discharge monitoring reports", "Spill notifications"]
                },
                {
                    "requirement_id": "LR-ENERGY-001",
                    "title": "Energy Efficiency Standards",
                    "description": "Compliance with federal and state energy efficiency requirements",
                    "type": RequirementType.FEDERAL_LAW,
                    "source": "Department of Energy",
                    "number": "ENERGY STAR Program",
                    "jurisdiction": "United States",
                    "activities": ["Equipment procurement", "Building operations"],
                    "obligations": ["Use energy efficient equipment", "Report energy consumption", "Meet efficiency targets"],
                    "monitoring": ["Energy consumption tracking", "Equipment efficiency verification"],
                    "reporting": ["Annual energy reports", "Efficiency compliance documentation"]
                },
                {
                    "requirement_id": "LR-OSHA-001",
                    "title": "Occupational Safety and Health Standards",
                    "description": "Workplace safety requirements for environmental hazards",
                    "type": RequirementType.FEDERAL_LAW,
                    "source": "Occupational Safety and Health Administration",
                    "number": "29 CFR 1910",
                    "jurisdiction": "United States",
                    "activities": ["Chemical handling", "Waste management", "Equipment maintenance"],
                    "obligations": ["Provide safe workplace", "Train employees", "Maintain safety records"],
                    "monitoring": ["Safety inspections", "Incident tracking"],
                    "reporting": ["Injury and illness reports", "Safety training records"]
                },
                {
                    "requirement_id": "LR-STATE-001",
                    "title": "State Environmental Permits",
                    "description": "State-level environmental permits and authorizations",
                    "type": RequirementType.STATE_LAW,
                    "source": "State Environmental Agency",
                    "number": "Various",
                    "jurisdiction": "State",
                    "activities": ["Air emissions", "Water discharge", "Waste management"],
                    "obligations": ["Maintain valid permits", "Comply with permit conditions", "Renew permits timely"],
                    "monitoring": ["Permit condition compliance", "Renewal tracking"],
                    "reporting": ["Permit compliance reports", "Renewal applications"]
                }
            ]
            
            for req_data in core_requirements:
                if req_data["requirement_id"] not in self.legal_requirements:
                    requirement = LegalRequirement(
                        requirement_id=req_data["requirement_id"],
                        requirement_title=req_data["title"],
                        requirement_description=req_data["description"],
                        requirement_type=req_data["type"],
                        regulation_source=req_data["source"],
                        regulation_number=req_data["number"],
                        jurisdiction=req_data["jurisdiction"],
                        effective_date=current_time,
                        last_updated=current_time,
                        applicable_activities=req_data["activities"],
                        applicable_locations=["All facilities"],
                        compliance_obligations=req_data["obligations"],
                        compliance_status=ComplianceStatus.UNDER_REVIEW,
                        compliance_evidence=[],
                        compliance_actions=[],
                        responsible_person="compliance_manager",
                        backup_responsible="environmental_manager",
                        review_frequency=ReviewFrequency.ANNUALLY,
                        last_review_date=current_time,
                        next_review_date=current_time + (365 * 24 * 3600),  # 1 year
                        compliance_deadline=None,
                        penalties_for_non_compliance="Fines, penalties, and potential criminal liability",
                        related_permits=[],
                        related_aspects=["EA-001", "EA-002", "EA-003"],
                        monitoring_requirements=req_data["monitoring"],
                        reporting_requirements=req_data["reporting"]
                    )
                    
                    await self._store_legal_requirement(requirement)
                    self.legal_requirements[requirement.requirement_id] = requirement
            
            self.logger.info(f"Initialized {len(core_requirements)} legal requirements")
            
        except Exception as e:
            self.logger.error(f"Error initializing legal requirements: {e}")
    
    async def _store_legal_requirement(self, requirement: LegalRequirement):
        """Store legal requirement in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO legal_requirements
                (requirement_id, requirement_title, requirement_description, requirement_type,
                 regulation_source, regulation_number, jurisdiction, effective_date, last_updated,
                 applicable_activities, applicable_locations, compliance_obligations,
                 compliance_status, compliance_evidence, compliance_actions, responsible_person,
                 backup_responsible, review_frequency, last_review_date, next_review_date,
                 compliance_deadline, penalties_for_non_compliance, related_permits,
                 related_aspects, monitoring_requirements, reporting_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                requirement.requirement_id, requirement.requirement_title,
                requirement.requirement_description, requirement.requirement_type.value,
                requirement.regulation_source, requirement.regulation_number,
                requirement.jurisdiction, requirement.effective_date, requirement.last_updated,
                json.dumps(requirement.applicable_activities),
                json.dumps(requirement.applicable_locations),
                json.dumps(requirement.compliance_obligations),
                requirement.compliance_status.value,
                json.dumps(requirement.compliance_evidence),
                json.dumps(requirement.compliance_actions),
                requirement.responsible_person, requirement.backup_responsible,
                requirement.review_frequency.value, requirement.last_review_date,
                requirement.next_review_date, requirement.compliance_deadline,
                requirement.penalties_for_non_compliance,
                json.dumps(requirement.related_permits),
                json.dumps(requirement.related_aspects),
                json.dumps(requirement.monitoring_requirements),
                json.dumps(requirement.reporting_requirements)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing legal requirement: {e}")
            raise
    
    async def _start_compliance_monitoring(self):
        """Start compliance monitoring tasks"""
        try:
            # Start review date monitoring
            asyncio.create_task(self._monitor_review_dates())
            
            # Start compliance deadline monitoring
            asyncio.create_task(self._monitor_compliance_deadlines())
            
            # Start periodic compliance assessment
            asyncio.create_task(self._periodic_compliance_assessment())
            
        except Exception as e:
            self.logger.error(f"Error starting compliance monitoring: {e}")
    
    async def _monitor_review_dates(self):
        """Monitor legal requirement review dates"""
        try:
            while True:
                current_time = time.time()
                
                for requirement in self.legal_requirements.values():
                    if requirement.next_review_date <= current_time:
                        self.logger.info(f"Legal requirement due for review: {requirement.requirement_id}")
                        
                        # Schedule compliance assessment
                        await self._schedule_compliance_assessment(requirement.requirement_id)
                
                # Check daily
                await asyncio.sleep(86400)
                
        except Exception as e:
            self.logger.error(f"Error monitoring review dates: {e}")
    
    async def _monitor_compliance_deadlines(self):
        """Monitor compliance deadlines"""
        try:
            while True:
                current_time = time.time()
                
                for requirement in self.legal_requirements.values():
                    if (requirement.compliance_deadline and 
                        requirement.compliance_deadline <= current_time and
                        requirement.compliance_status != ComplianceStatus.COMPLIANT):
                        
                        self.logger.warning(f"Compliance deadline passed: {requirement.requirement_id}")
                        self.overdue_requirements.append(requirement.requirement_id)
                
                # Check daily
                await asyncio.sleep(86400)
                
        except Exception as e:
            self.logger.error(f"Error monitoring compliance deadlines: {e}")
    
    async def _periodic_compliance_assessment(self):
        """Perform periodic compliance assessments"""
        try:
            while True:
                # Assess compliance monthly
                await asyncio.sleep(30 * 24 * 3600)  # 30 days
                
                for requirement_id in self.legal_requirements.keys():
                    await self._conduct_compliance_assessment(requirement_id)
                
        except Exception as e:
            self.logger.error(f"Error in periodic compliance assessment: {e}")
    
    async def _schedule_compliance_assessment(self, requirement_id: str):
        """Schedule a compliance assessment"""
        try:
            if requirement_id in self.legal_requirements:
                # Update next review date
                requirement = self.legal_requirements[requirement_id]
                
                # Calculate next review date based on frequency
                frequency_days = {
                    ReviewFrequency.MONTHLY: 30,
                    ReviewFrequency.QUARTERLY: 90,
                    ReviewFrequency.SEMI_ANNUALLY: 180,
                    ReviewFrequency.ANNUALLY: 365,
                    ReviewFrequency.BIANNUALLY: 730,
                    ReviewFrequency.AS_NEEDED: 365  # Default to annual
                }
                
                days = frequency_days.get(requirement.review_frequency, 365)
                requirement.next_review_date = time.time() + (days * 24 * 3600)
                
                await self._store_legal_requirement(requirement)
                
                self.logger.info(f"Scheduled compliance assessment for {requirement_id}")
                
        except Exception as e:
            self.logger.error(f"Error scheduling compliance assessment: {e}")
    
    async def _conduct_compliance_assessment(self, requirement_id: str) -> str:
        """Conduct compliance assessment"""
        try:
            if requirement_id not in self.legal_requirements:
                raise ValueError(f"Legal requirement {requirement_id} not found")
            
            requirement = self.legal_requirements[requirement_id]
            current_time = time.time()
            assessment_id = f"CA-{int(current_time)}-{str(uuid.uuid4())[:8]}"
            
            # Simulate compliance assessment (in real implementation, this would involve actual evaluation)
            compliance_percentage = 85.0  # Simulated value
            compliance_status = ComplianceStatus.COMPLIANT if compliance_percentage >= 90 else ComplianceStatus.UNDER_REVIEW
            
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                requirement_id=requirement_id,
                assessment_date=current_time,
                assessor="compliance_manager",
                assessment_method="Document review and site inspection",
                compliance_status=compliance_status,
                compliance_percentage=compliance_percentage,
                findings=[
                    "Documentation is current and accessible",
                    "Procedures are being followed",
                    "Some minor improvements needed in record keeping"
                ],
                evidence_reviewed=[
                    "Compliance procedures",
                    "Training records",
                    "Monitoring data",
                    "Previous assessment reports"
                ],
                gaps_identified=[
                    "Update training materials",
                    "Improve record organization"
                ],
                corrective_actions=[
                    "Update training materials within 30 days",
                    "Implement improved record keeping system"
                ],
                target_completion_date=current_time + (30 * 24 * 3600),  # 30 days
                follow_up_required=True,
                next_assessment_date=current_time + (90 * 24 * 3600),  # 90 days
                assessment_notes="Overall compliance is good with minor improvements needed"
            )
            
            # Store assessment
            await self._store_compliance_assessment(assessment)
            self.compliance_assessments[assessment_id] = assessment
            
            # Update requirement compliance status
            requirement.compliance_status = compliance_status
            requirement.last_review_date = current_time
            await self._store_legal_requirement(requirement)
            
            self.logger.info(f"Conducted compliance assessment: {assessment_id}")
            return assessment_id
            
        except Exception as e:
            self.logger.error(f"Error conducting compliance assessment: {e}")
            raise
    
    async def _store_compliance_assessment(self, assessment: ComplianceAssessment):
        """Store compliance assessment in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO compliance_assessments
                (assessment_id, requirement_id, assessment_date, assessor, assessment_method,
                 compliance_status, compliance_percentage, findings, evidence_reviewed,
                 gaps_identified, corrective_actions, target_completion_date, follow_up_required,
                 next_assessment_date, assessment_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                assessment.assessment_id, assessment.requirement_id, assessment.assessment_date,
                assessment.assessor, assessment.assessment_method, assessment.compliance_status.value,
                assessment.compliance_percentage, json.dumps(assessment.findings),
                json.dumps(assessment.evidence_reviewed), json.dumps(assessment.gaps_identified),
                json.dumps(assessment.corrective_actions), assessment.target_completion_date,
                assessment.follow_up_required, assessment.next_assessment_date,
                assessment.assessment_notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing compliance assessment: {e}")
            raise
    
    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance register summary"""
        try:
            current_time = time.time()
            
            # Count requirements by status
            total_requirements = len(self.legal_requirements)
            compliant_requirements = sum(1 for r in self.legal_requirements.values() 
                                       if r.compliance_status == ComplianceStatus.COMPLIANT)
            non_compliant_requirements = sum(1 for r in self.legal_requirements.values() 
                                           if r.compliance_status == ComplianceStatus.NON_COMPLIANT)
            under_review_requirements = sum(1 for r in self.legal_requirements.values() 
                                          if r.compliance_status == ComplianceStatus.UNDER_REVIEW)
            
            # Count overdue reviews
            overdue_reviews = sum(1 for r in self.legal_requirements.values() 
                                if r.next_review_date <= current_time)
            
            # Count requirements by type
            requirement_types = {}
            for requirement in self.legal_requirements.values():
                req_type = requirement.requirement_type.value
                if req_type not in requirement_types:
                    requirement_types[req_type] = 0
                requirement_types[req_type] += 1
            
            # Calculate compliance rate
            compliance_rate = (compliant_requirements / total_requirements * 100) if total_requirements > 0 else 0
            
            summary = {
                "compliance_statistics": {
                    "total_requirements": total_requirements,
                    "compliant_requirements": compliant_requirements,
                    "non_compliant_requirements": non_compliant_requirements,
                    "under_review_requirements": under_review_requirements,
                    "compliance_rate": round(compliance_rate, 2)
                },
                "review_status": {
                    "overdue_reviews": overdue_reviews,
                    "overdue_requirements": len(self.overdue_requirements)
                },
                "requirement_types": requirement_types,
                "assessments": {
                    "total_assessments": len(self.compliance_assessments),
                    "recent_assessments": sum(1 for a in self.compliance_assessments.values() 
                                            if current_time - a.assessment_date <= 86400 * 30)  # Last 30 days
                },
                "system_health": {
                    "overall_status": "COMPLIANT" if compliance_rate >= 90 else "NEEDS_ATTENTION" if compliance_rate >= 70 else "NON_COMPLIANT",
                    "critical_issues": non_compliant_requirements + len(self.overdue_requirements),
                    "action_required": overdue_reviews > 0 or non_compliant_requirements > 0
                },
                "timestamp": current_time
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting compliance summary: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "system_health": {"overall_status": "ERROR", "critical_issues": 0, "action_required": True}
            }


# Global compliance register instance
compliance_register_instance = None

async def get_compliance_register_instance():
    """Get global compliance register instance"""
    global compliance_register_instance
    if compliance_register_instance is None:
        compliance_register_instance = LegalComplianceRegister()
        await asyncio.sleep(1)  # Allow initialization
    return compliance_register_instance


if __name__ == "__main__":
    async def main():
        """Main function for testing"""
        logging.basicConfig(level=logging.INFO)
        
        # Initialize compliance register
        register = LegalComplianceRegister()
        await asyncio.sleep(3)  # Allow initialization
        
        # Get compliance summary
        print("Getting compliance summary...")
        summary = await register.get_compliance_summary()
        print(f"Compliance Summary: {json.dumps(summary, indent=2)}")
        
        # Conduct sample assessment
        if register.legal_requirements:
            requirement_id = list(register.legal_requirements.keys())[0]
            print(f"Conducting assessment for {requirement_id}...")
            assessment_id = await register._conduct_compliance_assessment(requirement_id)
            print(f"Assessment completed: {assessment_id}")
    
    asyncio.run(main())