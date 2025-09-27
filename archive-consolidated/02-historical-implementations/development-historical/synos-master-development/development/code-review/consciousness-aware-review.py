#!/usr/bin/env python3
"""
SynOS Consciousness-Aware Code Review System
Neural Darwinism integration for intelligent code analysis
"""

import os
import sys
import json
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import ast
import re

class ConsciousnessCodeReviewer:
    """Neural Darwinism-powered code review system"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.consciousness_metrics = {
            'emergence_potential': 0.0,
            'neural_complexity': 0.0,
            'adaptation_score': 0.0,
            'fitness_contribution': 0.0
        }
        self.review_history = []
        
    async def analyze_code_fitness(self, file_path: str) -> Dict:
        """Analyze code using Neural Darwinism fitness principles"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file': file_path,
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'cyclomatic_complexity': self._calculate_complexity(content),
                    'neural_patterns': self._detect_neural_patterns(content),
                    'emergence_indicators': self._check_emergence_potential(content),
                    'adaptation_readiness': self._assess_adaptation(content)
                },
                'suggestions': [],
                'consciousness_score': 0.0
            }
            
            # Calculate overall consciousness compatibility
            analysis['consciousness_score'] = self._calculate_consciousness_score(analysis['metrics'])
            
            # Generate improvement suggestions
            analysis['suggestions'] = self._generate_suggestions(analysis['metrics'])
            
            return analysis
            
        except Exception as e:
            return {'error': f"Analysis failed: {str(e)}", 'file': file_path}
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity with consciousness weighting"""
        complexity = 0
        
        # Traditional complexity patterns
        complexity += len(re.findall(r'\bif\b', content))
        complexity += len(re.findall(r'\bwhile\b', content))
        complexity += len(re.findall(r'\bfor\b', content))
        complexity += len(re.findall(r'\btry\b', content))
        complexity += len(re.findall(r'\bcatch\b|\bexcept\b', content))
        
        # Consciousness-specific patterns (higher weight)
        complexity += len(re.findall(r'consciousness|neural|emerge', content, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'adapt|evolve|fitness', content, re.IGNORECASE)) * 1.5
        
        return complexity
    
    def _detect_neural_patterns(self, content: str) -> List[str]:
        """Detect Neural Darwinism implementation patterns"""
        patterns = []
        
        neural_indicators = [
            (r'class.*Neural|class.*Consciousness', 'Neural class detected'),
            (r'def.*emerge|def.*evolve', 'Evolution method detected'),
            (r'fitness.*score|adaptation.*rate', 'Fitness calculation found'),
            (r'async.*consciousness|await.*emerge', 'Async consciousness pattern'),
            (r'selection.*pressure|survival', 'Selection mechanism detected')
        ]
        
        for pattern, description in neural_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                patterns.append(description)
        
        return patterns
    
    def _check_emergence_potential(self, content: str) -> float:
        """Assess code's potential for emergent behavior"""
        emergence_score = 0.0
        
        # Complexity indicators
        if len(content.split('\n')) > 100:
            emergence_score += 0.2
        
        # Interaction patterns
        if 'async' in content and 'await' in content:
            emergence_score += 0.3
        
        # Data flow complexity
        if re.search(r'yield|generator', content):
            emergence_score += 0.2
        
        # Neural network indicators
        if re.search(r'neural|network|consciousness', content, re.IGNORECASE):
            emergence_score += 0.3
        
        return min(emergence_score, 1.0)
    
    def _assess_adaptation(self, content: str) -> float:
        """Assess code's adaptability and evolutionary potential"""
        adaptation_score = 0.0
        
        # Modularity indicators
        if 'class' in content:
            adaptation_score += 0.2
        
        # Interface flexibility
        if re.search(r'def.*\*args|def.*\*\*kwargs', content):
            adaptation_score += 0.2
        
        # Configuration adaptability
        if re.search(r'config|settings|parameters', content, re.IGNORECASE):
            adaptation_score += 0.2
        
        # Error handling (survival mechanism)
        if 'try:' in content and 'except' in content:
            adaptation_score += 0.2
        
        # Logging/monitoring (awareness)
        if re.search(r'log|monitor|track', content, re.IGNORECASE):
            adaptation_score += 0.2
        
        return min(adaptation_score, 1.0)
    
    def _calculate_consciousness_score(self, metrics: Dict) -> float:
        """Calculate overall consciousness compatibility score"""
        weights = {
            'cyclomatic_complexity': -0.1,  # Lower complexity preferred
            'neural_patterns': 0.3,         # Neural patterns heavily weighted
            'emergence_indicators': 0.4,     # Emergence potential important
            'adaptation_readiness': 0.3      # Adaptability crucial
        }
        
        score = 0.0
        
        # Normalize complexity (inverse scoring)
        complexity_score = max(0, 1.0 - (metrics['cyclomatic_complexity'] / 50))
        score += complexity_score * weights['cyclomatic_complexity']
        
        # Neural patterns bonus
        neural_bonus = min(len(metrics['neural_patterns']) * 0.1, 1.0)
        score += neural_bonus * weights['neural_patterns']
        
        # Direct metric scoring
        score += metrics['emergence_indicators'] * weights['emergence_indicators']
        score += metrics['adaptation_readiness'] * weights['adaptation_readiness']
        
        return max(0.0, min(1.0, score))
    
    def _generate_suggestions(self, metrics: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        if metrics['cyclomatic_complexity'] > 20:
            suggestions.append("Consider reducing complexity for better consciousness integration")
        
        if metrics['emergence_indicators'] < 0.3:
            suggestions.append("Add async patterns to increase emergence potential")
        
        if metrics['adaptation_readiness'] < 0.5:
            suggestions.append("Implement configuration parameters for better adaptability")
        
        if len(metrics['neural_patterns']) == 0:
            suggestions.append("Consider adding Neural Darwinism design patterns")
        
        if not any('error' in s.lower() for s in metrics['neural_patterns']):
            suggestions.append("Add robust error handling for survival mechanisms")
        
        return suggestions
    
    async def review_pull_request(self, pr_files: List[str]) -> Dict:
        """Review entire pull request with consciousness analysis"""
        review_results = {
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': len(pr_files),
            'overall_score': 0.0,
            'file_analyses': [],
            'summary_suggestions': [],
            'consciousness_impact': 'neutral'
        }
        
        total_score = 0.0
        
        for file_path in pr_files:
            if file_path.endswith(('.py', '.rs', '.js', '.ts', '.go')):
                analysis = await self.analyze_code_fitness(file_path)
                if 'error' not in analysis:
                    review_results['file_analyses'].append(analysis)
                    total_score += analysis['consciousness_score']
        
        # Calculate overall impact
        if review_results['file_analyses']:
            review_results['overall_score'] = total_score / len(review_results['file_analyses'])
            
            if review_results['overall_score'] > 0.7:
                review_results['consciousness_impact'] = 'positive'
            elif review_results['overall_score'] < 0.3:
                review_results['consciousness_impact'] = 'concerning'
        
        # Generate summary suggestions
        review_results['summary_suggestions'] = self._generate_summary_suggestions(review_results)
        
        return review_results
    
    def _generate_summary_suggestions(self, review_results: Dict) -> List[str]:
        """Generate overall suggestions for the pull request"""
        suggestions = []
        
        if review_results['overall_score'] < 0.5:
            suggestions.append("This PR may negatively impact consciousness system performance")
            suggestions.append("Consider refactoring for better Neural Darwinism integration")
        
        high_complexity_files = [
            f for f in review_results['file_analyses'] 
            if f.get('metrics', {}).get('cyclomatic_complexity', 0) > 25
        ]
        
        if high_complexity_files:
            suggestions.append(f"High complexity detected in {len(high_complexity_files)} files")
        
        low_emergence_files = [
            f for f in review_results['file_analyses']
            if f.get('metrics', {}).get('emergence_indicators', 0) < 0.2
        ]
        
        if len(low_emergence_files) > len(review_results['file_analyses']) * 0.5:
            suggestions.append("Consider adding more emergence-enabling patterns")
        
        return suggestions
    
    def generate_review_report(self, review_results: Dict) -> str:
        """Generate human-readable review report"""
        report = f"""
# SynOS Consciousness-Aware Code Review Report

**Timestamp:** {review_results['timestamp']}
**Files Analyzed:** {review_results['files_analyzed']}
**Overall Consciousness Score:** {review_results['overall_score']:.2f}/1.0
**Consciousness Impact:** {review_results['consciousness_impact'].upper()}

## Summary

"""
        
        if review_results['consciousness_impact'] == 'positive':
            report += "✅ This change enhances the consciousness system integration.\n"
        elif review_results['consciousness_impact'] == 'concerning':
            report += "⚠️ This change may negatively impact consciousness system performance.\n"
        else:
            report += "ℹ️ This change has neutral impact on consciousness system.\n"
        
        report += "\n## File Analysis\n\n"
        
        for analysis in review_results['file_analyses']:
            report += f"### {analysis['file']}\n"
            report += f"- **Consciousness Score:** {analysis['consciousness_score']:.2f}/1.0\n"
            report += f"- **Complexity:** {analysis['metrics']['cyclomatic_complexity']}\n"
            report += f"- **Emergence Potential:** {analysis['metrics']['emergence_indicators']:.2f}\n"
            report += f"- **Adaptation Readiness:** {analysis['metrics']['adaptation_readiness']:.2f}\n"
            
            if analysis['metrics']['neural_patterns']:
                report += f"- **Neural Patterns:** {', '.join(analysis['metrics']['neural_patterns'])}\n"
            
            if analysis['suggestions']:
                report += "- **Suggestions:**\n"
                for suggestion in analysis['suggestions']:
                    report += f"  - {suggestion}\n"
            
            report += "\n"
        
        if review_results['summary_suggestions']:
            report += "## Overall Recommendations\n\n"
            for suggestion in review_results['summary_suggestions']:
                report += f"- {suggestion}\n"
        
        report += "\n---\n*Generated by SynOS Consciousness-Aware Code Review System*\n"
        
        return report

async def main():
    """Main entry point for code review system"""
    if len(sys.argv) < 2:
        print("Usage: python consciousness-aware-review.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    reviewer = ConsciousnessCodeReviewer(os.getcwd())
    
    if os.path.isfile(target):
        # Single file analysis
        analysis = await reviewer.analyze_code_fitness(target)
        print(json.dumps(analysis, indent=2))
    
    elif os.path.isdir(target):
        # Directory analysis
        files = []
        for root, _, filenames in os.walk(target):
            for filename in filenames:
                if filename.endswith(('.py', '.rs', '.js', '.ts', '.go')):
                    files.append(os.path.join(root, filename))
        
        review_results = await reviewer.review_pull_request(files)
        report = reviewer.generate_review_report(review_results)
        print(report)
    
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
