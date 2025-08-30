#!/usr/bin/env python3
"""
Environmental Monitoring Program
Comprehensive environmental monitoring and measurement system
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
import random


class MonitoringFrequency(Enum):
    """Monitoring frequency options"""
    CONTINUOUS = "continuous"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class AlertLevel(Enum):
    """Environmental alert levels"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringStatus(Enum):
    """Monitoring point status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    CALIBRATION = "calibration"


@dataclass
class MonitoringPoint:
    """Environmental monitoring point definition"""
    point_id: str
    point_name: str
    location: str
    parameter_type: str
    measurement_unit: str
    monitoring_frequency: MonitoringFrequency
    legal_limit: Optional[float]
    internal_limit: Optional[float]
    warning_threshold: Optional[float]
    critical_threshold: Optional[float]
    monitoring_method: str
    equipment_id: str
    responsible_person: str
    status: MonitoringStatus
    last_calibration: float
    next_calibration: float
    installation_date: float
    related_aspects: List[str]


@dataclass
class MonitoringData:
    """Environmental monitoring measurement"""
    measurement_id: str
    point_id: str
    measurement_value: float
    measurement_unit: str
    measurement_timestamp: float
    measurement_method: str
    operator: str
    equipment_id: str
    quality_flag: str  # valid, invalid, suspect
    alert_level: AlertLevel
    comments: str
    weather_conditions: Optional[str]
    calibration_status: str


@dataclass
class EnvironmentalAlert:
    """Environmental alert/alarm"""
    alert_id: str
    point_id: str
    alert_type: str
    alert_level: AlertLevel
    trigger_value: float
    threshold_value: float
    alert_timestamp: float
    alert_message: str
    response_actions: List[str]
    responsible_persons: List[str]
    acknowledgment_status: str
    resolution_timestamp: Optional[float]
    resolution_actions: List[str]


class EnvironmentalMonitoringProgram:
    """
    Environmental Monitoring Program
    Comprehensive monitoring and measurement system
    """
    
    def __init__(self):
        """Initialize environmental monitoring program"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.monitoring_directory = "/var/lib/synos/environmental/monitoring"
        self.database_file = f"{self.monitoring_directory}/monitoring.db"
        self.data_directory = f"{self.monitoring_directory}/data"
        self.alerts_directory = f"{self.monitoring_directory}/alerts"
        self.reports_directory = f"{self.monitoring_directory}/reports"
        
        # System components
        self.monitoring_points: Dict[str, MonitoringPoint] = {}
        self.monitoring_data: Dict[str, List[MonitoringData]] = {}
        self.environmental_alerts: Dict[str, EnvironmentalAlert] = {}
        
        # Monitoring parameters
        self.monitoring_parameters = {
            "energy_consumption": {
                "unit": "kWh",
                "legal_limit": None,
                "internal_limit": 10000.0,
                "warning_threshold": 8000.0,
                "critical_threshold": 9500.0
            },
            "water_consumption": {
                "unit": "liters",
                "legal_limit": None,
                "internal_limit": 5000.0,
                "warning_threshold": 4000.0,
                "critical_threshold": 4800.0
            },
            "waste_generation": {
                "unit": "kg",
                "legal_limit": None,
                "internal_limit": 100.0,
                "warning_threshold": 80.0,
                "critical_threshold": 95.0
            },
            "carbon_emissions": {
                "unit": "kg_CO2e",
                "legal_limit": None,
                "internal_limit": 1000.0,
                "warning_threshold": 800.0,
                "critical_threshold": 950.0
            },
            "temperature": {
                "unit": "celsius",
                "legal_limit": None,
                "internal_limit": 25.0,
                "warning_threshold": 23.0,
                "critical_threshold": 27.0
            },
            "humidity": {
                "unit": "percentage",
                "legal_limit": None,
                "internal_limit": 60.0,
                "warning_threshold": 55.0,
                "critical_threshold": 65.0
            }
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_monitoring())
    
    async def _initialize_monitoring(self):
        """Initialize monitoring program"""
        try:
            self.logger.info("Initializing Environmental Monitoring Program...")
            
            # Create directories
            for directory in [self.monitoring_directory, self.data_directory, 
                            self.alerts_directory, self.reports_directory]:
                os.makedirs(directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_existing_data()
            
            # Initialize monitoring points
            await self._initialize_monitoring_points()
            
            # Start monitoring tasks
            asyncio.create_task(self._start_monitoring_tasks())
            
            self.logger.info("Environmental Monitoring Program initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing monitoring program: {e}")
    
    async def _initialize_database(self):
        """Initialize monitoring database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Monitoring points table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_points (
                    point_id TEXT PRIMARY KEY,
                    point_name TEXT NOT NULL,
                    location TEXT,
                    parameter_type TEXT,
                    measurement_unit TEXT,
                    monitoring_frequency TEXT,
                    legal_limit REAL,
                    internal_limit REAL,
                    warning_threshold REAL,
                    critical_threshold REAL,
                    monitoring_method TEXT,
                    equipment_id TEXT,
                    responsible_person TEXT,
                    status TEXT,
                    last_calibration REAL,
                    next_calibration REAL,
                    installation_date REAL,
                    related_aspects TEXT
                )
            ''')
            
            # Monitoring data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_data (
                    measurement_id TEXT PRIMARY KEY,
                    point_id TEXT,
                    measurement_value REAL,
                    measurement_unit TEXT,
                    measurement_timestamp REAL,
                    measurement_method TEXT,
                    operator TEXT,
                    equipment_id TEXT,
                    quality_flag TEXT,
                    alert_level TEXT,
                    comments TEXT,
                    weather_conditions TEXT,
                    calibration_status TEXT,
                    FOREIGN KEY (point_id) REFERENCES monitoring_points (point_id)
                )
            ''')
            
            # Environmental alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_alerts (
                    alert_id TEXT PRIMARY KEY,
                    point_id TEXT,
                    alert_type TEXT,
                    alert_level TEXT,
                    trigger_value REAL,
                    threshold_value REAL,
                    alert_timestamp REAL,
                    alert_message TEXT,
                    response_actions TEXT,
                    responsible_persons TEXT,
                    acknowledgment_status TEXT,
                    resolution_timestamp REAL,
                    resolution_actions TEXT,
                    FOREIGN KEY (point_id) REFERENCES monitoring_points (point_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_monitoring_timestamp ON monitoring_data (measurement_timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_level ON environmental_alerts (alert_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_points_status ON monitoring_points (status)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing monitoring database: {e}")
            raise
    
    async def _load_existing_data(self):
        """Load existing monitoring data"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load monitoring points
            cursor.execute('SELECT * FROM monitoring_points')
            for row in cursor.fetchall():
                point = MonitoringPoint(
                    point_id=row[0],
                    point_name=row[1],
                    location=row[2],
                    parameter_type=row[3],
                    measurement_unit=row[4],
                    monitoring_frequency=MonitoringFrequency(row[5]),
                    legal_limit=row[6],
                    internal_limit=row[7],
                    warning_threshold=row[8],
                    critical_threshold=row[9],
                    monitoring_method=row[10],
                    equipment_id=row[11],
                    responsible_person=row[12],
                    status=MonitoringStatus(row[13]),
                    last_calibration=row[14],
                    next_calibration=row[15],
                    installation_date=row[16],
                    related_aspects=json.loads(row[17]) if row[17] else []
                )
                self.monitoring_points[point.point_id] = point
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.monitoring_points)} monitoring points")
            
        except Exception as e:
            self.logger.error(f"Error loading existing monitoring data: {e}")
    
    async def _initialize_monitoring_points(self):
        """Initialize core monitoring points"""
        try:
            current_time = time.time()
            
            monitoring_points_config = [
                {
                    "point_id": "MP-001",
                    "name": "Data Center Energy Consumption",
                    "location": "Main Data Center",
                    "parameter": "energy_consumption",
                    "frequency": MonitoringFrequency.HOURLY,
                    "method": "Smart meter reading",
                    "equipment": "EQ-METER-001",
                    "aspects": ["EA-001"]
                },
                {
                    "point_id": "MP-002",
                    "name": "Office Energy Consumption",
                    "location": "Office Building",
                    "parameter": "energy_consumption",
                    "frequency": MonitoringFrequency.DAILY,
                    "method": "Utility meter reading",
                    "equipment": "EQ-METER-002",
                    "aspects": ["EA-001"]
                },
                {
                    "point_id": "MP-003",
                    "name": "Water Consumption",
                    "location": "Facility Wide",
                    "parameter": "water_consumption",
                    "frequency": MonitoringFrequency.DAILY,
                    "method": "Water meter reading",
                    "equipment": "EQ-WATER-001",
                    "aspects": ["EA-006"]
                },
                {
                    "point_id": "MP-004",
                    "name": "Electronic Waste Generation",
                    "location": "Waste Collection Point",
                    "parameter": "waste_generation",
                    "frequency": MonitoringFrequency.WEEKLY,
                    "method": "Weight measurement",
                    "equipment": "EQ-SCALE-001",
                    "aspects": ["EA-002"]
                },
                {
                    "point_id": "MP-005",
                    "name": "Carbon Emissions Calculation",
                    "location": "Virtual - Calculation",
                    "parameter": "carbon_emissions",
                    "frequency": MonitoringFrequency.MONTHLY,
                    "method": "Calculation based on energy consumption",
                    "equipment": "EQ-CALC-001",
                    "aspects": ["EA-001", "EA-005"]
                },
                {
                    "point_id": "MP-006",
                    "name": "Data Center Temperature",
                    "location": "Data Center Server Room",
                    "parameter": "temperature",
                    "frequency": MonitoringFrequency.CONTINUOUS,
                    "method": "Temperature sensor",
                    "equipment": "EQ-TEMP-001",
                    "aspects": ["EA-003"]
                }
            ]
            
            for point_config in monitoring_points_config:
                if point_config["point_id"] not in self.monitoring_points:
                    param_config = self.monitoring_parameters[point_config["parameter"]]
                    
                    point = MonitoringPoint(
                        point_id=point_config["point_id"],
                        point_name=point_config["name"],
                        location=point_config["location"],
                        parameter_type=point_config["parameter"],
                        measurement_unit=param_config["unit"],
                        monitoring_frequency=point_config["frequency"],
                        legal_limit=param_config["legal_limit"],
                        internal_limit=param_config["internal_limit"],
                        warning_threshold=param_config["warning_threshold"],
                        critical_threshold=param_config["critical_threshold"],
                        monitoring_method=point_config["method"],
                        equipment_id=point_config["equipment"],
                        responsible_person="environmental_technician",
                        status=MonitoringStatus.ACTIVE,
                        last_calibration=current_time,
                        next_calibration=current_time + (90 * 24 * 3600),  # 90 days
                        installation_date=current_time,
                        related_aspects=point_config["aspects"]
                    )
                    
                    await self._store_monitoring_point(point)
                    self.monitoring_points[point.point_id] = point
            
            self.logger.info(f"Initialized {len(monitoring_points_config)} monitoring points")
            
        except Exception as e:
            self.logger.error(f"Error initializing monitoring points: {e}")
    
    async def _store_monitoring_point(self, point: MonitoringPoint):
        """Store monitoring point in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO monitoring_points
                (point_id, point_name, location, parameter_type, measurement_unit,
                 monitoring_frequency, legal_limit, internal_limit, warning_threshold,
                 critical_threshold, monitoring_method, equipment_id, responsible_person,
                 status, last_calibration, next_calibration, installation_date, related_aspects)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                point.point_id, point.point_name, point.location, point.parameter_type,
                point.measurement_unit, point.monitoring_frequency.value, point.legal_limit,
                point.internal_limit, point.warning_threshold, point.critical_threshold,
                point.monitoring_method, point.equipment_id, point.responsible_person,
                point.status.value, point.last_calibration, point.next_calibration,
                point.installation_date, json.dumps(point.related_aspects)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing monitoring point: {e}")
            raise
    
    async def _start_monitoring_tasks(self):
        """Start monitoring tasks"""
        try:
            # Start continuous monitoring
            asyncio.create_task(self._continuous_monitoring())
            
            # Start periodic data collection
            asyncio.create_task(self._periodic_data_collection())
            
            # Start alert monitoring
            asyncio.create_task(self._alert_monitoring())
            
            # Start calibration monitoring
            asyncio.create_task(self._calibration_monitoring())
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring tasks: {e}")
    
    async def _continuous_monitoring(self):
        """Continuous monitoring for real-time parameters"""
        try:
            while True:
                current_time = time.time()
                
                # Monitor continuous parameters
                for point in self.monitoring_points.values():
                    if (point.monitoring_frequency == MonitoringFrequency.CONTINUOUS and 
                        point.status == MonitoringStatus.ACTIVE):
                        
                        # Simulate measurement (in real implementation, this would read from actual sensors)
                        measurement_value = await self._simulate_measurement(point)
                        
                        # Create monitoring data
                        measurement = MonitoringData(
                            measurement_id=f"M-{int(current_time)}-{str(uuid.uuid4())[:8]}",
                            point_id=point.point_id,
                            measurement_value=measurement_value,
                            measurement_unit=point.measurement_unit,
                            measurement_timestamp=current_time,
                            measurement_method=point.monitoring_method,
                            operator="automated_system",
                            equipment_id=point.equipment_id,
                            quality_flag="valid",
                            alert_level=self._determine_alert_level(measurement_value, point),
                            comments="Automated continuous monitoring",
                            weather_conditions=None,
                            calibration_status="in_calibration"
                        )
                        
                        # Store measurement
                        await self._store_measurement(measurement)
                        
                        # Check for alerts
                        if measurement.alert_level != AlertLevel.NORMAL:
                            await self._generate_alert(point, measurement)
                
                # Wait 5 minutes before next continuous monitoring cycle
                await asyncio.sleep(300)
                
        except Exception as e:
            self.logger.error(f"Error in continuous monitoring: {e}")
    
    async def _periodic_data_collection(self):
        """Periodic data collection for scheduled monitoring"""
        try:
            while True:
                current_time = time.time()
                
                # Check each monitoring point for scheduled collection
                for point in self.monitoring_points.values():
                    if (point.status == MonitoringStatus.ACTIVE and 
                        point.monitoring_frequency != MonitoringFrequency.CONTINUOUS):
                        
                        # Check if it's time for measurement based on frequency
                        if await self._is_measurement_due(point, current_time):
                            measurement_value = await self._simulate_measurement(point)
                            
                            measurement = MonitoringData(
                                measurement_id=f"M-{int(current_time)}-{str(uuid.uuid4())[:8]}",
                                point_id=point.point_id,
                                measurement_value=measurement_value,
                                measurement_unit=point.measurement_unit,
                                measurement_timestamp=current_time,
                                measurement_method=point.monitoring_method,
                                operator="environmental_technician",
                                equipment_id=point.equipment_id,
                                quality_flag="valid",
                                alert_level=self._determine_alert_level(measurement_value, point),
                                comments=f"Scheduled {point.monitoring_frequency.value} monitoring",
                                weather_conditions="normal",
                                calibration_status="in_calibration"
                            )
                            
                            await self._store_measurement(measurement)
                            
                            if measurement.alert_level != AlertLevel.NORMAL:
                                await self._generate_alert(point, measurement)
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
        except Exception as e:
            self.logger.error(f"Error in periodic data collection: {e}")
    
    async def _simulate_measurement(self, point: MonitoringPoint) -> float:
        """Simulate measurement value (replace with actual sensor reading)"""
        try:
            # Generate realistic simulated values based on parameter type
            base_values = {
                "energy_consumption": 5000.0,
                "water_consumption": 2000.0,
                "waste_generation": 50.0,
                "carbon_emissions": 500.0,
                "temperature": 22.0,
                "humidity": 45.0
            }
            
            base_value = base_values.get(point.parameter_type, 100.0)
            
            # Add some random variation (±20%)
            variation = random.uniform(-0.2, 0.2)
            simulated_value = base_value * (1 + variation)
            
            # Occasionally simulate threshold exceedances for testing
            if random.random() < 0.05:  # 5% chance
                if point.warning_threshold:
                    simulated_value = point.warning_threshold * 1.1
            
            return round(simulated_value, 2)
            
        except Exception as e:
            self.logger.error(f"Error simulating measurement: {e}")
            return 0.0
    
    def _determine_alert_level(self, value: float, point: MonitoringPoint) -> AlertLevel:
        """Determine alert level based on measurement value and thresholds"""
        try:
            if point.critical_threshold and value >= point.critical_threshold:
                return AlertLevel.CRITICAL
            elif point.warning_threshold and value >= point.warning_threshold:
                return AlertLevel.WARNING
            else:
                return AlertLevel.NORMAL
                
        except Exception as e:
            self.logger.error(f"Error determining alert level: {e}")
            return AlertLevel.NORMAL
    
    async def _is_measurement_due(self, point: MonitoringPoint, current_time: float) -> bool:
        """Check if measurement is due based on frequency"""
        try:
            # Get last measurement time for this point
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT MAX(measurement_timestamp) FROM monitoring_data 
                WHERE point_id = ?
            ''', (point.point_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            last_measurement = result[0] if result[0] else 0
            
            # Calculate time since last measurement
            time_since_last = current_time - last_measurement
            
            # Determine if measurement is due based on frequency
            frequency_intervals = {
                MonitoringFrequency.HOURLY: 3600,
                MonitoringFrequency.DAILY: 86400,
                MonitoringFrequency.WEEKLY: 604800,
                MonitoringFrequency.MONTHLY: 2592000,
                MonitoringFrequency.QUARTERLY: 7776000,
                MonitoringFrequency.ANNUALLY: 31536000
            }
            
            required_interval = frequency_intervals.get(point.monitoring_frequency, 86400)
            return time_since_last >= required_interval
            
        except Exception as e:
            self.logger.error(f"Error checking measurement due: {e}")
            return False
    
    async def _store_measurement(self, measurement: MonitoringData):
        """Store measurement in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO monitoring_data
                (measurement_id, point_id, measurement_value, measurement_unit,
                 measurement_timestamp, measurement_method, operator, equipment_id,
                 quality_flag, alert_level, comments, weather_conditions, calibration_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                measurement.measurement_id, measurement.point_id, measurement.measurement_value,
                measurement.measurement_unit, measurement.measurement_timestamp,
                measurement.measurement_method, measurement.operator, measurement.equipment_id,
                measurement.quality_flag, measurement.alert_level.value, measurement.comments,
                measurement.weather_conditions, measurement.calibration_status
            ))
            
            conn.commit()
            conn.close()
            
            # Store in memory for quick access
            if measurement.point_id not in self.monitoring_data:
                self.monitoring_data[measurement.point_id] = []
            self.monitoring_data[measurement.point_id].append(measurement)
            
            # Keep only last 1000 measurements in memory per point
            if len(self.monitoring_data[measurement.point_id]) > 1000:
                self.monitoring_data[measurement.point_id] = self.monitoring_data[measurement.point_id][-1000:]
            
        except Exception as e:
            self.logger.error(f"Error storing measurement: {e}")
            raise
    
    async def _generate_alert(self, point: MonitoringPoint, measurement: MonitoringData):
        """Generate environmental alert"""
        try:
            current_time = time.time()
            alert_id = f"ALERT-{int(current_time)}-{str(uuid.uuid4())[:8]}"
            
            # Determine threshold that was exceeded
            threshold_value = point.warning_threshold
            if measurement.alert_level == AlertLevel.CRITICAL:
                threshold_value = point.critical_threshold
            
            alert = EnvironmentalAlert(
                alert_id=alert_id,
                point_id=point.point_id,
                alert_type=f"{point.parameter_type}_threshold_exceeded",
                alert_level=measurement.alert_level,
                trigger_value=measurement.measurement_value,
                threshold_value=threshold_value or 0.0,
                alert_timestamp=current_time,
                alert_message=f"{point.point_name}: {point.parameter_type} value {measurement.measurement_value} {point.measurement_unit} exceeds {measurement.alert_level.value} threshold of {threshold_value} {point.measurement_unit}",
                response_actions=self._get_response_actions(measurement.alert_level, point.parameter_type),
                responsible_persons=["environmental_manager", point.responsible_person],
                acknowledgment_status="pending",
                resolution_timestamp=None,
                resolution_actions=[]
            )
            
            # Store alert
            await self._store_alert(alert)
            self.environmental_alerts[alert_id] = alert
            
            # Log alert
            self.logger.warning(f"Environmental alert generated: {alert.alert_message}")
            
            # Save alert to file
            alert_file = f"{self.alerts_directory}/alert_{alert_id}.json"
            with open(alert_file, 'w') as f:
                json.dump(asdict(alert), f, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Error generating alert: {e}")
    
    def _get_response_actions(self, alert_level: AlertLevel, parameter_type: str) -> List[str]:
        """Get appropriate response actions for alert"""
        base_actions = {
            "energy_consumption": [
                "Check equipment efficiency",
                "Review energy usage patterns",
                "Implement energy saving measures"
            ],
            "water_consumption": [
                "Check for leaks",
                "Review water usage patterns",
                "Implement water conservation measures"
            ],
            "waste_generation": [
                "Review waste management procedures",
                "Implement waste reduction measures",
                "Check recycling processes"
            ],
            "carbon_emissions": [
                "Review energy sources",
                "Implement carbon reduction measures",
                "Consider renewable energy options"
            ],
            "temperature": [
                "Check HVAC systems",
                "Review cooling efficiency",
                "Adjust temperature controls"
            ],
            "humidity": [
                "Check humidity control systems",
                "Review ventilation",
                "Adjust humidity controls"
            ]
        }
        
        actions = base_actions.get(parameter_type, ["Investigate cause", "Take corrective action"])
        
        if alert_level == AlertLevel.CRITICAL:
            actions.insert(0, "Immediate investigation required")
            actions.append("Notify management immediately")
        
        return actions
    
    async def _store_alert(self, alert: EnvironmentalAlert):
        """Store alert in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO environmental_alerts
                (alert_id, point_id, alert_type, alert_level, trigger_value, threshold_value,
                 alert_timestamp, alert_message, response_actions, responsible_persons,
                 acknowledgment_status, resolution_timestamp, resolution_actions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id, alert.point_id, alert.alert_type, alert.alert_level.value,
                alert.trigger_value, alert.threshold_value, alert.alert_timestamp,
                alert.alert_message, json.dumps(alert.response_actions),
                json.dumps(alert.responsible_persons), alert.acknowledgment_status,
                alert.resolution_timestamp, json.dumps(alert.resolution_actions)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}")
            raise
    
    async def _alert_monitoring(self):
        """Monitor and manage alerts"""
        try:
            while True:
                # Check for unacknowledged alerts
                current_time = time.time()
                
                for alert in self.environmental_alerts.values():
                    if (alert.acknowledgment_status == "pending" and 
                        current_time - alert.alert_timestamp > 3600):  # 1 hour
                        
                        self.logger.warning(f"Unacknowledged alert: {alert.alert_id}")
                        # Could escalate alert here
                
                # Wait 30 minutes before next check
                await asyncio.sleep(1800)
                
        except Exception as e:
            self.logger.error(f"Error in alert monitoring: {e}")
    
    async def _calibration_monitoring(self):
        """Monitor equipment calibration status"""
        try:
            while True:
                current_time = time.time()
                
                for point in self.monitoring_points.values():
                    if point.next_calibration <= current_time:
                        self.logger.info(f"Equipment calibration due: {point.equipment_id} for {point.point_name}")
                        # Could trigger calibration workflow here
                
                # Check daily
                await asyncio.sleep(86400)
                
        except Exception as e:
            self.logger.error(f"Error in calibration monitoring: {e}")
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring program summary"""
        try:
            current_time = time.time()
            
            # Count monitoring points by status
            active_points = sum(1 for p in self.monitoring_points.values() if p.status == MonitoringStatus.ACTIVE)
            total_points = len(self.monitoring_points)
            
            # Count recent measurements (last 24 hours)
            recent_measurements = 0
            for measurements in self.monitoring_data.values():
                recent_measurements += sum(1 for m in measurements if current_time - m.measurement_timestamp <= 86400)
            
            # Count active alerts
            active_alerts = sum(1 for a in self.environmental_alerts.values()
                              if a.acknowledgment_status == "pending")
            
            # Count critical alerts
            critical_alerts = sum(1 for a in self.environmental_alerts.values()
                                if a.alert_level == AlertLevel.CRITICAL and a.acknowledgment_status == "pending")
            
            # Calculate monitoring coverage
            monitoring_coverage = (active_points / total_points * 100) if total_points > 0 else 0
            
            # Get parameter type distribution
            parameter_types = {}
            for point in self.monitoring_points.values():
                param_type = point.parameter_type
                if param_type not in parameter_types:
                    parameter_types[param_type] = 0
                parameter_types[param_type] += 1
            
            summary = {
                "monitoring_points": {
                    "total_points": total_points,
                    "active_points": active_points,
                    "inactive_points": total_points - active_points,
                    "monitoring_coverage": round(monitoring_coverage, 2)
                },
                "measurements": {
                    "recent_measurements_24h": recent_measurements,
                    "total_data_points": sum(len(measurements) for measurements in self.monitoring_data.values())
                },
                "alerts": {
                    "active_alerts": active_alerts,
                    "critical_alerts": critical_alerts,
                    "total_alerts": len(self.environmental_alerts)
                },
                "parameter_distribution": parameter_types,
                "system_status": {
                    "operational": active_points > 0,
                    "alert_status": "CRITICAL" if critical_alerts > 0 else "WARNING" if active_alerts > 0 else "NORMAL",
                    "data_quality": "GOOD" if recent_measurements > 0 else "NO_DATA"
                },
                "timestamp": current_time
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring summary: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "system_status": {"operational": False, "alert_status": "ERROR", "data_quality": "ERROR"}
            }


# Global monitoring program instance
monitoring_program_instance = None

async def get_monitoring_program_instance():
    """Get global monitoring program instance"""
    global monitoring_program_instance
    if monitoring_program_instance is None:
        monitoring_program_instance = EnvironmentalMonitoringProgram()
        await asyncio.sleep(1)  # Allow initialization
    return monitoring_program_instance


if __name__ == "__main__":
    async def main():
        """Main function for testing"""
        logging.basicConfig(level=logging.INFO)
        
        # Initialize monitoring program
        program = EnvironmentalMonitoringProgram()
        await asyncio.sleep(3)  # Allow initialization
        
        # Get monitoring summary
        print("Getting monitoring summary...")
        summary = await program.get_monitoring_summary()
        print(f"Monitoring Summary: {json.dumps(summary, indent=2)}")
        
        # Simulate some measurements
        print("Simulating measurements...")
        for point_id in list(program.monitoring_points.keys())[:3]:
            point = program.monitoring_points[point_id]
            value = await program._simulate_measurement(point)
            print(f"Simulated measurement for {point.point_name}: {value} {point.measurement_unit}")
    
    asyncio.run(main())