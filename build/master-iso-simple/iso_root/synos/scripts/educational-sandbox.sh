#!/bin/bash
# Syn_OS Educational Sandbox Service
# Manages isolated educational environments with consciousness tracking

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SANDBOX_DIR="/home/student/sandbox"
CHALLENGES_DIR="/home/student/challenges"
CONSCIOUSNESS_LOG_DIR="/home/student/consciousness-data"
PROGRESS_DIR="/home/student/learning-progress"

# Service status
SERVICE_PID_FILE="/tmp/educational-sandbox.pid"
RUNNING=true

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  [$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${CONSCIOUSNESS_LOG_DIR}/sandbox.log"
}

log_success() {
    echo -e "${GREEN}✅ [$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${CONSCIOUSNESS_LOG_DIR}/sandbox.log"
}

log_warning() {
    echo -e "${YELLOW}⚠️  [$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${CONSCIOUSNESS_LOG_DIR}/sandbox.log"
}

log_error() {
    echo -e "${RED}❌ [$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${CONSCIOUSNESS_LOG_DIR}/sandbox.log"
}

# Initialize sandbox environment
initialize_sandbox() {
    log_info "Initializing educational sandbox environment..."
    
    # Create required directories
    mkdir -p "$SANDBOX_DIR" "$CHALLENGES_DIR" "$CONSCIOUSNESS_LOG_DIR" "$PROGRESS_DIR"
    mkdir -p "$SANDBOX_DIR/exploits" "$SANDBOX_DIR/forensics" "$SANDBOX_DIR/network"
    mkdir -p "$PROGRESS_DIR/sessions" "$PROGRESS_DIR/analytics"
    
    # Set proper permissions
    chmod 755 "$SANDBOX_DIR" "$CHALLENGES_DIR" "$PROGRESS_DIR"
    chmod 700 "$CONSCIOUSNESS_LOG_DIR"
    
    # Create sandbox isolation namespace
    if command -v unshare &> /dev/null; then
        log_info "Setting up network namespace for sandbox isolation..."
        unshare -n /bin/bash -c "
            ip link set lo up
            echo 'Sandbox network namespace initialized'
        " 2>/dev/null || log_warning "Could not create network namespace (permissions may be insufficient)"
    fi
    
    log_success "Sandbox environment initialized"
}

