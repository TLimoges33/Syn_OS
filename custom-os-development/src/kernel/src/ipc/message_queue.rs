/// Advanced Message Queue Implementation for SynOS IPC
/// Provides consciousness-integrated message passing with priority handling

use alloc::collections::{BTreeMap, VecDeque};
use alloc::vec::Vec;
use core::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use spin::Mutex;

use super::{IPCId, IPCError};

/// Message priority levels for consciousness-aware scheduling
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum MessagePriority {
    Idle = 0,
    Low = 1,
    Normal = 2,
    High = 3,
    RealTime = 4,
    Consciousness = 5,  // Highest priority for AI operations
}

impl Default for MessagePriority {
    fn default() -> Self {
        MessagePriority::Normal
    }
}

/// Message flags for special handling
#[derive(Debug, Clone, Copy)]
pub struct MessageFlags {
    pub no_wait: bool,           // Non-blocking operations
    pub except: bool,            // Exception message
    pub consciousness_aware: bool, // Enable AI optimization
    pub persistent: bool,        // Survive system reboot
}

impl MessageFlags {
    /// No special flags set
    pub const NONE: MessageFlags = MessageFlags {
        no_wait: false,
        except: false,
        consciousness_aware: false,
        persistent: false,
    };
}

impl Default for MessageFlags {
    fn default() -> Self {
        Self {
            no_wait: false,
            except: false,
            consciousness_aware: true,
            persistent: false,
        }
    }
}

/// Individual message in the queue
#[derive(Debug, Clone)]
pub struct Message {
    pub id: u64,
    pub msg_type: u32,
    pub priority: MessagePriority,
    pub data: Vec<u8>,
    pub sender_pid: u64,
    pub timestamp: u64,
    pub flags: MessageFlags,
    pub consciousness_score: f32,
}

impl Message {
    /// Create a new message
    pub fn new(
        msg_type: u32,
        data: Vec<u8>,
        sender_pid: u64,
        priority: MessagePriority,
        flags: MessageFlags,
    ) -> Self {
        static NEXT_MSG_ID: AtomicU64 = AtomicU64::new(1);
        
        Self {
            id: NEXT_MSG_ID.fetch_add(1, Ordering::SeqCst),
            msg_type,
            priority,
            data,
            sender_pid,
            timestamp: Self::get_current_time(),
            flags,
            consciousness_score: 0.0,
        }
    }

    /// Get current system time (placeholder implementation)
    fn get_current_time() -> u64 {
        // In a real implementation, this would get the actual system time
        static TIME_COUNTER: AtomicU64 = AtomicU64::new(0);
        TIME_COUNTER.fetch_add(1, Ordering::SeqCst)
    }

    /// Calculate consciousness relevance score
    pub fn calculate_consciousness_score(&mut self, context: Option<&[u8]>) {
        // Consciousness scoring algorithm
        let mut score = match self.priority {
            MessagePriority::Consciousness => 1.0,
            MessagePriority::RealTime => 0.8,
            MessagePriority::High => 0.6,
            MessagePriority::Normal => 0.4,
            MessagePriority::Low => 0.2,
            MessagePriority::Idle => 0.1,
        };

        // Boost score for consciousness-aware messages
        if self.flags.consciousness_aware {
            score *= 1.5;
        }

        // Content-based scoring (simplified)
        if let Some(ctx) = context {
            if self.data.len() > 0 && ctx.len() > 0 {
                // Simple correlation score based on data similarity
                let correlation = self.calculate_data_correlation(ctx);
                score *= 1.0 + correlation;
            }
        }

        self.consciousness_score = score.min(1.0);
    }

    /// Calculate correlation between message data and context
    fn calculate_data_correlation(&self, context: &[u8]) -> f32 {
        if self.data.is_empty() || context.is_empty() {
            return 0.0;
        }

        let mut matches = 0;
        let max_len = self.data.len().min(context.len());
        
        for i in 0..max_len {
            if self.data[i] == context[i] {
                matches += 1;
            }
        }

        matches as f32 / max_len as f32
    }
}

/// Priority-based message queue structure
#[derive(Debug)]
struct PriorityQueue {
    queues: BTreeMap<MessagePriority, VecDeque<Message>>,
    total_messages: usize,
}

impl PriorityQueue {
    fn new() -> Self {
        Self {
            queues: BTreeMap::new(),
            total_messages: 0,
        }
    }

    /// Add message to appropriate priority queue
    fn enqueue(&mut self, message: Message) -> Result<(), IPCError> {
        let priority = message.priority;
        
        self.queues
            .entry(priority)
            .or_insert_with(VecDeque::new)
            .push_back(message);
        
        self.total_messages += 1;
        Ok(())
    }

