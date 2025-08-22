#!/bin/bash
# Syn_OS Educational Container Entrypoint
# Initializes consciousness-aware educational sandbox environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Educational environment variables
STUDENT_HOME="/home/student"
CONSCIOUSNESS_LOG_DIR="$STUDENT_HOME/consciousness-data"
LEARNING_PROGRESS_DIR="$STUDENT_HOME/learning-progress"
CHALLENGE_DIR="$STUDENT_HOME/challenges"
SANDBOX_DIR="$STUDENT_HOME/sandbox"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🎓 $1${NC}"
}

# Initialize educational environment
initialize_educational_environment() {
    print_header "Initializing Syn_OS Educational Environment"
    echo "==========================================="
    
    # Ensure all directories exist with proper permissions
    mkdir -p "$CONSCIOUSNESS_LOG_DIR" "$LEARNING_PROGRESS_DIR" "$CHALLENGE_DIR" "$SANDBOX_DIR"
    mkdir -p "$SANDBOX_DIR/exploits" "$SANDBOX_DIR/forensics" "$SANDBOX_DIR/network"
    mkdir -p "$LEARNING_PROGRESS_DIR/sessions" "$LEARNING_PROGRESS_DIR/analytics"
    
    # Set proper permissions for educational safety
    chmod 755 "$CHALLENGE_DIR" "$SANDBOX_DIR" "$LEARNING_PROGRESS_DIR"
    chmod 700 "$CONSCIOUSNESS_LOG_DIR"
    
    print_status "Educational directories initialized"
}

# Setup consciousness tracking
setup_consciousness_tracking() {
    print_info "Setting up consciousness tracking system..."
    
    # Create consciousness tracking configuration
    cat > "$CONSCIOUSNESS_LOG_DIR/config.json" << EOF
{
    "student_id": "${STUDENT_ID:-default}",
    "session_start": "$(date -Iseconds)",
    "consciousness_tracking": "${CONSCIOUSNESS_TRACKING:-enabled}",
    "educational_level": "${EDUCATIONAL_LEVEL:-adaptive}",
    "safe_mode": "${SAFE_MODE:-true}",
    "logging_enabled": true,
    "analytics_enabled": true
}
EOF
    
    # Initialize learning session
    SESSION_ID="session_$(date +%s)"
    cat > "$LEARNING_PROGRESS_DIR/sessions/${SESSION_ID}.json" << EOF
{
    "session_id": "$SESSION_ID",
    "student_id": "${STUDENT_ID:-default}",
    "start_time": "$(date -Iseconds)",
    "consciousness_baseline": 0.5,
    "challenges_attempted": [],
    "learning_objectives": [],
    "progress_markers": []
}
EOF
    
    export CURRENT_SESSION_ID="$SESSION_ID"
    print_status "Consciousness tracking configured (Session: $SESSION_ID)"
}

# Start educational services
start_educational_services() {
    print_info "Starting educational services..."
    
    # Start consciousness monitoring service
    if [ -f "/opt/consciousness-service.py" ]; then
        python3 /opt/consciousness-service.py &
        CONSCIOUSNESS_PID=$!
        echo $CONSCIOUSNESS_PID > /tmp/consciousness-service.pid
        print_status "Consciousness monitoring service started (PID: $CONSCIOUSNESS_PID)"
    fi
    
    # Start educational dashboard
    if [ -f "$SANDBOX_DIR/educational_dashboard.py" ]; then
        cd "$SANDBOX_DIR"
        python3 educational_dashboard.py &
        DASHBOARD_PID=$!
        echo $DASHBOARD_PID > /tmp/educational-dashboard.pid
        print_status "Educational dashboard started on port 8000 (PID: $DASHBOARD_PID)"
    fi
    
    # Start learning analytics service
    python3 -c "
import http.server
import socketserver
import json
from datetime import datetime

class LearningAnalyticsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/analytics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            analytics = {
                'session_id': '$SESSION_ID',
                'student_id': '${STUDENT_ID:-default}',
                'consciousness_level': 0.75,
                'learning_velocity': 0.8,
                'challenges_completed': 0,
                'time_in_session': 0,
                'breakthrough_detected': False,
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(analytics).encode())
        else:
            super().do_GET()

PORT = 8001
with socketserver.TCPServer(('', PORT), LearningAnalyticsHandler) as httpd:
    print(f'Learning analytics API started on port {PORT}')
    httpd.serve_forever()
" &
    ANALYTICS_PID=$!
    echo $ANALYTICS_PID > /tmp/learning-analytics.pid
    print_status "Learning analytics API started on port 8001 (PID: $ANALYTICS_PID)"
}

