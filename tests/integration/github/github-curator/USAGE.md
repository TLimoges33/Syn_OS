# 🚀 GitHub Repository Curator - Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the curator directory
cd tools/github-curator

# Run the setup script
python setup.py

# Edit your configuration
cp .env.example .env
# Add your GitHub token to .env file
```

### 2. Get GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with these scopes:
   - `repo` (Full control of private repositories)
   - `user` (Access user profile information)
   - `read:org` (Read organization membership)
3. Copy the token and add it to your `.env` file:
   ```
   GITHUB_TOKEN=your_token_here
   ```

### 3. Basic Commands

```bash
# Show help
python main.py --help

# View your library statistics
python main.py stats

# Preview what would be forked (dry run)
python main.py fork-starred --dry-run

# Fork your starred repositories
python main.py fork-starred --limit 10

# Curate your repository library
python main.py curate-repos

# Search your repositories
python main.py search "machine learning"

# Generate documentation
python main.py generate-docs --format markdown

# Start web dashboard
python main.py dashboard --port 8080
```

## Detailed Usage

### Fork Management

#### Fork All Starred Repositories
```bash
# Preview what will be forked
python main.py fork-starred --dry-run --limit 20

# Fork first 50 starred repos
python main.py fork-starred --limit 50

# Fork all starred repos (be careful with rate limits!)
python main.py fork-starred
```

#### Sync Your Forks
```bash
# Sync all forks with upstream
python main.py sync-forks
```

### Repository Curation

#### Automatic Curation
```bash
# Curate all repositories
python main.py curate-repos

# Update existing repository metadata
python main.py curate-repos --update-existing

# Curate only specific categories
python main.py curate-repos --categories "Web Development" "Data Science & AI"
```

### Search and Discovery

#### Search Your Library
```bash
# Basic search
python main.py search "docker"

# Search with filters
python main.py search "api" --language Python --limit 10

# Search by category
python main.py search "framework" --category "Web Development"
```

### Documentation Generation

#### Generate Different Formats
```bash
# Generate Markdown documentation
python main.py generate-docs --format markdown --output-dir ./docs

# Generate HTML documentation with interactive features
python main.py generate-docs --format html --output-dir ./web-docs

# Generate JSON for API consumption
python main.py generate-docs --format json --output-dir ./api-data
```

### Web Dashboard

#### Start the Dashboard
```bash
# Default settings (localhost:8080)
python main.py dashboard

# Custom host and port
python main.py dashboard --host 0.0.0.0 --port 3000

# Debug mode
python main.py dashboard --debug
```

#### Dashboard Features
- **Repository Overview**: Visual cards for all repositories
- **Category Management**: Browse repositories by category
- **Search & Filter**: Real-time search and filtering
- **Analytics**: Statistics and insights about your library
- **Bulk Operations**: Fork, curate, and sync operations
- **Documentation Export**: Generate docs directly from the web interface

## Configuration

### Environment Variables (.env)

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_username  # Optional, auto-detected

# Fork Settings
FORK_AS_PRIVATE=true
FORK_PREFIX=""
FORK_SUFFIX=""
MAX_CONCURRENT_FORKS=5

# Curation Settings
AUTO_CATEGORIZE=true
UPDATE_DESCRIPTIONS=true
CREATE_TOPICS=true

# Quality Thresholds
MIN_STARS_THRESHOLD=10

# Rate Limiting
GITHUB_RATE_LIMIT_BUFFER=100
REQUESTS_PER_HOUR=4000
```

### Advanced Configuration

#### Custom Categories
Edit `config/settings.py` to customize categories:

```python
default_categories = [
    "Web Development",
    "Mobile Development", 
    "DevOps & Infrastructure",
    "Data Science & AI",
    "Security & Privacy",
    "Game Development",
    "CLI Tools",
    # Add your custom categories
]
```

#### Language Mappings
Customize how languages map to categories:

```python
language_category_mapping = {
    "JavaScript": "Web Development",
    "Python": "Data Science & AI",
    "Go": "DevOps & Infrastructure",
    # Add your mappings
}
```