    /// Remove highest priority message
    fn dequeue(&mut self) -> Option<Message> {
        // Process messages in priority order (highest first)
        for (_, queue) in self.queues.iter_mut().rev() {
            if let Some(message) = queue.pop_front() {
                self.total_messages -= 1;
                return Some(message);
            }
        }
        None
    }

    /// Remove message of specific type
    fn dequeue_by_type(&mut self, msg_type: u32) -> Option<Message> {
        for (_, queue) in self.queues.iter_mut().rev() {
            for i in 0..queue.len() {
                if queue[i].msg_type == msg_type {
                    self.total_messages -= 1;
                    return queue.remove(i);
                }
            }
        }
        None
    }

    /// Get current queue size
    fn len(&self) -> usize {
        self.total_messages
    }

    /// Check if queue is empty
    fn is_empty(&self) -> bool {
        self.total_messages == 0
    }

    /// Get queue statistics
    fn get_stats(&self) -> MessageQueueStats {
        let mut stats = MessageQueueStats::default();
        
        for (priority, queue) in &self.queues {
            let count = queue.len();
            match priority {
                MessagePriority::Consciousness => stats.consciousness_messages = count,
                MessagePriority::RealTime => stats.realtime_messages = count,
                MessagePriority::High => stats.high_priority_messages = count,
                MessagePriority::Normal => stats.normal_messages = count,
                MessagePriority::Low => stats.low_priority_messages = count,
                MessagePriority::Idle => stats.idle_messages = count,
            }
        }
        
        stats.total_messages = self.total_messages;
        stats
    }
}

/// Message queue statistics
#[derive(Debug, Default)]
pub struct MessageQueueStats {
    pub total_messages: usize,
    pub consciousness_messages: usize,
    pub realtime_messages: usize,
    pub high_priority_messages: usize,
    pub normal_messages: usize,
    pub low_priority_messages: usize,
    pub idle_messages: usize,
    pub messages_sent: u64,
    pub messages_received: u64,
    pub average_wait_time: u64,
    pub consciousness_optimizations: u64,
}

/// Message queue configuration
#[derive(Debug, Clone)]
pub struct MessageQueueConfig {
    pub max_messages: usize,
    pub max_message_size: usize,
    pub enable_consciousness: bool,
    pub persistence: bool,
    pub timeout_ms: u64,
}

impl Default for MessageQueueConfig {
    fn default() -> Self {
        Self {
            max_messages: 1000,
            max_message_size: 8192,  // 8KB default
            enable_consciousness: true,
            persistence: false,
            timeout_ms: 5000,  // 5 second timeout
        }
    }
}

/// Complete message queue implementation
pub struct MessageQueue {
    id: IPCId,
    owner_pid: u64,
    config: MessageQueueConfig,
    queue: Mutex<PriorityQueue>,
    stats: Mutex<MessageQueueStats>,
    waiting_senders: AtomicUsize,
    waiting_receivers: AtomicUsize,
    consciousness_context: Mutex<Vec<u8>>,
}

impl MessageQueue {
    /// Create a new message queue
    pub fn new(id: IPCId, owner_pid: u64, config: MessageQueueConfig) -> Self {
        Self {
            id,
            owner_pid,
            config,
            queue: Mutex::new(PriorityQueue::new()),
            stats: Mutex::new(MessageQueueStats::default()),
            waiting_senders: AtomicUsize::new(0),
            waiting_receivers: AtomicUsize::new(0),
            consciousness_context: Mutex::new(Vec::new()),
        }
    }

    /// Send a message to the queue
    pub fn send_message(
        &self,
        msg_type: u32,
        data: Vec<u8>,
        sender_pid: u64,
        priority: MessagePriority,
        flags: MessageFlags,
    ) -> Result<(), IPCError> {
        // Validate message size
        if data.len() > self.config.max_message_size {
            return Err(IPCError::InvalidArgument);
        }

        let mut queue = self.queue.lock();
        
        // Check queue capacity
        if queue.len() >= self.config.max_messages {
            if flags.no_wait {
                return Err(IPCError::ResourceBusy);
            }
            // In a real implementation, we would block here
            return Err(IPCError::ResourceBusy);
        }

        // Create message
        let mut message = Message::new(msg_type, data, sender_pid, priority, flags);

        // Apply consciousness scoring if enabled
        if self.config.enable_consciousness && flags.consciousness_aware {
            let context = self.consciousness_context.lock();
            message.calculate_consciousness_score(Some(&context));
            
            // Update consciousness context with new data
            drop(context);
            self.update_consciousness_context(&message.data);
        }

        // Add to queue
        queue.enqueue(message)?;

        // Update statistics
        let mut stats = self.stats.lock();
        stats.messages_sent += 1;

        Ok(())
    }

