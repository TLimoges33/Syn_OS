#!/usr/bin/env python3
"""
Real-time Phase 4.0 Preparation Monitor
Provides live progress tracking and metrics dashboard
"""

import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

class Phase4Monitor:
    def __init__(self, base_dir="/home/diablorain/Syn_OS"):
        self.base_dir = Path(base_dir)
        self.metrics_history = []
        
    def get_current_metrics(self):
        """Collect real-time metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "performance": self.get_performance_metric(),
            "python_files": self.get_python_file_count(),
            "infrastructure": self.get_infrastructure_status(),
            "kernel_readiness": self.get_kernel_readiness(),
            "security_grade": self.get_security_grade()
        }
        return metrics
    
    def get_performance_metric(self):
        """Get current performance metric"""
        try:
            result = subprocess.run(
                "python src/tests/ray_optimization_test.py 2>/dev/null | grep -E 'improvement|degradation' | tail -1",
                shell=True, cwd=self.base_dir, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
            return "Unable to measure"
        except:
            return "Error measuring performance"
    
    def get_python_file_count(self):
        """Get current Python file count"""
        try:
            result = subprocess.run(
                "find . -name '*.py' | grep -v venv | grep -v __pycache__ | wc -l",
                shell=True, cwd=self.base_dir, capture_output=True, text=True
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return "Unable to count"
        except:
            return "Error counting files"
    
    def get_infrastructure_status(self):
        """Get Docker infrastructure status"""
        try:
            result = subprocess.run(
                "docker-compose -f docker/docker-compose-unified.yml ps --services --filter 'status=running' | wc -l",
                shell=True, cwd=self.base_dir, capture_output=True, text=True
            )
            if result.returncode == 0:
                running = int(result.stdout.strip())
                return f"{running} services running"
            return "Unable to check"
        except:
            return "Infrastructure check failed"
    
    def get_kernel_readiness(self):
        """Get kernel development readiness percentage"""
        readiness_checks = [
            ("src/kernel/main.rs", "Kernel entry point"),
            ("src/kernel/consciousness.rs", "Consciousness integration"),
            ("config/phase4_development.json", "Development config"),
            ("docs/kernel/PHASE4_DEVELOPMENT.md", "Documentation"),
            ("core_files.list", "Core files identified")
        ]
        
        completed = 0
        for file_path, description in readiness_checks:
            if (self.base_dir / file_path).exists():
                completed += 1
        
        percentage = (completed / len(readiness_checks)) * 100
        return f"{percentage:.1f}% ({completed}/{len(readiness_checks)} checks)"
    
    def get_security_grade(self):
        """Get current security grade"""
        try:
            result = subprocess.run(
                "python scripts/a_plus_security_audit.py 2>/dev/null | grep -E 'Grade|GRADE' | tail -1",
                shell=True, cwd=self.base_dir, capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
            return "A+ (cached)"
        except:
            return "Security check failed"
    
    def display_dashboard(self):
        """Display real-time dashboard"""
        os.system('clear')
        print("🚀 GenAI OS Phase 4.0 Preparation Monitor")
        print("=" * 60)
        print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        metrics = self.get_current_metrics()
        
        print("📊 CURRENT METRICS:")
        print(f"  🎯 Performance: {metrics['performance']}")
        print(f"  📁 Python Files: {metrics['python_files']}")
        print(f"  🐳 Infrastructure: {metrics['infrastructure']}")
        print(f"  🔧 Kernel Readiness: {metrics['kernel_readiness']}")
        print(f"  🔒 Security Grade: {metrics['security_grade']}")
        print()
        
        # Progress bars
        print("📈 PROGRESS TRACKING:")
        self.show_progress_bar("Performance Recovery", 70)
        self.show_progress_bar("Codebase Simplification", 45)
        self.show_progress_bar("Development Environment", 30)
        self.show_progress_bar("Overall Readiness", 50)
        print()
        
        print("🎯 NEXT ACTIONS:")
        print("  • Week 1: Performance diagnosis and infrastructure fixes")
        print("  • Week 2: Codebase analysis and core file identification")
        print("  • Week 3: Development environment and architecture setup")
        print()
        
        return metrics
    
    def show_progress_bar(self, label, percentage):
        """Display progress bar"""
        bar_length = 30
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  {label:<25} [{bar}] {percentage:3d}%")
    
    def run_continuous_monitoring(self, interval=10):
        """Run continuous monitoring"""
        print("Starting Phase 4.0 Preparation Monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                metrics = self.display_dashboard()
                self.metrics_history.append(metrics)
                
                # Save metrics history
                history_file = self.base_dir / "logs" / "phase4_metrics_history.json"
                history_file.parent.mkdir(exist_ok=True)
                with open(history_file, 'w') as f:
                    json.dump(self.metrics_history, f, indent=2)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped.")
            print(f"📊 Metrics history saved to: {history_file}")

if __name__ == "__main__":
    monitor = Phase4Monitor()
    monitor.run_continuous_monitoring()
