/// Advanced Inter-Process Communication for SynOS
/// Pipes, Shared Memory, Message Queues, Semaphores

use alloc::vec::Vec;
use alloc::collections::{BTreeMap, VecDeque};
use alloc::sync::Arc;
use spin::Mutex;

/// Pipe for inter-process communication
pub struct Pipe {
    buffer: VecDeque<u8>,
    capacity: usize,
    read_end_open: bool,
    write_end_open: bool,
}

impl Pipe {
    pub fn new(capacity: usize) -> Self {
        Self {
            buffer: VecDeque::with_capacity(capacity),
            capacity,
            read_end_open: true,
            write_end_open: true,
        }
    }

    /// Write data to pipe
    pub fn write(&mut self, data: &[u8]) -> Result<usize, &'static str> {
        if !self.write_end_open {
            return Err("Write end closed");
        }

        let available = self.capacity - self.buffer.len();
        let to_write = core::cmp::min(data.len(), available);

        for byte in &data[..to_write] {
            self.buffer.push_back(*byte);
        }

        Ok(to_write)
    }

    /// Read data from pipe
    pub fn read(&mut self, buf: &mut [u8]) -> Result<usize, &'static str> {
        if !self.read_end_open {
            return Err("Read end closed");
        }

        let to_read = core::cmp::min(buf.len(), self.buffer.len());

        for i in 0..to_read {
            if let Some(byte) = self.buffer.pop_front() {
                buf[i] = byte;
            }
        }

        Ok(to_read)
    }

    /// Close read end
    pub fn close_read(&mut self) {
        self.read_end_open = false;
    }

    /// Close write end
    pub fn close_write(&mut self) {
        self.write_end_open = false;
    }

    /// Check if pipe is empty
    pub fn is_empty(&self) -> bool {
        self.buffer.is_empty()
    }

    /// Get available space
    pub fn available_space(&self) -> usize {
        self.capacity - self.buffer.len()
    }
}

/// Shared memory region
pub struct SharedMemory {
    pub id: u64,
    pub size: usize,
    pub data: Vec<u8>,
    pub attached_processes: Vec<u64>,
    pub permissions: u32,
}

impl SharedMemory {
    pub fn new(id: u64, size: usize, permissions: u32) -> Self {
        Self {
            id,
            size,
            data: vec![0u8; size],
            attached_processes: Vec::new(),
            permissions,
        }
    }

    /// Attach process to shared memory
    pub fn attach(&mut self, pid: u64) -> Result<(), &'static str> {
        if self.attached_processes.contains(&pid) {
            return Err("Already attached");
        }

        self.attached_processes.push(pid);
        Ok(())
    }

    /// Detach process from shared memory
    pub fn detach(&mut self, pid: u64) -> Result<(), &'static str> {
        let initial_len = self.attached_processes.len();
        self.attached_processes.retain(|p| *p != pid);

        if self.attached_processes.len() == initial_len {
            Err("Not attached")
        } else {
            Ok(())
        }
    }

    /// Read from shared memory
    pub fn read(&self, offset: usize, buf: &mut [u8]) -> Result<usize, &'static str> {
        if offset >= self.size {
            return Err("Offset out of bounds");
        }

        let to_read = core::cmp::min(buf.len(), self.size - offset);
        buf[..to_read].copy_from_slice(&self.data[offset..offset + to_read]);

        Ok(to_read)
    }

    /// Write to shared memory
    pub fn write(&mut self, offset: usize, data: &[u8]) -> Result<usize, &'static str> {
        if offset >= self.size {
            return Err("Offset out of bounds");
        }

        let to_write = core::cmp::min(data.len(), self.size - offset);
        self.data[offset..offset + to_write].copy_from_slice(&data[..to_write]);

        Ok(to_write)
    }

    /// Check if anyone is attached
    pub fn is_attached(&self) -> bool {
        !self.attached_processes.is_empty()
    }
}

/// Message for message queue
#[derive(Debug, Clone)]
pub struct Message {
    pub msg_type: i64,
    pub data: Vec<u8>,
    pub sender_pid: u64,
}

/// Message Queue
pub struct MessageQueue {
    pub id: u64,
    messages: VecDeque<Message>,
    max_messages: usize,
    max_message_size: usize,
}

impl MessageQueue {
    pub fn new(id: u64, max_messages: usize, max_message_size: usize) -> Self {
        Self {
            id,
            messages: VecDeque::with_capacity(max_messages),
            max_messages,
            max_message_size,
        }
    }

