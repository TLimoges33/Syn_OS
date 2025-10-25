/// Signal Handling System for SynOS
/// POSIX-compatible signals with AI-enhanced handling

use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Signal numbers (POSIX-compatible)
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
#[repr(u32)]
pub enum Signal {
    SIGHUP = 1,      // Hangup
    SIGINT = 2,      // Interrupt
    SIGQUIT = 3,     // Quit
    SIGILL = 4,      // Illegal instruction
    SIGTRAP = 5,     // Trace/breakpoint trap
    SIGABRT = 6,     // Aborted
    SIGBUS = 7,      // Bus error
    SIGFPE = 8,      // Floating point exception
    SIGKILL = 9,     // Killed (cannot be caught)
    SIGUSR1 = 10,    // User-defined signal 1
    SIGSEGV = 11,    // Segmentation fault
    SIGUSR2 = 12,    // User-defined signal 2
    SIGPIPE = 13,    // Broken pipe
    SIGALRM = 14,    // Alarm clock
    SIGTERM = 15,    // Terminated
    SIGSTKFLT = 16,  // Stack fault
    SIGCHLD = 17,    // Child status changed
    SIGCONT = 18,    // Continued
    SIGSTOP = 19,    // Stopped (cannot be caught)
    SIGTSTP = 20,    // Stopped (terminal)
    SIGTTIN = 21,    // Stopped (tty input)
    SIGTTOU = 22,    // Stopped (tty output)
    SIGURG = 23,     // Urgent I/O condition
    SIGXCPU = 24,    // CPU time limit exceeded
    SIGXFSZ = 25,    // File size limit exceeded
    SIGVTALRM = 26,  // Virtual timer expired
    SIGPROF = 27,    // Profiling timer expired
    SIGWINCH = 28,   // Window size changed
    SIGIO = 29,      // I/O possible
    SIGPWR = 30,     // Power failure
    SIGSYS = 31,     // Bad system call
}

impl Signal {
    pub fn from_u32(value: u32) -> Option<Self> {
        match value {
            1 => Some(Signal::SIGHUP),
            2 => Some(Signal::SIGINT),
            3 => Some(Signal::SIGQUIT),
            4 => Some(Signal::SIGILL),
            5 => Some(Signal::SIGTRAP),
            6 => Some(Signal::SIGABRT),
            7 => Some(Signal::SIGBUS),
            8 => Some(Signal::SIGFPE),
            9 => Some(Signal::SIGKILL),
            10 => Some(Signal::SIGUSR1),
            11 => Some(Signal::SIGSEGV),
            12 => Some(Signal::SIGUSR2),
            13 => Some(Signal::SIGPIPE),
            14 => Some(Signal::SIGALRM),
            15 => Some(Signal::SIGTERM),
            16 => Some(Signal::SIGSTKFLT),
            17 => Some(Signal::SIGCHLD),
            18 => Some(Signal::SIGCONT),
            19 => Some(Signal::SIGSTOP),
            20 => Some(Signal::SIGTSTP),
            21 => Some(Signal::SIGTTIN),
            22 => Some(Signal::SIGTTOU),
            23 => Some(Signal::SIGURG),
            24 => Some(Signal::SIGXCPU),
            25 => Some(Signal::SIGXFSZ),
            26 => Some(Signal::SIGVTALRM),
            27 => Some(Signal::SIGPROF),
            28 => Some(Signal::SIGWINCH),
            29 => Some(Signal::SIGIO),
            30 => Some(Signal::SIGPWR),
            31 => Some(Signal::SIGSYS),
            _ => None,
        }
    }

    /// Check if signal can be caught
    pub fn is_catchable(&self) -> bool {
        !matches!(self, Signal::SIGKILL | Signal::SIGSTOP)
    }

    /// Get default action
    pub fn default_action(&self) -> SignalAction {
        match self {
            Signal::SIGCHLD | Signal::SIGURG | Signal::SIGWINCH => SignalAction::Ignore,
            Signal::SIGSTOP | Signal::SIGTSTP | Signal::SIGTTIN | Signal::SIGTTOU => SignalAction::Stop,
            Signal::SIGCONT => SignalAction::Continue,
            _ => SignalAction::Terminate,
        }
    }
}

