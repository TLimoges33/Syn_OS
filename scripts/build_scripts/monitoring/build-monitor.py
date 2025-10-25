#!/usr/bin/env python3

"""
SynOS Ultimate Build Monitor
Independent monitoring system that tracks build progress and system health
Can run in web browser when terminal has issues
"""

import http.server
import socketserver
import json
import time
import os
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path

class BuildMonitor:
    def __init__(self):
        self.build_dir = Path("/home/diablorain/Syn_OS/build")
        self.monitor_data = {
            'system': {},
            'build': {},
            'logs': [],
            'alerts': [],
            'status': 'ready'
        }
        self.monitoring = False
        
    def get_system_stats(self):
        """Get current system statistics"""
        try:
            # Memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            mem_total = int([line for line in meminfo.split('\n') if 'MemTotal:' in line][0].split()[1])
            mem_free = int([line for line in meminfo.split('\n') if 'MemFree:' in line][0].split()[1])
            mem_available = int([line for line in meminfo.split('\n') if 'MemAvailable:' in line][0].split()[1])
            mem_used_percent = ((mem_total - mem_available) / mem_total) * 100
            
            # Load average
            with open('/proc/loadavg', 'r') as f:
                load_avg = float(f.read().split()[0])
            
            # Disk usage for /tmp
            disk_usage = subprocess.run(['df', '/tmp'], capture_output=True, text=True)
            if disk_usage.returncode == 0:
                disk_line = disk_usage.stdout.split('\n')[1]
                disk_parts = disk_line.split()
                disk_free_gb = int(disk_parts[3]) / (1024 * 1024)
                disk_used_percent = int(disk_parts[4].replace('%', ''))
            else:
                disk_free_gb = 0
                disk_used_percent = 0
            
            # CPU usage (simplified)
            cpu_percent = 0
            try:
                cpu_info = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=5)
                if cpu_info.returncode == 0:
                    for line in cpu_info.stdout.split('\n'):
                        if 'Cpu(s):' in line:
                            # Extract CPU usage percentage
                            parts = line.split(',')
                            if len(parts) > 0:
                                idle_part = [p for p in parts if 'id' in p]
                                if idle_part:
                                    idle_percent = float(idle_part[0].split('%')[0].split()[-1])
                                    cpu_percent = 100 - idle_percent
                            break
            except:
                pass
            
            return {
                'memory_used_percent': round(mem_used_percent, 1),
                'memory_free_gb': round(mem_available / (1024 * 1024), 2),
                'load_average': load_avg,
                'disk_free_gb': round(disk_free_gb, 2),
                'disk_used_percent': disk_used_percent,
                'cpu_percent': round(cpu_percent, 1),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_build_status(self):
        """Check current build status"""
        build_files = {
            'ultimate_log': self.build_dir / 'synos-ultimate' / 'ultimate-build.log',
            'monitor_log': self.build_dir / 'synos-ultimate' / 'system-monitor.log',
            'error_log': self.build_dir / 'synos-ultimate' / 'ultimate-errors.log',
            'iso_file': None
        }
        
        # Look for ISO files
        if self.build_dir.exists():
            iso_files = list(self.build_dir.glob('SynOS-v*.iso'))
            if iso_files:
                build_files['iso_file'] = iso_files[-1]  # Most recent
        
        status = {
            'files_exist': {},
            'build_progress': 'unknown',
            'last_activity': None,
            'iso_ready': False
        }
        
        for name, path in build_files.items():
            if path and path.exists():
                status['files_exist'][name] = {
                    'path': str(path),
                    'size': path.stat().st_size,
                    'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
                
                if name == 'ultimate_log':
                    # Try to determine build progress from log
                    try:
                        with open(path, 'r') as f:
                            lines = f.readlines()[-20:]  # Last 20 lines
                        
                        for line in reversed(lines):
                            if '[STEP]' in line:
                                status['build_progress'] = line.split('[STEP]')[1].strip()
                                break
                            elif '[SUCCESS]' in line and 'completed' in line.lower():
                                status['build_progress'] = 'completed'
                                break
                    except:
                        pass
                        
                elif name == 'iso_file':
                    status['iso_ready'] = True
                    status['iso_size'] = f"{path.stat().st_size / (1024**3):.2f} GB"
            else:
                status['files_exist'][name] = None
        
        return status
    
    def get_recent_logs(self, max_lines=50):
        """Get recent log entries"""
        logs = []
        log_files = [
            self.build_dir / 'synos-ultimate' / 'ultimate-build.log',
            self.build_dir / 'synos-ultimate' / 'ultimate-errors.log'
        ]
        
        for log_file in log_files:
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-max_lines:]
                    
                    for line in lines:
                        if line.strip():
                            logs.append({
                                'file': log_file.name,
                                'content': line.strip(),
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass
        
        return logs[-max_lines:]  # Return most recent entries
    
    def continuous_monitoring(self):
        """Continuous monitoring loop"""
        while self.monitoring:
            try:
                self.monitor_data['system'] = self.get_system_stats()
                self.monitor_data['build'] = self.check_build_status()
                self.monitor_data['logs'] = self.get_recent_logs()
                self.monitor_data['last_update'] = datetime.now().isoformat()
                
                # Check for alerts
                system = self.monitor_data['system']
                if 'memory_used_percent' in system:
                    if system['memory_used_percent'] > 80:
                        self.monitor_data['alerts'].append({
                            'type': 'memory',
                            'level': 'warning',
                            'message': f"High memory usage: {system['memory_used_percent']}%",
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Keep only recent alerts (last hour)
                hour_ago = datetime.now() - timedelta(hours=1)
                self.monitor_data['alerts'] = [
                    alert for alert in self.monitor_data['alerts']
                    if datetime.fromisoformat(alert['timestamp']) > hour_ago
                ]
                
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            time.sleep(5)  # Update every 5 seconds

class MonitorHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, monitor, *args, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/monitor':
            self.send_monitor_dashboard()
        elif self.path == '/api/status':
            self.send_json_response(self.monitor.monitor_data)
        elif self.path == '/api/system':
            self.send_json_response(self.monitor.get_system_stats())
        elif self.path == '/api/build':
            self.send_json_response(self.monitor.check_build_status())
        else:
            self.send_404()
    
    def send_monitor_dashboard(self):
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>SynOS Ultimate Build Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ 
            font-family: 'Courier New', monospace; 
            background: #0d1117; 
            color: #c9d1d9; 
            margin: 0; 
            padding: 20px; 
        }}
        .header {{ 
            text-align: center; 
            border: 2px solid #30363d; 
            padding: 20px; 
            margin-bottom: 20px; 
            background: #161b22;
        }}
        .dashboard {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }}
        .panel {{ 
            background: #161b22; 
            border: 1px solid #30363d; 
            padding: 15px; 
            border-radius: 8px; 
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 8px 0; 
            padding: 8px; 
            background: #21262d; 
            border-radius: 4px; 
        }}
        .status-ok {{ color: #238636; }}
        .status-warning {{ color: #d29922; }}
        .status-error {{ color: #f85149; }}
        .progress-bar {{ 
            width: 100%; 
            height: 20px; 
            background: #21262d; 
            border-radius: 10px; 
            overflow: hidden; 
            margin: 10px 0; 
        }}
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #238636, #2ea043); 
            transition: width 0.3s ease; 
        }}
        .log-entry {{ 
            font-size: 12px; 
            margin: 4px 0; 
            padding: 4px; 
            background: #0d1117; 
            border-left: 3px solid #30363d; 
        }}
        .log-error {{ border-left-color: #f85149; }}
        .log-warning {{ border-left-color: #d29922; }}
        .log-success {{ border-left-color: #238636; }}
        .refresh-btn {{ 
            background: #238636; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 6px; 
            cursor: pointer; 
            margin: 10px 5px; 
        }}
        .refresh-btn:hover {{ background: #2ea043; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 SynOS Ultimate Build Monitor</h1>
        <p>Real-time monitoring for ISO build process</p>
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        <button class="refresh-btn" onclick="toggleAutoRefresh()">⏰ Auto-refresh: <span id="auto-status">OFF</span></button>
    </div>
    
    <div class="dashboard">
        <div class="panel">
            <h3>💻 System Resources</h3>
            <div id="system-metrics">Loading...</div>
        </div>
        
        <div class="panel">
            <h3>🔧 Build Status</h3>
            <div id="build-status">Loading...</div>
        </div>
        
        <div class="panel">
            <h3>🚨 Alerts & Warnings</h3>
            <div id="alerts">Loading...</div>
        </div>
        
        <div class="panel" style="grid-column: 1 / -1;">
            <h3>📝 Recent Build Logs</h3>
            <div id="recent-logs" style="max-height: 300px; overflow-y: auto;">Loading...</div>
        </div>
    </div>
    
    <script>
        let autoRefresh = false;
        let refreshInterval;
        
        function updateStatus() {{
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {{
                    updateSystemMetrics(data.system);
                    updateBuildStatus(data.build);
                    updateAlerts(data.alerts);
                    updateLogs(data.logs);
                }})
                .catch(error => {{
                    console.error('Update failed:', error);
                    document.getElementById('system-metrics').innerHTML = '<div class="status-error">Connection failed</div>';
                }});
        }}
        
        function updateSystemMetrics(system) {{
            if (!system) return;
            
            let html = '';
            if (system.memory_used_percent !== undefined) {{
                const memClass = system.memory_used_percent > 80 ? 'status-error' : 
                               system.memory_used_percent > 60 ? 'status-warning' : 'status-ok';
                html += `<div class="metric">
                    <span>Memory Usage:</span>
                    <span class="${{memClass}}">${{system.memory_used_percent}}%</span>
                </div>`;
                
                html += `<div class="progress-bar">
                    <div class="progress-fill" style="width: ${{system.memory_used_percent}}%"></div>
                </div>`;
                
                html += `<div class="metric">
                    <span>Free Memory:</span>
                    <span>${{system.memory_free_gb}} GB</span>
                </div>`;
                
                html += `<div class="metric">
                    <span>Load Average:</span>
                    <span>${{system.load_average}}</span>
                </div>`;
                
                html += `<div class="metric">
                    <span>Disk Free:</span>
                    <span>${{system.disk_free_gb}} GB</span>
                </div>`;
                
                html += `<div class="metric">
                    <span>CPU Usage:</span>
                    <span>${{system.cpu_percent}}%</span>
                </div>`;
            }} else {{
                html = '<div class="status-error">System metrics unavailable</div>';
            }}
            
            document.getElementById('system-metrics').innerHTML = html;
        }}
        
        function updateBuildStatus(build) {{
            if (!build) return;
            
            let html = `<div class="metric">
                <span>Status:</span>
                <span class="status-ok">${{build.build_progress || 'Unknown'}}</span>
            </div>`;
            
            if (build.iso_ready) {{
                html += `<div class="metric">
                    <span>ISO Ready:</span>
                    <span class="status-ok">✅ ${{build.iso_size || 'Yes'}}</span>
                </div>`;
            }}
            
            if (build.files_exist) {{
                Object.entries(build.files_exist).forEach(([name, info]) => {{
                    if (info) {{
                        const sizeKB = Math.round(info.size / 1024);
                        html += `<div class="metric">
                            <span>${{name}}:</span>
                            <span class="status-ok">${{sizeKB}} KB</span>
                        </div>`;
                    }}
                }});
            }}
            
            document.getElementById('build-status').innerHTML = html;
        }}
        
        function updateAlerts(alerts) {{
            let html = '';
            if (alerts && alerts.length > 0) {{
                alerts.forEach(alert => {{
                    const alertClass = alert.level === 'error' ? 'status-error' : 'status-warning';
                    html += `<div class="metric">
                        <span class="${{alertClass}}">${{alert.type}}:</span>
                        <span>${{alert.message}}</span>
                    </div>`;
                }});
            }} else {{
                html = '<div class="status-ok">No active alerts</div>';
            }}
            
            document.getElementById('alerts').innerHTML = html;
        }}
        
        function updateLogs(logs) {{
            let html = '';
            if (logs && logs.length > 0) {{
                logs.slice(-20).forEach(log => {{
                    let logClass = 'log-entry';
                    if (log.content.includes('[ERROR]')) logClass += ' log-error';
                    else if (log.content.includes('[WARNING]')) logClass += ' log-warning';
                    else if (log.content.includes('[SUCCESS]')) logClass += ' log-success';
                    
                    html += `<div class="${{logClass}}">${{log.content}}</div>`;
                }});
            }} else {{
                html = '<div class="log-entry">No recent logs available</div>';
            }}
            
            document.getElementById('recent-logs').innerHTML = html;
        }}
        
        function toggleAutoRefresh() {{
            autoRefresh = !autoRefresh;
            document.getElementById('auto-status').textContent = autoRefresh ? 'ON' : 'OFF';
            
            if (autoRefresh) {{
                refreshInterval = setInterval(updateStatus, 5000);
                updateStatus();
            }} else {{
                clearInterval(refreshInterval);
            }}
        }}
        
        // Initial load
        updateStatus();
        
        // Auto-refresh every 10 seconds by default
        setTimeout(() => toggleAutoRefresh(), 1000);
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'404 - Not Found')
    
    def log_message(self, format, *args):
        # Suppress HTTP request logs
        pass

def create_handler(monitor):
    def handler(*args, **kwargs):
        MonitorHandler(monitor, *args, **kwargs)
    return handler

def main():
    port = 8090
    monitor = BuildMonitor()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              SynOS Ultimate Build Monitor                   ║
║                Independent Monitoring System                ║
║                                                              ║
║  Monitor Dashboard: http://localhost:{port}                    ║
║  System API:        http://localhost:{port}/api/system         ║
║  Build API:         http://localhost:{port}/api/build          ║
║                                                              ║
║  This monitor runs independently of terminal issues         ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Start monitoring thread
    monitor.monitoring = True
    monitor_thread = threading.Thread(target=monitor.continuous_monitoring, daemon=True)
    monitor_thread.start()
    
    try:
        with socketserver.TCPServer(("", port), create_handler(monitor)) as httpd:
            print(f"Monitor serving on port {port}")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Monitor stopped")
        monitor.monitoring = False

if __name__ == "__main__":
    main()
