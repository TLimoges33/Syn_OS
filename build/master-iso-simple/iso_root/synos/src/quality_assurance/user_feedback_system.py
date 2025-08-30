#!/usr/bin/env python3
"""
User Feedback Integration System for Syn_OS
Collects, analyzes, and integrates user feedback for continuous improvement
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import statistics
import hashlib
import re

from src.consciousness_v2.consciousness_bus import ConsciousnessBus


class FeedbackType(Enum):
    """Types of user feedback"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_CONCERN = "security_concern"
    USABILITY_FEEDBACK = "usability_feedback"
    DOCUMENTATION_FEEDBACK = "documentation_feedback"
    GENERAL_FEEDBACK = "general_feedback"
    CRASH_REPORT = "crash_report"


class FeedbackPriority(Enum):
    """Feedback priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeedbackStatus(Enum):
    """Feedback processing status"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    DUPLICATE = "duplicate"
    WONT_FIX = "wont_fix"


@dataclass
class UserFeedback:
    """User feedback item"""
    feedback_id: str
    user_id: str
    feedback_type: FeedbackType
    title: str
    description: str
    priority: FeedbackPriority
    status: FeedbackStatus
    system_info: Dict[str, Any]
    attachments: List[str]
    tags: List[str]
    created_at: float
    updated_at: float
    resolved_at: Optional[float] = None
    resolution_notes: Optional[str] = None
    votes: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = time.time()


@dataclass
class FeedbackAnalysis:
    """Feedback analysis results"""
    analysis_id: str
    feedback_id: str
    sentiment_score: float  # -1 to 1
    urgency_score: float   # 0 to 1
    complexity_score: float # 0 to 1
    similar_feedback: List[str]
    suggested_actions: List[str]
    auto_categorization: Dict[str, float]
    analysis_timestamp: float


@dataclass
class FeedbackReport:
    """Feedback analytics report"""
    report_id: str
    period_start: float
    period_end: float
    total_feedback: int
    feedback_by_type: Dict[str, int]
    feedback_by_priority: Dict[str, int]
    feedback_by_status: Dict[str, int]
    average_resolution_time: float
    satisfaction_score: float
    trending_issues: List[Dict[str, Any]]
    improvement_suggestions: List[str]
    generated_at: float


