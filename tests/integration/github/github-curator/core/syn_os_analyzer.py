"""
Syn_OS integration analysis and XML documentation generator.
Analyzes repositories for potential integration into the Syn_OS ecosystem.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

from services.github_service import GitHubService
from config.settings import Settings
from core.curator import RepositoryCurator

logger = logging.getLogger(__name__)


class SynOSIntegrationAnalyzer:
    """Analyzes repositories for Syn_OS integration potential and generates XML documentation."""
    
    def __init__(self, github_service: GitHubService, settings: Settings):
        self.github = github_service
        self.settings = settings
        self.curator = RepositoryCurator(github_service, settings)
        
        # Syn_OS specific integration categories
        self.syn_os_categories = {
            'kernel_modules': {
                'keywords': ['kernel', 'driver', 'module', 'hardware', 'device', 'embedded'],
                'languages': ['C', 'C++', 'Assembly', 'Rust'],
                'integration_level': 'core'
            },
            'consciousness_ai': {
                'keywords': ['ai', 'ml', 'neural', 'consciousness', 'cognition', 'reasoning', 'llm'],
                'languages': ['Python', 'C++', 'CUDA', 'Julia'],
                'integration_level': 'consciousness'
            },
            'security_frameworks': {
                'keywords': ['security', 'encryption', 'cryptography', 'zero-trust', 'quantum'],
                'languages': ['C', 'C++', 'Rust', 'Go', 'Python'],
                'integration_level': 'security'
            },
            'educational_platform': {
                'keywords': ['education', 'learning', 'tutorial', 'course', 'interactive'],
                'languages': ['JavaScript', 'Python', 'Web', 'React', 'Vue'],
                'integration_level': 'application'
            },
            'development_tools': {
                'keywords': ['development', 'tool', 'compiler', 'debugger', 'ide', 'editor'],
                'languages': ['Any'],
                'integration_level': 'toolchain'
            },
            'system_utilities': {
                'keywords': ['system', 'utility', 'monitor', 'performance', 'admin'],
                'languages': ['C', 'C++', 'Rust', 'Go', 'Python'],
                'integration_level': 'system'
            },
            'networking_protocols': {
                'keywords': ['network', 'protocol', 'tcp', 'udp', 'socket', 'distributed'],
                'languages': ['C', 'C++', 'Rust', 'Go'],
                'integration_level': 'core'
            },
            'web_interfaces': {
                'keywords': ['web', 'frontend', 'backend', 'api', 'dashboard', 'ui'],
                'languages': ['JavaScript', 'TypeScript', 'Python', 'Go', 'Rust'],
                'integration_level': 'interface'
            },
            'data_processing': {
                'keywords': ['data', 'processing', 'stream', 'pipeline', 'etl', 'analytics'],
                'languages': ['Python', 'Scala', 'Java', 'Go', 'Rust'],
                'integration_level': 'application'
            },
            'containerization': {
                'keywords': ['docker', 'container', 'kubernetes', 'orchestration', 'deployment'],
                'languages': ['Go', 'Python', 'Shell', 'YAML'],
                'integration_level': 'infrastructure'
            }
        }
    
    async def analyze_all_repositories(self, output_dir: Path) -> Dict[str, int]:
        """Analyze all repositories and generate XML documentation."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_results = {
            'total_analyzed': 0,
            'high_integration_potential': 0,
            'medium_integration_potential': 0,
            'low_integration_potential': 0,
            'categories_found': set()
        }
        
        # Create master index XML
        master_root = ET.Element('syn_os_repository_analysis')
        master_root.set('generated_at', datetime.now().isoformat())
        master_root.set('analyzer_version', '1.0')
        
        summary_elem = ET.SubElement(master_root, 'summary')
        repos_elem = ET.SubElement(master_root, 'repositories')
        
        async for repo in self.github.get_user_repositories():
            analysis_results['total_analyzed'] += 1
            
            # Analyze repository for Syn_OS integration
            integration_analysis = await self.analyze_repository_integration(repo)
            
            # Update statistics
            potential = integration_analysis['integration_potential']
            if potential >= 0.8:
                analysis_results['high_integration_potential'] += 1
            elif potential >= 0.5:
                analysis_results['medium_integration_potential'] += 1
            else:
                analysis_results['low_integration_potential'] += 1
            
            for category in integration_analysis['syn_os_categories']:
                analysis_results['categories_found'].add(category)
            
            # Generate individual XML file
            await self.generate_repository_xml(repo, integration_analysis, output_dir)
            
            # Add to master index
            repo_ref = ET.SubElement(repos_elem, 'repository')
            repo_ref.set('name', repo['name'])
            repo_ref.set('full_name', repo['full_name'])
            repo_ref.set('integration_potential', f"{integration_analysis['integration_potential']:.2f}")
            repo_ref.set('primary_category', integration_analysis['primary_syn_os_category'])
            repo_ref.set('xml_file', f"{repo['name']}_syn_os_analysis.xml")
        
        # Update summary
        for key, value in analysis_results.items():
            if key != 'categories_found':
                summary_elem.set(key, str(value))
        
        categories_elem = ET.SubElement(summary_elem, 'categories_found')
        for category in analysis_results['categories_found']:
            cat_elem = ET.SubElement(categories_elem, 'category')
            cat_elem.text = category
        
        # Save master index
        master_xml = self._prettify_xml(master_root)
        with open(output_dir / 'syn_os_master_analysis.xml', 'w') as f:
            f.write(master_xml)
        
        logger.info(f"Generated XML analysis for {analysis_results['total_analyzed']} repositories")
        return analysis_results
    
    async def analyze_repository_integration(self, repo: Dict) -> Dict:
        """Analyze a single repository for Syn_OS integration potential."""
        integration_analysis = {
            'repository': repo,
            'syn_os_categories': [],
            'integration_potential': 0.0,
            'primary_syn_os_category': 'uncategorized',
            'integration_suggestions': [],
            'technical_details': {},
            'risks_and_challenges': [],
            'implementation_strategy': {}
        }
        
        # Analyze against Syn_OS categories
        category_scores = {}
        repo_text = f"{repo['name']} {repo.get('description', '')} {' '.join(repo.get('topics', []))}"
        repo_language = repo.get('language', '')
        
        for category, criteria in self.syn_os_categories.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = 0
            for keyword in criteria['keywords']:
                if keyword.lower() in repo_text.lower():
                    keyword_matches += 1
            
            keyword_score = min(1.0, keyword_matches / len(criteria['keywords'])) * 0.6
            
            # Language matching
            language_score = 0.0
            if criteria['languages'] == ['Any'] or repo_language in criteria['languages']:
                language_score = 0.4
            
            # Repository quality and activity
            quality_score = await self._calculate_integration_quality(repo) * 0.3
            
            # Stars and community (indicates usefulness)
            community_score = min(0.2, repo.get('stargazers_count', 0) / 1000) * 0.1
            
            total_score = keyword_score + language_score + quality_score + community_score
            category_scores[category] = total_score
            
            if total_score > 0.3:  # Threshold for inclusion
                integration_analysis['syn_os_categories'].append(category)
        
        # Determine primary category and overall potential
        if category_scores:
            primary_category = max(category_scores.items(), key=lambda x: x[1])
            integration_analysis['primary_syn_os_category'] = primary_category[0]
            integration_analysis['integration_potential'] = primary_category[1]
        
        # Generate integration suggestions
        integration_analysis['integration_suggestions'] = await self._generate_integration_suggestions(
            repo, integration_analysis['primary_syn_os_category']
        )
        
        # Analyze technical details
        integration_analysis['technical_details'] = await self._analyze_technical_details(repo)
        
        # Identify risks and challenges
        integration_analysis['risks_and_challenges'] = await self._identify_integration_risks(repo)
        
        # Create implementation strategy
        integration_analysis['implementation_strategy'] = await self._create_implementation_strategy(
            repo, integration_analysis['primary_syn_os_category']
        )
        
        return integration_analysis
    
    async def generate_repository_xml(self, repo: Dict, analysis: Dict, output_dir: Path):
        """Generate detailed XML documentation for a repository."""
        root = ET.Element('syn_os_repository_analysis')
        root.set('repository_name', repo['name'])
        root.set('generated_at', datetime.now().isoformat())
        
        # Basic repository information
        repo_info = ET.SubElement(root, 'repository_information')
        for key, value in repo.items():
            if isinstance(value, (str, int, bool)) and value is not None:
                elem = ET.SubElement(repo_info, key.replace('-', '_'))
                elem.text = str(value)
        
        # Integration analysis
        integration = ET.SubElement(root, 'syn_os_integration')
        
        # Integration potential
        potential_elem = ET.SubElement(integration, 'integration_potential')
        potential_elem.set('score', f"{analysis['integration_potential']:.2f}")
        potential_elem.set('level', self._get_potential_level(analysis['integration_potential']))
        
        # Primary category
        primary_cat = ET.SubElement(integration, 'primary_category')
        primary_cat.text = analysis['primary_syn_os_category']
        primary_cat.set('integration_level', 
                       self.syn_os_categories.get(analysis['primary_syn_os_category'], {}).get('integration_level', 'unknown'))
        
        # All matching categories
        categories_elem = ET.SubElement(integration, 'matching_categories')
        for category in analysis['syn_os_categories']:
            cat_elem = ET.SubElement(categories_elem, 'category')
            cat_elem.text = category
            cat_elem.set('integration_level', 
                        self.syn_os_categories.get(category, {}).get('integration_level', 'unknown'))
        
        # Integration suggestions
        suggestions_elem = ET.SubElement(integration, 'integration_suggestions')
        for suggestion in analysis['integration_suggestions']:
            sugg_elem = ET.SubElement(suggestions_elem, 'suggestion')
            sugg_elem.set('type', suggestion['type'])
            sugg_elem.set('priority', suggestion['priority'])
            sugg_elem.text = suggestion['description']
        
        # Technical details
        tech_elem = ET.SubElement(integration, 'technical_analysis')
        for key, value in analysis['technical_details'].items():
            detail_elem = ET.SubElement(tech_elem, key)
            if isinstance(value, list):
                for item in value:
                    item_elem = ET.SubElement(detail_elem, 'item')
                    item_elem.text = str(item)
            else:
                detail_elem.text = str(value)
        
        # Risks and challenges
        risks_elem = ET.SubElement(integration, 'risks_and_challenges')
        for risk in analysis['risks_and_challenges']:
            risk_elem = ET.SubElement(risks_elem, 'risk')
            risk_elem.set('severity', risk['severity'])
            risk_elem.set('category', risk['category'])
            risk_elem.text = risk['description']
        
        # Implementation strategy
        strategy_elem = ET.SubElement(integration, 'implementation_strategy')
        for phase, details in analysis['implementation_strategy'].items():
            phase_elem = ET.SubElement(strategy_elem, 'phase')
            phase_elem.set('name', phase)
            phase_elem.set('estimated_effort', details.get('effort', 'unknown'))
            phase_elem.set('priority', details.get('priority', 'medium'))
            
            desc_elem = ET.SubElement(phase_elem, 'description')
            desc_elem.text = details.get('description', '')
            
            if 'steps' in details:
                steps_elem = ET.SubElement(phase_elem, 'steps')
                for step in details['steps']:
                    step_elem = ET.SubElement(steps_elem, 'step')
                    step_elem.text = step
        
        # Save XML file
        xml_content = self._prettify_xml(root)
        filename = f"{repo['name']}_syn_os_analysis.xml"
        with open(output_dir / filename, 'w') as f:
            f.write(xml_content)
    
    async def _calculate_integration_quality(self, repo: Dict) -> float:
        """Calculate quality score for integration potential."""
        score = 0.0
        
        # Has documentation
        if repo.get('description') and len(repo['description']) > 20:
            score += 0.2
        
        # Has license
        if repo.get('license'):
            score += 0.2
        
        # Active repository
        if not repo.get('archived', False):
            score += 0.2
        
        # Community engagement
        stars = repo.get('stargazers_count', 0)
        if stars > 10:
            score += 0.2
        if stars > 100:
            score += 0.1
        
        # Recent activity
        if repo.get('pushed_at'):
            try:
                from datetime import datetime, timedelta
                pushed_date = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
                if datetime.now().replace(tzinfo=pushed_date.tzinfo) - pushed_date < timedelta(days=365):
                    score += 0.1
            except (ValueError, TypeError):
                pass
        
        return min(1.0, score)
    
    async def _generate_integration_suggestions(self, repo: Dict, category: str) -> List[Dict]:
        """Generate specific integration suggestions based on category."""
        suggestions = []
        
        category_suggestions = {
            'kernel_modules': [
                {'type': 'driver_integration', 'priority': 'high', 
                 'description': 'Evaluate for hardware driver integration in Syn_OS kernel'},
                {'type': 'module_adaptation', 'priority': 'medium',
                 'description': 'Adapt as loadable kernel module for specific hardware support'}
            ],
            'consciousness_ai': [
                {'type': 'ai_core_integration', 'priority': 'critical',
                 'description': 'Integrate into Syn_OS consciousness subsystem for cognitive processing'},
                {'type': 'neural_network_optimization', 'priority': 'high',
                 'description': 'Optimize neural network models for real-time consciousness processing'}
            ],
            'security_frameworks': [
                {'type': 'security_layer', 'priority': 'critical',
                 'description': 'Implement as core security layer in Syn_OS architecture'},
                {'type': 'zero_trust_component', 'priority': 'high',
                 'description': 'Integrate into zero-trust security framework'}
            ],
            'educational_platform': [
                {'type': 'learning_module', 'priority': 'medium',
                 'description': 'Integrate as educational component in Syn_OS learning platform'},
                {'type': 'interactive_tutorial', 'priority': 'low',
                 'description': 'Adapt as interactive tutorial for Syn_OS features'}
            ],
            'development_tools': [
                {'type': 'toolchain_integration', 'priority': 'high',
                 'description': 'Include in Syn_OS development toolchain for enhanced productivity'},
                {'type': 'ide_plugin', 'priority': 'medium',
                 'description': 'Develop as plugin for Syn_OS integrated development environment'}
            ],
            'system_utilities': [
                {'type': 'system_service', 'priority': 'high',
                 'description': 'Deploy as system service for monitoring and administration'},
                {'type': 'utility_integration', 'priority': 'medium',
                 'description': 'Integrate into Syn_OS utility suite for system management'}
            ],
            'networking_protocols': [
                {'type': 'protocol_stack', 'priority': 'high',
                 'description': 'Implement in Syn_OS networking protocol stack'},
                {'type': 'distributed_communication', 'priority': 'medium',
                 'description': 'Use for distributed consciousness communication between nodes'}
            ],
            'web_interfaces': [
                {'type': 'dashboard_component', 'priority': 'medium',
                 'description': 'Integrate into Syn_OS web dashboard for system monitoring'},
                {'type': 'api_service', 'priority': 'high',
                 'description': 'Deploy as API service for external system integration'}
            ],
            'data_processing': [
                {'type': 'data_pipeline', 'priority': 'high',
                 'description': 'Implement in Syn_OS data processing pipeline for consciousness data'},
                {'type': 'analytics_engine', 'priority': 'medium',
                 'description': 'Use for real-time analytics and system optimization'}
            ],
            'containerization': [
                {'type': 'deployment_platform', 'priority': 'high',
                 'description': 'Use for Syn_OS service containerization and orchestration'},
                {'type': 'development_environment', 'priority': 'medium',
                 'description': 'Implement for consistent development and testing environments'}
            ]
        }
        
        if category in category_suggestions:
            suggestions.extend(category_suggestions[category])
        else:
            suggestions.append({
                'type': 'general_evaluation',
                'priority': 'low',
                'description': 'Evaluate for potential integration opportunities in Syn_OS ecosystem'
            })
        
        return suggestions
    
    async def _analyze_technical_details(self, repo: Dict) -> Dict:
        """Analyze technical aspects relevant to Syn_OS integration."""
        details = {
            'programming_language': repo.get('language', 'Unknown'),
            'repository_size_kb': repo.get('size', 0),
            'open_issues': repo.get('open_issues_count', 0),
            'is_fork': repo.get('fork', False),
            'has_wiki': repo.get('has_wiki', False),
            'has_pages': repo.get('has_pages', False),
            'dependencies': [],
            'build_system': 'unknown',
            'testing_framework': 'unknown',
            'documentation_quality': 'unknown'
        }
        
        # Analyze based on language
        language = repo.get('language', '').lower()
        if language in ['c', 'c++']:
            details['build_system'] = 'make/cmake'
            details['memory_management'] = 'manual'
            details['performance_profile'] = 'high'
        elif language == 'rust':
            details['build_system'] = 'cargo'
            details['memory_management'] = 'safe'
            details['performance_profile'] = 'high'
        elif language == 'python':
            details['build_system'] = 'pip/setup.py'
            details['memory_management'] = 'garbage_collected'
            details['performance_profile'] = 'medium'
        elif language == 'go':
            details['build_system'] = 'go_modules'
            details['memory_management'] = 'garbage_collected'
            details['performance_profile'] = 'high'
        
        return details
    
    async def _identify_integration_risks(self, repo: Dict) -> List[Dict]:
        """Identify potential risks and challenges for integration."""
        risks = []
        
        # License compatibility
        license_name = repo.get('license', {}).get('name') if repo.get('license') else None
        if not license_name:
            risks.append({
                'severity': 'high',
                'category': 'legal',
                'description': 'No license specified - may not be suitable for integration'
            })
        elif license_name in ['GPL-3.0', 'GPL-2.0', 'AGPL-3.0']:
            risks.append({
                'severity': 'medium',
                'category': 'legal',
                'description': f'{license_name} license may require careful consideration for proprietary integration'
            })
        
        # Maintenance status
        if repo.get('archived', False):
            risks.append({
                'severity': 'high',
                'category': 'maintenance',
                'description': 'Repository is archived - no ongoing maintenance'
            })
        
        # Activity level
        try:
            from datetime import datetime, timedelta
            if repo.get('pushed_at'):
                pushed_date = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
                if datetime.now().replace(tzinfo=pushed_date.tzinfo) - pushed_date > timedelta(days=730):
                    risks.append({
                        'severity': 'medium',
                        'category': 'maintenance',
                        'description': 'Repository appears inactive (no updates in 2+ years)'
                    })
        except (ValueError, TypeError):
            pass
        
        # Size and complexity
        size_kb = repo.get('size', 0)
        if size_kb > 100000:  # > 100MB
            risks.append({
                'severity': 'medium',
                'category': 'technical',
                'description': 'Large repository size may impact integration complexity'
            })
        
        # Language compatibility
        language = repo.get('language', '')
        if language in ['MATLAB', 'R', 'Mathematica']:
            risks.append({
                'severity': 'high',
                'category': 'technical',
                'description': f'{language} may not be suitable for system-level integration'
            })
        
        return risks
    
    async def _create_implementation_strategy(self, repo: Dict, category: str) -> Dict:
        """Create implementation strategy for integrating the repository."""
        strategy = {}
        
        base_phases = {
            'evaluation': {
                'description': 'Detailed evaluation of repository for Syn_OS compatibility',
                'effort': 'low',
                'priority': 'high',
                'steps': [
                    'Review code quality and architecture',
                    'Assess license compatibility',
                    'Evaluate dependencies and build requirements',
                    'Test basic functionality'
                ]
            },
            'adaptation': {
                'description': 'Adapt repository code for Syn_OS integration',
                'effort': 'medium',
                'priority': 'medium',
                'steps': [
                    'Modify build system for Syn_OS compatibility',
                    'Update dependencies to match Syn_OS versions',
                    'Implement Syn_OS-specific interfaces',
                    'Add integration tests'
                ]
            },
            'integration': {
                'description': 'Full integration into Syn_OS ecosystem',
                'effort': 'high',
                'priority': 'medium',
                'steps': [
                    'Integrate with Syn_OS build system',
                    'Implement monitoring and logging',
                    'Add to Syn_OS test suite',
                    'Document integration procedures'
                ]
            },
            'deployment': {
                'description': 'Deploy integrated component in Syn_OS',
                'effort': 'medium',
                'priority': 'low',
                'steps': [
                    'Create deployment configuration',
                    'Set up monitoring and alerting',
                    'Perform integration testing',
                    'Deploy to production environment'
                ]
            }
        }
        
        # Customize strategy based on category
        if category in ['kernel_modules', 'security_frameworks']:
            base_phases['evaluation']['priority'] = 'critical'
            base_phases['adaptation']['effort'] = 'high'
            strategy.update(base_phases)
        elif category in ['consciousness_ai', 'networking_protocols']:
            base_phases['evaluation']['priority'] = 'critical'
            base_phases['integration']['priority'] = 'high'
            strategy.update(base_phases)
        else:
            strategy.update(base_phases)
        
        return strategy
    
    def _get_potential_level(self, score: float) -> str:
        """Convert numerical score to descriptive level."""
        if score >= 0.8:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        elif score >= 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