    /// Receive a message from the queue
    pub fn receive_message(
        &self,
        msg_type: Option<u32>,
        flags: MessageFlags,
    ) -> Result<Option<Message>, IPCError> {
        let mut queue = self.queue.lock();

        let message = match msg_type {
            Some(mt) => queue.dequeue_by_type(mt),
            None => queue.dequeue(),
        };

        if let Some(msg) = message {
            // Update statistics
            let mut stats = self.stats.lock();
            stats.messages_received += 1;
            
            // Update consciousness context if this was a consciousness message
            if msg.flags.consciousness_aware && self.config.enable_consciousness {
                self.update_consciousness_context(&msg.data);
            }

            Ok(Some(msg))
        } else if flags.no_wait {
            Ok(None)
        } else {
            // In a real implementation, we would block here
            Ok(None)
        }
    }

    /// Update consciousness context for better message prioritization
    fn update_consciousness_context(&self, new_data: &[u8]) {
        let mut context = self.consciousness_context.lock();
        
        // Simple sliding window approach - keep last 1KB of context
        const MAX_CONTEXT_SIZE: usize = 1024;
        
        context.extend_from_slice(new_data);
        if context.len() > MAX_CONTEXT_SIZE {
            let excess = context.len() - MAX_CONTEXT_SIZE;
            context.drain(0..excess);
        }
    }

    /// Get queue statistics
    pub fn get_stats(&self) -> MessageQueueStats {
        let queue_stats = self.queue.lock().get_stats();
        let mut stats = self.stats.lock();
        
        // Merge queue stats with persistent stats
        stats.total_messages = queue_stats.total_messages;
        stats.consciousness_messages = queue_stats.consciousness_messages;
        stats.realtime_messages = queue_stats.realtime_messages;
        stats.high_priority_messages = queue_stats.high_priority_messages;
        stats.normal_messages = queue_stats.normal_messages;
        stats.low_priority_messages = queue_stats.low_priority_messages;
        stats.idle_messages = queue_stats.idle_messages;
        
        MessageQueueStats {
            total_messages: stats.total_messages,
            consciousness_messages: stats.consciousness_messages,
            realtime_messages: stats.realtime_messages,
            high_priority_messages: stats.high_priority_messages,
            normal_messages: stats.normal_messages,
            low_priority_messages: stats.low_priority_messages,
            idle_messages: stats.idle_messages,
            messages_sent: stats.messages_sent,
            messages_received: stats.messages_received,
            average_wait_time: stats.average_wait_time,
            consciousness_optimizations: stats.consciousness_optimizations,
        }
    }

    /// Get queue ID
    pub fn get_id(&self) -> IPCId {
        self.id
    }

    /// Get owner process ID
    pub fn get_owner_pid(&self) -> u64 {
        self.owner_pid
    }

    /// Check if queue is full
    pub fn is_full(&self) -> bool {
        let queue = self.queue.lock();
        queue.len() >= self.config.max_messages
    }

    /// Check if queue is empty
    pub fn is_empty(&self) -> bool {
        let queue = self.queue.lock();
        queue.is_empty()
    }

    /// Get current queue length
    pub fn len(&self) -> usize {
        let queue = self.queue.lock();
        queue.len()
    }

    /// Clear all messages from the queue
    pub fn clear(&self) {
        let mut queue = self.queue.lock();
        *queue = PriorityQueue::new();
        
        let mut stats = self.stats.lock();
        stats.total_messages = 0;
        stats.consciousness_messages = 0;
        stats.realtime_messages = 0;
        stats.high_priority_messages = 0;
        stats.normal_messages = 0;
        stats.low_priority_messages = 0;
        stats.idle_messages = 0;
    }
}

/// Message queue manager for handling multiple queues
pub struct MessageQueueManager {
    queues: Mutex<BTreeMap<IPCId, MessageQueue>>,
    next_id: AtomicU64,
}

impl MessageQueueManager {
    /// Create a new message queue manager
    pub fn new() -> Self {
        Self {
            queues: Mutex::new(BTreeMap::new()),
            next_id: AtomicU64::new(1),
        }
    }

