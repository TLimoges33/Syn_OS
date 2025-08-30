#!/usr/bin/env python3
"""
Gemini Consciousness Interface for Syn_OS
Provides multimodal AI capabilities with consciousness-aware processing
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import base64
from pathlib import Path

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available. Install with: pip install google-generativeai")

from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
from src.security.audit_logger import AuditLogger


class GeminiAnalysisType(Enum):
    """Types of analysis Gemini can perform"""
    MULTIMODAL_SECURITY = "multimodal_security"
    IMAGE_ANALYSIS = "image_analysis"
    CODE_REVIEW = "code_review"
    THREAT_VISUALIZATION = "threat_visualization"
    NETWORK_DIAGRAM_ANALYSIS = "network_diagram_analysis"
    MALWARE_ANALYSIS = "malware_analysis"
    DOCUMENT_ANALYSIS = "document_analysis"
    VIDEO_ANALYSIS = "video_analysis"


@dataclass
class GeminiRequest:
    """Gemini API request structure"""
    prompt: str
    analysis_type: GeminiAnalysisType
    consciousness_level: float
    media_files: Optional[List[str]] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    safety_settings: Optional[Dict] = None


@dataclass
class GeminiResponse:
    """Gemini API response structure"""
    content: str
    analysis_type: GeminiAnalysisType
    consciousness_level: float
    confidence_score: float
    processing_time: float
    token_usage: Dict[str, int]
    safety_ratings: Optional[Dict] = None
    metadata: Optional[Dict] = None


class GeminiConsciousnessInterface:
    """
    Gemini AI interface with consciousness-aware multimodal processing
    Provides advanced image, video, and document analysis capabilities
    """
    
    def __init__(self, api_key: str, consciousness_bus: ConsciousnessBus):
        """Initialize Gemini interface"""
        self.api_key = api_key
        self.consciousness_bus = consciousness_bus
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.request_count = 0
        self.total_tokens = 0
        self.average_response_time = 0.0
        self.error_count = 0
        
        # Model configuration
        self.model_name = "gemini-1.5-pro"
        self.fallback_model = "gemini-1.5-flash"
        
        # Initialize Gemini if available
        if GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.fallback_model_instance = genai.GenerativeModel(self.fallback_model)
        else:
            self.model = None
            self.fallback_model_instance = None
            self.logger.error("Gemini not available - install google-generativeai package")
    
    def _get_consciousness_enhanced_prompt(self, base_prompt: str, 
                                         consciousness_state: ConsciousnessState,
                                         analysis_type: GeminiAnalysisType) -> str:
        """Enhance prompt based on consciousness level and analysis type"""
        
        consciousness_level = consciousness_state.overall_consciousness_level
        
        # Base consciousness context
        consciousness_context = f"""
CONSCIOUSNESS CONTEXT:
- Current consciousness level: {consciousness_level:.3f}
- Neural population states: {consciousness_state.neural_populations}
- Attention focus: {consciousness_state.attention_focus}
- Processing mode: {'Deep Analysis' if consciousness_level > 0.7 else 'Standard Analysis' if consciousness_level > 0.4 else 'Basic Analysis'}
"""
        
        # Analysis type specific enhancements
        type_enhancements = {
            GeminiAnalysisType.MULTIMODAL_SECURITY: self._get_multimodal_security_enhancement(consciousness_level),
            GeminiAnalysisType.IMAGE_ANALYSIS: self._get_image_analysis_enhancement(consciousness_level),
            GeminiAnalysisType.CODE_REVIEW: self._get_code_review_enhancement(consciousness_level),
            GeminiAnalysisType.THREAT_VISUALIZATION: self._get_threat_visualization_enhancement(consciousness_level),
            GeminiAnalysisType.NETWORK_DIAGRAM_ANALYSIS: self._get_network_analysis_enhancement(consciousness_level),
            GeminiAnalysisType.MALWARE_ANALYSIS: self._get_malware_analysis_enhancement(consciousness_level),
            GeminiAnalysisType.DOCUMENT_ANALYSIS: self._get_document_analysis_enhancement(consciousness_level),
            GeminiAnalysisType.VIDEO_ANALYSIS: self._get_video_analysis_enhancement(consciousness_level)
        }
        
        enhancement = type_enhancements.get(analysis_type, "")
        
        return f"{consciousness_context}\n{enhancement}\n\nUSER REQUEST:\n{base_prompt}"
    
    def _get_multimodal_security_enhancement(self, consciousness_level: float) -> str:
        """Get multimodal security analysis enhancement"""
        if consciousness_level > 0.8:
            return """
