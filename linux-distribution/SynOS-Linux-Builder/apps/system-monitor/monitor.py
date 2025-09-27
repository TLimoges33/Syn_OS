#!/usr/bin/env python3

"""
SynOS System Monitor - Real-time Dashboard
AI-enhanced system monitoring with security focus
"""

import psutil
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import time
import pandas as pd
from datetime import datetime, timedelta

class SynOSMonitor:
    def __init__(self):
        self.start_time = time.time()

    def get_system_stats(self):
        """Get current system statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory(),
            'disk': psutil.disk_usage('/'),
            'network': psutil.net_io_counters(),
            'processes': len(psutil.pids()),
            'uptime': time.time() - self.start_time
        }

    def get_security_processes(self):
        """Identify security-related processes"""
        security_keywords = ['nmap', 'wireshark', 'metasploit', 'burp', 'nikto']
        security_procs = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if any(keyword in proc.info['name'].lower() for keyword in security_keywords):
                    security_procs.append(proc.info)
            except:
                pass

        return security_procs

    def detect_anomalies(self, stats):
        """Simple anomaly detection"""
        anomalies = []

        if stats['cpu_percent'] > 90:
            anomalies.append("High CPU usage detected")
        if stats['memory'].percent > 85:
            anomalies.append("High memory usage detected")
        if stats['disk'].percent > 90:
            anomalies.append("Disk space critical")

        return anomalies

def main():
    st.set_page_config(page_title="SynOS Monitor", layout="wide")
    st.title("🔒 SynOS System Monitor")

    monitor = SynOSMonitor()

    # Auto-refresh every 5 seconds
    placeholder = st.empty()

    while True:
        with placeholder.container():
            stats = monitor.get_system_stats()

            # Key metrics row
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("CPU Usage", f"{stats['cpu_percent']:.1f}%")
            with col2:
                st.metric("Memory", f"{stats['memory'].percent:.1f}%")
            with col3:
                st.metric("Disk", f"{stats['disk'].percent:.1f}%")
            with col4:
                st.metric("Processes", stats['processes'])

            # Anomaly detection
            anomalies = monitor.detect_anomalies(stats)
            if anomalies:
                st.error("🚨 Anomalies Detected:")
                for anomaly in anomalies:
                    st.write(f"- {anomaly}")

            # Security processes
            sec_procs = monitor.get_security_processes()
            if sec_procs:
                st.subheader("🛡️ Active Security Tools")
                df = pd.DataFrame(sec_procs)
                st.dataframe(df)

        time.sleep(5)

if __name__ == "__main__":
    main()
