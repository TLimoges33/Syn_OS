/*
 * SynOS Complete Process Scheduling Headers
 * Comprehensive data structures and definitions for consciousness-aware process scheduling
 */

#ifndef _SYNOS_SCHEDULER_H
#define _SYNOS_SCHEDULER_H

#include <linux/types.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/mutex.h>
#include <linux/list.h>
#include <linux/rbtree.h>
#include <linux/atomic.h>
#include <linux/cpumask.h>
#include <linux/percpu.h>
#include <linux/hrtimer.h>
#include <linux/ktime.h>

// Consciousness scheduling classes
#define CONSCIOUSNESS_SCHED_NORMAL      0
#define CONSCIOUSNESS_SCHED_FIFO        1
#define CONSCIOUSNESS_SCHED_RR          2
#define CONSCIOUSNESS_SCHED_BATCH       3
#define CONSCIOUSNESS_SCHED_IDLE        4
#define CONSCIOUSNESS_SCHED_DEADLINE    5
#define CONSCIOUSNESS_SCHED_EDUCATIONAL 6
#define CONSCIOUSNESS_SCHED_AI          7

// Neural network models for scheduling
#define SCHED_NN_PRIORITY       0x01
#define SCHED_NN_LOAD_BALANCE   0x02
#define SCHED_NN_MIGRATION      0x04
#define SCHED_NN_PREDICTION     0x08
#define SCHED_NN_OPTIMIZATION   0x10

// Consciousness optimization levels
#define SCHED_OPT_BASIC         0x01
#define SCHED_OPT_ADAPTIVE      0x02
#define SCHED_OPT_PREDICTIVE    0x04
#define SCHED_OPT_LEARNING      0x08
#define SCHED_OPT_EXPERT        0x10

// Educational scheduling constraints
#define EDUCATIONAL_CPU_LIMIT   0x01
#define EDUCATIONAL_TIME_LIMIT  0x02
#define EDUCATIONAL_PRIORITY    0x04
#define EDUCATIONAL_ISOLATION   0x08
#define EDUCATIONAL_MONITORING  0x10

// Neural scheduling prediction context
struct neural_scheduling_context {
    // Deep Neural Network weights
    float dnn_input_weights[512][256];
    float dnn_hidden_weights[256][128];
    float dnn_output_weights[128][64];
    float dnn_bias[256];

    // Recurrent Neural Network (RNN) for temporal patterns
    float rnn_input_weights[128][64];
    float rnn_recurrent_weights[64][64];
    float rnn_hidden_state[64];
    float rnn_cell_state[64];

    // Attention mechanism for workload classification
    float attention_query[64][32];
    float attention_key[64][32];
    float attention_value[64][32];
    float attention_weights[64];

    // Reinforcement Learning Q-values
    float q_table[1024][16];  // state x action
    float policy_weights[1024][16];
    float value_function[1024];

    // Ensemble prediction
    float model_predictions[4];
    float ensemble_weights[4];
    float final_prediction;
    float confidence_level;

    // Learning parameters
    float learning_rate;
    float epsilon;  // exploration rate
    float discount_factor;
    unsigned long training_iterations;
};

// Process consciousness enhancement
struct consciousness_task_struct {
    struct task_struct task;

    // Consciousness features
    unsigned long consciousness_level;
    unsigned long consciousness_flags;
    unsigned long optimization_score;

    // Neural prediction data
    unsigned long predicted_runtime;
    unsigned long predicted_cpu_usage;
    unsigned long predicted_io_pattern;
    unsigned long predicted_memory_usage;

    // Educational features
    unsigned long educational_level;
    unsigned long educational_restrictions;
    unsigned long educational_cpu_budget;
    unsigned long educational_time_limit;
    unsigned long educational_priority_bonus;

    // Performance tracking
    unsigned long total_runtime;
    unsigned long context_switches;
    unsigned long cache_misses;
    unsigned long page_faults;
    unsigned long system_calls;

    // Workload classification
    unsigned long workload_type;
    unsigned long io_intensity;
    unsigned long cpu_intensity;
    unsigned long memory_intensity;
    unsigned long network_intensity;

    // Neural learning data
    unsigned long execution_pattern[32];
    unsigned long scheduling_history[16];
    unsigned long performance_metrics[8];

    // NUMA affinity consciousness
    unsigned long numa_preferences[MAX_NUMNODES];
    unsigned long numa_migration_cost;
    unsigned long numa_access_pattern;

