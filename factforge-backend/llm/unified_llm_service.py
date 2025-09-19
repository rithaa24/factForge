"""
Unified LLM service that can switch between Vertex AI and Ollama
"""
import os
import logging
from typing import Dict, Any, List, Optional
from .vertex_ai_service import get_vertex_ai_service, generate_fact_check_response as vertex_fact_check, generate_mini_lesson as vertex_mini_lesson
from .llm_service import get_ollama_service, generate_fact_check_response as ollama_fact_check, generate_mini_lesson as ollama_mini_lesson

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedLLMService:
    """Unified LLM service that can use either Vertex AI or Ollama"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "vertex_ai")
        self.vertex_ai_service = None
        self.ollama_service = None
        
        # Initialize services based on provider
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize the appropriate LLM service"""
        try:
            if self.provider == "vertex_ai":
                self.vertex_ai_service = get_vertex_ai_service()
                if self.vertex_ai_service.is_available():
                    logger.info("Using Vertex AI as LLM provider")
                else:
                    logger.warning("Vertex AI not available, falling back to Ollama")
                    self.provider = "ollama"
                    self.ollama_service = get_ollama_service()
            else:
                self.ollama_service = get_ollama_service()
                if self.ollama_service.is_available():
                    logger.info("Using Ollama as LLM provider")
                else:
                    logger.warning("Ollama not available, trying Vertex AI")
                    self.provider = "vertex_ai"
                    self.vertex_ai_service = get_vertex_ai_service()
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            # Try fallback
            if self.provider == "vertex_ai":
                logger.info("Falling back to Ollama")
                self.provider = "ollama"
                self.ollama_service = get_ollama_service()
            else:
                logger.info("Falling back to Vertex AI")
                self.provider = "vertex_ai"
                self.vertex_ai_service = get_vertex_ai_service()
    
    def is_available(self) -> bool:
        """Check if any LLM service is available"""
        if self.provider == "vertex_ai" and self.vertex_ai_service:
            return self.vertex_ai_service.is_available()
        elif self.provider == "ollama" and self.ollama_service:
            return self.ollama_service.is_available()
        return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        return {
            "provider": self.provider,
            "available": self.is_available(),
            "vertex_ai_available": self.vertex_ai_service.is_available() if self.vertex_ai_service else False,
            "ollama_available": self.ollama_service.is_available() if self.ollama_service else False
        }
    
    def generate_fact_check_response(self, claim: str, evidence: List[Dict[str, Any]], 
                                   language: str = "en") -> Dict[str, Any]:
        """Generate fact-check response using the configured provider"""
        try:
            if self.provider == "vertex_ai" and self.vertex_ai_service and self.vertex_ai_service.is_available():
                return self.vertex_ai_service.generate_fact_check_response(claim, evidence, language)
            elif self.provider == "ollama" and self.ollama_service and self.ollama_service.is_available():
                return self.ollama_service.generate_fact_check_response(claim, evidence, language)
            else:
                # Fallback to available service
                if self.vertex_ai_service and self.vertex_ai_service.is_available():
                    logger.info("Using Vertex AI as fallback")
                    return self.vertex_ai_service.generate_fact_check_response(claim, evidence, language)
                elif self.ollama_service and self.ollama_service.is_available():
                    logger.info("Using Ollama as fallback")
                    return self.ollama_service.generate_fact_check_response(claim, evidence, language)
                else:
                    logger.error("No LLM service available")
                    return self._get_fallback_response()
        except Exception as e:
            logger.error(f"Error generating fact-check response: {e}")
            return self._get_fallback_response()
    
    def generate_mini_lesson(self, claim: str, verdict: str, evidence: List[Dict[str, Any]], 
                           language: str = "en") -> Dict[str, Any]:
        """Generate mini lesson using the configured provider"""
        try:
            if self.provider == "vertex_ai" and self.vertex_ai_service and self.vertex_ai_service.is_available():
                return self.vertex_ai_service.generate_mini_lesson(claim, verdict, evidence, language)
            elif self.provider == "ollama" and self.ollama_service and self.ollama_service.is_available():
                return self.ollama_service.generate_mini_lesson(claim, verdict, evidence, language)
            else:
                # Fallback to available service
                if self.vertex_ai_service and self.vertex_ai_service.is_available():
                    logger.info("Using Vertex AI as fallback for mini lesson")
                    return self.vertex_ai_service.generate_mini_lesson(claim, verdict, evidence, language)
                elif self.ollama_service and self.ollama_service.is_available():
                    logger.info("Using Ollama as fallback for mini lesson")
                    return self.ollama_service.generate_mini_lesson(claim, verdict, evidence, language)
                else:
                    logger.error("No LLM service available for mini lesson")
                    return self._get_fallback_mini_lesson()
        except Exception as e:
            logger.error(f"Error generating mini lesson: {e}")
            return self._get_fallback_mini_lesson()
    
    def _get_fallback_response(self) -> Dict[str, Any]:
        """Get fallback response when no LLM service is available"""
        return {
            "verdict": "UNVERIFIED",
            "trust_score": 0,
            "reasons": ["LLM service unavailable"],
            "evidence_list": [],
            "confidence": 0,
            "one_line_tip": "Please verify this information from reliable sources"
        }
    
    def _get_fallback_mini_lesson(self) -> Dict[str, Any]:
        """Get fallback mini lesson when no LLM service is available"""
        return {
            "mini_lesson": "Unable to generate lesson at this time. Please verify information from reliable sources.",
            "tips": ["Verify information from reliable sources", "Check multiple sources"],
            "quiz": {
                "question": "What should you do when you see suspicious claims?",
                "options": ["A) Share immediately", "B) Verify first", "C) Ignore"],
                "answer": "B"
            }
        }
    
    def switch_provider(self, new_provider: str) -> bool:
        """Switch to a different LLM provider"""
        try:
            old_provider = self.provider
            self.provider = new_provider
            self._initialize_services()
            
            if self.is_available():
                logger.info(f"Successfully switched from {old_provider} to {new_provider}")
                return True
            else:
                logger.error(f"Failed to switch to {new_provider}, reverting to {old_provider}")
                self.provider = old_provider
                self._initialize_services()
                return False
        except Exception as e:
            logger.error(f"Error switching provider: {e}")
            return False

# Global service instance
_unified_llm_service = None

def get_unified_llm_service() -> UnifiedLLMService:
    """Get the global unified LLM service instance"""
    global _unified_llm_service
    if _unified_llm_service is None:
        _unified_llm_service = UnifiedLLMService()
    return _unified_llm_service

def generate_fact_check_response(claim: str, evidence: List[Dict[str, Any]], 
                               language: str = "en") -> Dict[str, Any]:
    """Generate fact-check response (convenience function)"""
    service = get_unified_llm_service()
    return service.generate_fact_check_response(claim, evidence, language)

def generate_mini_lesson(claim: str, verdict: str, evidence: List[Dict[str, Any]], 
                        language: str = "en") -> Dict[str, Any]:
    """Generate mini lesson (convenience function)"""
    service = get_unified_llm_service()
    return service.generate_mini_lesson(claim, verdict, evidence, language)

def get_llm_provider_info() -> Dict[str, Any]:
    """Get LLM provider information (convenience function)"""
    service = get_unified_llm_service()
    return service.get_provider_info()

def switch_llm_provider(provider: str) -> bool:
    """Switch LLM provider (convenience function)"""
    service = get_unified_llm_service()
    return service.switch_provider(provider)
