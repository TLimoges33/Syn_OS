/// Syscall Optimization Module
/// Fast paths, batching, and hardware acceleration

use crate::syscalls::synos_syscalls::{SyscallArgs, SyscallResult, SyscallError};
use alloc::vec::Vec;

/// Fast-path syscall cache
pub struct SyscallCache {
    /// Recently accessed file descriptors
    fd_cache: [(i32, bool); 8],  // (fd, valid)
    /// Cached PID for getpid
    cached_pid: Option<u64>,
    /// Last syscall number
    last_syscall: u64,
    /// Hit counter
    hits: u64,
    /// Miss counter
    misses: u64,
}

impl SyscallCache {
    pub fn new() -> Self {
        Self {
            fd_cache: [(0, false); 8],
            cached_pid: None,
            last_syscall: 0,
            hits: 0,
            misses: 0,
        }
    }

    /// Check if FD is in cache
    pub fn check_fd(&mut self, fd: i32) -> bool {
        for (cached_fd, valid) in &self.fd_cache {
            if *valid && *cached_fd == fd {
                self.hits += 1;
                return true;
            }
        }
        self.misses += 1;
        false
    }

    /// Cache FD
    pub fn cache_fd(&mut self, fd: i32) {
        // Simple replacement: use first invalid or overwrite oldest
        for entry in &mut self.fd_cache {
            if !entry.1 {
                *entry = (fd, true);
                return;
            }
        }
        // All valid, replace first
        self.fd_cache[0] = (fd, true);
    }

    /// Get cached PID
    pub fn get_cached_pid(&mut self) -> Option<u64> {
        if self.cached_pid.is_some() {
            self.hits += 1;
        } else {
            self.misses += 1;
        }
        self.cached_pid
    }

    /// Set cached PID
    pub fn set_cached_pid(&mut self, pid: u64) {
        self.cached_pid = Some(pid);
    }

    /// Get hit rate
    pub fn hit_rate(&self) -> f64 {
        if self.hits + self.misses == 0 {
            0.0
        } else {
            self.hits as f64 / (self.hits + self.misses) as f64
        }
    }

    /// Record syscall
    pub fn record_syscall(&mut self, num: u64) {
        self.last_syscall = num;
    }
}

/// Batch syscall request
#[derive(Debug, Clone, Copy)]
pub struct BatchSyscall {
    pub syscall_num: u64,
    pub args: SyscallArgs,
}

/// Batch syscall result
#[derive(Debug, Clone)]
pub struct BatchResult {
    pub results: Vec<Result<i64, SyscallError>>,
    pub executed: usize,
    pub failed: usize,
}

/// Syscall batching engine
pub struct SyscallBatcher {
    /// Maximum batch size
    max_batch: usize,
    /// Pending syscalls
    pending: Vec<BatchSyscall>,
}

impl SyscallBatcher {
    pub fn new(max_batch: usize) -> Self {
        Self {
            max_batch,
            pending: Vec::with_capacity(max_batch),
        }
    }

    /// Add syscall to batch
    pub fn add(&mut self, syscall_num: u64, args: SyscallArgs) -> Result<(), &'static str> {
        if self.pending.len() >= self.max_batch {
            return Err("Batch full");
        }

        self.pending.push(BatchSyscall { syscall_num, args });
        Ok(())
    }

    /// Execute batch (would call actual syscall handler)
    pub fn execute<F>(&mut self, mut handler: F) -> BatchResult
    where
        F: FnMut(u64, &SyscallArgs) -> SyscallResult,
    {
        let mut results = Vec::with_capacity(self.pending.len());
        let mut executed = 0;
        let mut failed = 0;

        for batch_call in &self.pending {
            let result = handler(batch_call.syscall_num, &batch_call.args);

            if result.is_ok() {
                executed += 1;
            } else {
                failed += 1;
            }

            results.push(result);
        }

        self.pending.clear();

        BatchResult {
            results,
            executed,
            failed,
        }
    }

    /// Get pending count
    pub fn pending_count(&self) -> usize {
        self.pending.len()
    }

    /// Check if batch is full
    pub fn is_full(&self) -> bool {
        self.pending.len() >= self.max_batch
    }

    /// Clear batch
    pub fn clear(&mut self) {
        self.pending.clear();
    }
}