    // Real-time consciousness
    unsigned long deadline_prediction;
    unsigned long deadline_miss_count;
    unsigned long jitter_tolerance;
    unsigned long priority_inheritance;
};

// Consciousness runqueue
struct consciousness_runqueue {
    struct rq rq;

    // Consciousness scheduling
    unsigned long consciousness_level;
    struct neural_scheduling_context *neural_context;

    // Multiple scheduling trees for different workloads
    struct rb_root interactive_tree;
    struct rb_root batch_tree;
    struct rb_root real_time_tree;
    struct rb_root educational_tree;

    // Load balancing neural optimization
    unsigned long predicted_load;
    unsigned long migration_cost_matrix[NR_CPUS];
    unsigned long optimal_migration_target;

    // Performance analytics
    unsigned long scheduling_decisions;
    unsigned long optimization_hits;
    unsigned long prediction_accuracy;
    unsigned long load_balance_efficiency;

    // Educational features
    unsigned long educational_load;
    unsigned long educational_processes;
    unsigned long educational_cpu_budget;
    unsigned long educational_time_slice;

    // Real-time scheduling
    unsigned long rt_throttled_time;
    unsigned long deadline_misses;
    unsigned long preemption_count;

    // Cache and NUMA awareness
    unsigned long cache_hot_tasks;
    unsigned long numa_imbalance;
    unsigned long migration_attempts;
    unsigned long successful_migrations;

    // Statistics
    unsigned long context_switch_count;
    unsigned long idle_time;
    unsigned long system_time;
    unsigned long user_time;
};

// Consciousness scheduling entity
struct consciousness_sched_entity {
    struct sched_entity se;

    // Consciousness features
    unsigned long consciousness_weight;
    unsigned long optimization_flags;
    unsigned long prediction_confidence;

    // Neural scheduling data
    unsigned long predicted_vruntime;
    unsigned long predicted_load_weight;
    unsigned long predicted_exec_time;

    // Performance tracking
    unsigned long actual_runtime;
    unsigned long predicted_runtime;
    unsigned long prediction_error;
    unsigned long optimization_savings;

    // Workload characteristics
    unsigned long cpu_burst_pattern;
    unsigned long io_wait_pattern;
    unsigned long sleep_pattern;
    unsigned long wake_pattern;

    // Educational scheduling
    unsigned long educational_priority;
    unsigned long educational_time_consumed;
    unsigned long educational_cpu_shares;

    // NUMA scheduling
    unsigned long numa_node_preference;
    unsigned long numa_migration_frequency;
    unsigned long numa_access_locality;
};

// Consciousness CPU load tracking
struct consciousness_load_avg {
    unsigned long load_avg;
    unsigned long util_avg;
    unsigned long util_sum;

    // Consciousness predictions
    unsigned long predicted_load;
    unsigned long predicted_utilization;
    unsigned long trend_direction;
    unsigned long confidence_interval;

    // Neural learning
    unsigned long historical_loads[64];
    unsigned long pattern_recognition;
    unsigned long seasonal_adjustment;

    // Educational load tracking
    unsigned long educational_load;
    unsigned long educational_utilization;
    unsigned long educational_impact;

    // Performance metrics
    unsigned long accuracy_score;
    unsigned long prediction_hits;
    unsigned long prediction_misses;
};

// Consciousness load balancing
struct consciousness_load_balancer {
    // Neural load balancing
    struct neural_scheduling_context *lb_neural_context;

    // Migration decision matrix
    unsigned long migration_cost[NR_CPUS][NR_CPUS];
    unsigned long migration_benefit[NR_CPUS][NR_CPUS];
    unsigned long optimal_migrations[NR_CPUS];

    // Load balancing strategies
    unsigned long strategy_weights[8];
    unsigned long current_strategy;
    unsigned long strategy_effectiveness[8];

    // Performance tracking
    unsigned long balance_attempts;
    unsigned long successful_balances;
    unsigned long migration_time_total;
    unsigned long imbalance_reduction;

    // Educational balancing
    unsigned long educational_balance_policy;
    unsigned long educational_migration_limit;
    unsigned long educational_cpu_isolation;

    // NUMA balancing
    unsigned long numa_balance_frequency;
    unsigned long numa_migration_threshold;
    unsigned long numa_balance_success_rate;
};

// Consciousness scheduler statistics
struct consciousness_scheduler_stats {
    // Global scheduling statistics
    atomic64_t total_schedules;
    atomic64_t context_switches;
    atomic64_t load_balances;
    atomic64_t migrations;