# Create educational challenges
create_educational_challenges() {
    log_info "Setting up educational challenges..."
    
    # Basic cybersecurity challenge
    cat > "$CHALLENGES_DIR/buffer_overflow_intro.py" << 'EOF'
#!/usr/bin/env python3
"""
Educational Buffer Overflow Challenge
Safe learning environment for understanding memory vulnerabilities
"""

import sys
import ctypes

class BufferOverflowDemo:
    def __init__(self):
        self.secret_value = 0xDEADBEEF
        self.user_input = ""
    
    def vulnerable_function(self, user_data):
        """
        Intentionally vulnerable function for educational purposes
        Students should identify the buffer overflow condition
        """
        buffer = ctypes.create_string_buffer(64)
        
        # Consciousness tracking point
        print(f"🧠 Consciousness Check: Buffer size = {len(buffer)}")
        print(f"🧠 Input size = {len(user_data)}")
        
        if len(user_data) > len(buffer):
            print("⚠️  Potential buffer overflow detected!")
            print("🎓 Learning Opportunity: What happens when input exceeds buffer size?")
            return False
        
        # Safe copy for educational demonstration
        buffer.value = user_data.encode()[:len(buffer)-1]
        print(f"✅ Safe buffer operation completed")
        return True
    
    def demonstrate_exploit(self):
        """Educational demonstration of exploitation concepts"""
        print("🎓 Educational Exploit Demonstration")
        print("=" * 50)
        print("This is a SAFE simulation for learning purposes")
        print("Real exploits are used only for defensive education")
        
        # Simulate various attack vectors for educational analysis
        attack_vectors = [
            "Stack overflow simulation",
            "Return address manipulation demo",
            "Shellcode injection concept",
            "NOP sled explanation"
        ]
        
        for i, vector in enumerate(attack_vectors, 1):
            print(f"{i}. {vector}")
            # Consciousness tracking for learning analytics
            self.track_learning_moment(vector)
    
    def track_learning_moment(self, concept):
        """Track learning moments for consciousness analysis"""
        import json
        import time
        
        learning_data = {
            "timestamp": time.time(),
            "concept": concept,
            "type": "educational_demonstration",
            "consciousness_context": "cybersecurity_learning"
        }
        
        try:
            with open("/home/student/consciousness-data/learning_moments.jsonl", "a") as f:
                f.write(json.dumps(learning_data) + "\n")
        except:
            pass  # Fail silently in sandbox

if __name__ == "__main__":
    demo = BufferOverflowDemo()
    
    print("🎓 Syn_OS Cybersecurity Education Challenge")
    print("=" * 45)
    print("🛡️  Safe Buffer Overflow Learning Environment")
    print()
    
    # Interactive educational session
    while True:
        print("Options:")
        print("1. Test buffer input (safe mode)")
        print("2. View exploit demonstration") 
        print("3. Exit")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            user_input = input("Enter test input: ")
            demo.vulnerable_function(user_input)
        elif choice == "2":
            demo.demonstrate_exploit()
        elif choice == "3":
            print("🎓 Educational session complete!")
            break
        else:
            print("❌ Invalid option")
        
        print()
EOF

    # Network security challenge
    cat > "$CHALLENGES_DIR/network_analysis.py" << 'EOF'
#!/usr/bin/env python3
"""
Network Security Analysis Challenge
Educational packet analysis and network forensics
"""

import json
import time
import random

class NetworkAnalysisChallenge:
    def __init__(self):
        self.packets_analyzed = 0
        self.threats_detected = 0
    
    def simulate_packet_capture(self):
        """Simulate network packet capture for analysis"""
        print("🌐 Starting simulated packet capture...")
        print("📊 Analyzing network traffic patterns...")
        
        # Simulate various network scenarios
        scenarios = [
            {"type": "normal_http", "threat_level": 0, "description": "Standard HTTP request"},
            {"type": "suspicious_scan", "threat_level": 3, "description": "Port scanning detected"},
            {"type": "malware_beacon", "threat_level": 5, "description": "Potential C2 communication"},
            {"type": "data_exfiltration", "threat_level": 4, "description": "Large data transfer"},
            {"type": "ddos_attempt", "threat_level": 5, "description": "Distributed denial of service"}
        ]
        
        for _ in range(10):
            scenario = random.choice(scenarios)
            self.packets_analyzed += 1
            
            print(f"📦 Packet #{self.packets_analyzed}: {scenario['description']}")
            
            if scenario['threat_level'] > 2:
                self.threats_detected += 1
                print(f"🚨 THREAT DETECTED - Level {scenario['threat_level']}")
                self.track_security_event(scenario)
            
            time.sleep(0.5)  # Simulate processing time
        
        print(f"✅ Analysis complete: {self.packets_analyzed} packets, {self.threats_detected} threats")
    
    def track_security_event(self, event):
        """Track security events for consciousness analysis"""
        learning_data = {
            "timestamp": time.time(),
            "event_type": event["type"],
            "threat_level": event["threat_level"],
            "description": event["description"],
            "analysis_context": "network_security_learning"
        }
        
        try:
            with open("/home/student/consciousness-data/security_events.jsonl", "a") as f:
                f.write(json.dumps(learning_data) + "\n")
        except:
            pass

if __name__ == "__main__":
    challenge = NetworkAnalysisChallenge()
    
    print("🌐 Network Security Analysis Challenge")
    print("=" * 40)
    print("🔍 Educational Network Forensics Environment")
    print()
    
    challenge.simulate_packet_capture()
EOF

    # Digital forensics challenge
    cat > "$CHALLENGES_DIR/digital_forensics.py" << 'EOF'
#!/usr/bin/env python3
"""
Digital Forensics Challenge
Educational investigation and evidence analysis
"""

import json
import time
import hashlib
import os

class DigitalForensicsChallenge:
    def __init__(self):
        self.evidence_chain = []
        self.investigation_id = f"INV-{int(time.time())}"
    
    def start_investigation(self):
        """Begin digital forensics investigation"""
        print("🔍 Starting Digital Forensics Investigation")
        print(f"📋 Investigation ID: {self.investigation_id}")
        print("=" * 50)
        
        # Create simulated evidence
        self.create_evidence_files()
        
        print("📁 Evidence collected:")
        print("1. Suspicious log file")
        print("2. Memory dump (simulated)")
        print("3. Network capture")
        print("4. System artifacts")
        
        # Interactive analysis
        self.analyze_evidence()
    
    def create_evidence_files(self):
        """Create simulated evidence files for analysis"""
        evidence_dir = os.path.join(self.get_sandbox_dir(), "evidence")
        os.makedirs(evidence_dir, exist_ok=True)
        
        # Simulated log file with suspicious activity
        log_content = """
2024-01-15 14:32:01 - INFO - User login: admin
2024-01-15 14:32:15 - WARNING - Failed login attempt: root
2024-01-15 14:32:16 - WARNING - Failed login attempt: root
2024-01-15 14:32:17 - WARNING - Failed login attempt: root
2024-01-15 14:33:45 - CRITICAL - Privilege escalation detected
2024-01-15 14:34:12 - INFO - File access: /etc/shadow
2024-01-15 14:34:30 - INFO - Network connection: 192.168.1.100:4444
2024-01-15 14:35:00 - WARNING - Unusual data transfer: 50MB outbound
"""
        
        with open(os.path.join(evidence_dir, "system.log"), "w") as f:
            f.write(log_content)
        
        # Simulated memory dump indicators
        memory_indicators = {
            "process_list": ["cmd.exe", "powershell.exe", "suspicious.exe"],
            "network_connections": ["192.168.1.100:4444", "10.0.0.1:443"],
            "loaded_modules": ["kernel32.dll", "ntdll.dll", "malicious.dll"]
        }
        
        with open(os.path.join(evidence_dir, "memory_analysis.json"), "w") as f:
            json.dump(memory_indicators, f, indent=2)
        
        self.track_evidence_collection()
    
    def analyze_evidence(self):
        """Interactive evidence analysis"""
        print("\n🔬 Evidence Analysis Phase")
        
        analysis_steps = [
            "Timeline reconstruction",
            "Hash verification", 
            "Network artifact analysis",
            "Memory forensics",
            "Log correlation"
        ]
        
        for step in analysis_steps:
            print(f"📝 Performing: {step}")
            time.sleep(1)
            
            # Simulate consciousness-tracked learning
            self.track_forensics_learning(step)
        
        print("\n📊 Investigation Summary:")
        print("🔍 Attack vector: Brute force login")
        print("🎯 Privilege escalation: Confirmed")
        print("📡 Data exfiltration: Suspected")
        print("⚖️  Evidence integrity: Verified")
    
    def get_sandbox_dir(self):
        """Get sandbox directory path"""
        return "/home/student/sandbox"
    
    def track_evidence_collection(self):
        """Track evidence collection for consciousness analysis"""
        evidence_data = {
            "timestamp": time.time(),
            "investigation_id": self.investigation_id,
            "phase": "evidence_collection",
            "consciousness_context": "digital_forensics_learning"
        }
        
        try:
            with open("/home/student/consciousness-data/forensics_tracking.jsonl", "a") as f:
                f.write(json.dumps(evidence_data) + "\n")
        except:
            pass
    
    def track_forensics_learning(self, analysis_step):
        """Track forensics learning progress"""
        learning_data = {
            "timestamp": time.time(),
            "investigation_id": self.investigation_id,
            "analysis_step": analysis_step,
            "phase": "evidence_analysis",
            "consciousness_context": "digital_forensics_learning"
        }
        
        try:
            with open("/home/student/consciousness-data/forensics_tracking.jsonl", "a") as f:
                f.write(json.dumps(learning_data) + "\n")
        except:
            pass

if __name__ == "__main__":
    challenge = DigitalForensicsChallenge()
    challenge.start_investigation()
EOF

    chmod +x "$CHALLENGES_DIR"/*.py
    log_success "Educational challenges created"
}

# Monitor consciousness data collection
monitor_consciousness() {
    log_info "Starting consciousness monitoring for educational sandbox..."
    
    while $RUNNING; do
        # Check consciousness data collection
        if [ -d "$CONSCIOUSNESS_LOG_DIR" ]; then
            # Count learning events
            learning_events=$(find "$CONSCIOUSNESS_LOG_DIR" -name "*.jsonl" -exec wc -l {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
            
            if [ "$learning_events" -gt 0 ]; then
                log_info "Consciousness tracking active: $learning_events learning events recorded"
            fi
        fi
        
        # Check active sessions
        if [ -d "$PROGRESS_DIR/sessions" ]; then
            active_sessions=$(ls -1 "$PROGRESS_DIR/sessions" 2>/dev/null | wc -l)
            if [ "$active_sessions" -gt 0 ]; then
                log_info "Active learning sessions: $active_sessions"
            fi
        fi
        
        sleep 60  # Check every minute
    done
}

# Start educational web interface
start_educational_interface() {
    log_info "Starting educational web interface..."
    
    # Create simple educational dashboard
    cat > "$SANDBOX_DIR/educational_dashboard.py" << 'EOF'
#!/usr/bin/env python3
"""
Simple educational dashboard for consciousness-aware learning
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

class EducationalHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for educational interface"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/api/consciousness':
            self.serve_consciousness_data()
        elif parsed_path.path == '/api/progress':
            self.serve_progress_data()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve main educational dashboard"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Syn_OS Educational Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .stat-card { background: #2a2a2a; padding: 20px; border-radius: 8px; border: 1px solid #444; }
        .stat-title { font-size: 18px; margin-bottom: 10px; color: #4CAF50; }
        .stat-value { font-size: 24px; font-weight: bold; }
        .challenges { margin-top: 30px; }
        .challenge-item { background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2196F3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Syn_OS Educational Dashboard</h1>
            <p>Consciousness-Aware Cybersecurity Learning Platform</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-title">🎯 Consciousness Level</div>
                <div class="stat-value" id="consciousness-level">0.75</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">📚 Challenges Completed</div>
                <div class="stat-value" id="challenges-completed">3</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">🚀 Learning Velocity</div>
                <div class="stat-value" id="learning-velocity">0.85</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">🔍 Security Events</div>
                <div class="stat-value" id="security-events">12</div>
            </div>
        </div>
        
        <div class="challenges">
            <h2>🎓 Available Challenges</h2>
            <div class="challenge-item">
                <h3>Buffer Overflow Introduction</h3>
                <p>Learn about memory vulnerabilities in a safe environment</p>
                <button onclick="startChallenge('buffer_overflow')">Start Challenge</button>
            </div>
            <div class="challenge-item">
                <h3>Network Security Analysis</h3>
                <p>Analyze network traffic and detect threats</p>
                <button onclick="startChallenge('network_analysis')">Start Challenge</button>
            </div>
            <div class="challenge-item">
                <h3>Digital Forensics Investigation</h3>
                <p>Conduct digital forensics analysis</p>
                <button onclick="startChallenge('digital_forensics')">Start Challenge</button>
            </div>
        </div>
    </div>
    
    <script>
        function startChallenge(challengeType) {
            alert('Starting ' + challengeType + ' challenge!');
            // In a real implementation, this would launch the challenge
        }
        
        // Update stats periodically
        setInterval(function() {
            // Simulate consciousness level updates
            const level = (0.6 + Math.random() * 0.3).toFixed(2);
            document.getElementById('consciousness-level').textContent = level;
        }, 5000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_consciousness_data(self):
        """Serve consciousness monitoring data"""
        # Simulate consciousness data
        data = {
            "consciousness_level": 0.75,
            "cognitive_load": 0.6,
            "attention_score": 0.8,
            "learning_velocity": 0.85,
            "timestamp": "2024-01-15T14:30:00Z"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_progress_data(self):
        """Serve learning progress data"""
        # Simulate progress data
        data = {
            "challenges_completed": 3,
            "total_challenges": 10,
            "security_events_analyzed": 12,
            "breakthroughs_detected": 2,
            "session_duration_minutes": 45
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), EducationalHandler)
    print("🌐 Educational dashboard started on http://localhost:8000")
    server.serve_forever()
EOF

    # Start the educational interface in background
    cd "$SANDBOX_DIR"
    python3 educational_dashboard.py &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > /tmp/educational-dashboard.pid
    
    log_success "Educational interface started on port 8000"
}

# Cleanup function
cleanup() {
    log_info "Shutting down educational sandbox..."
    RUNNING=false
    
    # Kill dashboard if running
    if [ -f /tmp/educational-dashboard.pid ]; then
        kill $(cat /tmp/educational-dashboard.pid) 2>/dev/null || true
        rm -f /tmp/educational-dashboard.pid
    fi
    
    # Remove PID file
    rm -f "$SERVICE_PID_FILE"
    
    log_success "Educational sandbox shutdown complete"
}

# Signal handlers
trap cleanup EXIT INT TERM

# Main function
main() {
    echo "🎓 Starting Syn_OS Educational Sandbox Service"
    echo "=============================================="
    
    # Store PID
    echo $$ > "$SERVICE_PID_FILE"
    
    # Initialize environment
    initialize_sandbox
    create_educational_challenges
    start_educational_interface
    
    log_success "Educational sandbox service started successfully"
    log_info "Dashboard available at: http://localhost:8000"
    log_info "Challenges directory: $CHALLENGES_DIR"
    log_info "Consciousness tracking: $CONSCIOUSNESS_LOG_DIR"
    
    # Start monitoring
    monitor_consciousness
}

# Run main function
main