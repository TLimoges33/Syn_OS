#!/usr/bin/env python3
"""
SynOS Security Knowledge Graph
Personal cybersecurity knowledge base with vector embeddings and semantic search
"""

import asyncio
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import networkx as nx

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.metrics.pairwise import cosine_similarity
import spacy


class EntityType(Enum):
    VULNERABILITY = "vulnerability"
    THREAT_ACTOR = "threat_actor"
    TECHNIQUE = "technique"
    TOOL = "tool"
    INDICATOR = "indicator"
    ASSET = "asset"
    CONTROL = "control"
    INCIDENT = "incident"
    ASSESSMENT = "assessment"
    FINDING = "finding"
    MITIGATION = "mitigation"
    FRAMEWORK = "framework"


class RelationType(Enum):
    EXPLOITS = "exploits"
    MITIGATES = "mitigates"
    USES = "uses"
    TARGETS = "targets"
    RELATES_TO = "relates_to"
    IMPLEMENTS = "implements"
    CONTAINS = "contains"
    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    SUPERSEDES = "supersedes"


@dataclass
class KnowledgeEntity:
    id: str
    name: str
    entity_type: EntityType
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0
    source: str = "manual"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    embedding: Optional[np.ndarray] = None
    embedding_model: Optional[str] = None


@dataclass
class KnowledgeRelation:
    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: str = "manual"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SemanticQuery:
    query_text: str
    entity_types: Optional[List[EntityType]] = None
    max_results: int = 10
    similarity_threshold: float = 0.7
    include_relations: bool = True
    temporal_filter: Optional[Tuple[datetime, datetime]] = None


@dataclass
class SearchResult:
    entity: KnowledgeEntity
    similarity_score: float
    related_entities: List[Tuple[KnowledgeEntity, RelationType, float]] = field(default_factory=list)
    explanation: str = ""


class VectorEmbeddingManager:
    """Manage vector embeddings for semantic search"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.sentence_transformer = None
        self.faiss_index = None
        self.entity_id_map: Dict[int, str] = {}
        self.embedding_dimension = 384  # Default for MiniLM

        # Initialize model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize sentence transformer model"""
        try:
            self.sentence_transformer = SentenceTransformer(self.model_name)
            self.embedding_dimension = self.sentence_transformer.get_sentence_embedding_dimension()
            logging.info(f"Initialized embedding model: {self.model_name} (dim: {self.embedding_dimension})")

            # Initialize FAISS index
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner product for cosine similarity

        except Exception as e:
            logging.error(f"Failed to initialize embedding model: {e}")
            # Fallback to simple text matching
            self.sentence_transformer = None

    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text"""
        if not self.sentence_transformer:
            return None

        try:
            # Clean and prepare text
            clean_text = self._prepare_text(text)
            embedding = self.sentence_transformer.encode(clean_text, normalize_embeddings=True)
            return embedding.astype(np.float32)

        except Exception as e:
            logging.debug(f"Failed to generate embedding: {e}")
            return None

    def _prepare_text(self, text: str) -> str:
        """Prepare text for embedding"""
        # Remove excessive whitespace and normalize
        cleaned = ' '.join(text.split())
        return cleaned[:512]  # Limit to 512 characters

    def add_to_index(self, entity_id: str, embedding: np.ndarray):
        """Add embedding to FAISS index"""
        if self.faiss_index is None:
            return

        try:
            # Normalize embedding for cosine similarity
            embedding_norm = embedding / np.linalg.norm(embedding)
            embedding_2d = embedding_norm.reshape(1, -1)

            # Add to index
            index_id = self.faiss_index.ntotal
            self.faiss_index.add(embedding_2d)
            self.entity_id_map[index_id] = entity_id

        except Exception as e:
            logging.debug(f"Failed to add to index: {e}")

    def search_similar(self, query_embedding: np.ndarray, k: int = 10, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Search for similar embeddings"""
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []

        try:
            # Normalize query embedding
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            query_2d = query_norm.reshape(1, -1)

            # Search
            scores, indices = self.faiss_index.search(query_2d, min(k, self.faiss_index.ntotal))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if score >= threshold and idx in self.entity_id_map:
                    entity_id = self.entity_id_map[idx]
                    results.append((entity_id, float(score)))

            return results

        except Exception as e:
            logging.debug(f"Failed to search similar: {e}")
            return []

    def rebuild_index(self, entities: List[Tuple[str, np.ndarray]]):
        """Rebuild FAISS index from scratch"""
        if not self.sentence_transformer:
            return

        try:
            # Reset index
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dimension)
            self.entity_id_map = {}

            # Add all entities
            for entity_id, embedding in entities:
                self.add_to_index(entity_id, embedding)

            logging.info(f"Rebuilt FAISS index with {len(entities)} entities")

        except Exception as e:
            logging.error(f"Failed to rebuild index: {e}")