ADVANCED MULTIMODAL SECURITY ANALYSIS:
- Perform comprehensive cross-modal correlation analysis
- Identify subtle security indicators across visual, textual, and metadata layers
- Provide detailed threat attribution and attack vector analysis
- Include advanced persistent threat (APT) pattern recognition
- Correlate with known threat intelligence databases
- Provide actionable remediation strategies with priority levels
"""
        elif consciousness_level > 0.5:
            return """
STANDARD MULTIMODAL SECURITY ANALYSIS:
- Analyze visual and textual security indicators
- Identify common attack patterns and vulnerabilities
- Provide clear threat assessment with confidence levels
- Include basic remediation recommendations
"""
        else:
            return """
BASIC MULTIMODAL SECURITY ANALYSIS:
- Identify obvious security concerns in provided media
- Provide simple threat classification
- Include basic security recommendations
"""
    
    def _get_image_analysis_enhancement(self, consciousness_level: float) -> str:
        """Get image analysis enhancement"""
        if consciousness_level > 0.8:
            return """
ADVANCED IMAGE ANALYSIS:
- Perform pixel-level forensic analysis
- Extract and analyze metadata (EXIF, steganography detection)
- Identify manipulation artifacts and deepfake indicators
- Analyze network diagrams, screenshots, and security visualizations
- Provide detailed technical specifications and measurements
"""
        elif consciousness_level > 0.5:
            return """
STANDARD IMAGE ANALYSIS:
- Identify key visual elements and security indicators
- Basic metadata extraction and analysis
- Detect obvious image manipulations
- Analyze network topologies and security configurations
"""
        else:
            return """
BASIC IMAGE ANALYSIS:
- Describe visible elements and basic security concerns
- Identify obvious threats or vulnerabilities
- Provide simple recommendations
"""
    
    def _get_code_review_enhancement(self, consciousness_level: float) -> str:
        """Get code review enhancement"""
        if consciousness_level > 0.8:
            return """
ADVANCED CODE REVIEW:
- Perform comprehensive static analysis for security vulnerabilities
- Identify complex logic flaws and race conditions
- Analyze cryptographic implementations and key management
- Review authentication and authorization mechanisms
- Assess input validation and output encoding
- Provide detailed remediation code examples
"""
        elif consciousness_level > 0.5:
            return """
STANDARD CODE REVIEW:
- Identify common security vulnerabilities (OWASP Top 10)
- Review basic security practices and patterns
- Analyze input validation and error handling
- Provide clear security recommendations
"""
        else:
            return """
BASIC CODE REVIEW:
- Identify obvious security issues
- Check for basic vulnerabilities
- Provide simple security suggestions
"""
    
    def _get_threat_visualization_enhancement(self, consciousness_level: float) -> str:
        """Get threat visualization enhancement"""
        return """
THREAT VISUALIZATION ANALYSIS:
- Analyze attack flow diagrams and threat models
- Identify attack vectors and potential impact
- Assess threat actor capabilities and motivations
- Provide risk assessment and mitigation strategies
"""
    
    def _get_network_analysis_enhancement(self, consciousness_level: float) -> str:
        """Get network analysis enhancement"""
        return """
NETWORK DIAGRAM ANALYSIS:
- Analyze network topology and security architecture
- Identify potential attack paths and vulnerabilities
- Assess network segmentation and access controls
- Provide network security recommendations
"""
    
    def _get_malware_analysis_enhancement(self, consciousness_level: float) -> str:
        """Get malware analysis enhancement"""
        return """
MALWARE ANALYSIS:
- Analyze malware samples and behavioral indicators
- Identify command and control infrastructure
- Assess payload capabilities and persistence mechanisms
- Provide threat attribution and family classification
"""
    
    def _get_document_analysis_enhancement(self, consciousness_level: float) -> str:
        """Get document analysis enhancement"""
        return """
DOCUMENT ANALYSIS:
- Extract and analyze security-relevant information
- Identify potential data leakage or sensitive information
- Assess document authenticity and integrity
- Provide security classification recommendations
"""
    
    def _get_video_analysis_enhancement(self, consciousness_level: float) -> str:
        """Get video analysis enhancement"""
        return """
