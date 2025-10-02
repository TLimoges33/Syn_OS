# GitHub Repository Curator

A comprehensive Python application for managing your GitHub ecosystem by automatically forking starred repositories and curating all your repositories into an organized developer library.

## Features

- 🌟 **Star-to-Fork Pipeline**: Automatically fork your starred repositories into private repos
- 📚 **Repository Curation**: Organize all your repositories into categorized libraries
- 🏷️ **Smart Tagging**: Automatically tag repositories by language, framework, and purpose
- 📊 **Analytics Dashboard**: View statistics about your repository collection
- 🔄 **Sync Management**: Keep forks updated with upstream repositories
- 🔍 **Search & Discovery**: Advanced search through your curated library
- 📋 **Documentation Generator**: Auto-generate documentation for your library

## Installation

```bash
cd tools/github-curator
pip install -r requirements.txt
```

## Configuration

1. Create a GitHub Personal Access Token with repository permissions
2. Copy `config/config.example.yml` to `config/config.yml`
3. Add your GitHub token and preferences

## Usage

```bash
# Fork all starred repositories
python main.py fork-starred

# Curate all repositories
python main.py curate-repos

# Generate library documentation
python main.py generate-docs

# Start web dashboard
python main.py dashboard
```

## Architecture

- `core/` - Core application logic
- `services/` - GitHub API and data services
- `models/` - Data models and schemas
- `web/` - Web dashboard interface
- `config/` - Configuration files
- `data/` - Local database and cache
