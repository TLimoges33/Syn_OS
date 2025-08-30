#!/usr/bin/env python3
"""Quick GitHub token update script."""

import sys
from pathlib import Path

def update_token():
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    print("🔑 GitHub Token Update")
    print("Please paste your complete GitHub Personal Access Token:")
    print("(It should start with 'ghp_' or 'github_pat_' and be quite long)")
    print()
    
    token = input("Token: ").strip()
    
    if not token:
        print("❌ No token provided!")
        return False
    
    if len(token) < 20:
        print("⚠️ Token seems too short. Are you sure it's complete?")
        
    # Read current .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update the token line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('GITHUB_TOKEN='):
            lines[i] = f'GITHUB_TOKEN={token}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'GITHUB_TOKEN={token}\n')
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Token updated in {env_file.absolute()}")
    return True

if __name__ == '__main__':
    if update_token():
        print("🚀 Now you can test the connection again!")
    else:
        sys.exit(1)
