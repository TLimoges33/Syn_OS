"""Advanced repository categorization using multiple classification methods."""

import re
import asyncio
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass

from config.settings import Settings, CurationRules

logger = logging.getLogger(__name__)


@dataclass
class CategoryMatch:
    """Represents a category match with confidence score."""
    category: str
    confidence: float
    reasons: List[str]


class RepositoryCategorizer:
    """Advanced repository categorization system."""
    
    def __init__(self, settings: Settings, rules: CurationRules):
        self.settings = settings
        self.rules = rules
        self.category_cache = {}
        
    async def categorize_repository(self, repo: Dict) -> Tuple[str, float]:
        """Categorize a repository and return category with confidence score."""
        repo_id = repo['id']
        
        # Check cache first
        if repo_id in self.category_cache:
            cached = self.category_cache[repo_id]
            return cached['category'], cached['confidence']
        
        # Collect all classification signals
        signals = await self._collect_classification_signals(repo)
        
        # Run classification methods
        keyword_matches = self._classify_by_keywords(signals)
        language_match = self._classify_by_language(signals)
        name_match = self._classify_by_name(signals)
        description_match = self._classify_by_description(signals)
        topics_match = self._classify_by_topics(signals)
        
        # Combine all matches with weighted scoring
        all_matches = [
            *keyword_matches,
            language_match,
            name_match,
            description_match,
            topics_match
        ]
        
        # Filter out None matches
        valid_matches = [match for match in all_matches if match is not None]
        
        if not valid_matches:
            final_category = "Miscellaneous"
            final_confidence = 0.1
        else:
            # Aggregate scores by category
            category_scores = defaultdict(list)
            for match in valid_matches:
                category_scores[match.category].append(match.confidence)
            
            # Calculate weighted average for each category
            category_confidence = {}
            for category, scores in category_scores.items():
                # Use weighted average with diminishing returns for multiple signals
                weighted_score = sum(score * (0.8 ** i) for i, score in enumerate(sorted(scores, reverse=True)))
                category_confidence[category] = min(1.0, weighted_score)
            
            # Select best category
            best_category = max(category_confidence.items(), key=lambda x: x[1])
            final_category, final_confidence = best_category
        
        # Cache the result
        self.category_cache[repo_id] = {
            'category': final_category,
            'confidence': final_confidence
        }
        
        logger.debug(f"Categorized {repo['name']} as {final_category} (confidence: {final_confidence:.2f})")
        return final_category, final_confidence
    
    async def _collect_classification_signals(self, repo: Dict) -> Dict:
        """Collect all available signals for classification."""
        signals = {
            'name': repo.get('name', '').lower(),
            'description': repo.get('description', '').lower(),
            'language': repo.get('language', ''),
            'topics': [topic.lower() for topic in repo.get('topics', [])],
            'readme_content': '',  # Could be fetched if needed
            'stars': repo.get('stargazers_count', 0),
            'size': repo.get('size', 0),
            'fork': repo.get('fork', False),
            'archived': repo.get('archived', False)
        }
        
        # Fetch additional signals if high priority repo
        if signals['stars'] > 100 or not signals['fork']:
            # Could fetch README, file structure, etc.
            pass
        
        return signals
    
    def _classify_by_keywords(self, signals: Dict) -> List[CategoryMatch]:
        """Classify repository based on keyword matching."""
        matches = []
        text_to_search = f"{signals['name']} {signals['description']} {' '.join(signals['topics'])}"
        
        for category, keywords in self.rules.keyword_rules.items():
            category_score = 0.0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Check for exact matches with higher weight
                if keyword_lower in text_to_search:
                    if keyword_lower in signals['name']:
                        category_score += 0.8  # Name matches are strongest
                        matched_keywords.append(f"name:{keyword}")
                    elif keyword_lower in signals['description']:
                        category_score += 0.6  # Description matches are strong
                        matched_keywords.append(f"desc:{keyword}")
                    elif keyword_lower in signals['topics']:
                        category_score += 0.7  # Topic matches are very strong
                        matched_keywords.append(f"topic:{keyword}")
            
            if category_score > 0:
                # Normalize score based on number of keywords
                normalized_score = min(1.0, category_score / 2.0)
                matches.append(CategoryMatch(
                    category=category,
                    confidence=normalized_score,
                    reasons=matched_keywords
                ))
        
        return sorted(matches, key=lambda x: x.confidence, reverse=True)
    
    def _classify_by_language(self, signals: Dict) -> Optional[CategoryMatch]:
        """Classify repository based on primary programming language."""
        language = signals['language']
        if not language:
            return None
        
        # Use language mapping from settings
        if language in self.settings.language_category_mapping:
            category = self.settings.language_category_mapping[language]
            confidence = 0.4  # Language alone is a moderate signal
            
            return CategoryMatch(
                category=category,
                confidence=confidence,
                reasons=[f"language:{language}"]
            )
        
        return None
    
    def _classify_by_name(self, signals: Dict) -> Optional[CategoryMatch]:
        """Classify repository based on naming patterns."""
        name = signals['name']
        
        # Common naming patterns
        patterns = {
            'CLI Tools': [
                r'.*-cli$', r'^cli-.*', r'.*-tool$', r'^tool-.*',
                r'.*-utility$', r'.*-util$', r'.*-script$'
            ],
            'Libraries & Frameworks': [
                r'^lib.*', r'.*-lib$', r'.*-framework$', r'^framework-.*',
                r'.*-sdk$', r'^sdk-.*', r'.*-api$'
            ],
            'Web Development': [
                r'.*-web$', r'^web-.*', r'.*-app$', r'.*-frontend$',
                r'.*-backend$', r'.*-server$', r'.*-client$'
            ],
            'Mobile Development': [
                r'.*-mobile$', r'^mobile-.*', r'.*-android$', r'.*-ios$',
                r'.*-app$'  # Note: overlap with web, will be resolved by other signals
            ],
            'DevOps & Infrastructure': [
                r'.*-docker$', r'^docker-.*', r'.*-k8s$', r'.*-kubernetes$',
                r'.*-terraform$', r'.*-ansible$', r'.*-deploy.*'
            ],
            'Game Development': [
                r'.*-game$', r'^game-.*', r'.*-engine$', r'.*-unity$'
            ]
        }
        
        for category, category_patterns in patterns.items():
            for pattern in category_patterns:
                if re.match(pattern, name):
                    confidence = 0.5  # Name patterns are moderately strong
                    return CategoryMatch(
                        category=category,
                        confidence=confidence,
                        reasons=[f"name_pattern:{pattern}"]
                    )
        
        return None
    
    def _classify_by_description(self, signals: Dict) -> Optional[CategoryMatch]:
        """Classify repository based on description analysis."""
        description = signals['description']
        if not description:
            return None
        
        # Advanced description analysis
        description_indicators = {
            'Web Development': [
                'web application', 'website', 'web app', 'web development',
                'frontend', 'backend', 'full stack', 'rest api', 'graphql'
            ],
            'Data Science & AI': [
                'machine learning', 'deep learning', 'neural network', 'ai',
                'data science', 'data analysis', 'artificial intelligence',
                'ml model', 'nlp', 'computer vision'
            ],
            'DevOps & Infrastructure': [
                'deployment', 'infrastructure', 'monitoring', 'logging',
                'containerization', 'orchestration', 'ci/cd', 'automation'
            ],
            'Security & Privacy': [
                'security', 'privacy', 'encryption', 'authentication',
                'vulnerability', 'penetration testing', 'cybersecurity'
            ],
            'Educational': [
                'tutorial', 'learning', 'course', 'educational', 'teaching',
                'example', 'demo', 'workshop', 'guide'
            ]
        }
        
        best_match = None
        best_score = 0.0
        
        for category, indicators in description_indicators.items():
            score = 0.0
            matched_indicators = []
            
            for indicator in indicators:
                if indicator in description:
                    score += 0.3
                    matched_indicators.append(indicator)
            
            if score > best_score:
                best_score = score
                best_match = CategoryMatch(
                    category=category,
                    confidence=min(0.8, score),  # Cap at 0.8 for description alone
                    reasons=[f"desc_indicator:{ind}" for ind in matched_indicators]
                )
        
        return best_match
    
    def _classify_by_topics(self, signals: Dict) -> Optional[CategoryMatch]:
        """Classify repository based on GitHub topics."""
        topics = signals['topics']
        if not topics:
            return None
        
        # Topics are very reliable signals
        topic_mappings = {
            'Web Development': [
                'javascript', 'typescript', 'react', 'vue', 'angular', 'nodejs',
                'web', 'frontend', 'backend', 'html', 'css', 'webapp'
            ],
            'Mobile Development': [
                'android', 'ios', 'mobile', 'react-native', 'flutter', 'ionic',
                'swift', 'kotlin'
            ],
            'Data Science & AI': [
                'machine-learning', 'deep-learning', 'artificial-intelligence',
                'data-science', 'ml', 'ai', 'neural-network', 'tensorflow',
                'pytorch', 'scikit-learn'
            ],
            'DevOps & Infrastructure': [
                'devops', 'docker', 'kubernetes', 'terraform', 'ansible',
                'infrastructure', 'ci-cd', 'monitoring'
            ],
            'Security & Privacy': [
                'security', 'privacy', 'cryptography', 'encryption',
                'cybersecurity', 'infosec'
            ],
            'Game Development': [
                'game', 'gamedev', 'unity', 'unreal', 'godot', 'gaming'
            ],
            'CLI Tools': [
                'cli', 'command-line', 'terminal', 'shell', 'tool', 'utility'
            ]
        }
        
        category_scores = defaultdict(float)
        all_matches = []
        
        for topic in topics:
            for category, topic_list in topic_mappings.items():
                if topic in topic_list:
                    category_scores[category] += 0.7  # Topics are highly reliable
                    all_matches.append(f"topic:{topic}")
        
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            category, score = best_category
            
            return CategoryMatch(
                category=category,
                confidence=min(1.0, score),
                reasons=all_matches
            )
        
        return None
    
    def get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of categories from cached results."""
        distribution = Counter()
        
        for cached in self.category_cache.values():
            distribution[cached['category']] += 1
        
        return dict(distribution)
    
    def clear_cache(self):
        """Clear the categorization cache."""
        self.category_cache.clear()
        logger.info("Categorization cache cleared")
