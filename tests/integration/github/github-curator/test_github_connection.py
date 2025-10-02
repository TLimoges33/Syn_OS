#!/usr/bin/env python3
"""
Simple GitHub API test to verify token and connection.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from github import Github
from config.settings import Settings

def test_github_connection():
    """Test basic GitHub API connection."""
    print("🔍 Testing GitHub API Connection...")
    print("=" * 40)
    
    try:
        # Load settings
        settings = Settings()
        if not settings.github_token or settings.github_token == 'your_github_personal_access_token_here':
            print("❌ GitHub token not configured!")
            print("   Please run: python configure_github.py")
            return False
        
        print(f"🔑 Token found: {settings.github_token[:10]}...")
        
        # Test GitHub connection
        github = Github(settings.github_token)
        user = github.get_user()
        
        print(f"✅ Connected as: {user.login}")
        print(f"📊 Public repos: {user.public_repos}")
        print(f"⭐ Total stars given: {user.following}")
        
        # Test getting repositories
        print("\n🔍 Fetching first 5 repositories:")
        repos = list(user.get_repos()[:5])
        
        for repo in repos:
            print(f"   • {repo.name} ({repo.language or 'Unknown'}) ⭐{repo.stargazers_count}")
        
        # Test getting starred repositories
        print("\n⭐ Fetching first 5 starred repositories:")
        starred = list(user.get_starred()[:5])
        
        for repo in starred:
            print(f"   • {repo.full_name} ({repo.language or 'Unknown'}) ⭐{repo.stargazers_count}")
        
        print(f"\n✅ GitHub API connection successful!")
        rate_limit = github.get_rate_limit()
        print(f"   Rate limit remaining: {rate_limit.core.remaining}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing GitHub connection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_github_connection()
    if not success:
        sys.exit(1)
    print("\n🚀 Ready to proceed with repository analysis!")