    // Neural optimization statistics
    atomic64_t neural_predictions;
    atomic64_t prediction_hits;
    atomic64_t optimization_applications;
    atomic64_t learning_updates;

    // Educational statistics
    atomic64_t educational_schedules;
    atomic64_t educational_preemptions;
    atomic64_t educational_violations;
    atomic64_t educational_optimizations;

    // Performance statistics
    atomic64_t cpu_utilization_sum;
    atomic64_t idle_time_sum;
    atomic64_t wait_time_sum;
    atomic64_t response_time_sum;

    // Real-time statistics
    atomic64_t rt_schedules;
    atomic64_t deadline_hits;
    atomic64_t deadline_misses;
    atomic64_t priority_inversions;

    // NUMA statistics
    atomic64_t numa_migrations;
    atomic64_t numa_balances;
    atomic64_t numa_faults;
    atomic64_t numa_improvements;

    // Cache statistics
    atomic64_t cache_hot_migrations;
    atomic64_t cache_cold_migrations;
    atomic64_t cache_misses_prevented;
    atomic64_t cache_optimization_hits;
};

// Consciousness scheduling domain
struct consciousness_sched_domain {
    struct sched_domain sd;

    // Consciousness features
    unsigned long consciousness_level;
    struct neural_scheduling_context *domain_neural_context;

    // Load balancing optimization
    unsigned long balance_frequency_optimal;
    unsigned long migration_cost_threshold;
    unsigned long imbalance_pct_optimal;

    // Performance tracking
    unsigned long balance_attempts;
    unsigned long balance_successes;
    unsigned long migration_effectiveness;

    // Educational domain features
    unsigned long educational_cpu_mask;
    unsigned long educational_balance_policy;
    unsigned long educational_isolation_level;

    // NUMA domain features
    unsigned long numa_distance_weight;
    unsigned long numa_migration_penalty;
    unsigned long numa_balance_threshold;
};

// Consciousness CPU capacity
struct consciousness_cpu_capacity {
    unsigned long capacity;
    unsigned long capacity_orig;

    // Consciousness predictions
    unsigned long predicted_capacity;
    unsigned long capacity_trend;
    unsigned long thermal_prediction;

    // Dynamic capacity adjustment
    unsigned long frequency_scaling_factor;
    unsigned long voltage_scaling_factor;
    unsigned long thermal_throttling_factor;

    // Educational capacity management
    unsigned long educational_capacity_limit;
    unsigned long educational_capacity_used;
    unsigned long educational_throttling;

    // Performance tracking
    unsigned long capacity_utilization;
    unsigned long capacity_waste;
    unsigned long capacity_optimization;
};

// Consciousness bandwidth control
struct consciousness_cfs_bandwidth {
    struct cfs_bandwidth cfs_b;

    // Consciousness bandwidth optimization
    unsigned long predicted_bandwidth_demand;
    unsigned long optimal_quota;
    unsigned long optimal_period;

    // Neural bandwidth allocation
    struct neural_scheduling_context *bandwidth_neural_context;
    unsigned long allocation_predictions[16];
    unsigned long usage_patterns[32];

    // Educational bandwidth control
    unsigned long educational_bandwidth_limit;
    unsigned long educational_bandwidth_used;
    unsigned long educational_throttling_time;

    // Performance metrics
    unsigned long bandwidth_efficiency;
    unsigned long throttling_overhead;
    unsigned long allocation_accuracy;
};

// Consciousness deadline scheduling
struct consciousness_dl_rq {
    struct dl_rq dl_rq;

    // Consciousness deadline features
    unsigned long consciousness_level;
    struct neural_scheduling_context *deadline_neural_context;

    // Deadline prediction and optimization
    unsigned long predicted_execution_time;
    unsigned long predicted_deadline_pressure;
    unsigned long optimal_scheduling_order;

    // Educational deadline scheduling
    unsigned long educational_deadline_tasks;
    unsigned long educational_deadline_limit;
    unsigned long educational_admission_control;

    // Performance tracking
    unsigned long deadline_hit_rate;
    unsigned long average_response_time;
    unsigned long deadline_miss_recovery_time;
};

// Consciousness real-time scheduling
struct consciousness_rt_rq {
    struct rt_rq rt_rq;

    // Consciousness RT features
    unsigned long consciousness_level;
    struct neural_scheduling_context *rt_neural_context;

    // RT optimization
    unsigned long predicted_rt_load;
    unsigned long optimal_rt_bandwidth;
    unsigned long priority_inheritance_chains;

