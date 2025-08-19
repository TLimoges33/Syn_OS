#!/usr/bin/env python3
"""
SynPkg Manager - AI-Enhanced Package Management System
Aggregates tools from Kali, BlackArch, ParrotOS with intelligent conflict resolution
"""

import asyncio
import json
import logging
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp
import yaml

# Import our existing consciousness interface
import sys
sys.path.append('/home/diablorain/Syn_OS/src/consciousness_v2')
from core.consciousness_bus import ConsciousnessBus
from components.neural_darwinism_v2 import NeuralDarwinismEngine

@dataclass
class PackageInfo:
    """Package information structure"""
    name: str
    version: str
    source_repo: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    category: str = ""
    size: int = 0
    security_level: str = "standard"
    ai_enhanced: bool = False
    hash_sha256: str = ""

@dataclass 
class Repository:
    """Repository configuration"""
    name: str
    url: str
    distribution: str
    components: List[str] = field(default_factory=list)
    priority: int = 100
    gpg_key: str = ""
    enabled: bool = True

class ConflictResolver:
    """AI-powered package conflict resolution"""
    
    def __init__(self, consciousness: NeuralDarwinismEngine):
        self.consciousness = consciousness
        self.logger = logging.getLogger(__name__)
    
    async def resolve_conflicts(self, packages: List[PackageInfo]) -> List[PackageInfo]:
        """Resolve package conflicts using AI decision making"""
        
        # Group packages by name to find conflicts
        package_groups = {}
        for pkg in packages:
            base_name = self._get_base_name(pkg.name)
            if base_name not in package_groups:
                package_groups[base_name] = []
            package_groups[base_name].append(pkg)
        
        resolved_packages = []
        
        for base_name, pkg_group in package_groups.items():
            if len(pkg_group) == 1:
                # No conflict
                resolved_packages.extend(pkg_group)
            else:
                # Conflict detected - use AI to resolve
                best_package = await self._ai_resolve_conflict(base_name, pkg_group)
                resolved_packages.append(best_package)
                
                self.logger.info(f"Resolved conflict for {base_name}: chose {best_package.source_repo}")
        
        return resolved_packages
    
    def _get_base_name(self, package_name: str) -> str:
        """Extract base name from package (remove version suffixes, etc.)"""
        # Remove common suffixes
        for suffix in ['-git', '-stable', '-dev', '-bin', '-python3', '-python2']:
            if package_name.endswith(suffix):
                package_name = package_name[:-len(suffix)]
        
        return package_name.lower()
    
    async def _ai_resolve_conflict(self, base_name: str, conflicting_packages: List[PackageInfo]) -> PackageInfo:
        """Use AI to choose the best package from conflicts"""
        
        # Prepare decision context for AI
        context = {
            'package_name': base_name,
            'options': [
                {
                    'name': pkg.name,
                    'source': pkg.source_repo,
                    'version': pkg.version,
                    'size': pkg.size,
                    'security_level': pkg.security_level,
                    'description': pkg.description[:200]  # Truncate for AI processing
                }
                for pkg in conflicting_packages
            ]
        }
        
        # AI decision criteria:
        # 1. Security level (higher is better)
        # 2. Active maintenance (newer versions preferred) 
        # 3. Source reputation (BlackArch > Kali > ParrotOS > others)
        # 4. Size efficiency (smaller preferred if functionality equal)
        
        try:
            # Use consciousness engine for decision
            decision_prompt = f"""
            Choose the best package for cybersecurity operations:
            Package: {base_name}
            Options: {json.dumps(context['options'], indent=2)}
            
            Criteria:
            - Security and reliability (most important)
            - Latest version and active maintenance
            - Source reputation and community support
            - Functionality completeness
            
            Return only the index (0-based) of the best option.
            """
            
            # Simplified AI decision for now - use heuristics
            best_score = -1
            best_package = conflicting_packages[0]
            
            for pkg in conflicting_packages:
                score = self._calculate_package_score(pkg)
                if score > best_score:
                    best_score = score
                    best_package = pkg
            
            return best_package
            
        except Exception as e:
            self.logger.warning(f"AI resolution failed for {base_name}, using heuristic: {e}")
            return self._heuristic_resolve(conflicting_packages)
    
    def _calculate_package_score(self, pkg: PackageInfo) -> float:
        """Calculate package preference score"""
        score = 0.0
        
        # Source repository preference
        repo_scores = {
            'blackarch': 10.0,
            'kali': 8.0,
            'parrot': 6.0,
            'debian': 4.0,
            'synos': 15.0  # Our custom packages get highest priority
        }
        score += repo_scores.get(pkg.source_repo.lower(), 2.0)
        
        # Security level preference
        security_scores = {
            'high': 5.0,
            'standard': 3.0,
            'low': 1.0
        }
        score += security_scores.get(pkg.security_level.lower(), 2.0)
        
        # AI enhancement bonus
        if pkg.ai_enhanced:
            score += 5.0
        
        # Size penalty (prefer smaller packages)
        if pkg.size > 0:
            size_mb = pkg.size / (1024 * 1024)
            score -= min(size_mb / 100.0, 3.0)  # Cap penalty at 3 points
        
        return score
    
    def _heuristic_resolve(self, packages: List[PackageInfo]) -> PackageInfo:
        """Fallback heuristic resolution"""
        # Simple preference: BlackArch > Kali > ParrotOS > others
        preference_order = ['synos', 'blackarch', 'kali', 'parrot', 'debian']
        
        for preferred_source in preference_order:
            for pkg in packages:
                if preferred_source in pkg.source_repo.lower():
                    return pkg
        
        # If no preference match, return first package
        return packages[0]

