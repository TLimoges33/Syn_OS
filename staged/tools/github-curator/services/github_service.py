"""Core services for GitHub API interactions."""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional, AsyncGenerator
from github import Github, Repository, UnknownObjectException
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)


class GitHubService:
    """Enhanced GitHub API service with async support and rate limiting."""
    
    def __init__(self, token: str, settings: Optional[Settings] = None):
        self.token = token
        self.settings = settings or Settings()
        self.github = Github(token)
        self.user = self.github.get_user()
        self.session = None
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = time.time()
        
        # Don't setup async session in __init__ to avoid event loop issues
        
    def _setup_async_session(self):
        """Setup async HTTP session with proper headers."""
        if self.session is None:
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-Repository-Curator/1.0'
            }
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers, 
                connector=connector, 
                timeout=timeout
            )
    
    async def close(self):
        """Close the async session."""
        if self.session:
            await self.session.close()
    
    async def check_rate_limit(self):
        """Check and handle GitHub API rate limiting."""
        rate_limit = self.github.get_rate_limit()
        self.rate_limit_remaining = rate_limit.core.remaining
        self.rate_limit_reset = rate_limit.core.reset.timestamp()
        
        if self.rate_limit_remaining < self.settings.github_rate_limit_buffer:
            sleep_time = max(0, self.rate_limit_reset - time.time() + 60)
            logger.warning(f"Rate limit low ({self.rate_limit_remaining}), sleeping for {sleep_time} seconds")
            await asyncio.sleep(sleep_time)
    
    async def ensure_session(self):
        """Ensure async session is initialized."""
        if self.session is None:
            self._setup_async_session()
    
    async def get_starred_repositories(self) -> AsyncGenerator[Dict, None]:
        """Async generator for starred repositories."""
        await self.ensure_session()
        page = 1
        per_page = 100
        
        while True:
            await self.check_rate_limit()
            
            url = f"https://api.github.com/user/starred"
            params = {'page': page, 'per_page': per_page}
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch starred repos: {response.status}")
                    break
                
                repos = await response.json()
                if not repos:
                    break
                
                for repo in repos:
                    yield self._normalize_repo_data(repo)
                
                page += 1
    
    async def get_user_repositories(self, include_forks: bool = True) -> AsyncGenerator[Dict, None]:
        """Async generator for user's repositories."""
        page = 1
        per_page = 100
        
        while True:
            await self.check_rate_limit()
            
            url = f"https://api.github.com/user/repos"
            params = {
                'page': page, 
                'per_page': per_page,
                'type': 'all',
                'sort': 'updated',
                'direction': 'desc'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch user repos: {response.status}")
                    break
                
                repos = await response.json()
                if not repos:
                    break
                
                for repo in repos:
                    if not include_forks and repo.get('fork', False):
                        continue
                    yield self._normalize_repo_data(repo)
                
                page += 1
    
    async def fork_repository(self, owner: str, repo_name: str, 
                            new_name: Optional[str] = None,
                            private: bool = True) -> Optional[Dict]:
        """Fork a repository asynchronously."""
        await self.check_rate_limit()
        
        fork_data = {
            'name': new_name or repo_name,
            'private': private
        }
        
        url = f"https://api.github.com/repos/{owner}/{repo_name}/forks"
        
        try:
            async with self.session.post(url, json=fork_data) as response:
                if response.status == 202:
                    fork_info = await response.json()
                    logger.info(f"Successfully forked {owner}/{repo_name}")
                    return self._normalize_repo_data(fork_info)
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to fork {owner}/{repo_name}: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Exception forking {owner}/{repo_name}: {e}")
            return None
    
    async def update_repository(self, repo_full_name: str, updates: Dict) -> bool:
        """Update repository metadata."""
        await self.check_rate_limit()
        
        url = f"https://api.github.com/repos/{repo_full_name}"
        
        try:
            async with self.session.patch(url, json=updates) as response:
                if response.status == 200:
                    logger.info(f"Updated repository {repo_full_name}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to update {repo_full_name}: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Exception updating {repo_full_name}: {e}")
            return False
    
    async def set_repository_topics(self, repo_full_name: str, topics: List[str]) -> bool:
        """Set repository topics."""
        await self.check_rate_limit()
        
        url = f"https://api.github.com/repos/{repo_full_name}/topics"
        data = {'names': topics}
        
        headers = {'Accept': 'application/vnd.github.mercy-preview+json'}
        
        try:
            async with self.session.put(url, json=data, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Set topics for {repo_full_name}: {topics}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to set topics for {repo_full_name}: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Exception setting topics for {repo_full_name}: {e}")
            return False
    
    async def sync_fork(self, repo_full_name: str) -> bool:
        """Sync a fork with its upstream repository."""
        await self.check_rate_limit()
        
        # First, get the default branch
        repo_url = f"https://api.github.com/repos/{repo_full_name}"
        async with self.session.get(repo_url) as response:
            if response.status != 200:
                return False
            repo_data = await response.json()
            default_branch = repo_data.get('default_branch', 'main')
        
        # Sync the fork
        sync_url = f"https://api.github.com/repos/{repo_full_name}/merge-upstream"
        sync_data = {'branch': default_branch}
        
        try:
            async with self.session.post(sync_url, json=sync_data) as response:
                if response.status in [200, 409]:  # 409 means already up-to-date
                    logger.info(f"Synced fork {repo_full_name}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to sync {repo_full_name}: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Exception syncing {repo_full_name}: {e}")
            return False
    
    async def get_repository_contents(self, repo_full_name: str, path: str = "") -> Optional[List[Dict]]:
        """Get repository contents."""
        await self.check_rate_limit()
        
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except Exception as e:
            logger.error(f"Exception getting contents for {repo_full_name}: {e}")
            return None
    
    async def search_repositories(self, query: str, language: Optional[str] = None,
                                topic: Optional[str] = None, 
                                sort: str = 'stars',
                                order: str = 'desc',
                                per_page: int = 30) -> List[Dict]:
        """Search GitHub repositories."""
        await self.check_rate_limit()
        
        # Build search query
        search_terms = [query]
        if language:
            search_terms.append(f"language:{language}")
        if topic:
            search_terms.append(f"topic:{topic}")
        
        search_query = " ".join(search_terms)
        
        url = "https://api.github.com/search/repositories"
        params = {
            'q': search_query,
            'sort': sort,
            'order': order,
            'per_page': per_page
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._normalize_repo_data(repo) for repo in data.get('items', [])]
                else:
                    logger.error(f"Search failed: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Exception searching repositories: {e}")
            return []
    
    def _normalize_repo_data(self, repo: Dict) -> Dict:
        """Normalize repository data from GitHub API."""
        return {
            'id': repo.get('id'),
            'name': repo.get('name'),
            'full_name': repo.get('full_name'),
            'description': repo.get('description', ''),
            'private': repo.get('private', False),
            'fork': repo.get('fork', False),
            'html_url': repo.get('html_url'),
            'clone_url': repo.get('clone_url'),
            'ssh_url': repo.get('ssh_url'),
            'language': repo.get('language'),
            'languages_url': repo.get('languages_url'),
            'stargazers_count': repo.get('stargazers_count', 0),
            'watchers_count': repo.get('watchers_count', 0),
            'forks_count': repo.get('forks_count', 0),
            'open_issues_count': repo.get('open_issues_count', 0),
            'default_branch': repo.get('default_branch', 'main'),
            'topics': repo.get('topics', []),
            'created_at': repo.get('created_at'),
            'updated_at': repo.get('updated_at'),
            'pushed_at': repo.get('pushed_at'),
            'size': repo.get('size', 0),
            'archived': repo.get('archived', False),
            'disabled': repo.get('disabled', False),
            'license': repo.get('license', {}).get('name') if repo.get('license') else None,
            'owner': {
                'login': repo.get('owner', {}).get('login'),
                'type': repo.get('owner', {}).get('type'),
                'html_url': repo.get('owner', {}).get('html_url')
            },
            'parent': repo.get('parent'),  # For forks
            'source': repo.get('source')   # For forks
        }
    
    def get_user_info(self) -> Dict:
        """Get authenticated user information."""
        user = self.github.get_user()
        return {
            'login': user.login,
            'name': user.name,
            'email': user.email,
            'public_repos': user.public_repos,
            'total_private_repos': user.total_private_repos,
            'followers': user.followers,
            'following': user.following,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
