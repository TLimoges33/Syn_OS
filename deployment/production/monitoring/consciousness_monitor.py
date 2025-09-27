#!/usr/bin/env python3
"""SynOS Consciousness Real-time Monitoring System"""

import json
import time
from datetime import datetime
import psutil

class ConsciousnessMonitor:
    def __init__(self):
        self.metrics = {
            'neural_activity': 0.0,
            'decision_accuracy': 0.0,
            'learning_rate': 0.0,
            'quantum_coherence': 0.0,
            'response_time': 0.0
        }
        
    def collect_metrics(self):
        """Collect real-time consciousness metrics"""
        # Simulate consciousness metrics based on system performance
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        self.metrics.update({
            'neural_activity': min(95.0, cpu_percent * 1.2),
            'decision_accuracy': 92.5 + (cpu_percent * 0.05),
            'learning_rate': memory.percent * 0.8,
            'quantum_coherence': 85.0 + (10 - cpu_percent/10),
            'response_time': max(50, 200 - cpu_percent * 2),
            'timestamp': datetime.now().isoformat()
        })
        
        return self.metrics
    
    def generate_dashboard_data(self):
        """Generate dashboard JSON for real-time display"""
        metrics = self.collect_metrics()
        dashboard = {
            'status': 'operational',
            'consciousness_health': 'excellent' if metrics['neural_activity'] > 80 else 'good',
            'metrics': metrics,
            'alerts': self.check_alerts(metrics)
        }
        return dashboard
    
    def check_alerts(self, metrics):
        """Check for consciousness system alerts"""
        alerts = []
        if metrics['neural_activity'] < 60:
            alerts.append({'type': 'warning', 'msg': 'Low neural activity'})
        if metrics['response_time'] > 150:
            alerts.append({'type': 'warning', 'msg': 'High response time'})
        return alerts

if __name__ == "__main__":
    monitor = ConsciousnessMonitor()
    print(json.dumps(monitor.generate_dashboard_data(), indent=2))
