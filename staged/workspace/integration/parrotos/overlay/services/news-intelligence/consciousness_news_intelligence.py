#!/usr/bin/env python3
"""
SynapticOS News Intelligence Platform
Advanced news analysis with consciousness-enhanced insights
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import feedparser
from dataclasses import dataclass, asdict
import numpy as np
from textblob import TextBlob
import networkx as nx
from collections import defaultdict, Counter
import sqlite3
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('news-intelligence')

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
class NewsCluster:
    """Clustered news stories"""
    id: str
    main_topic: str
    articles: List[NewsArticle]
    sentiment_trend: str
    consciousness_insights: Dict[str, Any]
    timestamp: str

@dataclass
class ThreatIntelligence:
    """Security threat intelligence from news"""
    threat_id: str
    threat_type: str
    severity: str
    description: str
    indicators: List[str]
    source_articles: List[str]
    consciousness_assessment: float
    timestamp: str

class ConsciousnessNewsIntelligence:
    """Advanced news intelligence with consciousness enhancement"""
    
    def __init__(self, data_dir: str = "/app/data/news"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.data_dir / "news_intelligence.db"
        self.init_database()
        
        # News sources configuration
        self.news_sources = {
            "security": [
                "https://feeds.feedburner.com/eset/blog",
                "https://www.darkreading.com/rss.xml",
                "https://feeds.feedburner.com/securityweek",
                "https://krebsonsecurity.com/feed/"
            ],
            "technology": [
                "https://feeds.feedburner.com/TechCrunch",
                "https://rss.cnn.com/rss/edition.rss",
                "https://feeds.arstechnica.com/arstechnica/index"
            ],
            "ai_research": [
                "https://arxiv.org/rss/cs.AI",
                "https://arxiv.org/rss/cs.LG"
            ]
        }
        
        # Consciousness keywords for relevance scoring
        self.consciousness_keywords = [
            "consciousness", "awareness", "neural", "cognitive", "intelligence",
            "learning", "adaptation", "emergence", "complexity", "evolution",
            "quantum", "computation", "algorithm", "ai", "machine learning"
        ]
        
        logger.info("Consciousness News Intelligence Platform initialized")
    
    def init_database(self):
        """Initialize SQLite database for news intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    url TEXT,
                    source TEXT,
                    published TEXT,
                    sentiment_score REAL,
                    consciousness_relevance REAL,
                    topics TEXT,
                    entities TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    id TEXT PRIMARY KEY,
                    main_topic TEXT,
                    article_ids TEXT,
                    sentiment_trend TEXT,
                    consciousness_insights TEXT,
                    timestamp TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_intelligence (
                    threat_id TEXT PRIMARY KEY,
                    threat_type TEXT,
                    severity TEXT,
                    description TEXT,
                    indicators TEXT,
                    source_articles TEXT,
                    consciousness_assessment REAL,
                    timestamp TEXT
                )
            """)
            conn.commit()
    
    async def fetch_news_feeds(self, category: str = None) -> List[NewsArticle]:
        """Fetch news from RSS feeds with consciousness analysis"""
        articles = []
        
        sources = self.news_sources if not category else {category: self.news_sources.get(category, [])}
        
        for cat, urls in sources.items():
            for url in urls:
                try:
                    feed = feedparser.parse(url)
                    
                    for entry in feed.entries[:10]:  # Limit per feed
                        article = await self._process_article(entry, cat)
                        if article:
                            articles.append(article)
                            
                except Exception as e:
                    logger.error(f"Failed to fetch from {url}: {e}")
        
        # Store articles
        await self._store_articles(articles)
        
        logger.info(f"Fetched {len(articles)} articles")
        return articles
    
    async def _process_article(self, entry, category: str) -> Optional[NewsArticle]:
        """Process individual article with consciousness analysis"""
        try:
            # Extract content
            title = entry.get('title', '')
            content = entry.get('summary', '')
            url = entry.get('link', '')
            published = entry.get('published', datetime.now().isoformat())
            
            # Sentiment analysis
            blob = TextBlob(f"{title} {content}")
            sentiment_score = blob.sentiment.polarity
            
            # Consciousness relevance scoring
            consciousness_relevance = self._calculate_consciousness_relevance(title, content)
            
            # Topic and entity extraction (simplified)
            topics = self._extract_topics(title, content)
            entities = self._extract_entities(title, content)
            
            article_id = f"{category}_{hash(url)}_{int(datetime.now().timestamp())}"
            
            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                url=url,
                source=category,
                published=published,
                sentiment_score=sentiment_score,
                consciousness_relevance=consciousness_relevance,
                topics=topics,
                entities=entities,
                metadata={
                    "word_count": len(content.split()),
                    "fetch_time": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process article: {e}")
            return None
    
    def _calculate_consciousness_relevance(self, title: str, content: str) -> float:
        """Calculate consciousness relevance score"""
        text = f"{title} {content}".lower()
        
        keyword_matches = sum(1 for keyword in self.consciousness_keywords if keyword in text)
        total_words = len(text.split())
        
        # Base relevance from keyword density
        keyword_density = keyword_matches / max(total_words, 1)
        
        # Enhanced scoring for consciousness-related terms
        consciousness_boost = 0
        if "neural" in text or "consciousness" in text:
            consciousness_boost += 0.3
        if "ai" in text or "artificial intelligence" in text:
            consciousness_boost += 0.2
        if "learning" in text or "adaptation" in text:
            consciousness_boost += 0.1
        
        final_score = min(keyword_density * 10 + consciousness_boost, 1.0)
        return final_score
    
    def _extract_topics(self, title: str, content: str) -> List[str]:
        """Extract topics from article"""
        text = f"{title} {content}".lower()
        
        topic_keywords = {
            "cybersecurity": ["security", "hack", "breach", "vulnerability", "malware"],
            "ai": ["artificial intelligence", "machine learning", "neural", "algorithm"],
            "consciousness": ["consciousness", "awareness", "cognitive", "mind"],
            "quantum": ["quantum", "qubit", "entanglement"],
            "blockchain": ["blockchain", "cryptocurrency", "bitcoin", "ethereum"],
            "privacy": ["privacy", "surveillance", "data protection", "gdpr"]
        }
        
        topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_entities(self, title: str, content: str) -> List[str]:
        """Extract entities from article (simplified)"""
        # In production, use spaCy or similar for proper NER
        text = f"{title} {content}"
        
        # Simple pattern matching for common entities
        entities = []
        
        # Look for company names (simplified)
        companies = ["microsoft", "google", "apple", "amazon", "meta", "openai", "anthropic"]
        for company in companies:
            if company.lower() in text.lower():
                entities.append(f"company:{company}")
        
        # Look for technologies
        technologies = ["python", "rust", "javascript", "docker", "kubernetes", "linux"]
        for tech in technologies:
            if tech.lower() in text.lower():
                entities.append(f"technology:{tech}")
        
        return entities
    
    async def _store_articles(self, articles: List[NewsArticle]):
        """Store articles in database"""
        with sqlite3.connect(self.db_path) as conn:
            for article in articles:
                conn.execute("""
                    INSERT OR REPLACE INTO articles 
                    (id, title, content, url, source, published, sentiment_score, 
                     consciousness_relevance, topics, entities, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.id, article.title, article.content, article.url,
                    article.source, article.published, article.sentiment_score,
                    article.consciousness_relevance, json.dumps(article.topics),
                    json.dumps(article.entities), json.dumps(article.metadata)
                ))
            conn.commit()
    
    async def cluster_news_stories(self, timeframe_hours: int = 24) -> List[NewsCluster]:
        """Cluster related news stories"""
        # Get recent articles
        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM articles 
                WHERE datetime(published) > datetime(?)
                ORDER BY consciousness_relevance DESC
            """, (cutoff_time.isoformat(),))
            
            rows = cursor.fetchall()
        
        if not rows:
            return []
        
        # Simple clustering by topics (in production, use proper clustering algorithms)
        topic_clusters = defaultdict(list)
        
        for row in rows:
            article = NewsArticle(
                id=row[0], title=row[1], content=row[2], url=row[3],
                source=row[4], published=row[5], sentiment_score=row[6],
                consciousness_relevance=row[7], topics=json.loads(row[8]),
                entities=json.loads(row[9]), metadata=json.loads(row[10])
            )
            
            # Assign to primary topic cluster
            if article.topics:
                primary_topic = article.topics[0]
                topic_clusters[primary_topic].append(article)
            else:
                topic_clusters["general"].append(article)
        
        clusters = []
        for topic, articles in topic_clusters.items():
            if len(articles) >= 2:  # Only cluster if multiple articles
                cluster_id = f"cluster_{topic}_{int(datetime.now().timestamp())}"
                
                # Calculate sentiment trend
                sentiments = [article.sentiment_score for article in articles]
                avg_sentiment = sum(sentiments) / len(sentiments)
                sentiment_trend = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
                
                # Consciousness insights
                consciousness_insights = {
                    "average_relevance": sum(article.consciousness_relevance for article in articles) / len(articles),
                    "high_relevance_count": sum(1 for article in articles if article.consciousness_relevance > 0.5),
                    "dominant_entities": self._get_dominant_entities(articles)
                }
                
                cluster = NewsCluster(
                    id=cluster_id,
                    main_topic=topic,
                    articles=articles,
                    sentiment_trend=sentiment_trend,
                    consciousness_insights=consciousness_insights,
                    timestamp=datetime.now().isoformat()
                )
                
                clusters.append(cluster)
        
        # Store clusters
        await self._store_clusters(clusters)
        
        logger.info(f"Created {len(clusters)} news clusters")
        return clusters
    
    def _get_dominant_entities(self, articles: List[NewsArticle]) -> List[str]:
        """Get dominant entities across articles"""
        entity_counter = Counter()
        
        for article in articles:
            for entity in article.entities:
                entity_counter[entity] += 1
        
        return [entity for entity, count in entity_counter.most_common(5)]
    
    async def _store_clusters(self, clusters: List[NewsCluster]):
        """Store clusters in database"""
        with sqlite3.connect(self.db_path) as conn:
            for cluster in clusters:
                article_ids = [article.id for article in cluster.articles]
                conn.execute("""
                    INSERT OR REPLACE INTO clusters 
                    (id, main_topic, article_ids, sentiment_trend, consciousness_insights, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    cluster.id, cluster.main_topic, json.dumps(article_ids),
                    cluster.sentiment_trend, json.dumps(cluster.consciousness_insights),
                    cluster.timestamp
                ))
            conn.commit()
    
    async def generate_threat_intelligence(self) -> List[ThreatIntelligence]:
        """Generate security threat intelligence from news"""
        # Get security-related articles
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM articles 
                WHERE source = 'security' 
                AND datetime(published) > datetime('now', '-7 days')
                ORDER BY consciousness_relevance DESC
            """)
            
            rows = cursor.fetchall()
        
        threats = []
        
        for row in rows:
            article = NewsArticle(
                id=row[0], title=row[1], content=row[2], url=row[3],
                source=row[4], published=row[5], sentiment_score=row[6],
                consciousness_relevance=row[7], topics=json.loads(row[8]),
                entities=json.loads(row[9]), metadata=json.loads(row[10])
            )
            
            # Analyze for threat indicators
            threat = await self._analyze_threat_indicators(article)
            if threat:
                threats.append(threat)
        
        # Store threats
        await self._store_threats(threats)
        
        logger.info(f"Generated {len(threats)} threat intelligence items")
        return threats
    
    async def _analyze_threat_indicators(self, article: NewsArticle) -> Optional[ThreatIntelligence]:
        """Analyze article for threat indicators"""
        text = f"{article.title} {article.content}".lower()
        
        # Threat type detection
        threat_types = {
            "malware": ["malware", "virus", "trojan", "ransomware", "spyware"],
            "phishing": ["phishing", "phish", "social engineering", "fake email"],
            "vulnerability": ["vulnerability", "cve", "exploit", "zero-day", "patch"],
            "data_breach": ["data breach", "leaked", "stolen data", "compromised"],
            "ddos": ["ddos", "denial of service", "botnet"],
            "apt": ["apt", "advanced persistent", "state-sponsored", "nation-state"]
        }
        
        detected_type = None
        for threat_type, keywords in threat_types.items():
            if any(keyword in text for keyword in keywords):
                detected_type = threat_type
                break
        
        if not detected_type:
            return None
        
        # Severity assessment
        severity_keywords = {
            "critical": ["critical", "severe", "emergency", "immediate"],
            "high": ["high", "serious", "significant", "major"],
            "medium": ["medium", "moderate", "notable"],
            "low": ["low", "minor", "informational"]
        }
        
        severity = "medium"  # default
        for sev, keywords in severity_keywords.items():
            if any(keyword in text for keyword in keywords):
                severity = sev
                break
        
        # Extract indicators (simplified)
        indicators = []
        
        # Look for IP addresses (basic pattern)
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        indicators.extend(re.findall(ip_pattern, text))
        
        # Look for domain names
        domain_pattern = r'\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        potential_domains = re.findall(domain_pattern, text)
        # Filter out common non-malicious domains
        common_domains = ['gmail.com', 'microsoft.com', 'google.com', 'apple.com']
        indicators.extend([d for d in potential_domains if d not in common_domains])
        
        threat_id = f"threat_{detected_type}_{int(datetime.now().timestamp())}"
        
        return ThreatIntelligence(
            threat_id=threat_id,
            threat_type=detected_type,
            severity=severity,
            description=article.title,
            indicators=indicators[:5],  # Limit indicators
            source_articles=[article.id],
            consciousness_assessment=article.consciousness_relevance,
            timestamp=datetime.now().isoformat()
        )
    
    async def _store_threats(self, threats: List[ThreatIntelligence]):
        """Store threat intelligence in database"""
        with sqlite3.connect(self.db_path) as conn:
            for threat in threats:
                conn.execute("""
                    INSERT OR REPLACE INTO threat_intelligence 
                    (threat_id, threat_type, severity, description, indicators, 
                     source_articles, consciousness_assessment, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    threat.threat_id, threat.threat_type, threat.severity,
                    threat.description, json.dumps(threat.indicators),
                    json.dumps(threat.source_articles), threat.consciousness_assessment,
                    threat.timestamp
                ))
            conn.commit()
    
    async def get_intelligence_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive intelligence dashboard"""
        with sqlite3.connect(self.db_path) as conn:
            # Article statistics
            cursor = conn.execute("SELECT COUNT(*), AVG(consciousness_relevance) FROM articles WHERE datetime(published) > datetime('now', '-24 hours')")
            article_stats = cursor.fetchone()
            
            # Cluster statistics
            cursor = conn.execute("SELECT COUNT(*) FROM clusters WHERE datetime(timestamp) > datetime('now', '-24 hours')")
            cluster_count = cursor.fetchone()[0]
            
            # Threat statistics
            cursor = conn.execute("SELECT threat_type, COUNT(*) FROM threat_intelligence WHERE datetime(timestamp) > datetime('now', '-24 hours') GROUP BY threat_type")
            threat_stats = dict(cursor.fetchall())
            
            # Top consciousness-relevant articles
            cursor = conn.execute("""
                SELECT title, consciousness_relevance, source 
                FROM articles 
                WHERE datetime(published) > datetime('now', '-24 hours')
                ORDER BY consciousness_relevance DESC 
                LIMIT 5
            """)
            top_articles = cursor.fetchall()
        
        return {
            "articles_24h": article_stats[0] or 0,
            "avg_consciousness_relevance": article_stats[1] or 0,
            "clusters_24h": cluster_count,
            "threat_breakdown": threat_stats,
            "top_consciousness_articles": [
                {"title": row[0], "relevance": row[1], "source": row[2]}
                for row in top_articles
            ],
            "last_updated": datetime.now().isoformat()
        }

async def main():
    """Demo the news intelligence platform"""
    intelligence = ConsciousnessNewsIntelligence()
    
    print("🧠 SynapticOS News Intelligence Platform Demo")
    print("=" * 50)
    
    # Fetch news
    print("📰 Fetching news articles...")
    articles = await intelligence.fetch_news_feeds("security")
    print(f"✅ Fetched {len(articles)} articles")
    
    # Cluster stories
    print("\n🔗 Clustering related stories...")
    clusters = await intelligence.cluster_news_stories()
    print(f"✅ Created {len(clusters)} clusters")
    
    # Generate threat intelligence
    print("\n🛡️ Generating threat intelligence...")
    threats = await intelligence.generate_threat_intelligence()
    print(f"✅ Generated {len(threats)} threat indicators")
    
    # Get dashboard
    print("\n📊 Intelligence Dashboard:")
    dashboard = await intelligence.get_intelligence_dashboard()
    for key, value in dashboard.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
