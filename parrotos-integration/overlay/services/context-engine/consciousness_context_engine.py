#!/usr/bin/env python3
"""
SynapticOS Personal Context Engine
Advanced semantic search with consciousness enhancement
"""

import asyncio
import json
import logging
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import sqlite3

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('context-engine')

@dataclass
class ContextItem:
    """Individual context item with consciousness enhancement"""
    id: str
    content: str
    source: str
    timestamp: str
    consciousness_score: float
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None

@dataclass
class SearchResult:
    """Enhanced search result with consciousness relevance"""
    item: ContextItem
    relevance_score: float
    consciousness_relevance: float
    combined_score: float

class ConsciousnessContextEngine:
    """Advanced context engine with consciousness integration"""
    
    def __init__(self, data_dir: str = "/app/data/context"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index
        self.dimension = 384  # MiniLM embedding dimension
        self.faiss_index = faiss.IndexFlatIP(self.dimension)
        
        # Initialize SQLite for metadata
        self.db_path = self.data_dir / "context.db"
        self.init_database()
        
        # Context storage
        self.context_items: Dict[str, ContextItem] = {}
        
        logger.info("Consciousness Context Engine initialized")
    
    def init_database(self):
        """Initialize SQLite database for context metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_items (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    source TEXT,
                    timestamp TEXT,
                    consciousness_score REAL,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consciousness_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_data TEXT,
                    effectiveness_score REAL,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT
                )
            """)
            conn.commit()
    
    async def add_context(self, content: str, source: str, consciousness_score: float = 0.5, metadata: Dict = None):
        """Add content to context engine with consciousness enhancement"""
        try:
            # Generate unique ID
            item_id = hashlib.md5(f"{content}{source}{datetime.now().isoformat()}".encode()).hexdigest()
            
            # Generate embedding
            embedding = self.embedding_model.encode(content)
            
            # Create context item
            context_item = ContextItem(
                id=item_id,
                content=content,
                source=source,
                timestamp=datetime.now().isoformat(),
                consciousness_score=consciousness_score,
                embedding=embedding.tolist(),
                metadata=metadata or {}
            )
            
            # Store in memory
            self.context_items[item_id] = context_item
            
            # Add to FAISS index
            self.faiss_index.add(np.array([embedding]))
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO context_items (id, content, source, timestamp, consciousness_score, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (item_id, content, source, context_item.timestamp, consciousness_score, json.dumps(metadata or {})))
                conn.commit()
            
            logger.info(f"Added context item {item_id} from {source}")
            return item_id
            
        except Exception as e:
            logger.error(f"Failed to add context: {e}")
            return None
    
    async def semantic_search(self, query: str, consciousness_context: Dict = None, top_k: int = 10) -> List[SearchResult]:
        """Perform semantic search with consciousness enhancement"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search FAISS index
            scores, indices = self.faiss_index.search(np.array([query_embedding]), top_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # No more results
                    break
                    
                # Get context item by index (this is simplified - in production, maintain ID mapping)
                item_list = list(self.context_items.values())
                if idx < len(item_list):
                    item = item_list[idx]
                    
                    # Calculate consciousness relevance
                    consciousness_relevance = self._calculate_consciousness_relevance(
                        item, consciousness_context or {}
                    )
                    
                    # Combined score (semantic + consciousness)
                    combined_score = (score * 0.7) + (consciousness_relevance * 0.3)
                    
                    results.append(SearchResult(
                        item=item,
                        relevance_score=float(score),
                        consciousness_relevance=consciousness_relevance,
                        combined_score=combined_score
                    ))
            
            # Sort by combined score
            results.sort(key=lambda x: x.combined_score, reverse=True)
            
            logger.info(f"Semantic search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def _calculate_consciousness_relevance(self, item: ContextItem, consciousness_context: Dict) -> float:
        """Calculate consciousness relevance score"""
        try:
            base_score = item.consciousness_score
            
            # Enhance based on consciousness context
            if consciousness_context:
                level = consciousness_context.get('level', 0.5)
                learning_rate = consciousness_context.get('learning_rate', 0.5)
                adaptation_factor = consciousness_context.get('adaptation_factor', 0.5)
                
                # Simple consciousness relevance calculation
                context_boost = (level + learning_rate + adaptation_factor) / 3
                enhanced_score = base_score * (1 + context_boost * 0.5)
                
                return min(enhanced_score, 1.0)
            
            return base_score
            
        except Exception as e:
            logger.error(f"Consciousness relevance calculation failed: {e}")
            return item.consciousness_score
    
    async def add_web_content(self, url: str, consciousness_score: float = 0.5):
        """Add web content to context engine"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Simple content extraction (in production, use proper HTML parsing)
                        clean_content = content[:2000]  # Truncate for demo
                        
                        return await self.add_context(
                            content=clean_content,
                            source=f"web:{url}",
                            consciousness_score=consciousness_score,
                            metadata={"url": url, "status": response.status}
                        )
        except Exception as e:
            logger.error(f"Failed to add web content from {url}: {e}")
            return None
    
    async def add_file_content(self, file_path: str, consciousness_score: float = 0.5):
        """Add file content to context engine"""
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                
                return await self.add_context(
                    content=content,
                    source=f"file:{file_path}",
                    consciousness_score=consciousness_score,
                    metadata={"file_path": file_path, "file_size": len(content)}
                )
        except Exception as e:
            logger.error(f"Failed to add file content from {file_path}: {e}")
            return None
    
    async def get_context_stats(self) -> Dict[str, Any]:
        """Get context engine statistics"""
        return {
            "total_items": len(self.context_items),
            "faiss_index_size": self.faiss_index.ntotal,
            "average_consciousness_score": sum(item.consciousness_score for item in self.context_items.values()) / len(self.context_items) if self.context_items else 0,
            "sources": list(set(item.source.split(':')[0] for item in self.context_items.values())),
            "data_directory": str(self.data_dir),
            "timestamp": datetime.now().isoformat()
        }

