#!/usr/bin/env python3
"""
Test script for GitHub Repository Curator with Syn_OS integration analysis.
This will analyze all your repositories and generate XML documentation.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.syn_os_analyzer import SynOSIntegrationAnalyzer
from services.github_service import GitHubService
from config.settings import Settings

async def run_syn_os_analysis():
    """Run the Syn_OS integration analysis."""
    print("🔍 Starting Syn_OS Integration Analysis...")
    print("=" * 60)
    
    # Load settings
    try:
        settings = Settings()
        if not settings.github_token or settings.github_token == 'your_github_personal_access_token_here':
            print("❌ GitHub token not configured!")
            print("   Please run: python configure_github.py")
            return False
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    # Initialize services
    github_service = GitHubService(settings.github_token)
    analyzer = SynOSIntegrationAnalyzer(github_service, settings)
    
    # Create output directory
    output_dir = Path("syn_os_analysis_results")
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {output_dir.absolute()}")
    print("🔄 Analyzing repositories...")
    
    try:
        # Run the analysis
        results = await analyzer.analyze_all_repositories(output_dir)
        
        # Display results
        print("\n✅ Analysis Complete!")
        print(f"📊 Total Repositories Analyzed: {results['total_analyzed']}")
        print(f"🔥 High Integration Potential: {results['high_integration_potential']}")
        print(f"🔶 Medium Integration Potential: {results['medium_integration_potential']}")
        print(f"🔷 Low Integration Potential: {results['low_integration_potential']}")
        print(f"📂 Categories Found: {len(results['categories_found'])}")
        
        # Show categories
        if results['categories_found']:
            print("\n🏷️ Syn_OS Integration Categories Found:")
            for category in sorted(results['categories_found']):
                print(f"   • {category}")
        
        print(f"\n📄 XML Documentation Generated:")
        print(f"   🎯 Master analysis: {output_dir}/syn_os_master_analysis.xml")
        print(f"   📋 Individual analyses: {output_dir}/*_syn_os_analysis.xml")
        
        # Show some example XML files
        xml_files = list(output_dir.glob("*_syn_os_analysis.xml"))
        if xml_files:
            print(f"\n📝 Sample analysis files:")
            for xml_file in xml_files[:5]:  # Show first 5
                print(f"   • {xml_file.name}")
            if len(xml_files) > 5:
                print(f"   ... and {len(xml_files) - 5} more files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def preview_repositories():
    """Preview repositories that will be analyzed."""
    print("👀 Repository Preview")
    print("=" * 30)
    
    try:
        settings = Settings()
        if not settings.github_token or settings.github_token == 'your_github_personal_access_token_here':
            print("❌ GitHub token not configured!")
            return False
            
        github_service = GitHubService(settings.github_token)
        
        print("🔍 Fetching your repositories...")
        repo_count = 0
        sample_repos = []
        
        async for repo in github_service.get_user_repositories():
            repo_count += 1
            if len(sample_repos) < 10:  # Keep first 10 for preview
                sample_repos.append(repo)
            
            if repo_count >= 100:  # Don't fetch all if you have many repos
                break
        
        print(f"\n📊 Found {repo_count}+ repositories")
        print("📋 Sample repositories:")
        
        for repo in sample_repos:
            language = repo.get('language', 'Unknown')
            stars = repo.get('stargazers_count', 0)
            description = repo.get('description', 'No description')[:50] + '...' if repo.get('description') else 'No description'
            print(f"   • {repo['name']} ({language}) ⭐{stars} - {description}")
        
        if repo_count > len(sample_repos):
            print(f"   ... and {repo_count - len(sample_repos)} more repositories")
        
        return True
        
    except Exception as e:
        print(f"❌ Error previewing repositories: {e}")
        return False

def main():
    """Main entry point."""
    print("🚀 Syn_OS Repository Analysis Test")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        # Just preview repositories
        success = asyncio.run(preview_repositories())
    else:
        # Run full analysis
        print("This will analyze ALL your repositories and generate XML documentation")
        print("for potential integration into the Syn_OS ecosystem.")
        print()
        
        choice = input("Continue? (y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("Cancelled.")
            return
        
        success = asyncio.run(run_syn_os_analysis())
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed. Please check your configuration.")
        sys.exit(1)

if __name__ == '__main__':
    main()
