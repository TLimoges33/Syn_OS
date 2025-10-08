#!/usr/bin/env python3
"""
Syn_OS Command Line Interface

A comprehensive CLI tool for managing the Syn_OS consciousness-aware infrastructure.
Provides commands for service management, consciousness monitoring, user management,
and system administration.
"""

import asyncio
import click
import json
import requests
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from tabulate import tabulate
import nats
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

console = Console()

# Configuration
DEFAULT_ORCHESTRATOR_URL = "http://localhost:8080"
DEFAULT_CONSCIOUSNESS_URL = "http://localhost:8081"
DEFAULT_SECURITY_TUTOR_URL = "http://localhost:8082"
DEFAULT_NATS_URL = "nats://localhost:4222"

class SynOSCLI:
    """Main CLI class for Syn_OS management"""
    
    def __init__(self, orchestrator_url: str = DEFAULT_ORCHESTRATOR_URL,
                 consciousness_url: str = DEFAULT_CONSCIOUSNESS_URL,
                 security_tutor_url: str = DEFAULT_SECURITY_TUTOR_URL,
                 nats_url: str = DEFAULT_NATS_URL):
        self.orchestrator_url = orchestrator_url
        self.consciousness_url = consciousness_url
        self.security_tutor_url = security_tutor_url
        self.nats_url = nats_url
        self.nats_client = None
    
    async def connect_nats(self):
        """Connect to NATS for real-time monitoring"""
        try:
            self.nats_client = await nats.connect(self.nats_url)
            return True
        except Exception as e:
            console.print(f"[red]Failed to connect to NATS: {e}[/red]")
            return False
    
    async def disconnect_nats(self):
        """Disconnect from NATS"""
        if self.nats_client:
            await self.nats_client.close()
            self.nats_client = None
    
    def make_request(self, url: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                console.print(f"[red]Unsupported HTTP method: {method}[/red]")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                console.print(f"[red]HTTP {response.status_code}: {response.text}[/red]")
                return None
                
        except requests.RequestException as e:
            console.print(f"[red]Request failed: {e}[/red]")
            return None


# Initialize CLI instance
cli_instance = SynOSCLI()

@click.group()
@click.option('--orchestrator-url', default=DEFAULT_ORCHESTRATOR_URL, help='Orchestrator service URL')
@click.option('--consciousness-url', default=DEFAULT_CONSCIOUSNESS_URL, help='Consciousness service URL')
@click.option('--security-tutor-url', default=DEFAULT_SECURITY_TUTOR_URL, help='Security tutor URL')
@click.option('--nats-url', default=DEFAULT_NATS_URL, help='NATS server URL')
def cli(orchestrator_url, consciousness_url, security_tutor_url, nats_url):
    """Syn_OS Command Line Interface - Manage your consciousness-aware infrastructure"""
    global cli_instance
    cli_instance = SynOSCLI(orchestrator_url, consciousness_url, security_tutor_url, nats_url)
    
    console.print(Panel.fit(
        "[bold blue]Syn_OS CLI[/bold blue]\n"
        "Consciousness-Aware Infrastructure Management",
        border_style="blue"
    ))

@cli.group()
def system():
    """System-wide operations and monitoring"""
    pass

@cli.group()
def services():
    """Service management operations"""
    pass

@cli.group()
def consciousness():
    """Consciousness system operations"""
    pass

@cli.group()
def users():
    """User management operations"""
    pass

# System Commands
@system.command()
def status():
    """Show overall system status"""
    console.print("[bold]Checking system status...[/bold]")
    
    services_status = {
        "Orchestrator": cli_instance.make_request(f"{cli_instance.orchestrator_url}/health"),
        "Consciousness": cli_instance.make_request(f"{cli_instance.consciousness_url}/health"),
        "Security Tutor": cli_instance.make_request(f"{cli_instance.security_tutor_url}/health")
    }
    
    table = Table(title="System Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    for service_name, status_data in services_status.items():
        if status_data:
            status = "🟢 Healthy" if status_data.get("status") == "healthy" else "🟡 Degraded"
            details = f"Uptime: {status_data.get('uptime', 'N/A')}"
        else:
            status = "🔴 Unhealthy"
            details = "Service unreachable"
        
        table.add_row(service_name, status, details)
    
    console.print(table)

@system.command()
def metrics():
    """Show system metrics"""
    console.print("[bold]Fetching system metrics...[/bold]")
    
    # Get orchestrator metrics
    orchestrator_metrics = cli_instance.make_request(f"{cli_instance.orchestrator_url}/api/v1/system/metrics")
    
    if orchestrator_metrics:
        console.print("\n[bold cyan]Orchestrator Metrics:[/bold cyan]")
        
        if "system" in orchestrator_metrics:
            system_metrics = orchestrator_metrics["system"]
            console.print(f"CPU Usage: {system_metrics.get('cpu_usage', 'N/A')}%")
            console.print(f"Memory Usage: {system_metrics.get('memory_usage', 'N/A')}%")
            console.print(f"Uptime: {system_metrics.get('uptime', 'N/A')}")
        
        if "services" in orchestrator_metrics:
            services = orchestrator_metrics["services"]
            console.print(f"Registered Services: {len(services)}")
            healthy_services = sum(1 for s in services if s.get('status') == 'healthy')
            console.print(f"Healthy Services: {healthy_services}/{len(services)}")
    
    # Get consciousness metrics
    consciousness_metrics = cli_instance.make_request(f"{cli_instance.consciousness_url}/metrics")
    
    if consciousness_metrics:
        console.print("\n[bold cyan]Consciousness Metrics:[/bold cyan]")
        
        if "consciousness" in consciousness_metrics:
            consciousness_data = consciousness_metrics["consciousness"]
            console.print(f"Attention Level: {consciousness_data.get('attention_level', 'N/A')}")
            console.print(f"Cognitive Load: {consciousness_data.get('cognitive_load', 'N/A')}")
            console.print(f"Active Processes: {consciousness_data.get('active_processes', 'N/A')}")

@system.command()
@click.option('--duration', default=30, help='Monitoring duration in seconds')
def monitor(duration):
    """Real-time system monitoring"""
    async def monitor_system():
        if not await cli_instance.connect_nats():
            console.print("[red]Cannot start monitoring without NATS connection[/red]")
            return
        
        console.print(f"[bold]Starting real-time monitoring for {duration} seconds...[/bold]")
        console.print("[dim]Press Ctrl+C to stop early[/dim]\n")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # Clear screen and show current status
                console.clear()
                console.print(f"[bold]Syn_OS Real-time Monitor[/bold] - {datetime.now().strftime('%H:%M:%S')}")
                console.print("=" * 50)
                
                # Get current metrics
                orchestrator_health = cli_instance.make_request(f"{cli_instance.orchestrator_url}/health")
                consciousness_health = cli_instance.make_request(f"{cli_instance.consciousness_url}/health")
                
                if orchestrator_health:
                    console.print(f"🟢 Orchestrator: {orchestrator_health.get('status', 'unknown')}")
                else:
                    console.print("🔴 Orchestrator: unreachable")
                
                if consciousness_health:
                    console.print(f"🟢 Consciousness: {consciousness_health.get('status', 'unknown')}")
                    if consciousness_health.get('consciousness_state'):
                        state = consciousness_health['consciousness_state']
                        console.print(f"   Attention: {state.get('attention_focus', 'N/A')}")
                        console.print(f"   Cognitive Load: {state.get('cognitive_load', 'N/A')}")
                else:
                    console.print("🔴 Consciousness: unreachable")
                
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        finally:
            await cli_instance.disconnect_nats()
    
    asyncio.run(monitor_system())

# Service Commands
@services.command()
def list():
    """List all registered services"""
    console.print("[bold]Fetching registered services...[/bold]")
    
    services_data = cli_instance.make_request(f"{cli_instance.orchestrator_url}/api/v1/services")
    
    if services_data:
        table = Table(title="Registered Services")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Endpoint", style="blue")
        table.add_column("Last Seen", style="magenta")
        
        for service in services_data:
            status_icon = "🟢" if service.get('status') == 'healthy' else "🔴"
            table.add_row(
                service.get('name', 'N/A'),
                service.get('type', 'N/A'),
                f"{status_icon} {service.get('status', 'unknown')}",
                service.get('endpoint', 'N/A'),
                service.get('last_seen', 'N/A')
            )
        
        console.print(table)
    else:
        console.print("[red]Failed to fetch services[/red]")

@services.command()
@click.argument('service_name')
def info(service_name):
    """Get detailed information about a service"""
    console.print(f"[bold]Getting information for service: {service_name}[/bold]")
    
    service_data = cli_instance.make_request(f"{cli_instance.orchestrator_url}/api/v1/services/{service_name}")
    
    if service_data:
        console.print(f"\n[cyan]Service: {service_data.get('name', 'N/A')}[/cyan]")
        console.print(f"Type: {service_data.get('type', 'N/A')}")
        console.print(f"Status: {service_data.get('status', 'N/A')}")
        console.print(f"Endpoint: {service_data.get('endpoint', 'N/A')}")
        console.print(f"Version: {service_data.get('version', 'N/A')}")
        console.print(f"Last Seen: {service_data.get('last_seen', 'N/A')}")
        
        if service_data.get('metadata'):
            console.print("\n[yellow]Metadata:[/yellow]")
            for key, value in service_data['metadata'].items():
                console.print(f"  {key}: {value}")
    else:
        console.print(f"[red]Service '{service_name}' not found[/red]")

@services.command()
@click.argument('service_name')
@click.argument('action', type=click.Choice(['start', 'stop', 'restart']))
def control(service_name, action):
    """Control service lifecycle"""
    console.print(f"[bold]Sending {action} command to {service_name}...[/bold]")
    
    result = cli_instance.make_request(
        f"{cli_instance.orchestrator_url}/api/v1/services/{service_name}/{action}",
        method="POST"
    )
    
    if result:
        console.print(f"[green]Successfully sent {action} command to {service_name}[/green]")
    else:
        console.print(f"[red]Failed to {action} service {service_name}[/red]")

# Consciousness Commands
@consciousness.command()
def status():
    """Show consciousness system status"""
    console.print("[bold]Checking consciousness system status...[/bold]")
    
    health_data = cli_instance.make_request(f"{cli_instance.consciousness_url}/health")
    
    if health_data:
        console.print(f"\n[cyan]Consciousness System Status[/cyan]")
        console.print(f"Status: {health_data.get('status', 'unknown')}")
        console.print(f"Mode: {health_data.get('mode', 'unknown')}")
        console.print(f"Consciousness Core: {'✓' if health_data.get('consciousness_core') else '✗'}")
        console.print(f"Event Bus: {'✓' if health_data.get('event_bus') else '✗'}")
        console.print(f"NATS Bridge: {'✓' if health_data.get('nats_bridge') else '✗'}")
        
        if health_data.get('consciousness_state'):
            state = health_data['consciousness_state']
            console.print(f"\n[yellow]Current State:[/yellow]")
            console.print(f"Attention Focus: {state.get('attention_focus', 'N/A')}")
            console.print(f"Emotional State: {state.get('emotional_state', 'N/A')}")
            console.print(f"Cognitive Load: {state.get('cognitive_load', 'N/A')}")
            console.print(f"Learning Mode: {state.get('learning_mode', 'N/A')}")
    else:
        console.print("[red]Consciousness system is not responding[/red]")

@consciousness.command()
def insights():
    """Show consciousness insights and analytics"""
    console.print("[bold]Fetching consciousness insights...[/bold]")
    
    metrics_data = cli_instance.make_request(f"{cli_instance.consciousness_url}/metrics")
    
    if metrics_data:
        if "consciousness" in metrics_data:
            consciousness_metrics = metrics_data["consciousness"]
            
            table = Table(title="Consciousness Insights")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Description", style="yellow")
            
            metrics_info = {
                "attention_level": ("Attention Level", "Current focus and alertness"),
                "cognitive_load": ("Cognitive Load", "Mental processing demand"),
                "learning_momentum": ("Learning Momentum", "Rate of knowledge acquisition"),
                "emotional_state": ("Emotional State", "Current emotional context"),
                "active_processes": ("Active Processes", "Number of concurrent thoughts")
            }
            
            for key, (name, description) in metrics_info.items():
                value = consciousness_metrics.get(key, 'N/A')
                if isinstance(value, float):
                    value = f"{value:.2f}"
                table.add_row(name, str(value), description)
            
            console.print(table)
        
        if "events" in metrics_data:
            event_metrics = metrics_data["events"]
            console.print(f"\n[cyan]Event Processing:[/cyan]")
            console.print(f"Total Processed: {event_metrics.get('total_processed', 'N/A')}")
            console.print(f"Pending: {event_metrics.get('pending', 'N/A')}")
            console.print(f"Processing Rate: {event_metrics.get('processing_rate', 'N/A')}/sec")
    else:
        console.print("[red]Failed to fetch consciousness insights[/red]")

# User Commands
@users.command()
def list():
    """List all users in the security tutor"""
    console.print("[bold]Fetching user list...[/bold]")
    
    # This would typically come from a user management API
    console.print("[yellow]User management API not yet implemented[/yellow]")
    console.print("This feature will be available in the next version.")

@users.command()
@click.argument('user_id')
def profile(user_id):
    """Show user profile and learning progress"""
    console.print(f"[bold]Fetching profile for user: {user_id}[/bold]")
    
    user_data = cli_instance.make_request(f"{cli_instance.security_tutor_url}/api/users/{user_id}")
    
    if user_data:
        console.print(f"\n[cyan]User Profile: {user_data.get('name', 'N/A')}[/cyan]")
        console.print(f"User ID: {user_data.get('user_id', 'N/A')}")
        console.print(f"Skill Level: {user_data.get('skill_level', 'N/A')}")
        console.print(f"Learning Style: {user_data.get('learning_style', 'N/A')}")
        console.print(f"Total Score: {user_data.get('total_score', 'N/A')}")
        console.print(f"Current Streak: {user_data.get('current_streak', 'N/A')}")
        console.print(f"Completed Modules: {len(user_data.get('completed_modules', []))}")
        console.print(f"Last Active: {user_data.get('last_active', 'N/A')}")
        
        if user_data.get('consciousness_insights'):
            console.print(f"\n[yellow]Consciousness Insights:[/yellow]")
            for key, value in user_data['consciousness_insights'].items():
                console.print(f"  {key.replace('_', ' ').title()}: {value}")
    else:
        console.print(f"[red]User '{user_id}' not found[/red]")

@users.command()
@click.argument('user_id')
def recommendations(user_id):
    """Get personalized learning recommendations for a user"""
    console.print(f"[bold]Fetching recommendations for user: {user_id}[/bold]")
    
    recommendations_data = cli_instance.make_request(
        f"{cli_instance.security_tutor_url}/api/users/{user_id}/recommendations"
    )
    
    if recommendations_data and recommendations_data.get('recommendations'):
        recommendations = recommendations_data['recommendations']
        
        console.print(f"\n[cyan]Personalized Recommendations[/cyan]")
        console.print(f"Optimal Session Length: {recommendations.get('optimal_session_length', 'N/A')} minutes")
        console.print(f"Best Learning Time: {recommendations.get('best_time_to_learn', 'N/A')}")
        console.print(f"Learning Approach: {recommendations.get('learning_approach', 'N/A')}")
        
        if recommendations.get('suggested_modules'):
            console.print(f"\n[yellow]Suggested Modules:[/yellow]")
            for module in recommendations['suggested_modules']:
                console.print(f"• {module.get('title', 'N/A')}")
                console.print(f"  Reason: {module.get('reason', 'N/A')}")
    else:
        console.print(f"[red]No recommendations available for user '{user_id}'[/red]")

# Utility Commands
@cli.command()
def version():
    """Show version information"""
    console.print(Panel.fit(
        "[bold]Syn_OS CLI v1.0.0[/bold]\n"
        "Consciousness-Aware Infrastructure Management\n"
        "Built with ❤️ for the future of AI",
        border_style="green"
    ))

@cli.command()
def config():
    """Show current configuration"""
    console.print("[bold]Current Configuration:[/bold]")
    console.print(f"Orchestrator URL: {cli_instance.orchestrator_url}")
    console.print(f"Consciousness URL: {cli_instance.consciousness_url}")
    console.print(f"Security Tutor URL: {cli_instance.security_tutor_url}")
    console.print(f"NATS URL: {cli_instance.nats_url}")

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)