/// Signal actions
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SignalAction {
    Default,              // Use default action
    Ignore,               // Ignore signal
    Terminate,            // Terminate process
    Stop,                 // Stop process
    Continue,             // Continue process
    Handler(u64),         // User handler address
}

/// Signal mask for blocking
#[derive(Debug, Clone)]
pub struct SignalMask {
    blocked: Vec<Signal>,
}

impl SignalMask {
    pub fn new() -> Self {
        Self {
            blocked: Vec::new(),
        }
    }

    pub fn block(&mut self, signal: Signal) {
        if !self.blocked.contains(&signal) {
            self.blocked.push(signal);
        }
    }

    pub fn unblock(&mut self, signal: Signal) {
        self.blocked.retain(|s| *s != signal);
    }

    pub fn is_blocked(&self, signal: Signal) -> bool {
        self.blocked.contains(&signal)
    }

    pub fn block_all(&mut self) {
        for sig in 1..=31 {
            if let Some(signal) = Signal::from_u32(sig) {
                self.block(signal);
            }
        }
    }

    pub fn unblock_all(&mut self) {
        self.blocked.clear();
    }
}

/// Pending signal
#[derive(Debug, Clone)]
pub struct PendingSignal {
    pub signal: Signal,
    pub sender_pid: u64,
    pub value: i32,
}

/// Signal handler registration
pub struct SignalHandler {
    /// Registered handlers
    handlers: BTreeMap<Signal, SignalAction>,
    /// Signal mask
    mask: SignalMask,
    /// Pending signals
    pending: Vec<PendingSignal>,
}

impl SignalHandler {
    pub fn new() -> Self {
        Self {
            handlers: BTreeMap::new(),
            mask: SignalMask::new(),
            pending: Vec::new(),
        }
    }

    /// Register signal handler
    pub fn register(&mut self, signal: Signal, action: SignalAction) -> Result<(), &'static str> {
        if !signal.is_catchable() {
            return Err("Signal cannot be caught");
        }

        self.handlers.insert(signal, action);
        Ok(())
    }

    /// Send signal to process
    pub fn send(&mut self, signal: Signal, sender_pid: u64, value: i32) {
        // Check if blocked
        if self.mask.is_blocked(signal) {
            self.pending.push(PendingSignal {
                signal,
                sender_pid,
                value,
            });
            return;
        }

        // Process signal immediately
        self.process_signal(signal, sender_pid, value);
    }

    /// Process a signal
    fn process_signal(&mut self, signal: Signal, sender_pid: u64, value: i32) {
        let action = self.handlers.get(&signal)
            .copied()
            .unwrap_or(signal.default_action());

        match action {
            SignalAction::Default => {
                // Use default action
                match signal.default_action() {
                    SignalAction::Terminate => {
                        // Process should terminate
                    },
                    SignalAction::Ignore => {
                        // Do nothing
                    },
                    SignalAction::Stop => {
                        // Process should stop
                    },
                    SignalAction::Continue => {
                        // Process should continue
                    },
                    _ => {},
                }
            },
            SignalAction::Ignore => {
                // Do nothing
            },
            SignalAction::Handler(handler_addr) => {
                // Call user handler (in real kernel, set up stack and jump)
                // For now, just note that we would call it
            },
            _ => {
                // Handle other actions
            },
        }
    }

    /// Process pending signals
    pub fn process_pending(&mut self) {
        let pending = core::mem::take(&mut self.pending);

        for sig in pending {
            if !self.mask.is_blocked(sig.signal) {
                self.process_signal(sig.signal, sig.sender_pid, sig.value);
            } else {
                self.pending.push(sig);
            }
        }
    }

    /// Block signal
    pub fn block_signal(&mut self, signal: Signal) {
        self.mask.block(signal);
    }

    /// Unblock signal
    pub fn unblock_signal(&mut self, signal: Signal) {
        self.mask.unblock(signal);
        self.process_pending();
    }

    /// Get pending signals count
    pub fn pending_count(&self) -> usize {
        self.pending.len()
    }
}