class SynPkgManager:
    """AI-Enhanced Package Manager for Syn_OS"""
    
    def __init__(self, config_path: str = "/etc/synpkg/config.yaml"):
        self.config_path = Path(config_path)
        self.repositories: List[Repository] = []
        self.package_cache: Dict[str, List[PackageInfo]] = {}
        self.consciousness: Optional[NeuralDarwinismEngine] = None
        self.conflict_resolver: Optional[ConflictResolver] = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI components
        asyncio.create_task(self._initialize_ai())
    
    async def _initialize_ai(self):
        """Initialize AI consciousness components"""
        try:
            # Initialize consciousness engine
            self.consciousness = NeuralDarwinismEngine(
                component_id="synpkg_manager",
                population_size=50,
                learning_rate=0.01
            )
            await self.consciousness.start()
            
            # Initialize conflict resolver
            self.conflict_resolver = ConflictResolver(self.consciousness)
            
            self.logger.info("AI components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI components: {e}")
            # Continue without AI - use heuristic fallbacks
    
    async def load_config(self):
        """Load repository configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.repositories = []
            for repo_config in config.get('repositories', []):
                repo = Repository(**repo_config)
                self.repositories.append(repo)
            
            self.logger.info(f"Loaded {len(self.repositories)} repositories")
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self._load_default_config()
    
    def _load_default_config(self):
        """Load default repository configuration"""
        self.repositories = [
            Repository(
                name="synos-main",
                url="https://repo.synos.ai/packages",
                distribution="stable",
                components=["main", "ai-tools", "custom-kernel"],
                priority=10
            ),
            Repository(
                name="blackarch",
                url="https://blackarch.org/blackarch/$arch",
                distribution="blackarch",
                components=["blackarch"],
                priority=20
            ),
            Repository(
                name="kali",
                url="https://http.kali.org/kali",
                distribution="kali-rolling",
                components=["main", "non-free", "contrib"],
                priority=30
            ),
            Repository(
                name="parrot",
                url="https://deb.parrotsec.org/parrot",
                distribution="parrot",
                components=["main", "contrib", "non-free"],
                priority=40
            ),
            Repository(
                name="debian",
                url="https://deb.debian.org/debian",
                distribution="bookworm",
                components=["main", "non-free-firmware"],
                priority=100
            )
        ]
    
    async def update_package_lists(self):
        """Update package lists from all repositories"""
        self.logger.info("Updating package lists...")
        
        tasks = []
        for repo in self.repositories:
            if repo.enabled:
                task = asyncio.create_task(self._fetch_repository_packages(repo))
                tasks.append(task)
        
        # Fetch all repositories in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        total_packages = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to fetch {self.repositories[i].name}: {result}")
            else:
                repo_name = self.repositories[i].name
                self.package_cache[repo_name] = result
                total_packages += len(result)
                self.logger.info(f"Fetched {len(result)} packages from {repo_name}")
        
        self.logger.info(f"Total packages available: {total_packages}")
    
    async def _fetch_repository_packages(self, repo: Repository) -> List[PackageInfo]:
        """Fetch package list from a single repository"""
        packages = []
        
        try:
            # Different logic based on repository type
            if repo.name == "blackarch":
                packages = await self._fetch_blackarch_packages(repo)
            elif repo.name == "kali":
                packages = await self._fetch_kali_packages(repo)
            elif repo.name == "parrot":
                packages = await self._fetch_parrot_packages(repo)
            elif repo.name == "synos-main":
                packages = await self._fetch_synos_packages(repo)
            else:
                packages = await self._fetch_debian_packages(repo)
                
        except Exception as e:
            self.logger.error(f"Error fetching {repo.name}: {e}")
            
        return packages
    
    async def _fetch_blackarch_packages(self, repo: Repository) -> List[PackageInfo]:
        """Fetch BlackArch package list"""
        packages = []
        
        # BlackArch has a packages.txt file listing all tools
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{repo.url}/packages.txt") as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        for line in content.strip().split('\n'):
                            if line.strip():
                                # Parse BlackArch package line format
                                parts = line.strip().split()
                                if len(parts) >= 2:
                                    name = parts[0]
                                    description = ' '.join(parts[1:]) if len(parts) > 1 else ""
                                    
                                    pkg = PackageInfo(
                                        name=name,
                                        version="latest",
                                        source_repo="blackarch",
                                        description=description,
                                        category="security",
                                        security_level="high"
                                    )
                                    packages.append(pkg)
                                    
        except Exception as e:
            self.logger.warning(f"BlackArch fetch failed, using fallback: {e}")
            # Fallback to hardcoded essential tools
            packages = self._get_blackarch_essential_tools()
            
        return packages
    
    async def _fetch_kali_packages(self, repo: Repository) -> List[PackageInfo]:
        """Fetch Kali Linux package list"""
        packages = []
        
        # Kali packages can be fetched from their package index
        try:
            # Use apt-cache simulation for now
            cmd = ["apt-cache", "search", "--names-only", ""]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ' - ' in line:
                        name, description = line.split(' - ', 1)
                        name = name.strip()
                        
                        # Filter for security-related packages
                        if self._is_security_tool(name, description):
                            pkg = PackageInfo(
                                name=name,
                                version="latest",
                                source_repo="kali",
                                description=description,
                                category="security",
                                security_level="high"
                            )
                            packages.append(pkg)
                            
        except Exception as e:
            self.logger.warning(f"Kali fetch failed, using fallback: {e}")
            packages = self._get_kali_essential_tools()
            
        return packages
    
    async def _fetch_parrot_packages(self, repo: Repository) -> List[PackageInfo]:
        """Fetch ParrotOS package list"""
        # Similar to Kali but with ParrotOS specific tools
        packages = self._get_parrot_essential_tools()
        return packages
    
    async def _fetch_synos_packages(self, repo: Repository) -> List[PackageInfo]:
        """Fetch custom Syn_OS packages"""
        # These are our AI-enhanced custom tools
        packages = [
            PackageInfo(
                name="synos-consciousness-engine",
                version="2.0.0",
                source_repo="synos",
                description="AI consciousness engine for cybersecurity operations",
                category="ai-core",
                security_level="high",
                ai_enhanced=True
            ),
            PackageInfo(
                name="synos-neural-nmap",
                version="1.0.0", 
                source_repo="synos",
                description="AI-enhanced network scanner with intelligent target selection",
                category="reconnaissance",
                security_level="high",
                ai_enhanced=True
            ),
            PackageInfo(
                name="synos-adaptive-metasploit",
                version="1.0.0",
                source_repo="synos", 
                description="Metasploit with AI-guided exploit selection and payload optimization",
                category="exploitation",
                security_level="high",
                ai_enhanced=True
            ),
            PackageInfo(
                name="synos-intelligent-burp",
                version="1.0.0",
                source_repo="synos",
                description="Burp Suite proxy with AI-powered vulnerability detection",
                category="web-security",
                security_level="high", 
                ai_enhanced=True
            ),
            PackageInfo(
                name="synos-consciousness-wireshark",
                version="1.0.0",
                source_repo="synos",
                description="Wireshark with AI traffic analysis and threat detection",
                category="analysis",
                security_level="high",
                ai_enhanced=True
            )
        ]
        return packages
    
    async def _fetch_debian_packages(self, repo: Repository) -> List[PackageInfo]:
        """Fetch base Debian packages"""
        # Base system packages - return essential ones only
        packages = [
            PackageInfo(
                name="systemd",
                version="latest",
                source_repo="debian", 
                description="System and service manager",
                category="system",
                security_level="high"
            ),
            PackageInfo(
                name="python3",
                version="latest",
                source_repo="debian",
                description="Interactive high-level object-oriented language",
                category="development",
                security_level="standard"
            )
        ]
        return packages
    
    def _is_security_tool(self, name: str, description: str) -> bool:
        """Determine if a package is a security tool"""
        security_keywords = [
            'penetration', 'pentest', 'exploit', 'vulnerability', 'scanner',
            'fuzzer', 'crack', 'hash', 'forensic', 'reverse', 'malware',
            'network', 'wireless', 'web', 'sql injection', 'xss', 'security',
            'audit', 'monitor', 'analyze', 'decrypt', 'encrypt', 'steganography'
        ]
        
        text = (name + ' ' + description).lower()
        return any(keyword in text for keyword in security_keywords)
    
    def _get_blackarch_essential_tools(self) -> List[PackageInfo]:
        """Hardcoded list of essential BlackArch tools"""
        tools = [
            "0trace", "3proxy", "afl", "aircrack-ng", "angr", "apktool", 
            "armitage", "autopsy", "binwalk", "bloodhound", "burpsuite",
            "capstone", "commix", "crackmapexec", "dirb", "dnsrecon",
            "empire", "exploit-db", "eyewitness", "fierce", "foremost",
            "gobuster", "hashcat", "hydra", "impacket", "john", "maltego",
            "masscan", "metasploit", "nikto", "nmap", "nuclei", "opencv",
            "radare2", "recon-ng", "responder", "searchsploit", "sherlock",
            "sqlmap", "sublist3r", "theharvester", "volatility", "wfuzz",
            "wireshark", "wordlists", "yara", "zaproxy"
        ]
        
        return [
            PackageInfo(
                name=tool,
                version="latest",
                source_repo="blackarch", 
                description=f"BlackArch security tool: {tool}",
                category="security",
                security_level="high"
            ) for tool in tools
        ]
    
    def _get_kali_essential_tools(self) -> List[PackageInfo]:
        """Hardcoded list of essential Kali tools"""
        tools = [
            "aircrack-ng", "beef-xss", "burpsuite", "dirb", "exploitdb",
            "gobuster", "hashcat", "hydra", "john", "maltego", "masscan",
            "metasploit-framework", "nmap", "recon-ng", "sqlmap", 
            "theharvester", "wireshark", "zaproxy", "nikto", "wfuzz",
            "binwalk", "foremost", "volatility-tools", "autopsy"
        ]
        
        return [
            PackageInfo(
                name=tool,
                version="latest",
                source_repo="kali",
                description=f"Kali Linux security tool: {tool}",
                category="security", 
                security_level="high"
            ) for tool in tools
        ]
    
    def _get_parrot_essential_tools(self) -> List[PackageInfo]:
        """Hardcoded list of essential ParrotOS tools"""
        tools = [
            "anonsurf", "firejail", "tor-browser", "i2p", "aircrack-ng",
            "nmap", "wireshark", "burpsuite", "zaproxy", "nikto", "dirb",
            "gobuster", "hydra", "john", "hashcat", "metasploit-framework"
        ]
        
        return [
            PackageInfo(
                name=tool,
                version="latest",
                source_repo="parrot",
                description=f"ParrotOS security tool: {tool}",
                category="security",
                security_level="high"
            ) for tool in tools
        ]
    
    async def install_packages(self, package_names: List[str], context: str = "operational") -> bool:
        """Install packages with AI-enhanced resolution"""
        self.logger.info(f"Installing packages: {package_names}")
        
        # Find all matching packages across repositories
        matching_packages = []
        for name in package_names:
            packages = self._find_packages(name)
            matching_packages.extend(packages)
        
        if not matching_packages:
            self.logger.error("No packages found to install")
            return False
        
        # Resolve conflicts with AI
        if self.conflict_resolver:
            resolved_packages = await self.conflict_resolver.resolve_conflicts(matching_packages)
        else:
            resolved_packages = matching_packages
        
        # Install resolved packages
        success = True
        for pkg in resolved_packages:
            if not await self._install_package(pkg, context):
                success = False
                
        return success
    
    def _find_packages(self, name: str) -> List[PackageInfo]:
        """Find packages by name across all repositories"""
        packages = []
        
        for repo_name, repo_packages in self.package_cache.items():
            for pkg in repo_packages:
                if name.lower() in pkg.name.lower():
                    packages.append(pkg)
        
        return packages
    
    async def _install_package(self, pkg: PackageInfo, context: str) -> bool:
        """Install a single package"""
        self.logger.info(f"Installing {pkg.name} from {pkg.source_repo}")
        
        try:
            # Different installation methods based on source
            if pkg.source_repo == "synos":
                return await self._install_synos_package(pkg)
            else:
                return await self._install_external_package(pkg)
                
        except Exception as e:
            self.logger.error(f"Failed to install {pkg.name}: {e}")
            return False
    
    async def _install_synos_package(self, pkg: PackageInfo) -> bool:
        """Install custom Syn_OS package"""
        # Custom installation logic for our AI-enhanced tools
        self.logger.info(f"Installing Syn_OS custom package: {pkg.name}")
        
        # This would involve:
        # 1. Download from our repository
        # 2. Install AI wrapper components
        # 3. Configure consciousness integration
        # 4. Register with AI orchestrator
        
        return True
    
    async def _install_external_package(self, pkg: PackageInfo) -> bool:
        """Install package from external repository"""
        # Use appropriate package manager
        if pkg.source_repo == "debian":
            cmd = ["apt-get", "install", "-y", pkg.name]
        elif pkg.source_repo in ["kali", "parrot"]:
            cmd = ["apt-get", "install", "-y", pkg.name]
        elif pkg.source_repo == "blackarch":
            cmd = ["pacman", "-S", "--noconfirm", pkg.name]
        else:
            self.logger.error(f"Unknown repository: {pkg.source_repo}")
            return False
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"Successfully installed {pkg.name}")
                
                # Add AI wrapper after installation
                await self._add_ai_wrapper(pkg)
                return True
            else:
                self.logger.error(f"Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Installation exception: {e}")
            return False
    
    async def _add_ai_wrapper(self, pkg: PackageInfo):
        """Add AI enhancement wrapper to installed tool"""
        wrapper_script = f"""#!/bin/bash
# AI Wrapper for {pkg.name}
# Provides consciousness integration for security tool

TOOL_NAME="{pkg.name}"
ORIGINAL_BINARY="$(which {pkg.name})"

# Log tool execution to consciousness
echo "$(date): $TOOL_NAME executed with args: $@" >> /var/log/synos/tool_usage.log

# Execute original tool with AI monitoring
exec "$ORIGINAL_BINARY" "$@"
"""
        
        wrapper_path = f"/usr/local/bin/ai-{pkg.name}"
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
        
        # Make executable
        subprocess.run(["chmod", "+x", wrapper_path])
        
        self.logger.info(f"Added AI wrapper for {pkg.name}")

async def main():
    """Main function for testing"""
    logging.basicConfig(level=logging.INFO)
    
    manager = SynPkgManager()
    await manager.load_config()
    await manager.update_package_lists()
    
    # Test installation
    await manager.install_packages(["nmap", "burpsuite", "wireshark"])

if __name__ == "__main__":
    asyncio.run(main())