/// Hardware acceleration hints
#[derive(Debug, Clone, Copy)]
pub enum HwAccelHint {
    None,
    CryptoEngine,      // Use crypto accelerator
    NetworkOffload,    // Use network card offload
    AiAccelerator,     // Use AI/ML accelerator (TPU/NPU)
    VectorUnit,        // Use SIMD/AVX
}

/// Syscall optimizer
pub struct SyscallOptimizer {
    cache: SyscallCache,
    batcher: SyscallBatcher,
    hw_accel_enabled: bool,
}

impl SyscallOptimizer {
    pub fn new(batch_size: usize) -> Self {
        Self {
            cache: SyscallCache::new(),
            batcher: SyscallBatcher::new(batch_size),
            hw_accel_enabled: false,
        }
    }

    /// Enable hardware acceleration
    pub fn enable_hw_accel(&mut self) {
        self.hw_accel_enabled = true;
    }

    /// Get hardware acceleration hint for syscall
    pub fn get_hw_hint(&self, syscall_num: u64) -> HwAccelHint {
        if !self.hw_accel_enabled {
            return HwAccelHint::None;
        }

        match syscall_num {
            25 => HwAccelHint::CryptoEngine,      // crypto_op
            26 => HwAccelHint::CryptoEngine,      // secure_random
            15..=18 => HwAccelHint::NetworkOffload, // network syscalls
            27..=32 => HwAccelHint::AiAccelerator,  // AI syscalls
            _ => HwAccelHint::None,
        }
    }

    /// Optimize syscall execution
    pub fn optimize_syscall(&mut self, syscall_num: u64, args: &SyscallArgs) -> Option<i64> {
        self.cache.record_syscall(syscall_num);

        // Fast path: getpid
        if syscall_num == 8 {
            if let Some(pid) = self.cache.get_cached_pid() {
                return Some(pid as i64);
            }
        }

        // Fast path: close with cached FD
        if syscall_num == 4 {
            let fd = args.arg0 as i32;
            if self.cache.check_fd(fd) {
                // FD was recently used, likely valid
                return Some(0);  // Would actually close
            }
        }

        None // No optimization available
    }

    /// Update cache after syscall
    pub fn update_cache(&mut self, syscall_num: u64, args: &SyscallArgs, result: i64) {
        match syscall_num {
            3 => {
                // open - cache FD
                if result >= 0 {
                    self.cache.cache_fd(result as i32);
                }
            },
            8 => {
                // getpid - cache PID
                self.cache.set_cached_pid(result as u64);
            },
            4 => {
                // close - invalidate FD
                let fd = args.arg0 as i32;
                for entry in &mut self.cache.fd_cache {
                    if entry.1 && entry.0 == fd {
                        entry.1 = false;
                        break;
                    }
                }
            },
            _ => {},
        }
    }

    /// Add to batch
    pub fn batch_add(&mut self, syscall_num: u64, args: SyscallArgs) -> Result<(), &'static str> {
        self.batcher.add(syscall_num, args)
    }

    /// Execute batch
    pub fn batch_execute<F>(&mut self, handler: F) -> BatchResult
    where
        F: FnMut(u64, &SyscallArgs) -> SyscallResult,
    {
        self.batcher.execute(handler)
    }

    /// Get cache statistics
    pub fn cache_stats(&self) -> (u64, u64, f64) {
        (self.cache.hits, self.cache.misses, self.cache.hit_rate())
    }
}

