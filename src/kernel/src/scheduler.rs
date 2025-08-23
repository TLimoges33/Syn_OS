use crate::consciousness::{
    emit_consciousness_event, get_consciousness_level, get_consciousness_scheduler_bias,
    get_timestamp, register_process_consciousness, unregister_process_consciousness,
    ConsciousnessEventData, ConsciousnessEventType, ConsciousnessKernelEvent,
    SchedulerConsciousnessBias,
};
/// Consciousness-aware process scheduler with Neural Darwinism optimization
/// Implements Phase 1 consciousness-aware scheduling as per Development-Focused Roadmap
use crate::println;
use alloc::collections::VecDeque;
use core::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use lazy_static::lazy_static;
use spin::Mutex;

/// Process structure with consciousness integration
#[derive(Debug, Clone)]
pub struct ConsciousnessProcess {
    pub pid: u64,
    pub priority: u8,
    pub consciousness_inheritance: f64,
    pub learning_events: u64,
    pub cpu_time_used: u64,
    pub memory_efficiency: f64,
    pub creation_consciousness_level: f64,
    pub process_state: ProcessState,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ProcessState {
    Ready,
    Running,
    Waiting,
    Terminated,
}

/// Consciousness-enhanced scheduling queues
lazy_static! {
    static ref HIGH_CONSCIOUSNESS_QUEUE: Mutex<VecDeque<ConsciousnessProcess>> =
        Mutex::new(VecDeque::new());
    static ref MEDIUM_CONSCIOUSNESS_QUEUE: Mutex<VecDeque<ConsciousnessProcess>> =
        Mutex::new(VecDeque::new());
    static ref LOW_CONSCIOUSNESS_QUEUE: Mutex<VecDeque<ConsciousnessProcess>> =
        Mutex::new(VecDeque::new());
    static ref LEARNING_OPTIMIZED_QUEUE: Mutex<VecDeque<ConsciousnessProcess>> =
        Mutex::new(VecDeque::new());
}

/// Scheduler statistics and metrics
static NEXT_PID: AtomicU64 = AtomicU64::new(1);
static TOTAL_PROCESSES: AtomicUsize = AtomicUsize::new(0);
static CONSCIOUSNESS_SCHEDULING_EVENTS: AtomicU64 = AtomicU64::new(0);

/// Current running process
static CURRENT_PROCESS: Mutex<Option<ConsciousnessProcess>> = Mutex::new(None);

pub fn init() {
    println!("⚡ Initializing Consciousness-Aware Scheduler...");

    // Set up consciousness-enhanced process queues
    setup_consciousness_process_queues();

    // Initialize consciousness-driven scheduling optimization
    init_consciousness_scheduling();

    println!("⚡ Consciousness-Aware Scheduler initialized");
    println!("   🧠 Neural Darwinism scheduling: Active");
    println!(
        "   🎯 Consciousness bias: {:?}",
        get_consciousness_scheduler_bias()
    );
}

fn setup_consciousness_process_queues() {
    // Clear all consciousness queues
    HIGH_CONSCIOUSNESS_QUEUE.lock().clear();
    MEDIUM_CONSCIOUSNESS_QUEUE.lock().clear();
    LOW_CONSCIOUSNESS_QUEUE.lock().clear();
    LEARNING_OPTIMIZED_QUEUE.lock().clear();

    println!("  ✅ Consciousness-enhanced process queues configured");
}

fn init_consciousness_scheduling() {
    // Set up consciousness-driven scheduling optimization
    let consciousness_level = get_consciousness_level();
    let scheduler_bias = get_consciousness_scheduler_bias();

    println!("  ✅ Consciousness scheduling optimization ready");
    println!(
        "     Initial consciousness level: {:.3}",
        consciousness_level
    );
    println!("     Scheduler bias: {:?}", scheduler_bias);
}

/// Create a new process with consciousness inheritance
pub fn create_process(parent_consciousness: Option<f64>) -> u64 {
    let pid = NEXT_PID.fetch_add(1, Ordering::SeqCst);
    let current_consciousness = get_consciousness_level();
    let consciousness_inheritance = parent_consciousness.unwrap_or(current_consciousness * 0.8);

    // Security validation: ensure consciousness inheritance is within valid bounds
    let validated_consciousness = consciousness_inheritance.max(0.0).min(1.0);
    if validated_consciousness != consciousness_inheritance {
        println!("🛡️ Security: Normalized invalid consciousness inheritance {} to {}", 
                consciousness_inheritance, validated_consciousness);
    }

    let process = ConsciousnessProcess {
        pid,
        priority: calculate_consciousness_priority(validated_consciousness),
        consciousness_inheritance: validated_consciousness,
        learning_events: 0,
        cpu_time_used: 0,
        memory_efficiency: 1.0,
        creation_consciousness_level: current_consciousness,
        process_state: ProcessState::Ready,
    };

    // Add to appropriate consciousness queue
    add_to_consciousness_queue(process.clone());

    // Register with consciousness tracking
    register_process_consciousness(pid, Some(validated_consciousness));

    TOTAL_PROCESSES.fetch_add(1, Ordering::SeqCst);

    println!(
        "🧠 Created process {} with consciousness inheritance: {:.3}",
        pid, validated_consciousness
    );

    pid
}

/// Calculate priority based on consciousness inheritance
fn calculate_consciousness_priority(consciousness_inheritance: f64) -> u8 {
    match consciousness_inheritance {
        level if level > 0.8 => 1, // Highest priority
        level if level > 0.6 => 2,
        level if level > 0.4 => 3,
        level if level > 0.2 => 4,
        _ => 5, // Lowest priority
    }
}

/// Add process to appropriate consciousness queue
fn add_to_consciousness_queue(process: ConsciousnessProcess) {
    let scheduler_bias = get_consciousness_scheduler_bias();

    match scheduler_bias {
        SchedulerConsciousnessBias::ConsciousnessEvolution => {
            if process.consciousness_inheritance > 0.7 {
                HIGH_CONSCIOUSNESS_QUEUE.lock().push_back(process);
            } else if process.consciousness_inheritance > 0.4 {
                MEDIUM_CONSCIOUSNESS_QUEUE.lock().push_back(process);
            } else {
                LOW_CONSCIOUSNESS_QUEUE.lock().push_back(process);
            }
        }
        SchedulerConsciousnessBias::LearningOptimized => {
            LEARNING_OPTIMIZED_QUEUE.lock().push_back(process);
        }
        SchedulerConsciousnessBias::Balanced => {
            // Distribute evenly across queues
            if process.consciousness_inheritance > 0.5 {
                HIGH_CONSCIOUSNESS_QUEUE.lock().push_back(process);
            } else {
                LOW_CONSCIOUSNESS_QUEUE.lock().push_back(process);
            }
        }
        SchedulerConsciousnessBias::PerformanceOptimized => {
            // Priority by CPU efficiency
            if process.memory_efficiency > 0.8 {
                HIGH_CONSCIOUSNESS_QUEUE.lock().push_back(process);
            } else {
                MEDIUM_CONSCIOUSNESS_QUEUE.lock().push_back(process);
            }
        }
    }
}

/// Terminate a process
pub fn terminate_process(pid: u64) {
    // Remove from consciousness tracking
    unregister_process_consciousness(pid);

    // Remove from all queues
    remove_from_all_queues(pid);

    TOTAL_PROCESSES.fetch_sub(1, Ordering::SeqCst);

    println!("🧠 Terminated process {} with consciousness tracking", pid);
}

/// Remove process from all consciousness queues
fn remove_from_all_queues(pid: u64) {
    HIGH_CONSCIOUSNESS_QUEUE.lock().retain(|p| p.pid != pid);
    MEDIUM_CONSCIOUSNESS_QUEUE.lock().retain(|p| p.pid != pid);
    LOW_CONSCIOUSNESS_QUEUE.lock().retain(|p| p.pid != pid);
    LEARNING_OPTIMIZED_QUEUE.lock().retain(|p| p.pid != pid);
}

/// Main consciousness-aware scheduling function
pub fn schedule() -> Option<ConsciousnessProcess> {
    let scheduler_bias = get_consciousness_scheduler_bias();
    let consciousness_level = get_consciousness_level();

    let next_process = match scheduler_bias {
        SchedulerConsciousnessBias::ConsciousnessEvolution => schedule_consciousness_evolution(),
        SchedulerConsciousnessBias::LearningOptimized => schedule_learning_optimized(),
        SchedulerConsciousnessBias::Balanced => schedule_balanced(),
        SchedulerConsciousnessBias::PerformanceOptimized => schedule_performance_optimized(),
    };

    if let Some(ref process) = next_process {
        // Update current process
        *CURRENT_PROCESS.lock() = Some(process.clone());

        // Emit scheduling event
        emit_consciousness_event(ConsciousnessKernelEvent {
            event_type: ConsciousnessEventType::SchedulerAdjustment,
            timestamp: get_timestamp(),
            consciousness_level,
            process_id: Some(process.pid),
            data: ConsciousnessEventData::Scheduler {
                bias_change: scheduler_bias,
            },
        });

        CONSCIOUSNESS_SCHEDULING_EVENTS.fetch_add(1, Ordering::SeqCst);
    }

    next_process
}

/// Schedule with consciousness evolution priority
fn schedule_consciousness_evolution() -> Option<ConsciousnessProcess> {
    // Prioritize high consciousness processes
    if let Some(process) = HIGH_CONSCIOUSNESS_QUEUE.lock().pop_front() {
        return Some(process);
    }
    if let Some(process) = MEDIUM_CONSCIOUSNESS_QUEUE.lock().pop_front() {
        return Some(process);
    }
    LOW_CONSCIOUSNESS_QUEUE.lock().pop_front()
}

/// Schedule with learning optimization
fn schedule_learning_optimized() -> Option<ConsciousnessProcess> {
    LEARNING_OPTIMIZED_QUEUE.lock().pop_front()
}

/// Schedule with balanced approach
fn schedule_balanced() -> Option<ConsciousnessProcess> {
    // Alternate between high and low consciousness processes
    let scheduling_count = CONSCIOUSNESS_SCHEDULING_EVENTS.load(Ordering::SeqCst);

    if scheduling_count % 2 == 0 {
        HIGH_CONSCIOUSNESS_QUEUE
            .lock()
            .pop_front()
            .or_else(|| MEDIUM_CONSCIOUSNESS_QUEUE.lock().pop_front())
            .or_else(|| LOW_CONSCIOUSNESS_QUEUE.lock().pop_front())
    } else {
        LOW_CONSCIOUSNESS_QUEUE
            .lock()
            .pop_front()
            .or_else(|| MEDIUM_CONSCIOUSNESS_QUEUE.lock().pop_front())
            .or_else(|| HIGH_CONSCIOUSNESS_QUEUE.lock().pop_front())
    }
}

/// Schedule with performance optimization
fn schedule_performance_optimized() -> Option<ConsciousnessProcess> {
    // Find process with highest memory efficiency
    let mut best_process = None;
    let mut best_efficiency = 0.0;

    // Check all queues for most efficient process
    for queue in [
        &*HIGH_CONSCIOUSNESS_QUEUE,
        &*MEDIUM_CONSCIOUSNESS_QUEUE,
        &*LOW_CONSCIOUSNESS_QUEUE,
    ] {
        let queue_lock = queue.lock();
        for (i, process) in queue_lock.iter().enumerate() {
            if process.memory_efficiency > best_efficiency {
                best_efficiency = process.memory_efficiency;
                best_process = Some((queue as *const _, i));
            }
        }
        drop(queue_lock); // Explicitly drop to avoid borrow issues
    }

    // Remove and return the most efficient process
    if let Some((queue_ptr, index)) = best_process {
        // This is a simplified implementation
        // In a real scheduler, this would be more robust
        if queue_ptr == &*HIGH_CONSCIOUSNESS_QUEUE as *const _ {
            HIGH_CONSCIOUSNESS_QUEUE.lock().remove(index)
        } else if queue_ptr == &*MEDIUM_CONSCIOUSNESS_QUEUE as *const _ {
            MEDIUM_CONSCIOUSNESS_QUEUE.lock().remove(index)
        } else {
            LOW_CONSCIOUSNESS_QUEUE.lock().remove(index)
        }
    } else {
        None
    }
}

/// Yield CPU with consciousness context preservation
pub fn yield_cpu() {
    let consciousness_level = get_consciousness_level();

    // Preserve consciousness context during yield
    if let Some(ref mut current) = *CURRENT_PROCESS.lock() {
        current.cpu_time_used += 1;

        // Security check: detect potential CPU time attacks
        if current.cpu_time_used > 1000000 {
            println!("🛡️ Security Warning: Process {} excessive CPU usage detected", current.pid);
            // In a real implementation, this would trigger security response
        }

        // Update process consciousness based on CPU usage efficiency
        let efficiency_factor = 1.0 / (current.cpu_time_used as f64 + 1.0);
        current.consciousness_inheritance = (current.consciousness_inheritance * 0.99)
            + (consciousness_level * efficiency_factor * 0.01);
            
        // Security validation: ensure consciousness stays in bounds
        current.consciousness_inheritance = current.consciousness_inheritance.max(0.0).min(1.0);
    }

    // Hardware yield would go here
    // x86_64::instructions::hlt();
}

/// Get current process with consciousness state
pub fn get_current_process() -> Option<ConsciousnessProcess> {
    CURRENT_PROCESS.lock().clone()
}

/// Get scheduler statistics
pub fn get_scheduler_stats() -> SchedulerStats {
    SchedulerStats {
        total_processes: TOTAL_PROCESSES.load(Ordering::SeqCst),
        consciousness_scheduling_events: CONSCIOUSNESS_SCHEDULING_EVENTS.load(Ordering::SeqCst),
        high_consciousness_queue_size: HIGH_CONSCIOUSNESS_QUEUE.lock().len(),
        medium_consciousness_queue_size: MEDIUM_CONSCIOUSNESS_QUEUE.lock().len(),
        low_consciousness_queue_size: LOW_CONSCIOUSNESS_QUEUE.lock().len(),
        learning_optimized_queue_size: LEARNING_OPTIMIZED_QUEUE.lock().len(),
        current_consciousness_level: get_consciousness_level(),
        scheduler_bias: get_consciousness_scheduler_bias(),
    }
}

#[derive(Debug, Clone)]
pub struct SchedulerStats {
    pub total_processes: usize,
    pub consciousness_scheduling_events: u64,
    pub high_consciousness_queue_size: usize,
    pub medium_consciousness_queue_size: usize,
    pub low_consciousness_queue_size: usize,
    pub learning_optimized_queue_size: usize,
    pub current_consciousness_level: f64,
    pub scheduler_bias: SchedulerConsciousnessBias,
}