class KnowledgeExtractor:
    """Extract structured knowledge from unstructured text"""

    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy model not available")
            self.nlp = None

        # Security-specific entity patterns
        self.security_patterns = {
            'cve': r'CVE-\d{4}-\d{4,}',
            'cwe': r'CWE-\d+',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'domain': r'\b[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}\b',
            'hash_md5': r'\b[a-fA-F0-9]{32}\b',
            'hash_sha1': r'\b[a-fA-F0-9]{40}\b',
            'hash_sha256': r'\b[a-fA-F0-9]{64}\b',
            'registry_key': r'HKEY_[A-Z_]+\\[^\s<>"|*?]*',
            'file_path': r'[A-Za-z]:\\[^\s<>"]+|/[^\s<>"]+',
            'mitre_technique': r'T\d{4}(?:\.\d{3})?'
        }

        # Cybersecurity taxonomy
        self.cyber_taxonomy = {
            'vulnerabilities': ['vulnerability', 'exploit', 'bug', 'flaw', 'weakness'],
            'threats': ['malware', 'virus', 'trojan', 'ransomware', 'apt', 'threat', 'attack'],
            'controls': ['firewall', 'antivirus', 'ids', 'ips', 'siem', 'control', 'defense'],
            'techniques': ['phishing', 'sql injection', 'xss', 'buffer overflow', 'privilege escalation'],
            'assets': ['server', 'workstation', 'database', 'network', 'application', 'system']
        }

    def extract_entities(self, text: str, source: str = "text_analysis") -> List[KnowledgeEntity]:
        """Extract knowledge entities from text"""
        entities = []

        # Extract using regex patterns
        entities.extend(self._extract_pattern_entities(text, source))

        # Extract using spaCy NER
        if self.nlp:
            entities.extend(self._extract_spacy_entities(text, source))

        # Extract using cybersecurity taxonomy
        entities.extend(self._extract_taxonomy_entities(text, source))

        return entities

    def _extract_pattern_entities(self, text: str, source: str) -> List[KnowledgeEntity]:
        """Extract entities using regex patterns"""
        entities = []

        for pattern_type, pattern in self.security_patterns.items():
            import re
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                entity_value = match.group()
                entity_id = self._generate_entity_id(entity_value, pattern_type)

                # Determine entity type based on pattern
                entity_type = self._map_pattern_to_entity_type(pattern_type)

                entity = KnowledgeEntity(
                    id=entity_id,
                    name=entity_value,
                    entity_type=entity_type,
                    description=f"{pattern_type.replace('_', ' ').title()}: {entity_value}",
                    properties={
                        'pattern_type': pattern_type,
                        'extracted_from': text[:100] + "..." if len(text) > 100 else text
                    },
                    source=source,
                    confidence=0.8
                )

                entities.append(entity)

        return entities

    def _extract_spacy_entities(self, text: str, source: str) -> List[KnowledgeEntity]:
        """Extract entities using spaCy NER"""
        entities = []

        try:
            doc = self.nlp(text)

            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'GPE', 'PRODUCT']:
                    entity_id = self._generate_entity_id(ent.text, 'spacy')
                    entity_type = self._map_spacy_label_to_entity_type(ent.label_)

                    entity = KnowledgeEntity(
                        id=entity_id,
                        name=ent.text,
                        entity_type=entity_type,
                        description=f"{ent.label_}: {ent.text}",
                        properties={
                            'spacy_label': ent.label_,
                            'confidence': ent._.get('confidence', 0.7)
                        },
                        source=source,
                        confidence=0.7
                    )

                    entities.append(entity)

        except Exception as e:
            logging.debug(f"spaCy extraction failed: {e}")

        return entities

    def _extract_taxonomy_entities(self, text: str, source: str) -> List[KnowledgeEntity]:
        """Extract entities using cybersecurity taxonomy"""
        entities = []
        text_lower = text.lower()

        for category, terms in self.cyber_taxonomy.items():
            for term in terms:
                if term in text_lower:
                    entity_id = self._generate_entity_id(term, 'taxonomy')
                    entity_type = self._map_taxonomy_to_entity_type(category)

                    entity = KnowledgeEntity(
                        id=entity_id,
                        name=term.title(),
                        entity_type=entity_type,
                        description=f"Cybersecurity {category.rstrip('s')}: {term}",
                        properties={
                            'taxonomy_category': category,
                            'context': text[:200] + "..." if len(text) > 200 else text
                        },
                        source=source,
                        confidence=0.6
                    )

                    entities.append(entity)

        return entities

    def _generate_entity_id(self, value: str, source_type: str) -> str:
        """Generate unique entity ID"""
        combined = f"{source_type}:{value.lower()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _map_pattern_to_entity_type(self, pattern_type: str) -> EntityType:
        """Map regex pattern type to entity type"""
        mapping = {
            'cve': EntityType.VULNERABILITY,
            'cwe': EntityType.VULNERABILITY,
            'ip_address': EntityType.INDICATOR,
            'domain': EntityType.INDICATOR,
            'hash_md5': EntityType.INDICATOR,
            'hash_sha1': EntityType.INDICATOR,
            'hash_sha256': EntityType.INDICATOR,
            'registry_key': EntityType.INDICATOR,
            'file_path': EntityType.INDICATOR,
            'mitre_technique': EntityType.TECHNIQUE
        }
        return mapping.get(pattern_type, EntityType.INDICATOR)

    def _map_spacy_label_to_entity_type(self, spacy_label: str) -> EntityType:
        """Map spaCy entity label to our entity type"""
        mapping = {
            'ORG': EntityType.THREAT_ACTOR,
            'PERSON': EntityType.THREAT_ACTOR,
            'GPE': EntityType.ASSET,
            'PRODUCT': EntityType.TOOL
        }
        return mapping.get(spacy_label, EntityType.INDICATOR)

    def _map_taxonomy_to_entity_type(self, category: str) -> EntityType:
        """Map taxonomy category to entity type"""
        mapping = {
            'vulnerabilities': EntityType.VULNERABILITY,
            'threats': EntityType.THREAT_ACTOR,
            'controls': EntityType.CONTROL,
            'techniques': EntityType.TECHNIQUE,
            'assets': EntityType.ASSET
        }
        return mapping.get(category, EntityType.INDICATOR)


