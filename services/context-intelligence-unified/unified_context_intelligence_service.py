#!/usr/bin/env python3
"""
Syn_OS Unified Context Intelligence Service
Combined context engine + news intelligence for consciousness-enhanced information processing
Consolidates context-engine + news-intelligence functionality
"""

import asyncio
import json
import logging
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
import numpy as np
import sqlite3
from collections import defaultdict, Counter
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Advanced processing dependencies
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger = logging.getLogger('context-intelligence-unified')
    logger.warning("Sentence transformers not available, using simplified embeddings")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import feedparser
    from textblob import TextBlob
    import networkx as nx
    NLP_DEPENDENCIES_AVAILABLE = True
except ImportError:
    logger = logging.getLogger('context-intelligence-unified')
    logger.warning("NLP dependencies not available, using simplified processing")
    NLP_DEPENDENCIES_AVAILABLE = False

# Logging setup
log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'context-intelligence-unified.log')
    ]
)
logger = logging.getLogger('context-intelligence-unified')

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
class NewsArticle:
    """News article with consciousness analysis"""
    id: str
    title: str
    content: str
    url: str
    source: str
    published: str
    sentiment_score: float
    consciousness_relevance: float
    topics: List[str]
    entities: List[str]
    metadata: Dict[str, Any]

@dataclass
class SearchResult:
    """Enhanced search result with consciousness relevance"""
    item: ContextItem
    relevance_score: float
    consciousness_relevance: float
    combined_score: float

@dataclass
class NewsCluster:
    """Clustered news stories"""
    id: str
    main_topic: str
    articles: List[NewsArticle]
    sentiment_trend: str
    consciousness_insights: Dict[str, Any]
    timestamp: str

@dataclass
class IntelligenceInsight:
    """Combined intelligence insight from context and news"""
    id: str
    insight_type: str  # 'contextual', 'news_based', 'combined'
    content: str
    confidence_score: float
    consciousness_correlation: float
    sources: List[str]
    timestamp: str
    metadata: Dict[str, Any]

