"""
Helper classes for the Consciousness-Aware Security Tutor V2
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from ..core.data_models import ConsciousnessState, LearningProgressData
from ..core.event_types import EventType


@dataclass
class BrowserContext:
    """Context information from browser analysis"""
    url: str
    title: str
    content_type: str
    difficulty_indicators: List[str]
    progress_markers: List[str]
    interactive_elements: List[Dict[str, Any]]
    consciousness_relevance: float


@dataclass
class PDFAssignmentData:
    """Processed PDF assignment data"""
    title: str
    content: str
    requirements: List[str]
    difficulty_level: str
    topics: List[str]
    due_date: Optional[datetime]
    consciousness_optimization: Dict[str, Any]


class ConsciousnessLearningEngine:
    """Engine for consciousness-aware learning optimization"""
    
    def __init__(self):
        self.learning_patterns = {}
        self.consciousness_correlations = {}
        self.adaptive_algorithms = {}
        self.consciousness_bus = None
    
    async def initialize(self, consciousness_bus):
        """Initialize the learning engine"""
        self.consciousness_bus = consciousness_bus
        logging.info("ConsciousnessLearningEngine initialized")
        
    async def analyze_learning_pattern(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning patterns based on consciousness state"""
        consciousness_level = session_data.get('consciousness_level', 0.5)
        learning_mode = session_data.get('learning_mode', 'exploration')
        
        pattern_analysis = {
            'optimal_difficulty': self._calculate_optimal_difficulty(consciousness_level),
            'learning_velocity': self._calculate_learning_velocity(session_data),
            'retention_prediction': self._predict_retention(consciousness_level, learning_mode),
            'cognitive_load': self._assess_cognitive_load(session_data),
            'adaptation_recommendations': self._generate_adaptations(consciousness_level)
        }
        
        return pattern_analysis
    
    def _calculate_optimal_difficulty(self, consciousness_level: float) -> float:
        """Calculate optimal difficulty based on consciousness level"""
        # Higher consciousness allows for higher difficulty
        base_difficulty = consciousness_level * 0.8
        # Add some challenge factor
        optimal_difficulty = min(base_difficulty + 0.2, 1.0)
        return optimal_difficulty
    
    def _calculate_learning_velocity(self, session_data: Dict[str, Any]) -> float:
        """Calculate current learning velocity"""
        progress_points = session_data.get('progress_history', [])
        if len(progress_points) < 2:
            return 0.5
        
        # Calculate velocity based on recent progress
        recent_progress = progress_points[-5:]  # Last 5 data points
        if len(recent_progress) < 2:
            return 0.5
            
        time_deltas = []
        progress_deltas = []
        
        for i in range(1, len(recent_progress)):
            time_delta = (recent_progress[i][0] - recent_progress[i-1][0]).total_seconds()
            progress_delta = recent_progress[i][1] - recent_progress[i-1][1]
            
            if time_delta > 0:
                time_deltas.append(time_delta)
                progress_deltas.append(progress_delta)
        
        if not time_deltas:
            return 0.5
            
        avg_velocity = sum(p/t for p, t in zip(progress_deltas, time_deltas)) / len(time_deltas)
        return max(0.1, min(avg_velocity, 1.0))
    
    def _predict_retention(self, consciousness_level: float, learning_mode: str) -> float:
        """Predict knowledge retention based on consciousness and mode"""
        base_retention = consciousness_level * 0.7
        
        mode_multipliers = {
            'exploration': 0.8,
            'focused': 1.0,
            'intensive': 1.2,
            'breakthrough': 1.4
        }
        
        multiplier = mode_multipliers.get(learning_mode, 1.0)
        predicted_retention = min(base_retention * multiplier, 1.0)
        
        return predicted_retention
    
    def _assess_cognitive_load(self, session_data: Dict[str, Any]) -> float:
        """Assess current cognitive load"""
        factors = {
            'session_duration': session_data.get('duration_minutes', 0) / 120.0,  # Normalize to 2 hours
            'task_complexity': session_data.get('task_complexity', 0.5),
            'interruptions': len(session_data.get('interruptions', [])) / 10.0,
            'multitasking': session_data.get('multitasking_score', 0.0)
        }
        
        # Weight the factors
        weights = {'session_duration': 0.3, 'task_complexity': 0.4, 'interruptions': 0.2, 'multitasking': 0.1}
        
        cognitive_load = sum(factors[key] * weights[key] for key in factors)
        return max(0.0, min(cognitive_load, 1.0))
    
    def _generate_adaptations(self, consciousness_level: float) -> List[str]:
        """Generate adaptation recommendations"""
        adaptations = []
        
        if consciousness_level < 0.3:
            adaptations.extend([
                "Reduce content complexity",
                "Increase break frequency",
                "Use more visual aids",
                "Provide step-by-step guidance"
            ])
        elif consciousness_level < 0.6:
            adaptations.extend([
                "Maintain current difficulty",
                "Add interactive elements",
                "Provide contextual hints"
            ])
        else:
            adaptations.extend([
                "Increase challenge level",
                "Introduce advanced concepts",
                "Encourage exploration",
                "Provide minimal guidance"
            ])
        
        return adaptations


