#!/usr/bin/env python3
"""
SynOS LLM-Based Evidence Correlation Engine
GPT-4-turbo powered evidence network construction for digital forensics
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import hashlib
import re
import mimetypes

import networkx as nx
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import openai
import requests


class EvidenceType(Enum):
    FILE = "file"
    NETWORK_LOG = "network_log"
    SYSTEM_LOG = "system_log"
    REGISTRY_ENTRY = "registry_entry"
    MEMORY_ARTIFACT = "memory_artifact"
    EMAIL = "email"
    IMAGE = "image"
    DOCUMENT = "document"
    EXECUTABLE = "executable"
    SCRIPT = "script"
    DATABASE = "database"
    BROWSER_ARTIFACT = "browser_artifact"


class CorrelationType(Enum):
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    BEHAVIORAL = "behavioral"
    TECHNOLOGICAL = "technological"
    LINGUISTIC = "linguistic"
    CRYPTOGRAPHIC = "cryptographic"
    NETWORK = "network"
    FILESYSTEM = "filesystem"


@dataclass
class EvidenceItem:
    id: str
    name: str
    type: EvidenceType
    content: str
    metadata: Dict[str, Any]
    timestamp: Optional[datetime] = None
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    size: Optional[int] = None
    source_system: Optional[str] = None
    extracted_entities: Dict[str, List[str]] = field(default_factory=dict)
    relevance_score: float = 0.0
    processed: bool = False


@dataclass
class EvidenceCorrelation:
    id: str
    source_evidence: str
    target_evidence: str
    correlation_type: CorrelationType
    confidence_score: float
    description: str
    supporting_facts: List[str] = field(default_factory=list)
    llm_analysis: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvidenceCluster:
    id: str
    name: str
    evidence_items: List[str]
    cluster_type: str
    description: str
    timeline: List[Tuple[datetime, str]] = field(default_factory=list)
    key_indicators: List[str] = field(default_factory=list)
    threat_level: str = "unknown"


class LLMAnalyzer:
    """Large Language Model analyzer for evidence correlation"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        self.model = model
        self.client = None

        if api_key:
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
        else:
            logging.warning("No OpenAI API key provided - using mock responses")

    async def analyze_evidence_pair(self, evidence1: EvidenceItem, evidence2: EvidenceItem) -> Dict[str, Any]:
        """Analyze correlation between two evidence items using LLM"""

        if not self.client:
            return self._mock_analysis(evidence1, evidence2)

        prompt = self._build_correlation_prompt(evidence1, evidence2)

        try:
            response = await self._call_llm(prompt)
            return self._parse_llm_response(response)

        except Exception as e:
            logging.error(f"LLM analysis failed: {e}")
            return self._mock_analysis(evidence1, evidence2)

    def _build_correlation_prompt(self, evidence1: EvidenceItem, evidence2: EvidenceItem) -> str:
        """Build detailed prompt for evidence correlation analysis"""

        prompt = f"""
You are a digital forensics expert analyzing potential correlations between two pieces of evidence.

EVIDENCE 1:
Type: {evidence1.type.value}
Name: {evidence1.name}
Timestamp: {evidence1.timestamp}
Content: {evidence1.content[:1000]}...
Metadata: {json.dumps(evidence1.metadata, indent=2)}

EVIDENCE 2:
Type: {evidence2.type.value}
Name: {evidence2.name}
Timestamp: {evidence2.timestamp}
Content: {evidence2.content[:1000]}...
Metadata: {json.dumps(evidence2.metadata, indent=2)}

Analyze these evidence items and determine:

1. CORRELATION_TYPE: Choose from [temporal, causal, behavioral, technological, linguistic, cryptographic, network, filesystem]

2. CONFIDENCE_SCORE: Rate 0.0-1.0 based on strength of correlation

3. CORRELATION_DESCRIPTION: Detailed explanation of the relationship

4. SUPPORTING_FACTS: List specific facts supporting the correlation

5. ATTACK_CHAIN_POSITION: Where these items might fit in an attack timeline

6. THREAT_INDICATORS: Any IoCs or suspicious patterns

7. RECOMMENDED_ACTIONS: Next investigative steps

Respond in JSON format:
{{
    "correlation_type": "...",
    "confidence_score": 0.0-1.0,
    "description": "...",
    "supporting_facts": ["...", "..."],
    "attack_chain_position": "...",
    "threat_indicators": ["...", "..."],
    "recommended_actions": ["...", "..."],
    "timeline_reconstruction": "...",
    "technical_analysis": "..."
}}
"""
        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Make API call to LLM"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert digital forensics analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"LLM API call failed: {e}")
            raise

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # Fallback parsing
            return {"error": "Could not parse LLM response", "raw_response": response}

        except json.JSONDecodeError:
            return {"error": "Invalid JSON in LLM response", "raw_response": response}

    def _mock_analysis(self, evidence1: EvidenceItem, evidence2: EvidenceItem) -> Dict[str, Any]:
        """Generate mock analysis when LLM is unavailable"""
        # Simple heuristic-based correlation
        confidence = 0.5

        # Check temporal correlation
        if evidence1.timestamp and evidence2.timestamp:
            time_diff = abs((evidence1.timestamp - evidence2.timestamp).total_seconds())
            if time_diff < 300:  # Within 5 minutes
                confidence += 0.2

        # Check content similarity
        if evidence1.content and evidence2.content:
            # Simple keyword overlap check
            words1 = set(evidence1.content.lower().split())
            words2 = set(evidence2.content.lower().split())
            overlap = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0
            confidence += overlap * 0.3

        return {
            "correlation_type": "temporal",
            "confidence_score": min(confidence, 1.0),
            "description": "Automated heuristic correlation analysis",
            "supporting_facts": ["Temporal proximity", "Content similarity"],
            "attack_chain_position": "unknown",
            "threat_indicators": [],
            "recommended_actions": ["Manual review required"],
            "timeline_reconstruction": "Automated analysis - manual review needed",
            "technical_analysis": "Basic heuristic correlation performed"
        }

    async def generate_attack_narrative(self, evidence_cluster: EvidenceCluster, all_evidence: List[EvidenceItem]) -> str:
        """Generate comprehensive attack narrative using LLM"""

        if not self.client:
            return "LLM unavailable - attack narrative generation disabled"

        # Get evidence details for cluster
        cluster_evidence = [e for e in all_evidence if e.id in evidence_cluster.evidence_items]

        prompt = f"""
Generate a comprehensive attack narrative based on the following correlated evidence cluster:

CLUSTER: {evidence_cluster.name}
TYPE: {evidence_cluster.cluster_type}
THREAT LEVEL: {evidence_cluster.threat_level}

EVIDENCE TIMELINE:
"""

        # Add timeline information
        for timestamp, event in evidence_cluster.timeline:
            prompt += f"- {timestamp}: {event}\n"

        prompt += "\nDETAILED EVIDENCE:\n"

        # Add evidence details
        for evidence in cluster_evidence[:10]:  # Limit to prevent prompt overflow
            prompt += f"""
EVIDENCE: {evidence.name}
Type: {evidence.type.value}
Timestamp: {evidence.timestamp}
Content: {evidence.content[:500]}...
Entities: {evidence.extracted_entities}
---
"""

        prompt += """
Based on this evidence, provide:

1. ATTACK_NARRATIVE: Comprehensive story of what happened
2. ATTACKER_PROFILE: Likely skill level, tools used, motivation
3. ATTACK_VECTORS: How the attack was carried out
4. TIMELINE_RECONSTRUCTION: Detailed chronological sequence
5. INDICATORS_OF_COMPROMISE: Specific IoCs for detection
6. IMPACT_ASSESSMENT: What was affected/compromised
7. ATTRIBUTION_ANALYSIS: Possible threat actor characteristics
8. REMEDIATION_RECOMMENDATIONS: Specific steps to address the incident

Respond in detailed markdown format.
"""

        try:
            response = await self._call_llm(prompt)
            return response

        except Exception as e:
            logging.error(f"Attack narrative generation failed: {e}")
            return "Error generating attack narrative - manual analysis required"


