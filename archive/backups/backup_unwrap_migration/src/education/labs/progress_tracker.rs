/// Progress Tracker for Educational Labs
/// Tracks student learning analytics and progress

use alloc::collections::BTreeMap;
use alloc::vec::Vec;

/// Learning metric
#[derive(Debug, Clone)]
pub struct LearningMetric {
    pub metric_name: &'static str,
    pub value: f32,
    pub timestamp: u64,
}

/// Progress snapshot
#[derive(Debug, Clone)]
pub struct ProgressSnapshot {
    pub student_id: u64,
    pub timestamp: u64,
    pub labs_completed: u32,
    pub total_points: u32,
    pub time_spent_mins: u64,
    pub success_rate: f32,
}

/// Progress tracker
pub struct ProgressTracker {
    metrics: BTreeMap<u64, Vec<LearningMetric>>, // student_id -> metrics
    snapshots: BTreeMap<u64, Vec<ProgressSnapshot>>, // student_id -> snapshots
    lab_attempts: BTreeMap<(u64, u64), u32>, // (student_id, lab_id) -> attempts
}

impl ProgressTracker {
    pub fn new() -> Self {
        Self {
            metrics: BTreeMap::new(),
            snapshots: BTreeMap::new(),
            lab_attempts: BTreeMap::new(),
        }
    }

    /// Record learning metric
    pub fn record_metric(&mut self, student_id: u64, metric_name: &'static str, value: f32) {
        let metric = LearningMetric {
            metric_name,
            value,
            timestamp: 0, // Would use actual timestamp
        };

        self.metrics.entry(student_id)
            .or_insert_with(Vec::new)
            .push(metric);
    }

    /// Record lab attempt
    pub fn record_attempt(&mut self, student_id: u64, lab_id: u64) {
        let key = (student_id, lab_id);
        *self.lab_attempts.entry(key).or_insert(0) += 1;
    }

    /// Get attempt count
    pub fn get_attempt_count(&self, student_id: u64, lab_id: u64) -> u32 {
        self.lab_attempts.get(&(student_id, lab_id)).copied().unwrap_or(0)
    }

    /// Create progress snapshot
    pub fn create_snapshot(&mut self, student_id: u64, labs_completed: u32, total_points: u32, time_spent_mins: u64) {
        let attempts = self.lab_attempts.iter()
            .filter(|((sid, _), _)| *sid == student_id)
            .count() as u32;

        let success_rate = if attempts > 0 {
            labs_completed as f32 / attempts as f32
        } else {
            0.0
        };

        let snapshot = ProgressSnapshot {
            student_id,
            timestamp: 0,
            labs_completed,
            total_points,
            time_spent_mins,
            success_rate,
        };

        self.snapshots.entry(student_id)
            .or_insert_with(Vec::new)
            .push(snapshot);
    }

    /// Get learning velocity (labs per week)
    pub fn get_learning_velocity(&self, student_id: u64) -> f32 {
        if let Some(snapshots) = self.snapshots.get(&student_id) {
            if snapshots.len() < 2 {
                return 0.0;
            }

            let first = &snapshots[0];
            let last = &snapshots[snapshots.len() - 1];

            let time_diff_weeks = (last.timestamp - first.timestamp) as f32 / (7.0 * 24.0 * 60.0 * 60.0);
            if time_diff_weeks > 0.0 {
                (last.labs_completed - first.labs_completed) as f32 / time_diff_weeks
            } else {
                0.0
            }
        } else {
            0.0
        }
    }

    /// Get average time per lab
    pub fn get_avg_time_per_lab(&self, student_id: u64) -> u64 {
        if let Some(snapshots) = self.snapshots.get(&student_id) {
            if let Some(latest) = snapshots.last() {
                if latest.labs_completed > 0 {
                    return latest.time_spent_mins / latest.labs_completed as u64;
                }
            }
        }
        0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metric_recording() {
        let mut tracker = ProgressTracker::new();

        tracker.record_metric(1, "engagement", 0.85);
        assert!(tracker.metrics.get(&1).is_some());
    }

    #[test]
    fn test_attempt_tracking() {
        let mut tracker = ProgressTracker::new();

        tracker.record_attempt(1, 100);
        tracker.record_attempt(1, 100);

        assert_eq!(tracker.get_attempt_count(1, 100), 2);
    }

    #[test]
    fn test_snapshot_creation() {
        let mut tracker = ProgressTracker::new();

        tracker.create_snapshot(1, 5, 500, 300);

        assert!(tracker.snapshots.get(&1).is_some());
    }
}
