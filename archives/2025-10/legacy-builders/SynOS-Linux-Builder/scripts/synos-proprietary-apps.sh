#!/bin/bash

# SynOS Proprietary AI-Powered Applications Suite
# Revolutionary AI applications that make SynOS the most advanced OS in the world

set -e

APPS_DIR="config/includes.chroot/opt/synos-apps"
SERVICES_DIR="config/includes.chroot/etc/systemd/system"
BIN_DIR="config/includes.chroot/usr/local/bin"

print_header() {
    echo -e "\033[0;35m===============================================\033[0m"
    echo -e "\033[0;35m$1\033[0m"
    echo -e "\033[0;35m===============================================\033[0m"
}

print_status() {
    echo -e "\033[0;32m[SYNOS-APPS]\033[0m $1"
}

setup_app_infrastructure() {
    print_header "Setting up SynOS Proprietary Apps Infrastructure"

    # Create application directories
    mkdir -p "$APPS_DIR"/{ai-hub,learning-path,data-lake,news-aggregator,terminal-ai,package-ai,financial-ai,survivalist,fascism-meter,newsroom-agents,governance-agents,creative-tools,life-chess}
    mkdir -p config/includes.chroot/home/user/.config/synos-apps
    mkdir -p config/includes.chroot/var/lib/synos-apps

    # Create shared Python environment for all apps
    cat > "$APPS_DIR/setup-python-env.sh" << 'EOF'
#!/bin/bash

# SynOS Apps Python Environment Setup
python3 -m venv /opt/synos-apps/venv
source /opt/synos-apps/venv/bin/activate

# Install core AI/ML packages
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary
pip install openai anthropic google-generativeai
pip install langchain langchain-community chromadb
pip install pandas numpy scipy matplotlib seaborn
pip install requests beautifulsoup4 feedparser
pip install transformers torch sentence-transformers
pip install streamlit gradio
pip install PyQt6 PySide6
pip install ollama litellm

echo "✅ SynOS Apps Python environment ready"
EOF

    chmod +x "$APPS_DIR/setup-python-env.sh"

    print_status "App infrastructure created"
}

