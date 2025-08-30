#!/usr/bin/env python3
"""
Document Control and Change Management System
ISO 9001 compliant document control and change management
"""

import asyncio
import logging
import os
import json
import time
import hashlib
import shutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class DocumentStatus(Enum):
    """Document status definitions"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class ChangeStatus(Enum):
    """Change request status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CLOSED = "closed"


class ChangePriority(Enum):
    """Change priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ControlledDocument:
    """Controlled document definition"""
    document_id: str
    document_title: str
    document_type: str
    document_category: str
    version: str
    file_path: str
    file_hash: str
    author: str
    reviewer: str
    approver: str
    status: DocumentStatus
    created_date: float
    modified_date: float
    review_date: float
    approval_date: float
    effective_date: float
    next_review_date: float
    retention_period: int  # months
    distribution_list: List[str]
    access_level: str
    keywords: List[str]
    related_documents: List[str]
    change_history: List[str]


@dataclass
class ChangeRequest:
    """Change request definition"""
    change_id: str
    change_title: str
    change_description: str
    change_justification: str
    change_type: str  # corrective, preventive, improvement
    priority: ChangePriority
    requestor: str
    affected_documents: List[str]
    affected_processes: List[str]
    impact_assessment: str
    risk_assessment: str
    implementation_plan: str
    testing_plan: str
    rollback_plan: str
    status: ChangeStatus
    submitted_date: float
    review_date: float
    approval_date: float
    implementation_date: float
    completion_date: float
    reviewer: str
    approver: str
    estimated_effort: float
    actual_effort: float
    cost_estimate: float
    actual_cost: float


@dataclass
class DocumentTemplate:
    """Document template definition"""
    template_id: str
    template_name: str
    template_category: str
    template_content: str
    required_sections: List[str]
    optional_sections: List[str]
    approval_workflow: List[str]
    retention_period: int
    review_frequency: int  # months


class DocumentControlSystem:
    """
    Document Control and Change Management System
    ISO 9001 compliant document and change management
    """
    
    def __init__(self):
        """Initialize document control system"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.system_directory = "/var/lib/synos/document_control"
        self.database_file = f"{self.system_directory}/document_control.db"
        self.documents_directory = f"{self.system_directory}/documents"
        self.templates_directory = f"{self.system_directory}/templates"
        self.archive_directory = f"{self.system_directory}/archive"
        self.backup_directory = f"{self.system_directory}/backup"
        
        # System components
        self.controlled_documents: Dict[str, ControlledDocument] = {}
        self.change_requests: Dict[str, ChangeRequest] = {}
        self.document_templates: Dict[str, DocumentTemplate] = {}
        
        # Version control settings
        self.version_format = "v{major}.{minor}.{patch}"
        self.backup_retention_days = 90
        
        # Initialize system
        asyncio.create_task(self._initialize_system())
    
    async def _initialize_system(self):
        """Initialize document control system"""
        try:
            self.logger.info("Initializing Document Control System...")
            
            # Create directories
            for directory in [self.system_directory, self.documents_directory, 
                            self.templates_directory, self.archive_directory, 
                            self.backup_directory]:
                os.makedirs(directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_existing_data()
            
            # Initialize templates
            await self._initialize_templates()
            
            # Schedule maintenance tasks
            asyncio.create_task(self._schedule_maintenance())
            
            self.logger.info("Document Control System initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing document control system: {e}")
    
    async def _initialize_database(self):
        """Initialize document control database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Controlled documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS controlled_documents (
                    document_id TEXT PRIMARY KEY,
                    document_title TEXT NOT NULL,
                    document_type TEXT,
                    document_category TEXT,
                    version TEXT,
                    file_path TEXT,
                    file_hash TEXT,
                    author TEXT,
                    reviewer TEXT,
                    approver TEXT,
                    status TEXT,
                    created_date REAL,
                    modified_date REAL,
                    review_date REAL,
                    approval_date REAL,
                    effective_date REAL,
                    next_review_date REAL,
                    retention_period INTEGER,
                    distribution_list TEXT,
                    access_level TEXT,
                    keywords TEXT,
                    related_documents TEXT,
                    change_history TEXT
                )
            ''')
            
            # Change requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS change_requests (
                    change_id TEXT PRIMARY KEY,
                    change_title TEXT NOT NULL,
                    change_description TEXT,
                    change_justification TEXT,
                    change_type TEXT,
                    priority TEXT,
                    requestor TEXT,
                    affected_documents TEXT,
                    affected_processes TEXT,
                    impact_assessment TEXT,
                    risk_assessment TEXT,
                    implementation_plan TEXT,
                    testing_plan TEXT,
                    rollback_plan TEXT,
                    status TEXT,
                    submitted_date REAL,
                    review_date REAL,
                    approval_date REAL,
                    implementation_date REAL,
                    completion_date REAL,
                    reviewer TEXT,
                    approver TEXT,
                    estimated_effort REAL,
                    actual_effort REAL,
                    cost_estimate REAL,
                    actual_cost REAL
                )
            ''')
            
            # Document templates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_templates (
                    template_id TEXT PRIMARY KEY,
                    template_name TEXT NOT NULL,
                    template_category TEXT,
                    template_content TEXT,
                    required_sections TEXT,
                    optional_sections TEXT,
                    approval_workflow TEXT,
                    retention_period INTEGER,
                    review_frequency INTEGER
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_status ON controlled_documents (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_type ON controlled_documents (document_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_changes_status ON change_requests (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_changes_priority ON change_requests (priority)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    async def _load_existing_data(self):
        """Load existing document control data"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load controlled documents
            cursor.execute('SELECT * FROM controlled_documents')
            for row in cursor.fetchall():
                document = ControlledDocument(
                    document_id=row[0],
                    document_title=row[1],
                    document_type=row[2],
                    document_category=row[3],
                    version=row[4],
                    file_path=row[5],
                    file_hash=row[6],
                    author=row[7],
                    reviewer=row[8],
                    approver=row[9],
                    status=DocumentStatus(row[10]),
                    created_date=row[11],
                    modified_date=row[12],
                    review_date=row[13],
                    approval_date=row[14],
                    effective_date=row[15],
                    next_review_date=row[16],
                    retention_period=row[17],
                    distribution_list=json.loads(row[18]) if row[18] else [],
                    access_level=row[19],
                    keywords=json.loads(row[20]) if row[20] else [],
                    related_documents=json.loads(row[21]) if row[21] else [],
                    change_history=json.loads(row[22]) if row[22] else []
                )
                self.controlled_documents[document.document_id] = document
            
            # Load change requests
            cursor.execute('SELECT * FROM change_requests')
            for row in cursor.fetchall():
                change = ChangeRequest(
                    change_id=row[0],
                    change_title=row[1],
                    change_description=row[2],
                    change_justification=row[3],
                    change_type=row[4],
                    priority=ChangePriority(row[5]),
                    requestor=row[6],
                    affected_documents=json.loads(row[7]) if row[7] else [],
                    affected_processes=json.loads(row[8]) if row[8] else [],
                    impact_assessment=row[9],
                    risk_assessment=row[10],
                    implementation_plan=row[11],
                    testing_plan=row[12],
                    rollback_plan=row[13],
                    status=ChangeStatus(row[14]),
                    submitted_date=row[15],
                    review_date=row[16],
                    approval_date=row[17],
                    implementation_date=row[18],
                    completion_date=row[19],
                    reviewer=row[20],
                    approver=row[21],
                    estimated_effort=row[22],
                    actual_effort=row[23],
                    cost_estimate=row[24],
                    actual_cost=row[25]
                )
                self.change_requests[change.change_id] = change
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.controlled_documents)} documents and {len(self.change_requests)} change requests")
            
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
    
    async def _initialize_templates(self):
        """Initialize document templates"""
        try:
            templates = {
                "procedure": DocumentTemplate(
                    template_id="TMPL-PROC-001",
                    template_name="Standard Operating Procedure",
                    template_category="procedure",
                    template_content="""# {title}

## 1. Purpose
{purpose}

## 2. Scope
{scope}

## 3. Responsibilities
{responsibilities}

## 4. Procedure
{procedure_steps}

## 5. Records
{records}

## 6. References
{references}

## 7. Revision History
{revision_history}
""",
                    required_sections=["Purpose", "Scope", "Responsibilities", "Procedure"],
                    optional_sections=["Records", "References", "Revision History"],
                    approval_workflow=["author", "reviewer", "approver"],
                    retention_period=60,  # 5 years
                    review_frequency=12   # annually
                ),
                "policy": DocumentTemplate(
                    template_id="TMPL-POL-001",
                    template_name="Policy Document",
                    template_category="policy",
                    template_content="""# {title}

## 1. Policy Statement
{policy_statement}

## 2. Scope and Application
{scope}

## 3. Definitions
{definitions}

## 4. Policy Details
{policy_details}

## 5. Responsibilities
{responsibilities}

## 6. Compliance and Monitoring
{compliance}

## 7. Related Documents
{related_documents}

## 8. Revision History
{revision_history}
""",
                    required_sections=["Policy Statement", "Scope and Application", "Policy Details"],
                    optional_sections=["Definitions", "Responsibilities", "Compliance and Monitoring"],
                    approval_workflow=["author", "reviewer", "senior_management"],
                    retention_period=84,  # 7 years
                    review_frequency=24   # bi-annually
                ),
                "work_instruction": DocumentTemplate(
                    template_id="TMPL-WI-001",
                    template_name="Work Instruction",
                    template_category="work_instruction",
                    template_content="""# {title}

## 1. Objective
{objective}

## 2. Prerequisites
{prerequisites}

## 3. Materials and Tools
{materials}

## 4. Step-by-Step Instructions
{instructions}

## 5. Quality Checks
{quality_checks}

## 6. Troubleshooting
{troubleshooting}

## 7. Safety Considerations
{safety}

## 8. Revision History
{revision_history}
""",
                    required_sections=["Objective", "Step-by-Step Instructions"],
                    optional_sections=["Prerequisites", "Materials and Tools", "Quality Checks"],
                    approval_workflow=["author", "supervisor"],
                    retention_period=36,  # 3 years
                    review_frequency=6    # semi-annually
                )
            }
            
            for template_id, template in templates.items():
                if template_id not in self.document_templates:
                    await self._store_template(template)
                    self.document_templates[template_id] = template
            
            self.logger.info(f"Initialized {len(templates)} document templates")
            
        except Exception as e:
            self.logger.error(f"Error initializing templates: {e}")
    
    async def create_document(self, title: str, document_type: str, content: str, 
                            author: str, template_id: Optional[str] = None) -> str:
        """Create a new controlled document"""
        try:
            current_time = time.time()
            document_id = f"DOC-{int(current_time)}-{hash(title) % 10000:04d}"
            
            # Generate file path
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            file_name = f"{document_id}_{safe_title.replace(' ', '_')}.md"
            file_path = os.path.join(self.documents_directory, file_name)
            
            # Calculate file hash
            file_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Create document
            document = ControlledDocument(
                document_id=document_id,
                document_title=title,
                document_type=document_type,
                document_category="general",
                version="v1.0.0",
                file_path=file_path,
                file_hash=file_hash,
                author=author,
                reviewer="",
                approver="",
                status=DocumentStatus.DRAFT,
                created_date=current_time,
                modified_date=current_time,
                review_date=0.0,
                approval_date=0.0,
                effective_date=0.0,
                next_review_date=current_time + (365 * 24 * 3600),  # 1 year
                retention_period=60,  # 5 years
                distribution_list=[],
                access_level="internal",
                keywords=[],
                related_documents=[],
                change_history=[]
            )
            
            # Write document content to file
            with open(file_path, 'w') as f:
                f.write(content)
            
            # Store in database
            await self._store_document(document)
            self.controlled_documents[document_id] = document
            
            self.logger.info(f"Created document: {document_id}")
            return document_id
            
        except Exception as e:
            self.logger.error(f"Error creating document: {e}")
            raise
    
    async def submit_change_request(self, title: str, description: str, 
                                  justification: str, change_type: str,
                                  priority: ChangePriority, requestor: str,
                                  affected_documents: List[str]) -> str:
        """Submit a change request"""
        try:
            current_time = time.time()
            change_id = f"CR-{int(current_time)}-{hash(title) % 10000:04d}"
            
            change_request = ChangeRequest(
                change_id=change_id,
                change_title=title,
                change_description=description,
                change_justification=justification,
                change_type=change_type,
                priority=priority,
                requestor=requestor,
                affected_documents=affected_documents,
                affected_processes=[],
                impact_assessment="",
                risk_assessment="",
                implementation_plan="",
                testing_plan="",
                rollback_plan="",
                status=ChangeStatus.SUBMITTED,
                submitted_date=current_time,
                review_date=0.0,
                approval_date=0.0,
                implementation_date=0.0,
                completion_date=0.0,
                reviewer="",
                approver="",
                estimated_effort=0.0,
                actual_effort=0.0,
                cost_estimate=0.0,
                actual_cost=0.0
            )
            
            # Store in database
            await self._store_change_request(change_request)
            self.change_requests[change_id] = change_request
            
            self.logger.info(f"Submitted change request: {change_id}")
            return change_id
            
        except Exception as e:
            self.logger.error(f"Error submitting change request: {e}")
            raise
    
    async def approve_change_request(self, change_id: str, approver: str, 
                                   implementation_plan: str) -> bool:
        """Approve a change request"""
        try:
            if change_id not in self.change_requests:
                raise ValueError(f"Change request {change_id} not found")
            
            change = self.change_requests[change_id]
            current_time = time.time()
            
            # Update change request
            change.status = ChangeStatus.APPROVED
            change.approver = approver
            change.approval_date = current_time
            change.implementation_plan = implementation_plan
            
            # Update in database
            await self._store_change_request(change)
            
            self.logger.info(f"Approved change request: {change_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error approving change request: {e}")
            return False
    
    async def implement_change(self, change_id: str) -> bool:
        """Implement an approved change"""
        try:
            if change_id not in self.change_requests:
                raise ValueError(f"Change request {change_id} not found")
            
            change = self.change_requests[change_id]
            
            if change.status != ChangeStatus.APPROVED:
                raise ValueError(f"Change request {change_id} is not approved")
            
            current_time = time.time()
            
            # Update affected documents
            for doc_id in change.affected_documents:
                if doc_id in self.controlled_documents:
                    document = self.controlled_documents[doc_id]
                    
                    # Create backup
                    await self._backup_document(document)
                    
                    # Update document version
                    version_parts = document.version.replace('v', '').split('.')
                    major, minor, patch = map(int, version_parts)
                    
                    if change.change_type == "corrective":
                        patch += 1
                    elif change.change_type == "improvement":
                        minor += 1
                        patch = 0
                    else:  # major change
                        major += 1
                        minor = 0
                        patch = 0
                    
                    document.version = f"v{major}.{minor}.{patch}"
                    document.modified_date = current_time
                    document.status = DocumentStatus.UNDER_REVIEW
                    document.change_history.append(change_id)
                    
                    await self._store_document(document)
            
            # Update change request
            change.status = ChangeStatus.IMPLEMENTED
            change.implementation_date = current_time
            
            await self._store_change_request(change)
            
            self.logger.info(f"Implemented change: {change_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error implementing change: {e}")
            return False
    
    async def _backup_document(self, document: ControlledDocument):
        """Create backup of document before changes"""
        try:
            if os.path.exists(document.file_path):
                backup_name = f"{document.document_id}_{document.version}_{int(time.time())}.md"
                backup_path = os.path.join(self.backup_directory, backup_name)
                shutil.copy2(document.file_path, backup_path)
                
                self.logger.debug(f"Created backup: {backup_path}")
                
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
    
    async def _store_document(self, document: ControlledDocument):
        """Store controlled document in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO controlled_documents
                (document_id, document_title, document_type, document_category, version,
                 file_path, file_hash, author, reviewer, approver, status, created_date,
                 modified_date, review_date, approval_date, effective_date, next_review_date,
                 retention_period, distribution_list, access_level, keywords, related_documents,
                 change_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document.document_id, document.document_title, document.document_type,
                document.document_category, document.version, document.file_path,
                document.file_hash, document.author, document.reviewer, document.approver,
                document.status.value, document.created_date, document.modified_date,
                document.review_date, document.approval_date, document.effective_date,
                document.next_review_date, document.retention_period,
                json.dumps(document.distribution_list), document.access_level,
                json.dumps(document.keywords), json.dumps(document.related_documents),
                json.dumps(document.change_history)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing document: {e}")
            raise
    
    async def _store_change_request(self, change: ChangeRequest):
        """Store change request in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO change_requests
                (change_id, change_title, change_description, change_justification, change_type,
                 priority, requestor, affected_documents, affected_processes, impact_assessment,
                 risk_assessment, implementation_plan, testing_plan, rollback_plan, status,
                 submitted_date, review_date, approval_date, implementation_date, completion_date,
                 reviewer, approver, estimated_effort, actual_effort, cost_estimate, actual_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                change.change_id, change.change_title, change.change_description,
                change.change_justification, change.change_type, change.priority.value,
                change.requestor, json.dumps(change.affected_documents),
                json.dumps(change.affected_processes), change.impact_assessment,
                change.risk_assessment, change.implementation_plan, change.testing_plan,
                change.rollback_plan, change.status.value, change.submitted_date,
                change.review_date, change.approval_date, change.implementation_date,
                change.completion_date, change.reviewer, change.approver,
                change.estimated_effort, change.actual_effort, change.cost_estimate,
                change.actual_cost
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing change request: {e}")
            raise
    
    async def _store_template(self, template: DocumentTemplate):
        """Store document template in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO document_templates
                (template_id, template_name, template_category, template_content,
                 required_sections, optional_sections, approval_workflow,
                 retention_period, review_frequency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template.template_id, template.template_name, template.template_category,
                template.template_content, json.dumps(template.required_sections),
                json.dumps(template.optional_sections), json.dumps(template.approval_workflow),
                template.retention_period, template.review_frequency
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing template: {e}")
            raise
    
    async def _schedule_maintenance(self):
        """Schedule maintenance tasks"""
        try:
            while True:
                # Run maintenance every 24 hours
                await asyncio.sleep(24 * 3600)
                
                # Clean up old backups
                await self._cleanup_backups()
                
                # Check for documents due for review
                await self._check_review_dates()
                
                # Archive obsolete documents
                await self._archive_obsolete_documents()
                
        except Exception as e:
            self.logger.error(f"Error in maintenance tasks: {e}")
    
    async def _cleanup_backups(self):
        """Clean up old backup files"""
        try:
            cutoff_time = time.time() - (self.backup_retention_days * 24 * 3600)
            
            for filename in os.listdir(self.backup_directory):
                file_path = os.path.join(self.backup_directory, filename)
                if os.path.getctime(file_path) < cutoff_time:
                    os.remove(file_path)
                    self.logger.debug(f"Removed old backup: {filename}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {e}")
    
    async def _check_review_dates(self):
        """Check for documents due for review"""
        try:
            current_time = time.time()
            
            for document in self.controlled_documents.values():
                if (document.status == DocumentStatus.ACTIVE and 
                    document.next_review_date <= current_time):
                    
                    self.logger.info(f"Document due for review: {document.document_id}")
                    # Could trigger notification system here
                    
        except Exception as e:
            self.logger.error(f"Error checking review dates: {e}")
    
    async def _archive_obsolete_documents(self):
        """Archive obsolete documents"""
        try:
            for document in self.controlled_documents.values():
                if document.status == DocumentStatus.OBSOLETE:
                    # Move to archive
                    archive_path = os.path.join(self.archive_directory, 
                                              os.path.basename(document.file_path))
                    
                    if os.path.exists(document.file_path):
                        shutil.move(document.file_path, archive_path)
                        document.file_path = archive_path
                        document.status = DocumentStatus.ARCHIVED
                        
                        await self._store_document(document)
                        self.logger.info(f"Archived document: {document.document_id}")
                        
        except Exception as e:
            self.logger.error(f"Error archiving documents: {e}")
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get document control system metrics"""
        try:
            # Document statistics
            total_documents = len(self.controlled_documents)
            active_documents = sum(1 for d in self.controlled_documents.values()
                                 if d.status == DocumentStatus.ACTIVE)
            draft_documents = sum(1 for d in self.controlled_documents.values()
                                if d.status == DocumentStatus.DRAFT)
            
            # Change request statistics
            total_changes = len(self.change_requests)
            pending_changes = sum(1 for c in self.change_requests.values()
                                if c.status in [ChangeStatus.SUBMITTED, ChangeStatus.UNDER_REVIEW])
            approved_changes = sum(1 for c in self.change_requests.values()
                                 if c.status == ChangeStatus.APPROVED)
            
            # Review statistics
            current_time = time.time()
            due_for_review = sum(1 for d in self.controlled_documents.values()
                               if d.next_review_date <= current_time and d.status == DocumentStatus.ACTIVE)
            
            metrics = {
                "document_statistics": {
                    "total_documents": total_documents,
                    "active_documents": active_documents,
                    "draft_documents": draft_documents,
                    "due_for_review": due_for_review
                },
                "change_statistics": {
                    "total_changes": total_changes,
                    "pending_changes": pending_changes,
                    "approved_changes": approved_changes
                },
                "system_health": {
                    "document_control_rate": (active_documents / total_documents * 100) if total_documents > 0 else 0,
                    "change_approval_rate": (approved_changes / total_changes * 100) if total_changes > 0 else 0,
                    "review_compliance": ((total_documents - due_for_review) / total_documents * 100) if total_documents > 0 else 0
                },
                "timestamp": time.time()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {
                "document_statistics": {"total_documents": 0, "active_documents": 0, "draft_documents": 0, "due_for_review": 0},
                "change_statistics": {"total_changes": 0, "pending_changes": 0, "approved_changes": 0},
                "system_health": {"document_control_rate": 0, "change_approval_rate": 0, "review_compliance": 0},
                "timestamp": time.time(),
                "error": str(e)
            }


# Global document control instance
document_control_instance = None

async def get_document_control_instance():
    """Get global document control instance"""
    global document_control_instance
    if document_control_instance is None:
        document_control_instance = DocumentControlSystem()
        await asyncio.sleep(1)  # Allow initialization
    return document_control_instance


if __name__ == "__main__":
    async def main():
        """Main function for testing"""
        logging.basicConfig(level=logging.INFO)
        
        # Initialize document control system
        doc_control = DocumentControlSystem()
        await asyncio.sleep(2)  # Allow initialization
        
        # Create sample document
        doc_id = await doc_control.create_document(
            title="Sample Quality Procedure",
            document_type="procedure",
            content="# Sample Quality Procedure\n\nThis is a sample procedure document.",
            author="quality_manager"
        )
        print(f"Created document: {doc_id}")
        
        # Submit change request
        change_id = await doc_control.submit_change_request(
            title="Update Sample Procedure",
            description="Update procedure to include new requirements",
            justification="Regulatory compliance requirement",
            change_type="improvement",
            priority=ChangePriority.MEDIUM,
            requestor="quality_manager",
            affected_documents=[doc_id]
        )
        print(f"Submitted change request: {change_id}")
        
        # Get metrics
        metrics = await doc_control.get_system_metrics()
        print(f"System metrics: {json.dumps(metrics, indent=2)}")
    
    asyncio.run(main())