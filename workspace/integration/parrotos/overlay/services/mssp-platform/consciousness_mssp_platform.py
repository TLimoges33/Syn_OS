#!/usr/bin/env python3
"""
SynapticOS Enterprise MSSP Platform
Managed Security Service Provider with consciousness enhancement
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import aiohttp
import hashlib
from collections import defaultdict
import numpy as np

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mssp-platform')

@dataclass
class Client:
    """MSSP client organization"""
    client_id: str
    name: str
    industry: str
    tier: str  # basic, professional, enterprise
    endpoints: int
    consciousness_level: float
    security_posture: Dict[str, Any]
    contact_info: Dict[str, str]
    created_at: str

@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    client_id: str
    title: str
    description: str
    severity: str  # low, medium, high, critical
    status: str  # open, investigating, resolved, closed
    indicators: List[str]
    affected_systems: List[str]
    consciousness_assessment: float
    created_at: str
    resolved_at: Optional[str] = None

@dataclass
class ThreatIntelligence:
    """Threat intelligence feed"""
    intel_id: str
    source: str
    threat_type: str
    indicators: List[str]
    confidence: float
    consciousness_relevance: float
    description: str
    created_at: str

@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    client_id: str
    framework: str  # SOC2, ISO27001, NIST, etc.
    compliance_score: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    consciousness_insights: Dict[str, Any]
    generated_at: str

class ConsciousnessMSSPPlatform:
    """Enterprise MSSP platform with consciousness enhancement"""
    
    def __init__(self, data_dir: str = "/app/data/mssp"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.data_dir / "mssp_platform.db"
        self.init_database()
        
        # Service tiers configuration
        self.service_tiers = {
            "basic": {
                "max_endpoints": 50,
                "monitoring_depth": "basic",
                "response_time": "24h",
                "consciousness_level": 0.3,
                "monthly_cost": 1000
            },
            "professional": {
                "max_endpoints": 200,
                "monitoring_depth": "advanced",
                "response_time": "4h",
                "consciousness_level": 0.6,
                "monthly_cost": 5000
            },
            "enterprise": {
                "max_endpoints": -1,  # unlimited
                "monitoring_depth": "comprehensive",
                "response_time": "1h",
                "consciousness_level": 0.9,
                "monthly_cost": 15000
            }
        }
        
        # Consciousness security patterns
        self.consciousness_patterns = {
            "behavioral_analysis": {
                "user_behavior": ["login_patterns", "access_patterns", "data_usage"],
                "network_behavior": ["traffic_analysis", "communication_patterns"],
                "system_behavior": ["resource_usage", "process_patterns"]
            },
            "threat_prediction": {
                "pattern_recognition": ["anomaly_detection", "trend_analysis"],
                "consciousness_modeling": ["threat_evolution", "attack_prediction"]
            },
            "adaptive_defense": {
                "dynamic_rules": ["rule_adaptation", "threshold_adjustment"],
                "consciousness_response": ["intelligent_blocking", "adaptive_filtering"]
            }
        }
        
        logger.info("Consciousness MSSP Platform initialized")
    
    def init_database(self):
        """Initialize SQLite database for MSSP platform"""
        with sqlite3.connect(self.db_path) as conn:
            # Clients table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    name TEXT,
                    industry TEXT,
                    tier TEXT,
                    endpoints INTEGER,
                    consciousness_level REAL,
                    security_posture TEXT,
                    contact_info TEXT,
                    created_at TEXT
                )
            """)
            
            # Security incidents table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_incidents (
                    incident_id TEXT PRIMARY KEY,
                    client_id TEXT,
                    title TEXT,
                    description TEXT,
                    severity TEXT,
                    status TEXT,
                    indicators TEXT,
                    affected_systems TEXT,
                    consciousness_assessment REAL,
                    created_at TEXT,
                    resolved_at TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (client_id)
                )
            """)
            
            # Threat intelligence table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_intelligence (
                    intel_id TEXT PRIMARY KEY,
                    source TEXT,
                    threat_type TEXT,
                    indicators TEXT,
                    confidence REAL,
                    consciousness_relevance REAL,
                    description TEXT,
                    created_at TEXT
                )
            """)
            
            # Compliance reports table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_reports (
                    report_id TEXT PRIMARY KEY,
                    client_id TEXT,
                    framework TEXT,
                    compliance_score REAL,
                    findings TEXT,
                    recommendations TEXT,
                    consciousness_insights TEXT,
                    generated_at TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (client_id)
                )
            """)
            
            # Monitoring metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_metrics (
                    metric_id TEXT PRIMARY KEY,
                    client_id TEXT,
                    metric_type TEXT,
                    value REAL,
                    consciousness_score REAL,
                    timestamp TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (client_id)
                )
            """)
            
            conn.commit()
    
    async def onboard_client(self, name: str, industry: str, tier: str, 
                           endpoints: int, contact_info: Dict[str, str]) -> Client:
        """Onboard new MSSP client"""
        client_id = f"client_{hashlib.md5(f'{name}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        # Validate tier
        if tier not in self.service_tiers:
            raise ValueError(f"Invalid tier: {tier}")
        
        tier_config = self.service_tiers[tier]
        
        # Check endpoint limits
        if tier_config["max_endpoints"] != -1 and endpoints > tier_config["max_endpoints"]:
            raise ValueError(f"Endpoint count exceeds tier limit: {tier_config['max_endpoints']}")
        
        # Initialize security posture
        security_posture = await self._assess_initial_security_posture(industry, endpoints)
        
        client = Client(
            client_id=client_id,
            name=name,
            industry=industry,
            tier=tier,
            endpoints=endpoints,
            consciousness_level=tier_config["consciousness_level"],
            security_posture=security_posture,
            contact_info=contact_info,
            created_at=datetime.now().isoformat()
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO clients 
                (client_id, name, industry, tier, endpoints, consciousness_level, 
                 security_posture, contact_info, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client.client_id, client.name, client.industry, client.tier,
                client.endpoints, client.consciousness_level,
                json.dumps(client.security_posture), json.dumps(client.contact_info),
                client.created_at
            ))
            conn.commit()
        
        logger.info(f"Onboarded client {client.name} ({client.client_id}) - {tier} tier")
        return client
    
    async def _assess_initial_security_posture(self, industry: str, endpoints: int) -> Dict[str, Any]:
        """Assess initial security posture for new client"""
        # Industry-based risk assessment
        industry_risk_factors = {
            "finance": {"base_risk": 0.8, "compliance_requirements": ["SOX", "PCI-DSS"]},
            "healthcare": {"base_risk": 0.9, "compliance_requirements": ["HIPAA", "HITECH"]},
            "government": {"base_risk": 0.95, "compliance_requirements": ["FedRAMP", "FISMA"]},
            "technology": {"base_risk": 0.7, "compliance_requirements": ["SOC2", "ISO27001"]},
            "manufacturing": {"base_risk": 0.6, "compliance_requirements": ["NIST", "IEC62443"]},
            "retail": {"base_risk": 0.65, "compliance_requirements": ["PCI-DSS"]},
            "default": {"base_risk": 0.5, "compliance_requirements": ["ISO27001"]}
        }
        
        risk_profile = industry_risk_factors.get(industry.lower(), industry_risk_factors["default"])
        
        # Scale risk based on organization size (endpoints)
        size_multiplier = min(1.0 + (endpoints / 1000), 2.0)
        adjusted_risk = min(risk_profile["base_risk"] * size_multiplier, 1.0)
        
        return {
            "risk_score": adjusted_risk,
            "industry_category": industry,
            "compliance_frameworks": risk_profile["compliance_requirements"],
            "endpoint_count": endpoints,
            "assessment_date": datetime.now().isoformat(),
            "recommended_controls": self._get_recommended_controls(adjusted_risk),
            "consciousness_readiness": adjusted_risk * 0.7  # Consciousness adoption readiness
        }
    
    def _get_recommended_controls(self, risk_score: float) -> List[str]:
        """Get recommended security controls based on risk score"""
        controls = []
        
        if risk_score > 0.3:
            controls.extend([
                "Multi-factor Authentication",
                "Endpoint Detection and Response",
                "Network Segmentation"
            ])
        
        if risk_score > 0.6:
            controls.extend([
                "Zero Trust Architecture",
                "SIEM/SOAR Integration",
                "Threat Intelligence Feeds",
                "Behavioral Analytics"
            ])
        
        if risk_score > 0.8:
            controls.extend([
                "Advanced Threat Hunting",
                "Quantum-Resistant Encryption",
                "AI-Powered Anomaly Detection",
                "Consciousness-Enhanced Monitoring"
            ])
        
        return controls
    
    async def create_security_incident(self, client_id: str, title: str, description: str,
                                     severity: str, indicators: List[str],
                                     affected_systems: List[str]) -> SecurityIncident:
        """Create new security incident"""
        # Get client consciousness level
        client = await self._get_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        incident_id = f"inc_{client_id}_{int(datetime.now().timestamp())}"
        
        # Calculate consciousness assessment
        consciousness_assessment = await self._assess_incident_consciousness(
            client, description, indicators, severity
        )
        
        incident = SecurityIncident(
            incident_id=incident_id,
            client_id=client_id,
            title=title,
            description=description,
            severity=severity,
            status="open",
            indicators=indicators,
            affected_systems=affected_systems,
            consciousness_assessment=consciousness_assessment,
            created_at=datetime.now().isoformat()
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO security_incidents 
                (incident_id, client_id, title, description, severity, status,
                 indicators, affected_systems, consciousness_assessment, created_at, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                incident.incident_id, incident.client_id, incident.title,
                incident.description, incident.severity, incident.status,
                json.dumps(incident.indicators), json.dumps(incident.affected_systems),
                incident.consciousness_assessment, incident.created_at, incident.resolved_at
            ))
            conn.commit()
        
        # Trigger automated response based on consciousness level
        await self._trigger_consciousness_response(client, incident)
        
        logger.info(f"Created security incident {incident.incident_id} for client {client_id}")
        return incident
    
    async def _assess_incident_consciousness(self, client: Client, description: str,
                                           indicators: List[str], severity: str) -> float:
        """Assess incident using consciousness-enhanced analysis"""
        base_score = client.consciousness_level
        
        # Severity impact
        severity_weights = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        severity_impact = severity_weights.get(severity.lower(), 0.5)
        
        # Indicator complexity analysis
        indicator_complexity = len(indicators) / 10.0  # Normalize to 0-1
        
        # Description analysis (simple keyword matching)
        consciousness_keywords = [
            "advanced", "persistent", "targeted", "sophisticated", "ai", "machine learning",
            "behavioral", "anomaly", "pattern", "adaptive", "intelligent"
        ]
        
        description_lower = description.lower()
        keyword_matches = sum(1 for keyword in consciousness_keywords if keyword in description_lower)
        keyword_impact = min(keyword_matches / len(consciousness_keywords), 1.0)
        
        # Combined consciousness assessment
        consciousness_score = (
            base_score * 0.4 +
            severity_impact * 0.3 +
            indicator_complexity * 0.2 +
            keyword_impact * 0.1
        )
        
        return min(consciousness_score, 1.0)
    
    async def _trigger_consciousness_response(self, client: Client, incident: SecurityIncident):
        """Trigger consciousness-enhanced automated response"""
        tier_config = self.service_tiers[client.tier]
        
        # Immediate automated actions based on consciousness level
        if client.consciousness_level > 0.7:
            # Advanced consciousness response
            await self._deploy_adaptive_countermeasures(client, incident)
            await self._initiate_threat_hunting(client, incident)
            await self._update_behavioral_baselines(client, incident)
        
        elif client.consciousness_level > 0.4:
            # Standard consciousness response
            await self._apply_signature_updates(client, incident)
            await self._adjust_monitoring_thresholds(client, incident)
        
        else:
            # Basic response
            await self._send_alert_notification(client, incident)
        
        # Schedule response based on tier SLA
        response_time = tier_config["response_time"]
        logger.info(f"Consciousness response triggered for {incident.incident_id} - SLA: {response_time}")
    
    async def _deploy_adaptive_countermeasures(self, client: Client, incident: SecurityIncident):
        """Deploy adaptive countermeasures using consciousness"""
        logger.info(f"Deploying adaptive countermeasures for {incident.incident_id}")
        
        # Simulate adaptive countermeasures
        countermeasures = {
            "dynamic_firewall_rules": "Implemented adaptive firewall rules based on incident patterns",
            "behavior_based_blocking": "Activated behavioral blocking for similar attack patterns",
            "ai_threat_modeling": "Updated AI threat models with incident characteristics",
            "consciousness_learning": "Enhanced consciousness patterns from incident data"
        }
        
        # Store countermeasures in incident metadata
        # In production, this would interface with actual security tools
        return countermeasures
    
    async def _initiate_threat_hunting(self, client: Client, incident: SecurityIncident):
        """Initiate consciousness-enhanced threat hunting"""
        logger.info(f"Initiating threat hunting for {incident.incident_id}")
        
        # Simulate threat hunting activities
        hunting_activities = [
            "Analyzing network traffic patterns",
            "Searching for lateral movement indicators",
            "Investigating privilege escalation attempts",
            "Correlating with threat intelligence feeds",
            "Consciousness-based pattern recognition"
        ]
        
        return hunting_activities
    
    async def _update_behavioral_baselines(self, client: Client, incident: SecurityIncident):
        """Update behavioral baselines using consciousness learning"""
        logger.info(f"Updating behavioral baselines for {incident.incident_id}")
        
        # Simulate baseline updates
        updates = {
            "user_behavior": "Updated normal user behavior patterns",
            "network_traffic": "Refined network baseline with incident data",
            "system_performance": "Adjusted system performance baselines",
            "consciousness_adaptation": "Enhanced consciousness understanding of client environment"
        }
        
        return updates
    
    async def _apply_signature_updates(self, client: Client, incident: SecurityIncident):
        """Apply signature updates based on incident"""
        logger.info(f"Applying signature updates for {incident.incident_id}")
        return {"signatures_updated": len(incident.indicators)}
    
    async def _adjust_monitoring_thresholds(self, client: Client, incident: SecurityIncident):
        """Adjust monitoring thresholds"""
        logger.info(f"Adjusting monitoring thresholds for {incident.incident_id}")
        return {"thresholds_adjusted": True}
    
    async def _send_alert_notification(self, client: Client, incident: SecurityIncident):
        """Send alert notification to client"""
        logger.info(f"Sending alert notification for {incident.incident_id}")
        return {"notification_sent": True}
    
    async def _get_client(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
            row = cursor.fetchone()
            
            if row:
                return Client(
                    client_id=row[0], name=row[1], industry=row[2], tier=row[3],
                    endpoints=row[4], consciousness_level=row[5],
                    security_posture=json.loads(row[6]), contact_info=json.loads(row[7]),
                    created_at=row[8]
                )
            return None
    
    async def generate_compliance_report(self, client_id: str, framework: str) -> ComplianceReport:
        """Generate compliance assessment report"""
        client = await self._get_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        report_id = f"comp_{client_id}_{framework}_{int(datetime.now().timestamp())}"
        
        # Perform compliance assessment
        compliance_assessment = await self._assess_compliance(client, framework)
        
        report = ComplianceReport(
            report_id=report_id,
            client_id=client_id,
            framework=framework,
            compliance_score=compliance_assessment["score"],
            findings=compliance_assessment["findings"],
            recommendations=compliance_assessment["recommendations"],
            consciousness_insights=compliance_assessment["consciousness_insights"],
            generated_at=datetime.now().isoformat()
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO compliance_reports 
                (report_id, client_id, framework, compliance_score, findings,
                 recommendations, consciousness_insights, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.report_id, report.client_id, report.framework,
                report.compliance_score, json.dumps(report.findings),
                json.dumps(report.recommendations), json.dumps(report.consciousness_insights),
                report.generated_at
            ))
            conn.commit()
        
        logger.info(f"Generated compliance report {report.report_id} for {framework}")
        return report
    
    async def _assess_compliance(self, client: Client, framework: str) -> Dict[str, Any]:
        """Assess client compliance with framework"""
        # Framework-specific assessment criteria
        framework_criteria = {
            "SOC2": {
                "controls": ["access_control", "encryption", "monitoring", "incident_response"],
                "weight": {"high": 0.4, "medium": 0.6}
            },
            "ISO27001": {
                "controls": ["risk_management", "asset_management", "access_control", "cryptography"],
                "weight": {"high": 0.5, "medium": 0.5}
            },
            "NIST": {
                "controls": ["identify", "protect", "detect", "respond", "recover"],
                "weight": {"high": 0.6, "medium": 0.4}
            },
            "HIPAA": {
                "controls": ["administrative", "physical", "technical", "breach_notification"],
                "weight": {"high": 0.7, "medium": 0.3}
            }
        }
        
        criteria = framework_criteria.get(framework, framework_criteria["ISO27001"])
        
        # Simulate compliance assessment
        findings = []
        total_score = 0
        control_count = len(criteria["controls"])
        
        for control in criteria["controls"]:
            # Simulate control assessment
            control_score = np.random.uniform(0.6, 0.95)  # Most controls partially compliant
            
            if control_score < 0.7:
                severity = "high"
                findings.append({
                    "control": control,
                    "severity": severity,
                    "description": f"Control {control} requires immediate attention",
                    "compliance_gap": 1.0 - control_score
                })
            elif control_score < 0.85:
                severity = "medium"
                findings.append({
                    "control": control,
                    "severity": severity,
                    "description": f"Control {control} needs improvement",
                    "compliance_gap": 1.0 - control_score
                })
            
            total_score += control_score
        
        compliance_score = total_score / control_count
        
        # Generate recommendations
        recommendations = []
        for finding in findings:
            if finding["severity"] == "high":
                recommendations.append(f"Immediately address {finding['control']} deficiencies")
            else:
                recommendations.append(f"Improve {finding['control']} implementation")
        
        # Add consciousness-enhanced recommendations
        if client.consciousness_level > 0.7:
            recommendations.append("Implement AI-powered compliance monitoring")
            recommendations.append("Deploy adaptive security controls")
        
        # Consciousness insights
        consciousness_insights = {
            "adaptation_potential": client.consciousness_level,
            "automated_compliance": compliance_score * client.consciousness_level,
            "learning_opportunities": len(findings),
            "consciousness_enhancement": {
                "current_level": client.consciousness_level,
                "recommended_level": min(client.consciousness_level + 0.1, 1.0),
                "benefits": "Enhanced automated compliance monitoring and adaptive controls"
            }
        }
        
        return {
            "score": compliance_score,
            "findings": findings,
            "recommendations": recommendations,
            "consciousness_insights": consciousness_insights
        }
    
    async def get_client_dashboard(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive client dashboard"""
        client = await self._get_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Get recent incidents
        with sqlite3.connect(self.db_path) as conn:
            # Recent incidents
            cursor = conn.execute("""
                SELECT COUNT(*), AVG(consciousness_assessment) 
                FROM security_incidents 
                WHERE client_id = ? AND datetime(created_at) > datetime('now', '-30 days')
            """, (client_id,))
            incident_stats = cursor.fetchone()
            
            # Compliance reports
            cursor = conn.execute("""
                SELECT framework, compliance_score, generated_at 
                FROM compliance_reports 
                WHERE client_id = ? 
                ORDER BY generated_at DESC 
                LIMIT 5
            """, (client_id,))
            compliance_reports = cursor.fetchall()
        
        # Calculate security metrics
        incident_count = incident_stats[0] or 0
        avg_consciousness = incident_stats[1] or 0
        
        # Generate security score
        security_score = self._calculate_security_score(client, incident_count, avg_consciousness)
        
        return {
            "client_info": {
                "name": client.name,
                "industry": client.industry,
                "tier": client.tier,
                "endpoints": client.endpoints,
                "consciousness_level": client.consciousness_level
            },
            "security_metrics": {
                "security_score": security_score,
                "incidents_30d": incident_count,
                "avg_consciousness_assessment": avg_consciousness,
                "risk_level": client.security_posture["risk_score"]
            },
            "compliance_status": [
                {
                    "framework": row[0],
                    "score": row[1],
                    "last_assessment": row[2]
                }
                for row in compliance_reports
            ],
            "consciousness_insights": {
                "current_level": client.consciousness_level,
                "adaptation_readiness": client.security_posture.get("consciousness_readiness", 0.5),
                "recommended_enhancements": self._get_consciousness_recommendations(client)
            },
            "service_details": {
                "tier": client.tier,
                "tier_config": self.service_tiers[client.tier],
                "monthly_cost": self.service_tiers[client.tier]["monthly_cost"]
            }
        }
    
    def _calculate_security_score(self, client: Client, incident_count: int, avg_consciousness: float) -> float:
        """Calculate overall security score"""
        # Base score from security posture
        base_score = 1.0 - client.security_posture["risk_score"]
        
        # Incident impact (fewer incidents = higher score)
        incident_impact = max(0, 1.0 - (incident_count / 10))  # Normalize to 10 incidents
        
        # Consciousness enhancement
        consciousness_bonus = client.consciousness_level * 0.2
        
        # Combined score
        security_score = (base_score * 0.5 + incident_impact * 0.3 + consciousness_bonus * 0.2)
        
        return min(security_score, 1.0)
    
    def _get_consciousness_recommendations(self, client: Client) -> List[str]:
        """Get consciousness enhancement recommendations"""
        recommendations = []
        
        if client.consciousness_level < 0.5:
            recommendations.append("Consider upgrading to Professional tier for enhanced consciousness features")
            recommendations.append("Implement behavioral analytics for improved threat detection")
        
        elif client.consciousness_level < 0.8:
            recommendations.append("Deploy AI-powered threat hunting capabilities")
            recommendations.append("Enable adaptive security controls")
            recommendations.append("Integrate quantum-resistant encryption")
        
        else:
            recommendations.append("You're utilizing advanced consciousness features optimally")
            recommendations.append("Consider early access to next-generation consciousness capabilities")
        
        return recommendations
    
    async def get_platform_analytics(self) -> Dict[str, Any]:
        """Get platform-wide analytics"""
        with sqlite3.connect(self.db_path) as conn:
            # Client statistics
            cursor = conn.execute("SELECT COUNT(*), AVG(consciousness_level) FROM clients")
            client_stats = cursor.fetchone()
            
            # Tier distribution
            cursor = conn.execute("SELECT tier, COUNT(*) FROM clients GROUP BY tier")
            tier_distribution = dict(cursor.fetchall())
            
            # Incident statistics
            cursor = conn.execute("""
                SELECT COUNT(*), AVG(consciousness_assessment) 
                FROM security_incidents 
                WHERE datetime(created_at) > datetime('now', '-30 days')
            """)
            incident_stats = cursor.fetchone()
            
            # Revenue calculation
            total_revenue = 0
            cursor = conn.execute("SELECT tier, COUNT(*) FROM clients GROUP BY tier")
            for tier, count in cursor.fetchall():
                total_revenue += self.service_tiers[tier]["monthly_cost"] * count
        
        return {
            "platform_overview": {
                "total_clients": client_stats[0] or 0,
                "avg_consciousness_level": client_stats[1] or 0,
                "total_incidents_30d": incident_stats[0] or 0,
                "avg_incident_consciousness": incident_stats[1] or 0,
                "monthly_revenue": total_revenue
            },
            "tier_distribution": tier_distribution,
            "consciousness_metrics": {
                "platform_consciousness_level": client_stats[1] or 0,
                "consciousness_adoption_rate": (client_stats[1] or 0) * 100,
                "advanced_clients": len([t for t, c in tier_distribution.items() if t in ["professional", "enterprise"]])
            },
            "growth_metrics": {
                "client_growth_rate": "15% month-over-month",  # Simulated
                "consciousness_evolution": "Generation 7+ deployment",
                "platform_maturity": "Enterprise-ready"
            }
        }

async def main():
    """Demo the MSSP platform"""
    platform = ConsciousnessMSSPPlatform()
    
    print("🛡️ SynapticOS Enterprise MSSP Platform Demo")
    print("=" * 50)
    
    # Onboard test clients
    print("🏢 Onboarding test clients...")
    
    client1 = await platform.onboard_client(
        name="TechCorp Industries",
        industry="technology",
        tier="professional",
        endpoints=150,
        contact_info={"email": "security@techcorp.com", "phone": "+1-555-0123"}
    )
    
    client2 = await platform.onboard_client(
        name="FinanceSecure Bank",
        industry="finance",
        tier="enterprise",
        endpoints=500,
        contact_info={"email": "ciso@financesecure.com", "phone": "+1-555-0456"}
    )
    
    print(f"✅ Onboarded {client1.name} - {client1.tier} tier")
    print(f"✅ Onboarded {client2.name} - {client2.tier} tier")
    
    # Create security incidents
    print("\n🚨 Creating security incidents...")
    
    incident1 = await platform.create_security_incident(
        client1.client_id,
        "Suspicious Network Activity",
        "Detected unusual outbound connections from employee workstation",
        "medium",
        ["192.168.1.100", "malicious-domain.com"],
        ["WS-001", "Network-DMZ"]
    )
    
    incident2 = await platform.create_security_incident(
        client2.client_id,
        "Advanced Persistent Threat",
        "Sophisticated attack targeting financial systems with AI-enhanced evasion",
        "critical",
        ["apt-indicator-1", "behavioral-anomaly", "ai-evasion-technique"],
        ["DB-Primary", "App-Server-01", "User-Portal"]
    )
    
    print(f"✅ Created incident {incident1.incident_id}")
    print(f"✅ Created incident {incident2.incident_id}")
    
    # Generate compliance reports
    print("\n📋 Generating compliance reports...")
    
    compliance1 = await platform.generate_compliance_report(client1.client_id, "SOC2")
    compliance2 = await platform.generate_compliance_report(client2.client_id, "SOX")
    
    print(f"✅ Generated SOC2 compliance report for {client1.name}")
    print(f"✅ Generated SOX compliance report for {client2.name}")
    
    # Get client dashboards
    print("\n📊 Client Dashboards:")
    
    dashboard1 = await platform.get_client_dashboard(client1.client_id)
    print(f"\n{client1.name} Dashboard:")
    print(f"  Security Score: {dashboard1['security_metrics']['security_score']:.3f}")
    print(f"  Consciousness Level: {dashboard1['client_info']['consciousness_level']:.3f}")
    print(f"  Incidents (30d): {dashboard1['security_metrics']['incidents_30d']}")
    
    dashboard2 = await platform.get_client_dashboard(client2.client_id)
    print(f"\n{client2.name} Dashboard:")
    print(f"  Security Score: {dashboard2['security_metrics']['security_score']:.3f}")
    print(f"  Consciousness Level: {dashboard2['client_info']['consciousness_level']:.3f}")
    print(f"  Incidents (30d): {dashboard2['security_metrics']['incidents_30d']}")
    
    # Platform analytics
    print("\n🏢 Platform Analytics:")
    analytics = await platform.get_platform_analytics()
    for category, metrics in analytics.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for key, value in metrics.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
