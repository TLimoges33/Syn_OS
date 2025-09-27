"""Documentation and library generation for curated repositories."""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict, Counter
import markdown
from jinja2 import Environment, FileSystemLoader, Template

from services.github_service import GitHubService
from config.settings import Settings
from core.curator import RepositoryCurator

logger = logging.getLogger(__name__)


class LibraryGenerator:
    """Generates comprehensive documentation for the curated repository library."""
    
    def __init__(self, github_service: GitHubService, settings: Settings):
        self.github = github_service
        self.settings = settings
        self.curator = RepositoryCurator(github_service, settings)
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / 'templates'
        template_dir.mkdir(exist_ok=True)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        self._create_default_templates()
    
    async def generate_documentation(self, format_type: str, output_dir: Path) -> bool:
        """Generate comprehensive library documentation."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Collect all repository data
            library_data = await self._collect_library_data()
            
            if format_type == 'markdown':
                await self._generate_markdown_docs(library_data, output_dir)
            elif format_type == 'html':
                await self._generate_html_docs(library_data, output_dir)
            elif format_type == 'json':
                await self._generate_json_docs(library_data, output_dir)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            logger.info(f"Generated {format_type} documentation in {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate documentation: {e}")
            return False
    
    async def _collect_library_data(self) -> Dict:
        """Collect comprehensive data about the entire library."""
        library_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'GitHub Repository Curator',
                'user': self.github.get_user_info()
            },
            'statistics': await self.curator.get_library_stats(),
            'categories': defaultdict(list),
            'repositories': [],
            'languages': defaultdict(list),
            'quality_levels': defaultdict(list),
            'recent_activity': []
        }
        
        # Curate all repositories and organize data
        curated_results = await self.curator.curate_all_repositories()
        
        for category, repos in curated_results.items():
            for curation_result in repos:
                repo = curation_result.repo
                repo_data = {
                    'basic_info': repo,
                    'curation': {
                        'category': curation_result.category,
                        'confidence': curation_result.confidence,
                        'tags': curation_result.tags,
                        'quality_score': curation_result.quality_score,
                        'metadata': curation_result.metadata
                    }
                }
                
                # Add to main repository list
                library_data['repositories'].append(repo_data)
                
                # Add to category
                library_data['categories'][category].append(repo_data)
                
                # Add to language groups
                if repo.get('language'):
                    library_data['languages'][repo['language']].append(repo_data)
                
                # Add to quality levels
                quality_level = self._get_quality_level(curation_result.quality_score)
                library_data['quality_levels'][quality_level].append(repo_data)
                
                # Add to recent activity if updated recently
                if self._is_recently_updated(repo):
                    library_data['recent_activity'].append(repo_data)
        
        # Sort recent activity by update date
        library_data['recent_activity'].sort(
            key=lambda x: x['basic_info'].get('updated_at', ''),
            reverse=True
        )
        
        return library_data
    
    async def _generate_markdown_docs(self, library_data: Dict, output_dir: Path):
        """Generate Markdown documentation."""
        # Main README
        await self._generate_main_readme(library_data, output_dir)
        
        # Category pages
        await self._generate_category_pages(library_data, output_dir)
        
        # Language pages
        await self._generate_language_pages(library_data, output_dir)
        
        # Statistics page
        await self._generate_statistics_page(library_data, output_dir)
        
        # Quality report
        await self._generate_quality_report(library_data, output_dir)
    
    async def _generate_html_docs(self, library_data: Dict, output_dir: Path):
        """Generate HTML documentation with interactive features."""
        # Create assets directory
        assets_dir = output_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        
        # Generate CSS and JS
        await self._generate_web_assets(assets_dir)
        
        # Main index page
        template = self.jinja_env.get_template('index.html')
        html_content = template.render(library_data=library_data)
        
        with open(output_dir / 'index.html', 'w') as f:
            f.write(html_content)
        
        # Generate individual pages
        for category, repos in library_data['categories'].items():
            category_template = self.jinja_env.get_template('category.html')
            category_html = category_template.render(
                category=category,
                repositories=repos,
                library_data=library_data
            )
            
            category_file = output_dir / f"{self._slugify(category)}.html"
            with open(category_file, 'w') as f:
                f.write(category_html)
    
    async def _generate_json_docs(self, library_data: Dict, output_dir: Path):
        """Generate JSON documentation for API consumption."""
        # Main library data
        with open(output_dir / 'library.json', 'w') as f:
            json.dump(library_data, f, indent=2, default=str)
        
        # Separate files for different views
        with open(output_dir / 'categories.json', 'w') as f:
            json.dump(dict(library_data['categories']), f, indent=2, default=str)
        
        with open(output_dir / 'statistics.json', 'w') as f:
            json.dump(library_data['statistics'], f, indent=2, default=str)
        
        # Repository index for search
        repo_index = []
        for repo_data in library_data['repositories']:
            repo = repo_data['basic_info']
            index_entry = {
                'id': repo['id'],
                'full_name': repo['full_name'],
                'name': repo['name'],
                'description': repo.get('description', ''),
                'language': repo.get('language'),
                'category': repo_data['curation']['category'],
                'tags': repo_data['curation']['tags'],
                'quality_score': repo_data['curation']['quality_score'],
                'stars': repo.get('stargazers_count', 0),
                'updated_at': repo.get('updated_at')
            }
            repo_index.append(index_entry)
        
        with open(output_dir / 'repository_index.json', 'w') as f:
            json.dump(repo_index, f, indent=2, default=str)
    
    async def _generate_main_readme(self, library_data: Dict, output_dir: Path):
        """Generate the main README.md file."""
        template = self.jinja_env.get_template('main_readme.md')
        content = template.render(library_data=library_data)
        
        with open(output_dir / 'README.md', 'w') as f:
            f.write(content)
    
    async def _generate_category_pages(self, library_data: Dict, output_dir: Path):
        """Generate individual category pages."""
        categories_dir = output_dir / 'categories'
        categories_dir.mkdir(exist_ok=True)
        
        template = self.jinja_env.get_template('category_page.md')
        
        for category, repos in library_data['categories'].items():
            # Calculate category statistics
            category_stats = {
                'total_repos': len(repos),
                'total_stars': sum(r['basic_info'].get('stargazers_count', 0) for r in repos),
                'languages': Counter(r['basic_info'].get('language') for r in repos if r['basic_info'].get('language')),
                'avg_quality': sum(r['curation']['quality_score'] for r in repos) / len(repos) if repos else 0,
                'recent_repos': [r for r in repos if self._is_recently_updated(r['basic_info'])]
            }
            
            content = template.render(
                category=category,
                repositories=repos,
                stats=category_stats
            )
            
            filename = f"{self._slugify(category)}.md"
            with open(categories_dir / filename, 'w') as f:
                f.write(content)
    
    async def _generate_language_pages(self, library_data: Dict, output_dir: Path):
        """Generate pages organized by programming language."""
        languages_dir = output_dir / 'languages'
        languages_dir.mkdir(exist_ok=True)
        
        template = self.jinja_env.get_template('language_page.md')
        
        for language, repos in library_data['languages'].items():
            if not language:
                continue
            
            # Group by category within language
            categories_in_lang = defaultdict(list)
            for repo in repos:
                category = repo['curation']['category']
                categories_in_lang[category].append(repo)
            
            content = template.render(
                language=language,
                repositories=repos,
                categories=dict(categories_in_lang),
                total_repos=len(repos)
            )
            
            filename = f"{self._slugify(language)}.md"
            with open(languages_dir / filename, 'w') as f:
                f.write(content)
    
    async def _generate_statistics_page(self, library_data: Dict, output_dir: Path):
        """Generate comprehensive statistics page."""
        template = self.jinja_env.get_template('statistics.md')
        
        stats = library_data['statistics']
        
        # Enhanced statistics
        enhanced_stats = {
            **stats,
            'category_distribution': dict(Counter(
                repo['curation']['category'] for repo in library_data['repositories']
            )),
            'quality_distribution': dict(Counter(
                self._get_quality_level(repo['curation']['quality_score']) 
                for repo in library_data['repositories']
            )),
            'fork_vs_original': {
                'forks': len([r for r in library_data['repositories'] if r['basic_info'].get('fork')]),
                'original': len([r for r in library_data['repositories'] if not r['basic_info'].get('fork')])
            }
        }
        
        content = template.render(statistics=enhanced_stats)
        
        with open(output_dir / 'STATISTICS.md', 'w') as f:
            f.write(content)
    
    async def _generate_quality_report(self, library_data: Dict, output_dir: Path):
        """Generate quality analysis report."""
        template = self.jinja_env.get_template('quality_report.md')
        
        # Analyze quality metrics
        quality_analysis = {
            'high_quality': [r for r in library_data['repositories'] if r['curation']['quality_score'] >= 0.8],
            'medium_quality': [r for r in library_data['repositories'] if 0.6 <= r['curation']['quality_score'] < 0.8],
            'low_quality': [r for r in library_data['repositories'] if r['curation']['quality_score'] < 0.6],
            'quality_by_category': defaultdict(list),
            'improvement_suggestions': []
        }
        
        # Group quality by category
        for repo in library_data['repositories']:
            category = repo['curation']['category']
            quality_analysis['quality_by_category'][category].append(repo['curation']['quality_score'])
        
        # Calculate average quality per category
        category_quality = {}
        for category, scores in quality_analysis['quality_by_category'].items():
            category_quality[category] = sum(scores) / len(scores) if scores else 0
        
        quality_analysis['category_quality_avg'] = category_quality
        
        content = template.render(quality=quality_analysis)
        
        with open(output_dir / 'QUALITY_REPORT.md', 'w') as f:
            f.write(content)
    
    async def _generate_web_assets(self, assets_dir: Path):
        """Generate CSS and JavaScript for HTML documentation."""
        # Simple CSS for styling
        css_content = """
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .repo-card { border: 1px solid #e1e4e8; border-radius: 6px; padding: 16px; margin: 10px 0; }
        .repo-title { font-size: 1.25em; font-weight: 600; }
        .repo-desc { color: #586069; margin: 8px 0; }
        .repo-meta { font-size: 0.875em; color: #586069; }
        .tag { background: #f1f8ff; color: #0366d6; padding: 2px 6px; border-radius: 3px; margin: 2px; }
        .quality-high { border-left: 4px solid #28a745; }
        .quality-medium { border-left: 4px solid #ffd33d; }
        .quality-low { border-left: 4px solid #d73a49; }
        """
        
        with open(assets_dir / 'style.css', 'w') as f:
            f.write(css_content)
        
        # Simple JavaScript for interactivity
        js_content = """
        function filterRepos(category) {
            const repos = document.querySelectorAll('.repo-card');
            repos.forEach(repo => {
                if (category === 'all' || repo.dataset.category === category) {
                    repo.style.display = 'block';
                } else {
                    repo.style.display = 'none';
                }
            });
        }
        
        function searchRepos() {
            const query = document.getElementById('search').value.toLowerCase();
            const repos = document.querySelectorAll('.repo-card');
            repos.forEach(repo => {
                const text = repo.textContent.toLowerCase();
                repo.style.display = text.includes(query) ? 'block' : 'none';
            });
        }
        """
        
        with open(assets_dir / 'script.js', 'w') as f:
            f.write(js_content)
    
    def _create_default_templates(self):
        """Create default Jinja2 templates if they don't exist."""
        template_dir = Path(self.jinja_env.loader.searchpath[0])
        
        templates = {
            'main_readme.md': self._get_main_readme_template(),
            'category_page.md': self._get_category_page_template(),
            'language_page.md': self._get_language_page_template(),
            'statistics.md': self._get_statistics_template(),
            'quality_report.md': self._get_quality_report_template(),
            'index.html': self._get_index_html_template(),
            'category.html': self._get_category_html_template()
        }
        
        for filename, content in templates.items():
            template_file = template_dir / filename
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    f.write(content)
    
    def _get_main_readme_template(self) -> str:
        return """# 🚀 My Curated Development Library

*Generated on {{ library_data.metadata.generated_at }}*

## 📊 Quick Stats

- **Total Repositories**: {{ library_data.statistics.total_repos }}
- **Categories**: {{ library_data.categories|length }}
- **Programming Languages**: {{ library_data.statistics.languages|length }}
- **Total Stars**: {{ library_data.statistics.total_stars }}

## 📚 Categories

{% for category, repos in library_data.categories.items() %}
### [{{ category }}](categories/{{ category|lower|replace(' ', '-') }}.md)
*{{ repos|length }} repositories*

{% for repo in repos[:3] %}
- [{{ repo.basic_info.name }}]({{ repo.basic_info.html_url }}) - {{ repo.basic_info.description[:100] }}...
{% endfor %}
{% if repos|length > 3 %}
[... and {{ repos|length - 3 }} more](categories/{{ category|lower|replace(' ', '-') }}.md)
{% endif %}

{% endfor %}

## 📈 Recent Activity

{% for repo in library_data.recent_activity[:10] %}
- [{{ repo.basic_info.name }}]({{ repo.basic_info.html_url }}) - Updated {{ repo.basic_info.updated_at }}
{% endfor %}

---
*Curated with ❤️ by [GitHub Repository Curator](https://github.com/your-username/github-curator)*
"""
    
    def _get_category_page_template(self) -> str:
        return """# {{ category }}

*{{ stats.total_repos }} repositories | {{ stats.total_stars }} total stars | Average quality: {{ "%.2f"|format(stats.avg_quality) }}*

## 📊 Category Statistics

- **Total Repositories**: {{ stats.total_repos }}
- **Total Stars**: {{ stats.total_stars }}
- **Average Quality Score**: {{ "%.2f"|format(stats.avg_quality) }}
- **Top Languages**: 
{% for lang, count in stats.languages.most_common(5) %}
  - {{ lang }}: {{ count }} repos
{% endfor %}

## 📚 Repositories

{% for repo in repositories %}
### [{{ repo.basic_info.name }}]({{ repo.basic_info.html_url }})

{{ repo.basic_info.description or "No description available." }}

**Details:**
- **Language**: {{ repo.basic_info.language or "Not specified" }}
- **Stars**: {{ repo.basic_info.stargazers_count }}
- **Quality Score**: {{ "%.2f"|format(repo.curation.quality_score) }}
- **Tags**: {% for tag in repo.curation.tags %}{{ tag }}{% if not loop.last %}, {% endif %}{% endfor %}

---
{% endfor %}
"""
    
    def _get_language_page_template(self) -> str:
        return """# {{ language }} Projects

*{{ total_repos }} repositories*

{% for category, repos in categories.items() %}
## {{ category }}

{% for repo in repos %}
### [{{ repo.basic_info.name }}]({{ repo.basic_info.html_url }})
{{ repo.basic_info.description or "No description" }} (⭐ {{ repo.basic_info.stargazers_count }})

{% endfor %}
{% endfor %}
"""
    
    def _get_statistics_template(self) -> str:
        return """# 📊 Library Statistics

*Generated on {{ statistics.last_updated }}*

## Overview
- Total Repositories: {{ statistics.total_repos }}
- Original Repositories: {{ statistics.original_repos }}
- Forked Repositories: {{ statistics.forked_stars }}
- Total Stars: {{ statistics.total_stars }}
- Total Forks: {{ statistics.total_forks }}

## Category Distribution
{% for category, count in statistics.category_distribution.items() %}
- {{ category }}: {{ count }} repositories
{% endfor %}

## Language Distribution
{% for lang, count in statistics.top_languages %}
- {{ lang }}: {{ count }} repositories
{% endfor %}

## Quality Distribution
{% for level, count in statistics.quality_distribution.items() %}
- {{ level|title }} Quality: {{ count }} repositories
{% endfor %}
"""
    
    def _get_quality_report_template(self) -> str:
        return """# 🏆 Quality Report

## High Quality Repositories ({{ quality.high_quality|length }})
{% for repo in quality.high_quality %}
- [{{ repo.basic_info.name }}]({{ repo.basic_info.html_url }}) - Score: {{ "%.2f"|format(repo.curation.quality_score) }}
{% endfor %}

## Quality by Category
{% for category, avg_score in quality.category_quality_avg.items() %}
- {{ category }}: {{ "%.2f"|format(avg_score) }} average
{% endfor %}
"""
    
    def _get_index_html_template(self) -> str:
        return """<!DOCTYPE html>
<html>
<head>
    <title>My Development Library</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div class="container">
        <h1>🚀 My Development Library</h1>
        
        <div class="search-section">
            <input type="text" id="search" placeholder="Search repositories..." onkeyup="searchRepos()">
            <select onchange="filterRepos(this.value)">
                <option value="all">All Categories</option>
                {% for category in library_data.categories.keys() %}
                <option value="{{ category }}">{{ category }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="repositories">
            {% for repo in library_data.repositories %}
            <div class="repo-card quality-{{ 'high' if repo.curation.quality_score >= 0.8 else 'medium' if repo.curation.quality_score >= 0.6 else 'low' }}" 
                 data-category="{{ repo.curation.category }}">
                <h3 class="repo-title">
                    <a href="{{ repo.basic_info.html_url }}">{{ repo.basic_info.name }}</a>
                </h3>
                <p class="repo-desc">{{ repo.basic_info.description or "No description" }}</p>
                <div class="repo-meta">
                    <span>{{ repo.basic_info.language or "Unknown" }}</span> |
                    <span>⭐ {{ repo.basic_info.stargazers_count }}</span> |
                    <span>Quality: {{ "%.1f"|format(repo.curation.quality_score * 10) }}/10</span>
                </div>
                <div class="tags">
                    {% for tag in repo.curation.tags[:5] %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script src="assets/script.js"></script>
</body>
</html>"""
    
    def _get_category_html_template(self) -> str:
        return """<!DOCTYPE html>
<html>
<head>
    <title>{{ category }} - My Development Library</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div class="container">
        <h1>{{ category }}</h1>
        <p>{{ repositories|length }} repositories</p>
        
        {% for repo in repositories %}
        <div class="repo-card">
            <h3><a href="{{ repo.basic_info.html_url }}">{{ repo.basic_info.name }}</a></h3>
            <p>{{ repo.basic_info.description or "No description" }}</p>
            <div class="repo-meta">
                {{ repo.basic_info.language or "Unknown" }} | ⭐ {{ repo.basic_info.stargazers_count }}
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>"""
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        return text.lower().replace(' ', '-').replace('&', 'and')
    
    def _get_quality_level(self, score: float) -> str:
        """Convert quality score to human-readable level."""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _is_recently_updated(self, repo: Dict) -> bool:
        """Check if repository was updated recently (within 30 days)."""
        try:
            from datetime import datetime, timedelta
            updated_at = datetime.fromisoformat(repo.get('updated_at', '').replace('Z', '+00:00'))
            cutoff_date = datetime.now().replace(tzinfo=updated_at.tzinfo) - timedelta(days=30)
            return updated_at > cutoff_date
        except (ValueError, TypeError):
            return False