class EvidenceCorrelationEngine:
    """Main engine for evidence correlation and analysis"""

    def __init__(self, db_path: str = "/var/lib/synos/evidence_correlation.db", openai_key: Optional[str] = None):
        self.db_path = Path(db_path)
        self.llm_analyzer = LLMAnalyzer(openai_key)
        self.evidence_items: Dict[str, EvidenceItem] = {}
        self.correlations: List[EvidenceCorrelation] = []
        self.evidence_graph = nx.DiGraph()
        self.clusters: List[EvidenceCluster] = []

        # Text processing components
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.entity_patterns = self._load_entity_patterns()

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for evidence correlation"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_items (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    content TEXT,
                    metadata TEXT,
                    timestamp TIMESTAMP,
                    file_path TEXT,
                    file_hash TEXT,
                    size INTEGER,
                    source_system TEXT,
                    extracted_entities TEXT,
                    relevance_score REAL DEFAULT 0.0,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS correlations (
                    id TEXT PRIMARY KEY,
                    source_evidence TEXT NOT NULL,
                    target_evidence TEXT NOT NULL,
                    correlation_type TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    description TEXT,
                    supporting_facts TEXT,
                    llm_analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_evidence) REFERENCES evidence_items (id),
                    FOREIGN KEY (target_evidence) REFERENCES evidence_items (id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_clusters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    cluster_type TEXT NOT NULL,
                    description TEXT,
                    evidence_items TEXT,
                    timeline TEXT,
                    key_indicators TEXT,
                    threat_level TEXT DEFAULT 'unknown',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _load_entity_patterns(self) -> Dict[str, re.Pattern]:
        """Load regex patterns for entity extraction"""
        return {
            'ip_addresses': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'email_addresses': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'urls': re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
            'file_paths': re.compile(r'[A-Za-z]:\\[^\s<>"|*?]*|/[^\s<>"|*?]*'),
            'registry_keys': re.compile(r'HKEY_[A-Z_]+\\[^\s<>"|*?]*'),
            'hash_md5': re.compile(r'\b[a-fA-F0-9]{32}\b'),
            'hash_sha1': re.compile(r'\b[a-fA-F0-9]{40}\b'),
            'hash_sha256': re.compile(r'\b[a-fA-F0-9]{64}\b'),
            'mac_addresses': re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'),
            'domain_names': re.compile(r'\b[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}\b')
        }

    async def add_evidence_item(self, evidence: EvidenceItem) -> str:
        """Add new evidence item to the correlation engine"""
        # Extract entities from content
        if evidence.content:
            evidence.extracted_entities = self._extract_entities(evidence.content)

        # Store in memory
        self.evidence_items[evidence.id] = evidence

        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO evidence_items
                (id, name, type, content, metadata, timestamp, file_path,
                 file_hash, size, source_system, extracted_entities, relevance_score, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evidence.id, evidence.name, evidence.type.value, evidence.content,
                json.dumps(evidence.metadata), evidence.timestamp, evidence.file_path,
                evidence.file_hash, evidence.size, evidence.source_system,
                json.dumps(evidence.extracted_entities), evidence.relevance_score, evidence.processed
            ))
            conn.commit()

        logging.info(f"Added evidence item: {evidence.name} ({evidence.id})")
        return evidence.id

    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities from evidence content using regex patterns"""
        entities = {}

        for entity_type, pattern in self.entity_patterns.items():
            matches = pattern.findall(content)
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates

        return entities

    async def correlate_evidence(self, evidence_id1: str, evidence_id2: str) -> Optional[EvidenceCorrelation]:
        """Correlate two evidence items using AI analysis"""

        evidence1 = self.evidence_items.get(evidence_id1)
        evidence2 = self.evidence_items.get(evidence_id2)

        if not evidence1 or not evidence2:
            logging.error(f"Evidence items not found: {evidence_id1}, {evidence_id2}")
            return None

        # Perform LLM-based correlation analysis
        analysis = await self.llm_analyzer.analyze_evidence_pair(evidence1, evidence2)

        if analysis.get('confidence_score', 0) < 0.3:
            return None  # Skip low-confidence correlations

        # Create correlation object
        correlation_id = self._generate_correlation_id(evidence_id1, evidence_id2)
        correlation = EvidenceCorrelation(
            id=correlation_id,
            source_evidence=evidence_id1,
            target_evidence=evidence_id2,
            correlation_type=CorrelationType(analysis.get('correlation_type', 'behavioral')),
            confidence_score=analysis.get('confidence_score', 0.5),
            description=analysis.get('description', ''),
            supporting_facts=analysis.get('supporting_facts', []),
            llm_analysis=json.dumps(analysis)
        )

        # Store correlation
        self.correlations.append(correlation)
        self._store_correlation(correlation)

        # Update evidence graph
        self.evidence_graph.add_edge(
            evidence_id1, evidence_id2,
            correlation_type=correlation.correlation_type.value,
            confidence=correlation.confidence_score,
            description=correlation.description
        )

        logging.info(f"Created correlation: {correlation_id} (confidence: {correlation.confidence_score:.2f})")
        return correlation

    async def perform_bulk_correlation(self, evidence_ids: Optional[List[str]] = None) -> int:
        """Perform correlation analysis on all evidence pairs"""
        if evidence_ids is None:
            evidence_ids = list(self.evidence_items.keys())

        correlations_created = 0

        # Generate all pairs for correlation
        for i, id1 in enumerate(evidence_ids):
            for id2 in evidence_ids[i+1:]:
                correlation = await self.correlate_evidence(id1, id2)
                if correlation:
                    correlations_created += 1

                # Rate limiting to avoid overwhelming LLM API
                await asyncio.sleep(0.1)

        logging.info(f"Created {correlations_created} evidence correlations")
        return correlations_created

    async def detect_evidence_clusters(self, min_cluster_size: int = 3) -> List[EvidenceCluster]:
        """Detect clusters of related evidence using graph analysis"""
        if len(self.evidence_graph.nodes) < min_cluster_size:
            return []

        clusters = []

        # Use community detection algorithms
        try:
            import networkx.algorithms.community as nx_comm
            communities = nx_comm.greedy_modularity_communities(self.evidence_graph.to_undirected())

            for i, community in enumerate(communities):
                if len(community) >= min_cluster_size:
                    cluster = await self._create_evidence_cluster(list(community), f"cluster_{i}")
                    clusters.append(cluster)
                    self.clusters.append(cluster)

        except Exception as e:
            logging.error(f"Cluster detection failed: {e}")
            # Fallback to simple connected components
            components = list(nx.connected_components(self.evidence_graph.to_undirected()))
            for i, component in enumerate(components):
                if len(component) >= min_cluster_size:
                    cluster = await self._create_evidence_cluster(list(component), f"component_{i}")
                    clusters.append(cluster)
                    self.clusters.append(cluster)

        logging.info(f"Detected {len(clusters)} evidence clusters")
        return clusters

    async def _create_evidence_cluster(self, evidence_ids: List[str], cluster_name: str) -> EvidenceCluster:
        """Create evidence cluster from list of evidence IDs"""

        # Analyze cluster characteristics
        evidence_items = [self.evidence_items[eid] for eid in evidence_ids if eid in self.evidence_items]

        # Create timeline
        timeline = []
        for evidence in evidence_items:
            if evidence.timestamp:
                timeline.append((evidence.timestamp, f"{evidence.name} ({evidence.type.value})"))

        timeline.sort(key=lambda x: x[0])

        # Extract key indicators
        key_indicators = set()
        for evidence in evidence_items:
            for entity_type, entities in evidence.extracted_entities.items():
                key_indicators.update(entities)

        # Determine cluster type based on evidence types
        evidence_types = [e.type.value for e in evidence_items]
        if 'network_log' in evidence_types and 'file' in evidence_types:
            cluster_type = "lateral_movement"
        elif 'executable' in evidence_types or 'script' in evidence_types:
            cluster_type = "malware_execution"
        elif 'registry_entry' in evidence_types:
            cluster_type = "persistence"
        else:
            cluster_type = "unknown"

        # Assess threat level based on evidence characteristics
        threat_level = self._assess_threat_level(evidence_items)

        cluster = EvidenceCluster(
            id=f"cluster_{int(time.time())}_{len(evidence_ids)}",
            name=cluster_name,
            evidence_items=evidence_ids,
            cluster_type=cluster_type,
            description=f"Cluster of {len(evidence_ids)} correlated evidence items",
            timeline=timeline,
            key_indicators=list(key_indicators)[:20],  # Limit to top 20
            threat_level=threat_level
        )

        # Store cluster in database
        self._store_cluster(cluster)
        return cluster

    def _assess_threat_level(self, evidence_items: List[EvidenceItem]) -> str:
        """Assess threat level based on evidence characteristics"""
        risk_indicators = 0

        for evidence in evidence_items:
            # Check for high-risk file types
            if evidence.type in [EvidenceType.EXECUTABLE, EvidenceType.SCRIPT]:
                risk_indicators += 2

            # Check for suspicious network activity
            if evidence.type == EvidenceType.NETWORK_LOG:
                if any(ip in evidence.content for ip in ['tor', 'onion', '10.', '192.168.']):
                    risk_indicators += 1

            # Check for system modifications
            if evidence.type == EvidenceType.REGISTRY_ENTRY:
                risk_indicators += 1

            # Check for suspicious entities
            for entities in evidence.extracted_entities.values():
                if any('.exe' in entity or '.bat' in entity or '.ps1' in entity for entity in entities):
                    risk_indicators += 1

        if risk_indicators >= 5:
            return "critical"
        elif risk_indicators >= 3:
            return "high"
        elif risk_indicators >= 1:
            return "medium"
        else:
            return "low"

    async def generate_investigation_report(self, cluster_id: str) -> Dict[str, Any]:
        """Generate comprehensive investigation report for evidence cluster"""

        cluster = next((c for c in self.clusters if c.id == cluster_id), None)
        if not cluster:
            return {"error": "Cluster not found"}

        # Get cluster evidence
        evidence_items = [self.evidence_items[eid] for eid in cluster.evidence_items
                         if eid in self.evidence_items]

        # Generate attack narrative using LLM
        attack_narrative = await self.llm_analyzer.generate_attack_narrative(cluster, evidence_items)

        # Calculate cluster statistics
        total_files = len([e for e in evidence_items if e.type == EvidenceType.FILE])
        total_logs = len([e for e in evidence_items if 'log' in e.type.value])
        time_span = None

        if cluster.timeline:
            start_time = min(t[0] for t in cluster.timeline)
            end_time = max(t[0] for t in cluster.timeline)
            time_span = (end_time - start_time).total_seconds() / 3600  # Hours

        # Get correlations within cluster
        cluster_correlations = []
        for correlation in self.correlations:
            if (correlation.source_evidence in cluster.evidence_items and
                correlation.target_evidence in cluster.evidence_items):
                cluster_correlations.append({
                    "source": self.evidence_items[correlation.source_evidence].name,
                    "target": self.evidence_items[correlation.target_evidence].name,
                    "type": correlation.correlation_type.value,
                    "confidence": correlation.confidence_score,
                    "description": correlation.description
                })

        report = {
            "cluster_id": cluster_id,
            "cluster_name": cluster.name,
            "cluster_type": cluster.cluster_type,
            "threat_level": cluster.threat_level,
            "evidence_count": len(evidence_items),
            "time_span_hours": time_span,
            "statistics": {
                "total_files": total_files,
                "total_logs": total_logs,
                "unique_systems": len(set(e.source_system for e in evidence_items if e.source_system)),
                "correlations_count": len(cluster_correlations)
            },
            "timeline": [{"timestamp": t[0].isoformat(), "event": t[1]} for t in cluster.timeline],
            "key_indicators": cluster.key_indicators,
            "correlations": cluster_correlations,
            "attack_narrative": attack_narrative,
            "evidence_summary": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type.value,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    "entities": e.extracted_entities
                }
                for e in evidence_items
            ],
            "generated_at": datetime.now().isoformat()
        }

        return report

    def _store_correlation(self, correlation: EvidenceCorrelation):
        """Store correlation in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO correlations
                (id, source_evidence, target_evidence, correlation_type,
                 confidence_score, description, supporting_facts, llm_analysis, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                correlation.id, correlation.source_evidence, correlation.target_evidence,
                correlation.correlation_type.value, correlation.confidence_score,
                correlation.description, json.dumps(correlation.supporting_facts),
                correlation.llm_analysis, correlation.created_at
            ))
            conn.commit()

    def _store_cluster(self, cluster: EvidenceCluster):
        """Store evidence cluster in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO evidence_clusters
                (id, name, cluster_type, description, evidence_items,
                 timeline, key_indicators, threat_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cluster.id, cluster.name, cluster.cluster_type, cluster.description,
                json.dumps(cluster.evidence_items),
                json.dumps([{"timestamp": t[0].isoformat(), "event": t[1]} for t in cluster.timeline]),
                json.dumps(cluster.key_indicators), cluster.threat_level
            ))
            conn.commit()

    def _generate_correlation_id(self, evidence_id1: str, evidence_id2: str) -> str:
        """Generate unique correlation ID"""
        combined = f"{min(evidence_id1, evidence_id2)}_{max(evidence_id1, evidence_id2)}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    async def import_evidence_from_file(self, file_path: Path) -> List[str]:
        """Import evidence from various file formats"""
        evidence_ids = []

        try:
            if file_path.suffix.lower() == '.json':
                # Import from JSON format
                with open(file_path, 'r') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    for item in data:
                        evidence = self._convert_dict_to_evidence(item, file_path)
                        if evidence:
                            evidence_id = await self.add_evidence_item(evidence)
                            evidence_ids.append(evidence_id)

            elif file_path.suffix.lower() in ['.log', '.txt']:
                # Import log files
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                evidence = EvidenceItem(
                    id=f"log_{int(time.time())}_{hash(str(file_path))}",
                    name=file_path.name,
                    type=EvidenceType.SYSTEM_LOG,
                    content=content,
                    metadata={"source_file": str(file_path)},
                    file_path=str(file_path),
                    size=file_path.stat().st_size,
                    timestamp=datetime.fromtimestamp(file_path.stat().st_mtime)
                )
                evidence_id = await self.add_evidence_item(evidence)
                evidence_ids.append(evidence_id)

        except Exception as e:
            logging.error(f"Failed to import evidence from {file_path}: {e}")

        return evidence_ids

    def _convert_dict_to_evidence(self, data: Dict[str, Any], source_file: Path) -> Optional[EvidenceItem]:
        """Convert dictionary data to EvidenceItem"""
        try:
            evidence_type = EvidenceType(data.get('type', 'file'))
            timestamp = None

            if 'timestamp' in data:
                if isinstance(data['timestamp'], str):
                    timestamp = datetime.fromisoformat(data['timestamp'])
                elif isinstance(data['timestamp'], (int, float)):
                    timestamp = datetime.fromtimestamp(data['timestamp'])

            return EvidenceItem(
                id=data.get('id', f"imported_{int(time.time())}_{hash(str(data))}"),
                name=data.get('name', 'Unknown'),
                type=evidence_type,
                content=data.get('content', ''),
                metadata=data.get('metadata', {}),
                timestamp=timestamp,
                file_path=data.get('file_path'),
                file_hash=data.get('file_hash'),
                size=data.get('size'),
                source_system=data.get('source_system')
            )
        except Exception as e:
            logging.error(f"Failed to convert data to evidence: {e}")
            return None


async def main():
    """Example usage of LLM Evidence Correlation Engine"""
    logging.basicConfig(level=logging.INFO)

    # Initialize correlation engine (without OpenAI key for demo)
    correlator = EvidenceCorrelationEngine()

    # Example: Add sample evidence items
    evidence1 = EvidenceItem(
        id="file_001",
        name="malware.exe",
        type=EvidenceType.EXECUTABLE,
        content="Binary executable file with suspicious patterns",
        metadata={"size": 524288, "hash": "abc123"},
        timestamp=datetime.now(),
        file_path="C:\\temp\\malware.exe"
    )

    evidence2 = EvidenceItem(
        id="log_001",
        name="system.log",
        type=EvidenceType.SYSTEM_LOG,
        content="Process creation: malware.exe started at 192.168.1.100",
        metadata={"source": "Windows Event Log"},
        timestamp=datetime.now() + timedelta(minutes=2)
    )

    evidence3 = EvidenceItem(
        id="network_001",
        name="network.pcap",
        type=EvidenceType.NETWORK_LOG,
        content="HTTP connection to suspicious-domain.com from 192.168.1.100",
        metadata={"protocol": "HTTP", "size": 1024},
        timestamp=datetime.now() + timedelta(minutes=5)
    )

    # Add evidence to correlator
    await correlator.add_evidence_item(evidence1)
    await correlator.add_evidence_item(evidence2)
    await correlator.add_evidence_item(evidence3)

    print("Added 3 evidence items")

    # Perform bulk correlation
    correlations_count = await correlator.perform_bulk_correlation()
    print(f"Created {correlations_count} correlations")

    # Detect clusters
    clusters = await correlator.detect_evidence_clusters()
    print(f"Detected {len(clusters)} evidence clusters")

    # Generate investigation report for first cluster
    if clusters:
        report = await correlator.generate_investigation_report(clusters[0].id)
        print(f"Generated report for cluster: {report['cluster_name']}")
        print(f"Threat level: {report['threat_level']}")
        print(f"Evidence count: {report['evidence_count']}")


if __name__ == "__main__":
    asyncio.run(main())