/// System-wide signal manager
pub struct SignalManager {
    /// Per-process signal handlers
    process_handlers: BTreeMap<u64, SignalHandler>,
}

impl SignalManager {
    pub fn new() -> Self {
        Self {
            process_handlers: BTreeMap::new(),
        }
    }

    /// Register process for signal handling
    pub fn register_process(&mut self, pid: u64) {
        self.process_handlers.insert(pid, SignalHandler::new());
    }

    /// Unregister process
    pub fn unregister_process(&mut self, pid: u64) {
        self.process_handlers.remove(&pid);
    }

    /// Send signal to process
    pub fn send_signal(&mut self, target_pid: u64, signal: Signal, sender_pid: u64, value: i32) -> Result<(), &'static str> {
        let handler = self.process_handlers.get_mut(&target_pid)
            .ok_or("Process not found")?;

        handler.send(signal, sender_pid, value);
        Ok(())
    }

    /// Register signal handler for process
    pub fn register_handler(&mut self, pid: u64, signal: Signal, action: SignalAction) -> Result<(), &'static str> {
        let handler = self.process_handlers.get_mut(&pid)
            .ok_or("Process not found")?;

        handler.register(signal, action)
    }

    /// Block signal for process
    pub fn block_signal(&mut self, pid: u64, signal: Signal) -> Result<(), &'static str> {
        let handler = self.process_handlers.get_mut(&pid)
            .ok_or("Process not found")?;

        handler.block_signal(signal);
        Ok(())
    }

    /// Unblock signal for process
    pub fn unblock_signal(&mut self, pid: u64, signal: Signal) -> Result<(), &'static str> {
        let handler = self.process_handlers.get_mut(&pid)
            .ok_or("Process not found")?;

        handler.unblock_signal(signal);
        Ok(())
    }

    /// Process all pending signals
    pub fn process_all_pending(&mut self) {
        for handler in self.process_handlers.values_mut() {
            handler.process_pending();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_signal_creation() {
        assert_eq!(Signal::from_u32(2), Some(Signal::SIGINT));
        assert_eq!(Signal::from_u32(100), None);
    }

    #[test]
    fn test_signal_catchable() {
        assert!(Signal::SIGINT.is_catchable());
        assert!(!Signal::SIGKILL.is_catchable());
        assert!(!Signal::SIGSTOP.is_catchable());
    }

    #[test]
    fn test_signal_mask() {
        let mut mask = SignalMask::new();
        assert!(!mask.is_blocked(Signal::SIGINT));

        mask.block(Signal::SIGINT);
        assert!(mask.is_blocked(Signal::SIGINT));

        mask.unblock(Signal::SIGINT);
        assert!(!mask.is_blocked(Signal::SIGINT));
    }

    #[test]
    fn test_signal_handler() {
        let mut handler = SignalHandler::new();

        assert!(handler.register(Signal::SIGINT, SignalAction::Ignore).is_ok());
        assert!(handler.register(Signal::SIGKILL, SignalAction::Ignore).is_err());

        handler.block_signal(Signal::SIGTERM);
        handler.send(Signal::SIGTERM, 100, 0);
        assert_eq!(handler.pending_count(), 1);

        handler.unblock_signal(Signal::SIGTERM);
        assert_eq!(handler.pending_count(), 0);
    }

    #[test]
    fn test_signal_manager() {
        let mut manager = SignalManager::new();

        manager.register_process(1000);
        assert!(manager.send_signal(1000, Signal::SIGINT, 1, 0).is_ok());
        assert!(manager.send_signal(9999, Signal::SIGINT, 1, 0).is_err());

        assert!(manager.register_handler(1000, Signal::SIGUSR1, SignalAction::Ignore).is_ok());
        assert!(manager.block_signal(1000, Signal::SIGUSR2).is_ok());
    }
}