/// Performance statistics
pub struct SyscallPerfStats {
    pub total_syscalls: u64,
    pub fast_path_hits: u64,
    pub batch_executed: u64,
    pub hw_accelerated: u64,
    pub avg_latency_ns: u64,
}

impl SyscallPerfStats {
    pub fn new() -> Self {
        Self {
            total_syscalls: 0,
            fast_path_hits: 0,
            batch_executed: 0,
            hw_accelerated: 0,
            avg_latency_ns: 0,
        }
    }

    /// Record syscall execution
    pub fn record(&mut self, fast_path: bool, batched: bool, hw_accel: bool, latency_ns: u64) {
        self.total_syscalls += 1;

        if fast_path {
            self.fast_path_hits += 1;
        }

        if batched {
            self.batch_executed += 1;
        }

        if hw_accel {
            self.hw_accelerated += 1;
        }

        // Running average
        self.avg_latency_ns = (self.avg_latency_ns * (self.total_syscalls - 1) + latency_ns) / self.total_syscalls;
    }

    /// Get optimization rate
    pub fn optimization_rate(&self) -> f64 {
        if self.total_syscalls == 0 {
            0.0
        } else {
            (self.fast_path_hits + self.batch_executed + self.hw_accelerated) as f64 / self.total_syscalls as f64
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_syscall_cache() {
        let mut cache = SyscallCache::new();

        assert!(!cache.check_fd(3));
        cache.cache_fd(3);
        assert!(cache.check_fd(3));

        assert_eq!(cache.get_cached_pid(), None);
        cache.set_cached_pid(1000);
        assert_eq!(cache.get_cached_pid(), Some(1000));

        assert!(cache.hit_rate() > 0.0);
    }

    #[test]
    fn test_syscall_batcher() {
        let mut batcher = SyscallBatcher::new(10);

        let args = SyscallArgs { arg0: 0, arg1: 0, arg2: 0, arg3: 0, arg4: 0, arg5: 0 };

        assert!(batcher.add(1, args).is_ok());
        assert!(batcher.add(2, args).is_ok());
        assert_eq!(batcher.pending_count(), 2);

        let result = batcher.execute(|num, _args| Ok(num as i64));
        assert_eq!(result.executed, 2);
        assert_eq!(result.failed, 0);
        assert_eq!(batcher.pending_count(), 0);
    }

    #[test]
    fn test_syscall_optimizer() {
        let mut opt = SyscallOptimizer::new(10);

        let args = SyscallArgs { arg0: 0, arg1: 0, arg2: 0, arg3: 0, arg4: 0, arg5: 0 };

        // First getpid - no cache
        assert_eq!(opt.optimize_syscall(8, &args), None);

        // Update cache
        opt.update_cache(8, &args, 1000);

        // Second getpid - cached
        assert_eq!(opt.optimize_syscall(8, &args), Some(1000));

        let (hits, misses, rate) = opt.cache_stats();
        assert!(rate > 0.0);
    }

    #[test]
    fn test_hw_accel_hints() {
        let mut opt = SyscallOptimizer::new(10);

        opt.enable_hw_accel();

        assert!(matches!(opt.get_hw_hint(25), HwAccelHint::CryptoEngine));
        assert!(matches!(opt.get_hw_hint(27), HwAccelHint::AiAccelerator));
        assert!(matches!(opt.get_hw_hint(15), HwAccelHint::NetworkOffload));
        assert!(matches!(opt.get_hw_hint(1), HwAccelHint::None));
    }

    #[test]
    fn test_perf_stats() {
        let mut stats = SyscallPerfStats::new();

        stats.record(true, false, false, 100);
        stats.record(false, true, false, 200);
        stats.record(false, false, true, 150);

        assert_eq!(stats.total_syscalls, 3);
        assert_eq!(stats.fast_path_hits, 1);
        assert_eq!(stats.batch_executed, 1);
        assert_eq!(stats.hw_accelerated, 1);
        assert!(stats.optimization_rate() == 1.0);
    }
}
