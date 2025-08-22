"""
NATS Message Persistence and Replay
===================================

Provides message persistence, replay capabilities, and recovery mechanisms
for NATS communication in the consciousness system.
"""

import asyncio
import json
import logging
import sqlite3
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import uuid


class MessageStatus(Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class PersistedMessage:
    """Persisted message data structure"""
    message_id: str
    subject: str
    data: bytes
    headers: Dict[str, str] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    error_message: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'message_id': self.message_id,
            'subject': self.subject,
            'data': self.data.decode('utf-8') if isinstance(self.data, bytes) else self.data,
            'headers': self.headers,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'next_retry_at': self.next_retry_at.isoformat() if self.next_retry_at else None,
            'error_message': self.error_message,
            'correlation_id': self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersistedMessage':
        """Create from dictionary"""
        message = cls(
            message_id=data['message_id'],
            subject=data['subject'],
            data=data['data'].encode('utf-8') if isinstance(data['data'], str) else data['data'],
            headers=data.get('headers', {}),
            priority=MessagePriority(data.get('priority', MessagePriority.NORMAL.value)),
            status=MessageStatus(data.get('status', MessageStatus.PENDING.value)),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            error_message=data.get('error_message'),
            correlation_id=data.get('correlation_id')
        )
        
        if 'created_at' in data:
            message.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            message.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('next_retry_at'):
            message.next_retry_at = datetime.fromisoformat(data['next_retry_at'])
        
        return message


class MessagePersistenceStore:
    """
    SQLite-based message persistence store
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize persistence store
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    data BLOB NOT NULL,
                    headers TEXT,
                    priority INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    next_retry_at TEXT,
                    error_message TEXT,
                    correlation_id TEXT
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON messages(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_subject ON messages(subject)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_priority ON messages(priority)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_next_retry ON messages(next_retry_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_correlation ON messages(correlation_id)')
            
            conn.commit()
    
    async def store_message(self, message: PersistedMessage) -> bool:
        """Store a message in the persistence store"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO messages (
                        message_id, subject, data, headers, priority, status,
                        created_at, updated_at, retry_count, max_retries,
                        next_retry_at, error_message, correlation_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message.message_id,
                    message.subject,
                    message.data,
                    json.dumps(message.headers),
                    message.priority.value,
                    message.status.value,
                    message.created_at.isoformat(),
                    message.updated_at.isoformat(),
                    message.retry_count,
                    message.max_retries,
                    message.next_retry_at.isoformat() if message.next_retry_at else None,
                    message.error_message,
                    message.correlation_id
                ))
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store message {message.message_id}: {e}")
            return False
    
    async def get_message(self, message_id: str) -> Optional[PersistedMessage]:
        """Get a message by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM messages WHERE message_id = ?',
                    (message_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_message(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get message {message_id}: {e}")
            return None
    
    async def get_messages_by_status(self, status: MessageStatus, limit: int = 100) -> List[PersistedMessage]:
        """Get messages by status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM messages WHERE status = ? ORDER BY priority DESC, created_at ASC LIMIT ?',
                    (status.value, limit)
                )
                rows = cursor.fetchall()
                
                return [self._row_to_message(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get messages by status {status}: {e}")
            return []
    
    async def get_messages_for_retry(self, limit: int = 50) -> List[PersistedMessage]:
        """Get messages that are ready for retry"""
        try:
            current_time = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM messages 
                    WHERE status IN ('failed', 'retrying') 
                    AND retry_count < max_retries 
                    AND (next_retry_at IS NULL OR next_retry_at <= ?)
                    ORDER BY priority DESC, next_retry_at ASC 
                    LIMIT ?
                ''', (current_time, limit))
                rows = cursor.fetchall()
                
                return [self._row_to_message(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get messages for retry: {e}")
            return []
    
    async def update_message_status(self, 
                                  message_id: str, 
                                  status: MessageStatus,
                                  error_message: Optional[str] = None,
                                  increment_retry: bool = False) -> bool:
        """Update message status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                updates = {
                    'status': status.value,
                    'updated_at': datetime.now().isoformat(),
                    'error_message': error_message
                }
                
                if increment_retry:
                    # Get current retry count
                    cursor = conn.execute(
                        'SELECT retry_count, max_retries FROM messages WHERE message_id = ?',
                        (message_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        retry_count = row[0] + 1
                        max_retries = row[1]
                        
                        updates['retry_count'] = retry_count
                        
                        # Calculate next retry time with exponential backoff
                        if retry_count < max_retries:
                            backoff_seconds = min(300, 2 ** retry_count * 10)  # Max 5 minutes
                            next_retry = datetime.now() + timedelta(seconds=backoff_seconds)
                            updates['next_retry_at'] = next_retry.isoformat()
                            updates['status'] = MessageStatus.RETRYING.value
                        else:
                            updates['status'] = MessageStatus.DEAD_LETTER.value
                
                # Build update query with parameterized placeholders
                set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
                values = list(updates.values()) + [message_id]
                
                # Use parameterized query to prevent SQL injection
                query = f'UPDATE messages SET {set_clause} WHERE message_id = ?'  # nosec - parameters used
                conn.execute(query, values)
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update message status {message_id}: {e}")
            return False
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message from the store"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM messages WHERE message_id = ?', (message_id,))
                conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete message {message_id}: {e}")
            return False
    
    async def cleanup_old_messages(self, older_than_days: int = 7) -> int:
        """Clean up old completed/dead letter messages"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM messages 
                    WHERE status IN ('completed', 'dead_letter') 
                    AND updated_at < ?
                ''', (cutoff_date,))
                deleted_count = cursor.rowcount
                conn.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old messages")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old messages: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get persistence store statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Count by status
                cursor = conn.execute('''
                    SELECT status, COUNT(*) as count 
                    FROM messages 
                    GROUP BY status
                ''')
                status_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Total messages
                cursor = conn.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]
                
                # Oldest pending message
                cursor = conn.execute('''
                    SELECT MIN(created_at) FROM messages 
                    WHERE status = 'pending'
                ''')
                oldest_pending = cursor.fetchone()[0]
                
                return {
                    'total_messages': total_messages,
                    'status_counts': status_counts,
                    'oldest_pending_message': oldest_pending,
                    'database_path': str(self.db_path)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def _row_to_message(self, row: sqlite3.Row) -> PersistedMessage:
        """Convert SQLite row to PersistedMessage"""
        message = PersistedMessage(
            message_id=row['message_id'],
            subject=row['subject'],
            data=row['data'],
            headers=json.loads(row['headers']) if row['headers'] else {},
            priority=MessagePriority(row['priority']),
            status=MessageStatus(row['status']),
            retry_count=row['retry_count'],
            max_retries=row['max_retries'],
            error_message=row['error_message'],
            correlation_id=row['correlation_id']
        )
        
        message.created_at = datetime.fromisoformat(row['created_at'])
        message.updated_at = datetime.fromisoformat(row['updated_at'])
        
        if row['next_retry_at']:
            message.next_retry_at = datetime.fromisoformat(row['next_retry_at'])
        
        return message


class MessageReplayManager:
    """
    Manages message replay and recovery operations
    """
    
    def __init__(self, 
                 persistence_store: MessagePersistenceStore,
                 nats_client: Any = None):
        """
        Initialize replay manager
        
        Args:
            persistence_store: Message persistence store
            nats_client: NATS client for publishing messages
        """
        self.store = persistence_store
        self.nats_client = nats_client
        self.logger = logging.getLogger(__name__)
        
        # Replay configuration
        self.replay_batch_size = 50
        self.replay_interval = 30.0  # seconds
        self.max_concurrent_replays = 10
        
        # Replay state
        self.is_running = False
        self.replay_task: Optional[asyncio.Task] = None
        self.replay_semaphore = asyncio.Semaphore(self.max_concurrent_replays)
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
    
    def set_nats_client(self, nats_client: Any):
        """Set NATS client for message publishing"""
        self.nats_client = nats_client
    
    def register_message_handler(self, subject_pattern: str, handler: Callable):
        """Register a message handler for a subject pattern"""
        self.message_handlers[subject_pattern] = handler
    
    async def start(self):
        """Start the replay manager"""
        if self.is_running:
            return
        
        self.is_running = True
        self.replay_task = asyncio.create_task(self._replay_loop())
        self.logger.info("Message replay manager started")
    
    async def stop(self):
        """Stop the replay manager"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.replay_task:
            self.replay_task.cancel()
            try:
                await self.replay_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Message replay manager stopped")
    
    async def persist_message(self, 
                            subject: str, 
                            data: bytes,
                            headers: Optional[Dict[str, str]] = None,
                            priority: MessagePriority = MessagePriority.NORMAL,
                            correlation_id: Optional[str] = None) -> str:
        """Persist a message for reliable delivery"""
        
        message_id = str(uuid.uuid4())
        message = PersistedMessage(
            message_id=message_id,
            subject=subject,
            data=data,
            headers=headers or {},
            priority=priority,
            correlation_id=correlation_id
        )
        
        success = await self.store.store_message(message)
        if success:
            self.logger.debug(f"Persisted message {message_id} for subject {subject}")
            return message_id
        else:
            raise RuntimeError(f"Failed to persist message for subject {subject}")
    
    async def replay_message(self, message_id: str) -> bool:
        """Replay a specific message"""
        message = await self.store.get_message(message_id)
        if not message:
            self.logger.error(f"Message {message_id} not found for replay")
            return False
        
        return await self._process_message(message)
    
    async def replay_failed_messages(self, limit: int = 50) -> int:
        """Replay failed messages that are ready for retry"""
        messages = await self.store.get_messages_for_retry(limit)
        
        if not messages:
            return 0
        
        self.logger.info(f"Replaying {len(messages)} failed messages")
        
        # Process messages concurrently
        tasks = []
        for message in messages:
            task = asyncio.create_task(self._process_message_with_semaphore(message))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful replays
        success_count = sum(1 for result in results if result is True)
        
        self.logger.info(f"Successfully replayed {success_count}/{len(messages)} messages")
        return success_count
    
    async def _replay_loop(self):
        """Background loop for message replay"""
        while self.is_running:
            try:
                # Replay failed messages
                await self.replay_failed_messages(self.replay_batch_size)
                
                # Cleanup old messages
                await self.store.cleanup_old_messages()
                
                # Wait for next iteration
                await asyncio.sleep(self.replay_interval)
                
            except Exception as e:
                self.logger.error(f"Error in replay loop: {e}")
                await asyncio.sleep(self.replay_interval)
    
    async def _process_message_with_semaphore(self, message: PersistedMessage) -> bool:
        """Process message with concurrency control"""
        async with self.replay_semaphore:
            return await self._process_message(message)
    
    async def _process_message(self, message: PersistedMessage) -> bool:
        """Process a single message"""
        try:
            # Update status to processing
            await self.store.update_message_status(
                message.message_id, 
                MessageStatus.PROCESSING
            )
            
            # Try to publish via NATS if client is available
            if self.nats_client:
                success = await self._publish_via_nats(message)
            else:
                # Try custom handlers
                success = await self._process_via_handlers(message)
            
            if success:
                # Mark as completed
                await self.store.update_message_status(
                    message.message_id,
                    MessageStatus.COMPLETED
                )
                self.logger.debug(f"Successfully processed message {message.message_id}")
                return True
            else:
                # Mark as failed and increment retry
                await self.store.update_message_status(
                    message.message_id,
                    MessageStatus.FAILED,
                    error_message="Processing failed",
                    increment_retry=True
                )
                return False
                
        except Exception as e:
            # Mark as failed and increment retry
            await self.store.update_message_status(
                message.message_id,
                MessageStatus.FAILED,
                error_message=str(e),
                increment_retry=True
            )
            self.logger.error(f"Failed to process message {message.message_id}: {e}")
            return False
    
    async def _publish_via_nats(self, message: PersistedMessage) -> bool:
        """Publish message via NATS"""
        try:
            if hasattr(self.nats_client, 'publish'):
                await self.nats_client.publish(
                    message.subject,
                    message.data,
                    headers=message.headers
                )
                return True
            elif hasattr(self.nats_client, 'js') and self.nats_client.js:
                await self.nats_client.js.publish(
                    message.subject,
                    message.data,
                    headers=message.headers
                )
                return True
            else:
                self.logger.error("NATS client does not support publishing")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to publish message via NATS: {e}")
            return False
    
    async def _process_via_handlers(self, message: PersistedMessage) -> bool:
        """Process message via registered handlers"""
        for pattern, handler in self.message_handlers.items():
            if self._subject_matches_pattern(message.subject, pattern):
                try:
                    await handler(message)
                    return True
                except Exception as e:
                    self.logger.error(f"Handler {pattern} failed for message {message.message_id}: {e}")
                    return False
        
        self.logger.warning(f"No handler found for subject {message.subject}")
        return False
    
    def _subject_matches_pattern(self, subject: str, pattern: str) -> bool:
        """Check if subject matches pattern (simple wildcard support)"""
        if pattern == "*" or pattern == ">":
            return True
        
        if ">" in pattern:
            prefix = pattern.replace(">", "")
            return subject.startswith(prefix)
        
        if "*" in pattern:
            # Simple wildcard matching
            parts = pattern.split("*")
            if len(parts) == 2:
                return subject.startswith(parts[0]) and subject.endswith(parts[1])
        
        return subject == pattern
    
    async def get_replay_statistics(self) -> Dict[str, Any]:
        """Get replay manager statistics"""
        store_stats = await self.store.get_statistics()
        
        return {
            'is_running': self.is_running,
            'replay_batch_size': self.replay_batch_size,
            'replay_interval': self.replay_interval,
            'max_concurrent_replays': self.max_concurrent_replays,
            'registered_handlers': len(self.message_handlers),
            'store_statistics': store_stats
        }