    /// Create a new message queue
    pub fn create_queue(
        &self,
        owner_pid: u64,
        config: MessageQueueConfig,
    ) -> Result<IPCId, IPCError> {
        let id = self.next_id.fetch_add(1, Ordering::SeqCst);
        let queue = MessageQueue::new(id, owner_pid, config);
        
        let mut queues = self.queues.lock();
        queues.insert(id, queue);
        
        Ok(id)
    }

    /// Get a message queue by ID
    pub fn get_queue(&self, id: IPCId) -> Option<()> {
        let queues = self.queues.lock();
        if queues.contains_key(&id) {
            Some(())
        } else {
            None
        }
    }

    /// Send message to a queue
    pub fn send_message(
        &self,
        queue_id: IPCId,
        msg_type: u32,
        data: Vec<u8>,
        sender_pid: u64,
        priority: MessagePriority,
        flags: MessageFlags,
    ) -> Result<(), IPCError> {
        let queues = self.queues.lock();
        if let Some(queue) = queues.get(&queue_id) {
            queue.send_message(msg_type, data, sender_pid, priority, flags)
        } else {
            Err(IPCError::ResourceNotFound)
        }
    }

    /// Receive message from a queue
    pub fn receive_message(
        &self,
        queue_id: IPCId,
        msg_type: Option<u32>,
        flags: MessageFlags,
    ) -> Result<Option<Message>, IPCError> {
        let queues = self.queues.lock();
        if let Some(queue) = queues.get(&queue_id) {
            queue.receive_message(msg_type, flags)
        } else {
            Err(IPCError::ResourceNotFound)
        }
    }

    /// Remove a message queue
    pub fn remove_queue(&self, id: IPCId) -> Result<(), IPCError> {
        let mut queues = self.queues.lock();
        if queues.remove(&id).is_some() {
            Ok(())
        } else {
            Err(IPCError::ResourceNotFound)
        }
    }

    /// Get statistics for all queues
    pub fn get_global_stats(&self) -> MessageQueueManagerStats {
        let queues = self.queues.lock();
        let mut global_stats = MessageQueueManagerStats::default();
        
        for (_, queue) in queues.iter() {
            let stats = queue.get_stats();
            global_stats.total_queues += 1;
            global_stats.total_messages += stats.total_messages;
            global_stats.total_messages_sent += stats.messages_sent;
            global_stats.total_messages_received += stats.messages_received;
        }
        
        global_stats
    }
}

/// Global statistics for message queue manager
#[derive(Debug, Default)]
pub struct MessageQueueManagerStats {
    pub total_queues: usize,
    pub total_messages: usize,
    pub total_messages_sent: u64,
    pub total_messages_received: u64,
    pub consciousness_optimizations: u64,
}

/// Test functions for message queue functionality
#[cfg(test)]
pub mod tests {
    use super::*;

    /// Test basic message queue operations
    pub fn test_message_queue_basic() -> Result<(), IPCError> {
        let config = MessageQueueConfig::default();
        let queue = MessageQueue::new(1, 1000, config);

        // Send a message
        let data = b"Hello, World!".to_vec();
        queue.send_message(
            1,
            data.clone(),
            1000,
            MessagePriority::Normal,
            MessageFlags::default(),
        )?;

        // Receive the message
        let received = queue.receive_message(Some(1), MessageFlags::default())?;
        assert!(received.is_some());
        
        let msg = received.unwrap();
        assert_eq!(msg.msg_type, 1);
        assert_eq!(msg.data, data);
        assert_eq!(msg.sender_pid, 1000);

        Ok(())
    }

    /// Test consciousness-aware message prioritization
    pub fn test_consciousness_prioritization() -> Result<(), IPCError> {
        let config = MessageQueueConfig::default();
        let queue = MessageQueue::new(2, 1000, config);

        // Send messages with different priorities
        queue.send_message(
            1,
            b"Low priority".to_vec(),
            1000,
            MessagePriority::Low,
            MessageFlags::default(),
        )?;

        queue.send_message(
            2,
            b"High priority".to_vec(),
            1000,
            MessagePriority::High,
            MessageFlags::default(),
        )?;

        queue.send_message(
            3,
            b"Consciousness priority".to_vec(),
            1000,
            MessagePriority::Consciousness,
            MessageFlags::default(),
        )?;

        // Messages should be received in priority order
        let first = queue.receive_message(None, MessageFlags::default())?.unwrap();
        assert_eq!(first.msg_type, 3); // Consciousness priority first

        let second = queue.receive_message(None, MessageFlags::default())?.unwrap();
        assert_eq!(second.msg_type, 2); // High priority second

        let third = queue.receive_message(None, MessageFlags::default())?.unwrap();
        assert_eq!(third.msg_type, 1); // Low priority last

        Ok(())
    }
}
