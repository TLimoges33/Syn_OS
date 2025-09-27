#!/usr/bin/env python3
"""
SynOS RAG (Retrieval-Augmented Generation) Architecture
ChromaDB/FAISS integration for contextual information retrieval and AI assistance
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import hashlib

import numpy as np
import chromadb
from chromadb.config import Settings
import faiss
from sentence_transformers import SentenceTransformer
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class DocumentType(Enum):
    SECURITY_REPORT = "security_report"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    INCIDENT_RESPONSE = "incident_response"
    THREAT_INTELLIGENCE = "threat_intelligence"
    PENETRATION_TEST = "penetration_test"
    SECURITY_POLICY = "security_policy"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    KNOWLEDGE_ARTICLE = "knowledge_article"
    CHAT_HISTORY = "chat_history"
    SYSTEM_LOG = "system_log"


class RetrievalStrategy(Enum):
    SEMANTIC_SIMILARITY = "semantic_similarity"
    HYBRID_SEARCH = "hybrid_search"
    CONTEXTUAL_RANKING = "contextual_ranking"
    TEMPORAL_RELEVANCE = "temporal_relevance"
    KNOWLEDGE_GRAPH_ENHANCED = "knowledge_graph_enhanced"


@dataclass
class DocumentChunk:
    id: str
    content: str
    metadata: Dict[str, Any]
    document_type: DocumentType
    source: str
    chunk_index: int
    total_chunks: int
    embedding: Optional[np.ndarray] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0


@dataclass
class RetrievalQuery:
    query_text: str
    query_embedding: Optional[np.ndarray] = None
    context: Dict[str, Any] = field(default_factory=dict)
    document_types: Optional[List[DocumentType]] = None
    max_results: int = 5
    similarity_threshold: float = 0.7
    strategy: RetrievalStrategy = RetrievalStrategy.SEMANTIC_SIMILARITY
    temporal_weight: float = 0.1
    recency_bias: bool = True


@dataclass
class RetrievalResult:
    chunk: DocumentChunk
    similarity_score: float
    relevance_score: float
    rank: int
    explanation: str = ""


@dataclass
class RAGResponse:
    query: str
    retrieved_chunks: List[RetrievalResult]
    generated_response: str
    confidence: float
    context_used: List[str]
    sources: List[str]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)


class ChromaDBManager:
    """Manage ChromaDB for vector storage and retrieval"""

    def __init__(self, persist_directory: str = "/var/lib/synos/chromadb"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.persist_directory),
                anonymized_telemetry=False
            )
        )

        # Collection for security documents
        self.security_collection = self.client.get_or_create_collection(
            name="security_documents",
            metadata={"description": "Security-focused document chunks for RAG"}
        )

        # Collection for chat history
        self.chat_collection = self.client.get_or_create_collection(
            name="chat_history",
            metadata={"description": "Conversation history for context"}
        )

        logging.info(f"ChromaDB initialized at {self.persist_directory}")

    def add_documents(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to ChromaDB"""
        try:
            # Prepare data for ChromaDB
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.content for chunk in chunks]
            metadatas = []

            for chunk in chunks:
                metadata = chunk.metadata.copy()
                metadata.update({
                    'document_type': chunk.document_type.value,
                    'source': chunk.source,
                    'chunk_index': chunk.chunk_index,
                    'total_chunks': chunk.total_chunks,
                    'created_at': chunk.created_at.isoformat(),
                    'access_count': chunk.access_count
                })
                metadatas.append(metadata)

            # Add to collection
            collection = self._get_collection_for_type(chunks[0].document_type)
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            logging.info(f"Added {len(chunks)} chunks to ChromaDB")
            return True

        except Exception as e:
            logging.error(f"Failed to add documents to ChromaDB: {e}")
            return False

    def query_documents(self, query_text: str, n_results: int = 5,
                       document_types: Optional[List[DocumentType]] = None,
                       where_filter: Optional[Dict[str, Any]] = None) -> List[Tuple[str, str, float, Dict[str, Any]]]:
        """Query documents from ChromaDB"""
        try:
            # Build where filter
            where = where_filter or {}
            if document_types:
                where["document_type"] = {"$in": [dt.value for dt in document_types]}

            # Query primary collection
            results = self.security_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where if where else None
            )

            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    chunk_id = results['ids'][0][i]
                    content = results['documents'][0][i]
                    distance = results['distances'][0][i] if results['distances'] else [0.5][i]
                    metadata = results['metadatas'][0][i] if results['metadatas'] else [{}][i]

                    # Convert distance to similarity score
                    similarity = 1.0 - distance

                    formatted_results.append((chunk_id, content, similarity, metadata))

            return formatted_results

        except Exception as e:
            logging.error(f"Failed to query ChromaDB: {e}")
            return []

    def _get_collection_for_type(self, document_type: DocumentType):
        """Get appropriate collection for document type"""
        if document_type == DocumentType.CHAT_HISTORY:
            return self.chat_collection
        else:
            return self.security_collection

    def update_access_stats(self, chunk_ids: List[str]):
        """Update access statistics for chunks"""
        try:
            for chunk_id in chunk_ids:
                # ChromaDB doesn't support in-place updates easily
                # We'll track this in our metadata layer
                pass
        except Exception as e:
            logging.debug(f"Failed to update access stats: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            security_count = self.security_collection.count()
            chat_count = self.chat_collection.count()

            return {
                "security_documents": security_count,
                "chat_history": chat_count,
                "total_documents": security_count + chat_count
            }
        except Exception as e:
            logging.error(f"Failed to get collection stats: {e}")
            return {}


class DocumentProcessor:
    """Process and chunk documents for RAG system"""

    def __init__(self):
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Security-specific document patterns
        self.security_patterns = {
            'cve_pattern': r'CVE-\d{4}-\d{4,}',
            'cwe_pattern': r'CWE-\d+',
            'mitre_technique': r'T\d{4}(?:\.\d{3})?',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'hash_pattern': r'\b[a-fA-F0-9]{32,64}\b'
        }

    async def process_document(self, content: str, source: str,
                             document_type: DocumentType,
                             metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Process document into chunks with embeddings"""

        if not content.strip():
            return []

        # Create base metadata
        base_metadata = metadata or {}
        base_metadata.update({
            'processed_at': datetime.now().isoformat(),
            'content_length': len(content),
            'security_indicators': self._extract_security_indicators(content)
        })

        # Split document into chunks
        text_chunks = self.text_splitter.split_text(content)

        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_id = self._generate_chunk_id(source, i, chunk_text)

            # Generate embedding
            embedding = await self._generate_embedding(chunk_text)

            # Create chunk metadata
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                'chunk_summary': chunk_text[:100] + "..." if len(chunk_text) > 100 else chunk_text,
                'word_count': len(chunk_text.split()),
                'security_score': self._calculate_security_score(chunk_text)
            })

            chunk = DocumentChunk(
                id=chunk_id,
                content=chunk_text,
                metadata=chunk_metadata,
                document_type=document_type,
                source=source,
                chunk_index=i,
                total_chunks=len(text_chunks),
                embedding=embedding
            )

            chunks.append(chunk)

        logging.info(f"Processed document into {len(chunks)} chunks")
        return chunks

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text chunk"""
        try:
            # Clean text for embedding
            clean_text = self._clean_text_for_embedding(text)

            # Generate embedding
            embedding = await asyncio.to_thread(
                self.embedding_model.encode,
                clean_text,
                normalize_embeddings=True
            )

            return embedding.astype(np.float32)

        except Exception as e:
            logging.debug(f"Failed to generate embedding: {e}")
            # Return zero embedding as fallback
            return np.zeros(384, dtype=np.float32)

    def _clean_text_for_embedding(self, text: str) -> str:
        """Clean text for optimal embedding generation"""
        # Remove excessive whitespace
        cleaned = ' '.join(text.split())

        # Truncate if too long (models have token limits)
        if len(cleaned) > 8000:  # Conservative limit
            cleaned = cleaned[:8000] + "..."

        return cleaned

    def _extract_security_indicators(self, content: str) -> Dict[str, List[str]]:
        """Extract security-specific indicators from content"""
        import re
        indicators = {}

        for pattern_name, pattern in self.security_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                indicators[pattern_name] = list(set(matches))  # Remove duplicates

        return indicators

    def _calculate_security_score(self, text: str) -> float:
        """Calculate security relevance score for text chunk"""
        security_keywords = [
            'vulnerability', 'exploit', 'malware', 'attack', 'breach', 'security',
            'threat', 'risk', 'incident', 'penetration', 'assessment', 'audit',
            'firewall', 'encryption', 'authentication', 'authorization', 'compliance'
        ]

        text_lower = text.lower()
        keyword_count = sum(1 for keyword in security_keywords if keyword in text_lower)

        # Normalize score
        score = min(keyword_count / len(security_keywords), 1.0)

        # Boost score for specific indicators
        if any(pattern in text for pattern in ['CVE-', 'CWE-', 'MITRE']):
            score += 0.2

        return min(score, 1.0)

    def _generate_chunk_id(self, source: str, index: int, content: str) -> str:
        """Generate unique chunk ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        return f"chunk_{source_hash}_{index:04d}_{content_hash}"


class RetrievalEngine:
    """Advanced retrieval engine with multiple strategies"""

    def __init__(self, chromadb_manager: ChromaDBManager):
        self.chromadb_manager = chromadb_manager
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    async def retrieve(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieve relevant chunks using specified strategy"""

        # Generate query embedding if not provided
        if query.query_embedding is None:
            query.query_embedding = await self._generate_query_embedding(query.query_text)

        # Execute retrieval based on strategy
        if query.strategy == RetrievalStrategy.SEMANTIC_SIMILARITY:
            results = await self._semantic_similarity_retrieval(query)
        elif query.strategy == RetrievalStrategy.HYBRID_SEARCH:
            results = await self._hybrid_search_retrieval(query)
        elif query.strategy == RetrievalStrategy.CONTEXTUAL_RANKING:
            results = await self._contextual_ranking_retrieval(query)
        elif query.strategy == RetrievalStrategy.TEMPORAL_RELEVANCE:
            results = await self._temporal_relevance_retrieval(query)
        else:
            results = await self._semantic_similarity_retrieval(query)

        # Post-process results
        results = await self._post_process_results(results, query)

        return results

    async def _semantic_similarity_retrieval(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Basic semantic similarity retrieval"""
        raw_results = self.chromadb_manager.query_documents(
            query_text=query.query_text,
            n_results=query.max_results * 2,  # Get more candidates
            document_types=query.document_types
        )

        results = []
        for i, (chunk_id, content, similarity, metadata) in enumerate(raw_results):
            if similarity >= query.similarity_threshold:
                chunk = DocumentChunk(
                    id=chunk_id,
                    content=content,
                    metadata=metadata,
                    document_type=DocumentType(metadata.get('document_type', 'knowledge_article')),
                    source=metadata.get('source', ''),
                    chunk_index=metadata.get('chunk_index', 0),
                    total_chunks=metadata.get('total_chunks', 1)
                )

                result = RetrievalResult(
                    chunk=chunk,
                    similarity_score=similarity,
                    relevance_score=similarity,
                    rank=i + 1,
                    explanation=f"Semantic similarity: {similarity:.3f}"
                )

                results.append(result)

        return results[:query.max_results]

    async def _hybrid_search_retrieval(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Combine semantic similarity with keyword matching"""
        # Get semantic similarity results
        semantic_results = await self._semantic_similarity_retrieval(query)

        # Enhance with keyword-based scoring
        query_terms = set(query.query_text.lower().split())

        for result in semantic_results:
            content_terms = set(result.chunk.content.lower().split())
            keyword_overlap = len(query_terms.intersection(content_terms))
            keyword_score = keyword_overlap / len(query_terms) if query_terms else 0

            # Combine scores
            result.relevance_score = (
                result.similarity_score * 0.7 +
                keyword_score * 0.3
            )

            result.explanation += f" | Keyword match: {keyword_score:.3f}"

        # Re-rank by combined relevance score
        semantic_results.sort(key=lambda x: x.relevance_score, reverse=True)

        return semantic_results

    async def _contextual_ranking_retrieval(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieval with contextual ranking based on user context"""
        base_results = await self._hybrid_search_retrieval(query)

        # Apply contextual boosting
        for result in base_results:
            context_boost = self._calculate_context_boost(result.chunk, query.context)
            result.relevance_score = (
                result.relevance_score * 0.8 +
                context_boost * 0.2
            )

            if context_boost > 0:
                result.explanation += f" | Context boost: {context_boost:.3f}"

        # Re-rank
        base_results.sort(key=lambda x: x.relevance_score, reverse=True)

        return base_results

    async def _temporal_relevance_retrieval(self, query: RetrievalQuery) -> List[RetrievalResult]:
        """Retrieval with temporal relevance weighting"""
        base_results = await self._contextual_ranking_retrieval(query)

        # Apply temporal weighting
        now = datetime.now()

        for result in base_results:
            created_at_str = result.chunk.metadata.get('created_at')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    age_days = (now - created_at).days

                    # Exponential decay for age (newer is better)
                    temporal_factor = np.exp(-age_days / 30.0)  # 30-day half-life

                    if query.recency_bias:
                        result.relevance_score = (
                            result.relevance_score * (1 - query.temporal_weight) +
                            temporal_factor * query.temporal_weight
                        )

                        result.explanation += f" | Temporal: {temporal_factor:.3f}"

                except ValueError:
                    pass  # Skip invalid timestamps

        # Re-rank
        base_results.sort(key=lambda x: x.relevance_score, reverse=True)

        return base_results

    def _calculate_context_boost(self, chunk: DocumentChunk, context: Dict[str, Any]) -> float:
        """Calculate context-based relevance boost"""
        boost = 0.0

        # Check for matching document type context
        if 'preferred_document_types' in context:
            preferred_types = context['preferred_document_types']
            if chunk.document_type.value in preferred_types:
                boost += 0.3

        # Check for matching source context
        if 'preferred_sources' in context:
            preferred_sources = context['preferred_sources']
            if any(source in chunk.source for source in preferred_sources):
                boost += 0.2

        # Check for security focus
        if context.get('security_focus'):
            security_score = chunk.metadata.get('security_score', 0)
            boost += security_score * 0.3

        # Check for recent activity context
        if context.get('recent_activity'):
            last_accessed = chunk.last_accessed
            if last_accessed and (datetime.now() - last_accessed).days < 7:
                boost += 0.2

        return min(boost, 1.0)

    async def _post_process_results(self, results: List[RetrievalResult], query: RetrievalQuery) -> List[RetrievalResult]:
        """Post-process retrieval results"""
        # Remove duplicates based on content similarity
        unique_results = self._remove_similar_duplicates(results)

        # Update access statistics
        chunk_ids = [result.chunk.id for result in unique_results]
        self.chromadb_manager.update_access_stats(chunk_ids)

        # Update chunk access info
        for result in unique_results:
            result.chunk.last_accessed = datetime.now()
            result.chunk.access_count += 1

        return unique_results

    def _remove_similar_duplicates(self, results: List[RetrievalResult], similarity_threshold: float = 0.9) -> List[RetrievalResult]:
        """Remove results with very similar content"""
        if len(results) <= 1:
            return results

        unique_results = []

        for result in results:
            is_duplicate = False

            for existing in unique_results:
                # Simple content similarity check
                content_similarity = self._calculate_content_similarity(
                    result.chunk.content,
                    existing.chunk.content
                )

                if content_similarity > similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_results.append(result)

        return unique_results

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate simple content similarity"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    async def _generate_query_embedding(self, query_text: str) -> np.ndarray:
        """Generate embedding for query text"""
        try:
            embedding = await asyncio.to_thread(
                self.embedding_model.encode,
                query_text,
                normalize_embeddings=True
            )
            return embedding.astype(np.float32)
        except Exception as e:
            logging.error(f"Failed to generate query embedding: {e}")
            return np.zeros(384, dtype=np.float32)


class RAGOrchestrator:
    """Main RAG system orchestrator"""

    def __init__(self,
                 chromadb_path: str = "/var/lib/synos/chromadb",
                 knowledge_graph = None):  # Optional integration with knowledge graph

        # Initialize components
        self.chromadb_manager = ChromaDBManager(chromadb_path)
        self.document_processor = DocumentProcessor()
        self.retrieval_engine = RetrievalEngine(self.chromadb_manager)
        self.knowledge_graph = knowledge_graph

        # Processing queue for documents
        self.processing_queue = asyncio.Queue()
        self.is_processing = False

        # Statistics
        self.stats = {
            'documents_processed': 0,
            'chunks_created': 0,
            'queries_served': 0,
            'last_updated': datetime.now()
        }

    async def add_document(self, content: str, source: str,
                          document_type: DocumentType = DocumentType.TECHNICAL_DOCUMENTATION,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add document to RAG system"""

        try:
            # Process document into chunks
            chunks = await self.document_processor.process_document(
                content, source, document_type, metadata
            )

            if not chunks:
                logging.warning(f"No chunks generated for document: {source}")
                return False

            # Add chunks to ChromaDB
            success = self.chromadb_manager.add_documents(chunks)

            if success:
                # Optionally add to knowledge graph
                if self.knowledge_graph:
                    await self._sync_with_knowledge_graph(chunks)

                # Update statistics
                self.stats['documents_processed'] += 1
                self.stats['chunks_created'] += len(chunks)
                self.stats['last_updated'] = datetime.now()

                logging.info(f"Successfully added document: {source} ({len(chunks)} chunks)")
                return True

            return False

        except Exception as e:
            logging.error(f"Failed to add document {source}: {e}")
            return False

    async def query(self, query_text: str,
                   document_types: Optional[List[DocumentType]] = None,
                   max_results: int = 5,
                   strategy: RetrievalStrategy = RetrievalStrategy.HYBRID_SEARCH,
                   context: Optional[Dict[str, Any]] = None) -> List[RetrievalResult]:
        """Query RAG system for relevant information"""

        start_time = time.time()

        try:
            # Create retrieval query
            retrieval_query = RetrievalQuery(
                query_text=query_text,
                document_types=document_types,
                max_results=max_results,
                strategy=strategy,
                context=context or {}
            )

            # Retrieve relevant chunks
            results = await self.retrieval_engine.retrieve(retrieval_query)

            # Update statistics
            self.stats['queries_served'] += 1
            processing_time = time.time() - start_time

            logging.info(f"Query processed in {processing_time:.3f}s, returned {len(results)} results")

            return results

        except Exception as e:
            logging.error(f"Query failed: {e}")
            return []

    async def generate_response(self, query_text: str,
                              llm_engine=None,
                              context: Optional[Dict[str, Any]] = None) -> RAGResponse:
        """Generate AI response using retrieved context"""

        start_time = time.time()

        # Retrieve relevant context
        retrieval_results = await self.query(
            query_text,
            strategy=RetrievalStrategy.CONTEXTUAL_RANKING,
            context=context
        )

        # Prepare context for LLM
        context_chunks = []
        sources = []

        for result in retrieval_results:
            context_chunks.append(result.chunk.content)
            sources.append(result.chunk.source)

        # Generate response using LLM if available
        if llm_engine:
            try:
                # Create contextualized prompt
                context_text = "\n\n".join(context_chunks)

                enhanced_prompt = f"""Based on the following context information, please answer the question.

Context:
{context_text}

Question: {query_text}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain sufficient information, please indicate that clearly."""

                # Generate response (assuming llm_engine has a generate_response method)
                if hasattr(llm_engine, 'generate_response'):
                    session_id = llm_engine.create_chat_session("RAG Query Response")
                    generated_response = await llm_engine.generate_response(session_id, enhanced_prompt)
                else:
                    generated_response = "LLM integration not available"

                confidence = 0.8  # Could be calculated based on retrieval scores

            except Exception as e:
                logging.error(f"LLM generation failed: {e}")
                generated_response = "Error generating response with LLM"
                confidence = 0.0
        else:
            # Fallback: summarize retrieved context
            if context_chunks:
                generated_response = f"Based on the retrieved information:\n\n" + "\n\n".join(context_chunks[:2])
                confidence = 0.6
            else:
                generated_response = "No relevant information found in the knowledge base."
                confidence = 0.0

        processing_time = time.time() - start_time

        return RAGResponse(
            query=query_text,
            retrieved_chunks=retrieval_results,
            generated_response=generated_response,
            confidence=confidence,
            context_used=context_chunks,
            sources=list(set(sources)),  # Remove duplicates
            processing_time=processing_time
        )

    async def _sync_with_knowledge_graph(self, chunks: List[DocumentChunk]):
        """Sync document chunks with knowledge graph"""
        try:
            if self.knowledge_graph and hasattr(self.knowledge_graph, 'extract_and_add_knowledge'):
                for chunk in chunks:
                    if chunk.metadata.get('security_score', 0) > 0.5:  # Only sync security-relevant content
                        await self.knowledge_graph.extract_and_add_knowledge(
                            chunk.content,
                            f"rag_chunk:{chunk.source}"
                        )
        except Exception as e:
            logging.debug(f"Knowledge graph sync failed: {e}")

    def get_system_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        chromadb_stats = self.chromadb_manager.get_collection_stats()

        return {
            **self.stats,
            **chromadb_stats,
            'avg_chunks_per_document': (
                self.stats['chunks_created'] / max(self.stats['documents_processed'], 1)
            )
        }

    async def batch_import_directory(self, directory_path: Path,
                                   file_extensions: List[str] = ['.txt', '.md', '.json'],
                                   document_type: DocumentType = DocumentType.TECHNICAL_DOCUMENTATION) -> Dict[str, Any]:
        """Batch import documents from directory"""

        import_stats = {
            'processed': 0,
            'failed': 0,
            'total_chunks': 0,
            'errors': []
        }

        if not directory_path.exists() or not directory_path.is_dir():
            return {'error': f'Directory not found: {directory_path}'}

        # Find all matching files
        files_to_process = []
        for ext in file_extensions:
            files_to_process.extend(directory_path.rglob(f'*{ext}'))

        logging.info(f"Found {len(files_to_process)} files to import from {directory_path}")

        # Process files
        for file_path in files_to_process:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                success = await self.add_document(
                    content=content,
                    source=str(file_path),
                    document_type=document_type,
                    metadata={
                        'file_name': file_path.name,
                        'file_size': file_path.stat().st_size,
                        'import_batch': datetime.now().isoformat()
                    }
                )

                if success:
                    import_stats['processed'] += 1
                    # Estimate chunks (rough approximation)
                    import_stats['total_chunks'] += len(content) // 1000
                else:
                    import_stats['failed'] += 1

            except Exception as e:
                import_stats['failed'] += 1
                import_stats['errors'].append(f"{file_path.name}: {str(e)}")
                logging.error(f"Failed to import {file_path}: {e}")

        logging.info(f"Batch import complete: {import_stats['processed']} successful, {import_stats['failed']} failed")
        return import_stats


async def main():
    """Example usage of RAG Architecture"""
    logging.basicConfig(level=logging.INFO)

    # Initialize RAG system
    rag = RAGOrchestrator()

    print("🔍 SynOS RAG (Retrieval-Augmented Generation) Architecture")
    print("=" * 60)

    # Add sample security documents
    sample_docs = [
        {
            'content': """
            CVE-2021-44228 (Log4Shell) is a critical vulnerability in Apache Log4j2.
            This vulnerability allows remote code execution through LDAP lookups.
            Organizations should immediately update to version 2.17.1 or later.
            Mitigation includes setting log4j2.formatMsgNoLookups=true.
            """,
            'source': 'security_advisory_log4j.txt',
            'type': DocumentType.SECURITY_REPORT
        },
        {
            'content': """
            Network segmentation is a critical security control that isolates
            different parts of a network to limit the scope of potential breaches.
            Best practices include using VLANs, firewalls, and access control lists.
            Regular network assessments should verify segmentation effectiveness.
            """,
            'source': 'network_security_guide.md',
            'type': DocumentType.SECURITY_POLICY
        },
        {
            'content': """
            Incident Response Plan Phase 1: Preparation
            - Establish incident response team
            - Develop communication procedures
            - Create forensic imaging capabilities
            - Maintain updated contact lists
            Phase 2: Detection and Analysis
            - Monitor security events continuously
            - Classify incident severity levels
            - Document all findings thoroughly
            """,
            'source': 'incident_response_playbook.txt',
            'type': DocumentType.INCIDENT_RESPONSE
        }
    ]

    # Add documents to RAG system
    print("📄 Adding sample documents...")
    for doc in sample_docs:
        success = await rag.add_document(
            content=doc['content'],
            source=doc['source'],
            document_type=doc['type']
        )
        print(f"  {'✅' if success else '❌'} {doc['source']}")

    # Test queries
    test_queries = [
        "How to fix Log4j vulnerability?",
        "What is network segmentation?",
        "Incident response procedures for security breaches",
        "CVE-2021-44228 mitigation steps"
    ]

    print(f"\n🔍 Testing RAG Queries:")
    for query in test_queries:
        print(f"\nQuery: '{query}'")

        results = await rag.query(
            query_text=query,
            strategy=RetrievalStrategy.HYBRID_SEARCH,
            max_results=3
        )

        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.chunk.source} (Score: {result.relevance_score:.3f})")
            print(f"     {result.chunk.content[:150]}...")
            print(f"     {result.explanation}")

    # Show system statistics
    stats = rag.get_system_stats()
    print(f"\n📊 RAG System Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print(f"\n✅ RAG Architecture ready for integration with LLM systems!")


if __name__ == "__main__":
    asyncio.run(main())