    /// Send message to queue
    pub fn send(&mut self, msg: Message) -> Result<(), &'static str> {
        if self.messages.len() >= self.max_messages {
            return Err("Queue full");
        }

        if msg.data.len() > self.max_message_size {
            return Err("Message too large");
        }

        self.messages.push_back(msg);
        Ok(())
    }

    /// Receive message from queue
    pub fn receive(&mut self, msg_type: i64) -> Option<Message> {
        if msg_type == 0 {
            // Get first message
            self.messages.pop_front()
        } else if msg_type > 0 {
            // Get first message of specific type
            if let Some(pos) = self.messages.iter().position(|m| m.msg_type == msg_type) {
                self.messages.remove(pos)
            } else {
                None
            }
        } else {
            // Get message with lowest type <= |msg_type|
            let target = msg_type.abs();
            if let Some(pos) = self.messages.iter().position(|m| m.msg_type <= target) {
                self.messages.remove(pos)
            } else {
                None
            }
        }
    }

    /// Get message count
    pub fn count(&self) -> usize {
        self.messages.len()
    }

    /// Check if queue is empty
    pub fn is_empty(&self) -> bool {
        self.messages.is_empty()
    }

    /// Check if queue is full
    pub fn is_full(&self) -> bool {
        self.messages.len() >= self.max_messages
    }
}

/// Semaphore for synchronization
pub struct Semaphore {
    pub id: u64,
    value: i32,
    max_value: i32,
    waiting_processes: VecDeque<u64>,
}

impl Semaphore {
    pub fn new(id: u64, initial_value: i32, max_value: i32) -> Self {
        Self {
            id,
            value: initial_value,
            max_value,
            waiting_processes: VecDeque::new(),
        }
    }

    /// Wait (P operation / down)
    pub fn wait(&mut self, pid: u64) -> Result<(), &'static str> {
        if self.value > 0 {
            self.value -= 1;
            Ok(())
        } else {
            self.waiting_processes.push_back(pid);
            Err("Would block")
        }
    }

    /// Signal (V operation / up)
    pub fn signal(&mut self) -> Option<u64> {
        if let Some(pid) = self.waiting_processes.pop_front() {
            // Wake up waiting process
            Some(pid)
        } else {
            if self.value < self.max_value {
                self.value += 1;
            }
            None
        }
    }

    /// Try wait (non-blocking)
    pub fn try_wait(&mut self) -> bool {
        if self.value > 0 {
            self.value -= 1;
            true
        } else {
            false
        }
    }

    /// Get current value
    pub fn get_value(&self) -> i32 {
        self.value
    }

    /// Get waiting count
    pub fn waiting_count(&self) -> usize {
        self.waiting_processes.len()
    }
}

/// IPC Manager
pub struct IpcManager {
    pipes: BTreeMap<u64, Arc<Mutex<Pipe>>>,
    shared_memory: BTreeMap<u64, Arc<Mutex<SharedMemory>>>,
    message_queues: BTreeMap<u64, Arc<Mutex<MessageQueue>>>,
    semaphores: BTreeMap<u64, Arc<Mutex<Semaphore>>>,
    next_id: u64,
}

impl IpcManager {
    pub fn new() -> Self {
        Self {
            pipes: BTreeMap::new(),
            shared_memory: BTreeMap::new(),
            message_queues: BTreeMap::new(),
            semaphores: BTreeMap::new(),
            next_id: 1,
        }
    }

    /// Create pipe
    pub fn create_pipe(&mut self, capacity: usize) -> u64 {
        let id = self.next_id;
        self.next_id += 1;

        let pipe = Arc::new(Mutex::new(Pipe::new(capacity)));
        self.pipes.insert(id, pipe);

        id
    }

    /// Create shared memory
    pub fn create_shared_memory(&mut self, size: usize, permissions: u32) -> u64 {
        let id = self.next_id;
        self.next_id += 1;

        let shm = Arc::new(Mutex::new(SharedMemory::new(id, size, permissions)));
        self.shared_memory.insert(id, shm);

        id
    }

    /// Create message queue
    pub fn create_message_queue(&mut self, max_messages: usize, max_message_size: usize) -> u64 {
        let id = self.next_id;
        self.next_id += 1;

        let mq = Arc::new(Mutex::new(MessageQueue::new(id, max_messages, max_message_size)));
        self.message_queues.insert(id, mq);

        id
    }

