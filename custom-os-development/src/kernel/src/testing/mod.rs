/// Testing Module for SynOS Kernel
/// Contains comprehensive test suites for all kernel components

pub mod phase2_ipc_tests;

// Re-export test functions 
pub use phase2_ipc_tests::{run_phase2_priority1_test, test_and_report_phase2_priority1};