class SecurityKnowledgeGraph:
    """Main security knowledge graph implementation"""

    def __init__(self, db_path: str = "/var/lib/synos/knowledge_graph.db"):
        self.db_path = Path(db_path)
        self.graph = nx.MultiDiGraph()
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.relations: Dict[str, KnowledgeRelation] = {}

        # Components
        self.embedding_manager = VectorEmbeddingManager()
        self.knowledge_extractor = KnowledgeExtractor()

        # Initialize database
        self._init_database()

        # Load existing knowledge
        self._load_knowledge()

    def _init_database(self):
        """Initialize SQLite database for knowledge storage"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Entities table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    description TEXT,
                    properties TEXT,
                    tags TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    embedding BLOB,
                    embedding_model TEXT
                )
            """)

            # Relations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    properties TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES entities (id),
                    FOREIGN KEY (target_id) REFERENCES entities (id)
                )
            """)

            # Search index for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS entity_search USING fts5(
                    entity_id,
                    name,
                    description,
                    tags,
                    content='entities',
                    content_rowid='rowid'
                )
            """)

            conn.commit()

    def _load_knowledge(self):
        """Load existing knowledge from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load entities
                cursor = conn.execute("""
                    SELECT id, name, entity_type, description, properties, tags,
                           confidence, source, created_at, updated_at, embedding, embedding_model
                    FROM entities
                """)

                embeddings_to_index = []

                for row in cursor.fetchall():
                    entity = KnowledgeEntity(
                        id=row[0],
                        name=row[1],
                        entity_type=EntityType(row[2]),
                        description=row[3] or "",
                        properties=json.loads(row[4] or '{}'),
                        tags=json.loads(row[5] or '[]'),
                        confidence=row[6],
                        source=row[7],
                        created_at=datetime.fromisoformat(row[8]),
                        updated_at=datetime.fromisoformat(row[9]),
                        embedding_model=row[11]
                    )

                    # Deserialize embedding
                    if row[10]:
                        entity.embedding = np.frombuffer(row[10], dtype=np.float32)
                        embeddings_to_index.append((entity.id, entity.embedding))

                    self.entities[entity.id] = entity
                    self.graph.add_node(entity.id, entity=entity)

                # Load relations
                cursor = conn.execute("""
                    SELECT id, source_id, target_id, relation_type, properties,
                           confidence, source, created_at
                    FROM relations
                """)

                for row in cursor.fetchall():
                    relation = KnowledgeRelation(
                        id=row[0],
                        source_id=row[1],
                        target_id=row[2],
                        relation_type=RelationType(row[3]),
                        properties=json.loads(row[4] or '{}'),
                        confidence=row[5],
                        source=row[6],
                        created_at=datetime.fromisoformat(row[7])
                    )

                    self.relations[relation.id] = relation
                    self.graph.add_edge(
                        relation.source_id,
                        relation.target_id,
                        key=relation.id,
                        relation=relation
                    )

                # Rebuild vector index
                if embeddings_to_index:
                    self.embedding_manager.rebuild_index(embeddings_to_index)

                logging.info(f"Loaded {len(self.entities)} entities and {len(self.relations)} relations")

        except Exception as e:
            logging.error(f"Failed to load knowledge: {e}")

    async def add_entity(self, entity: KnowledgeEntity, auto_embed: bool = True) -> str:
        """Add entity to knowledge graph"""

        # Generate embedding if requested
        if auto_embed and not entity.embedding:
            embed_text = f"{entity.name} {entity.description}"
            entity.embedding = self.embedding_manager.generate_embedding(embed_text)
            entity.embedding_model = self.embedding_manager.model_name

        # Store entity
        self.entities[entity.id] = entity
        self.graph.add_node(entity.id, entity=entity)

        # Add to vector index
        if entity.embedding is not None:
            self.embedding_manager.add_to_index(entity.id, entity.embedding)

        # Store in database
        await self._store_entity(entity)

        logging.debug(f"Added entity: {entity.name} ({entity.id})")
        return entity.id

    async def add_relation(self, relation: KnowledgeRelation) -> str:
        """Add relation to knowledge graph"""

        # Verify entities exist
        if relation.source_id not in self.entities:
            raise ValueError(f"Source entity {relation.source_id} not found")
        if relation.target_id not in self.entities:
            raise ValueError(f"Target entity {relation.target_id} not found")

        # Store relation
        self.relations[relation.id] = relation
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            key=relation.id,
            relation=relation
        )

        # Store in database
        await self._store_relation(relation)

        logging.debug(f"Added relation: {relation.source_id} -> {relation.target_id} ({relation.relation_type.value})")
        return relation.id

    async def semantic_search(self, query: SemanticQuery) -> List[SearchResult]:
        """Perform semantic search on knowledge graph"""

        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embedding(query.query_text)
        if query_embedding is None:
            # Fallback to text-based search
            return await self._text_based_search(query)

        # Search similar entities
        similar_entities = self.embedding_manager.search_similar(
            query_embedding,
            k=query.max_results * 2,  # Get more candidates for filtering
            threshold=query.similarity_threshold
        )

        results = []

        for entity_id, similarity_score in similar_entities:
            entity = self.entities.get(entity_id)
            if not entity:
                continue

            # Apply entity type filter
            if query.entity_types and entity.entity_type not in query.entity_types:
                continue

            # Apply temporal filter
            if query.temporal_filter:
                start_time, end_time = query.temporal_filter
                if not (start_time <= entity.updated_at <= end_time):
                    continue

            # Get related entities if requested
            related_entities = []
            if query.include_relations:
                related_entities = self._get_related_entities(entity_id, max_depth=1)

            # Generate explanation
            explanation = self._generate_search_explanation(entity, query.query_text, similarity_score)

            result = SearchResult(
                entity=entity,
                similarity_score=similarity_score,
                related_entities=related_entities,
                explanation=explanation
            )

            results.append(result)

        # Sort by similarity score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:query.max_results]

    async def _text_based_search(self, query: SemanticQuery) -> List[SearchResult]:
        """Fallback text-based search when embeddings not available"""
        results = []

        query_terms = query.query_text.lower().split()

        for entity in self.entities.values():
            # Simple text matching
            entity_text = f"{entity.name} {entity.description}".lower()
            match_score = sum(1 for term in query_terms if term in entity_text) / len(query_terms)

            if match_score >= 0.3:  # 30% term match threshold
                # Apply filters
                if query.entity_types and entity.entity_type not in query.entity_types:
                    continue

                if query.temporal_filter:
                    start_time, end_time = query.temporal_filter
                    if not (start_time <= entity.updated_at <= end_time):
                        continue

                related_entities = []
                if query.include_relations:
                    related_entities = self._get_related_entities(entity.id, max_depth=1)

                result = SearchResult(
                    entity=entity,
                    similarity_score=match_score,
                    related_entities=related_entities,
                    explanation=f"Text match: {match_score:.2f}"
                )

                results.append(result)

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:query.max_results]

    def _get_related_entities(self, entity_id: str, max_depth: int = 1) -> List[Tuple[KnowledgeEntity, RelationType, float]]:
        """Get entities related to given entity"""
        related = []

        try:
            # Get immediate neighbors
            for neighbor_id in self.graph.neighbors(entity_id):
                neighbor_entity = self.entities.get(neighbor_id)
                if not neighbor_entity:
                    continue

                # Get relation information
                edge_data = self.graph.get_edge_data(entity_id, neighbor_id)
                if edge_data:
                    # Take first relation if multiple exist
                    relation_info = next(iter(edge_data.values()))
                    relation = relation_info.get('relation')
                    if relation:
                        related.append((
                            neighbor_entity,
                            relation.relation_type,
                            relation.confidence
                        ))

            # Sort by confidence
            related.sort(key=lambda x: x[2], reverse=True)

        except Exception as e:
            logging.debug(f"Error getting related entities: {e}")

        return related[:10]  # Limit to top 10 related entities

    def _generate_search_explanation(self, entity: KnowledgeEntity, query_text: str, similarity_score: float) -> str:
        """Generate explanation for search result"""
        explanation_parts = [
            f"Similarity: {similarity_score:.2f}",
            f"Type: {entity.entity_type.value}",
            f"Source: {entity.source}"
        ]

        if entity.confidence < 0.8:
            explanation_parts.append(f"Confidence: {entity.confidence:.2f}")

        return " | ".join(explanation_parts)

    async def extract_and_add_knowledge(self, text: str, source: str = "text_analysis") -> List[str]:
        """Extract knowledge entities from text and add to graph"""
        extracted_entities = self.knowledge_extractor.extract_entities(text, source)
        added_entity_ids = []

        for entity in extracted_entities:
            # Check if entity already exists
            existing_entity = self._find_similar_entity(entity)
            if existing_entity:
                # Update existing entity
                await self._merge_entities(existing_entity, entity)
            else:
                # Add new entity
                entity_id = await self.add_entity(entity)
                added_entity_ids.append(entity_id)

        # Auto-generate relations between extracted entities
        await self._auto_generate_relations(extracted_entities)

        return added_entity_ids

    def _find_similar_entity(self, entity: KnowledgeEntity) -> Optional[KnowledgeEntity]:
        """Find existing similar entity"""
        for existing_entity in self.entities.values():
            if (existing_entity.name.lower() == entity.name.lower() and
                existing_entity.entity_type == entity.entity_type):
                return existing_entity
        return None

    async def _merge_entities(self, existing: KnowledgeEntity, new: KnowledgeEntity):
        """Merge information from new entity into existing"""
        # Update description if new one is longer
        if len(new.description) > len(existing.description):
            existing.description = new.description

        # Merge properties
        existing.properties.update(new.properties)

        # Merge tags
        for tag in new.tags:
            if tag not in existing.tags:
                existing.tags.append(tag)

        # Update confidence (average)
        existing.confidence = (existing.confidence + new.confidence) / 2

        existing.updated_at = datetime.now()

        # Update in database
        await self._store_entity(existing)

    async def _auto_generate_relations(self, entities: List[KnowledgeEntity]):
        """Auto-generate relations between extracted entities"""
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                relation_type = self._infer_relation_type(entity1, entity2)
                if relation_type:
                    relation_id = f"auto_{entity1.id}_{entity2.id}_{relation_type.value}"

                    # Check if relation already exists
                    if relation_id not in self.relations:
                        relation = KnowledgeRelation(
                            id=relation_id,
                            source_id=entity1.id,
                            target_id=entity2.id,
                            relation_type=relation_type,
                            confidence=0.6,
                            source="auto_inference"
                        )

                        await self.add_relation(relation)

    def _infer_relation_type(self, entity1: KnowledgeEntity, entity2: KnowledgeEntity) -> Optional[RelationType]:
        """Infer relation type between two entities"""
        type1, type2 = entity1.entity_type, entity2.entity_type

        # Define relation inference rules
        inference_rules = {
            (EntityType.THREAT_ACTOR, EntityType.TECHNIQUE): RelationType.USES,
            (EntityType.THREAT_ACTOR, EntityType.TOOL): RelationType.USES,
            (EntityType.TECHNIQUE, EntityType.VULNERABILITY): RelationType.EXPLOITS,
            (EntityType.CONTROL, EntityType.VULNERABILITY): RelationType.MITIGATES,
            (EntityType.CONTROL, EntityType.TECHNIQUE): RelationType.MITIGATES,
            (EntityType.VULNERABILITY, EntityType.ASSET): RelationType.TARGETS,
            (EntityType.INDICATOR, EntityType.THREAT_ACTOR): RelationType.RELATES_TO,
        }

        # Check direct rules
        if (type1, type2) in inference_rules:
            return inference_rules[(type1, type2)]

        # Check reverse rules
        reverse_mapping = {
            RelationType.USES: RelationType.USES,
            RelationType.EXPLOITS: RelationType.MITIGATES,
            RelationType.MITIGATES: RelationType.EXPLOITS,
            RelationType.TARGETS: RelationType.CONTAINS,
            RelationType.RELATES_TO: RelationType.RELATES_TO
        }

        if (type2, type1) in inference_rules:
            base_relation = inference_rules[(type2, type1)]
            return reverse_mapping.get(base_relation, RelationType.RELATES_TO)

        return None

    async def _store_entity(self, entity: KnowledgeEntity):
        """Store entity in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Serialize embedding
                embedding_blob = None
                if entity.embedding is not None:
                    embedding_blob = entity.embedding.tobytes()

                conn.execute("""
                    INSERT OR REPLACE INTO entities
                    (id, name, entity_type, description, properties, tags,
                     confidence, source, created_at, updated_at, embedding, embedding_model)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.id, entity.name, entity.entity_type.value, entity.description,
                    json.dumps(entity.properties), json.dumps(entity.tags),
                    entity.confidence, entity.source, entity.created_at, entity.updated_at,
                    embedding_blob, entity.embedding_model
                ))

                # Update search index
                conn.execute("""
                    INSERT OR REPLACE INTO entity_search (entity_id, name, description, tags)
                    VALUES (?, ?, ?, ?)
                """, (entity.id, entity.name, entity.description, ' '.join(entity.tags)))

                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store entity: {e}")

    async def _store_relation(self, relation: KnowledgeRelation):
        """Store relation in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO relations
                    (id, source_id, target_id, relation_type, properties,
                     confidence, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    relation.id, relation.source_id, relation.target_id,
                    relation.relation_type.value, json.dumps(relation.properties),
                    relation.confidence, relation.source, relation.created_at
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store relation: {e}")

    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    def get_entity_by_name(self, name: str, entity_type: Optional[EntityType] = None) -> Optional[KnowledgeEntity]:
        """Get entity by name and optionally type"""
        for entity in self.entities.values():
            if entity.name.lower() == name.lower():
                if entity_type is None or entity.entity_type == entity_type:
                    return entity
        return None

    def list_entities(self, entity_type: Optional[EntityType] = None, limit: int = 100) -> List[KnowledgeEntity]:
        """List entities with optional type filter"""
        entities = list(self.entities.values())

        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]

        # Sort by updated date
        entities.sort(key=lambda x: x.updated_at, reverse=True)
        return entities[:limit]

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        entity_type_counts = {}
        for entity in self.entities.values():
            entity_type_counts[entity.entity_type.value] = entity_type_counts.get(entity.entity_type.value, 0) + 1

        relation_type_counts = {}
        for relation in self.relations.values():
            relation_type_counts[relation.relation_type.value] = relation_type_counts.get(relation.relation_type.value, 0) + 1

        return {
            'total_entities': len(self.entities),
            'total_relations': len(self.relations),
            'entity_types': entity_type_counts,
            'relation_types': relation_type_counts,
            'graph_density': nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0,
            'connected_components': nx.number_weakly_connected_components(self.graph),
            'embeddings_available': sum(1 for e in self.entities.values() if e.embedding is not None)
        }

    async def export_knowledge(self, file_path: Path, format: str = "json") -> bool:
        """Export knowledge graph to file"""
        try:
            if format == "json":
                export_data = {
                    'entities': [
                        {
                            'id': e.id,
                            'name': e.name,
                            'type': e.entity_type.value,
                            'description': e.description,
                            'properties': e.properties,
                            'tags': e.tags,
                            'confidence': e.confidence,
                            'source': e.source,
                            'created_at': e.created_at.isoformat(),
                            'updated_at': e.updated_at.isoformat()
                        }
                        for e in self.entities.values()
                    ],
                    'relations': [
                        {
                            'id': r.id,
                            'source_id': r.source_id,
                            'target_id': r.target_id,
                            'type': r.relation_type.value,
                            'properties': r.properties,
                            'confidence': r.confidence,
                            'source': r.source,
                            'created_at': r.created_at.isoformat()
                        }
                        for r in self.relations.values()
                    ]
                }

                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)

                logging.info(f"Exported knowledge graph to {file_path}")
                return True

        except Exception as e:
            logging.error(f"Failed to export knowledge: {e}")
            return False


