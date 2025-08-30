"""Web dashboard for GitHub Repository Curator."""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from services.github_service import GitHubService
from config.settings import Settings
from core.curator import RepositoryCurator
from core.fork_manager import ForkManager
from core.library_generator import LibraryGenerator

logger = logging.getLogger(__name__)


class DashboardApp:
    """FastAPI-based web dashboard for repository management."""
    
    def __init__(self, github_service: GitHubService, settings: Settings):
        self.github = github_service
        self.settings = settings
        self.curator = RepositoryCurator(github_service, settings)
        self.fork_manager = ForkManager(github_service, settings)
        self.library_generator = LibraryGenerator(github_service, settings)
        
        # Setup FastAPI app
        self.app = FastAPI(
            title="GitHub Repository Curator",
            description="Manage and curate your GitHub repository ecosystem",
            version="1.0.0"
        )
        
        self._setup_routes()
        self._setup_static_files()
        
    def _setup_routes(self):
        """Setup all API routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home(request: Request):
            """Main dashboard page."""
            stats = await self.curator.get_library_stats()
            recent_activity = []
            
            # Get recent activity
            count = 0
            async for repo in self.github.get_user_repositories():
                if count >= 10:
                    break
                if self._is_recently_updated(repo):
                    recent_activity.append(repo)
                    count += 1
            
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "stats": stats,
                "recent_activity": recent_activity,
                "user": self.github.get_user_info()
            })
        
        @self.app.get("/api/repositories")
        async def get_repositories(
            category: Optional[str] = None,
            language: Optional[str] = None,
            limit: int = 50
        ):
            """Get repositories with optional filtering."""
            repos = []
            count = 0
            
            async for repo in self.github.get_user_repositories():
                if count >= limit:
                    break
                
                # Apply filters
                if language and repo.get('language') != language:
                    continue
                
                if category:
                    repo_category, _ = await self.curator.categorizer.categorize_repository(repo)
                    if repo_category != category:
                        continue
                
                # Get curation data
                curation_result = await self.curator.curate_repository(repo)
                repo_data = {
                    **repo,
                    'curation': {
                        'category': curation_result.category if curation_result else 'Unknown',
                        'confidence': curation_result.confidence if curation_result else 0,
                        'quality_score': curation_result.quality_score if curation_result else 0,
                        'tags': curation_result.tags if curation_result else []
                    }
                }
                
                repos.append(repo_data)
                count += 1
            
            return JSONResponse(repos)
        
        @self.app.get("/api/categories")
        async def get_categories():
            """Get all available categories with counts."""
            category_counts = {}
            
            async for repo in self.github.get_user_repositories():
                category, _ = await self.curator.categorizer.categorize_repository(repo)
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return JSONResponse(category_counts)
        
        @self.app.get("/api/languages")
        async def get_languages():
            """Get all programming languages with counts."""
            language_counts = {}
            
            async for repo in self.github.get_user_repositories():
                language = repo.get('language')
                if language:
                    language_counts[language] = language_counts.get(language, 0) + 1
            
            return JSONResponse(language_counts)
        
        @self.app.get("/api/stats")
        async def get_stats():
            """Get comprehensive statistics."""
            return JSONResponse(await self.curator.get_library_stats())
        
        @self.app.post("/api/fork-starred")
        async def fork_starred_repos(background_tasks: BackgroundTasks, limit: Optional[int] = None):
            """Fork starred repositories in the background."""
            
            async def fork_task():
                try:
                    results = await self.fork_manager.fork_all_starred(limit)
                    logger.info(f"Fork operation completed: {results}")
                except Exception as e:
                    logger.error(f"Fork operation failed: {e}")
            
            background_tasks.add_task(fork_task)
            return JSONResponse({"message": "Fork operation started", "status": "running"})
        
        @self.app.post("/api/curate-repos")
        async def curate_repositories(background_tasks: BackgroundTasks):
            """Curate all repositories in the background."""
            
            async def curate_task():
                try:
                    results = await self.curator.curate_all_repositories()
                    logger.info(f"Curation completed: {len(results)} categories")
                except Exception as e:
                    logger.error(f"Curation failed: {e}")
            
            background_tasks.add_task(curate_task)
            return JSONResponse({"message": "Curation started", "status": "running"})
        
        @self.app.post("/api/sync-forks")
        async def sync_forks(background_tasks: BackgroundTasks):
            """Sync all forks in the background."""
            
            async def sync_task():
                try:
                    results = await self.fork_manager.sync_all_forks()
                    logger.info(f"Sync operation completed: {results}")
                except Exception as e:
                    logger.error(f"Sync operation failed: {e}")
            
            background_tasks.add_task(sync_task)
            return JSONResponse({"message": "Sync operation started", "status": "running"})
        
        @self.app.post("/api/generate-docs")
        async def generate_documentation(
            background_tasks: BackgroundTasks,
            format_type: str = "markdown"
        ):
            """Generate library documentation."""
            
            async def generate_task():
                try:
                    output_dir = self.settings.docs_dir / f"generated_{format_type}"
                    success = await self.library_generator.generate_documentation(format_type, output_dir)
                    if success:
                        logger.info(f"Documentation generated in {output_dir}")
                    else:
                        logger.error("Documentation generation failed")
                except Exception as e:
                    logger.error(f"Documentation generation failed: {e}")
            
            background_tasks.add_task(generate_task)
            return JSONResponse({
                "message": f"Documentation generation started ({format_type})",
                "status": "running"
            })
        
        @self.app.get("/api/search")
        async def search_repositories(
            query: str,
            category: Optional[str] = None,
            language: Optional[str] = None,
            limit: int = 20
        ):
            """Search repositories."""
            filters = {
                'category': category,
                'language': language,
                'limit': limit
            }
            
            results = await self.curator.search_repositories(query, filters)
            return JSONResponse(results)
        
        @self.app.get("/categories", response_class=HTMLResponse)
        async def categories_page(request: Request):
            """Categories overview page."""
            categories = {}
            
            async for repo in self.github.get_user_repositories():
                category, confidence = await self.curator.categorizer.categorize_repository(repo)
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    'repo': repo,
                    'confidence': confidence
                })
            
            return self.templates.TemplateResponse("categories.html", {
                "request": request,
                "categories": categories
            })
        
        @self.app.get("/category/{category_name}", response_class=HTMLResponse)
        async def category_detail(request: Request, category_name: str):
            """Detailed view of a specific category."""
            repos = []
            
            async for repo in self.github.get_user_repositories():
                category, confidence = await self.curator.categorizer.categorize_repository(repo)
                if category.lower().replace(' ', '-') == category_name.lower():
                    curation_result = await self.curator.curate_repository(repo)
                    repos.append({
                        'repo': repo,
                        'curation': curation_result
                    })
            
            return self.templates.TemplateResponse("category_detail.html", {
                "request": request,
                "category_name": category_name.replace('-', ' ').title(),
                "repositories": repos
            })
        
        @self.app.get("/analytics", response_class=HTMLResponse)
        async def analytics_page(request: Request):
            """Analytics and insights page."""
            stats = await self.curator.get_library_stats()
            
            # Additional analytics
            quality_distribution = []
            category_quality = {}
            
            async for repo in self.github.get_user_repositories():
                curation_result = await self.curator.curate_repository(repo)
                if curation_result:
                    quality_distribution.append(curation_result.quality_score)
                    
                    category = curation_result.category
                    if category not in category_quality:
                        category_quality[category] = []
                    category_quality[category].append(curation_result.quality_score)
            
            # Calculate average quality per category
            avg_category_quality = {}
            for category, scores in category_quality.items():
                avg_category_quality[category] = sum(scores) / len(scores) if scores else 0
            
            return self.templates.TemplateResponse("analytics.html", {
                "request": request,
                "stats": stats,
                "quality_distribution": quality_distribution,
                "category_quality": avg_category_quality
            })
    
    def _setup_static_files(self):
        """Setup static file serving."""
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        templates_dir = Path(__file__).parent / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        self.templates = Jinja2Templates(directory=str(templates_dir))
        
        # Create default templates and static files
        self._create_default_web_files(templates_dir, static_dir)
    
    def _create_default_web_files(self, templates_dir: Path, static_dir: Path):
        """Create default web templates and static files."""
        
        # Create base template
        base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GitHub Repository Curator{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/style.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">🚀 Repository Curator</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/categories">Categories</a>
                <a class="nav-link" href="/analytics">Analytics</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/script.js"></script>
</body>
</html>"""
        
        dashboard_template = """{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1>Welcome to Your Repository Library</h1>
        <p class="lead">Manage and curate your GitHub ecosystem with ease.</p>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">{{ stats.total_repos }}</h5>
                        <p class="card-text">Total Repositories</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">{{ stats.categories|length }}</h5>
                        <p class="card-text">Categories</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">{{ stats.languages|length }}</h5>
                        <p class="card-text">Languages</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">{{ stats.total_stars }}</h5>
                        <p class="card-text">Total Stars</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <h3>Quick Actions</h3>
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-primary" onclick="forkStarred()">Fork Starred Repos</button>
                <button type="button" class="btn btn-success" onclick="curateRepos()">Curate Library</button>
                <button type="button" class="btn btn-info" onclick="syncForks()">Sync Forks</button>
                <button type="button" class="btn btn-warning" onclick="generateDocs()">Generate Docs</button>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <h3>Recent Activity</h3>
        <div class="list-group">
            {% for repo in recent_activity %}
            <a href="{{ repo.html_url }}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">{{ repo.name }}</h6>
                    <small>{{ repo.language or "Unknown" }}</small>
                </div>
                <p class="mb-1">{{ repo.description[:100] }}...</p>
                <small>⭐ {{ repo.stargazers_count }}</small>
            </a>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}"""
        
        # Create CSS
        css_content = """
.repo-card {
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 16px;
    margin: 10px 0;
    transition: box-shadow 0.3s ease;
}

.repo-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.quality-high { border-left: 4px solid #28a745; }
.quality-medium { border-left: 4px solid #ffd33d; }
.quality-low { border-left: 4px solid #d73a49; }

.tag {
    background: #f1f8ff;
    color: #0366d6;
    padding: 2px 6px;
    border-radius: 3px;
    margin: 2px;
    font-size: 0.875em;
}

.category-badge {
    background: #6f42c1;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.875em;
}
"""
        
        # Create JavaScript
        js_content = """
async function forkStarred() {
    const response = await fetch('/api/fork-starred', { method: 'POST' });
    const result = await response.json();
    alert(result.message);
}

async function curateRepos() {
    const response = await fetch('/api/curate-repos', { method: 'POST' });
    const result = await response.json();
    alert(result.message);
}

async function syncForks() {
    const response = await fetch('/api/sync-forks', { method: 'POST' });
    const result = await response.json();
    alert(result.message);
}

async function generateDocs() {
    const response = await fetch('/api/generate-docs', { method: 'POST' });
    const result = await response.json();
    alert(result.message);
}

function filterRepos(category) {
    // Implementation for filtering repositories
}

function searchRepos() {
    // Implementation for searching repositories
}
"""
        
        # Write files
        templates = {
            'base.html': base_template,
            'dashboard.html': dashboard_template
        }
        
        for filename, content in templates.items():
            template_file = templates_dir / filename
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    f.write(content)
        
        # Write static files
        if not (static_dir / 'style.css').exists():
            with open(static_dir / 'style.css', 'w') as f:
                f.write(css_content)
        
        if not (static_dir / 'script.js').exists():
            with open(static_dir / 'script.js', 'w') as f:
                f.write(js_content)
    
    def _is_recently_updated(self, repo: Dict) -> bool:
        """Check if repository was updated recently."""
        try:
            from datetime import datetime, timedelta
            updated_at = datetime.fromisoformat(repo.get('updated_at', '').replace('Z', '+00:00'))
            cutoff_date = datetime.now().replace(tzinfo=updated_at.tzinfo) - timedelta(days=30)
            return updated_at > cutoff_date
        except (ValueError, TypeError):
            return False
    
    def run(self, host: str = "localhost", port: int = 8080, debug: bool = False):
        """Run the web dashboard."""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info" if not debug else "debug",
            reload=debug
        )