class UnifiedContextIntelligenceService:
    """Unified service combining context engine and news intelligence"""
    
    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Context engine components
        self.context_items = {}
        self.context_embeddings = None
        self.context_index = None
        
        # News intelligence components
        self.news_articles = {}
        self.news_clusters = {}
        self.news_sources = [
            'https://feeds.feedburner.com/oreilly/radar',
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.reuters.com/reuters/technologyNews',
            'https://feeds.bbci.co.uk/news/technology/rss.xml',
            'https://techcrunch.com/feed/'
        ]
        
        # Unified intelligence components
        self.intelligence_insights = {}
        self.consciousness_correlations = {}
        
        # Consciousness metrics
        self.consciousness_level = 0.5
        self.intelligence_accuracy = 0.8
        
        # WebSocket connections
        self.connected_clients = set()
        
        # Initialize components
        self.setup_databases()
        self.initialize_models()
        
    def setup_databases(self):
        """Initialize databases for context and news storage"""
        # Context database
        self.context_db_path = self.data_dir / 'context.db'
        with sqlite3.connect(self.context_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS context_items (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    consciousness_score REAL DEFAULT 0.5,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        
        # News database
        self.news_db_path = self.data_dir / 'news.db'
        with sqlite3.connect(self.news_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS news_articles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    published TEXT NOT NULL,
                    sentiment_score REAL DEFAULT 0.0,
                    consciousness_relevance REAL DEFAULT 0.5,
                    topics TEXT DEFAULT '[]',
                    entities TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS intelligence_insights (
                    id TEXT PRIMARY KEY,
                    insight_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.7,
                    consciousness_correlation REAL DEFAULT 0.5,
                    sources TEXT DEFAULT '[]',
                    timestamp TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def initialize_models(self):
        """Initialize ML models for semantic processing"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dimension = 384
                self.context_index = faiss.IndexFlatIP(self.embedding_dimension)
                logger.info("Sentence transformers initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize sentence transformers: {e}")
                self.sentence_model = None
        else:
            self.sentence_model = None
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate simple embedding when sentence transformers unavailable"""
        # Simple word-based embedding for fallback
        words = text.lower().split()
        embedding = [0.0] * 100  # Simple 100-dimension embedding
        
        for i, word in enumerate(words[:100]):
            embedding[i % 100] += hash(word) % 1000 / 1000.0
        
        # Normalize
        norm = sum(x*x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using available method"""
        if self.sentence_model and SENTENCE_TRANSFORMERS_AVAILABLE:
            return self.sentence_model.encode(text).tolist()
        else:
            return self._generate_simple_embedding(text)
    
    async def add_context_item(self, content: str, source: str, metadata: Dict[str, Any] = None) -> str:
        """Add new context item with consciousness enhancement"""
        item_id = hashlib.md5(f"{content}{source}{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Calculate consciousness score based on content complexity and relevance
        consciousness_score = self._calculate_consciousness_score(content, source)
        
        # Generate embedding
        embedding = self._get_embedding(content)
        
        # Create context item
        context_item = ContextItem(
            id=item_id,
            content=content,
            source=source,
            timestamp=datetime.now().isoformat(),
            consciousness_score=consciousness_score,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        # Store in memory
        self.context_items[item_id] = context_item
        
        # Update FAISS index if available
        if self.context_index and len(embedding) == self.embedding_dimension:
            self.context_index.add(np.array([embedding], dtype=np.float32))
        
        # Store in database
        with sqlite3.connect(self.context_db_path) as conn:
            conn.execute('''
                INSERT INTO context_items (id, content, source, timestamp, consciousness_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item_id, content, source, context_item.timestamp,
                consciousness_score, json.dumps(metadata or {})
            ))
            conn.commit()
        
        logger.info(f"Added context item {item_id} with consciousness score {consciousness_score:.2f}")
        return item_id
    
    def _calculate_consciousness_score(self, content: str, source: str) -> float:
        """Calculate consciousness enhancement score for content"""
        base_score = 0.5
        
        # Content complexity factor
        complexity_factor = min(len(content) / 1000.0, 1.0)  # Longer content gets higher score
        
        # Source reliability factor
        source_factors = {
            'academic': 0.9,
            'research': 0.85,
            'news': 0.7,
            'social': 0.5,
            'unknown': 0.3
        }
        
        source_type = 'unknown'
        for stype, score in source_factors.items():
            if stype in source.lower():
                source_type = stype
                break
        
        source_factor = source_factors[source_type]
        
        # Consciousness correlation (based on current system state)
        consciousness_factor = self.consciousness_level
        
        # Combine factors
        consciousness_score = (base_score + complexity_factor * 0.3 + source_factor * 0.4 + consciousness_factor * 0.3)
        return min(consciousness_score, 1.0)
    
    async def search_context(self, query: str, limit: int = 10, consciousness_threshold: float = 0.0) -> List[SearchResult]:
        """Search context with consciousness-enhanced relevance"""
        if not self.context_items:
            return []
        
        query_embedding = self._get_embedding(query)
        results = []
        
        for item in self.context_items.values():
            if item.consciousness_score < consciousness_threshold:
                continue
            
            # Calculate relevance score
            if item.embedding and len(item.embedding) == len(query_embedding):
                # Cosine similarity
                dot_product = sum(a * b for a, b in zip(query_embedding, item.embedding))
                norm_a = sum(a * a for a in query_embedding) ** 0.5
                norm_b = sum(b * b for b in item.embedding) ** 0.5
                relevance_score = dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0
            else:
                # Fallback to simple text matching
                relevance_score = len(set(query.lower().split()) & set(item.content.lower().split())) / len(set(query.lower().split()))
            
            # Calculate consciousness relevance
            consciousness_relevance = item.consciousness_score * self.consciousness_level
            
            # Combined score
            combined_score = (relevance_score * 0.7) + (consciousness_relevance * 0.3)
            
            results.append(SearchResult(
                item=item,
                relevance_score=relevance_score,
                consciousness_relevance=consciousness_relevance,
                combined_score=combined_score
            ))
        
        # Sort by combined score and return top results
        results.sort(key=lambda x: x.combined_score, reverse=True)
        return results[:limit]
    
    async def fetch_news_articles(self, max_articles: int = 50) -> List[NewsArticle]:
        """Fetch and process news articles from RSS feeds"""
        articles = []
        
        async with aiohttp.ClientSession() as session:
            for source_url in self.news_sources:
                try:
                    async with session.get(source_url) as response:
                        if response.status == 200:
                            feed_content = await response.text()
                            feed_articles = await self._process_feed(feed_content, source_url)
                            articles.extend(feed_articles)
                            
                            if len(articles) >= max_articles:
                                break
                                
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source_url}: {e}")
                    continue
        
        # Store articles
        for article in articles[:max_articles]:
            self.news_articles[article.id] = article
            await self._store_news_article(article)
        
        logger.info(f"Fetched {len(articles)} news articles")
        return articles[:max_articles]
    
    async def _process_feed(self, feed_content: str, source_url: str) -> List[NewsArticle]:
        """Process RSS feed content into NewsArticle objects"""
        articles = []
        
        if not NLP_DEPENDENCIES_AVAILABLE:
            logger.warning("NLP dependencies not available, using simplified news processing")
            return articles
        
        try:
            feed = feedparser.parse(feed_content)
            
            for entry in feed.entries:
                article_id = hashlib.md5(f"{entry.get('link', '')}{entry.get('published', '')}".encode()).hexdigest()
                
                # Extract content
                content = entry.get('summary', entry.get('description', ''))
                title = entry.get('title', '')
                
                # Sentiment analysis
                try:
                    blob = TextBlob(content)
                    sentiment_score = blob.sentiment.polarity
                except:
                    sentiment_score = 0.0
                
                # Calculate consciousness relevance
                consciousness_relevance = self._calculate_news_consciousness_relevance(title, content)
                
                # Extract topics and entities (simplified)
                topics = self._extract_topics(content)
                entities = self._extract_entities(content)
                
                article = NewsArticle(
                    id=article_id,
                    title=title,
                    content=content,
                    url=entry.get('link', ''),
                    source=source_url,
                    published=entry.get('published', datetime.now().isoformat()),
                    sentiment_score=sentiment_score,
                    consciousness_relevance=consciousness_relevance,
                    topics=topics,
                    entities=entities,
                    metadata={'feed_title': feed.feed.get('title', '')}
                )
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error processing feed: {e}")
        
        return articles
    
    def _calculate_news_consciousness_relevance(self, title: str, content: str) -> float:
        """Calculate consciousness relevance for news content"""
        consciousness_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'consciousness',
            'neural', 'cognitive', 'automation', 'technology', 'innovation',
            'cybersecurity', 'security', 'privacy', 'education', 'learning'
        ]
        
        text = (title + ' ' + content).lower()
        relevance_count = sum(1 for keyword in consciousness_keywords if keyword in text)
        
        # Normalize to 0-1 range
        max_relevance = len(consciousness_keywords)
        consciousness_relevance = min(relevance_count / max_relevance, 1.0)
        
        # Boost based on current consciousness level
        consciousness_relevance = min(consciousness_relevance * (1 + self.consciousness_level), 1.0)
        
        return consciousness_relevance
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content (simplified implementation)"""
        # Simple topic extraction based on keywords
        topic_keywords = {
            'technology': ['tech', 'software', 'hardware', 'digital', 'computer'],
            'ai': ['artificial intelligence', 'machine learning', 'neural', 'ai'],
            'security': ['security', 'cybersecurity', 'privacy', 'encryption', 'hack'],
            'business': ['business', 'economy', 'market', 'financial', 'company'],
            'education': ['education', 'learning', 'training', 'student', 'school'],
            'science': ['research', 'study', 'scientific', 'discovery', 'innovation']
        }
        
        content_lower = content.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:5]  # Limit to top 5 topics
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract entities from content (simplified implementation)"""
        # Simple entity extraction - in practice would use NER
        words = content.split()
        entities = []
        
        for word in words:
            # Simple heuristic: capitalized words might be entities
            if word.istitle() and len(word) > 3:
                entities.append(word)
        
        return list(set(entities))[:10]  # Unique entities, limit to 10
    
    async def _store_news_article(self, article: NewsArticle):
        """Store news article in database"""
        with sqlite3.connect(self.news_db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO news_articles 
                (id, title, content, url, source, published, sentiment_score, 
                 consciousness_relevance, topics, entities, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.id, article.title, article.content, article.url, article.source,
                article.published, article.sentiment_score, article.consciousness_relevance,
                json.dumps(article.topics), json.dumps(article.entities), 
                json.dumps(article.metadata)
            ))
            conn.commit()
    
    async def generate_intelligence_insights(self) -> List[IntelligenceInsight]:
        """Generate combined intelligence insights from context and news"""
        insights = []
        
        # Context-based insights
        context_insights = await self._generate_context_insights()
        insights.extend(context_insights)
        
        # News-based insights
        news_insights = await self._generate_news_insights()
        insights.extend(news_insights)
        
        # Combined insights
        combined_insights = await self._generate_combined_insights()
        insights.extend(combined_insights)
        
        # Store insights
        for insight in insights:
            self.intelligence_insights[insight.id] = insight
            await self._store_intelligence_insight(insight)
        
        logger.info(f"Generated {len(insights)} intelligence insights")
        return insights
    
    async def _generate_context_insights(self) -> List[IntelligenceInsight]:
        """Generate insights from context data"""
        insights = []
        
        if not self.context_items:
            return insights
        
        # Analyze context patterns
        source_distribution = defaultdict(int)
        consciousness_levels = []
        
        for item in self.context_items.values():
            source_distribution[item.source] += 1
            consciousness_levels.append(item.consciousness_score)
        
        # Generate insight about source diversity
        if len(source_distribution) > 1:
            insight_id = hashlib.md5(f"context_diversity_{datetime.now().isoformat()}".encode()).hexdigest()
            insight = IntelligenceInsight(
                id=insight_id,
                insight_type='contextual',
                content=f"Context diversity analysis: {len(source_distribution)} unique sources detected. "
                       f"Most active source: {max(source_distribution, key=source_distribution.get)}",
                confidence_score=0.8,
                consciousness_correlation=np.mean(consciousness_levels) if consciousness_levels else 0.5,
                sources=list(source_distribution.keys()),
                timestamp=datetime.now().isoformat(),
                metadata={'source_distribution': dict(source_distribution)}
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_news_insights(self) -> List[IntelligenceInsight]:
        """Generate insights from news data"""
        insights = []
        
        if not self.news_articles:
            return insights
        
        # Analyze sentiment trends
        sentiments = [article.sentiment_score for article in self.news_articles.values()]
        avg_sentiment = np.mean(sentiments) if sentiments else 0.0
        
        if sentiments:
            insight_id = hashlib.md5(f"news_sentiment_{datetime.now().isoformat()}".encode()).hexdigest()
            
            sentiment_trend = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
            
            insight = IntelligenceInsight(
                id=insight_id,
                insight_type='news_based',
                content=f"News sentiment analysis: Overall sentiment is {sentiment_trend} "
                       f"(score: {avg_sentiment:.2f}). Analyzed {len(sentiments)} articles.",
                confidence_score=0.75,
                consciousness_correlation=np.mean([a.consciousness_relevance for a in self.news_articles.values()]),
                sources=[article.source for article in list(self.news_articles.values())[:5]],
                timestamp=datetime.now().isoformat(),
                metadata={'sentiment_distribution': {'avg': avg_sentiment, 'count': len(sentiments)}}
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_combined_insights(self) -> List[IntelligenceInsight]:
        """Generate insights combining context and news data"""
        insights = []
        
        if not self.context_items or not self.news_articles:
            return insights
        
        # Find correlations between context and news topics
        context_topics = set()
        for item in self.context_items.values():
            # Extract topics from context content (simplified)
            words = item.content.lower().split()
            context_topics.update(word for word in words if len(word) > 4)
        
        news_topics = set()
        for article in self.news_articles.values():
            news_topics.update(topic.lower() for topic in article.topics)
        
        # Find overlapping topics
        overlapping_topics = context_topics & news_topics
        
        if overlapping_topics:
            insight_id = hashlib.md5(f"combined_correlation_{datetime.now().isoformat()}".encode()).hexdigest()
            
            insight = IntelligenceInsight(
                id=insight_id,
                insight_type='combined',
                content=f"Context-News correlation analysis: {len(overlapping_topics)} common themes detected. "
                       f"Top correlations: {list(overlapping_topics)[:5]}",
                confidence_score=0.7,
                consciousness_correlation=(self.consciousness_level + self.intelligence_accuracy) / 2,
                sources=['context_engine', 'news_intelligence'],
                timestamp=datetime.now().isoformat(),
                metadata={
                    'overlapping_topics': list(overlapping_topics),
                    'context_topic_count': len(context_topics),
                    'news_topic_count': len(news_topics)
                }
            )
            insights.append(insight)
        
        return insights
    
    async def _store_intelligence_insight(self, insight: IntelligenceInsight):
        """Store intelligence insight in database"""
        with sqlite3.connect(self.news_db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO intelligence_insights 
                (id, insight_type, content, confidence_score, consciousness_correlation, 
                 sources, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.id, insight.insight_type, insight.content, insight.confidence_score,
                insight.consciousness_correlation, json.dumps(insight.sources), 
                insight.timestamp, json.dumps(insight.metadata)
            ))
            conn.commit()
    
    async def start_background_processing(self):
        """Start background processing tasks"""
        asyncio.create_task(self._periodic_news_update())
        asyncio.create_task(self._periodic_insight_generation())
        logger.info("Background processing started")
    
    async def _periodic_news_update(self):
        """Periodically fetch new news articles"""
        while True:
            try:
                await self.fetch_news_articles(25)
                await asyncio.sleep(3600)  # Update every hour
            except Exception as e:
                logger.error(f"Error in periodic news update: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def _periodic_insight_generation(self):
        """Periodically generate new intelligence insights"""
        while True:
            try:
                await asyncio.sleep(1800)  # Generate every 30 minutes
                await self.generate_intelligence_insights()
            except Exception as e:
                logger.error(f"Error in periodic insight generation: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def _broadcast_update(self, update_type: str, data: Any):
        """Broadcast updates to connected WebSocket clients"""
        if not self.connected_clients:
            return
        
        update_message = {
            'type': update_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        disconnected_clients = set()
        for client in self.connected_clients.copy():
            try:
                await client.send_text(json.dumps(update_message, default=str))
            except Exception as e:
                logger.warning(f"Failed to send update to client: {e}")
                disconnected_clients.add(client)
        
        self.connected_clients -= disconnected_clients
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'service_name': 'unified-context-intelligence-service',
            'version': '1.0.0',
            'status': 'operational',
            'context_items_count': len(self.context_items),
            'news_articles_count': len(self.news_articles),
            'intelligence_insights_count': len(self.intelligence_insights),
            'consciousness_level': self.consciousness_level,
            'intelligence_accuracy': self.intelligence_accuracy,
            'models_available': {
                'sentence_transformers': SENTENCE_TRANSFORMERS_AVAILABLE,
                'nlp_dependencies': NLP_DEPENDENCIES_AVAILABLE
            },
            'connected_clients': len(self.connected_clients),
            'timestamp': datetime.now().isoformat()
        }

# Initialize unified service
context_intelligence_service = UnifiedContextIntelligenceService()

# FastAPI app
app = FastAPI(
    title="Syn_OS Unified Context Intelligence Service",
    description="Combined context engine and news intelligence for consciousness-enhanced information processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting Syn_OS Unified Context Intelligence Service...")
    await context_intelligence_service.start_background_processing()
    logger.info("Unified Context Intelligence Service started successfully!")

# Context Engine API Endpoints
@app.post("/api/v1/context/add")
async def add_context(content: str, source: str, metadata: Dict[str, Any] = None):
    """Add new context item"""
    item_id = await context_intelligence_service.add_context_item(content, source, metadata)
    return {'item_id': item_id, 'status': 'added'}

@app.get("/api/v1/context/search")
async def search_context(query: str, limit: int = 10, consciousness_threshold: float = 0.0):
    """Search context with consciousness enhancement"""
    results = await context_intelligence_service.search_context(query, limit, consciousness_threshold)
    return {
        'query': query,
        'results': [asdict(result) for result in results],
        'count': len(results)
    }

# News Intelligence API Endpoints
@app.post("/api/v1/news/fetch")
async def fetch_news(max_articles: int = 50):
    """Fetch latest news articles"""
    articles = await context_intelligence_service.fetch_news_articles(max_articles)
    return {
        'articles': [asdict(article) for article in articles],
        'count': len(articles)
    }

@app.get("/api/v1/news/articles")
async def get_news_articles(limit: int = 20):
    """Get stored news articles"""
    articles = list(context_intelligence_service.news_articles.values())[:limit]
    return {
        'articles': [asdict(article) for article in articles],
        'total_count': len(context_intelligence_service.news_articles)
    }

# Intelligence API Endpoints
@app.post("/api/v1/intelligence/generate")
async def generate_insights():
    """Generate intelligence insights"""
    insights = await context_intelligence_service.generate_intelligence_insights()
    return {
        'insights': [asdict(insight) for insight in insights],
        'count': len(insights)
    }

@app.get("/api/v1/intelligence/insights")
async def get_insights(limit: int = 20):
    """Get intelligence insights"""
    insights = list(context_intelligence_service.intelligence_insights.values())[:limit]
    return {
        'insights': [asdict(insight) for insight in insights],
        'total_count': len(context_intelligence_service.intelligence_insights)
    }

@app.get("/api/v1/status")
async def system_status():
    """Get system status"""
    return context_intelligence_service.get_system_status()

# WebSocket endpoint for real-time updates
@app.websocket("/ws/intelligence")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time intelligence updates"""
    await websocket.accept()
    context_intelligence_service.connected_clients.add(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            'type': 'connection_established',
            'status': context_intelligence_service.get_system_status()
        }, default=str))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        context_intelligence_service.connected_clients.discard(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        context_intelligence_service.connected_clients.discard(websocket)

# Dashboard web interface
@app.get("/", response_class=HTMLResponse)
async def intelligence_dashboard():
    """Context intelligence dashboard"""
    return HTMLResponse("""
    <html>
    <head><title>Syn_OS Context Intelligence Dashboard</title></head>
    <body>
    <h1>Syn_OS Unified Context Intelligence</h1>
    <h2>Real-time Information Processing</h2>
    <div id="service-status">Loading...</div>
    <div id="intelligence-metrics">Loading...</div>
    <script>
    async function updateDashboard() {
        try {
            const response = await fetch('/api/v1/status');
            const data = await response.json();
            
            document.getElementById('service-status').innerHTML = `
                <h3>Service Status: ${data.status}</h3>
                <p>Context Items: ${data.context_items_count}</p>
                <p>News Articles: ${data.news_articles_count}</p>
                <p>Intelligence Insights: ${data.intelligence_insights_count}</p>
            `;
            
            document.getElementById('intelligence-metrics').innerHTML = `
                <h3>Intelligence Metrics</h3>
                <p>Consciousness Level: ${data.consciousness_level.toFixed(2)}</p>
                <p>Intelligence Accuracy: ${data.intelligence_accuracy.toFixed(2)}</p>
                <p>Sentence Transformers: ${data.models_available.sentence_transformers ? 'Available' : 'Unavailable'}</p>
                <p>NLP Dependencies: ${data.models_available.nlp_dependencies ? 'Available' : 'Unavailable'}</p>
            `;
            
        } catch (error) {
            console.error('Dashboard update error:', error);
        }
    }
    updateDashboard();
    setInterval(updateDashboard, 10000);
    </script>
    </body>
    </html>
    """)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified-context-intelligence-service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting Syn_OS Unified Context Intelligence Service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082,
        log_level="info",
        access_log=True
    )