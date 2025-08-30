#!/usr/bin/env python3
"""
GitHub Token Configuration Helper
Helps set up GitHub Personal Access Token for the Repository Curator.
"""

import os
import sys
from pathlib import Path

def main():
    print("🔑 GitHub Repository Curator - Token Configuration")
    print("=" * 60)
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found. Please run 'cp .env.example .env' first.")
        sys.exit(1)
    
    print("\n📋 To use the GitHub Repository Curator, you need a Personal Access Token.")
    print("   Follow these steps to create one:")
    print()
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token' → 'Generate new token (classic)'")
    print("3. Give it a descriptive name like 'Syn_OS Repository Curator'")
    print("4. Select the following scopes:")
    print("   ✅ repo (Full control of private repositories)")
    print("   ✅ read:user (Read user profile data)")
    print("   ✅ user:email (Access user email addresses)")
    print("   ✅ read:org (Read org and team membership)")
    print("5. Click 'Generate token'")
    print("6. Copy the token (it starts with 'ghp_' or 'github_pat_')")
    print()
    
    token = input("📝 Enter your GitHub Personal Access Token: ").strip()
    
    if not token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)
    
    if not (token.startswith('ghp_') or token.startswith('github_pat_')):
        print("⚠️  Warning: Token doesn't look like a GitHub token. Continuing anyway...")
    
    username = input("👤 Enter your GitHub username: ").strip()
    
    if not username:
        print("❌ No username provided. Exiting.")
        sys.exit(1)
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace token and username
    content = content.replace('your_github_personal_access_token_here', token)
    content = content.replace('your_github_username', username)
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Configuration saved to {env_file.absolute()}")
    print("🚀 You can now run the Repository Curator commands!")
    print()
    print("Next steps:")
    print("  python main.py fork-starred --dry-run    # Preview what will be forked")
    print("  python main.py syn-os-analyze           # Analyze for Syn_OS integration")
    print("  python main.py dashboard                # Start web interface")

if __name__ == '__main__':
    main()
