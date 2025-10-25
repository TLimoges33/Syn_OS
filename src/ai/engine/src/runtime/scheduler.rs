//! Task Scheduler for AI Runtime
//!
//! Manages scheduling and prioritization of AI tasks across multiple runtimes

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::sync::Arc;
use tokio::sync::{Mutex, RwLock};
use tracing::{debug, info};

/// Task scheduler for AI operations
#[derive(Debug)]
pub struct TaskScheduler {
    task_queue: Arc<Mutex<VecDeque<Task>>>,
    active_tasks: Arc<RwLock<HashMap<TaskId, Task>>>,
    max_concurrent_tasks: usize,
    scheduler_state: SchedulerState,
}

/// Unique task identifier
pub type TaskId = uuid::Uuid;

/// AI task representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: TaskId,
    pub task_type: TaskType,
    pub priority: TaskPriority,
    pub model_path: String,
    pub input_data: Vec<u8>,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub timeout_ms: Option<u64>,
}

/// Types of AI tasks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TaskType {
    Inference,
    Training,
    ModelLoad,
    ModelUnload,
    Validation,
}

/// Task priority levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum TaskPriority {
    Low = 1,
    Normal = 2,
    High = 3,
    Critical = 4,
}

/// Scheduler state
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SchedulerState {
    Stopped,
    Running,
    Paused,
}

impl TaskScheduler {
    /// Create a new task scheduler
    pub fn new(max_concurrent_tasks: usize) -> Self {
        info!(
            "Creating task scheduler with max {} concurrent tasks",
            max_concurrent_tasks
        );

        Self {
            task_queue: Arc::new(Mutex::new(VecDeque::new())),
            active_tasks: Arc::new(RwLock::new(HashMap::new())),
            max_concurrent_tasks,
            scheduler_state: SchedulerState::Stopped,
        }
    }

    /// Start the task scheduler
    pub async fn start(&mut self) -> Result<()> {
        info!("Starting task scheduler");
        self.scheduler_state = SchedulerState::Running;

        // Start background scheduler loop
        self.scheduler_loop().await?;

        Ok(())
    }

    /// Submit a new task for execution
    pub async fn submit_task(&self, task: Task) -> Result<TaskId> {
        debug!("Submitting task: {:?}", task.id);

        let mut queue = self.task_queue.lock().await;
        let task_id = task.id;

        // Insert task based on priority
        let task_id = task.id.clone();
        let task_priority = task.priority.clone();

        self.insert_by_priority(&mut queue, task);

        info!("Task {} queued with priority {:?}", task_id, task_priority);
        Ok(task_id)
    }

    /// Get next task to execute
    pub async fn get_next_task(&self) -> Option<Task> {
        let mut queue = self.task_queue.lock().await;
        queue.pop_front()
    }

    /// Mark task as active
    pub async fn mark_active(&self, task: Task) -> Result<()> {
        let mut active = self.active_tasks.write().await;
        active.insert(task.id, task);
        Ok(())
    }

    /// Mark task as completed
    pub async fn mark_completed(&self, task_id: TaskId) -> Result<()> {
        let mut active = self.active_tasks.write().await;
        if let Some(_task) = active.remove(&task_id) {
            debug!("Task {} completed", task_id);
        }
        Ok(())
    }

    /// Get number of active tasks
    pub async fn active_task_count(&self) -> usize {
        let active = self.active_tasks.read().await;
        active.len()
    }

    /// Check if can accept more tasks
    pub async fn can_accept_task(&self) -> bool {
        self.active_task_count().await < self.max_concurrent_tasks
    }

    /// Stop the scheduler
    pub async fn stop(&mut self) -> Result<()> {
        info!("Stopping task scheduler");
        self.scheduler_state = SchedulerState::Stopped;

        // Wait for active tasks to complete
        loop {
            if self.active_task_count().await == 0 {
                break;
            }
            tokio::time::sleep(std::time::Duration::from_millis(100)).await;
        }

        info!("Task scheduler stopped");
        Ok(())
    }

    /// Insert task in queue based on priority
    fn insert_by_priority(&self, queue: &mut VecDeque<Task>, task: Task) {
        let mut insert_index = queue.len();

        for (index, queued_task) in queue.iter().enumerate() {
            if task.priority > queued_task.priority {
                insert_index = index;
                break;
            }
        }

        queue.insert(insert_index, task);
    }

    /// Main scheduler loop
    async fn scheduler_loop(&self) -> Result<()> {
        info!("Scheduler loop started");

        while self.scheduler_state == SchedulerState::Running {
            // Scheduler logic would go here
            tokio::time::sleep(std::time::Duration::from_millis(10)).await;
        }

        info!("Scheduler loop stopped");
        Ok(())
    }
}

impl Task {
    /// Create a new inference task
    pub fn new_inference(model_path: String, input_data: Vec<u8>, priority: TaskPriority) -> Self {
        Self {
            id: TaskId::new_v4(),
            task_type: TaskType::Inference,
            priority,
            model_path,
            input_data,
            created_at: chrono::Utc::now(),
            timeout_ms: Some(5000), // 5 second default timeout
        }
    }

    /// Create a new model loading task
    pub fn new_model_load(model_path: String, priority: TaskPriority) -> Self {
        Self {
            id: TaskId::new_v4(),
            task_type: TaskType::ModelLoad,
            priority,
            model_path,
            input_data: Vec::new(),
            created_at: chrono::Utc::now(),
            timeout_ms: Some(30000), // 30 second timeout for model loading
        }
    }
}
