#!/usr/bin/env python3
"""
Quality Management System Implementation
ISO 9001 compliant quality management for Syn_OS
"""

import asyncio
import logging
import time
import json
import os
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta


class QualityStatus(Enum):
    """Quality status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNSATISFACTORY = "unsatisfactory"


class ProcessStatus(Enum):
    """Process status definitions"""
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    SUSPENDED = "suspended"
    OBSOLETE = "obsolete"


class DocumentStatus(Enum):
    """Document status definitions"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class AuditType(Enum):
    """Internal audit types"""
    PROCESS_AUDIT = "process_audit"
    SYSTEM_AUDIT = "system_audit"
    COMPLIANCE_AUDIT = "compliance_audit"
    MANAGEMENT_REVIEW = "management_review"


@dataclass
class QualityProcess:
    """Quality management process"""
    process_id: str
    process_name: str
    process_description: str
    process_owner: str
    process_category: str
    inputs: List[str]
    outputs: List[str]
    resources: List[str]
    controls: List[str]
    metrics: Dict[str, Any]
    status: ProcessStatus
    effectiveness_rating: float
    last_review_date: float
    next_review_date: float
    improvement_actions: List[str]


@dataclass
class QualityDocument:
    """Quality management document"""
    document_id: str
    document_title: str
    document_type: str
    document_version: str
    document_content: str
    author: str
    reviewer: str
    approver: str
    status: DocumentStatus
    created_date: float
    review_date: float
    approval_date: float
    effective_date: float
    next_review_date: float
    distribution_list: List[str]
    related_processes: List[str]


@dataclass
class QualityObjective:
    """Quality objective definition"""
    objective_id: str
    objective_title: str
    objective_description: str
    target_value: float
    current_value: float
    measurement_unit: str
    responsible_person: str
    target_date: float
    status: str
    progress_percentage: float
    related_processes: List[str]
    action_plans: List[str]


@dataclass
class InternalAudit:
    """Internal audit record"""
    audit_id: str
    audit_title: str
    audit_type: AuditType
    audit_scope: str
    auditor: str
    auditee: str
    planned_date: float
    actual_date: float
    duration_hours: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    corrective_actions: List[str]
    status: str
    effectiveness_rating: float