class ConsciousnessRAGEngine:
    """Retrieval-Augmented Generation with consciousness integration"""
    
    def __init__(self, context_engine: ConsciousnessContextEngine):
        self.context_engine = context_engine
        logger.info("Consciousness RAG Engine initialized")
    
    async def enhanced_query(self, query: str, consciousness_context: Dict = None, max_context_length: int = 2000) -> Dict[str, Any]:
        """Perform RAG query with consciousness enhancement"""
        try:
            # Get relevant context
            search_results = await self.context_engine.semantic_search(
                query, consciousness_context, top_k=5
            )
            
            # Build context string
            context_parts = []
            total_length = 0
            
            for result in search_results:
                content = result.item.content[:500]  # Truncate individual items
                if total_length + len(content) < max_context_length:
                    context_parts.append({
                        "content": content,
                        "source": result.item.source,
                        "relevance": result.combined_score
                    })
                    total_length += len(content)
                else:
                    break
            
            return {
                "query": query,
                "context": context_parts,
                "consciousness_enhancement": consciousness_context,
                "total_context_length": total_length,
                "num_sources": len(context_parts),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced RAG query failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

async def main():
    """Demo the consciousness context engine"""
    engine = ConsciousnessContextEngine()
    rag_engine = ConsciousnessRAGEngine(engine)
    
    # Add some sample content
    await engine.add_context(
        "Neural Darwinism is a theory of consciousness based on evolutionary principles",
        "academic_paper",
        consciousness_score=0.9,
        metadata={"topic": "consciousness", "domain": "neuroscience"}
    )
    
    await engine.add_context(
        "Machine learning algorithms can be enhanced with consciousness-aware processing",
        "research_note",
        consciousness_score=0.8,
        metadata={"topic": "ai", "domain": "computer_science"}
    )
    
    # Demo search
    consciousness_context = {
        "level": 0.7,
        "learning_rate": 0.6,
        "adaptation_factor": 0.8
    }
    
    results = await engine.semantic_search("consciousness theory", consciousness_context)
    
    print("Search Results:")
    for i, result in enumerate(results):
        print(f"{i+1}. Score: {result.combined_score:.3f} - {result.item.content[:100]}...")
    
    # Demo RAG
    rag_result = await rag_engine.enhanced_query("How does consciousness relate to AI?", consciousness_context)
    print(f"\nRAG Query Result: {rag_result}")
    
    # Get stats
    stats = await engine.get_context_stats()
    print(f"\nContext Engine Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
