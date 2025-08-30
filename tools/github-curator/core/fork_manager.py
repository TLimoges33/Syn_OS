"""Fork management system for starred repositories."""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

from services.github_service import GitHubService
from config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class ForkOperation:
    """Represents a fork operation."""
    source_repo: Dict
    target_name: str
    status: str = "pending"  # pending, completed, failed, skipped
    error_message: Optional[str] = None
    fork_data: Optional[Dict] = None
    timestamp: datetime = datetime.now()


class ForkManager:
    """Manages forking operations for starred repositories."""
    
    def __init__(self, github_service: GitHubService, settings: Settings):
        self.github = github_service
        self.settings = settings
        self.fork_queue: List[ForkOperation] = []
        self.completed_forks: List[ForkOperation] = []
        self.failed_forks: List[ForkOperation] = []
    
    async def preview_fork_operations(self, limit: Optional[int] = None) -> List[Dict]:
        """Preview what repositories would be forked without actually doing it."""
        fork_candidates = []
        existing_repos = await self._get_existing_repository_names()
        
        count = 0
        async for starred_repo in self.github.get_starred_repositories():
            if limit and count >= limit:
                break
                
            if self._should_fork_repo(starred_repo, existing_repos):
                target_name = self._generate_fork_name(starred_repo)
                fork_candidates.append({
                    'source': f"{starred_repo['owner']['login']}/{starred_repo['name']}",
                    'target': target_name,
                    'description': starred_repo['description'][:100] + '...' if starred_repo['description'] else 'No description',
                    'language': starred_repo['language'] or 'Unknown',
                    'stars': starred_repo['stargazers_count'],
                    'reason': self._get_fork_reason(starred_repo, existing_repos)
                })
                count += 1
        
        logger.info(f"Found {len(fork_candidates)} repositories that would be forked")
        return fork_candidates
    
    async def fork_all_starred(self, limit: Optional[int] = None) -> Dict[str, int]:
        """Fork all starred repositories that don't already exist."""
        existing_repos = await self._get_existing_repository_names()
        semaphore = asyncio.Semaphore(self.settings.max_concurrent_forks)
        
        # Collect fork operations
        tasks = []
        count = 0
        
        async for starred_repo in self.github.get_starred_repositories():
            if limit and count >= limit:
                break
                
            if self._should_fork_repo(starred_repo, existing_repos):
                target_name = self._generate_fork_name(starred_repo)
                fork_op = ForkOperation(
                    source_repo=starred_repo,
                    target_name=target_name
                )
                self.fork_queue.append(fork_op)
                
                task = self._fork_with_semaphore(semaphore, fork_op)
                tasks.append(task)
                count += 1
        
        # Execute fork operations
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        results = {
            'attempted': len(self.fork_queue),
            'completed': len(self.completed_forks),
            'failed': len(self.failed_forks),
            'skipped': len([op for op in self.fork_queue if op.status == 'skipped'])
        }
        
        logger.info(f"Fork operation completed: {results}")
        return results
    
    async def sync_all_forks(self) -> Dict[str, int]:
        """Sync all forked repositories with their upstream sources."""
        synced = 0
        failed = 0
        skipped = 0
        
        async for repo in self.github.get_user_repositories(include_forks=True):
            if not repo['fork']:
                continue
            
            # Check if fork needs syncing (only sync if not updated in last 24 hours)
            if self._should_sync_fork(repo):
                success = await self.github.sync_fork(repo['full_name'])
                if success:
                    synced += 1
                else:
                    failed += 1
            else:
                skipped += 1
        
        results = {
            'synced': synced,
            'failed': failed,
            'skipped': skipped
        }
        
        logger.info(f"Sync operation completed: {results}")
        return results
    
    async def _fork_with_semaphore(self, semaphore: asyncio.Semaphore, fork_op: ForkOperation):
        """Fork a repository with semaphore control."""
        async with semaphore:
            try:
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming the API
                
                source_repo = fork_op.source_repo
                owner = source_repo['owner']['login']
                repo_name = source_repo['name']
                
                # Check if repo still exists and is accessible
                if await self._is_repo_accessible(owner, repo_name):
                    fork_data = await self.github.fork_repository(
                        owner=owner,
                        repo_name=repo_name,
                        new_name=fork_op.target_name,
                        private=self.settings.fork_as_private
                    )
                    
                    if fork_data:
                        fork_op.status = "completed"
                        fork_op.fork_data = fork_data
                        self.completed_forks.append(fork_op)
                        logger.info(f"Successfully forked {owner}/{repo_name} -> {fork_op.target_name}")
                    else:
                        fork_op.status = "failed"
                        fork_op.error_message = "Fork operation returned None"
                        self.failed_forks.append(fork_op)
                else:
                    fork_op.status = "skipped"
                    fork_op.error_message = "Repository not accessible"
                    
            except Exception as e:
                fork_op.status = "failed"
                fork_op.error_message = str(e)
                self.failed_forks.append(fork_op)
                logger.error(f"Failed to fork {fork_op.source_repo['full_name']}: {e}")
    
    async def _get_existing_repository_names(self) -> Set[str]:
        """Get set of existing repository names for the user."""
        existing_repos = set()
        
        async for repo in self.github.get_user_repositories():
            existing_repos.add(repo['name'].lower())
        
        return existing_repos
    
    def _should_fork_repo(self, repo: Dict, existing_repos: Set[str]) -> bool:
        """Determine if a repository should be forked."""
        # Skip if already exists
        target_name = self._generate_fork_name(repo).lower()
        if target_name in existing_repos:
            return False
        
        # Skip if it's our own repository
        if repo['owner']['login'].lower() == self.github.user.login.lower():
            return False
        
        # Skip if archived or disabled
        if repo.get('archived', False) or repo.get('disabled', False):
            return False
        
        # Skip based on exclusion patterns
        repo_name_lower = repo['name'].lower()
        description_lower = (repo.get('description') or '').lower()
        
        for pattern in self.settings.exclude_repos:
            if pattern.lower() in repo_name_lower or pattern.lower() in description_lower:
                return False
        
        # Skip based on language exclusions
        if repo.get('language') in self.settings.exclude_languages:
            return False
        
        return True
    
    def _generate_fork_name(self, repo: Dict) -> str:
        """Generate the target name for a forked repository."""
        base_name = repo['name']
        
        # Apply prefix and suffix
        if self.settings.fork_prefix:
            base_name = f"{self.settings.fork_prefix}{base_name}"
        
        if self.settings.fork_suffix:
            base_name = f"{base_name}{self.settings.fork_suffix}"
        
        return base_name
    
    def _get_fork_reason(self, repo: Dict, existing_repos: Set[str]) -> str:
        """Get human-readable reason for forking this repository."""
        if repo['stargazers_count'] > 1000:
            return f"Popular project ({repo['stargazers_count']} stars)"
        elif repo.get('language'):
            return f"{repo['language']} project"
        else:
            return "Starred repository"
    
    def _should_sync_fork(self, repo: Dict) -> bool:
        """Determine if a fork should be synced."""
        if not repo.get('parent'):
            return False
        
        # Parse the last update time
        try:
            updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
            now = datetime.now().replace(tzinfo=updated_at.tzinfo)
            
            # Only sync if not updated in the last 24 hours
            if now - updated_at > timedelta(hours=self.settings.sync_interval_hours):
                return True
        except (ValueError, TypeError):
            # If we can't parse the date, err on the side of syncing
            return True
        
        return False
    
    async def _is_repo_accessible(self, owner: str, repo_name: str) -> bool:
        """Check if a repository is still accessible."""
        try:
            # Simple check by trying to get repo info
            url = f"https://api.github.com/repos/{owner}/{repo_name}"
            async with self.github.session.get(url) as response:
                return response.status == 200
        except Exception:
            return False
    
    def get_fork_statistics(self) -> Dict:
        """Get statistics about fork operations."""
        total_operations = len(self.fork_queue)
        
        if total_operations == 0:
            return {
                'total_operations': 0,
                'success_rate': 0,
                'completion_rate': 0
            }
        
        completed = len(self.completed_forks)
        failed = len(self.failed_forks)
        
        return {
            'total_operations': total_operations,
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / total_operations) * 100 if total_operations > 0 else 0,
            'completion_rate': ((completed + failed) / total_operations) * 100 if total_operations > 0 else 0,
            'most_common_failures': self._get_common_failure_reasons()
        }
    
    def _get_common_failure_reasons(self) -> List[Dict]:
        """Get the most common failure reasons."""
        failure_counts = {}
        
        for fork_op in self.failed_forks:
            reason = fork_op.error_message or "Unknown error"
            failure_counts[reason] = failure_counts.get(reason, 0) + 1
        
        return [
            {'reason': reason, 'count': count}
            for reason, count in sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]
