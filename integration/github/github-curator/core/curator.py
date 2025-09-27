"""Repository curation system for organizing and categorizing repositories."""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, Counter
import json

from services.github_service import GitHubService
from config.settings import Settings, CurationRules
from core.categorizer import RepositoryCategorizer

logger = logging.getLogger(__name__)


@dataclass
class CurationResult:
    """Result of a repository curation operation."""
    repo: Dict
    category: str
    confidence: float
    tags: List[str]
    quality_score: float
    metadata: Dict
    updated: bool = False
    error: Optional[str] = None


class RepositoryCurator:
    """Manages repository curation, categorization, and organization."""
    
    def __init__(self, github_service: GitHubService, settings: Settings):
        self.github = github_service
        self.settings = settings
        self.rules = CurationRules()
        self.categorizer = RepositoryCategorizer(settings, self.rules)
        self.curation_cache = {}
        
    async def curate_all_repositories(self, filters: Optional[Dict] = None) -> Dict[str, List[CurationResult]]:
        """Curate all user repositories with categorization and metadata."""
        filters = filters or {}
        results = defaultdict(list)
        total_processed = 0
        
        async for repo in self.github.get_user_repositories():
            # Apply category filters if specified
            if filters.get('categories'):
                skip = True
                for category in filters['categories']:
                    if category.lower() in (repo.get('description', '').lower() + ' ' + repo['name'].lower()):
                        skip = False
                        break
                if skip:
                    continue
            
            curation_result = await self.curate_repository(repo, force_update=filters.get('update_existing', False))
            if curation_result:
                results[curation_result.category].append(curation_result)
                total_processed += 1
        
        logger.info(f"Curated {total_processed} repositories into {len(results)} categories")
        
        # Generate category summaries
        await self._generate_category_summaries(results)
        
        return dict(results)
    
    async def curate_repository(self, repo: Dict, force_update: bool = False) -> Optional[CurationResult]:
        """Curate a single repository."""
        repo_id = repo['id']
        
        # Check cache if not forcing update
        if not force_update and repo_id in self.curation_cache:
            cached_result = self.curation_cache[repo_id]
            if self._is_cache_valid(cached_result, repo):
                return cached_result
        
        try:
            # Categorize the repository
            category, confidence = await self.categorizer.categorize_repository(repo)
            
            # Generate tags
            tags = await self._generate_tags(repo, category)
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(repo)
            
            # Generate metadata
            metadata = await self._generate_metadata(repo, category, tags, quality_score)
            
            # Create curation result
            result = CurationResult(
                repo=repo,
                category=category,
                confidence=confidence,
                tags=tags,
                quality_score=quality_score,
                metadata=metadata
            )
            
            # Update repository if settings allow
            if self.settings.auto_categorize and confidence > 0.7:
                updated = await self._update_repository_metadata(repo, result)
                result.updated = updated
            
            # Cache the result
            self.curation_cache[repo_id] = result
            
            logger.debug(f"Curated {repo['full_name']} -> {category} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to curate {repo['full_name']}: {e}")
            return CurationResult(
                repo=repo,
                category="Miscellaneous",
                confidence=0.0,
                tags=[],
                quality_score=0.0,
                metadata={},
                error=str(e)
            )
    
    async def search_repositories(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search through curated repositories."""
        filters = filters or {}
        results = []
        
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        
        async for repo in self.github.get_user_repositories():
            # Basic text search in name, description, and topics
            searchable_text = " ".join([
                repo['name'],
                repo.get('description', ''),
                " ".join(repo.get('topics', []))
            ]).lower()
            
            if query_lower in searchable_text:
                # Apply filters
                if filters.get('category'):
                    category, _ = await self.categorizer.categorize_repository(repo)
                    if category.lower() != filters['category'].lower():
                        continue
                
                if filters.get('language'):
                    if repo.get('language', '').lower() != filters['language'].lower():
                        continue
                
                results.append(repo)
                
                if filters.get('limit') and len(results) >= filters['limit']:
                    break
        
        return results
    
    async def get_library_stats(self) -> Dict:
        """Get comprehensive statistics about the repository library."""
        stats = {
            'total_repos': 0,
            'forked_stars': 0,
            'original_repos': 0,
            'languages': set(),
            'categories': defaultdict(int),
            'top_languages': [],
            'quality_distribution': defaultdict(int),
            'total_stars': 0,
            'total_forks': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        async for repo in self.github.get_user_repositories():
            stats['total_repos'] += 1
            
            # Fork analysis
            if repo['fork']:
                stats['forked_stars'] += 1
            else:
                stats['original_repos'] += 1
            
            # Language analysis
            if repo.get('language'):
                stats['languages'].add(repo['language'])
            
            # Category analysis
            category, _ = await self.categorizer.categorize_repository(repo)
            stats['categories'][category] += 1
            
            # Stars and forks
            stats['total_stars'] += repo.get('stargazers_count', 0)
            stats['total_forks'] += repo.get('forks_count', 0)
            
            # Quality analysis
            quality_score = await self._calculate_quality_score(repo)
            if quality_score >= 0.8:
                stats['quality_distribution']['high'] += 1
            elif quality_score >= 0.6:
                stats['quality_distribution']['medium'] += 1
            else:
                stats['quality_distribution']['low'] += 1
        
        # Convert languages set to count
        language_counts = defaultdict(int)
        async for repo in self.github.get_user_repositories():
            if repo.get('language'):
                language_counts[repo['language']] += 1
        
        stats['languages'] = list(stats['languages'])
        stats['top_languages'] = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
        
        return stats
    
    async def _generate_tags(self, repo: Dict, category: str) -> List[str]:
        """Generate relevant tags for a repository."""
        tags = []
        
        # Add category as a tag
        tags.append(category.lower().replace(' ', '-'))
        
        # Add language tag
        if repo.get('language'):
            tags.append(f"lang-{repo['language'].lower()}")
        
        # Add size-based tags
        size = repo.get('size', 0)
        if size > 10000:
            tags.append('large-project')
        elif size > 1000:
            tags.append('medium-project')
        else:
            tags.append('small-project')
        
        # Add popularity tags
        stars = repo.get('stargazers_count', 0)
        if stars > 1000:
            tags.append('popular')
        elif stars > 100:
            tags.append('notable')
        
        # Add activity tags
        if repo.get('archived'):
            tags.append('archived')
        
        if repo.get('fork'):
            tags.append('forked')
        else:
            tags.append('original')
        
        # Add quality-based tags
        quality_score = await self._calculate_quality_score(repo)
        if quality_score > 0.8:
            tags.append('high-quality')
        elif quality_score > 0.6:
            tags.append('good-quality')
        
        # Extract tags from description and topics
        description_tags = self._extract_tags_from_text(repo.get('description', ''))
        tags.extend(description_tags)
        
        # Add existing topics
        tags.extend(repo.get('topics', []))
        
        # Remove duplicates and normalize
        unique_tags = list(set(tag.lower().replace(' ', '-') for tag in tags if tag))
        
        return sorted(unique_tags)
    
    async def _calculate_quality_score(self, repo: Dict) -> float:
        """Calculate a quality score for a repository."""
        score = 0.0
        max_score = 10.0
        
        # Has description
        if repo.get('description') and len(repo['description'].strip()) > 10:
            score += 1.0
        
        # Has license
        if repo.get('license'):
            score += 1.0
        
        # Has topics
        if repo.get('topics') and len(repo['topics']) > 0:
            score += 1.0
        
        # Has README (we'll assume it does if it has a description)
        if repo.get('description'):
            score += 1.0
        
        # Star count (logarithmic scale)
        stars = repo.get('stargazers_count', 0)
        if stars > 0:
            import math
            star_score = min(2.0, math.log10(stars + 1) / 2)
            score += star_score
        
        # Recent activity (based on pushed_at)
        if repo.get('pushed_at'):
            try:
                from datetime import datetime, timedelta
                pushed_date = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
                days_since_push = (datetime.now().replace(tzinfo=pushed_date.tzinfo) - pushed_date).days
                
                if days_since_push < 30:
                    score += 2.0
                elif days_since_push < 90:
                    score += 1.5
                elif days_since_push < 365:
                    score += 1.0
            except (ValueError, TypeError):
                pass
        
        # Fork count indicates usefulness
        forks = repo.get('forks_count', 0)
        if forks > 10:
            score += 1.0
        elif forks > 0:
            score += 0.5
        
        # Not archived
        if not repo.get('archived', False):
            score += 1.0
        
        return min(1.0, score / max_score)
    
    async def _generate_metadata(self, repo: Dict, category: str, tags: List[str], quality_score: float) -> Dict:
        """Generate comprehensive metadata for a repository."""
        metadata = {
            'curation_date': datetime.now().isoformat(),
            'category': category,
            'tags': tags,
            'quality_score': quality_score,
            'metrics': {
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'watchers': repo.get('watchers_count', 0),
                'issues': repo.get('open_issues_count', 0),
                'size_kb': repo.get('size', 0)
            },
            'dates': {
                'created': repo.get('created_at'),
                'updated': repo.get('updated_at'),
                'pushed': repo.get('pushed_at')
            },
            'classification': {
                'is_fork': repo.get('fork', False),
                'is_archived': repo.get('archived', False),
                'is_private': repo.get('private', False),
                'language': repo.get('language'),
                'license': repo.get('license')
            }
        }
        
        # Add parent info for forks
        if repo.get('parent'):
            metadata['fork_info'] = {
                'parent_full_name': repo['parent'].get('full_name'),
                'parent_stars': repo['parent'].get('stargazers_count', 0)
            }
        
        return metadata
    
    async def _update_repository_metadata(self, repo: Dict, curation_result: CurationResult) -> bool:
        """Update repository with curation metadata."""
        updates = {}
        
        # Update description with category if enabled
        if self.settings.update_descriptions and curation_result.confidence > 0.8:
            original_desc = repo.get('description', '')
            if not original_desc.startswith(f"[{curation_result.category}]"):
                new_desc = f"[{curation_result.category}] {original_desc}".strip()
                updates['description'] = new_desc
        
        # Update repository if we have changes
        success = True
        if updates:
            success = await self.github.update_repository(repo['full_name'], updates)
        
        # Set topics if enabled
        if self.settings.create_topics and curation_result.tags:
            # Limit to 20 topics (GitHub limit) and clean them
            clean_tags = [tag for tag in curation_result.tags[:20] if re.match(r'^[a-z0-9\-]+$', tag)]
            if clean_tags:
                topics_success = await self.github.set_repository_topics(repo['full_name'], clean_tags)
                success = success and topics_success
        
        return success
    
    async def _generate_category_summaries(self, results: Dict[str, List[CurationResult]]):
        """Generate summary statistics for each category."""
        summaries = {}
        
        for category, repos in results.items():
            total_repos = len(repos)
            avg_quality = sum(r.quality_score for r in repos) / total_repos if total_repos > 0 else 0
            total_stars = sum(r.repo.get('stargazers_count', 0) for r in repos)
            languages = Counter(r.repo.get('language') for r in repos if r.repo.get('language'))
            
            summaries[category] = {
                'total_repositories': total_repos,
                'average_quality_score': round(avg_quality, 2),
                'total_stars': total_stars,
                'top_languages': dict(languages.most_common(5)),
                'last_updated': datetime.now().isoformat()
            }
        
        # Save summaries to data directory
        summary_file = self.settings.data_dir / 'category_summaries.json'
        try:
            with open(summary_file, 'w') as f:
                json.dump(summaries, f, indent=2)
            logger.info(f"Saved category summaries to {summary_file}")
        except Exception as e:
            logger.error(f"Failed to save category summaries: {e}")
    
    def _extract_tags_from_text(self, text: str) -> List[str]:
        """Extract relevant tags from repository description."""
        if not text:
            return []
        
        text_lower = text.lower()
        extracted_tags = []
        
        # Common technology keywords
        tech_keywords = [
            'api', 'cli', 'gui', 'web', 'mobile', 'desktop', 'server', 'client',
            'framework', 'library', 'tool', 'utility', 'bot', 'plugin', 'extension',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
            'react', 'vue', 'angular', 'nodejs', 'python', 'golang', 'rust', 'java'
        ]
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                extracted_tags.append(keyword)
        
        return extracted_tags
    
    def _is_cache_valid(self, cached_result: CurationResult, repo: Dict) -> bool:
        """Check if cached curation result is still valid."""
        # Simple cache validation based on update time
        try:
            cached_time = datetime.fromisoformat(cached_result.metadata.get('curation_date', ''))
            repo_updated = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
            
            # Cache is valid if curation was done after the last repo update
            return cached_time > repo_updated
        except (ValueError, TypeError):
            return False