    /// Create semaphore
    pub fn create_semaphore(&mut self, initial_value: i32, max_value: i32) -> u64 {
        let id = self.next_id;
        self.next_id += 1;

        let sem = Arc::new(Mutex::new(Semaphore::new(id, initial_value, max_value)));
        self.semaphores.insert(id, sem);

        id
    }

    /// Get pipe
    pub fn get_pipe(&self, id: u64) -> Option<Arc<Mutex<Pipe>>> {
        self.pipes.get(&id).cloned()
    }

    /// Get shared memory
    pub fn get_shared_memory(&self, id: u64) -> Option<Arc<Mutex<SharedMemory>>> {
        self.shared_memory.get(&id).cloned()
    }

    /// Get message queue
    pub fn get_message_queue(&self, id: u64) -> Option<Arc<Mutex<MessageQueue>>> {
        self.message_queues.get(&id).cloned()
    }

    /// Get semaphore
    pub fn get_semaphore(&self, id: u64) -> Option<Arc<Mutex<Semaphore>>> {
        self.semaphores.get(&id).cloned()
    }

    /// Remove pipe
    pub fn remove_pipe(&mut self, id: u64) -> bool {
        self.pipes.remove(&id).is_some()
    }

    /// Remove shared memory
    pub fn remove_shared_memory(&mut self, id: u64) -> bool {
        self.shared_memory.remove(&id).is_some()
    }

    /// Remove message queue
    pub fn remove_message_queue(&mut self, id: u64) -> bool {
        self.message_queues.remove(&id).is_some()
    }

    /// Remove semaphore
    pub fn remove_semaphore(&mut self, id: u64) -> bool {
        self.semaphores.remove(&id).is_some()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pipe() {
        let mut pipe = Pipe::new(10);

        assert_eq!(pipe.write(b"hello"), Ok(5));
        assert!(!pipe.is_empty());

        let mut buf = [0u8; 10];
        assert_eq!(pipe.read(&mut buf), Ok(5));
        assert_eq!(&buf[..5], b"hello");
        assert!(pipe.is_empty());
    }

    #[test]
    fn test_shared_memory() {
        let mut shm = SharedMemory::new(1, 100, 0666);

        assert!(shm.attach(100).is_ok());
        assert!(shm.attach(100).is_err());

        assert_eq!(shm.write(0, b"test"), Ok(4));

        let mut buf = [0u8; 10];
        assert_eq!(shm.read(0, &mut buf), Ok(10));
        assert_eq!(&buf[..4], b"test");

        assert!(shm.detach(100).is_ok());
        assert!(!shm.is_attached());
    }

    #[test]
    fn test_message_queue() {
        let mut mq = MessageQueue::new(1, 10, 100);

        let msg = Message {
            msg_type: 1,
            data: b"hello".to_vec(),
            sender_pid: 100,
        };

        assert!(mq.send(msg.clone()).is_ok());
        assert_eq!(mq.count(), 1);

        let received = mq.receive(0);
        assert!(received.is_some());
        assert_eq!(received.unwrap().data, b"hello");
        assert!(mq.is_empty());
    }

    #[test]
    fn test_semaphore() {
        let mut sem = Semaphore::new(1, 1, 1);

        assert!(sem.wait(100).is_ok());
        assert_eq!(sem.get_value(), 0);

        assert!(sem.wait(101).is_err());
        assert_eq!(sem.waiting_count(), 1);

        let woken = sem.signal();
        assert_eq!(woken, Some(101));
        assert_eq!(sem.waiting_count(), 0);
    }

    #[test]
    fn test_ipc_manager() {
        let mut manager = IpcManager::new();

        let pipe_id = manager.create_pipe(100);
        assert!(manager.get_pipe(pipe_id).is_some());

        let shm_id = manager.create_shared_memory(1000, 0666);
        assert!(manager.get_shared_memory(shm_id).is_some());

        let mq_id = manager.create_message_queue(10, 100);
        assert!(manager.get_message_queue(mq_id).is_some());

        let sem_id = manager.create_semaphore(1, 10);
        assert!(manager.get_semaphore(sem_id).is_some());

        assert!(manager.remove_pipe(pipe_id));
        assert!(manager.get_pipe(pipe_id).is_none());
    }
}
