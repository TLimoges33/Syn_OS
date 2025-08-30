#!/usr/bin/env python3
"""
Security Governance Committee Framework
ISO 27001 compliant security governance implementation for Syn_OS
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


class GovernanceRole(Enum):
    """Security governance roles"""
    EXECUTIVE_SPONSOR = "executive_sponsor"
    COMMITTEE_CHAIR = "committee_chair"
    CISO = "ciso"
    SECURITY_ARCHITECT = "security_architect"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    TECHNICAL_LEAD = "technical_lead"
    BUSINESS_REPRESENTATIVE = "business_representative"
    LEGAL_COUNSEL = "legal_counsel"
    AUDIT_REPRESENTATIVE = "audit_representative"


class MeetingType(Enum):
    """Types of governance meetings"""
    MONTHLY_REVIEW = "monthly_review"
    QUARTERLY_ASSESSMENT = "quarterly_assessment"
    ANNUAL_PLANNING = "annual_planning"
    INCIDENT_REVIEW = "incident_review"
    EMERGENCY_SESSION = "emergency_session"
    COMPLIANCE_REVIEW = "compliance_review"
    RISK_ASSESSMENT = "risk_assessment"


class DecisionStatus(Enum):
    """Status of governance decisions"""
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    DEFERRED = "deferred"


@dataclass
class CommitteeMember:
    """Security governance committee member"""
    member_id: str
    name: str
    role: GovernanceRole
    department: str
    email: str
    phone: str
    responsibilities: List[str]
    authority_level: str
    backup_member: Optional[str]
    active: bool = True
    appointed_date: float = 0.0
    term_end_date: float = 0.0


@dataclass
class GovernanceMeeting:
    """Security governance meeting"""
    meeting_id: str
    meeting_type: MeetingType
    title: str
    date_time: float
    duration_minutes: int
    location: str
    chair: str
    attendees: List[str]
    agenda_items: List[str]
    decisions_made: List[str]
    action_items: List[Dict[str, Any]]
    next_meeting: float
    minutes_approved: bool = False
    recording_available: bool = False


@dataclass
class GovernanceDecision:
    """Security governance decision"""
    decision_id: str
    title: str
    description: str
    proposed_by: str
    meeting_id: str
    decision_date: float
    status: DecisionStatus
    rationale: str
    impact_assessment: str
    implementation_plan: str
    assigned_to: str
    due_date: float
    approval_votes: int
    rejection_votes: int
    abstentions: int
    implementation_status: str
    review_date: float


class SecurityGovernance:
    """
    Security Governance Committee Framework
    Implements ISO 27001 compliant security governance for Syn_OS
    """
    
    def __init__(self):
        """Initialize security governance framework"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.governance_directory = "/var/lib/synos/governance"
        self.database_file = f"{self.governance_directory}/governance.db"
        
        # Governance components
        self.committee_members: Dict[str, CommitteeMember] = {}
        self.meetings: Dict[str, GovernanceMeeting] = {}
        self.decisions: Dict[str, GovernanceDecision] = {}
        
        # Governance status
        self.committee_established = False
        self.charter_approved = False
        self.last_meeting = 0.0
        self.next_meeting = 0.0
        
        # Initialize system
        asyncio.create_task(self._initialize_governance())
    
    async def _initialize_governance(self):
        """Initialize security governance framework"""
        try:
            self.logger.info("Initializing security governance framework...")
            
            # Create governance directory
            os.makedirs(self.governance_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Establish committee
            await self._establish_committee()
            
            # Create governance charter
            await self._create_governance_charter()
            
            # Schedule initial meeting
            await self._schedule_initial_meeting()
            
            self.committee_established = True
            self.logger.info("Security governance framework initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing governance: {e}")
    
    async def _initialize_database(self):
        """Initialize governance database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Committee members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS committee_members (
                    member_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    department TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    responsibilities TEXT,
                    authority_level TEXT,
                    backup_member TEXT,
                    active BOOLEAN NOT NULL DEFAULT 1,
                    appointed_date REAL,
                    term_end_date REAL
                )
            ''')
            
            # Meetings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS governance_meetings (
                    meeting_id TEXT PRIMARY KEY,
                    meeting_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    date_time REAL NOT NULL,
                    duration_minutes INTEGER,
                    location TEXT,
                    chair TEXT NOT NULL,
                    attendees TEXT,
                    agenda_items TEXT,
                    decisions_made TEXT,
                    action_items TEXT,
                    next_meeting REAL,
                    minutes_approved BOOLEAN NOT NULL DEFAULT 0,
                    recording_available BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            
            # Decisions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS governance_decisions (
                    decision_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    proposed_by TEXT NOT NULL,
                    meeting_id TEXT,
                    decision_date REAL NOT NULL,
                    status TEXT NOT NULL,
                    rationale TEXT,
                    impact_assessment TEXT,
                    implementation_plan TEXT,
                    assigned_to TEXT,
                    due_date REAL,
                    approval_votes INTEGER DEFAULT 0,
                    rejection_votes INTEGER DEFAULT 0,
                    abstentions INTEGER DEFAULT 0,
                    implementation_status TEXT,
                    review_date REAL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_members_role ON committee_members (role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_type ON governance_meetings (meeting_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_decisions_status ON governance_decisions (status)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing governance database: {e}")
            raise
    
    async def _establish_committee(self):
        """Establish security governance committee"""
        try:
            current_time = time.time()
            term_end = current_time + (365 * 24 * 3600)  # 1 year term
            
            # Define committee members
            members = [
                CommitteeMember(
                    member_id="SGC-001",
                    name="Chief Executive Officer",
                    role=GovernanceRole.EXECUTIVE_SPONSOR,
                    department="Executive",
                    email="ceo@synos.org",
                    phone="+1-555-0001",
                    responsibilities=[
                        "Overall accountability for information security",
                        "Resource allocation and budget approval",
                        "Strategic direction and policy approval",
                        "Executive decision making authority"
                    ],
                    authority_level="Executive",
                    backup_member="SGC-002",
                    appointed_date=current_time,
                    term_end_date=term_end
                ),
                CommitteeMember(
                    member_id="SGC-002",
                    name="Interim Chief Information Security Officer",
                    role=GovernanceRole.CISO,
                    department="Security",
                    email="ciso@synos.org",
                    phone="+1-555-0002",
                    responsibilities=[
                        "ISMS implementation and maintenance",
                        "Security strategy development",
                        "Committee chair responsibilities",
                        "Security policy development and approval"
                    ],
                    authority_level="Senior Management",
                    backup_member="SGC-003",
                    appointed_date=current_time,
                    term_end_date=term_end
                ),
                CommitteeMember(
                    member_id="SGC-003",
                    name="Security Architect",
                    role=GovernanceRole.SECURITY_ARCHITECT,
                    department="Security",
                    email="security.architect@synos.org",
                    phone="+1-555-0003",
                    responsibilities=[
                        "Security architecture design and review",
                        "Technical security standards development",
                        "Security control implementation oversight",
                        "Technology risk assessment"
                    ],
                    authority_level="Management",
                    backup_member="SGC-004",
                    appointed_date=current_time,
                    term_end_date=term_end
                ),
                CommitteeMember(
                    member_id="SGC-004",
                    name="Risk Manager",
                    role=GovernanceRole.RISK_MANAGER,
                    department="Risk Management",
                    email="risk.manager@synos.org",
                    phone="+1-555-0004",
                    responsibilities=[
                        "Risk assessment coordination",
                        "Risk register maintenance",
                        "Risk treatment planning",
                        "Risk monitoring and reporting"
                    ],
                    authority_level="Management",
                    backup_member="SGC-005",
                    appointed_date=current_time,
                    term_end_date=term_end
                ),
                CommitteeMember(
                    member_id="SGC-005",
                    name="Compliance Officer",
                    role=GovernanceRole.COMPLIANCE_OFFICER,
                    department="Compliance",
                    email="compliance@synos.org",
                    phone="+1-555-0005",
                    responsibilities=[
                        "Regulatory compliance monitoring",
                        "Audit coordination and management",
                        "Compliance reporting and documentation",
                        "Legal requirement tracking"
                    ],
                    authority_level="Management",
                    backup_member="SGC-006",
                    appointed_date=current_time,
                    term_end_date=term_end
                ),
                CommitteeMember(
                    member_id="SGC-006",
                    name="Technical Lead",
                    role=GovernanceRole.TECHNICAL_LEAD,
                    department="Development",
                    email="tech.lead@synos.org",
                    phone="+1-555-0006",
                    responsibilities=[
                        "Technical implementation oversight",
                        "Development security standards",
                        "Code review and security testing",
                        "Technical risk assessment"
                    ],
                    authority_level="Management",
                    backup_member="SGC-007",
                    appointed_date=current_time,
                    term_end_date=term_end
                ),
                CommitteeMember(
                    member_id="SGC-007",
                    name="Business Representative",
                    role=GovernanceRole.BUSINESS_REPRESENTATIVE,
                    department="Business Operations",
                    email="business.rep@synos.org",
                    phone="+1-555-0007",
                    responsibilities=[
                        "Business impact assessment",
                        "User requirements representation",
                        "Business continuity planning",
                        "Stakeholder communication"
                    ],
                    authority_level="Management",
                    backup_member="SGC-008",
                    appointed_date=current_time,
                    term_end_date=term_end
                )
            ]
            
            # Store committee members
            for member in members:
                await self._store_member(member)
                self.committee_members[member.member_id] = member
            
            self.logger.info(f"Established security governance committee with {len(members)} members")
            
        except Exception as e:
            self.logger.error(f"Error establishing committee: {e}")
    
    async def _store_member(self, member: CommitteeMember):
        """Store committee member in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO committee_members
                (member_id, name, role, department, email, phone, responsibilities,
                 authority_level, backup_member, active, appointed_date, term_end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                member.member_id, member.name, member.role.value, member.department,
                member.email, member.phone, json.dumps(member.responsibilities),
                member.authority_level, member.backup_member, member.active,
                member.appointed_date, member.term_end_date
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing committee member: {e}")
    
    async def _create_governance_charter(self):
        """Create security governance charter"""
        try:
            charter = {
                "title": "Syn_OS Security Governance Committee Charter",
                "version": "1.0",
                "effective_date": time.time(),
                "approved_by": "Chief Executive Officer",
                "approval_date": time.time(),
                "purpose": "To provide strategic oversight and governance for information security within Syn_OS organization",
                "scope": "All information security matters affecting Syn_OS systems, data, and operations",
                "authority": {
                    "policy_approval": "Authority to approve information security policies and procedures",
                    "resource_allocation": "Authority to recommend security resource allocation",
                    "incident_oversight": "Authority to oversee major security incident response",
                    "compliance_monitoring": "Authority to monitor regulatory compliance status",
                    "risk_acceptance": "Authority to accept residual security risks"
                },
                "responsibilities": [
                    "Establish and maintain information security governance framework",
                    "Review and approve information security policies and procedures",
                    "Monitor information security risk management activities",
                    "Oversee compliance with regulatory and legal requirements",
                    "Review security incident reports and response effectiveness",
                    "Approve security investment and resource allocation recommendations",
                    "Conduct regular security posture assessments",
                    "Ensure security awareness and training programs are effective"
                ],
                "meeting_schedule": {
                    "regular_meetings": "Monthly on the first Tuesday of each month",
                    "quarterly_reviews": "Comprehensive quarterly security reviews",
                    "annual_planning": "Annual security strategy and planning session",
                    "emergency_meetings": "As needed for critical security incidents"
                },
                "reporting_structure": {
                    "reports_to": "Chief Executive Officer and Board of Directors",
                    "receives_reports_from": [
                        "Chief Information Security Officer",
                        "Security Operations Team",
                        "Risk Management Team",
                        "Compliance Team",
                        "Internal Audit"
                    ]
                },
                "decision_making": {
                    "quorum": "Majority of voting members (minimum 4 members)",
                    "voting_process": "Simple majority for policy decisions, unanimous for risk acceptance",
                    "escalation": "Unresolved issues escalated to CEO within 48 hours"
                },
                "performance_metrics": [
                    "Security incident response time and effectiveness",
                    "Compliance audit results and remediation status",
                    "Risk assessment completion and treatment status",
                    "Security awareness training completion rates",
                    "Security investment ROI and effectiveness"
                ],
                "review_schedule": "Annual charter review and update as needed"
            }
            
            # Save charter
            charter_file = f"{self.governance_directory}/governance_charter.json"
            with open(charter_file, 'w') as f:
                json.dump(charter, f, indent=2)
            
            self.charter_approved = True
            self.logger.info("Security governance charter created and approved")
            
        except Exception as e:
            self.logger.error(f"Error creating governance charter: {e}")
    
    async def _schedule_initial_meeting(self):
        """Schedule initial governance committee meeting"""
        try:
            current_time = time.time()
            meeting_time = current_time + (7 * 24 * 3600)  # Schedule for next week
            
            initial_meeting = GovernanceMeeting(
                meeting_id="SGM-001",
                meeting_type=MeetingType.MONTHLY_REVIEW,
                title="Security Governance Committee - Initial Meeting",
                date_time=meeting_time,
                duration_minutes=120,
                location="Executive Conference Room / Virtual",
                chair="SGC-002",  # Interim CISO
                attendees=list(self.committee_members.keys()),
                agenda_items=[
                    "Committee member introductions and role confirmation",
                    "Review and approval of governance charter",
                    "Current security posture assessment",
                    "Phase 1 critical security remediation status review",
                    "ISMS implementation progress review",
                    "Risk assessment methodology approval",
                    "Security policy framework review",
                    "Resource allocation and budget discussion",
                    "Meeting schedule and communication protocols",
                    "Action items and next steps"
                ],
                decisions_made=[],
                action_items=[
                    {
                        "item": "Complete ISMS scope definition review",
                        "assigned_to": "SGC-002",
                        "due_date": meeting_time + (3 * 24 * 3600),
                        "status": "pending"
                    },
                    {
                        "item": "Finalize risk assessment methodology",
                        "assigned_to": "SGC-004",
                        "due_date": meeting_time + (5 * 24 * 3600),
                        "status": "pending"
                    },
                    {
                        "item": "Establish 24/7 SOC operational procedures",
                        "assigned_to": "SGC-003",
                        "due_date": meeting_time + (7 * 24 * 3600),
                        "status": "pending"
                    }
                ],
                next_meeting=meeting_time + (30 * 24 * 3600)  # Next monthly meeting
            )
            
            await self._store_meeting(initial_meeting)
            self.meetings[initial_meeting.meeting_id] = initial_meeting
            self.next_meeting = meeting_time
            
            self.logger.info(f"Scheduled initial governance meeting for {datetime.fromtimestamp(meeting_time)}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling initial meeting: {e}")
    
    async def _store_meeting(self, meeting: GovernanceMeeting):
        """Store governance meeting in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO governance_meetings
                (meeting_id, meeting_type, title, date_time, duration_minutes,
                 location, chair, attendees, agenda_items, decisions_made,
                 action_items, next_meeting, minutes_approved, recording_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meeting.meeting_id, meeting.meeting_type.value, meeting.title,
                meeting.date_time, meeting.duration_minutes, meeting.location,
                meeting.chair, json.dumps(meeting.attendees),
                json.dumps(meeting.agenda_items), json.dumps(meeting.decisions_made),
                json.dumps(meeting.action_items), meeting.next_meeting,
                meeting.minutes_approved, meeting.recording_available
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing meeting: {e}")
    
    async def get_governance_status(self) -> Dict[str, Any]:
        """Get current governance status"""
        try:
            return {
                "committee_established": self.committee_established,
                "charter_approved": self.charter_approved,
                "total_members": len(self.committee_members),
                "active_members": sum(1 for m in self.committee_members.values() if m.active),
                "meetings_scheduled": len(self.meetings),
                "last_meeting": self.last_meeting,
                "next_meeting": self.next_meeting,
                "governance_directory": self.governance_directory,
                "database_file": self.database_file
            }
            
        except Exception as e:
            self.logger.error(f"Error getting governance status: {e}")
            return {"error": str(e)}
    
    async def get_committee_members(self) -> List[Dict[str, Any]]:
        """Get all committee members"""
        try:
            members = []
            for member in self.committee_members.values():
                member_dict = asdict(member)
                member_dict["role"] = member.role.value
                members.append(member_dict)
            
            return members
            
        except Exception as e:
            self.logger.error(f"Error getting committee members: {e}")
            return []
    
    async def get_scheduled_meetings(self) -> List[Dict[str, Any]]:
        """Get all scheduled meetings"""
        try:
            meetings = []
            for meeting in self.meetings.values():
                meeting_dict = asdict(meeting)
                meeting_dict["meeting_type"] = meeting.meeting_type.value
                meetings.append(meeting_dict)
            
            return meetings
            
        except Exception as e:
            self.logger.error(f"Error getting scheduled meetings: {e}")
            return []


# Global security governance instance
security_governance = SecurityGovernance()