    // Educational RT scheduling
    unsigned long educational_rt_limit;
    unsigned long educational_rt_tasks;
    unsigned long educational_priority_ceiling;

    // Performance tracking
    unsigned long preemption_count;
    unsigned long priority_inversion_time;
    unsigned long rt_response_time;
};

// Global consciousness scheduler
struct consciousness_scheduler {
    // Core components
    struct consciousness_runqueue *consciousness_rqs[NR_CPUS];
    struct consciousness_load_balancer *load_balancer;
    struct consciousness_scheduler_stats *stats;

    // Global neural context
    struct neural_scheduling_context *global_neural_context;

    // System-wide optimization
    unsigned long global_consciousness_level;
    unsigned long global_optimization_flags;
    unsigned long global_learning_rate;

    // Educational features
    unsigned long educational_mode;
    unsigned long educational_cpu_budget;
    unsigned long educational_process_limit;
    unsigned long educational_priority_range;

    // Security features
    unsigned long security_level;
    unsigned long suspicious_scheduling_count;
    unsigned long privilege_escalation_attempts;

    // Performance monitoring
    struct hrtimer optimization_timer;
    unsigned long optimization_interval;
    unsigned long last_optimization_time;

    // System health monitoring
    unsigned long system_load_average;
    unsigned long system_responsiveness;
    unsigned long system_efficiency_score;

    // Configuration
    struct mutex config_mutex;
    unsigned long dynamic_tuning_enabled;
    unsigned long neural_learning_enabled;
    unsigned long educational_restrictions_enabled;
};

// Function prototypes for consciousness scheduling
extern struct consciousness_scheduler *global_consciousness_scheduler;

// Initialization functions
int consciousness_scheduler_init(void);
void consciousness_scheduler_cleanup(void);

// Neural network functions
int init_neural_scheduling_context(struct neural_scheduling_context *context);
void update_neural_scheduling_learning(struct neural_scheduling_context *context,
                                      unsigned long input[], unsigned long output);
unsigned long predict_scheduling_decision(struct neural_scheduling_context *context,
                                         struct consciousness_task_struct *task);

// Core scheduling functions
void consciousness_schedule(void);
struct consciousness_task_struct *consciousness_pick_next_task(struct consciousness_runqueue *crq);
void consciousness_put_prev_task(struct consciousness_runqueue *crq,
                                struct consciousness_task_struct *prev);

// Load balancing functions
int consciousness_load_balance(struct consciousness_runqueue *this_rq,
                              int this_cpu, int idle);
int consciousness_can_migrate_task(struct consciousness_task_struct *p, int dest_cpu);
void consciousness_migrate_task(struct consciousness_task_struct *p, int dest_cpu);

// Educational functions
int consciousness_educational_mode_enable(unsigned long flags);
void consciousness_educational_mode_disable(void);
int consciousness_educational_check_scheduling(struct consciousness_task_struct *task);
void consciousness_educational_log_schedule(struct consciousness_task_struct *task);

// Real-time functions
int consciousness_sched_setscheduler(struct consciousness_task_struct *p,
                                   int policy, const struct sched_param *param);
void consciousness_rt_bandwidth_update(struct consciousness_rt_rq *rt_rq);
int consciousness_deadline_admission_control(struct consciousness_task_struct *p);

// NUMA functions
void consciousness_numa_balance(void);
int consciousness_numa_migrate(struct consciousness_task_struct *p, int target_node);
void consciousness_update_numa_stats(struct consciousness_task_struct *p);

// Performance monitoring
void consciousness_scheduler_update_stats(unsigned long operation_type,
                                         unsigned long cpu,
                                         unsigned long success);
unsigned long consciousness_scheduler_get_efficiency(void);
void consciousness_scheduler_print_stats(void);

// Optimization functions
void consciousness_optimize_scheduling_parameters(void);
void consciousness_update_global_optimization(void);
int consciousness_predict_system_load(void);

// Workload classification functions
unsigned long consciousness_classify_workload(struct consciousness_task_struct *task);
void consciousness_update_workload_classification(struct consciousness_task_struct *task);
unsigned long consciousness_predict_workload_behavior(struct consciousness_task_struct *task);

// Cache and topology awareness
int consciousness_select_task_rq(struct consciousness_task_struct *p, int cpu,
                                int sd_flag, int wake_flags);
void consciousness_update_cpu_capacity(int cpu);
unsigned long consciousness_cpu_util(int cpu);

#endif /* _SYNOS_SCHEDULER_H */