class AdaptiveContentGenerator:
    """Generates adaptive content based on consciousness state"""
    
    def __init__(self):
        self.content_templates = {}
        self.difficulty_scales = {}
    
    async def initialize(self):
        """Initialize the content generator"""
        logging.info("AdaptiveContentGenerator initialized")
    
    async def generate_consciousness_aware_content(self, topic: str, consciousness_level: float,
                                                 learning_mode: str, platform: str) -> Dict[str, Any]:
        """Generate consciousness-aware content"""
        return await self.generate_content(topic, consciousness_level, learning_mode, platform)
    
    async def generate_assignment_guidance(self, assignment_data: Dict[str, Any],
                                         consciousness_level: float) -> Dict[str, Any]:
        """Generate guidance for assignments"""
        return {
            'suggestions': [
                "Break down the assignment into smaller tasks",
                "Start with the requirements analysis",
                "Create a timeline for completion"
            ],
            'difficulty_adjustment': 'maintain' if consciousness_level > 0.5 else 'reduce',
            'resources': []
        }
    
    async def generate_consciousness_aware_hints(self, context: Dict[str, Any],
                                               consciousness_level: float) -> List[str]:
        """Generate consciousness-aware hints"""
        if consciousness_level < 0.3:
            return [
                "Take your time to understand the problem",
                "Break it down into smaller steps",
                "Don't hesitate to ask for help"
            ]
        elif consciousness_level < 0.6:
            return [
                "Consider multiple approaches",
                "Think about edge cases",
                "Review your methodology"
            ]
        else:
            return [
                "Trust your instincts",
                "Look for creative solutions",
                "Challenge assumptions"
            ]
        
    async def generate_content(self, topic: str, consciousness_level: float, 
                             learning_mode: str, platform: str) -> Dict[str, Any]:
        """Generate adaptive content for the given parameters"""
        
        content_structure = {
            'introduction': await self._generate_introduction(topic, consciousness_level),
            'main_content': await self._generate_main_content(topic, consciousness_level, learning_mode),
            'exercises': await self._generate_exercises(topic, consciousness_level, platform),
            'hints': await self._generate_hints(topic, consciousness_level),
            'resources': await self._generate_resources(topic, learning_mode)
        }
        
        return content_structure
    
    async def _generate_introduction(self, topic: str, consciousness_level: float) -> str:
        """Generate consciousness-appropriate introduction"""
        if consciousness_level < 0.3:
            return f"Let's start with the basics of {topic}. We'll take this step by step."
        elif consciousness_level < 0.6:
            return f"Today we're exploring {topic}. You're ready for some interesting challenges."
        else:
            return f"Time to dive deep into {topic}. Let's push the boundaries of what you know."
    
    async def _generate_main_content(self, topic: str, consciousness_level: float, 
                                   learning_mode: str) -> Dict[str, Any]:
        """Generate main content adapted to consciousness and learning mode"""
        
        complexity_level = self._map_consciousness_to_complexity(consciousness_level)
        
        content = {
            'complexity_level': complexity_level,
            'learning_mode': learning_mode,
            'content_blocks': [],
            'interactive_elements': []
        }
        
        # Generate content blocks based on topic and complexity
        if topic.lower() in ['web security', 'penetration testing', 'ctf']:
            content['content_blocks'] = await self._generate_security_content(topic, complexity_level)
        
        return content
    
    async def _generate_exercises(self, topic: str, consciousness_level: float, 
                                platform: str) -> List[Dict[str, Any]]:
        """Generate platform-specific exercises"""
        exercises = []
        
        difficulty = self._map_consciousness_to_difficulty(consciousness_level)
        
        if platform.lower() == 'hackthebox':
            exercises = await self._generate_htb_exercises(topic, difficulty)
        elif platform.lower() == 'tryhackme':
            exercises = await self._generate_thm_exercises(topic, difficulty)
        elif platform.lower() == 'overthewire':
            exercises = await self._generate_otw_exercises(topic, difficulty)
        
        return exercises
    
    async def _generate_hints(self, topic: str, consciousness_level: float) -> List[str]:
        """Generate consciousness-appropriate hints"""
        if consciousness_level < 0.3:
            return [
                "Take your time and read carefully",
                "Don't hesitate to ask for help",
                "Break the problem into smaller parts"
            ]
        elif consciousness_level < 0.6:
            return [
                "Think about what you've learned before",
                "Consider multiple approaches",
                "Test your assumptions"
            ]
        else:
            return [
                "Trust your instincts",
                "Look for patterns and connections",
                "Challenge conventional approaches"
            ]
    
    async def _generate_resources(self, topic: str, learning_mode: str) -> List[Dict[str, str]]:
        """Generate additional resources based on learning mode"""
        resources = []
        
        if learning_mode == 'exploration':
            resources.extend([
                {'type': 'article', 'title': f'Introduction to {topic}', 'url': '#'},
                {'type': 'video', 'title': f'{topic} Basics', 'url': '#'}
            ])
        elif learning_mode == 'intensive':
            resources.extend([
                {'type': 'documentation', 'title': f'{topic} Reference', 'url': '#'},
                {'type': 'practice', 'title': f'{topic} Lab Environment', 'url': '#'}
            ])
        
        return resources
    
    def _map_consciousness_to_complexity(self, consciousness_level: float) -> str:
        """Map consciousness level to content complexity"""
        if consciousness_level < 0.3:
            return 'basic'
        elif consciousness_level < 0.6:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _map_consciousness_to_difficulty(self, consciousness_level: float) -> str:
        """Map consciousness level to exercise difficulty"""
        if consciousness_level < 0.25:
            return 'easy'
        elif consciousness_level < 0.5:
            return 'medium'
        elif consciousness_level < 0.75:
            return 'hard'
        else:
            return 'insane'
    
    async def _generate_security_content(self, topic: str, complexity_level: str) -> List[Dict[str, Any]]:
        """Generate security-specific content blocks"""
        content_blocks = []
        
        if complexity_level == 'basic':
            content_blocks = [
                {'type': 'concept', 'title': 'What is Security?', 'content': 'Basic security concepts...'},
                {'type': 'example', 'title': 'Simple Example', 'content': 'Here\'s a basic example...'}
            ]
        elif complexity_level == 'intermediate':
            content_blocks = [
                {'type': 'theory', 'title': 'Security Principles', 'content': 'Advanced principles...'},
                {'type': 'practical', 'title': 'Hands-on Practice', 'content': 'Let\'s try this...'}
            ]
        else:
            content_blocks = [
                {'type': 'advanced_theory', 'title': 'Cutting-edge Concepts', 'content': 'Latest research...'},
                {'type': 'complex_scenario', 'title': 'Real-world Challenge', 'content': 'Complex scenario...'}
            ]
        
        return content_blocks
    
    async def _generate_htb_exercises(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate HackTheBox-specific exercises"""
        return [
            {
                'type': 'machine',
                'name': f'{topic.title()} Challenge',
                'difficulty': difficulty,
                'description': f'Practice {topic} skills on this {difficulty} machine'
            }
        ]
    
    async def _generate_thm_exercises(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate TryHackMe-specific exercises"""
        return [
            {
                'type': 'room',
                'name': f'{topic.title()} Room',
                'difficulty': difficulty,
                'description': f'Complete this {difficulty} room focusing on {topic}'
            }
        ]
    
    async def _generate_otw_exercises(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate OverTheWire-specific exercises"""
        return [
            {
                'type': 'wargame',
                'name': f'{topic.title()} Wargame',
                'difficulty': difficulty,
                'description': f'Solve {difficulty} challenges in {topic}'
            }
        ]


class VivaldiBrowserGuidanceSystem:
    """System for providing guidance through Vivaldi browser"""
    
    def __init__(self, vivaldi_path: str):
        self.vivaldi_path = vivaldi_path
        self.driver = None
        self.current_session = None
        self.guidance_overlay = None
        self.active_sessions = {}
    
    async def initialize(self):
        """Initialize the browser guidance system"""
        logging.info("VivaldiBrowserGuidanceSystem initialized")
    
    async def launch_guided_session(self, session_id: str, url: str) -> str:
        """Launch a guided browser session"""
        try:
            success = await self.initialize_browser_session(session_id)
            if success and self.driver:
                self.driver.get(url)
                self.active_sessions[session_id] = {
                    'url': url,
                    'started_at': datetime.now(),
                    'active': True
                }
                return session_id
        except Exception as e:
            logging.error(f"Failed to launch guided session: {e}")
        return None
    
    async def close_browser_session(self, session_id: str):
        """Close a browser session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        await self.close_session()
    
    async def take_screenshot(self, session_id: str) -> Optional[str]:
        """Take a screenshot of the current browser state"""
        if not self.driver or session_id not in self.active_sessions:
            return None
        
        try:
            screenshot_path = f"/tmp/screenshot_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            return screenshot_path
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")
            return None
    
    async def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """Analyze a screenshot for learning context"""
        # Placeholder implementation - would use computer vision in real implementation
        return {
            'content_type': 'unknown',
            'difficulty_indicators': [],
            'interactive_elements': [],
            'guidance_suggestions': ['Continue with current approach']
        }
        
    async def initialize_browser_session(self, session_id: str) -> bool:
        """Initialize a new browser guidance session"""
        if not SELENIUM_AVAILABLE:
            logging.warning("Selenium not available, browser guidance disabled")
            return False
            
        try:
            options = Options()
            options.binary_location = self.vivaldi_path
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            self.driver = webdriver.Chrome(options=options)
            self.current_session = session_id
            
            # Inject guidance overlay script
            await self._inject_guidance_overlay()
            
            return True
        except Exception as e:
            logging.error(f"Failed to initialize browser session: {e}")
            return False
    
    async def analyze_current_page(self) -> BrowserContext:
        """Analyze the current page for learning context"""
        if not self.driver:
            raise RuntimeError("Browser session not initialized")
        
        try:
            url = self.driver.current_url
            title = self.driver.title
            
            # Analyze page content
            content_type = await self._detect_content_type(url, title)
            difficulty_indicators = await self._extract_difficulty_indicators()
            progress_markers = await self._extract_progress_markers()
            interactive_elements = await self._find_interactive_elements()
            consciousness_relevance = await self._calculate_consciousness_relevance(
                content_type, difficulty_indicators
            )
            
            return BrowserContext(
                url=url,
                title=title,
                content_type=content_type,
                difficulty_indicators=difficulty_indicators,
                progress_markers=progress_markers,
                interactive_elements=interactive_elements,
                consciousness_relevance=consciousness_relevance
            )
        except Exception as e:
            logging.error(f"Failed to analyze current page: {e}")
            raise
    
    async def provide_contextual_guidance(self, context: BrowserContext, 
                                        consciousness_level: float) -> Dict[str, Any]:
        """Provide contextual guidance based on page analysis"""
        guidance = {
            'suggestions': [],
            'highlights': [],
            'next_steps': [],
            'difficulty_adjustment': None
        }
        
        # Generate suggestions based on content type
        if context.content_type == 'ctf_challenge':
            guidance['suggestions'] = await self._generate_ctf_guidance(context, consciousness_level)
        elif context.content_type == 'learning_material':
            guidance['suggestions'] = await self._generate_learning_guidance(context, consciousness_level)
        elif context.content_type == 'assignment':
            guidance['suggestions'] = await self._generate_assignment_guidance(context, consciousness_level)
        
        # Highlight important elements
        guidance['highlights'] = await self._generate_highlights(context, consciousness_level)
        
        # Suggest next steps
        guidance['next_steps'] = await self._generate_next_steps(context, consciousness_level)
        
        # Adjust difficulty if needed
        if consciousness_level < 0.3 and context.consciousness_relevance > 0.7:
            guidance['difficulty_adjustment'] = 'reduce'
        elif consciousness_level > 0.7 and context.consciousness_relevance < 0.5:
            guidance['difficulty_adjustment'] = 'increase'
        
        return guidance
    
    async def close_session(self):
        """Close the browser guidance session"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error closing browser session: {e}")
            finally:
                self.driver = None
                self.current_session = None
    
    async def _inject_guidance_overlay(self):
        """Inject JavaScript overlay for guidance display"""
        overlay_script = """
        // Create guidance overlay
        if (!document.getElementById('consciousness-guidance-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'consciousness-guidance-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                width: 300px;
                max-height: 400px;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                font-size: 12px;
                z-index: 10000;
                overflow-y: auto;
                display: none;
            `;
            document.body.appendChild(overlay);
            
            // Add toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.id = 'consciousness-guidance-toggle';
            toggleBtn.innerHTML = '🧠';
            toggleBtn.style.cssText = `
                position: fixed;
                top: 10px;
                right: 320px;
                width: 40px;
                height: 40px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 50%;
                font-size: 20px;
                cursor: pointer;
                z-index: 10001;
            `;
            toggleBtn.onclick = function() {
                const overlay = document.getElementById('consciousness-guidance-overlay');
                overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
            };
            document.body.appendChild(toggleBtn);
        }
        """
        
        try:
            self.driver.execute_script(overlay_script)
        except Exception as e:
            logging.error(f"Failed to inject guidance overlay: {e}")
    
    async def _detect_content_type(self, url: str, title: str) -> str:
        """Detect the type of content on the current page"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if 'hackthebox' in url_lower or 'htb' in url_lower:
            return 'ctf_challenge'
        elif 'tryhackme' in url_lower or 'thm' in url_lower:
            return 'ctf_challenge'
        elif 'overthewire' in url_lower:
            return 'ctf_challenge'
        elif 'freecodecamp' in url_lower:
            return 'learning_material'
        elif 'boot.dev' in url_lower:
            return 'learning_material'
        elif any(keyword in title_lower for keyword in ['assignment', 'homework', 'syllabus']):
            return 'assignment'
        else:
            return 'general'
    
    async def _extract_difficulty_indicators(self) -> List[str]:
        """Extract difficulty indicators from the page"""
        indicators = []
        
        try:
            # Look for common difficulty indicators
            difficulty_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Easy') or contains(text(), 'Medium') or contains(text(), 'Hard') or contains(text(), 'Insane')]")
            
            for element in difficulty_elements:
                text = element.text.strip()
                if text and len(text) < 20:  # Avoid long text blocks
                    indicators.append(text)
        except Exception as e:
            logging.error(f"Failed to extract difficulty indicators: {e}")
        
        return indicators
    
    async def _extract_progress_markers(self) -> List[str]:
        """Extract progress markers from the page"""
        markers = []
        
        try:
            # Look for progress indicators
            progress_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'progress') or contains(@class, 'complete') or contains(@class, 'score')]")
            
            for element in progress_elements:
                text = element.text.strip()
                if text and len(text) < 50:
                    markers.append(text)
        except Exception as e:
            logging.error(f"Failed to extract progress markers: {e}")
        
        return markers
    
    async def _find_interactive_elements(self) -> List[Dict[str, Any]]:
        """Find interactive elements on the page"""
        elements = []
        
        try:
            # Find buttons, inputs, and links
            interactive_selectors = [
                "button", "input[type='submit']", "input[type='button']", 
                "a[href]", "input[type='text']", "textarea"
            ]
            
            for selector in interactive_selectors:
                found_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in found_elements[:5]:  # Limit to first 5 of each type
                    try:
                        elements.append({
                            'type': selector,
                            'text': elem.text[:50] if elem.text else '',
                            'id': elem.get_attribute('id') or '',
                            'class': elem.get_attribute('class') or ''
                        })
                    except:
                        continue
        except Exception as e:
            logging.error(f"Failed to find interactive elements: {e}")
        
        return elements
    
    async def _calculate_consciousness_relevance(self, content_type: str, 
                                               difficulty_indicators: List[str]) -> float:
        """Calculate how relevant the content is to consciousness-aware learning"""
        base_relevance = {
            'ctf_challenge': 0.9,
            'learning_material': 0.8,
            'assignment': 0.7,
            'general': 0.3
        }.get(content_type, 0.3)
        
        # Adjust based on difficulty indicators
        if any('hard' in indicator.lower() or 'insane' in indicator.lower() 
               for indicator in difficulty_indicators):
            base_relevance += 0.1
        elif any('easy' in indicator.lower() for indicator in difficulty_indicators):
            base_relevance -= 0.1
        
        return max(0.0, min(base_relevance, 1.0))
    
    async def _generate_ctf_guidance(self, context: BrowserContext, 
                                   consciousness_level: float) -> List[str]:
        """Generate CTF-specific guidance"""
        suggestions = []
        
        if consciousness_level < 0.3:
            suggestions.extend([
                "Start with reconnaissance - gather information about the target",
                "Take notes of everything you discover",
                "Don't rush - methodical approach works best"
            ])
        elif consciousness_level < 0.6:
            suggestions.extend([
                "Consider multiple attack vectors",
                "Document your methodology",
                "Think about privilege escalation early"
            ])
        else:
            suggestions.extend([
                "Look for unconventional attack paths",
                "Consider chaining multiple vulnerabilities",
                "Trust your intuition about suspicious findings"
            ])
        
        return suggestions
    
    async def _generate_learning_guidance(self, context: BrowserContext, 
                                        consciousness_level: float) -> List[str]:
        """Generate learning material guidance"""
        suggestions = []
        
        if consciousness_level < 0.3:
            suggestions.extend([
                "Take breaks every 25 minutes",
                "Practice each concept before moving on",
                "Don't hesitate to review previous sections"
            ])
        else:
            suggestions.extend([
                "Try to connect concepts to real-world scenarios",
                "Experiment with variations of the examples",
                "Consider the broader implications"
            ])
        
        return suggestions
    
    async def _generate_assignment_guidance(self, context: BrowserContext, 
                                          consciousness_level: float) -> List[str]:
        """Generate assignment-specific guidance"""
        suggestions = []
        
        suggestions.extend([
            "Break the assignment into smaller tasks",
            "Identify the key requirements first",
            "Plan your approach before starting"
        ])
        
        if consciousness_level > 0.6:
            suggestions.append("Consider going beyond the minimum requirements")
        
        return suggestions
    
    async def _generate_highlights(self, context: BrowserContext, 
                                 consciousness_level: float) -> List[str]:
        """Generate elements to highlight on the page"""
        highlights = []
        
        # Highlight based on interactive elements and consciousness level
        for element in context.interactive_elements:
            if element['type'] in ['button', 'input[type="submit"]']:
                highlights.append(f"Action button: {element['text']}")
        
        return highlights
    
    async def _generate_next_steps(self, context: BrowserContext, 
                                 consciousness_level: float) -> List[str]:
        """Generate suggested next steps"""
        next_steps = []
        
        if context.content_type == 'ctf_challenge':
            next_steps.extend([
                "Run initial scans",
                "Analyze the results",
                "Identify potential entry points"
            ])
        elif context.content_type == 'learning_material':
            next_steps.extend([
                "Complete the current section",
                "Test your understanding",
                "Move to practical exercises"
            ])
        
        return next_steps


class PDFAssignmentProcessor:
    """Processes PDF assignments and syllabi for consciousness-aware guidance"""
    
    def __init__(self):
        self.processed_documents = {}
    
    async def initialize(self):
        """Initialize the PDF processor"""
        logging.info("PDFAssignmentProcessor initialized")
    
    async def extract_pdf_content(self, pdf_path: str) -> str:
        """Extract content from PDF file"""
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 not available for PDF processing")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
                return full_text
        except Exception as e:
            logging.error(f"Failed to extract PDF content: {e}")
            raise
    
    async def analyze_assignment(self, content: str, assignment_type: str) -> Dict[str, Any]:
        """Analyze assignment content"""
        analysis = await self._analyze_pdf_content(content)
        analysis['assignment_type'] = assignment_type
        return analysis
        
    async def process_pdf(self, pdf_path: str) -> PDFAssignmentData:
        """Process a PDF assignment or syllabus"""
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 not available for PDF processing")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
                
                # Analyze the content
                analysis = await self._analyze_pdf_content(full_text)
                
                assignment_data = PDFAssignmentData(
                    title=analysis['title'],
                    content=full_text,
                    requirements=analysis['requirements'],
                    difficulty_level=analysis['difficulty_level'],
                    topics=analysis['topics'],
                    due_date=analysis['due_date'],
                    consciousness_optimization=analysis['consciousness_optimization']
                )
                
                # Cache the processed document
                self.processed_documents[pdf_path] = assignment_data
                
                return assignment_data
                
        except Exception as e:
            logging.error(f"Failed to process PDF {pdf_path}: {e}")
            raise
    
    async def _analyze_pdf_content(self, text: str) -> Dict[str, Any]:
        """Analyze PDF content to extract key information"""
        analysis = {
            'title': self._extract_title(text),
            'requirements': self._extract_requirements(text),
            'difficulty_level': self._assess_difficulty(text),
            'topics': self._extract_topics(text),
            'due_date': self._extract_due_date(text),
            'consciousness_optimization': self._generate_consciousness_optimization(text)
        }
        
        return analysis
    
    def _extract_title(self, text: str) -> str:
        """Extract the document title"""
        lines = text.split('\n')
        # Usually the title is in the first few lines
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 100:
                # Skip common headers
                if not any(skip in line.lower() for skip in ['page', 'date', 'name:', 'course']):
                    return line
        
        return "Untitled Document"
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract assignment requirements"""
        requirements = []
        lines = text.split('\n')
        
        in_requirements_section = False
        for line in lines:
            line = line.strip()
            
            # Look for requirements section
            if any(keyword in line.lower() for keyword in ['requirement', 'objective', 'task', 'deliverable']):
                in_requirements_section = True
                continue
            
            if in_requirements_section:
                # Stop if we hit another section
                if line.isupper() and len(line) > 10:
                    break
                
                # Extract numbered or bulleted items
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    requirements.append(line)
                    
                # Limit to reasonable number
                if len(requirements) >= 10:
                    break
        
        return requirements
    
    def _assess_difficulty(self, text: str) -> str:
        """Assess the difficulty level of the assignment"""
        text_lower = text.lower()
        
        # Look for explicit difficulty indicators
        if any(word in text_lower for word in ['advanced', 'complex', 'challenging']):
            return 'advanced'
        elif any(word in text_lower for word in ['intermediate', 'moderate']):
            return 'intermediate'
        elif any(word in text_lower for word in ['basic', 'introductory', 'beginner']):
            return 'basic'
        
        # Assess based on content complexity
        complexity_indicators = [
            'implement', 'design', 'analyze', 'evaluate', 'create', 'develop',
            'algorithm', 'optimization', 'architecture', 'framework'
        ]
        
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in text_lower)
        
        if complexity_score >= 5:
            return 'advanced'
        elif complexity_score >= 2:
            return 'intermediate'
        else:
            return 'basic'
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from the document"""
        topics = []
        text_lower = text.lower()
        
        # Common cybersecurity topics
        security_topics = [
            'web security', 'network security', 'cryptography', 'penetration testing',
            'vulnerability assessment', 'malware analysis', 'forensics', 'incident response',
            'risk assessment', 'compliance', 'authentication', 'authorization',
            'sql injection', 'xss', 'csrf', 'buffer overflow', 'privilege escalation'
        ]
        
        for topic in security_topics:
            if topic in text_lower:
                topics.append(topic.title())
        
        # Extract topics from headings (usually in caps or title case)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.isupper() and 5 < len(line) < 50:
                topics.append(line.title())
        
        return list(set(topics))  # Remove duplicates
    
    def _extract_due_date(self, text: str) -> Optional[datetime]:
        """Extract due date from the document"""
        import re
        
        # Common date patterns
        date_patterns = [
            r'due\s+(?:date\s*:?\s*)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'deadline\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'submit\s+by\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:due|deadline)'
        ]
        
        text_lower = text.lower()
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except:
                    continue
        
        return None
    
    def _generate_consciousness_optimization(self, text: str) -> Dict[str, Any]:
        """Generate consciousness-aware optimization suggestions"""
        text_lower = text.lower()
        
        optimization = {
            'recommended_consciousness_level': 0.6,  # Default
            'learning_mode_suggestions': [],
            'cognitive_load_factors': [],
            'adaptation_strategies': []
        }
        
        # Assess complexity and adjust recommendations
        if any(word in text_lower for word in ['advanced', 'complex', 'research']):
            optimization['recommended_consciousness_level'] = 0.8
            optimization['learning_mode_suggestions'] = ['intensive', 'breakthrough']
            optimization['cognitive_load_factors'] = ['high_complexity', 'abstract_concepts']
        elif any(word in text_lower for word in ['basic', 'introduction', 'overview']):
            optimization['recommended_consciousness_level'] = 0.4
            optimization['learning_mode_suggestions'] = ['exploration', 'focused']
            optimization['cognitive_load_factors'] = ['structured_learning', 'step_by_step']
        else:
            optimization['learning_mode_suggestions'] = ['focused', 'intensive']
            optimization['cognitive_load_factors'] = ['moderate_complexity']
        
        # Add adaptation strategies
        if 'practical' in text_lower or 'hands-on' in text_lower:
            optimization['adaptation_strategies'].append('hands_on_practice')
        if 'theory' in text_lower or 'concept' in text_lower:
            optimization['adaptation_strategies'].append('conceptual_understanding')
        if 'project' in text_lower or 'assignment' in text_lower:
            optimization['adaptation_strategies'].append('project_based_learning')
        
        return optimization