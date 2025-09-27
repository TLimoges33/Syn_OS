#!/usr/bin/env python3
"""
GitHub Repository Curator - Main Entry Point
Manages your GitHub ecosystem by forking starred repos and curating your library.
"""

import asyncio
import click
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.curator import RepositoryCurator
from core.fork_manager import ForkManager
from core.library_generator import LibraryGenerator
from core.syn_os_analyzer import SynOSIntegrationAnalyzer
from web.dashboard import DashboardApp
from services.github_service import GitHubService
from config.settings import Settings


@click.group()
@click.pass_context
def cli(ctx):
    """GitHub Repository Curator - Your personal development library manager."""
    ctx.ensure_object(dict)
    settings = Settings()
    ctx.obj['settings'] = settings
    ctx.obj['github'] = GitHubService(settings.github_token)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Show what would be forked without actually doing it')
@click.option('--limit', type=int, default=None, help='Limit number of repos to fork')
@click.pass_context
def fork_starred(ctx, dry_run, limit):
    """Fork all your starred repositories as private repos."""
    click.echo("🌟 Starting starred repository fork process...")
    
    fork_manager = ForkManager(ctx.obj['github'], ctx.obj['settings'])
    
    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be forked:")
        asyncio.run(fork_manager.preview_fork_operations(limit))
    else:
        asyncio.run(fork_manager.fork_all_starred(limit))
    
    click.echo("✅ Fork process completed!")


@cli.command()
@click.option('--update-existing', is_flag=True, help='Update existing repository metadata')
@click.option('--categories', multiple=True, help='Only curate specific categories')
@click.pass_context
def curate_repos(ctx, update_existing, categories):
    """Curate all your repositories into an organized library."""
    click.echo("📚 Starting repository curation process...")
    
    curator = RepositoryCurator(ctx.obj['github'], ctx.obj['settings'])
    
    filters = {
        'update_existing': update_existing,
        'categories': list(categories) if categories else None
    }
    
    asyncio.run(curator.curate_all_repositories(filters))
    
    click.echo("✅ Curation process completed!")


@cli.command()
@click.option('--format', type=click.Choice(['markdown', 'html', 'json']), default='markdown')
@click.option('--output-dir', type=click.Path(), default='./library_docs')
@click.pass_context
def generate_docs(ctx, format, output_dir):
    """Generate documentation for your curated library."""
    click.echo(f"📋 Generating library documentation in {format} format...")
    
    generator = LibraryGenerator(ctx.obj['github'], ctx.obj['settings'])
    
    output_path = Path(output_dir)
    asyncio.run(generator.generate_documentation(format, output_path))
    
    click.echo(f"✅ Documentation generated in {output_path}")


@cli.command()
@click.option('--host', default='localhost', help='Host to bind the dashboard')
@click.option('--port', type=int, default=8080, help='Port to bind the dashboard')
@click.option('--debug', is_flag=True, help='Run in debug mode')
@click.pass_context
def dashboard(ctx, host, port, debug):
    """Start the web dashboard for managing your library."""
    click.echo(f"🚀 Starting dashboard at http://{host}:{port}")
    
    app = DashboardApp(ctx.obj['github'], ctx.obj['settings'])
    app.run(host=host, port=port, debug=debug)


@cli.command()
@click.pass_context
def sync_forks(ctx):
    """Sync all forked repositories with their upstream sources."""
    click.echo("🔄 Syncing forked repositories...")
    
    fork_manager = ForkManager(ctx.obj['github'], ctx.obj['settings'])
    asyncio.run(fork_manager.sync_all_forks())
    
    click.echo("✅ Sync process completed!")


@cli.command()
@click.argument('query')
@click.option('--category', help='Filter by category')
@click.option('--language', help='Filter by programming language')
@click.option('--limit', type=int, default=10, help='Limit number of results')
@click.pass_context
def search(ctx, query, category, language, limit):
    """Search through your curated repository library."""
    curator = RepositoryCurator(ctx.obj['github'], ctx.obj['settings'])
    
    filters = {
        'category': category,
        'language': language,
        'limit': limit
    }
    
    results = asyncio.run(curator.search_repositories(query, filters))
    
    click.echo(f"🔍 Found {len(results)} repositories matching '{query}':")
    for repo in results:
        click.echo(f"  📁 {repo['full_name']} - {repo['description'][:100]}...")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show statistics about your repository library."""
    curator = RepositoryCurator(ctx.obj['github'], ctx.obj['settings'])
    stats = asyncio.run(curator.get_library_stats())
    
    click.echo("📊 Repository Library Statistics:")
    click.echo(f"  Total Repositories: {stats['total_repos']}")
    click.echo(f"  Forked from Stars: {stats['forked_stars']}")
    click.echo(f"  Original Repositories: {stats['original_repos']}")
    click.echo(f"  Programming Languages: {len(stats['languages'])}")
    click.echo(f"  Categories: {len(stats['categories'])}")
    
    click.echo("\n🏷️ Top Languages:")
    for lang, count in stats['top_languages'][:5]:
        click.echo(f"  {lang}: {count} repos")


@cli.command()
@click.option('--output-dir', '-o', default='syn_os_analysis', 
              help='Output directory for XML analysis files')
@click.pass_context
def syn_os_analyze(ctx, output_dir):
    """Analyze all repositories for Syn_OS integration potential and generate XML documentation."""
    analyzer = SynOSIntegrationAnalyzer(ctx.obj['github'], ctx.obj['settings'])
    output_path = Path(output_dir)
    
    click.echo(f"🔍 Analyzing repositories for Syn_OS integration...")
    click.echo(f"📁 Output directory: {output_path.absolute()}")
    
    results = asyncio.run(analyzer.analyze_all_repositories(output_path))
    
    click.echo(f"\n✅ Analysis Complete!")
    click.echo(f"  📊 Total Repositories Analyzed: {results['total_analyzed']}")
    click.echo(f"  🔥 High Integration Potential: {results['high_integration_potential']}")
    click.echo(f"  🔶 Medium Integration Potential: {results['medium_integration_potential']}")
    click.echo(f"  🔷 Low Integration Potential: {results['low_integration_potential']}")
    click.echo(f"  📂 Categories Found: {len(results['categories_found'])}")
    
    click.echo(f"\n📄 XML files generated in: {output_path.absolute()}")
    click.echo(f"  🎯 Master analysis: syn_os_master_analysis.xml")
    click.echo(f"  📋 Individual repo analyses: *_syn_os_analysis.xml")


if __name__ == '__main__':
    cli()