# Create educational challenges
create_educational_content() {
    print_info "Setting up educational challenges..."
    
    # Create cybersecurity fundamentals challenge
    cat > "$CHALLENGE_DIR/cybersecurity_basics.py" << 'EOF'
#!/usr/bin/env python3
"""
Cybersecurity Basics Challenge
Introduction to consciousness-aware security learning
"""

import json
import time
import os

class CybersecurityBasics:
    def __init__(self):
        self.student_id = os.environ.get('STUDENT_ID', 'default')
        self.session_id = os.environ.get('CURRENT_SESSION_ID', 'session_default')
        self.consciousness_log = "/home/student/consciousness-data"
    
    def welcome_student(self):
        """Welcome message and consciousness baseline"""
        print("🛡️  Welcome to Syn_OS Cybersecurity Education!")
        print("=" * 50)
        print("🧠 This platform adapts to your consciousness level")
        print("📚 Learn cybersecurity through hands-on challenges")
        print("🔒 All exercises are conducted in a safe environment")
        print()
        
        # Establish consciousness baseline
        print("🧠 Establishing consciousness baseline...")
        self.record_consciousness_event("session_start", {"type": "baseline_establishment"})
        
        print("✅ Ready to begin learning!")
    
    def basic_security_concepts(self):
        """Teach basic security concepts"""
        concepts = [
            {
                "name": "Confidentiality",
                "description": "Ensuring information is accessible only to authorized users",
                "example": "Encrypting sensitive data"
            },
            {
                "name": "Integrity", 
                "description": "Ensuring information is accurate and unmodified",
                "example": "Using digital signatures"
            },
            {
                "name": "Availability",
                "description": "Ensuring information is accessible when needed",
                "example": "Implementing redundancy"
            }
        ]
        
        print("🎓 Learning: CIA Triad - Core Security Principles")
        print("-" * 45)
        
        for i, concept in enumerate(concepts, 1):
            print(f"{i}. {concept['name']}")
            print(f"   📝 {concept['description']}")
            print(f"   💡 Example: {concept['example']}")
            print()
            
            # Track learning progress
            self.record_consciousness_event("concept_learned", {
                "concept": concept['name'],
                "understanding_level": "basic"
            })
            
            time.sleep(2)  # Allow time for processing
    
    def interactive_quiz(self):
        """Interactive quiz with consciousness tracking"""
        questions = [
            {
                "question": "Which principle ensures data is not modified by unauthorized users?",
                "options": ["A) Confidentiality", "B) Integrity", "C) Availability"],
                "correct": "B",
                "explanation": "Integrity ensures data accuracy and prevents unauthorized modifications."
            },
            {
                "question": "What is the primary goal of encryption?",
                "options": ["A) Availability", "B) Performance", "C) Confidentiality"],
                "correct": "C", 
                "explanation": "Encryption protects confidentiality by making data unreadable to unauthorized users."
            }
        ]
        
        print("🧠 Interactive Consciousness-Aware Quiz")
        print("=" * 40)
        
        score = 0
        for i, q in enumerate(questions, 1):
            print(f"Question {i}: {q['question']}")
            for option in q['options']:
                print(f"  {option}")
            
            # Record question presentation
            self.record_consciousness_event("quiz_question_presented", {
                "question_id": i,
                "question": q['question']
            })
            
            answer = input("Your answer: ").strip().upper()
            
            if answer == q['correct']:
                print("✅ Correct! " + q['explanation'])
                score += 1
                self.record_consciousness_event("correct_answer", {
                    "question_id": i,
                    "response_time": 1.5  # Simulated
                })
            else:
                print("❌ Incorrect. " + q['explanation'])
                self.record_consciousness_event("incorrect_answer", {
                    "question_id": i,
                    "given_answer": answer,
                    "correct_answer": q['correct']
                })
            
            print()
        
        print(f"🎯 Quiz Complete! Score: {score}/{len(questions)}")
        
        # Analyze performance for consciousness insights
        if score == len(questions):
            print("🧠 Excellent! Your consciousness level appears optimal for learning.")
            self.record_consciousness_event("quiz_mastery", {"score": score})
        elif score >= len(questions) * 0.7:
            print("🧠 Good performance! Consider reviewing missed concepts.")
            self.record_consciousness_event("quiz_proficient", {"score": score})
        else:
            print("🧠 Consider reviewing the material. The system will adapt to help you learn.")
            self.record_consciousness_event("quiz_needs_review", {"score": score})
    
    def record_consciousness_event(self, event_type, data):
        """Record consciousness and learning events"""
        event = {
            "timestamp": time.time(),
            "student_id": self.student_id,
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data,
            "consciousness_context": "cybersecurity_basics"
        }
        
        try:
            log_file = os.path.join(self.consciousness_log, "learning_events.jsonl")
            with open(log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"📝 Note: Consciousness logging unavailable ({e})")

def main():
    challenge = CybersecurityBasics()
    
    challenge.welcome_student()
    challenge.basic_security_concepts()
    challenge.interactive_quiz()
    
    print("🎓 Cybersecurity Basics Challenge Complete!")
    print("🧠 Your learning progress has been recorded for consciousness analysis.")

if __name__ == "__main__":
    main()
EOF

    # Create hands-on security challenge
    cat > "$CHALLENGE_DIR/hands_on_security.py" << 'EOF'
#!/usr/bin/env python3
"""
Hands-On Security Challenge
Practical cybersecurity exercises with consciousness tracking
"""

import json
import time
import hashlib
import base64
import os

class HandsOnSecurity:
    def __init__(self):
        self.student_id = os.environ.get('STUDENT_ID', 'default')
        self.session_id = os.environ.get('CURRENT_SESSION_ID', 'session_default')
        self.consciousness_log = "/home/student/consciousness-data"
    
    def password_security_challenge(self):
        """Interactive password security challenge"""
        print("🔐 Password Security Challenge")
        print("=" * 30)
        print("Learn about password security through hands-on practice")
        print()
        
        # Test password strength
        print("🧪 Password Strength Analysis")
        
        passwords_to_test = [
            "123456",
            "password",
            "MyP@ssw0rd!",
            "Tr0ub4dor&3",
            "correct horse battery staple"
        ]
        
        for password in passwords_to_test:
            strength = self.analyze_password_strength(password)
            print(f"Password: '{password}' - Strength: {strength}")
            
            # Record learning interaction
            self.record_consciousness_event("password_analysis", {
                "password_length": len(password),
                "strength_score": strength,
                "learning_focus": "password_security"
            })
            
            time.sleep(1)
        
        print()
        print("💡 Key Learnings:")
        print("- Length matters more than complexity")
        print("- Passphrases can be stronger and easier to remember")
        print("- Avoid common passwords and personal information")
    
    def analyze_password_strength(self, password):
        """Analyze password strength with educational feedback"""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 3
            feedback.append("Good length")
        elif len(password) >= 8:
            score += 2
            feedback.append("Adequate length")
        else:
            score += 1
            feedback.append("Too short")
        
        # Character variety
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        variety_score = sum([has_lower, has_upper, has_digit, has_special])
        score += variety_score
        
        # Common password check
        common_passwords = ["123456", "password", "admin", "qwerty"]
        if password.lower() in common_passwords:
            score = max(1, score - 3)
            feedback.append("Common password - avoid!")
        
        # Convert to descriptive strength
        if score >= 7:
            return "Very Strong"
        elif score >= 5:
            return "Strong"
        elif score >= 3:
            return "Moderate"
        else:
            return "Weak"
    
    def encryption_demonstration(self):
        """Demonstrate basic encryption concepts"""
        print("🔒 Encryption Demonstration")
        print("=" * 25)
        print("Learn how encryption protects data")
        print()
        
        # Simple Caesar cipher for demonstration
        message = "Hello, Cybersecurity Student!"
        shift = 3
        
        print(f"Original message: {message}")
        
        # Encrypt
        encrypted = self.caesar_cipher(message, shift)
        print(f"Encrypted message: {encrypted}")
        
        # Decrypt
        decrypted = self.caesar_cipher(encrypted, -shift)
        print(f"Decrypted message: {decrypted}")
        
        print()
        print("💡 This is a simple demonstration. Real encryption uses complex algorithms!")
        
        # Record encryption learning
        self.record_consciousness_event("encryption_demo", {
            "cipher_type": "caesar",
            "understanding_level": "basic",
            "message_length": len(message)
        })
    
    def caesar_cipher(self, text, shift):
        """Simple Caesar cipher for educational purposes"""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                shifted = (ord(char) - ascii_offset + shift) % 26
                result += chr(shifted + ascii_offset)
            else:
                result += char
        return result
    
    def hash_function_demo(self):
        """Demonstrate hash functions and their properties"""
        print("🔍 Hash Function Demonstration")
        print("=" * 30)
        print("Explore cryptographic hash functions")
        print()
        
        test_data = [
            "Hello World",
            "Hello World!",  # Small change
            "Cybersecurity is important",
            ""  # Empty string
        ]
        
        for data in test_data:
            # Calculate MD5 and SHA256 hashes
            md5_hash = hashlib.md5(data.encode()).hexdigest()
            sha256_hash = hashlib.sha256(data.encode()).hexdigest()
            
            print(f"Input: '{data}'")
            print(f"MD5:    {md5_hash}")
            print(f"SHA256: {sha256_hash}")
            print()
            
            # Record hash learning
            self.record_consciousness_event("hash_demo", {
                "input_length": len(data),
                "hash_algorithms": ["MD5", "SHA256"],
                "learning_concept": "hash_functions"
            })
        
        print("💡 Key Properties of Hash Functions:")
        print("- Deterministic: Same input = Same output")
        print("- Fixed size output regardless of input size")
        print("- Small input changes = Completely different output")
        print("- One-way function: Cannot reverse to get original input")
    
    def record_consciousness_event(self, event_type, data):
        """Record consciousness and learning events"""
        event = {
            "timestamp": time.time(),
            "student_id": self.student_id,
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data,
            "consciousness_context": "hands_on_security"
        }
        
        try:
            log_file = os.path.join(self.consciousness_log, "learning_events.jsonl")
            with open(log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"📝 Note: Consciousness logging unavailable ({e})")

def main():
    challenge = HandsOnSecurity()
    
    print("🎯 Hands-On Security Challenge")
    print("=" * 35)
    print("🧠 Consciousness-aware practical security learning")
    print()
    
    challenge.password_security_challenge()
    print()
    challenge.encryption_demonstration()
    print()
    challenge.hash_function_demo()
    
    print("🎓 Hands-On Security Challenge Complete!")
    print("🧠 Continue practicing to strengthen your cybersecurity skills!")

if __name__ == "__main__":
    main()
EOF

    chmod +x "$CHALLENGE_DIR"/*.py
    print_status "Educational challenges created and configured"
}

# Display environment information
display_educational_info() {
    echo ""
    print_header "Syn_OS Educational Environment Ready"
    echo "====================================="
    echo ""
    echo -e "${GREEN}🎓 Student Environment:${NC}"
    echo "  • Student ID: ${STUDENT_ID:-default}"
    echo "  • Session ID: ${CURRENT_SESSION_ID:-session_default}"
    echo "  • Consciousness Tracking: ${CONSCIOUSNESS_TRACKING:-enabled}"
    echo "  • Educational Level: ${EDUCATIONAL_LEVEL:-adaptive}"
    echo "  • Safe Mode: ${SAFE_MODE:-true}"
    echo ""
    echo -e "${BLUE}📂 Directory Structure:${NC}"
    echo "  • Home: $STUDENT_HOME"
    echo "  • Challenges: $CHALLENGE_DIR"
    echo "  • Sandbox: $SANDBOX_DIR"
    echo "  • Progress Tracking: $LEARNING_PROGRESS_DIR"
    echo "  • Consciousness Data: $CONSCIOUSNESS_LOG_DIR"
    echo ""
    echo -e "${YELLOW}🌐 Available Services:${NC}"
    echo "  • Educational Dashboard: http://localhost:8000"
    echo "  • Learning Analytics API: http://localhost:8001"
    echo "  • Consciousness Monitoring API: http://localhost:8002"
    echo ""
    echo -e "${PURPLE}🚀 Quick Start Commands:${NC}"
    echo "  • python3 ~/challenges/cybersecurity_basics.py     # Start with basics"
    echo "  • python3 ~/challenges/hands_on_security.py       # Hands-on practice"
    echo "  • python3 ~/challenges/buffer_overflow_intro.py   # Advanced challenges"
    echo "  • python3 ~/challenges/network_analysis.py        # Network security"
    echo "  • python3 ~/challenges/digital_forensics.py       # Digital forensics"
    echo ""
    echo -e "${GREEN}🧠 Consciousness Features:${NC}"
    echo "  • Adaptive difficulty adjustment"
    echo "  • Real-time learning analytics" 
    echo "  • Breakthrough detection"
    echo "  • Personalized learning paths"
    echo ""
}

# Cleanup function
cleanup() {
    print_info "Shutting down educational services..."
    
    # Kill background services
    for pid_file in /tmp/consciousness-service.pid /tmp/educational-dashboard.pid /tmp/learning-analytics.pid; do
        if [ -f "$pid_file" ]; then
            kill $(cat "$pid_file") 2>/dev/null || true
            rm -f "$pid_file"
        fi
    done
    
    # Record session end
    if [ -n "$CURRENT_SESSION_ID" ] && [ -f "$LEARNING_PROGRESS_DIR/sessions/${CURRENT_SESSION_ID}.json" ]; then
        # Update session with end time
        python3 -c "
import json
session_file = '$LEARNING_PROGRESS_DIR/sessions/${CURRENT_SESSION_ID}.json'
try:
    with open(session_file, 'r') as f:
        session = json.load(f)
    session['end_time'] = '$(date -Iseconds)'
    with open(session_file, 'w') as f:
        json.dump(session, f, indent=2)
except:
    pass
"
    fi
    
    print_status "Educational environment shutdown complete"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main function
main() {
    # Handle different entrypoint modes
    case "${1:-educational-shell}" in
        "educational-shell")
            initialize_educational_environment
            setup_consciousness_tracking
            create_educational_content
            start_educational_services
            display_educational_info
            
            print_info "Starting interactive educational shell..."
            exec /bin/bash
            ;;
        "challenge")
            initialize_educational_environment
            setup_consciousness_tracking
            create_educational_content
            
            if [ -n "$2" ]; then
                challenge_file="$CHALLENGE_DIR/$2.py"
                if [ -f "$challenge_file" ]; then
                    print_info "Starting challenge: $2"
                    python3 "$challenge_file"
                else
                    print_error "Challenge not found: $2"
                    exit 1
                fi
            else
                print_error "No challenge specified"
                exit 1
            fi
            ;;
        "dashboard-only")
            initialize_educational_environment
            start_educational_services
            print_info "Dashboard-only mode - services started"
            sleep infinity
            ;;
        *)
            # Execute custom command
            initialize_educational_environment
            setup_consciousness_tracking
            print_info "Executing custom command: $*"
            exec "$@"
            ;;
    esac
}

# Run main function with all arguments
main "$@"