async def main():
    """Example usage of Security Knowledge Graph"""
    logging.basicConfig(level=logging.INFO)

    kg = SecurityKnowledgeGraph()

    print("🧠 SynOS Security Knowledge Graph")
    print("=" * 40)

    # Add some example entities
    cve_entity = KnowledgeEntity(
        id="cve_2021_44228",
        name="CVE-2021-44228",
        entity_type=EntityType.VULNERABILITY,
        description="Apache Log4j2 Remote Code Execution Vulnerability (Log4Shell)",
        properties={
            "cvss_score": 10.0,
            "severity": "critical",
            "affected_software": "Apache Log4j2"
        },
        tags=["rce", "log4j", "critical", "2021"]
    )

    await kg.add_entity(cve_entity)

    log4j_entity = KnowledgeEntity(
        id="tool_log4j",
        name="Apache Log4j",
        entity_type=EntityType.TOOL,
        description="Java-based logging utility",
        properties={
            "type": "logging_library",
            "language": "java"
        },
        tags=["java", "logging", "apache"]
    )

    await kg.add_entity(log4j_entity)

    # Add relation
    relation = KnowledgeRelation(
        id="vuln_affects_tool",
        source_id=cve_entity.id,
        target_id=log4j_entity.id,
        relation_type=RelationType.TARGETS,
        confidence=1.0
    )

    await kg.add_relation(relation)

    # Extract knowledge from text
    sample_text = """
    The Log4Shell vulnerability (CVE-2021-44228) affects Apache Log4j2 versions
    2.0-beta9 through 2.15.0. Attackers can exploit this vulnerability through
    LDAP and other JNDI related endpoints. Organizations should implement
    network segmentation and update to version 2.17.1 or later.
    """

    print("📄 Extracting knowledge from text...")
    extracted_ids = await kg.extract_and_add_knowledge(sample_text, "example_text")
    print(f"Extracted {len(extracted_ids)} entities")

    # Perform semantic search
    print("\n🔍 Semantic Search Examples:")

    search_queries = [
        "Apache logging vulnerabilities",
        "remote code execution CVE",
        "Log4j security issues"
    ]

    for query_text in search_queries:
        print(f"\nQuery: '{query_text}'")

        query = SemanticQuery(
            query_text=query_text,
            max_results=3,
            similarity_threshold=0.5
        )

        results = await kg.semantic_search(query)

        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.entity.name} ({result.similarity_score:.2f})")
            print(f"     {result.entity.description[:100]}...")
            if result.related_entities:
                print(f"     Related: {len(result.related_entities)} entities")

    # Show statistics
    print(f"\n📊 Knowledge Graph Statistics:")
    stats = kg.get_graph_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())