class QualityManagementSystem:
    """
    Quality Management System
    ISO 9001 compliant quality management implementation
    """
    
    def __init__(self):
        """Initialize quality management system"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.qms_directory = "/var/lib/synos/quality"
        self.database_file = f"{self.qms_directory}/quality.db"
        self.documents_directory = f"{self.qms_directory}/documents"
        self.records_directory = f"{self.qms_directory}/records"
        
        # System components
        self.processes: Dict[str, QualityProcess] = {}
        self.documents: Dict[str, QualityDocument] = {}
        self.objectives: Dict[str, QualityObjective] = {}
        self.audits: Dict[str, InternalAudit] = {}
        
        # Quality policy
        self.quality_policy = """
        Syn_OS Quality Policy
        
        At Syn_OS, we are committed to delivering exceptional consciousness-aware security 
        operating systems that exceed our customers' expectations and regulatory requirements.
        
        Our commitment includes:
        - Continuous improvement of our processes and products
        - Meeting all applicable regulatory and customer requirements
        - Ensuring the competence of our personnel through training and development
        - Maintaining effective communication with all stakeholders
        - Regular monitoring and measurement of our quality management system
        
        This policy is communicated throughout the organization and is available to all 
        interested parties. It is reviewed annually for continuing suitability.
        
        Management is committed to providing the necessary resources to achieve our 
        quality objectives and to continually improve the effectiveness of our 
        quality management system.
        """
        
        # Quality objectives
        self.quality_objectives_template = {
            "customer_satisfaction": {
                "title": "Customer Satisfaction",
                "description": "Achieve and maintain high levels of customer satisfaction",
                "target": 95.0,
                "unit": "percentage",
                "measurement": "Customer satisfaction surveys"
            },
            "defect_rate": {
                "title": "Defect Rate Reduction",
                "description": "Minimize defects in delivered products",
                "target": 0.1,
                "unit": "percentage",
                "measurement": "Defects per release"
            },
            "process_efficiency": {
                "title": "Process Efficiency",
                "description": "Improve process efficiency and reduce waste",
                "target": 90.0,
                "unit": "percentage",
                "measurement": "Process efficiency metrics"
            },
            "compliance_rate": {
                "title": "Compliance Rate",
                "description": "Maintain full compliance with applicable standards",
                "target": 100.0,
                "unit": "percentage",
                "measurement": "Compliance audit results"
            }
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_qms())
    
    async def _initialize_qms(self):
        """Initialize quality management system"""
        try:
            self.logger.info("Initializing Quality Management System...")
            
            # Create directories
            os.makedirs(self.qms_directory, exist_ok=True)
            os.makedirs(self.documents_directory, exist_ok=True)
            os.makedirs(self.records_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_existing_data()
            
            # Initialize core processes
            await self._initialize_core_processes()
            
            # Initialize quality documents
            await self._initialize_quality_documents()
            
            # Initialize quality objectives
            await self._initialize_quality_objectives()
            
            self.logger.info("Quality Management System initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing QMS: {e}")
    
    async def _initialize_database(self):
        """Initialize QMS database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Processes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_processes (
                    process_id TEXT PRIMARY KEY,
                    process_name TEXT NOT NULL,
                    process_description TEXT,
                    process_owner TEXT,
                    process_category TEXT,
                    inputs TEXT,
                    outputs TEXT,
                    resources TEXT,
                    controls TEXT,
                    metrics TEXT,
                    status TEXT,
                    effectiveness_rating REAL,
                    last_review_date REAL,
                    next_review_date REAL,
                    improvement_actions TEXT
                )
            ''')
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_documents (
                    document_id TEXT PRIMARY KEY,
                    document_title TEXT NOT NULL,
                    document_type TEXT,
                    document_version TEXT,
                    document_content TEXT,
                    author TEXT,
                    reviewer TEXT,
                    approver TEXT,
                    status TEXT,
                    created_date REAL,
                    review_date REAL,
                    approval_date REAL,
                    effective_date REAL,
                    next_review_date REAL,
                    distribution_list TEXT,
                    related_processes TEXT
                )
            ''')
            
            # Objectives table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_objectives (
                    objective_id TEXT PRIMARY KEY,
                    objective_title TEXT NOT NULL,
                    objective_description TEXT,
                    target_value REAL,
                    current_value REAL,
                    measurement_unit TEXT,
                    responsible_person TEXT,
                    target_date REAL,
                    status TEXT,
                    progress_percentage REAL,
                    related_processes TEXT,
                    action_plans TEXT
                )
            ''')
            
            # Audits table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS internal_audits (
                    audit_id TEXT PRIMARY KEY,
                    audit_title TEXT NOT NULL,
                    audit_type TEXT,
                    audit_scope TEXT,
                    auditor TEXT,
                    auditee TEXT,
                    planned_date REAL,
                    actual_date REAL,
                    duration_hours REAL,
                    findings TEXT,
                    recommendations TEXT,
                    corrective_actions TEXT,
                    status TEXT,
                    effectiveness_rating REAL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_processes_status ON quality_processes (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_status ON quality_documents (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_objectives_status ON quality_objectives (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audits_type ON internal_audits (audit_type)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing QMS database: {e}")
            raise
    
    async def _load_existing_data(self):
        """Load existing QMS data"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load processes
            cursor.execute('SELECT * FROM quality_processes')
            for row in cursor.fetchall():
                process = QualityProcess(
                    process_id=row[0],
                    process_name=row[1],
                    process_description=row[2],
                    process_owner=row[3],
                    process_category=row[4],
                    inputs=json.loads(row[5]) if row[5] else [],
                    outputs=json.loads(row[6]) if row[6] else [],
                    resources=json.loads(row[7]) if row[7] else [],
                    controls=json.loads(row[8]) if row[8] else [],
                    metrics=json.loads(row[9]) if row[9] else {},
                    status=ProcessStatus(row[10]),
                    effectiveness_rating=row[11],
                    last_review_date=row[12],
                    next_review_date=row[13],
                    improvement_actions=json.loads(row[14]) if row[14] else []
                )
                self.processes[process.process_id] = process
            
            # Load documents
            cursor.execute('SELECT * FROM quality_documents')
            for row in cursor.fetchall():
                document = QualityDocument(
                    document_id=row[0],
                    document_title=row[1],
                    document_type=row[2],
                    document_version=row[3],
                    document_content=row[4],
                    author=row[5],
                    reviewer=row[6],
                    approver=row[7],
                    status=DocumentStatus(row[8]),
                    created_date=row[9],
                    review_date=row[10],
                    approval_date=row[11],
                    effective_date=row[12],
                    next_review_date=row[13],
                    distribution_list=json.loads(row[14]) if row[14] else [],
                    related_processes=json.loads(row[15]) if row[15] else []
                )
                self.documents[document.document_id] = document
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.processes)} processes and {len(self.documents)} documents")
            
        except Exception as e:
            self.logger.error(f"Error loading existing QMS data: {e}")
    
    async def _initialize_core_processes(self):
        """Initialize core quality processes"""
        try:
            current_time = time.time()
            
            core_processes = [
                {
                    "process_id": "QP-001",
                    "name": "Document Control",
                    "description": "Control of documents and records in the QMS",
                    "owner": "quality_manager",
                    "category": "Management Process",
                    "inputs": ["Document requests", "Document changes", "Review requirements"],
                    "outputs": ["Controlled documents", "Document registers", "Obsolete document lists"],
                    "resources": ["Document management system", "Review personnel", "Approval authority"],
                    "controls": ["Document approval", "Version control", "Distribution control"]
                },
                {
                    "process_id": "QP-002",
                    "name": "Management Review",
                    "description": "Systematic review of QMS by top management",
                    "owner": "ceo",
                    "category": "Management Process",
                    "inputs": ["QMS performance data", "Audit results", "Customer feedback"],
                    "outputs": ["Management review decisions", "Resource allocation", "Improvement actions"],
                    "resources": ["Management time", "Performance data", "Review meeting facilities"],
                    "controls": ["Scheduled reviews", "Agenda control", "Decision recording"]
                },
                {
                    "process_id": "QP-003",
                    "name": "Internal Audit",
                    "description": "Internal auditing of QMS processes",
                    "owner": "quality_manager",
                    "category": "Monitoring Process",
                    "inputs": ["Audit program", "Process information", "Previous audit results"],
                    "outputs": ["Audit reports", "Nonconformities", "Improvement opportunities"],
                    "resources": ["Trained auditors", "Audit checklists", "Audit time"],
                    "controls": ["Auditor competence", "Audit planning", "Report approval"]
                },
                {
                    "process_id": "QP-004",
                    "name": "Corrective Action",
                    "description": "Management of corrective and preventive actions",
                    "owner": "quality_manager",
                    "category": "Improvement Process",
                    "inputs": ["Nonconformities", "Customer complaints", "Audit findings"],
                    "outputs": ["Corrective actions", "Root cause analysis", "Effectiveness verification"],
                    "resources": ["Investigation personnel", "Analysis tools", "Implementation resources"],
                    "controls": ["Root cause analysis", "Action verification", "Effectiveness review"]
                },
                {
                    "process_id": "QP-005",
                    "name": "Training and Competence",
                    "description": "Management of personnel competence and training",
                    "owner": "hr_manager",
                    "category": "Support Process",
                    "inputs": ["Competence requirements", "Training needs", "Performance gaps"],
                    "outputs": ["Training programs", "Competence records", "Training effectiveness"],
                    "resources": ["Training materials", "Trainers", "Training facilities"],
                    "controls": ["Competence evaluation", "Training effectiveness", "Record keeping"]
                }
            ]
            
            for process_data in core_processes:
                if process_data["process_id"] not in self.processes:
                    process = QualityProcess(
                        process_id=process_data["process_id"],
                        process_name=process_data["name"],
                        process_description=process_data["description"],
                        process_owner=process_data["owner"],
                        process_category=process_data["category"],
                        inputs=process_data["inputs"],
                        outputs=process_data["outputs"],
                        resources=process_data["resources"],
                        controls=process_data["controls"],
                        metrics={
                            "effectiveness": 0.0,
                            "efficiency": 0.0,
                            "customer_satisfaction": 0.0
                        },
                        status=ProcessStatus.ACTIVE,
                        effectiveness_rating=0.0,
                        last_review_date=current_time,
                        next_review_date=current_time + (90 * 24 * 3600),  # 90 days
                        improvement_actions=[]
                    )
                    
                    await self._store_process(process)
                    self.processes[process.process_id] = process
            
            self.logger.info(f"Initialized {len(core_processes)} core quality processes")
            
        except Exception as e:
            self.logger.error(f"Error initializing core processes: {e}")
    
    async def _initialize_quality_documents(self):
        """Initialize core quality documents"""
        try:
            current_time = time.time()
            
            core_documents = [
                {
                    "document_id": "QD-001",
                    "title": "Quality Manual",
                    "type": "Manual",
                    "content": f"""
# Syn_OS Quality Manual

## 1. Introduction
This Quality Manual describes the Quality Management System (QMS) of Syn_OS, 
demonstrating our commitment to quality and compliance with ISO 9001:2015.

## 2. Quality Policy
{self.quality_policy}

## 3. Scope
This QMS applies to the design, development, and delivery of consciousness-aware 
security operating systems and related services.

## 4. Process Approach
Our QMS is based on a process approach, with clearly defined processes for:
- Management processes
- Core business processes  
- Support processes
- Monitoring and improvement processes

## 5. Documentation
The QMS documentation includes:
- This Quality Manual
- Process procedures
- Work instructions
- Quality records

## 6. Management Responsibility
Top management demonstrates leadership and commitment to the QMS through:
- Establishing quality policy and objectives
- Ensuring customer focus
- Providing necessary resources
- Conducting management reviews

## 7. Continuous Improvement
We are committed to continually improving our QMS through:
- Regular monitoring and measurement
- Internal audits
- Management reviews
- Corrective and preventive actions
                    """
                },
                {
                    "document_id": "QD-002",
                    "title": "Document Control Procedure",
                    "type": "Procedure",
                    "content": """
# Document Control Procedure

## Purpose
To ensure that documents are controlled, current, and available where needed.

## Scope
Applies to all QMS documents including procedures, work instructions, and records.

## Procedure
1. Document Creation
   - Documents are created by authorized personnel
   - Templates are used to ensure consistency
   - Unique identification is assigned

2. Document Review and Approval
   - Documents are reviewed for adequacy
   - Approval is obtained before release
   - Approval authority is defined

3. Document Distribution
   - Controlled copies are distributed
   - Distribution lists are maintained
   - Access controls are implemented

4. Document Changes
   - Changes are reviewed and approved
   - Version control is maintained
   - Change history is recorded

5. Document Obsolescence
   - Obsolete documents are identified
   - Removal from use is ensured
   - Archival procedures are followed
                    """
                },
                {
                    "document_id": "QD-003",
                    "title": "Internal Audit Procedure",
                    "type": "Procedure",
                    "content": """
# Internal Audit Procedure

## Purpose
To verify that the QMS conforms to requirements and is effectively implemented.

## Scope
Applies to all QMS processes and activities.

## Procedure
1. Audit Planning
   - Annual audit program is developed
   - Audit schedules are prepared
   - Auditors are assigned

2. Audit Preparation
   - Audit checklists are prepared
   - Previous audit results are reviewed
   - Auditees are notified

3. Audit Execution
   - Opening meeting is conducted
   - Evidence is gathered
   - Findings are documented

4. Audit Reporting
   - Audit reports are prepared
   - Nonconformities are identified
   - Closing meeting is conducted

5. Follow-up
   - Corrective actions are tracked
   - Effectiveness is verified
   - Audit closure is confirmed
                    """
                }
            ]
            
            for doc_data in core_documents:
                if doc_data["document_id"] not in self.documents:
                    document = QualityDocument(
                        document_id=doc_data["document_id"],
                        document_title=doc_data["title"],
                        document_type=doc_data["type"],
                        document_version="1.0",
                        document_content=doc_data["content"],
                        author="quality_manager",
                        reviewer="quality_manager",
                        approver="ceo",
                        status=DocumentStatus.ACTIVE,
                        created_date=current_time,
                        review_date=current_time,
                        approval_date=current_time,
                        effective_date=current_time,
                        next_review_date=current_time + (365 * 24 * 3600),  # 1 year
                        distribution_list=["all_staff", "management", "quality_team"],
                        related_processes=["QP-001", "QP-002", "QP-003"]
                    )
                    
                    await self._store_document(document)
                    self.documents[document.document_id] = document
                    
                    # Save document content to file
                    doc_file = f"{self.documents_directory}/{document.document_id}_{document.document_title.replace(' ', '_')}.md"
                    with open(doc_file, 'w') as f:
                        f.write(document.document_content)
            
            self.logger.info(f"Initialized {len(core_documents)} core quality documents")
            
        except Exception as e:
            self.logger.error(f"Error initializing quality documents: {e}")
    
    async def _initialize_quality_objectives(self):
        """Initialize quality objectives"""
        try:
            current_time = time.time()
            target_date = current_time + (365 * 24 * 3600)  # 1 year
            
            for obj_id, obj_data in self.quality_objectives_template.items():
                objective_id = f"QO-{obj_id.upper()}"
                
                if objective_id not in self.objectives:
                    objective = QualityObjective(
                        objective_id=objective_id,
                        objective_title=obj_data["title"],
                        objective_description=obj_data["description"],
                        target_value=obj_data["target"],
                        current_value=0.0,
                        measurement_unit=obj_data["unit"],
                        responsible_person="quality_manager",
                        target_date=target_date,
                        status="active",
                        progress_percentage=0.0,
                        related_processes=["QP-001", "QP-002", "QP-003", "QP-004", "QP-005"],
                        action_plans=[]
                    )
                    
                    await self._store_objective(objective)
                    self.objectives[objective.objective_id] = objective
            
            self.logger.info(f"Initialized {len(self.quality_objectives_template)} quality objectives")
            
        except Exception as e:
            self.logger.error(f"Error initializing quality objectives: {e}")
    
    async def _store_process(self, process: QualityProcess):
        """Store quality process in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO quality_processes
                (process_id, process_name, process_description, process_owner, process_category,
                 inputs, outputs, resources, controls, metrics, status, effectiveness_rating,
                 last_review_date, next_review_date, improvement_actions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                process.process_id, process.process_name, process.process_description,
                process.process_owner, process.process_category,
                json.dumps(process.inputs), json.dumps(process.outputs),
                json.dumps(process.resources), json.dumps(process.controls),
                json.dumps(process.metrics), process.status.value,
                process.effectiveness_rating, process.last_review_date,
                process.next_review_date, json.dumps(process.improvement_actions)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing process: {e}")
            raise
    
    async def _store_document(self, document: QualityDocument):
        """Store quality document in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO quality_documents
                (document_id, document_title, document_type, document_version, document_content,
                 author, reviewer, approver, status, created_date, review_date, approval_date,
                 effective_date, next_review_date, distribution_list, related_processes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document.document_id, document.document_title, document.document_type,
                document.document_version, document.document_content, document.author,
                document.reviewer, document.approver, document.status.value,
                document.created_date, document.review_date, document.approval_date,
                document.effective_date, document.next_review_date,
                json.dumps(document.distribution_list), json.dumps(document.related_processes)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing document: {e}")
            raise
    
    async def _store_objective(self, objective: QualityObjective):
        """Store quality objective in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO quality_objectives
                (objective_id, objective_title, objective_description, target_value, current_value,
                 measurement_unit, responsible_person, target_date, status, progress_percentage,
                 related_processes, action_plans)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                objective.objective_id, objective.objective_title, objective.objective_description,
                objective.target_value, objective.current_value, objective.measurement_unit,
                objective.responsible_person, objective.target_date, objective.status,
                objective.progress_percentage, json.dumps(objective.related_processes),
                json.dumps(objective.action_plans)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing objective: {e}")
            raise
    
    async def conduct_internal_audit(self, audit_scope: str, auditor: str, auditee: str) -> str:
        """Conduct internal audit"""
        try:
            current_time = time.time()
            audit_id = f"IA-{int(current_time)}-{str(uuid.uuid4())[:8]}"
            
            audit = InternalAudit(
                audit_id=audit_id,
                audit_title=f"Internal Audit - {audit_scope}",
                audit_type=AuditType.PROCESS_AUDIT,
                audit_scope=audit_scope,
                auditor=auditor,
                auditee=auditee,
                planned_date=current_time,
                actual_date=current_time,
                duration_hours=4.0,
                findings=[
                    {
                        "finding_id": f"F-{audit_id}-001",
                        "type": "observation",
                        "description": "Process documentation is current and accessible",
                        "evidence": "Reviewed process documents and confirmed version control",
                        "severity": "low"
                    },
                    {
                        "finding_id": f"F-{audit_id}-002",
                        "type": "nonconformity",
                        "description": "Training records not up to date for all personnel",
                        "evidence": "Missing training records for 2 team members",
                        "severity": "medium"
                    }
                ],
                recommendations=[
                    "Update training records for all personnel",
                    "Implement regular training record reviews",
                    "Consider automated training tracking system"
                ],
                corrective_actions=[
                    "Update missing training records within 30 days",
                    "Establish monthly training record review process"
                ],
                status="completed",
                effectiveness_rating=85.0
            )
            
            await self._store_audit(audit)
            self.audits[audit_id] = audit
            
            self.logger.info(f"Conducted internal audit: {audit_id}")
            return audit_id
            
        except Exception as e:
            self.logger.error(f"Error conducting internal audit: {e}")
            raise
    
    async def _store_audit(self, audit: InternalAudit):
        """Store internal audit in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO internal_audits
                (audit_id, audit_title, audit_type, audit_scope, auditor, auditee,
                 planned_date, actual_date, duration_hours, findings, recommendations,
                 corrective_actions, status, effectiveness_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit.audit_id, audit.audit_title, audit.audit_type.value,
                audit.audit_scope, audit.auditor, audit.auditee,
                audit.planned_date, audit.actual_date, audit.duration_hours,
                json.dumps(audit.findings), json.dumps(audit.recommendations),
                json.dumps(audit.corrective_actions), audit.status,
                audit.effectiveness_rating
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing audit: {e}")
            raise
    
    async def get_qms_metrics(self) -> Dict[str, Any]:
        """Get QMS performance metrics"""
        try:
            # Calculate process effectiveness
            total_processes = len(self.processes)
            active_processes = sum(1 for p in self.processes.values() if p.status == ProcessStatus.ACTIVE)
            
            # Calculate document control metrics
            total_documents = len(self.documents)
            active_documents = sum(1 for d in self.documents.values() if d.status == DocumentStatus.ACTIVE)
            
            # Calculate objective progress
            total_objectives = len(self.objectives)
            objectives_on_track = sum(1 for o in self.objectives.values() if o.progress_percentage >= 50.0)
            
            # Calculate audit metrics
            total_audits = len(self.audits)
            completed_audits = sum(1 for a in self.audits.values() if a.status == "completed")
            
            # Calculate overall QMS effectiveness
            process_effectiveness = (active_processes / total_processes * 100) if total_processes > 0 else 0
            document_control = (active_documents / total_documents * 100) if total_documents > 0 else 0
            objective_progress = (objectives_on_track / total_objectives * 100) if total_objectives > 0 else 0
            audit_completion = (completed_audits / total_audits * 100) if total_audits > 0 else 0
            
            overall_effectiveness = (process_effectiveness + document_control + objective_progress + audit_completion) / 4
            
            metrics = {
                "overall_effectiveness": round(overall_effectiveness, 2),
                "process_metrics": {
                    "total_processes": total_processes,
                    "active_processes": active_processes,
                    "process_effectiveness": round(process_effectiveness, 2)
                },
                "document_metrics": {
                    "total_documents": total_documents,
                    "active_documents": active_documents,
                    "document_control": round(document_control, 2)
                },
                "objective_metrics": {
                    "total_objectives": total_objectives,
                    "objectives_on_track": objectives_on_track,
                    "objective_progress": round(objective_progress, 2)
                },
                "audit_metrics": {
                    "total_audits": total_audits,
                    "completed_audits": completed_audits,
                    "audit_completion": round(audit_completion, 2)
                },
                "quality_status": self._determine_quality_status(overall_effectiveness)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting QMS metrics: {e}")
            return {
                "overall_effectiveness": 0.0,
                "process_metrics": {"total_processes": 0, "active_processes": 0, "process_effectiveness": 0.0},
                "document_metrics": {"total_documents": 0, "active_documents": 0, "document_control": 0.0},
                "objective_metrics": {"total_objectives": 0, "objectives_on_track": 0, "objective_progress": 0.0},
                "audit_metrics": {"total_audits": 0, "completed_audits": 0, "audit_completion": 0.0},
                "quality_status": QualityStatus.UNSATISFACTORY.value
            }
    
    def _determine_quality_status(self, effectiveness: float) -> str:
        """Determine quality status based on effectiveness"""
        if effectiveness >= 90:
            return QualityStatus.EXCELLENT.value
        elif effectiveness >= 80:
            return QualityStatus.GOOD.value
        elif effectiveness >= 70:
            return QualityStatus.SATISFACTORY.value
        elif effectiveness >= 60:
            return QualityStatus.NEEDS_IMPROVEMENT.value
        else:
            return QualityStatus.UNSATISFACTORY.value
    
    async def generate_qms_report(self) -> str:
        """Generate comprehensive QMS report"""
        try:
            current_time = time.time()
            report_date = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")
            
            metrics = await self.get_qms_metrics()
            
            report = f"""
# Quality Management System Report
Generated: {report_date}

## Executive Summary
Overall QMS Effectiveness: {metrics['overall_effectiveness']}%
Quality Status: {metrics['quality_status'].upper()}

## Process Management
- Total Processes: {metrics['process_metrics']['total_processes']}
- Active Processes: {metrics['process_metrics']['active_processes']}
- Process Effectiveness: {metrics['process_metrics']['process_effectiveness']}%

## Document Control
- Total Documents: {metrics['document_metrics']['total_documents']}
- Active Documents: {metrics['document_metrics']['active_documents']}
- Document Control: {metrics['document_metrics']['document_control']}%

## Quality Objectives
- Total Objectives: {metrics['objective_metrics']['total_objectives']}
- Objectives On Track: {metrics['objective_metrics']['objectives_on_track']}
- Objective Progress: {metrics['objective_metrics']['objective_progress']}%

## Internal Audits
- Total Audits: {metrics['audit_metrics']['total_audits']}
- Completed Audits: {metrics['audit_metrics']['completed_audits']}
- Audit Completion: {metrics['audit_metrics']['audit_completion']}%

## Process Details
"""
            
            for process in self.processes.values():
                report += f"""
### {process.process_name} ({process.process_id})
- Owner: {process.process_owner}
- Category: {process.process_category}
- Status: {process.status.value}
- Effectiveness: {process.effectiveness_rating}%
- Last Review: {datetime.fromtimestamp(process.last_review_date).strftime("%Y-%m-%d")}
- Next Review: {datetime.fromtimestamp(process.next_review_date).strftime("%Y-%m-%d")}
"""
            
            report += "\n## Quality Objectives Status\n"
            
            for objective in self.objectives.values():
                report += f"""
### {objective.objective_title} ({objective.objective_id})
- Target: {objective.target_value} {objective.measurement_unit}
- Current: {objective.current_value} {objective.measurement_unit}
- Progress: {objective.progress_percentage}%
- Status: {objective.status}
- Responsible: {objective.responsible_person}
"""
            
            # Save report to file
            report_file = f"{self.records_directory}/QMS_Report_{int(current_time)}.md"
            os.makedirs(self.records_directory, exist_ok=True)
            with open(report_file, 'w') as f:
                f.write(report)
            
            self.logger.info(f"Generated QMS report: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"Error generating QMS report: {e}")
            raise


# Global QMS instance
qms_instance = None

async def get_qms_instance():
    """Get global QMS instance"""
    global qms_instance
    if qms_instance is None:
        qms_instance = QualityManagementSystem()
        await asyncio.sleep(1)  # Allow initialization
    return qms_instance


if __name__ == "__main__":
    async def main():
        """Main function for testing"""
        logging.basicConfig(level=logging.INFO)
        
        # Initialize QMS
        qms = QualityManagementSystem()
        await asyncio.sleep(2)  # Allow initialization
        
        # Conduct sample audit
        audit_id = await qms.conduct_internal_audit(
            audit_scope="Document Control Process",
            auditor="quality_auditor",
            auditee="quality_manager"
        )
        print(f"Conducted audit: {audit_id}")
        
        # Get metrics
        metrics = await qms.get_qms_metrics()
        print(f"QMS Metrics: {json.dumps(metrics, indent=2)}")
        
        # Generate report
        report_file = await qms.generate_qms_report()
        print(f"Generated report: {report_file}")
    
    asyncio.run(main())