#### Exclusion Rules
Configure what to exclude from curation:

```python
exclude_repos = [
    "fork",
    "archive", 
    "deprecated",
    "legacy",
    # Add patterns to exclude
]

exclude_languages = [
    "TeX",
    "Jupyter Notebook",
    # Add languages to exclude
]
```

## Advanced Features

### Batch Operations

#### Process Multiple Operations
```bash
# Fork starred repos and then curate them
python main.py fork-starred --limit 20 && python main.py curate-repos

# Complete workflow: fork, curate, generate docs
python main.py fork-starred && \
python main.py curate-repos && \
python main.py generate-docs --format markdown && \
python main.py generate-docs --format html
```

### Quality Analysis

#### Repository Quality Metrics
The curator analyzes repositories based on:
- **Description Quality**: Length and informativeness
- **Documentation**: README, license, contributing guidelines
- **Activity**: Recent commits and updates
- **Community**: Stars, forks, and watchers
- **Maintenance**: Issues, archived status

#### Quality Scores
- **High (0.8-1.0)**: Well-maintained, documented, active
- **Medium (0.6-0.8)**: Good quality with minor issues
- **Low (0.0-0.6)**: Needs improvement or unmaintained

### Analytics and Insights

#### View Statistics
```bash
# Overall library statistics
python main.py stats

# Category distribution
python main.py search "" | jq '.[] | .curation.category' | sort | uniq -c

# Language analysis
python main.py search "" | jq '.[] | .language' | sort | uniq -c
```

## Troubleshooting

### Common Issues

#### Rate Limiting
```bash
# Error: GitHub API rate limit exceeded
# Solution: Wait for rate limit reset or increase buffer

# Check current rate limit
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

#### Permission Errors
```bash
# Error: Cannot fork repository
# Solution: Check token permissions (needs 'repo' scope)

# Error: Cannot update repository metadata
# Solution: Ensure you own the repository or have write access
```

#### Memory Issues
```bash
# Error: Out of memory during processing
# Solution: Process repositories in smaller batches

python main.py fork-starred --limit 50
python main.py curate-repos --categories "Web Development"
```

### Debug Mode

#### Enable Detailed Logging
```bash
# Set log level in environment
export LOG_LEVEL=DEBUG

# Or modify logging_config.py
# logging.basicConfig(level=logging.DEBUG)
```

#### Check Log Files
```bash
# View recent logs
tail -f logs/curator.log

# Search for errors
grep ERROR logs/curator.log
```

## Best Practices

### Repository Management
1. **Start Small**: Begin with `--limit` to test functionality
2. **Regular Sync**: Run `sync-forks` weekly to stay current
3. **Quality Focus**: Prioritize high-quality repositories
4. **Organization**: Use consistent categorization

### Performance
1. **Batch Processing**: Process repositories in manageable chunks
2. **Rate Limiting**: Respect GitHub API limits
3. **Caching**: Let the curator cache results for efficiency
4. **Selective Curation**: Use category filters for targeted updates

### Security
1. **Token Security**: Keep your GitHub token secure and rotate regularly
2. **Private Repos**: Consider privacy implications when forking
3. **Permissions**: Use minimal required token permissions
4. **Environment**: Don't commit `.env` files to version control

## Integration Examples

### CI/CD Integration
```yaml
# .github/workflows/curator.yml
name: Repository Curation
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM

jobs:
  curate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Curate repositories
        env:
          GITHUB_TOKEN: ${{ secrets.CURATOR_TOKEN }}
        run: |
          python main.py curate-repos
          python main.py generate-docs --format markdown
```

### Automation Scripts
```bash
#!/bin/bash
# daily-curator.sh
# Daily automation script

echo "Starting daily curation..."

# Sync forks
python main.py sync-forks

# Update curation
python main.py curate-repos --update-existing

# Generate fresh documentation
python main.py generate-docs --format html --output-dir ./public

echo "Daily curation completed!"
```

This comprehensive usage guide covers all aspects of the GitHub Repository Curator. The tool is designed to be both powerful for advanced users and accessible for beginners.
