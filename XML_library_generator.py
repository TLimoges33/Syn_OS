#!/usr/bin/env python3
"""
GitHub Repository & Project XML Library Generator
Creates XML library of GitHub repositories and proprietary projects with human-readable documentation
"""

import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubProjectLibrary:
    """Generates XML library from GitHub repositories and proprietary projects"""
    
    def __init__(self, username: str, token: Optional[str] = None):
        self.username = username
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.token}' if self.token else None,
            'Accept': 'application/vnd.github.v3+json'
        }
        self.xml_library_path = "XML_library"
        
        # Project categories for organization
        self.categories = {
            'cybersecurity': ['security', 'cyber', 'hack', 'encryption', 'auth', 'firewall', 'audit'],
            'ai_ml': ['ai', 'ml', 'machine', 'learning', 'neural', 'consciousness', 'intelligence'],
            'os_development': ['os', 'kernel', 'boot', 'system', 'driver', 'hardware'],
            'web_development': ['web', 'html', 'css', 'javascript', 'react', 'vue', 'angular'],
            'cloud_devops': ['cloud', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci', 'cd'],
            'data_science': ['data', 'analysis', 'visualization', 'pandas', 'numpy', 'jupyter'],
            'mobile_development': ['mobile', 'android', 'ios', 'flutter', 'react-native'],
            'blockchain': ['blockchain', 'crypto', 'bitcoin', 'ethereum', 'smart', 'contract'],
            'game_development': ['game', 'unity', 'unreal', 'godot', 'pygame', 'graphics'],
            'education': ['education', 'tutorial', 'learning', 'course', 'training'],
            'tools_utilities': ['tool', 'utility', 'helper', 'script', 'automation'],
            'frameworks_libraries': ['framework', 'library', 'sdk', 'api', 'package'],
            'research_experimental': ['research', 'experimental', 'prototype', 'poc', 'demo']
        }
        
    def setup_xml_library(self):
        """Create XML library directory structure"""
        if not os.path.exists(self.xml_library_path):
            os.makedirs(self.xml_library_path)
            logger.info(f"✅ Created XML library directory: {self.xml_library_path}")
        
        # Create category subdirectories
        for category in self.categories.keys():
            category_path = os.path.join(self.xml_library_path, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
                logger.info(f"✅ Created category directory: {category_path}")
    
    def fetch_user_repositories(self) -> List[Dict]:
        """Fetch all repositories for a user (both owned and starred)"""
        repositories = []
        
        # Fetch owned repositories
        try:
            owned_repos = self._fetch_paginated(f"{self.base_url}/users/{self.username}/repos")
            for repo in owned_repos:
                repo['relationship'] = 'owned'
            repositories.extend(owned_repos)
            logger.info(f"✅ Fetched {len(owned_repos)} owned repositories")
        except Exception as e:
            logger.error(f"❌ Error fetching owned repositories: {e}")
        
        # Fetch starred repositories
        try:
            starred_repos = self._fetch_paginated(f"{self.base_url}/users/{self.username}/starred")
            for repo in starred_repos:
                repo['relationship'] = 'starred'
            repositories.extend(starred_repos)
            logger.info(f"✅ Fetched {len(starred_repos)} starred repositories")
        except Exception as e:
            logger.error(f"❌ Error fetching starred repositories: {e}")
        
        # Fetch forked repositories
        try:
            all_repos = self._fetch_paginated(f"{self.base_url}/users/{self.username}/repos")
            forked_repos = [repo for repo in all_repos if repo.get('fork', False)]
            for repo in forked_repos:
                repo['relationship'] = 'forked'
            logger.info(f"✅ Identified {len(forked_repos)} forked repositories")
        except Exception as e:
            logger.error(f"❌ Error identifying forked repositories: {e}")
        
        return repositories
    
    def _fetch_paginated(self, url: str) -> List[Dict]:
        """Fetch all pages of a paginated GitHub API response"""
        results = []
        page = 1
        
        while True:
            try:
                response = requests.get(f"{url}?page={page}&per_page=100", headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if not data:  # Empty page means we're done
                        break
                    results.extend(data)
                    page += 1
                elif response.status_code == 403:
                    logger.warning("⚠️ Rate limit reached, consider using GitHub token")
                    break
                else:
                    logger.error(f"❌ API request failed with status {response.status_code}")
                    break
            except Exception as e:
                logger.error(f"❌ Error fetching page {page}: {e}")
                break
        
        return results
    
    def categorize_repository(self, repo: Dict) -> str:
        """Categorize repository based on name, description, and topics"""
        repo_text = f"{repo.get('name', '')} {repo.get('description', '')} {' '.join(repo.get('topics', []))}"
        repo_text = repo_text.lower()
        
        # Check each category for keywords
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in repo_text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'tools_utilities' as default
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'tools_utilities'
    
    def create_repository_xml(self, repo: Dict, category: str):
        """Create XML file for a repository"""
        root = ET.Element("repository")
        
        # Basic information
        ET.SubElement(root, "name").text = repo.get('name', '')
        ET.SubElement(root, "full_name").text = repo.get('full_name', '')
        ET.SubElement(root, "description").text = repo.get('description', '') or 'No description available'
        ET.SubElement(root, "url").text = repo.get('html_url', '')
        ET.SubElement(root, "clone_url").text = repo.get('clone_url', '')
        ET.SubElement(root, "ssh_url").text = repo.get('ssh_url', '')
        
        # Repository metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "language").text = repo.get('language', '') or 'Unknown'
        ET.SubElement(metadata, "stars").text = str(repo.get('stargazers_count', 0))
        ET.SubElement(metadata, "forks").text = str(repo.get('forks_count', 0))
        ET.SubElement(metadata, "watchers").text = str(repo.get('watchers_count', 0))
        ET.SubElement(metadata, "size").text = str(repo.get('size', 0))
        ET.SubElement(metadata, "default_branch").text = repo.get('default_branch', 'main')
        ET.SubElement(metadata, "created_at").text = repo.get('created_at', '')
        ET.SubElement(metadata, "updated_at").text = repo.get('updated_at', '')
        ET.SubElement(metadata, "pushed_at").text = repo.get('pushed_at', '')
        
        # Relationship and category
        ET.SubElement(metadata, "relationship").text = repo.get('relationship', 'unknown')
        ET.SubElement(metadata, "category").text = category
        ET.SubElement(metadata, "is_fork").text = str(repo.get('fork', False))
        ET.SubElement(metadata, "is_private").text = str(repo.get('private', False))
        ET.SubElement(metadata, "has_wiki").text = str(repo.get('has_wiki', False))
        ET.SubElement(metadata, "has_pages").text = str(repo.get('has_pages', False))
        ET.SubElement(metadata, "has_downloads").text = str(repo.get('has_downloads', False))
        
        # Topics
        if repo.get('topics'):
            topics = ET.SubElement(root, "topics")
            for topic in repo['topics']:
                ET.SubElement(topics, "topic").text = topic
        
        # License
        if repo.get('license'):
            license_elem = ET.SubElement(root, "license")
            ET.SubElement(license_elem, "name").text = repo['license'].get('name', '')
            ET.SubElement(license_elem, "spdx_id").text = repo['license'].get('spdx_id', '')
        
        # Owner information
        if repo.get('owner'):
            owner = ET.SubElement(root, "owner")
            ET.SubElement(owner, "login").text = repo['owner'].get('login', '')
            ET.SubElement(owner, "type").text = repo['owner'].get('type', '')
            ET.SubElement(owner, "url").text = repo['owner'].get('html_url', '')
        
        # Development potential assessment
        potential = ET.SubElement(root, "development_potential")
        self._assess_development_potential(repo, potential)
        
        # Save XML file
        xml_filename = f"{repo.get('name', 'unknown')}.xml"
        xml_path = os.path.join(self.xml_library_path, category, xml_filename)
        
        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        logger.info(f"✅ Created XML: {xml_path}")
    
    def _assess_development_potential(self, repo: Dict, potential_elem: ET.Element):
        """Assess development potential of repository"""
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        size = repo.get('size', 0)
        has_recent_activity = self._has_recent_activity(repo.get('updated_at', ''))
        
        # Calculate potential score
        score = 0
        if stars > 100: score += 2
        elif stars > 10: score += 1
        
        if forks > 50: score += 2
        elif forks > 5: score += 1
        
        if size > 1000: score += 1
        if has_recent_activity: score += 2
        if repo.get('has_wiki'): score += 1
        if repo.get('topics'): score += 1
        
        # Determine potential level
        if score >= 7:
            level = "high"
        elif score >= 4:
            level = "medium"
        else:
            level = "low"
        
        ET.SubElement(potential_elem, "level").text = level
        ET.SubElement(potential_elem, "score").text = str(score)
        ET.SubElement(potential_elem, "assessment").text = self._get_potential_assessment(level, repo)
    
    def _has_recent_activity(self, updated_at: str) -> bool:
        """Check if repository has recent activity (within last year)"""
        if not updated_at:
            return False
        try:
            from datetime import datetime, timedelta
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            one_year_ago = datetime.now().replace(tzinfo=updated.tzinfo) - timedelta(days=365)
            return updated > one_year_ago
        except:
            return False
    
    def _get_potential_assessment(self, level: str, repo: Dict) -> str:
        """Get detailed assessment text based on potential level"""
        assessments = {
            "high": f"Excellent potential for integration. High community engagement with {repo.get('stargazers_count', 0)} stars and active development. Consider for immediate evaluation.",
            "medium": f"Good potential for integration. Moderate community interest with {repo.get('stargazers_count', 0)} stars. Suitable for selective implementation.",
            "low": f"Limited integration potential. Lower community engagement but may have specific use cases. Consider for research or learning purposes."
        }
        return assessments.get(level, "Assessment unavailable")
    
    def create_proprietary_projects_xml(self):
        """Create XML files for proprietary projects planned for development"""
        proprietary_projects = [
            {
                "name": "SynapticOS_Consciousness_Kernel",
                "description": "Advanced consciousness-driven operating system kernel with neural darwinism integration",
                "category": "os_development",
                "priority": "critical",
                "technologies": ["Rust", "Assembly", "C", "Python"],
                "features": ["Neural networks", "Quantum computing", "AI integration", "Security framework"],
                "target_release": "September 2025",
                "development_status": "active",
                "team_size": "14 developers + AI",
                "ai_acceleration": "10x speed multiplier"
            },
            {
                "name": "Zero_Trust_Security_Framework",
                "description": "Enterprise-grade zero-trust security architecture for SynapticOS",
                "category": "cybersecurity",
                "priority": "critical",
                "technologies": ["Rust", "Go", "Python", "C++"],
                "features": ["Encryption", "Threat detection", "Audit logging", "Access control"],
                "target_release": "September 2025",
                "development_status": "active",
                "team_size": "2-3 developers",
                "ai_acceleration": "Security-focused MCP"
            },
            {
                "name": "Consciousness_AI_Bridge",
                "description": "Bridge between AI systems and consciousness kernel for seamless integration",
                "category": "ai_ml",
                "priority": "high",
                "technologies": ["Python", "PyTorch", "Ray", "Rust"],
                "features": ["Neural darwinism", "Consciousness modeling", "AI orchestration"],
                "target_release": "September 2025",
                "development_status": "active",
                "team_size": "3-4 developers",
                "ai_acceleration": "All AI tools active"
            },
            {
                "name": "Performance_Optimization_Engine",
                "description": "High-performance system optimization and benchmarking suite",
                "category": "os_development",
                "priority": "high",
                "technologies": ["Rust", "C", "Assembly", "LLVM"],
                "features": ["Memory management", "CPU scheduling", "I/O optimization", "Profiling"],
                "target_release": "September 2025",
                "development_status": "active",
                "team_size": "2-3 developers",
                "ai_acceleration": "Performance analysis tools"
            },
            {
                "name": "Educational_Platform_Integration",
                "description": "Comprehensive educational and training platform for SynapticOS",
                "category": "education",
                "priority": "medium",
                "technologies": ["Python", "JavaScript", "React", "Docker"],
                "features": ["Interactive tutorials", "Gamification", "Progress tracking", "Certification"],
                "target_release": "October 2025",
                "development_status": "planning",
                "team_size": "1 developer",
                "ai_acceleration": "Educational MCP tools"
            },
            {
                "name": "Enterprise_Integration_Suite",
                "description": "Enterprise-grade APIs and scalability features for business environments",
                "category": "frameworks_libraries",
                "priority": "medium",
                "technologies": ["Go", "Python", "Kubernetes", "gRPC"],
                "features": ["Business APIs", "Scalability", "Compliance", "Management console"],
                "target_release": "October 2025",
                "development_status": "planning",
                "team_size": "1 developer",
                "ai_acceleration": "Enterprise tools"
            },
            {
                "name": "Quantum_Computing_Integration",
                "description": "Advanced quantum computing algorithms and consciousness modeling",
                "category": "research_experimental",
                "priority": "low",
                "technologies": ["Python", "Qiskit", "C++", "CUDA"],
                "features": ["Quantum algorithms", "Consciousness simulation", "Mathematical libraries"],
                "target_release": "November 2025",
                "development_status": "research",
                "team_size": "1 developer",
                "ai_acceleration": "Research tools"
            }
        ]
        
        for project in proprietary_projects:
            self._create_proprietary_xml(project)
    
    def _create_proprietary_xml(self, project: Dict):
        """Create XML file for a proprietary project"""
        root = ET.Element("proprietary_project")
        
        # Basic information
        ET.SubElement(root, "name").text = project["name"]
        ET.SubElement(root, "description").text = project["description"]
        ET.SubElement(root, "category").text = project["category"]
        ET.SubElement(root, "priority").text = project["priority"]
        ET.SubElement(root, "target_release").text = project["target_release"]
        ET.SubElement(root, "development_status").text = project["development_status"]
        ET.SubElement(root, "team_size").text = project["team_size"]
        ET.SubElement(root, "ai_acceleration").text = project["ai_acceleration"]
        
        # Technologies
        technologies = ET.SubElement(root, "technologies")
        for tech in project["technologies"]:
            ET.SubElement(technologies, "technology").text = tech
        
        # Features
        features = ET.SubElement(root, "features")
        for feature in project["features"]:
            ET.SubElement(features, "feature").text = feature
        
        # Development planning
        planning = ET.SubElement(root, "development_planning")
        ET.SubElement(planning, "created_date").text = datetime.now().isoformat()
        ET.SubElement(planning, "estimated_completion").text = project["target_release"]
        ET.SubElement(planning, "complexity").text = self._assess_project_complexity(project)
        ET.SubElement(planning, "dependencies").text = self._identify_dependencies(project)
        
        # Save XML file
        xml_filename = f"{project['name']}.xml"
        xml_path = os.path.join(self.xml_library_path, project["category"], xml_filename)
        
        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        logger.info(f"✅ Created proprietary project XML: {xml_path}")
    
    def _assess_project_complexity(self, project: Dict) -> str:
        """Assess complexity of proprietary project"""
        tech_count = len(project["technologies"])
        feature_count = len(project["features"])
        
        if tech_count >= 4 or feature_count >= 4:
            return "high"
        elif tech_count >= 2 or feature_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _identify_dependencies(self, project: Dict) -> str:
        """Identify project dependencies"""
        category = project["category"]
        if category == "os_development":
            return "Consciousness kernel, security framework, performance optimization"
        elif category == "cybersecurity":
            return "OS kernel, hardware security modules, audit systems"
        elif category == "ai_ml":
            return "Consciousness kernel, neural frameworks, quantum computing"
        else:
            return "Standard system libraries, framework dependencies"
    
    def create_library_index(self):
        """Create master index of all projects in the XML library"""
        root = ET.Element("project_library_index")
        ET.SubElement(root, "generated_date").text = datetime.now().isoformat()
        ET.SubElement(root, "username").text = self.username
        ET.SubElement(root, "total_categories").text = str(len(self.categories))
        
        # Count projects by category
        for category in self.categories.keys():
            category_path = os.path.join(self.xml_library_path, category)
            if os.path.exists(category_path):
                xml_files = [f for f in os.listdir(category_path) if f.endswith('.xml')]
                category_elem = ET.SubElement(root, "category")
                ET.SubElement(category_elem, "name").text = category
                ET.SubElement(category_elem, "project_count").text = str(len(xml_files))
                
                projects = ET.SubElement(category_elem, "projects")
                for xml_file in xml_files:
                    project_elem = ET.SubElement(projects, "project")
                    ET.SubElement(project_elem, "filename").text = xml_file
                    ET.SubElement(project_elem, "name").text = xml_file.replace('.xml', '')
        
        # Save index
        index_path = os.path.join(self.xml_library_path, "library_index.xml")
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        logger.info(f"✅ Created library index: {index_path}")
    
    def create_human_readable_documentation(self):
        """Create comprehensive human-readable documentation"""
        doc_content = self._generate_markdown_documentation()
        
        doc_path = os.path.join(self.xml_library_path, "PROJECT_LIBRARY_DOCUMENTATION.md")
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        logger.info(f"✅ Created human-readable documentation: {doc_path}")
    
    def _generate_markdown_documentation(self) -> str:
        """Generate comprehensive markdown documentation"""
        doc = f"""# 🏆 **SynapticOS Project Library Documentation**

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

## 📊 **Library Overview**

This XML library contains a comprehensive catalog of all GitHub repositories and proprietary projects related to SynapticOS development. The library is organized by categories for easy navigation and future development reference.

### **📁 Library Structure:**
```
XML_library/
├── cybersecurity/          # Security-related projects
├── ai_ml/                  # AI and machine learning projects
├── os_development/         # Operating system development
├── web_development/        # Web-based projects
├── cloud_devops/           # Cloud and DevOps tools
├── data_science/           # Data analysis and science
├── mobile_development/     # Mobile applications
├── blockchain/             # Blockchain and cryptocurrency
├── game_development/       # Game development projects
├── education/              # Educational and training
├── tools_utilities/        # General tools and utilities
├── frameworks_libraries/   # Frameworks and libraries
└── research_experimental/  # Research and experimental
```

---

## 🎯 **Project Categories**

"""
        
        # Add category documentation
        for category, keywords in self.categories.items():
            category_path = os.path.join(self.xml_library_path, category)
            if os.path.exists(category_path):
                xml_files = [f for f in os.listdir(category_path) if f.endswith('.xml')]
                
                doc += f"""### **{category.replace('_', ' ').title()}**
- **Keywords:** {', '.join(keywords)}
- **Project Count:** {len(xml_files)}
- **Description:** {self._get_category_description(category)}

"""
                
                if xml_files:
                    doc += "**Projects:**\n"
                    for xml_file in sorted(xml_files):
                        project_name = xml_file.replace('.xml', '').replace('_', ' ').title()
                        doc += f"- `{project_name}`\n"
                    doc += "\n"
        
        # Add proprietary projects section
        doc += """---

## 🚀 **Proprietary SynapticOS Projects**

These are custom projects being developed specifically for the SynapticOS ecosystem:

### **🔥 Critical Priority Projects:**
- **SynapticOS Consciousness Kernel** - Core OS with neural darwinism
- **Zero Trust Security Framework** - Enterprise-grade security architecture

### **⚡ High Priority Projects:**
- **Consciousness AI Bridge** - AI system integration layer
- **Performance Optimization Engine** - System performance suite

### **📚 Medium Priority Projects:**
- **Educational Platform Integration** - Learning and training system
- **Enterprise Integration Suite** - Business environment features

### **🔬 Research Projects:**
- **Quantum Computing Integration** - Advanced quantum algorithms

---

## 📈 **Development Potential Assessment**

Each GitHub repository is automatically assessed for development potential:

- **High Potential** (⭐⭐⭐): Excellent community engagement, active development, immediate integration value
- **Medium Potential** (⭐⭐): Good community interest, selective implementation potential
- **Low Potential** (⭐): Limited engagement, research or learning value

---

## 🤖 **AI-Accelerated Development**

All projects in this library can leverage the configured AI tools:

- **GitHub Copilot** - Code completion and suggestions
- **Claude Desktop** - Advanced reasoning with 25+ MCP servers
- **Kilo Code** - Context management and knowledge graphs
- **10x Speed Multiplier** - Through AI acceleration techniques

---

## 🔄 **Usage Instructions**

### **Finding Projects:**
1. Browse categories in the XML_library/ directory
2. Review XML files for detailed project information
3. Use the library_index.xml for quick overview
4. Reference this documentation for human-readable summaries

### **Integration Planning:**
1. Identify high-potential projects from assessments
2. Review technical specifications in XML files
3. Plan integration with SynapticOS architecture
4. Leverage AI tools for rapid development

### **Development Workflow:**
1. Clone interesting repositories for local analysis
2. Use specialized team branches for focused development
3. Apply ultra-clean enterprise architecture standards
4. Coordinate through team todo lists and sprint planning

---

## 📊 **Statistics Summary**

"""
        
        # Add statistics
        total_projects = 0
        for category in self.categories.keys():
            category_path = os.path.join(self.xml_library_path, category)
            if os.path.exists(category_path):
                xml_files = [f for f in os.listdir(category_path) if f.endswith('.xml')]
                total_projects += len(xml_files)
        
        doc += f"""- **Total Projects Cataloged:** {total_projects}
- **Categories:** {len(self.categories)}
- **GitHub Username:** {self.username}
- **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎯 **September Bootable ISO Integration**

This library supports the September bootable ISO sprint by:

1. **Identifying Integration Candidates** - High-potential repositories for immediate use
2. **Technology Stack Mapping** - Organizing projects by development categories
3. **Resource Planning** - Understanding scope and complexity of potential integrations
4. **Team Coordination** - Providing structured project information for specialized teams

---

**🏆 This library represents the most comprehensive project organization for SynapticOS development!**

*Generated by the SynapticOS XML Library Generator - Part of the ultimate OS development environment.*
"""
        
        return doc
    
    def _get_category_description(self, category: str) -> str:
        """Get description for a category"""
        descriptions = {
            'cybersecurity': 'Security tools, frameworks, and practices for enterprise-grade protection',
            'ai_ml': 'Artificial intelligence and machine learning projects for consciousness integration',
            'os_development': 'Operating system kernels, drivers, and low-level system components',
            'web_development': 'Web applications, frameworks, and front-end technologies',
            'cloud_devops': 'Cloud infrastructure, containerization, and DevOps automation tools',
            'data_science': 'Data analysis, visualization, and scientific computing projects',
            'mobile_development': 'Mobile applications and cross-platform development frameworks',
            'blockchain': 'Blockchain technologies, cryptocurrencies, and decentralized applications',
            'game_development': 'Game engines, graphics programming, and interactive entertainment',
            'education': 'Educational platforms, learning management systems, and training tools',
            'tools_utilities': 'General-purpose tools, utilities, and productivity applications',
            'frameworks_libraries': 'Reusable frameworks, libraries, and software development kits',
            'research_experimental': 'Cutting-edge research projects and experimental technologies'
        }
        return descriptions.get(category, 'Miscellaneous projects and tools')
    
    def run_full_library_generation(self):
        """Run complete XML library generation process"""
        logger.info("🚀 Starting GitHub Project XML Library Generation...")
        
        # Setup directory structure
        self.setup_xml_library()
        
        # Fetch and process GitHub repositories
        repositories = self.fetch_user_repositories()
        
        for repo in repositories:
            try:
                category = self.categorize_repository(repo)
                self.create_repository_xml(repo, category)
            except Exception as e:
                logger.error(f"❌ Error processing repository {repo.get('name', 'unknown')}: {e}")
        
        # Create proprietary projects
        self.create_proprietary_projects_xml()
        
        # Create library index
        self.create_library_index()
        
        # Create human-readable documentation
        self.create_human_readable_documentation()
        
        logger.info("✅ XML Library generation completed successfully!")
        logger.info(f"📁 Library location: {os.path.abspath(self.xml_library_path)}")


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Generate XML library from GitHub repositories')
    parser.add_argument('username', help='GitHub username')
    parser.add_argument('--token', help='GitHub API token (or set GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    # Create and run library generator
    library = GitHubProjectLibrary(args.username, args.token)
    library.run_full_library_generation()


if __name__ == "__main__":
    main()
