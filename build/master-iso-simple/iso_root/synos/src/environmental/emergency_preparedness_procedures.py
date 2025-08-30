#!/usr/bin/env python3
"""
Emergency Preparedness Procedures
Comprehensive environmental emergency response and preparedness system
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


class EmergencyType(Enum):
    """Types of environmental emergencies"""
    CHEMICAL_SPILL = "chemical_spill"
    FIRE = "fire"
    FLOOD = "flood"
    POWER_OUTAGE = "power_outage"
    HVAC_FAILURE = "hvac_failure"
    WASTE_INCIDENT = "waste_incident"
    AIR_EMISSION_EXCEEDANCE = "air_emission_exceedance"
    WATER_DISCHARGE_VIOLATION = "water_discharge_violation"
    EQUIPMENT_FAILURE = "equipment_failure"
    NATURAL_DISASTER = "natural_disaster"
    CYBER_ATTACK = "cyber_attack"
    CONTAMINATION = "contamination"


class EmergencyLevel(Enum):
    """Emergency severity levels"""
    LEVEL_1_MINOR = "level_1_minor"  # Minor incident, local response
    LEVEL_2_MODERATE = "level_2_moderate"  # Moderate incident, facility response
    LEVEL_3_MAJOR = "level_3_major"  # Major incident, external assistance
    LEVEL_4_CATASTROPHIC = "level_4_catastrophic"  # Catastrophic, full evacuation


class ResponseStatus(Enum):
    """Emergency response status"""
    STANDBY = "standby"
    ACTIVATED = "activated"
    RESPONDING = "responding"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    UNDER_INVESTIGATION = "under_investigation"


@dataclass
class EmergencyProcedure:
    """Emergency response procedure definition"""
    procedure_id: str
    emergency_type: EmergencyType
    emergency_level: EmergencyLevel
    procedure_title: str
    procedure_description: str
    trigger_conditions: List[str]
    immediate_actions: List[str]
    response_team_roles: Dict[str, List[str]]
    equipment_required: List[str]
    communication_plan: Dict[str, str]
    evacuation_procedures: List[str]
    containment_procedures: List[str]
    cleanup_procedures: List[str]
    notification_requirements: List[str]
    regulatory_reporting: List[str]
    recovery_procedures: List[str]
    training_requirements: List[str]
    drill_frequency: str
    last_drill_date: float
    next_drill_date: float
    procedure_owner: str
    approval_date: float
    review_date: float
    version: str


@dataclass
class EmergencyIncident:
    """Emergency incident record"""
    incident_id: str
    incident_type: EmergencyType
    incident_level: EmergencyLevel
    incident_title: str
    incident_description: str
    incident_location: str
    incident_date: float
    discovery_time: float
    response_time: float
    containment_time: Optional[float]
    resolution_time: Optional[float]
    incident_commander: str
    response_team: List[str]
    affected_areas: List[str]
    environmental_impact: str
    health_safety_impact: str
    property_damage: str
    response_actions: List[str]
    lessons_learned: List[str]
    corrective_actions: List[str]
    status: ResponseStatus
    final_report: Optional[str]


@dataclass
class EmergencyResource:
    """Emergency response resource"""
    resource_id: str
    resource_name: str
    resource_type: str  # equipment, personnel, facility, external
    resource_description: str
    location: str
    availability_status: str  # available, in_use, maintenance, unavailable
    capacity: str
    contact_information: str
    maintenance_schedule: str
    last_inspection_date: float
    next_inspection_date: float
    training_required: List[str]
    applicable_emergencies: List[EmergencyType]


class EmergencyPreparednessSystem:
    """
    Emergency Preparedness Procedures System
    Comprehensive environmental emergency response management
    """
    
    def __init__(self):
        """Initialize emergency preparedness system"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.emergency_directory = "/var/lib/synos/environmental/emergency"
        self.database_file = f"{self.emergency_directory}/emergency.db"
        self.procedures_directory = f"{self.emergency_directory}/procedures"
        self.incidents_directory = f"{self.emergency_directory}/incidents"
        self.training_directory = f"{self.emergency_directory}/training"
        self.resources_directory = f"{self.emergency_directory}/resources"
        
        # System components
        self.emergency_procedures: Dict[str, EmergencyProcedure] = {}
        self.emergency_incidents: Dict[str, EmergencyIncident] = {}
        self.emergency_resources: Dict[str, EmergencyResource] = {}
        
        # Emergency response state
        self.active_incidents: List[str] = []
        self.response_teams: Dict[str, List[str]] = {}
        self.emergency_contacts: Dict[str, str] = {}
        
        # Initialize system
        asyncio.create_task(self._initialize_emergency_system())
    
    async def _initialize_emergency_system(self):
        """Initialize emergency preparedness system"""
        try:
            self.logger.info("Initializing Emergency Preparedness System...")
            
            # Create directories
            for directory in [self.emergency_directory, self.procedures_directory, 
                            self.incidents_directory, self.training_directory, self.resources_directory]:
                os.makedirs(directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_existing_data()
            
            # Initialize emergency procedures
            await self._initialize_emergency_procedures()
            
            # Initialize emergency resources
            await self._initialize_emergency_resources()
            
            # Initialize emergency contacts
            await self._initialize_emergency_contacts()
            
            # Start monitoring systems
            asyncio.create_task(self._start_emergency_monitoring())
            
            self.logger.info("Emergency Preparedness System initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing emergency system: {e}")
    
    async def _initialize_database(self):
        """Initialize emergency database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Emergency procedures table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_procedures (
                    procedure_id TEXT PRIMARY KEY,
                    emergency_type TEXT,
                    emergency_level TEXT,
                    procedure_title TEXT,
                    procedure_description TEXT,
                    trigger_conditions TEXT,
                    immediate_actions TEXT,
                    response_team_roles TEXT,
                    equipment_required TEXT,
                    communication_plan TEXT,
                    evacuation_procedures TEXT,
                    containment_procedures TEXT,
                    cleanup_procedures TEXT,
                    notification_requirements TEXT,
                    regulatory_reporting TEXT,
                    recovery_procedures TEXT,
                    training_requirements TEXT,
                    drill_frequency TEXT,
                    last_drill_date REAL,
                    next_drill_date REAL,
                    procedure_owner TEXT,
                    approval_date REAL,
                    review_date REAL,
                    version TEXT
                )
            ''')
            
            # Emergency incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_incidents (
                    incident_id TEXT PRIMARY KEY,
                    incident_type TEXT,
                    incident_level TEXT,
                    incident_title TEXT,
                    incident_description TEXT,
                    incident_location TEXT,
                    incident_date REAL,
                    discovery_time REAL,
                    response_time REAL,
                    containment_time REAL,
                    resolution_time REAL,
                    incident_commander TEXT,
                    response_team TEXT,
                    affected_areas TEXT,
                    environmental_impact TEXT,
                    health_safety_impact TEXT,
                    property_damage TEXT,
                    response_actions TEXT,
                    lessons_learned TEXT,
                    corrective_actions TEXT,
                    status TEXT,
                    final_report TEXT
                )
            ''')
            
            # Emergency resources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_resources (
                    resource_id TEXT PRIMARY KEY,
                    resource_name TEXT,
                    resource_type TEXT,
                    resource_description TEXT,
                    location TEXT,
                    availability_status TEXT,
                    capacity TEXT,
                    contact_information TEXT,
                    maintenance_schedule TEXT,
                    last_inspection_date REAL,
                    next_inspection_date REAL,
                    training_required TEXT,
                    applicable_emergencies TEXT
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_procedures_type ON emergency_procedures (emergency_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_procedures_level ON emergency_procedures (emergency_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_date ON emergency_incidents (incident_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_status ON emergency_incidents (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_type ON emergency_resources (resource_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_status ON emergency_resources (availability_status)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing emergency database: {e}")
            raise
    
    async def _load_existing_data(self):
        """Load existing emergency data"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load emergency procedures
            cursor.execute('SELECT * FROM emergency_procedures')
            for row in cursor.fetchall():
                procedure = EmergencyProcedure(
                    procedure_id=row[0],
                    emergency_type=EmergencyType(row[1]),
                    emergency_level=EmergencyLevel(row[2]),
                    procedure_title=row[3],
                    procedure_description=row[4],
                    trigger_conditions=json.loads(row[5]) if row[5] else [],
                    immediate_actions=json.loads(row[6]) if row[6] else [],
                    response_team_roles=json.loads(row[7]) if row[7] else {},
                    equipment_required=json.loads(row[8]) if row[8] else [],
                    communication_plan=json.loads(row[9]) if row[9] else {},
                    evacuation_procedures=json.loads(row[10]) if row[10] else [],
                    containment_procedures=json.loads(row[11]) if row[11] else [],
                    cleanup_procedures=json.loads(row[12]) if row[12] else [],
                    notification_requirements=json.loads(row[13]) if row[13] else [],
                    regulatory_reporting=json.loads(row[14]) if row[14] else [],
                    recovery_procedures=json.loads(row[15]) if row[15] else [],
                    training_requirements=json.loads(row[16]) if row[16] else [],
                    drill_frequency=row[17],
                    last_drill_date=row[18],
                    next_drill_date=row[19],
                    procedure_owner=row[20],
                    approval_date=row[21],
                    review_date=row[22],
                    version=row[23]
                )
                self.emergency_procedures[procedure.procedure_id] = procedure
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.emergency_procedures)} emergency procedures")
            
        except Exception as e:
            self.logger.error(f"Error loading existing emergency data: {e}")
    
    async def _initialize_emergency_procedures(self):
        """Initialize core emergency procedures"""
        try:
            current_time = time.time()
            
            core_procedures = [
                {
                    "procedure_id": "EP-CHEM-001",
                    "type": EmergencyType.CHEMICAL_SPILL,
                    "level": EmergencyLevel.LEVEL_2_MODERATE,
                    "title": "Chemical Spill Response",
                    "description": "Response procedures for chemical spills in facility areas",
                    "triggers": ["Visible chemical spill", "Chemical odor detected", "Spill alarm activation"],
                    "immediate_actions": [
                        "Ensure personal safety - evacuate if necessary",
                        "Alert emergency response team",
                        "Isolate the area and prevent access",
                        "Identify the chemical if safely possible",
                        "Stop the source if safely possible",
                        "Begin containment procedures"
                    ],
                    "team_roles": {
                        "Incident Commander": ["Overall response coordination", "External communication"],
                        "Safety Officer": ["Personnel safety", "PPE requirements"],
                        "Spill Response Team": ["Containment", "Cleanup", "Waste disposal"],
                        "Environmental Coordinator": ["Regulatory notification", "Impact assessment"]
                    },
                    "equipment": ["Spill kits", "PPE", "Absorbent materials", "Containment barriers"],
                    "communication": {
                        "Internal": "Emergency notification system",
                        "External": "Regulatory agencies as required",
                        "Emergency Services": "911 if life safety threat"
                    }
                },
                {
                    "procedure_id": "EP-FIRE-001",
                    "type": EmergencyType.FIRE,
                    "level": EmergencyLevel.LEVEL_3_MAJOR,
                    "title": "Fire Emergency Response",
                    "description": "Response procedures for fire emergencies",
                    "triggers": ["Fire alarm activation", "Visible fire or smoke", "Smell of burning"],
                    "immediate_actions": [
                        "Activate fire alarm if not already activated",
                        "Call 911 immediately",
                        "Evacuate the area following evacuation procedures",
                        "Account for all personnel at assembly points",
                        "Do not re-enter until cleared by fire department"
                    ],
                    "team_roles": {
                        "Incident Commander": ["Coordinate with fire department", "Media relations"],
                        "Evacuation Wardens": ["Assist with evacuation", "Personnel accountability"],
                        "Facilities Manager": ["Utility shutoffs", "Building systems"],
                        "Environmental Coordinator": ["Environmental impact assessment"]
                    },
                    "equipment": ["Fire extinguishers", "Emergency lighting", "Communication devices"],
                    "communication": {
                        "Emergency Services": "911",
                        "Internal": "PA system, emergency notification",
                        "External": "Regulatory agencies, insurance"
                    }
                },
                {
                    "procedure_id": "EP-FLOOD-001",
                    "type": EmergencyType.FLOOD,
                    "level": EmergencyLevel.LEVEL_2_MODERATE,
                    "title": "Flood Response Procedures",
                    "description": "Response procedures for flooding incidents",
                    "triggers": ["Water accumulation in facility", "Severe weather warnings", "Pipe burst"],
                    "immediate_actions": [
                        "Ensure electrical safety - shut off power if necessary",
                        "Evacuate affected areas",
                        "Stop water source if possible",
                        "Protect critical equipment and documents",
                        "Begin water removal and drying"
                    ],
                    "team_roles": {
                        "Incident Commander": ["Overall coordination", "Resource allocation"],
                        "Facilities Team": ["Water source control", "Equipment protection"],
                        "IT Team": ["Data center protection", "System backup"],
                        "Environmental Team": ["Water quality assessment", "Waste management"]
                    },
                    "equipment": ["Water pumps", "Dehumidifiers", "Plastic sheeting", "Sandbags"],
                    "communication": {
                        "Internal": "Emergency notification system",
                        "External": "Insurance, restoration contractors",
                        "Regulatory": "Environmental agencies if contamination"
                    }
                },
                {
                    "procedure_id": "EP-POWER-001",
                    "type": EmergencyType.POWER_OUTAGE,
                    "level": EmergencyLevel.LEVEL_1_MINOR,
                    "title": "Power Outage Response",
                    "description": "Response procedures for electrical power outages",
                    "triggers": ["Loss of electrical power", "UPS alarms", "Generator activation"],
                    "immediate_actions": [
                        "Verify outage scope and cause",
                        "Activate backup power systems",
                        "Secure critical systems and data",
                        "Implement manual procedures as needed",
                        "Monitor environmental conditions"
                    ],
                    "team_roles": {
                        "Facilities Manager": ["Power system assessment", "Generator operation"],
                        "IT Manager": ["System shutdown/startup", "Data protection"],
                        "Environmental Coordinator": ["HVAC monitoring", "Temperature control"],
                        "Security": ["Access control", "Facility security"]
                    },
                    "equipment": ["Backup generators", "UPS systems", "Flashlights", "Battery radios"],
                    "communication": {
                        "Utility Company": "Outage reporting and updates",
                        "Internal": "Battery-powered communication systems",
                        "Management": "Status updates and decisions"
                    }
                }
            ]
            
            for proc_data in core_procedures:
                if proc_data["procedure_id"] not in self.emergency_procedures:
                    procedure = EmergencyProcedure(
                        procedure_id=proc_data["procedure_id"],
                        emergency_type=proc_data["type"],
                        emergency_level=proc_data["level"],
                        procedure_title=proc_data["title"],
                        procedure_description=proc_data["description"],
                        trigger_conditions=proc_data["triggers"],
                        immediate_actions=proc_data["immediate_actions"],
                        response_team_roles=proc_data["team_roles"],
                        equipment_required=proc_data["equipment"],
                        communication_plan=proc_data["communication"],
                        evacuation_procedures=[
                            "Use nearest safe exit",
                            "Proceed to designated assembly area",
                            "Report to evacuation warden",
                            "Remain at assembly area until all clear"
                        ],
                        containment_procedures=[
                            "Isolate affected area",
                            "Prevent spread of contamination",
                            "Establish perimeter control",
                            "Monitor environmental conditions"
                        ],
                        cleanup_procedures=[
                            "Assess extent of contamination",
                            "Develop cleanup plan",
                            "Execute cleanup with proper PPE",
                            "Dispose of waste properly",
                            "Verify cleanup effectiveness"
                        ],
                        notification_requirements=[
                            "Internal management",
                            "Regulatory agencies (as required)",
                            "Emergency services (if applicable)",
                            "Insurance company"
                        ],
                        regulatory_reporting=[
                            "EPA notification (if required)",
                            "State environmental agency",
                            "Local emergency management",
                            "OSHA (if workplace injury)"
                        ],
                        recovery_procedures=[
                            "Damage assessment",
                            "Restoration planning",
                            "System restart procedures",
                            "Return to normal operations",
                            "Lessons learned review"
                        ],
                        training_requirements=[
                            "Annual emergency response training",
                            "Procedure-specific training",
                            "Equipment operation training",
                            "Regulatory requirements training"
                        ],
                        drill_frequency="Quarterly",
                        last_drill_date=current_time - (90 * 24 * 3600),  # 90 days ago
                        next_drill_date=current_time + (90 * 24 * 3600),  # 90 days from now
                        procedure_owner="emergency_coordinator",
                        approval_date=current_time,
                        review_date=current_time + (365 * 24 * 3600),  # 1 year
                        version="1.0"
                    )
                    
                    await self._store_emergency_procedure(procedure)
                    self.emergency_procedures[procedure.procedure_id] = procedure
            
            self.logger.info(f"Initialized {len(core_procedures)} emergency procedures")
            
        except Exception as e:
            self.logger.error(f"Error initializing emergency procedures: {e}")
    
    async def _initialize_emergency_resources(self):
        """Initialize emergency response resources"""
        try:
            current_time = time.time()
            
            core_resources = [
                {
                    "resource_id": "ER-SPILL-001",
                    "name": "Chemical Spill Response Kit",
                    "type": "equipment",
                    "description": "Complete chemical spill response and cleanup kit",
                    "location": "Emergency Storage Room A",
                    "capacity": "50 gallon spill capacity",
                    "contact": "facilities_manager@synos.com",
                    "applicable": [EmergencyType.CHEMICAL_SPILL, EmergencyType.CONTAMINATION]
                },
                {
                    "resource_id": "ER-FIRE-001",
                    "name": "Fire Suppression Equipment",
                    "type": "equipment",
                    "description": "Fire extinguishers and suppression systems",
                    "location": "Throughout facility",
                    "capacity": "Class A, B, C fire suppression",
                    "contact": "safety_officer@synos.com",
                    "applicable": [EmergencyType.FIRE]
                },
                {
                    "resource_id": "ER-TEAM-001",
                    "name": "Emergency Response Team",
                    "type": "personnel",
                    "description": "Trained emergency response personnel",
                    "location": "On-site during business hours",
                    "capacity": "8 trained responders",
                    "contact": "emergency_coordinator@synos.com",
                    "applicable": list(EmergencyType)
                },
                {
                    "resource_id": "ER-COMM-001",
                    "name": "Emergency Communication System",
                    "type": "equipment",
                    "description": "Battery-powered communication equipment",
                    "location": "Emergency Command Center",
                    "capacity": "72-hour battery backup",
                    "contact": "it_manager@synos.com",
                    "applicable": list(EmergencyType)
                }
            ]
            
            for res_data in core_resources:
                if res_data["resource_id"] not in self.emergency_resources:
                    resource = EmergencyResource(
                        resource_id=res_data["resource_id"],
                        resource_name=res_data["name"],
                        resource_type=res_data["type"],
                        resource_description=res_data["description"],
                        location=res_data["location"],
                        availability_status="available",
                        capacity=res_data["capacity"],
                        contact_information=res_data["contact"],
                        maintenance_schedule="Monthly inspection",
                        last_inspection_date=current_time - (30 * 24 * 3600),  # 30 days ago
                        next_inspection_date=current_time + (30 * 24 * 3600),  # 30 days from now
                        training_required=["Emergency response procedures", "Equipment operation"],
                        applicable_emergencies=res_data["applicable"]
                    )
                    
                    await self._store_emergency_resource(resource)
                    self.emergency_resources[resource.resource_id] = resource
            
            self.logger.info(f"Initialized {len(core_resources)} emergency resources")
            
        except Exception as e:
            self.logger.error(f"Error initializing emergency resources: {e}")
    
    async def _initialize_emergency_contacts(self):
        """Initialize emergency contact information"""
        try:
            self.emergency_contacts = {
                "Emergency Services": "911",
                "Fire Department": "911",
                "Police": "911",
                "Ambulance/EMS": "911",
                "Poison Control": "1-800-222-1222",
                "EPA National Response Center": "1-800-424-8802",
                "State Environmental Emergency": "1-800-424-8802",
                "Local Emergency Management": "555-0123",
                "Facility Emergency Coordinator": "555-0100",
                "Environmental Manager": "555-0101",
                "Safety Officer": "555-0102",
                "Facilities Manager": "555-0103",
                "IT Manager": "555-0104",
                "Security": "555-0105",
                "Management": "555-0106",
                "Insurance Company": "1-800-555-0107",
                "Legal Counsel": "555-0108",
                "Public Relations": "555-0109",
                "Utility Company": "1-800-555-0110"
            }
            
            self.logger.info("Initialized emergency contact information")
            
        except Exception as e:
            self.logger.error(f"Error initializing emergency contacts: {e}")
    
    async def _store_emergency_procedure(self, procedure: EmergencyProcedure):
        """Store emergency procedure in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO emergency_procedures
                (procedure_id, emergency_type, emergency_level, procedure_title,
                 procedure_description, trigger_conditions, immediate_actions,
                 response_team_roles, equipment_required, communication_plan,
                 evacuation_procedures, containment_procedures, cleanup_procedures,
                 notification_requirements, regulatory_reporting, recovery_procedures,
                 training_requirements, drill_frequency, last_drill_date, next_drill_date,
                 procedure_owner, approval_date, review_date, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                procedure.procedure_id, procedure.emergency_type.value,
                procedure.emergency_level.value, procedure.procedure_title,
                procedure.procedure_description, json.dumps(procedure.trigger_conditions),
                json.dumps(procedure.immediate_actions), json.dumps(procedure.response_team_roles),
                json.dumps(procedure.equipment_required), json.dumps(procedure.communication_plan),
                json.dumps(procedure.evacuation_procedures), json.dumps(procedure.containment_procedures),
                json.dumps(procedure.cleanup_procedures), json.dumps(procedure.notification_requirements),
                json.dumps(procedure.regulatory_reporting), json.dumps(procedure.recovery_procedures),
                json.dumps(procedure.training_requirements), procedure.drill_frequency,
                procedure.last_drill_date, procedure.next_drill_date, procedure.procedure_owner,
                procedure.approval_date, procedure.review_date, procedure.version
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing emergency procedure: {e}")
            raise
    
    async def _store_emergency_resource(self, resource: EmergencyResource):
        """Store emergency resource in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO emergency_resources
                (resource_id, resource_name, resource_type, resource_description,
                 location, availability_status, capacity, contact_information,
                 maintenance_schedule, last_inspection_date, next_inspection_date,
                 training_required, applicable_emergencies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resource.resource_id, resource.resource_name, resource.resource_type,
                resource.resource_description, resource.location, resource.availability_status,
                resource.capacity, resource.contact_information, resource.maintenance_schedule,
                resource.last_inspection_date, resource.next_inspection_date,
                json.dumps(resource.training_required),
                json.dumps([e.value for e in resource.applicable_emergencies])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing emergency resource: {e}")
            raise
    
    async def _start_emergency_monitoring(self):
        """Start emergency monitoring systems"""
        try:
            # Start drill schedule monitoring
            asyncio.create_task(self._monitor_drill_schedule())
            
            # Start resource inspection monitoring
            asyncio.create_task(self._monitor_resource_inspections())
            
            # Start procedure review monitoring
            asyncio.create_task(self._monitor_procedure_reviews())
            
        except Exception as e:
            self.logger.error(f"Error starting emergency monitoring: {e}")
    
    async def _monitor_drill_schedule(self):
        """Monitor emergency drill schedule"""
        try:
            while True:
                current_time = time.time()
                
                for procedure in self.emergency_procedures.values():
                    if procedure.next_drill_date <= current_time:
                        self.logger.info(f"Emergency drill due: {procedure.procedure_id}")
                        
                        # Schedule drill (in real implementation, this would trigger actual scheduling)
                        await self._schedule_emergency_drill(procedure.procedure_id)
                
                # Check daily
                await asyncio.sleep(86400)
                
        except Exception as e:
            self.logger.error(f"Error monitoring drill schedule: {e}")
    
    async def _monitor_resource_inspections(self):
        """Monitor emergency resource inspections"""
        try:
            while True:
                current_time = time.time()
                
                for resource in self.emergency_resources.values():
                    if resource.next_inspection_date <= current_time:
                        self.logger.info(f"Resource inspection due: {resource.resource_id}")
                        
                        # Schedule inspection
                        await self._schedule_resource_inspection(resource.resource_id)
                
                # Check daily
                await asyncio.sleep(86400)
                
        except Exception as e:
            self.logger.error(f"Error monitoring resource inspections: {e}")
    
    async def _monitor_procedure_reviews(self):
        """Monitor emergency procedure reviews"""
        try:
            while True:
                current_time = time.time()
                
                for procedure in self.emergency_procedures.values():
                    if procedure.review_date <= current_time:
                        self.logger.info(f"Procedure review due: {procedure.procedure_id}")
                        
                        # Schedule review
                        await self._schedule_procedure_review(procedure.procedure_id)
                
                # Check monthly
                await asyncio.sleep(30 * 24 * 3600)
                
        except Exception as e:
            self.logger.error(f"Error monitoring procedure reviews: {e}")
    
    async def _schedule_emergency_drill(self, procedure_id: str):
        """Schedule an emergency drill"""
        try:
            if procedure_id in self.emergency_procedures:
                procedure = self.emergency_procedures[procedure_id]
                
                # Update drill dates
                current_time = time.time()
                procedure.last_drill_date = current_time
                
                # Calculate next drill date based on frequency
                frequency_days = {
                    "Monthly": 30,
                    "Quarterly": 90,
                    "Semi-annually": 180,
                    "Annually": 365
                }
                
                days = frequency_days.get(procedure.drill_frequency, 90)
                procedure.next_drill_date = current_time + (days * 24 * 3600)
                
                await self._store_emergency_procedure(procedure)
                
                self.logger.info(f"Scheduled emergency drill for {procedure_id}")
                
        except Exception as e:
            self.logger.error(f"Error scheduling emergency drill: {e}")
    
    async def _schedule_resource_inspection(self, resource_id: str):
        """Schedule a resource inspection"""
        try:
            if resource_id in self.emergency_resources:
                resource = self.emergency_resources[resource_id]
                
                # Update inspection dates
                current_time = time.time()
                resource.last_inspection_date = current_time
                resource.next_inspection_date = current_time + (30 * 24 * 3600)  # 30 days
                
                await self._store_emergency_resource(resource)
                
                self.logger.info(f"Scheduled resource inspection for {resource_id}")
                
        except Exception as e:
            self.logger.error(f"Error scheduling resource inspection: {e}")
    
    async def _schedule_procedure_review(self, procedure_id: str):
        """Schedule a procedure review"""
        try:
            if procedure_id in self.emergency_procedures:
                procedure = self.emergency_procedures[procedure_id]
                
                # Update review date
                current_time = time.time()
                procedure.review_date = current_time + (365 * 24 * 3600)  # 1 year
                
                await self._store_emergency_procedure(procedure)
                
                self.logger.info(f"Scheduled procedure review for {procedure_id}")
                
        except Exception as e:
            self.logger.error(f"Error scheduling procedure review: {e}")
    
    async def activate_emergency_response(self, emergency_type: EmergencyType,
                                        emergency_level: EmergencyLevel,
                                        location: str, description: str) -> str:
        """Activate emergency response procedures"""
        try:
            current_time = time.time()
            incident_id = f"EI-{int(current_time)}-{str(uuid.uuid4())[:8]}"
            
            # Create incident record
            incident = EmergencyIncident(
                incident_id=incident_id,
                incident_type=emergency_type,
                incident_level=emergency_level,
                incident_title=f"{emergency_type.value.replace('_', ' ').title()} - {location}",
                incident_description=description,
                incident_location=location,
                incident_date=current_time,
                discovery_time=current_time,
                response_time=current_time,
                containment_time=None,
                resolution_time=None,
                incident_commander="emergency_coordinator",
                response_team=["emergency_response_team"],
                affected_areas=[location],
                environmental_impact="Under assessment",
                health_safety_impact="Under assessment",
                property_damage="Under assessment",
                response_actions=["Emergency response activated"],
                lessons_learned=[],
                corrective_actions=[],
                status=ResponseStatus.ACTIVATED,
                final_report=None
            )
            
            # Store incident
            await self._store_emergency_incident(incident)
            self.emergency_incidents[incident_id] = incident
            self.active_incidents.append(incident_id)
            
            # Find applicable procedures
            applicable_procedures = [
                proc for proc in self.emergency_procedures.values()
                if proc.emergency_type == emergency_type and proc.emergency_level == emergency_level
            ]
            
            if applicable_procedures:
                procedure = applicable_procedures[0]
                self.logger.info(f"Activated emergency procedure: {procedure.procedure_id}")
                
                # Log immediate actions
                for action in procedure.immediate_actions:
                    self.logger.info(f"Immediate action: {action}")
            
            self.logger.critical(f"EMERGENCY ACTIVATED: {incident_id} - {emergency_type.value} at {location}")
            
            return incident_id
            
        except Exception as e:
            self.logger.error(f"Error activating emergency response: {e}")
            raise
    
    async def _store_emergency_incident(self, incident: EmergencyIncident):
        """Store emergency incident in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO emergency_incidents
                (incident_id, incident_type, incident_level, incident_title,
                 incident_description, incident_location, incident_date, discovery_time,
                 response_time, containment_time, resolution_time, incident_commander,
                 response_team, affected_areas, environmental_impact, health_safety_impact,
                 property_damage, response_actions, lessons_learned, corrective_actions,
                 status, final_report)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident.incident_id, incident.incident_type.value, incident.incident_level.value,
                incident.incident_title, incident.incident_description, incident.incident_location,
                incident.incident_date, incident.discovery_time, incident.response_time,
                incident.containment_time, incident.resolution_time, incident.incident_commander,
                json.dumps(incident.response_team), json.dumps(incident.affected_areas),
                incident.environmental_impact, incident.health_safety_impact, incident.property_damage,
                json.dumps(incident.response_actions), json.dumps(incident.lessons_learned),
                json.dumps(incident.corrective_actions), incident.status.value, incident.final_report
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing emergency incident: {e}")
            raise
    
    async def get_emergency_summary(self) -> Dict[str, Any]:
        """Get emergency preparedness summary"""
        try:
            current_time = time.time()
            
            # Count procedures by type and level
            procedures_by_type = {}
            procedures_by_level = {}
            
            for procedure in self.emergency_procedures.values():
                proc_type = procedure.emergency_type.value
                proc_level = procedure.emergency_level.value
                
                if proc_type not in procedures_by_type:
                    procedures_by_type[proc_type] = 0
                procedures_by_type[proc_type] += 1
                
                if proc_level not in procedures_by_level:
                    procedures_by_level[proc_level] = 0
                procedures_by_level[proc_level] += 1
            
            # Count overdue drills and inspections
            overdue_drills = sum(1 for p in self.emergency_procedures.values()
                               if p.next_drill_date <= current_time)
            overdue_inspections = sum(1 for r in self.emergency_resources.values()
                                    if r.next_inspection_date <= current_time)
            
            # Count resources by type and status
            resources_by_type = {}
            resources_by_status = {}
            
            for resource in self.emergency_resources.values():
                res_type = resource.resource_type
                res_status = resource.availability_status
                
                if res_type not in resources_by_type:
                    resources_by_type[res_type] = 0
                resources_by_type[res_type] += 1
                
                if res_status not in resources_by_status:
                    resources_by_status[res_status] = 0
                resources_by_status[res_status] += 1
            
            # Recent incidents
            recent_incidents = sum(1 for i in self.emergency_incidents.values()
                                 if current_time - i.incident_date <= 86400 * 30)  # Last 30 days
            
            summary = {
                "emergency_procedures": {
                    "total_procedures": len(self.emergency_procedures),
                    "procedures_by_type": procedures_by_type,
                    "procedures_by_level": procedures_by_level,
                    "overdue_drills": overdue_drills
                },
                "emergency_resources": {
                    "total_resources": len(self.emergency_resources),
                    "resources_by_type": resources_by_type,
                    "resources_by_status": resources_by_status,
                    "overdue_inspections": overdue_inspections
                },
                "emergency_incidents": {
                    "total_incidents": len(self.emergency_incidents),
                    "active_incidents": len(self.active_incidents),
                    "recent_incidents": recent_incidents
                },
                "emergency_contacts": {
                    "total_contacts": len(self.emergency_contacts)
                },
                "system_health": {
                    "overall_status": "READY" if overdue_drills == 0 and overdue_inspections == 0 else "NEEDS_ATTENTION",
                    "critical_issues": overdue_drills + overdue_inspections,
                    "action_required": overdue_drills > 0 or overdue_inspections > 0
                },
                "timestamp": current_time
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting emergency summary: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "system_health": {"overall_status": "ERROR", "critical_issues": 0, "action_required": True}
            }


# Global emergency preparedness instance
emergency_preparedness_instance = None

async def get_emergency_preparedness_instance():
    """Get global emergency preparedness instance"""
    global emergency_preparedness_instance
    if emergency_preparedness_instance is None:
        emergency_preparedness_instance = EmergencyPreparednessSystem()
        await asyncio.sleep(1)  # Allow initialization
    return emergency_preparedness_instance


if __name__ == "__main__":
    async def main():
        """Main function for testing"""
        logging.basicConfig(level=logging.INFO)
        
        # Initialize emergency preparedness system
        system = EmergencyPreparednessSystem()
        await asyncio.sleep(3)  # Allow initialization
        
        # Get emergency summary
        print("Getting emergency preparedness summary...")
        summary = await system.get_emergency_summary()
        print(f"Emergency Summary: {json.dumps(summary, indent=2)}")
        
        # Test emergency activation
        print("Testing emergency activation...")
        incident_id = await system.activate_emergency_response(
            EmergencyType.CHEMICAL_SPILL,
            EmergencyLevel.LEVEL_2_MODERATE,
            "Data Center Room A",
            "Small chemical spill detected near server rack"
        )
        print(f"Emergency activated: {incident_id}")
    
    asyncio.run(main())