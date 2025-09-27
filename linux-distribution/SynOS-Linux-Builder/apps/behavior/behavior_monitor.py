#!/usr/bin/env python3

"""
SynOS Behavioral Monitor - Process Behavior Analysis
Monitors system behavior for anomalies
"""

import psutil
import json
import time
import statistics
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List

class BehaviorMonitor:
    def __init__(self):
        self.baseline = {}
        self.process_history = defaultdict(deque)
        self.alerts = []

    def collect_baseline(self, duration: int = 300):
        """Collect baseline behavior over duration seconds"""
        print(f"Collecting baseline over {duration} seconds...")

        start_time = time.time()
        samples = defaultdict(list)

        while time.time() - start_time < duration:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    name = proc.info['name']
                    samples[name].append({
                        'cpu': proc.info['cpu_percent'],
                        'memory': proc.info['memory_percent'],
                        'timestamp': time.time()
                    })
                except:
                    continue

            time.sleep(10)

        # Calculate baselines
        for proc_name, data in samples.items():
            if len(data) >= 3:  # Need sufficient samples
                cpu_values = [d['cpu'] for d in data]
                memory_values = [d['memory'] for d in data]

                self.baseline[proc_name] = {
                    'cpu_mean': statistics.mean(cpu_values),
                    'cpu_stdev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0,
                    'memory_mean': statistics.mean(memory_values),
                    'memory_stdev': statistics.stdev(memory_values) if len(memory_values) > 1 else 0,
                    'sample_count': len(data)
                }

        print(f"Baseline established for {len(self.baseline)} processes")

    def detect_anomalies(self) -> List[Dict]:
        """Detect behavioral anomalies"""
        anomalies = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                name = proc.info['name']

                if name in self.baseline:
                    baseline = self.baseline[name]

                    # CPU anomaly detection
                    cpu_threshold = baseline['cpu_mean'] + (2 * baseline['cpu_stdev'])
                    if proc.info['cpu_percent'] > cpu_threshold and proc.info['cpu_percent'] > 20:
                        anomalies.append({
                            'type': 'cpu_anomaly',
                            'process': name,
                            'pid': proc.info['pid'],
                            'current_cpu': proc.info['cpu_percent'],
                            'baseline_cpu': baseline['cpu_mean'],
                            'severity': 'medium',
                            'timestamp': datetime.now().isoformat()
                        })

                    # Memory anomaly detection
                    memory_threshold = baseline['memory_mean'] + (2 * baseline['memory_stdev'])
                    if proc.info['memory_percent'] > memory_threshold and proc.info['memory_percent'] > 10:
                        anomalies.append({
                            'type': 'memory_anomaly',
                            'process': name,
                            'pid': proc.info['pid'],
                            'current_memory': proc.info['memory_percent'],
                            'baseline_memory': baseline['memory_mean'],
                            'severity': 'medium',
                            'timestamp': datetime.now().isoformat()
                        })

            except:
                continue

        return anomalies

    def monitor_continuously(self):
        """Continuous monitoring loop"""
        print("Starting continuous behavioral monitoring...")

        while True:
            anomalies = self.detect_anomalies()

            if anomalies:
                print(f"\n🚨 {len(anomalies)} anomalies detected:")
                for anomaly in anomalies:
                    print(f"  - {anomaly['type']}: {anomaly['process']} (PID: {anomaly['pid']})")
                    print(f"    Current: {anomaly.get('current_cpu', anomaly.get('current_memory', 0)):.1f}%")

                # Save anomalies
                with open('/tmp/synos_behavior_anomalies.json', 'w') as f:
                    json.dump(anomalies, f, indent=2)

            time.sleep(30)

def main():
    monitor = BehaviorMonitor()

    print("SynOS Behavioral Monitor")
    print("1. Collecting baseline (60 seconds for demo)")
    monitor.collect_baseline(60)

    print("2. Starting continuous monitoring...")
    monitor.monitor_continuously()

if __name__ == "__main__":
    main()