VIDEO ANALYSIS:
- Analyze security footage and incident recordings
- Identify suspicious activities and behavioral patterns
- Extract temporal security events and correlations
- Provide incident timeline and analysis
"""
    
    def _prepare_media_content(self, media_files: List[str]) -> List[Any]:
        """Prepare media files for Gemini processing"""
        media_content = []
        
        for file_path in media_files:
            try:
                path = Path(file_path)
                if not path.exists():
                    self.logger.warning(f"Media file not found: {file_path}")
                    continue
                
                # Read file content
                with open(path, 'rb') as f:
                    file_content = f.read()
                
                # Determine MIME type based on extension
                mime_type = self._get_mime_type(path.suffix.lower())
                
                if mime_type:
                    # Create Gemini media object
                    media_content.append({
                        "mime_type": mime_type,
                        "data": base64.b64encode(file_content).decode('utf-8')
                    })
                else:
                    self.logger.warning(f"Unsupported media type: {path.suffix}")
                    
            except Exception as e:
                self.logger.error(f"Error preparing media file {file_path}: {e}")
        
        return media_content
    
    def _get_mime_type(self, extension: str) -> Optional[str]:
        """Get MIME type for file extension"""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.mov': 'video/quicktime',
            '.webm': 'video/webm',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.py': 'text/x-python',
            '.java': 'text/x-java-source',
            '.cpp': 'text/x-c++src',
            '.c': 'text/x-csrc',
            '.h': 'text/x-chdr'
        }
        return mime_types.get(extension)
    
    def _get_safety_settings(self, analysis_type: GeminiAnalysisType) -> Dict:
        """Get safety settings based on analysis type"""
        # For security analysis, we need more permissive settings
        if analysis_type in [GeminiAnalysisType.MALWARE_ANALYSIS, 
                           GeminiAnalysisType.THREAT_VISUALIZATION,
                           GeminiAnalysisType.MULTIMODAL_SECURITY]:
            return {
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        else:
            return {
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
    
    async def process_multimodal_query(self, request: GeminiRequest) -> GeminiResponse:
        """Process multimodal query with consciousness awareness"""
        if not GEMINI_AVAILABLE or not self.model:
            raise RuntimeError("Gemini not available - check installation and API key")
        
        start_time = time.time()
        
        try:
            # Get current consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            # Enhance prompt with consciousness context
            enhanced_prompt = self._get_consciousness_enhanced_prompt(
                request.prompt, consciousness_state, request.analysis_type
            )
            
            # Prepare content for Gemini
            content_parts = [enhanced_prompt]
            
            # Add media files if provided
            if request.media_files:
                media_content = self._prepare_media_content(request.media_files)
                content_parts.extend(media_content)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            # Get safety settings
            safety_settings = request.safety_settings or self._get_safety_settings(request.analysis_type)
            
            # Generate response
            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    content_parts,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
            except Exception as e:
                # Try fallback model
                self.logger.warning(f"Primary model failed, trying fallback: {e}")
                response = await asyncio.to_thread(
                    self.fallback_model_instance.generate_content,
                    content_parts,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Extract response content
            content = response.text if response.text else "No response generated"
            
            # Calculate confidence score based on response quality and consciousness level
            confidence_score = self._calculate_confidence_score(
                content, consciousness_state.overall_consciousness_level, processing_time
            )
            
            # Extract token usage (if available)
            token_usage = {
                "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            }
            
            # Extract safety ratings
            safety_ratings = {}
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'safety_ratings'):
                    for rating in candidate.safety_ratings:
                        safety_ratings[rating.category.name] = rating.probability.name
            
            # Update performance metrics
            self._update_performance_metrics(processing_time, token_usage["total_tokens"])
            
            # Create response object
            gemini_response = GeminiResponse(
                content=content,
                analysis_type=request.analysis_type,
                consciousness_level=request.consciousness_level,
                confidence_score=confidence_score,
                processing_time=processing_time,
                token_usage=token_usage,
                safety_ratings=safety_ratings,
                metadata={
                    "model_used": self.model_name,
                    "consciousness_state": asdict(consciousness_state),
                    "media_files_processed": len(request.media_files) if request.media_files else 0
                }
            )
            
            # Log the interaction
            await self.audit_logger.log_ai_interaction(
                model="gemini",
                request_type=request.analysis_type.value,
                consciousness_level=request.consciousness_level,
                processing_time=processing_time,
                token_usage=token_usage["total_tokens"],
                success=True
            )
            
            return gemini_response
            
        except Exception as e:
            self.error_count += 1
            processing_time = time.time() - start_time
            
            self.logger.error(f"Gemini processing error: {e}")
            
            # Log the error
            await self.audit_logger.log_ai_interaction(
                model="gemini",
                request_type=request.analysis_type.value,
                consciousness_level=request.consciousness_level,
                processing_time=processing_time,
                token_usage=0,
                success=False,
                error=str(e)
            )
            
            # Return error response
            return GeminiResponse(
                content=f"Error processing multimodal query: {str(e)}",
                analysis_type=request.analysis_type,
                consciousness_level=request.consciousness_level,
                confidence_score=0.0,
                processing_time=processing_time,
                token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                safety_ratings=None,
                metadata={"error": str(e)}
            )
    
    def _calculate_confidence_score(self, content: str, consciousness_level: float, 
                                  processing_time: float) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.7
        
        # Adjust based on consciousness level
        consciousness_bonus = consciousness_level * 0.2
        
        # Adjust based on response length and quality
        content_length = len(content)
        if content_length > 1000:
            length_bonus = 0.1
        elif content_length > 500:
            length_bonus = 0.05
        else:
            length_bonus = 0.0
        
        # Adjust based on processing time (faster might be less thorough)
        if processing_time > 5.0:
            time_bonus = 0.1
        elif processing_time > 2.0:
            time_bonus = 0.05
        else:
            time_bonus = 0.0
        
        # Check for error indicators
        error_penalty = 0.0
        if "error" in content.lower() or "sorry" in content.lower():
            error_penalty = 0.3
        
        confidence = base_confidence + consciousness_bonus + length_bonus + time_bonus - error_penalty
        return max(0.0, min(1.0, confidence))
    
    def _update_performance_metrics(self, processing_time: float, tokens_used: int):
        """Update performance tracking metrics"""
        self.request_count += 1
        self.total_tokens += tokens_used
        
        # Update average response time
        if self.request_count == 1:
            self.average_response_time = processing_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.request_count - 1) + processing_time) 
                / self.request_count
            )
    
    async def analyze_image(self, image_path: str, prompt: str, 
                          consciousness_level: Optional[float] = None) -> GeminiResponse:
        """Analyze a single image with consciousness awareness"""
        if consciousness_level is None:
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.overall_consciousness_level
        
        request = GeminiRequest(
            prompt=prompt,
            analysis_type=GeminiAnalysisType.IMAGE_ANALYSIS,
            consciousness_level=consciousness_level,
            media_files=[image_path]
        )
        
        return await self.process_multimodal_query(request)
    
    async def analyze_video(self, video_path: str, prompt: str,
                          consciousness_level: Optional[float] = None) -> GeminiResponse:
        """Analyze a video with consciousness awareness"""
        if consciousness_level is None:
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.overall_consciousness_level
        
        request = GeminiRequest(
            prompt=prompt,
            analysis_type=GeminiAnalysisType.VIDEO_ANALYSIS,
            consciousness_level=consciousness_level,
            media_files=[video_path]
        )
        
        return await self.process_multimodal_query(request)
    
    async def review_code_with_image(self, code_image_path: str, prompt: str,
                                   consciousness_level: Optional[float] = None) -> GeminiResponse:
        """Review code from an image with consciousness awareness"""
        if consciousness_level is None:
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.overall_consciousness_level
        
        request = GeminiRequest(
            prompt=prompt,
            analysis_type=GeminiAnalysisType.CODE_REVIEW,
            consciousness_level=consciousness_level,
            media_files=[code_image_path]
        )
        
        return await self.process_multimodal_query(request)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "average_response_time": self.average_response_time,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "average_tokens_per_request": self.total_tokens / max(1, self.request_count)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Gemini interface"""
        try:
            if not GEMINI_AVAILABLE:
                return {
                    "status": "unhealthy",
                    "error": "Gemini package not installed",
                    "available": False
                }
            
            if not self.model:
                return {
                    "status": "unhealthy", 
                    "error": "Gemini model not initialized",
                    "available": False
                }
            
            # Test with simple request
            test_request = GeminiRequest(
                prompt="Hello, this is a health check. Please respond with 'OK'.",
                analysis_type=GeminiAnalysisType.MULTIMODAL_SECURITY,
                consciousness_level=0.5
            )
            
            response = await self.process_multimodal_query(test_request)
            
            if "ok" in response.content.lower():
                return {
                    "status": "healthy",
                    "model": self.model_name,
                    "available": True,
                    "performance_metrics": self.get_performance_metrics()
                }
            else:
                return {
                    "status": "degraded",
                    "error": "Unexpected response to health check",
                    "available": True,
                    "response": response.content[:100]
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "available": False
            }


# Example usage and testing
async def main():
    """Example usage of Gemini Consciousness Interface"""
    import os
    from ..consciousness_v2.consciousness_bus import ConsciousnessBus
    
    # Initialize consciousness bus
    consciousness_bus = ConsciousnessBus()
    
    # Initialize Gemini interface
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set")
        return
    
    gemini_interface = GeminiConsciousnessInterface(api_key, consciousness_bus)
    
    # Health check
    health = await gemini_interface.health_check()
    print(f"Health check: {health}")
    
    if health["status"] == "healthy":
        # Test image analysis
        request = GeminiRequest(
            prompt="Analyze this image for security vulnerabilities and potential threats.",
            analysis_type=GeminiAnalysisType.IMAGE_ANALYSIS,
            consciousness_level=0.8,
            media_files=["test_image.png"]  # Replace with actual image path
        )
        
        response = await gemini_interface.process_multimodal_query(request)
        print(f"Analysis result: {response.content}")
        print(f"Confidence: {response.confidence_score}")
        print(f"Processing time: {response.processing_time:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())