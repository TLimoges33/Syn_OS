#!/usr/bin/env python3
"""
Complete Syn_OS repository analyzer that includes BOTH owned and starred repositories.
This provides the full GitHub ecosystem analysis you requested.
"""

import sys
from pathlib import Path
from typing import Dict, List
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from github import Github
from config.settings import Settings

class CompleteSynOSAnalyzer:
    """Complete synchronous Syn_OS integration analyzer for owned + starred repos."""
    
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.user = self.github.get_user()
        
        # Syn_OS integration categories
        self.syn_os_categories = {
            'kernel_modules': {
                'keywords': ['kernel', 'driver', 'module', 'hardware', 'device', 'embedded', 'os', 'operating-system'],
                'languages': ['C', 'C++', 'Assembly', 'Rust'],
                'integration_level': 'core'
            },
            'consciousness_ai': {
                'keywords': ['ai', 'ml', 'neural', 'consciousness', 'cognition', 'reasoning', 'llm', 'gpt', 'transformer', 'intelligence'],
                'languages': ['Python', 'C++', 'CUDA', 'Julia'],
                'integration_level': 'consciousness'
            },
            'security_frameworks': {
                'keywords': ['security', 'encryption', 'cryptography', 'zero-trust', 'quantum', 'cybersecurity', 'pentest', 'vulnerability'],
                'languages': ['C', 'C++', 'Rust', 'Go', 'Python'],
                'integration_level': 'security'
            },
            'educational_platform': {
                'keywords': ['education', 'learning', 'tutorial', 'course', 'interactive', 'teaching', 'guide', 'documentation'],
                'languages': ['JavaScript', 'Python', 'Web', 'React', 'Vue'],
                'integration_level': 'application'
            },
            'development_tools': {
                'keywords': ['development', 'tool', 'compiler', 'debugger', 'ide', 'editor', 'devops', 'automation'],
                'languages': ['Any'],
                'integration_level': 'toolchain'
            },
            'system_utilities': {
                'keywords': ['system', 'utility', 'monitor', 'performance', 'admin', 'management', 'cli', 'terminal'],
                'languages': ['C', 'C++', 'Rust', 'Go', 'Python'],
                'integration_level': 'system'
            },
            'networking_protocols': {
                'keywords': ['network', 'protocol', 'tcp', 'udp', 'socket', 'distributed', 'communication', 'mesh'],
                'languages': ['C', 'C++', 'Rust', 'Go'],
                'integration_level': 'core'
            },
            'web_interfaces': {
                'keywords': ['web', 'frontend', 'backend', 'api', 'dashboard', 'ui', 'interface', 'react', 'vue'],
                'languages': ['JavaScript', 'TypeScript', 'Python', 'Go', 'Rust'],
                'integration_level': 'interface'
            },
            'data_processing': {
                'keywords': ['data', 'processing', 'stream', 'pipeline', 'etl', 'analytics', 'database', 'storage'],
                'languages': ['Python', 'Scala', 'Java', 'Go', 'Rust'],
                'integration_level': 'application'
            },
            'containerization': {
                'keywords': ['docker', 'container', 'kubernetes', 'orchestration', 'deployment', 'cloud', 'microservices'],
                'languages': ['Go', 'Python', 'Shell', 'YAML'],
                'integration_level': 'infrastructure'
            }
        }
    
    def analyze_repository(self, repo, repo_source: str = "owned") -> Dict:
        """Analyze a single repository for Syn_OS integration."""
        try:
            repo_dict = {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'language': repo.language,
                'stargazers_count': repo.stargazers_count,
                'size': repo.size,
                'open_issues_count': repo.open_issues_count,
                'fork': repo.fork,
                'archived': repo.archived,
                'has_wiki': repo.has_wiki,
                'has_pages': repo.has_pages,
                'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                'license': {'name': repo.license.name} if repo.license else None,
                'topics': repo.get_topics() if hasattr(repo, 'get_topics') else [],
                'source': repo_source  # Track if this is owned or starred
            }
        except Exception as e:
            print(f"   ⚠️  Error accessing {repo.name}: {e}")
            return None
        
        # Analyze against Syn_OS categories
        category_scores = {}
        repo_text = f"{repo.name} {repo.description or ''} {' '.join(repo_dict['topics'])}"
        repo_language = repo.language or ''
        
        for category, criteria in self.syn_os_categories.items():
            score = 0.0
            
            # Keyword matching (enhanced scoring)
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
            quality_score = self._calculate_quality_score(repo_dict) * 0.3
            
            # Stars and community (enhanced for popular starred repos)
            stars = repo.stargazers_count
            if repo_source == "starred":
                # Starred repos often have more stars, adjust scoring
                community_score = min(0.3, stars / 5000) * 0.1
            else:
                community_score = min(0.2, stars / 1000) * 0.1
            
            total_score = keyword_score + language_score + quality_score + community_score
            category_scores[category] = total_score
        
        # Find primary category
        primary_category = 'uncategorized'
        integration_potential = 0.0
        matching_categories = []
        
        if category_scores:
            primary_category_item = max(category_scores.items(), key=lambda x: x[1])
            primary_category = primary_category_item[0]
            integration_potential = primary_category_item[1]
            
            for category, score in category_scores.items():
                if score > 0.3:  # Threshold for inclusion
                    matching_categories.append(category)
        
        return {
            'repository': repo_dict,
            'integration_potential': integration_potential,
            'primary_syn_os_category': primary_category,
            'syn_os_categories': matching_categories,
            'category_scores': category_scores
        }
    
    def _calculate_quality_score(self, repo_dict: Dict) -> float:
        """Calculate quality score for integration potential."""
        score = 0.0
        
        # Has description
        if repo_dict.get('description') and len(repo_dict['description']) > 20:
            score += 0.2
        
        # Has license
        if repo_dict.get('license'):
            score += 0.2
        
        # Active repository
        if not repo_dict.get('archived', False):
            score += 0.2
        
        # Community engagement
        stars = repo_dict.get('stargazers_count', 0)
        if stars > 10:
            score += 0.2
        if stars > 100:
            score += 0.1
        if stars > 1000:
            score += 0.1
        
        # Recent activity
        if repo_dict.get('pushed_at'):
            try:
                from datetime import datetime, timedelta
                pushed_date = datetime.fromisoformat(repo_dict['pushed_at'].replace('Z', '+00:00'))
                if datetime.now().replace(tzinfo=pushed_date.tzinfo) - pushed_date < timedelta(days=365):
                    score += 0.1
            except (ValueError, TypeError):
                pass
        
        return min(1.0, score)
    
    def generate_xml(self, repo_analysis: Dict, output_file: Path):
        """Generate XML documentation for a repository."""
        if repo_analysis is None:
            return
            
        root = ET.Element('syn_os_repository_analysis')
        root.set('repository_name', repo_analysis['repository']['name'])
        root.set('repository_source', repo_analysis['repository']['source'])
        root.set('generated_at', datetime.now().isoformat())
        
        # Repository information
        repo_info = ET.SubElement(root, 'repository_information')
        for key, value in repo_analysis['repository'].items():
            if value is not None:
                elem = ET.SubElement(repo_info, key.replace('-', '_'))
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        sub_elem = ET.SubElement(elem, sub_key)
                        sub_elem.text = str(sub_value)
                elif isinstance(value, list):
                    for item in value:
                        item_elem = ET.SubElement(elem, 'item')
                        item_elem.text = str(item)
                else:
                    elem.text = str(value)
        
        # Integration analysis
        integration = ET.SubElement(root, 'syn_os_integration')
        
        # Integration potential
        potential_elem = ET.SubElement(integration, 'integration_potential')
        potential_elem.set('score', f"{repo_analysis['integration_potential']:.2f}")
        potential_elem.set('level', self._get_potential_level(repo_analysis['integration_potential']))
        
        # Primary category
        primary_cat = ET.SubElement(integration, 'primary_category')
        primary_cat.text = repo_analysis['primary_syn_os_category']
        primary_cat.set('integration_level', 
                       self.syn_os_categories.get(repo_analysis['primary_syn_os_category'], {}).get('integration_level', 'unknown'))
        
        # All matching categories
        categories_elem = ET.SubElement(integration, 'matching_categories')
        for category in repo_analysis['syn_os_categories']:
            cat_elem = ET.SubElement(categories_elem, 'category')
            cat_elem.text = category
            cat_elem.set('integration_level', 
                        self.syn_os_categories.get(category, {}).get('integration_level', 'unknown'))
        
        # Save XML file
        xml_content = self._prettify_xml(root)
        with open(output_file, 'w') as f:
            f.write(xml_content)
    
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
    
    def analyze_all_repositories(self, output_dir: Path):
        """Analyze ALL repositories (owned + starred) and generate XML documentation."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔍 Analyzing ALL repositories for user: {self.user.login}")
        print(f"📁 Output directory: {output_dir.absolute()}")
        
        # Create master analysis
        master_root = ET.Element('syn_os_complete_repository_analysis')
        master_root.set('generated_at', datetime.now().isoformat())
        master_root.set('analyzer_version', '2.0')
        master_root.set('includes_starred', 'true')
        
        summary_elem = ET.SubElement(master_root, 'summary')
        owned_repos_elem = ET.SubElement(master_root, 'owned_repositories')
        starred_repos_elem = ET.SubElement(master_root, 'starred_repositories')
        
        # Analysis results
        total_analyzed = 0
        owned_count = 0
        starred_count = 0
        high_potential = 0
        medium_potential = 0
        low_potential = 0
        categories_found = set()
        
        # Analyze owned repositories
        print("🔄 Fetching and analyzing YOUR repositories...")
        try:
            for repo in self.user.get_repos():
                owned_count += 1
                total_analyzed += 1
                print(f"   Analyzing owned: {repo.name}")
                
                analysis = self.analyze_repository(repo, "owned")
                if analysis is None:
                    continue
                
                # Update statistics
                potential = analysis['integration_potential']
                if potential >= 0.8:
                    high_potential += 1
                elif potential >= 0.5:
                    medium_potential += 1
                else:
                    low_potential += 1
                
                for category in analysis['syn_os_categories']:
                    categories_found.add(category)
                
                # Generate individual XML
                xml_file = output_dir / f"owned_{repo.name}_syn_os_analysis.xml"
                self.generate_xml(analysis, xml_file)
                
                # Add to master index
                repo_ref = ET.SubElement(owned_repos_elem, 'repository')
                repo_ref.set('name', repo.name)
                repo_ref.set('full_name', repo.full_name)
                repo_ref.set('integration_potential', f"{analysis['integration_potential']:.2f}")
                repo_ref.set('primary_category', analysis['primary_syn_os_category'])
                repo_ref.set('xml_file', f"owned_{repo.name}_syn_os_analysis.xml")
                
        except Exception as e:
            print(f"⚠️  Error fetching owned repositories: {e}")
        
        # Analyze starred repositories
        print(f"\n⭐ Fetching and analyzing your STARRED repositories...")
        try:
            for repo in self.user.get_starred():
                starred_count += 1
                total_analyzed += 1
                print(f"   Analyzing starred: {repo.full_name}")
                
                analysis = self.analyze_repository(repo, "starred")
                if analysis is None:
                    continue
                
                # Update statistics
                potential = analysis['integration_potential']
                if potential >= 0.8:
                    high_potential += 1
                elif potential >= 0.5:
                    medium_potential += 1
                else:
                    low_potential += 1
                
                for category in analysis['syn_os_categories']:
                    categories_found.add(category)
                
                # Generate individual XML
                safe_name = repo.full_name.replace('/', '_')
                xml_file = output_dir / f"starred_{safe_name}_syn_os_analysis.xml"
                self.generate_xml(analysis, xml_file)
                
                # Add to master index
                repo_ref = ET.SubElement(starred_repos_elem, 'repository')
                repo_ref.set('name', repo.name)
                repo_ref.set('full_name', repo.full_name)
                repo_ref.set('integration_potential', f"{analysis['integration_potential']:.2f}")
                repo_ref.set('primary_category', analysis['primary_syn_os_category'])
                repo_ref.set('xml_file', f"starred_{safe_name}_syn_os_analysis.xml")
                
        except Exception as e:
            print(f"⚠️  Error fetching starred repositories: {e}")
        
        # Update summary
        summary_elem.set('total_analyzed', str(total_analyzed))
        summary_elem.set('owned_repositories', str(owned_count))
        summary_elem.set('starred_repositories', str(starred_count))
        summary_elem.set('high_integration_potential', str(high_potential))
        summary_elem.set('medium_integration_potential', str(medium_potential))
        summary_elem.set('low_integration_potential', str(low_potential))
        
        categories_elem = ET.SubElement(summary_elem, 'categories_found')
        for category in categories_found:
            cat_elem = ET.SubElement(categories_elem, 'category')
            cat_elem.text = category
        
        # Save master analysis
        master_xml = self._prettify_xml(master_root)
        with open(output_dir / 'syn_os_complete_analysis.xml', 'w') as f:
            f.write(master_xml)
        
        return {
            'total_analyzed': total_analyzed,
            'owned_repositories': owned_count,
            'starred_repositories': starred_count,
            'high_integration_potential': high_potential,
            'medium_integration_potential': medium_potential,
            'low_integration_potential': low_potential,
            'categories_found': categories_found
        }

def main():
    """Main function to run the complete analysis."""
    print("🚀 Complete Syn_OS Repository Integration Analysis")
    print("   (Owned + Starred Repositories)")
    print("=" * 60)
    
    try:
        # Load settings
        settings = Settings()
        if not settings.github_token or settings.github_token == 'your_github_personal_access_token_here':
            print("❌ GitHub token not configured!")
            print("   Please run: python configure_github.py")
            return False
        
        # Create analyzer
        analyzer = CompleteSynOSAnalyzer(settings.github_token)
        
        # Run complete analysis
        output_dir = Path("complete_syn_os_analysis")
        results = analyzer.analyze_all_repositories(output_dir)
        
        # Display results
        print("\n" + "="*60)
        print("✅ COMPLETE ANALYSIS FINISHED!")
        print("="*60)
        print(f"📊 Total Repositories Analyzed: {results['total_analyzed']}")
        print(f"🏠 Your Owned Repositories: {results['owned_repositories']}")
        print(f"⭐ Your Starred Repositories: {results['starred_repositories']}")
        print(f"🔥 High Integration Potential: {results['high_integration_potential']}")
        print(f"🔶 Medium Integration Potential: {results['medium_integration_potential']}")
        print(f"🔷 Low Integration Potential: {results['low_integration_potential']}")
        print(f"📂 Categories Found: {len(results['categories_found'])}")
        
        if results['categories_found']:
            print("\n🏷️ Syn_OS Integration Categories:")
            for category in sorted(results['categories_found']):
                print(f"   • {category}")
        
        print(f"\n📄 XML Documentation Generated:")
        print(f"   🎯 Complete analysis: {output_dir}/syn_os_complete_analysis.xml")
        print(f"   🏠 Owned repo analyses: {output_dir}/owned_*_syn_os_analysis.xml")
        print(f"   ⭐ Starred repo analyses: {output_dir}/starred_*_syn_os_analysis.xml")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
    print("\n🎉 Complete GitHub ecosystem analysis ready for Syn_OS integration!")
