"""Configuration settings for GitHub Repository Curator."""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import List, Dict, Optional
import os


class Settings(BaseSettings):
    """Main application settings."""
    
    # GitHub API Configuration
    github_token: str = Field(description="GitHub Personal Access Token")
    github_username: Optional[str] = Field(default=None, description="GitHub username (auto-detected if not provided)")
    
    # Fork Configuration
    fork_as_private: bool = Field(default=True, description="Fork repositories as private")
    fork_prefix: str = Field(default="", description="Prefix for forked repository names")
    fork_suffix: str = Field(default="", description="Suffix for forked repository names")
    max_concurrent_forks: int = Field(default=5, description="Maximum concurrent fork operations")
    
    # Curation Configuration
    auto_categorize: bool = Field(default=True, description="Automatically categorize repositories")
    update_descriptions: bool = Field(default=True, description="Update repository descriptions with curation metadata")
    create_topics: bool = Field(default=True, description="Create GitHub topics for categorization")
    
    # Storage Configuration
    data_dir: Path = Field(default=Path("./data"), description="Directory for storing application data")
    cache_dir: Path = Field(default=Path("./cache"), description="Directory for caching API responses")
    docs_dir: Path = Field(default=Path("./library_docs"), description="Directory for generated documentation")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./curator.db", description="Database connection URL")
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL for caching")
    
    # Web Dashboard Configuration
    dashboard_host: str = Field(default="localhost", description="Dashboard host")
    dashboard_port: int = Field(default=8080, description="Dashboard port")
    dashboard_secret_key: str = Field(default="your-secret-key-here", description="Secret key for sessions")
    
    # Rate Limiting
    github_rate_limit_buffer: int = Field(default=100, description="Buffer for GitHub rate limiting")
    requests_per_hour: int = Field(default=4000, description="Maximum requests per hour")
    
    # Sync Configuration
    sync_interval_hours: int = Field(default=24, description="Interval for automatic sync in hours")
    sync_on_startup: bool = Field(default=False, description="Sync repositories on startup")
    
    # Categories Configuration
    default_categories: List[str] = Field(
        default=[
            "Web Development",
            "Mobile Development", 
            "DevOps & Infrastructure",
            "Data Science & AI",
            "Security & Privacy",
            "Game Development",
            "Desktop Applications",
            "CLI Tools",
            "Libraries & Frameworks",
            "Educational",
            "Research",
            "Miscellaneous"
        ],
        description="Default categories for repository classification"
    )
    
    # Language Mappings for Better Categorization
    language_category_mapping: Dict[str, str] = Field(
        default={
            "JavaScript": "Web Development",
            "TypeScript": "Web Development", 
            "Python": "Data Science & AI",
            "Go": "DevOps & Infrastructure",
            "Rust": "CLI Tools",
            "Java": "Desktop Applications",
            "Kotlin": "Mobile Development",
            "Swift": "Mobile Development",
            "C#": "Desktop Applications",
            "C++": "Game Development",
            "C": "System Programming",
            "Shell": "DevOps & Infrastructure",
            "Dockerfile": "DevOps & Infrastructure",
            "YAML": "DevOps & Infrastructure",
        },
        description="Mapping of programming languages to default categories"
    )
    
    # Exclusion Patterns
    exclude_repos: List[str] = Field(
        default=[
            "fork",
            "archive",
            "deprecated",
            "legacy",
            "old",
        ],
        description="Patterns in repository names/descriptions to exclude from curation"
    )
    
    exclude_languages: List[str] = Field(
        default=[
            "TeX",
            "Jupyter Notebook"  # Optional - might want to keep these for research
        ],
        description="Programming languages to exclude from curation"
    )
    
    # Documentation Generation
    generate_readme: bool = Field(default=True, description="Generate README files for categories")
    include_stats: bool = Field(default=True, description="Include statistics in generated documentation")
    markdown_template: str = Field(default="default", description="Template for markdown generation")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from .env file
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)


class CurationRules(BaseSettings):
    """Rules for repository curation and categorization."""
    
    # Keyword-based categorization rules
    keyword_rules: Dict[str, List[str]] = Field(
        default={
            "Web Development": [
                "react", "vue", "angular", "nodejs", "express", "django", "flask", 
                "fastapi", "nextjs", "nuxt", "svelte", "web", "frontend", "backend",
                "html", "css", "javascript", "typescript", "tailwind", "bootstrap"
            ],
            "Mobile Development": [
                "android", "ios", "mobile", "react-native", "flutter", "ionic", 
                "xamarin", "swift", "kotlin", "java-android", "objective-c"
            ],
            "DevOps & Infrastructure": [
                "docker", "kubernetes", "terraform", "ansible", "jenkins", "gitlab-ci",
                "aws", "azure", "gcp", "cloud", "infrastructure", "devops", "ci-cd",
                "monitoring", "logging", "prometheus", "grafana", "nginx", "apache"
            ],
            "Data Science & AI": [
                "machine-learning", "deep-learning", "neural-network", "ai", "ml",
                "data-science", "pandas", "numpy", "scikit-learn", "tensorflow", 
                "pytorch", "jupyter", "data-analysis", "statistics", "nlp", "cv"
            ],
            "Security & Privacy": [
                "security", "privacy", "encryption", "cryptography", "penetration-testing",
                "vulnerability", "cybersecurity", "infosec", "zero-trust", "blockchain",
                "oauth", "authentication", "authorization", "ssl", "tls"
            ],
            "Game Development": [
                "game", "unity", "unreal", "godot", "gaming", "gamedev", "3d", "graphics",
                "opengl", "vulkan", "directx", "physics", "animation", "shader"
            ],
            "CLI Tools": [
                "cli", "command-line", "terminal", "shell", "bash", "zsh", "fish",
                "automation", "script", "utility", "tool", "productivity"
            ],
            "Libraries & Frameworks": [
                "library", "framework", "sdk", "api", "package", "module", "plugin",
                "extension", "component", "boilerplate", "template", "starter"
            ],
            "Educational": [
                "tutorial", "learning", "course", "education", "teaching", "example",
                "demo", "workshop", "guide", "documentation", "book", "reference"
            ]
        },
        description="Keyword-based rules for categorizing repositories"
    )
    
    # Minimum stars for automatic inclusion
    min_stars_threshold: int = Field(default=10, description="Minimum stars for automatic inclusion")
    
    # Quality indicators
    quality_indicators: List[str] = Field(
        default=[
            "readme",
            "license", 
            "contributing",
            "tests",
            "documentation",
            "ci",
            "code-of-conduct"
        ],
        description="Indicators of repository quality"
    )
    
    class Config:
        env_file = ".env.rules"
        env_file_encoding = "utf-8"
