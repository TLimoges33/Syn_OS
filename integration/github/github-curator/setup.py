#!/usr/bin/env python3
"""Setup script for GitHub Repository Curator."""

import sys
import subprocess
import shutil
from pathlib import Path
import os


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def check_git():
    """Check if git is installed."""
    if not shutil.which('git'):
        print("❌ Git is not installed or not in PATH")
        sys.exit(1)
    print("✅ Git detected")


def install_requirements():
    """Install Python requirements."""
    print("📦 Installing Python requirements...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)


def setup_directories():
    """Create necessary directories."""
    directories = [
        'data',
        'cache',
        'library_docs',
        'logs',
        'web/static',
        'web/templates',
        'templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")


def setup_environment():
    """Setup environment configuration."""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("📝 Created .env file from .env.example")
        print("⚠️  Please edit .env file and add your GitHub token")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example found, please create .env manually")


def setup_logging():
    """Setup logging configuration."""
    log_config = """
import logging
import sys
from pathlib import Path

# Create logs directory
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/curator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Reduce noise from third-party libraries
logging.getLogger('github').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('aiohttp').setLevel(logging.WARNING)
"""
    
    with open('logging_config.py', 'w') as f:
        f.write(log_config)
    
    print("📋 Created logging configuration")


def create_gitignore():
    """Create .gitignore file."""
    gitignore_content = """
# Environment
.env
.env.local
.env.production

# Cache
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# Data and cache directories
data/
cache/
logs/

# Generated documentation
library_docs/generated_*/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
*.tmp
*.temp
"""
    
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("📝 Created .gitignore file")


def print_next_steps():
    """Print next steps for the user."""
    print("\n🚀 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your GitHub Personal Access Token")
    print("2. Test the installation: python main.py --help")
    print("3. Fork your starred repos: python main.py fork-starred --dry-run")
    print("4. Curate your repositories: python main.py curate-repos")
    print("5. Start the web dashboard: python main.py dashboard")
    print("\n🔗 Useful commands:")
    print("  python main.py stats                    # Show library statistics")
    print("  python main.py search 'keyword'         # Search repositories")
    print("  python main.py generate-docs            # Generate documentation")
    print("  python main.py dashboard --port 8080    # Start web interface")


def main():
    """Main setup function."""
    print("🚀 GitHub Repository Curator - Setup")
    print("=" * 40)
    
    # Check prerequisites
    check_python_version()
    check_git()
    
    # Setup project
    install_requirements()
    setup_directories()
    setup_environment()
    setup_logging()
    create_gitignore()
    
    print_next_steps()


if __name__ == '__main__':
    main()