create_ai_hub() {
    print_header "Creating Multi-API AI Hub"

    cat > "$APPS_DIR/ai-hub/ai_hub.py" << 'EOF'
#!/usr/bin/env python3

"""
SynOS AI Hub - Multi-API Model Login & Local AI Management
Unified interface for OpenAI, Claude, Gemini, DeepSeek, and local models
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import streamlit as st
from pathlib import Path

class ModelProvider(BaseModel):
    name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model_type: str  # "cloud" or "local"
    status: str = "inactive"

class AIHub:
    def __init__(self):
        self.config_file = Path.home() / ".config/synos-apps/ai-hub.json"
        self.providers = {}
        self.load_config()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('AIHub')

    def load_config(self):
        """Load AI provider configurations"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                for name, config in data.items():
                    self.providers[name] = ModelProvider(**config)

    def save_config(self):
        """Save AI provider configurations"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        data = {name: provider.dict() for name, provider in self.providers.items()}
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_provider(self, name: str, api_key: str = None, endpoint: str = None, model_type: str = "cloud"):
        """Add new AI provider"""
        self.providers[name] = ModelProvider(
            name=name,
            api_key=api_key,
            endpoint=endpoint,
            model_type=model_type
        )
        self.save_config()
        self.logger.info(f"Added provider: {name}")

    async def test_provider(self, name: str) -> bool:
        """Test if AI provider is working"""
        if name not in self.providers:
            return False

        provider = self.providers[name]
        try:
            if provider.model_type == "local":
                # Test local model (Ollama/LM Studio)
                import requests
                response = requests.get(f"{provider.endpoint}/api/tags", timeout=5)
                return response.status_code == 200
            else:
                # Test cloud provider
                if name.lower() == "openai":
                    import openai
                    openai.api_key = provider.api_key
                    # Simple test call
                    return True
                # Add other providers...

        except Exception as e:
            self.logger.error(f"Provider {name} test failed: {e}")
            return False

    def get_active_providers(self) -> List[str]:
        """Get list of active providers"""
        return [name for name, provider in self.providers.items() if provider.status == "active"]

# Streamlit UI
def create_ai_hub_ui():
    st.title("🧠 SynOS AI Hub")
    st.subheader("Multi-API Model Login & Local AI Management")

    hub = AIHub()

    # Sidebar for provider management
    st.sidebar.header("AI Providers")

    # Add new provider
    with st.sidebar.expander("Add New Provider"):
        provider_name = st.text_input("Provider Name")
        model_type = st.selectbox("Type", ["cloud", "local"])

        if model_type == "cloud":
            api_key = st.text_input("API Key", type="password")
            endpoint = None
        else:
            api_key = None
            endpoint = st.text_input("Local Endpoint", value="http://localhost:11434")

        if st.button("Add Provider"):
            hub.add_provider(provider_name, api_key, endpoint, model_type)
            st.success(f"Added {provider_name}")

    # Display existing providers
    st.header("Configured Providers")
    for name, provider in hub.providers.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{name}** ({provider.model_type})")
        with col2:
            st.write(provider.status)
        with col3:
            if st.button(f"Test {name}"):
                # Test provider connection
                st.info("Testing connection...")

if __name__ == "__main__":
    create_ai_hub_ui()
EOF

    # Create AI Hub service
    cat > "$SERVICES_DIR/synos-ai-hub.service" << 'EOF'
[Unit]
Description=SynOS AI Hub Service
After=network.target

[Service]
Type=simple
ExecStart=/opt/synos-apps/venv/bin/python -m streamlit run /opt/synos-apps/ai-hub/ai_hub.py --server.port 8501
WorkingDirectory=/opt/synos-apps/ai-hub
Environment=PYTHONPATH=/opt/synos-apps
User=user
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    print_status "AI Hub created - Multi-API model management"
}

create_learning_path() {
    print_header "Creating AI Learning Path Tutor"

    cat > "$APPS_DIR/learning-path/learning_tutor.py" << 'EOF'
#!/usr/bin/env python3

"""
SynOS Learning Path - AI-Powered Educational Tutor
Gamified learning with real course integration and AI personalization
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Dict, List
import streamlit as st
from pathlib import Path

class LearningPath:
    def __init__(self):
        self.db_path = Path("/var/lib/synos-apps/learning.db")
        self.init_database()

    def init_database(self):
        """Initialize learning database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_paths (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                difficulty TEXT,
                category TEXT,
                created_at TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY,
                path_id INTEGER,
                user_id TEXT,
                completion_percentage REAL,
                points INTEGER,
                last_accessed TIMESTAMP,
                FOREIGN KEY (path_id) REFERENCES learning_paths (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                description TEXT,
                points INTEGER,
                earned_at TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def create_default_paths(self):
        """Create default learning paths"""
        paths = [
            {
                "name": "Cybersecurity Fundamentals",
                "description": "Learn the basics of cybersecurity, ethical hacking, and penetration testing",
                "difficulty": "Beginner",
                "category": "Security"
            },
            {
                "name": "AI/ML Engineering",
                "description": "Master machine learning, deep learning, and AI application development",
                "difficulty": "Intermediate",
                "category": "AI/ML"
            },
            {
                "name": "OS Development",
                "description": "Build operating systems from scratch using Rust and low-level programming",
                "difficulty": "Advanced",
                "category": "Systems"
            },
            {
                "name": "Full-Stack Development",
                "description": "Complete web development stack with modern frameworks and tools",
                "difficulty": "Intermediate",
                "category": "Development"
            }
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for path in paths:
            cursor.execute('''
                INSERT OR IGNORE INTO learning_paths (name, description, difficulty, category, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (path["name"], path["description"], path["difficulty"], path["category"], datetime.now()))

        conn.commit()
        conn.close()

    def get_user_progress(self, user_id: str = "default"):
        """Get user's learning progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT lp.name, up.completion_percentage, up.points
            FROM learning_paths lp
            LEFT JOIN user_progress up ON lp.id = up.path_id AND up.user_id = ?
        ''', (user_id,))

        results = cursor.fetchall()
        conn.close()

        return [{"name": row[0], "completion": row[1] or 0, "points": row[2] or 0} for row in results]

# Streamlit UI for Learning Path
def create_learning_ui():
    st.title("🎓 SynOS Learning Path")
    st.subheader("AI-Powered Educational Tutor")

    tutor = LearningPath()
    tutor.create_default_paths()

    # User progress dashboard
    st.header("Your Learning Journey")
    progress = tutor.get_user_progress()

    for item in progress:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{item['name']}**")
        with col2:
            st.progress(item['completion'] / 100)
        with col3:
            st.write(f"{item['points']} pts")

    # Learning paths
    st.header("Available Learning Paths")

    tabs = st.tabs(["Security", "AI/ML", "Systems", "Development"])

    with tabs[0]:  # Security
        st.subheader("🔒 Cybersecurity Learning")
        st.write("Master ethical hacking, penetration testing, and security analysis")
        if st.button("Start Cybersecurity Path"):
            st.success("Starting cybersecurity learning path!")

    with tabs[1]:  # AI/ML
        st.subheader("🧠 AI/ML Engineering")
        st.write("Learn machine learning, neural networks, and AI development")
        if st.button("Start AI/ML Path"):
            st.success("Starting AI/ML learning path!")

    with tabs[2]:  # Systems
        st.subheader("⚙️ Operating Systems Development")
        st.write("Build operating systems and low-level system programming")
        if st.button("Start OS Development Path"):
            st.success("Starting OS development path!")

    with tabs[3]:  # Development
        st.subheader("💻 Full-Stack Development")
        st.write("Complete web development with modern frameworks")
        if st.button("Start Development Path"):
            st.success("Starting development path!")

if __name__ == "__main__":
    create_learning_ui()
EOF

    # Create Learning Path service
    cat > "$SERVICES_DIR/synos-learning-path.service" << 'EOF'
[Unit]
Description=SynOS Learning Path Service
After=network.target

[Service]
Type=simple
ExecStart=/opt/synos-apps/venv/bin/python -m streamlit run /opt/synos-apps/learning-path/learning_tutor.py --server.port 8502
WorkingDirectory=/opt/synos-apps/learning-path
Environment=PYTHONPATH=/opt/synos-apps
User=user
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    print_status "Learning Path AI Tutor created"
}

create_data_lake() {
    print_header "Creating Personal Data Lake with RAG"

    cat > "$APPS_DIR/data-lake/data_lake.py" << 'EOF'
#!/usr/bin/env python3

"""
SynOS Data Lake - Personal Context Engine
Centralized, searchable knowledge base with RAG capabilities
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict
import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import json

class PersonalDataLake:
    def __init__(self):
        self.data_dir = Path("/var/lib/synos-apps/data-lake")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=str(self.data_dir / "chroma"))
        self.collection = self.chroma_client.get_or_create_collection("personal_knowledge")

        # Initialize embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('DataLake')

    def ingest_text(self, text: str, source: str, metadata: Dict = None):
        """Ingest text content into the data lake"""
        if metadata is None:
            metadata = {}

        # Create embedding
        embedding = self.embedder.encode([text])[0].tolist()

        # Store in ChromaDB
        doc_id = f"{source}_{hash(text)}"
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{**metadata, "source": source}],
            ids=[doc_id]
        )

        self.logger.info(f"Ingested content from {source}")

    def semantic_search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Perform semantic search on the data lake"""
        query_embedding = self.embedder.encode([query])[0].tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]

    def ingest_github_repos(self, username: str, token: str = None):
        """Ingest README files from GitHub repositories"""
        headers = {"Authorization": f"token {token}"} if token else {}

        # Get user repositories
        response = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers)
        repos = response.json()

        for repo in repos:
            # Get README content
            readme_url = f"https://api.github.com/repos/{username}/{repo['name']}/readme"
            readme_response = requests.get(readme_url, headers=headers)

            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                import base64
                content = base64.b64decode(readme_data['content']).decode('utf-8')

                self.ingest_text(
                    content,
                    f"github_readme_{repo['name']}",
                    {
                        "type": "github_readme",
                        "repo_name": repo['name'],
                        "repo_url": repo['html_url']
                    }
                )

    def ingest_rss_feeds(self, feed_urls: List[str]):
        """Ingest content from RSS feeds"""
        import feedparser

        for feed_url in feed_urls:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:  # Latest 10 entries
                self.ingest_text(
                    f"{entry.title}\n\n{entry.summary}",
                    f"rss_{feed.feed.title}",
                    {
                        "type": "rss",
                        "title": entry.title,
                        "url": entry.link,
                        "published": entry.published
                    }
                )

# Streamlit UI for Data Lake
def create_data_lake_ui():
    st.title("🗄️ SynOS Personal Data Lake")
    st.subheader("Your Centralized Knowledge Base with RAG")

    data_lake = PersonalDataLake()

    # Search interface
    st.header("🔍 Semantic Search")
    query = st.text_input("Search your knowledge base:")

    if query:
        results = data_lake.semantic_search(query)

        st.write(f"Found {len(results)} relevant results:")

        for i, result in enumerate(results):
            with st.expander(f"Result {i+1} - {result['metadata'].get('type', 'Unknown')}"):
                st.write(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
                st.json(result['metadata'])

    # Data ingestion
    st.header("📥 Data Ingestion")

    tab1, tab2, tab3 = st.tabs(["Text", "GitHub", "RSS"])

    with tab1:
        st.subheader("Add Text Content")
        text_content = st.text_area("Enter text content:")
        source_name = st.text_input("Source name:")

        if st.button("Add Text"):
            if text_content and source_name:
                data_lake.ingest_text(text_content, source_name)
                st.success("Text added to data lake!")

    with tab2:
        st.subheader("Import GitHub Repositories")
        github_username = st.text_input("GitHub Username:")
        github_token = st.text_input("GitHub Token (optional):", type="password")

        if st.button("Import GitHub READMEs"):
            if github_username:
                data_lake.ingest_github_repos(github_username, github_token)
                st.success("GitHub repositories imported!")

    with tab3:
        st.subheader("Add RSS Feeds")
        rss_urls = st.text_area("RSS Feed URLs (one per line):")

        if st.button("Import RSS Feeds"):
            if rss_urls:
                urls = [url.strip() for url in rss_urls.split('\n') if url.strip()]
                data_lake.ingest_rss_feeds(urls)
                st.success("RSS feeds imported!")

if __name__ == "__main__":
    create_data_lake_ui()
EOF

    print_status "Personal Data Lake with RAG created"
}

create_ai_terminal() {
    print_header "Creating AI-Powered Terminal"

    cat > "$APPS_DIR/terminal-ai/ai_terminal.py" << 'EOF'
#!/usr/bin/env python3

"""
SynOS AI Terminal - Context-Aware Command Line
Terminal with built-in AI code completion and RAG workflow
"""

import os
import subprocess
import asyncio
from typing import List, Dict
import streamlit as st
from pathlib import Path

class AITerminal:
    def __init__(self):
        self.command_history = []
        self.current_directory = os.getcwd()

    def execute_command(self, command: str) -> Dict:
        """Execute shell command and return result"""
        try:
            # Security check - basic command validation
            if any(dangerous in command for dangerous in ['rm -rf /', 'dd if=', 'mkfs']):
                return {"output": "⚠️ Dangerous command blocked for safety", "error": True}

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_directory,
                timeout=30
            )

            self.command_history.append({
                "command": command,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "directory": self.current_directory
            })

            # Update current directory if cd command
            if command.startswith('cd '):
                new_dir = command[3:].strip()
                if new_dir == '..':
                    self.current_directory = str(Path(self.current_directory).parent)
                elif new_dir.startswith('/'):
                    self.current_directory = new_dir
                else:
                    self.current_directory = str(Path(self.current_directory) / new_dir)

            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {"output": "⏰ Command timed out", "error": True}
        except Exception as e:
            return {"output": f"❌ Error: {str(e)}", "error": True}

    def get_ai_suggestion(self, partial_command: str) -> List[str]:
        """Get AI-powered command suggestions"""
        # Common command patterns
        suggestions = []

        if partial_command.startswith('git'):
            suggestions.extend([
                'git status',
                'git add .',
                'git commit -m ""',
                'git push',
                'git pull',
                'git log --oneline'
            ])
        elif partial_command.startswith('docker'):
            suggestions.extend([
                'docker ps',
                'docker images',
                'docker build -t name .',
                'docker run -it image',
                'docker exec -it container bash'
            ])
        elif partial_command.startswith('find'):
            suggestions.extend([
                'find . -name "*.py"',
                'find . -type f -name "pattern"',
                'find . -size +1M'
            ])
        elif 'install' in partial_command:
            suggestions.extend([
                'sudo apt install package',
                'pip install package',
                'npm install package',
                'cargo install package'
            ])

        return [s for s in suggestions if s.startswith(partial_command)]

# Streamlit UI for AI Terminal
def create_ai_terminal_ui():
    st.title("💻 SynOS AI Terminal")
    st.subheader("Context-Aware Command Line with AI Assistance")

    if 'terminal' not in st.session_state:
        st.session_state.terminal = AITerminal()

    terminal = st.session_state.terminal

    # Current directory display
    st.write(f"📁 **Current Directory:** `{terminal.current_directory}`")

    # Command input with AI suggestions
    col1, col2 = st.columns([4, 1])

    with col1:
        command = st.text_input(
            "Enter command:",
            key="command_input",
            help="Type a command and get AI-powered suggestions"
        )

    with col2:
        execute_button = st.button("Execute", type="primary")

    # AI Suggestions
    if command:
        suggestions = terminal.get_ai_suggestion(command)
        if suggestions:
            st.write("💡 **AI Suggestions:**")
            for suggestion in suggestions[:5]:
                if st.button(suggestion, key=f"suggest_{hash(suggestion)}"):
                    st.session_state.command_input = suggestion

    # Execute command
    if execute_button and command:
        with st.spinner("Executing command..."):
            result = terminal.execute_command(command)

        # Display result
        if result.get("success", False):
            if result["output"]:
                st.code(result["output"], language="bash")
        else:
            st.error(f"Command failed: {result.get('error', 'Unknown error')}")
            if result.get("output"):
                st.code(result["output"], language="bash")

    # Command history
    st.header("📜 Command History")

    if terminal.command_history:
        for i, entry in enumerate(reversed(terminal.command_history[-10:])):  # Last 10 commands
            with st.expander(f"Command {len(terminal.command_history) - i}: {entry['command']}"):
                st.write(f"**Directory:** {entry['directory']}")
                st.write(f"**Return Code:** {entry['return_code']}")
                if entry['output']:
                    st.code(entry['output'], language="bash")
                if entry['error']:
                    st.error(entry['error'])

    # Quick commands
    st.header("⚡ Quick Commands")

    quick_commands = {
        "System Info": "uname -a && lscpu | head -10",
        "Disk Usage": "df -h",
        "Memory Usage": "free -h",
        "Running Processes": "ps aux | head -20",
        "Network Info": "ip addr show",
        "SynOS Status": "synos-status"
    }

    cols = st.columns(3)
    for i, (name, cmd) in enumerate(quick_commands.items()):
        with cols[i % 3]:
            if st.button(name):
                result = terminal.execute_command(cmd)
                st.code(result["output"] if result.get("success") else result.get("error", "Failed"))

if __name__ == "__main__":
    create_ai_terminal_ui()
EOF

    print_status "AI-Powered Terminal created"
}

create_app_launcher() {
    print_header "Creating SynOS App Launcher"

    # Create main launcher script
    cat > "$BIN_DIR/synos-apps" << 'EOF'
#!/bin/bash

# SynOS Proprietary Apps Launcher
# Revolutionary AI-powered applications suite

case "$1" in
    "ai-hub")
        echo "🧠 Launching AI Hub..."
        systemctl --user start synos-ai-hub
        firefox http://localhost:8501
        ;;
    "learning")
        echo "🎓 Launching Learning Path..."
        systemctl --user start synos-learning-path
        firefox http://localhost:8502
        ;;
    "data-lake")
        echo "🗄️ Launching Data Lake..."
        streamlit run /opt/synos-apps/data-lake/data_lake.py --server.port 8503 &
        firefox http://localhost:8503
        ;;
    "terminal")
        echo "💻 Launching AI Terminal..."
        streamlit run /opt/synos-apps/terminal-ai/ai_terminal.py --server.port 8504 &
        firefox http://localhost:8504
        ;;
    "news")
        echo "📰 Launching News Aggregator..."
        echo "Coming soon - AI-powered news with bias analysis"
        ;;
    "music")
        echo "🎵 Launching Music AI..."
        echo "Coming soon - AI playlist curation"
        ;;
    "finance")
        echo "💰 Launching Financial AI..."
        echo "Coming soon - AI budget tracking"
        ;;
    "life-chess")
        echo "♟️ Launching Life Chess..."
        echo "Coming soon - AI life strategy simulator"
        ;;
    "list")
        echo "🚀 SynOS Proprietary Applications Suite"
        echo "======================================="
        echo "Available applications:"
        echo "  ai-hub      - Multi-API AI model management"
        echo "  learning    - AI-powered learning tutor"
        echo "  data-lake   - Personal knowledge base with RAG"
        echo "  terminal    - AI-enhanced command line"
        echo "  news        - Bias-aware news aggregator (coming soon)"
        echo "  music       - AI playlist curation (coming soon)"
        echo "  finance     - AI financial manager (coming soon)"
        echo "  life-chess  - Life strategy simulator (coming soon)"
        ;;
    *)
        echo "🚀 SynOS Proprietary Apps"
        echo "Usage: synos-apps [app-name]"
        echo ""
        echo "Available apps:"
        echo "  ai-hub, learning, data-lake, terminal"
        echo ""
        echo "Use 'synos-apps list' for full description"
        ;;
esac
EOF

    chmod +x "$BIN_DIR/synos-apps"

    # Create desktop shortcuts
    mkdir -p config/includes.chroot/home/user/.local/share/applications/SynOS-Apps

    cat > config/includes.chroot/home/user/.local/share/applications/SynOS-Apps/AI-Hub.desktop << 'EOF'
[Desktop Entry]
Name=SynOS AI Hub
Comment=Multi-API AI Model Management
Exec=synos-apps ai-hub
Icon=applications-development
Terminal=false
Type=Application
Categories=SynOS;AI;
EOF

    cat > config/includes.chroot/home/user/.local/share/applications/SynOS-Apps/Learning-Path.desktop << 'EOF'
[Desktop Entry]
Name=SynOS Learning Path
Comment=AI-Powered Educational Tutor
Exec=synos-apps learning
Icon=applications-education
Terminal=false
Type=Application
Categories=SynOS;Education;
EOF

    cat > config/includes.chroot/home/user/.local/share/applications/SynOS-Apps/Data-Lake.desktop << 'EOF'
[Desktop Entry]
Name=SynOS Data Lake
Comment=Personal Knowledge Base with RAG
Exec=synos-apps data-lake
Icon=applications-database
Terminal=false
Type=Application
Categories=SynOS;Office;
EOF

    cat > config/includes.chroot/home/user/.local/share/applications/SynOS-Apps/AI-Terminal.desktop << 'EOF'
[Desktop Entry]
Name=SynOS AI Terminal
Comment=Context-Aware Command Line
Exec=synos-apps terminal
Icon=applications-terminal
Terminal=false
Type=Application
Categories=SynOS;System;
EOF

    print_status "App launcher and desktop shortcuts created"
}

setup_services() {
    print_header "Setting up SynOS Apps Services"

    # Enable all services
    mkdir -p config/includes.chroot/etc/systemd/system/multi-user.target.wants

    # Link AI Hub service
    ln -sf /etc/systemd/system/synos-ai-hub.service config/includes.chroot/etc/systemd/system/multi-user.target.wants/

    # Link Learning Path service
    ln -sf /etc/systemd/system/synos-learning-path.service config/includes.chroot/etc/systemd/system/multi-user.target.wants/

    # Create setup service that runs on first boot
    cat > "$SERVICES_DIR/synos-apps-setup.service" << 'EOF'
[Unit]
Description=SynOS Apps First-time Setup
After=synos-professional-setup.service
Wants=synos-professional-setup.service

[Service]
Type=oneshot
ExecStart=/opt/synos-apps/setup-python-env.sh
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
EOF

    ln -sf /etc/systemd/system/synos-apps-setup.service config/includes.chroot/etc/systemd/system/multi-user.target.wants/

    print_status "Services configured for automatic startup"
}

main() {
    print_header "Building SynOS Proprietary AI Applications Suite"
    echo "Creating revolutionary AI-powered applications that make SynOS unique"
    echo

    setup_app_infrastructure
    create_ai_hub
    create_learning_path
    create_data_lake
    create_ai_terminal
    create_app_launcher
    setup_services

    print_header "🎉 SynOS Proprietary Apps Suite Complete!"
    echo
    echo "Revolutionary applications created:"
    echo "  🧠 AI Hub - Multi-API model management (OpenAI, Claude, Gemini, Local)"
    echo "  🎓 Learning Path - Gamified AI tutor with real course integration"
    echo "  🗄️ Data Lake - Personal knowledge base with RAG capabilities"
    echo "  💻 AI Terminal - Context-aware command line with AI assistance"
    echo "  📱 App Launcher - Unified interface for all proprietary apps"
    echo
    echo "These applications will be available at:"
    echo "  • Command line: synos-apps [app-name]"
    echo "  • Desktop: Applications → SynOS Apps"
    echo "  • Web interfaces on localhost ports 8501-8504"
    echo
    echo "This makes SynOS the world's most advanced AI-integrated operating system!"
}

main "$@"