class UserFeedbackSystem:
    """
    Comprehensive user feedback integration system for Syn_OS
    Collects, analyzes, and processes user feedback for continuous improvement
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize user feedback system"""
        self.consciousness_bus = consciousness_bus
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.system_directory = "/var/lib/synos/user_feedback"
        self.database_file = f"{self.system_directory}/feedback.db"
        self.attachments_dir = f"{self.system_directory}/attachments"
        
        # Data stores
        self.feedback_items: Dict[str, UserFeedback] = {}
        self.feedback_analyses: Dict[str, FeedbackAnalysis] = {}
        self.reports: Dict[str, FeedbackReport] = {}
        
        # Analysis configuration
        self.sentiment_keywords = self._initialize_sentiment_keywords()
        self.urgency_keywords = self._initialize_urgency_keywords()
        
        # Initialize system
        asyncio.create_task(self._initialize_feedback_system())
    
    async def _initialize_feedback_system(self):
        """Initialize the user feedback system"""
        try:
            self.logger.info("Initializing user feedback system...")
            
            # Create directories
            import os
            os.makedirs(self.system_directory, exist_ok=True)
            os.makedirs(self.attachments_dir, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing feedback
            await self._load_feedback_data()
            
            # Start background processing
            asyncio.create_task(self._background_processing_loop())
            
            self.logger.info("User feedback system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing user feedback system: {e}")
    
    async def _initialize_database(self):
        """Initialize feedback database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # User feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    system_info TEXT,
                    attachments TEXT,
                    tags TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    resolved_at REAL,
                    resolution_notes TEXT,
                    votes INTEGER DEFAULT 0
                )
            ''')
            
            # Feedback analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback_analysis (
                    analysis_id TEXT PRIMARY KEY,
                    feedback_id TEXT NOT NULL,
                    sentiment_score REAL NOT NULL,
                    urgency_score REAL NOT NULL,
                    complexity_score REAL NOT NULL,
                    similar_feedback TEXT,
                    suggested_actions TEXT,
                    auto_categorization TEXT,
                    analysis_timestamp REAL NOT NULL,
                    FOREIGN KEY (feedback_id) REFERENCES user_feedback (feedback_id)
                )
            ''')
            
            # Feedback reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback_reports (
                    report_id TEXT PRIMARY KEY,
                    period_start REAL NOT NULL,
                    period_end REAL NOT NULL,
                    total_feedback INTEGER NOT NULL,
                    feedback_by_type TEXT,
                    feedback_by_priority TEXT,
                    feedback_by_status TEXT,
                    average_resolution_time REAL,
                    satisfaction_score REAL,
                    trending_issues TEXT,
                    improvement_suggestions TEXT,
                    generated_at REAL NOT NULL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_type ON user_feedback (feedback_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_status ON user_feedback (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_created ON user_feedback (created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user ON user_feedback (user_id)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing feedback database: {e}")
            raise
    
    async def _load_feedback_data(self):
        """Load existing feedback data from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load feedback items
            cursor.execute('SELECT * FROM user_feedback ORDER BY created_at DESC LIMIT 1000')
            for row in cursor.fetchall():
                feedback = UserFeedback(
                    feedback_id=row[0],
                    user_id=row[1],
                    feedback_type=FeedbackType(row[2]),
                    title=row[3],
                    description=row[4],
                    priority=FeedbackPriority(row[5]),
                    status=FeedbackStatus(row[6]),
                    system_info=json.loads(row[7]) if row[7] else {},
                    attachments=json.loads(row[8]) if row[8] else [],
                    tags=json.loads(row[9]) if row[9] else [],
                    created_at=row[10],
                    updated_at=row[11],
                    resolved_at=row[12],
                    resolution_notes=row[13],
                    votes=row[14] or 0
                )
                self.feedback_items[feedback.feedback_id] = feedback
            
            # Load feedback analyses
            cursor.execute('SELECT * FROM feedback_analysis')
            for row in cursor.fetchall():
                analysis = FeedbackAnalysis(
                    analysis_id=row[0],
                    feedback_id=row[1],
                    sentiment_score=row[2],
                    urgency_score=row[3],
                    complexity_score=row[4],
                    similar_feedback=json.loads(row[5]) if row[5] else [],
                    suggested_actions=json.loads(row[6]) if row[6] else [],
                    auto_categorization=json.loads(row[7]) if row[7] else {},
                    analysis_timestamp=row[8]
                )
                self.feedback_analyses[analysis.analysis_id] = analysis
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.feedback_items)} feedback items, "
                           f"{len(self.feedback_analyses)} analyses")
            
        except Exception as e:
            self.logger.error(f"Error loading feedback data: {e}")
    
    def _initialize_sentiment_keywords(self) -> Dict[str, List[str]]:
        """Initialize sentiment analysis keywords"""
        return {
            "positive": [
                "excellent", "great", "amazing", "love", "perfect", "awesome",
                "fantastic", "wonderful", "brilliant", "outstanding", "superb"
            ],
            "negative": [
                "terrible", "awful", "hate", "horrible", "disgusting", "worst",
                "broken", "useless", "frustrating", "annoying", "disappointing"
            ],
            "neutral": [
                "okay", "fine", "average", "normal", "standard", "typical"
            ]
        }
    
    def _initialize_urgency_keywords(self) -> Dict[str, List[str]]:
        """Initialize urgency detection keywords"""
        return {
            "critical": [
                "crash", "critical", "urgent", "emergency", "broken", "failure",
                "security", "vulnerability", "exploit", "data loss", "corruption"
            ],
            "high": [
                "important", "serious", "major", "significant", "blocking",
                "performance", "slow", "timeout", "error", "bug"
            ],
            "medium": [
                "improvement", "enhancement", "feature", "suggestion", "minor",
                "cosmetic", "ui", "ux", "usability"
            ],
            "low": [
                "nice to have", "future", "someday", "consider", "maybe",
                "documentation", "typo", "spelling"
            ]
        }
    
    async def submit_feedback(self, user_id: str, feedback_type: FeedbackType,
                            title: str, description: str, system_info: Optional[Dict[str, Any]] = None,
                            attachments: Optional[List[str]] = None) -> str:
        """Submit new user feedback"""
        try:
            feedback_id = str(uuid.uuid4())
            
            # Auto-analyze priority and urgency
            priority = await self._analyze_priority(title, description)
            
            feedback = UserFeedback(
                feedback_id=feedback_id,
                user_id=user_id,
                feedback_type=feedback_type,
                title=title,
                description=description,
                priority=priority,
                status=FeedbackStatus.NEW,
                system_info=system_info or {},
                attachments=attachments or [],
                tags=[],
                created_at=time.time(),
                updated_at=time.time()
            )
            
            # Store feedback
            self.feedback_items[feedback_id] = feedback
            await self._store_feedback(feedback)
            
            # Trigger analysis
            await self._analyze_feedback(feedback)
            
            # Consciousness-driven processing
            await self._consciousness_process_feedback(feedback)
            
            self.logger.info(f"New feedback submitted: {title} (ID: {feedback_id})")
            return feedback_id
            
        except Exception as e:
            self.logger.error(f"Error submitting feedback: {e}")
            raise
    
    async def _analyze_priority(self, title: str, description: str) -> FeedbackPriority:
        """Analyze feedback priority based on content"""
        try:
            text = f"{title} {description}".lower()
            
            # Check for critical keywords
            for keyword in self.urgency_keywords["critical"]:
                if keyword in text:
                    return FeedbackPriority.CRITICAL
            
            # Check for high priority keywords
            for keyword in self.urgency_keywords["high"]:
                if keyword in text:
                    return FeedbackPriority.HIGH
            
            # Check for low priority keywords
            for keyword in self.urgency_keywords["low"]:
                if keyword in text:
                    return FeedbackPriority.LOW
            
            # Default to medium priority
            return FeedbackPriority.MEDIUM
            
        except Exception as e:
            self.logger.error(f"Error analyzing priority: {e}")
            return FeedbackPriority.MEDIUM
    
    async def _store_feedback(self, feedback: UserFeedback):
        """Store feedback in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_feedback 
                (feedback_id, user_id, feedback_type, title, description, priority,
                 status, system_info, attachments, tags, created_at, updated_at,
                 resolved_at, resolution_notes, votes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id, feedback.user_id, feedback.feedback_type.value,
                feedback.title, feedback.description, feedback.priority.value,
                feedback.status.value, json.dumps(feedback.system_info),
                json.dumps(feedback.attachments), json.dumps(feedback.tags),
                feedback.created_at, feedback.updated_at, feedback.resolved_at,
                feedback.resolution_notes, feedback.votes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing feedback: {e}")
    
    async def _analyze_feedback(self, feedback: UserFeedback):
        """Perform comprehensive feedback analysis"""
        try:
            analysis_id = str(uuid.uuid4())
            
            # Sentiment analysis
            sentiment_score = await self._analyze_sentiment(feedback.title, feedback.description)
            
            # Urgency analysis
            urgency_score = await self._analyze_urgency(feedback.title, feedback.description)
            
            # Complexity analysis
            complexity_score = await self._analyze_complexity(feedback.description)
            
            # Find similar feedback
            similar_feedback = await self._find_similar_feedback(feedback)
            
            # Generate suggested actions
            suggested_actions = await self._generate_suggested_actions(feedback)
            
            # Auto-categorization
            auto_categorization = await self._auto_categorize_feedback(feedback)
            
            analysis = FeedbackAnalysis(
                analysis_id=analysis_id,
                feedback_id=feedback.feedback_id,
                sentiment_score=sentiment_score,
                urgency_score=urgency_score,
                complexity_score=complexity_score,
                similar_feedback=similar_feedback,
                suggested_actions=suggested_actions,
                auto_categorization=auto_categorization,
                analysis_timestamp=time.time()
            )
            
            self.feedback_analyses[analysis_id] = analysis
            await self._store_feedback_analysis(analysis)
            
        except Exception as e:
            self.logger.error(f"Error analyzing feedback: {e}")
    
    async def _analyze_sentiment(self, title: str, description: str) -> float:
        """Analyze sentiment of feedback text"""
        try:
            text = f"{title} {description}".lower()
            
            positive_count = sum(1 for word in self.sentiment_keywords["positive"] if word in text)
            negative_count = sum(1 for word in self.sentiment_keywords["negative"] if word in text)
            
            if positive_count + negative_count == 0:
                return 0.0  # Neutral
            
            sentiment = (positive_count - negative_count) / (positive_count + negative_count)
            return max(-1.0, min(1.0, sentiment))
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return 0.0
    
    async def _analyze_urgency(self, title: str, description: str) -> float:
        """Analyze urgency of feedback"""
        try:
            text = f"{title} {description}".lower()
            
            critical_count = sum(1 for word in self.urgency_keywords["critical"] if word in text)
            high_count = sum(1 for word in self.urgency_keywords["high"] if word in text)
            
            if critical_count > 0:
                return 1.0
            elif high_count > 0:
                return 0.7
            else:
                return 0.3
            
        except Exception as e:
            self.logger.error(f"Error analyzing urgency: {e}")
            return 0.5
    
    async def _analyze_complexity(self, description: str) -> float:
        """Analyze complexity of feedback issue"""
        try:
            # Simple complexity analysis based on description length and technical terms
            word_count = len(description.split())
            technical_terms = ["api", "database", "algorithm", "architecture", "integration", 
                             "configuration", "deployment", "security", "performance"]
            
            tech_count = sum(1 for term in technical_terms if term in description.lower())
            
            # Normalize complexity score
            complexity = min(1.0, (word_count / 100) + (tech_count / 10))
            return complexity
            
        except Exception as e:
            self.logger.error(f"Error analyzing complexity: {e}")
            return 0.5
    
    async def _find_similar_feedback(self, feedback: UserFeedback) -> List[str]:
        """Find similar feedback items"""
        try:
            similar = []
            feedback_words = set(feedback.title.lower().split() + feedback.description.lower().split())
            
            for other_id, other_feedback in self.feedback_items.items():
                if other_id == feedback.feedback_id:
                    continue
                
                other_words = set(other_feedback.title.lower().split() + 
                                other_feedback.description.lower().split())
                
                # Calculate similarity based on common words
                common_words = feedback_words.intersection(other_words)
                similarity = len(common_words) / len(feedback_words.union(other_words))
                
                if similarity > 0.3:  # 30% similarity threshold
                    similar.append(other_id)
            
            return similar[:5]  # Return top 5 similar items
            
        except Exception as e:
            self.logger.error(f"Error finding similar feedback: {e}")
            return []
    
    async def _generate_suggested_actions(self, feedback: UserFeedback) -> List[str]:
        """Generate suggested actions for feedback"""
        try:
            actions = []
            
            if feedback.feedback_type == FeedbackType.BUG_REPORT:
                actions.extend([
                    "Reproduce the issue in development environment",
                    "Check system logs for related errors",
                    "Create unit test to prevent regression",
                    "Assign to appropriate development team"
                ])
            
            elif feedback.feedback_type == FeedbackType.FEATURE_REQUEST:
                actions.extend([
                    "Evaluate feature feasibility",
                    "Estimate development effort",
                    "Check for similar existing features",
                    "Add to product roadmap for consideration"
                ])
            
            elif feedback.feedback_type == FeedbackType.PERFORMANCE_ISSUE:
                actions.extend([
                    "Run performance profiling",
                    "Check system resource usage",
                    "Analyze database query performance",
                    "Review recent code changes"
                ])
            
            elif feedback.feedback_type == FeedbackType.SECURITY_CONCERN:
                actions.extend([
                    "Escalate to security team immediately",
                    "Perform security assessment",
                    "Review access controls",
                    "Update security documentation"
                ])
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Error generating suggested actions: {e}")
            return []
    
    async def _auto_categorize_feedback(self, feedback: UserFeedback) -> Dict[str, float]:
        """Auto-categorize feedback into topics"""
        try:
            categories = {
                "ui_ux": 0.0,
                "performance": 0.0,
                "security": 0.0,
                "functionality": 0.0,
                "documentation": 0.0,
                "installation": 0.0
            }
            
            text = f"{feedback.title} {feedback.description}".lower()
            
            # UI/UX keywords
            ui_keywords = ["interface", "design", "layout", "button", "menu", "navigation", "usability"]
            categories["ui_ux"] = sum(1 for word in ui_keywords if word in text) / len(ui_keywords)
            
            # Performance keywords
            perf_keywords = ["slow", "fast", "performance", "speed", "lag", "timeout", "memory"]
            categories["performance"] = sum(1 for word in perf_keywords if word in text) / len(perf_keywords)
            
            # Security keywords
            sec_keywords = ["security", "vulnerability", "exploit", "password", "authentication", "encryption"]
            categories["security"] = sum(1 for word in sec_keywords if word in text) / len(sec_keywords)
            
            # Functionality keywords
            func_keywords = ["feature", "function", "work", "broken", "error", "bug", "crash"]
            categories["functionality"] = sum(1 for word in func_keywords if word in text) / len(func_keywords)
            
            # Documentation keywords
            doc_keywords = ["documentation", "help", "guide", "tutorial", "manual", "instructions"]
            categories["documentation"] = sum(1 for word in doc_keywords if word in text) / len(doc_keywords)
            
            # Installation keywords
            install_keywords = ["install", "setup", "configuration", "deployment", "upgrade"]
            categories["installation"] = sum(1 for word in install_keywords if word in text) / len(install_keywords)
            
            return categories
            
        except Exception as e:
            self.logger.error(f"Error auto-categorizing feedback: {e}")
            return {}
    
    async def _store_feedback_analysis(self, analysis: FeedbackAnalysis):
        """Store feedback analysis in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO feedback_analysis 
                (analysis_id, feedback_id, sentiment_score, urgency_score, complexity_score,
                 similar_feedback, suggested_actions, auto_categorization, analysis_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis.analysis_id, analysis.feedback_id, analysis.sentiment_score,
                analysis.urgency_score, analysis.complexity_score,
                json.dumps(analysis.similar_feedback), json.dumps(analysis.suggested_actions),
                json.dumps(analysis.auto_categorization), analysis.analysis_timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing feedback analysis: {e}")
    
    async def _consciousness_process_feedback(self, feedback: UserFeedback):
        """Process feedback through consciousness system"""
        try:
            # Consciousness-driven feedback processing
            consciousness_context = {
                "action": "process_feedback",
                "feedback": {
                    "type": feedback.feedback_type.value,
                    "priority": feedback.priority.value,
                    "title": feedback.title,
                    "description": feedback.description[:200]  # Truncate for context
                },
                "system_state": "feedback_processing"
            }
            
            # Simple processing for now (consciousness bus integration would be here)
            decision = {
                "approved": True,
                "priority_adjustment": None,
                "auto_actions": []
            }
            
            # Apply consciousness decisions
            if decision.get("priority_adjustment"):
                feedback.priority = FeedbackPriority(decision["priority_adjustment"])
                await self._store_feedback(feedback)
            
            # Execute auto-actions
            for action in decision.get("auto_actions", []):
                await self._execute_auto_action(feedback, action)
            
        except Exception as e:
            self.logger.error(f"Error in consciousness processing: {e}")
    
    async def _execute_auto_action(self, feedback: UserFeedback, action: str):
        """Execute automatic action on feedback"""
        try:
            if action == "escalate_security":
                feedback.priority = FeedbackPriority.CRITICAL
                feedback.tags.append("security_escalated")
                await self._store_feedback(feedback)
            
            elif action == "mark_duplicate":
                feedback.status = FeedbackStatus.DUPLICATE
                await self._store_feedback(feedback)
            
            elif action == "auto_resolve":
                feedback.status = FeedbackStatus.RESOLVED
                feedback.resolved_at = time.time()
                feedback.resolution_notes = "Automatically resolved by system"
                await self._store_feedback(feedback)
            
        except Exception as e:
            self.logger.error(f"Error executing auto action: {e}")
    
    async def _background_processing_loop(self):
        """Background processing loop for feedback system"""
        try:
            while True:
                # Process pending feedback
                await self._process_pending_feedback()
                
                # Update feedback priorities
                await self._update_feedback_priorities()
                
                # Generate periodic reports
                await self._generate_periodic_reports()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Wait before next iteration
                await asyncio.sleep(3600)  # Run every hour
                
        except Exception as e:
            self.logger.error(f"Error in background processing loop: {e}")
    
    async def _process_pending_feedback(self):
        """Process pending feedback items"""
        try:
            pending_feedback = [f for f in self.feedback_items.values() 
                              if f.status == FeedbackStatus.NEW]
            
            for feedback in pending_feedback:
                # Auto-acknowledge feedback
                if time.time() - feedback.created_at > 3600:  # 1 hour
                    feedback.status = FeedbackStatus.ACKNOWLEDGED
                    await self._store_feedback(feedback)
            
        except Exception as e:
            self.logger.error(f"Error processing pending feedback: {e}")
    
    async def _update_feedback_priorities(self):
        """Update feedback priorities based on votes and age"""
        try:
            for feedback in self.feedback_items.values():
                if feedback.status in [FeedbackStatus.NEW, FeedbackStatus.ACKNOWLEDGED]:
                    # Increase priority based on votes
                    if feedback.votes > 10 and feedback.priority == FeedbackPriority.LOW:
                        feedback.priority = FeedbackPriority.MEDIUM
                        await self._store_feedback(feedback)
                    elif feedback.votes > 25 and feedback.priority == FeedbackPriority.MEDIUM:
                        feedback.priority = FeedbackPriority.HIGH
                        await self._store_feedback(feedback)
            
        except Exception as e:
            self.logger.error(f"Error updating feedback priorities: {e}")
    
    async def _generate_periodic_reports(self):
        """Generate periodic feedback reports"""
        try:
            # Generate weekly report
            current_time = time.time()
            week_ago = current_time - (7 * 24 * 3600)
            
            # Check if we need to generate a new weekly report
            recent_reports = [r for r in self.reports.values() 
                            if r.period_start >= week_ago]
            
            if not recent_reports:
                await self.generate_feedback_report(period_days=7)
            
        except Exception as e:
            self.logger.error(f"Error generating periodic reports: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old feedback data"""
        try:
            cutoff_time = time.time() - (90 * 24 * 3600)  # 90 days
            
            # Remove old resolved feedback from memory
            old_feedback_ids = [
                fid for fid, feedback in self.feedback_items.items()
                if feedback.status in [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED]
                and feedback.resolved_at and feedback.resolved_at < cutoff_time
            ]
            
            for fid in old_feedback_ids:
                del self.feedback_items[fid]
            
            # Clean up database
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM user_feedback 
                WHERE status IN ('resolved', 'closed') 
                AND resolved_at < ?
            ''', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    async def generate_feedback_report(self, period_days: int = 30) -> FeedbackReport:
        """Generate comprehensive feedback report"""
        try:
            end_time = time.time()
            start_time = end_time - (period_days * 24 * 3600)
            
            # Filter feedback for period
            period_feedback = [
                f for f in self.feedback_items.values()
                if start_time <= f.created_at <= end_time
            ]
            
            if not period_feedback:
                raise ValueError("No feedback data available for the specified period")
            
            # Calculate statistics
            total_feedback = len(period_feedback)
            
            feedback_by_type = {}
            feedback_by_priority = {}
            feedback_by_status = {}
            
            for feedback in period_feedback:
                # Count by type
                ftype = feedback.feedback_type.value
                feedback_by_type[ftype] = feedback_by_type.get(ftype, 0) + 1
                
                # Count by priority
                priority = feedback.priority.value
                feedback_by_priority[priority] = feedback_by_priority.get(priority, 0) + 1
                
                # Count by status
                status = feedback.status.value
                feedback_by_status[status] = feedback_by_status.get(status, 0) + 1
            
            # Calculate average resolution time
            resolved_feedback = [f for f in period_feedback
                               if f.status == FeedbackStatus.RESOLVED and f.resolved_at is not None]
            
            if resolved_feedback:
                resolution_times = [f.resolved_at - f.created_at for f in resolved_feedback if f.resolved_at is not None]
                average_resolution_time = statistics.mean(resolution_times) if resolution_times else 0.0
            else:
                average_resolution_time = 0.0
            
            # Calculate satisfaction score (based on sentiment analysis)
            sentiment_scores = []
            for feedback in period_feedback:
                for analysis in self.feedback_analyses.values():
                    if analysis.feedback_id == feedback.feedback_id:
                        sentiment_scores.append(analysis.sentiment_score)
                        break
            
            satisfaction_score = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # Identify trending issues
            trending_issues = await self._identify_trending_issues(period_feedback)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(period_feedback)
            
            report = FeedbackReport(
                report_id=str(uuid.uuid4()),
                period_start=start_time,
                period_end=end_time,
                total_feedback=total_feedback,
                feedback_by_type=feedback_by_type,
                feedback_by_priority=feedback_by_priority,
                feedback_by_status=feedback_by_status,
                average_resolution_time=average_resolution_time,
                satisfaction_score=satisfaction_score,
                trending_issues=trending_issues,
                improvement_suggestions=improvement_suggestions,
                generated_at=time.time()
            )
            
            # Store report
            await self._store_feedback_report(report)
            self.reports[report.report_id] = report
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating feedback report: {e}")
            raise
    
    async def _identify_trending_issues(self, feedback_list: List[UserFeedback]) -> List[Dict[str, Any]]:
        """Identify trending issues from feedback"""
        try:
            # Group feedback by similar keywords
            keyword_counts = {}
            
            for feedback in feedback_list:
                words = feedback.title.lower().split() + feedback.description.lower().split()
                for word in words:
                    if len(word) > 3:  # Skip short words
                        keyword_counts[word] = keyword_counts.get(word, 0) + 1
            
            # Find trending keywords
            trending_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            trending_issues = []
            for keyword, count in trending_keywords:
                if count >= 3:  # At least 3 mentions
                    trending_issues.append({
                        "keyword": keyword,
                        "mentions": count,
                        "trend_score": count / len(feedback_list)
                    })
            
            return trending_issues
            
        except Exception as e:
            self.logger.error(f"Error identifying trending issues: {e}")
            return []
    
    async def _generate_improvement_suggestions(self, feedback_list: List[UserFeedback]) -> List[str]:
        """Generate improvement suggestions based on feedback"""
        try:
            suggestions = []
            
            # Analyze feedback types
            type_counts = {}
            for feedback in feedback_list:
                ftype = feedback.feedback_type.value
                type_counts[ftype] = type_counts.get(ftype, 0) + 1
            
            # Generate suggestions based on common issues
            if type_counts.get("bug_report", 0) > len(feedback_list) * 0.3:
                suggestions.append("Consider implementing more comprehensive testing procedures")
            
            if type_counts.get("performance_issue", 0) > len(feedback_list) * 0.2:
                suggestions.append("Focus on performance optimization initiatives")
            
            if type_counts.get("usability_feedback", 0) > len(feedback_list) * 0.25:
                suggestions.append("Conduct user experience research and design improvements")
            
            if type_counts.get("documentation_feedback", 0) > len(feedback_list) * 0.15:
                suggestions.append("Improve documentation quality and coverage")
            
            # Analyze resolution times
            unresolved_count = sum(1 for f in feedback_list
                                 if f.status not in [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED])
            
            if unresolved_count > len(feedback_list) * 0.4:
                suggestions.append("Increase resources for feedback resolution")
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error generating improvement suggestions: {e}")
            return []
    
    async def _store_feedback_report(self, report: FeedbackReport):
        """Store feedback report in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback_reports
                (report_id, period_start, period_end, total_feedback, feedback_by_type,
                 feedback_by_priority, feedback_by_status, average_resolution_time,
                 satisfaction_score, trending_issues, improvement_suggestions, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id, report.period_start, report.period_end,
                report.total_feedback, json.dumps(report.feedback_by_type),
                json.dumps(report.feedback_by_priority), json.dumps(report.feedback_by_status),
                report.average_resolution_time, report.satisfaction_score,
                json.dumps(report.trending_issues), json.dumps(report.improvement_suggestions),
                report.generated_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing feedback report: {e}")
    
    async def update_feedback_status(self, feedback_id: str, status: FeedbackStatus,
                                   resolution_notes: Optional[str] = None) -> bool:
        """Update feedback status"""
        try:
            if feedback_id not in self.feedback_items:
                raise ValueError(f"Feedback {feedback_id} not found")
            
            feedback = self.feedback_items[feedback_id]
            feedback.status = status
            feedback.updated_at = time.time()
            
            if status in [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED]:
                feedback.resolved_at = time.time()
                if resolution_notes:
                    feedback.resolution_notes = resolution_notes
            
            await self._store_feedback(feedback)
            
            self.logger.info(f"Updated feedback status: {feedback.title} -> {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating feedback status: {e}")
            return False
    
    async def vote_on_feedback(self, feedback_id: str, vote_delta: int = 1) -> bool:
        """Vote on feedback item"""
        try:
            if feedback_id not in self.feedback_items:
                raise ValueError(f"Feedback {feedback_id} not found")
            
            feedback = self.feedback_items[feedback_id]
            feedback.votes += vote_delta
            feedback.updated_at = time.time()
            
            await self._store_feedback(feedback)
            
            self.logger.info(f"Vote added to feedback: {feedback.title} (Total: {feedback.votes})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error voting on feedback: {e}")
            return False
    
    async def search_feedback(self, query: str, feedback_type: Optional[FeedbackType] = None,
                            status: Optional[FeedbackStatus] = None) -> List[Dict[str, Any]]:
        """Search feedback items"""
        try:
            results = []
            query_lower = query.lower()
            
            for feedback in self.feedback_items.values():
                # Filter by type and status
                if feedback_type and feedback.feedback_type != feedback_type:
                    continue
                if status and feedback.status != status:
                    continue
                
                # Search in title and description
                title_match = query_lower in feedback.title.lower()
                description_match = query_lower in feedback.description.lower()
                
                if title_match or description_match:
                    # Calculate relevance score
                    score = 0
                    if title_match:
                        score += 10
                    if description_match:
                        score += feedback.description.lower().count(query_lower)
                    
                    results.append({
                        "feedback_id": feedback.feedback_id,
                        "title": feedback.title,
                        "type": feedback.feedback_type.value,
                        "status": feedback.status.value,
                        "priority": feedback.priority.value,
                        "votes": feedback.votes,
                        "created_at": feedback.created_at,
                        "score": score
                    })
            
            # Sort by relevance score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching feedback: {e}")
            return []
    
    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback system statistics"""
        try:
            stats = {
                "total_feedback": len(self.feedback_items),
                "by_type": {},
                "by_priority": {},
                "by_status": {},
                "average_votes": 0,
                "resolution_rate": 0,
                "satisfaction_score": 0
            }
            
            if not self.feedback_items:
                return stats
            
            # Count by categories
            total_votes = 0
            resolved_count = 0
            sentiment_scores = []
            
            for feedback in self.feedback_items.values():
                # Count by type
                ftype = feedback.feedback_type.value
                stats["by_type"][ftype] = stats["by_type"].get(ftype, 0) + 1
                
                # Count by priority
                priority = feedback.priority.value
                stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
                
                # Count by status
                status = feedback.status.value
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Accumulate votes
                total_votes += feedback.votes
                
                # Count resolved items
                if feedback.status in [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED]:
                    resolved_count += 1
                
                # Get sentiment scores
                for analysis in self.feedback_analyses.values():
                    if analysis.feedback_id == feedback.feedback_id:
                        sentiment_scores.append(analysis.sentiment_score)
                        break
            
            # Calculate averages
            stats["average_votes"] = total_votes / len(self.feedback_items)
            stats["resolution_rate"] = (resolved_count / len(self.feedback_items)) * 100
            stats["satisfaction_score"] = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting feedback stats: {e}")
            return {}
    
    async def export_feedback_data(self, format_type: str = "json") -> str:
        """Export feedback data"""
        try:
            if format_type.lower() not in ["json", "csv"]:
                raise ValueError("Supported formats: json, csv")
            
            import os
            export_dir = f"{self.system_directory}/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = int(time.time())
            filepath = ""
            
            if format_type.lower() == "json":
                filename = f"feedback_export_{timestamp}.json"
                filepath = os.path.join(export_dir, filename)
                
                export_data = {
                    "feedback_items": [asdict(f) for f in self.feedback_items.values()],
                    "analyses": [asdict(a) for a in self.feedback_analyses.values()],
                    "export_timestamp": timestamp
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
            
            elif format_type.lower() == "csv":
                filename = f"feedback_export_{timestamp}.csv"
                filepath = os.path.join(export_dir, filename)
                
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow([
                        'feedback_id', 'user_id', 'type', 'title', 'description',
                        'priority', 'status', 'votes', 'created_at', 'updated_at'
                    ])
                    
                    # Write data
                    for feedback in self.feedback_items.values():
                        writer.writerow([
                            feedback.feedback_id, feedback.user_id, feedback.feedback_type.value,
                            feedback.title, feedback.description, feedback.priority.value,
                            feedback.status.value, feedback.votes,
                            datetime.fromtimestamp(feedback.created_at).isoformat(),
                            datetime.fromtimestamp(feedback.updated_at).isoformat()
                        ])
            
            self.logger.info(f"Exported feedback data to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting feedback data: {e}")
            raise