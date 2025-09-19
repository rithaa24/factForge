"""
Google Vertex AI service for FactForge backend
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import time
from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VertexAIService:
    """Service for interacting with Google Vertex AI"""
    
    def __init__(self, project_id: str = None, location: str = None, credentials_path: str = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location or os.getenv("GCP_REGION", "us-central1")
        self.credentials_path = credentials_path or os.getenv("GCP_CREDENTIALS_PATH")
        self.model_name = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-pro")
        
        # Initialize Vertex AI
        self._initialize_vertex_ai()
        
        # Load model
        self.model = None
        self._load_model()
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with credentials"""
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                vertexai.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=credentials
                )
            else:
                # Use default credentials (ADC)
                vertexai.init(
                    project=self.project_id,
                    location=self.location
                )
            
            logger.info(f"Vertex AI initialized for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise
    
    def _load_model(self):
        """Load the generative model"""
        try:
            self.model = GenerativeModel(self.model_name)
            logger.info(f"Vertex AI model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load Vertex AI model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Vertex AI service is available"""
        try:
            return self.model is not None
        except Exception as e:
            logger.error(f"Vertex AI service not available: {e}")
            return False
    
    def generate_text(self, prompt: str, temperature: float = 0.1, max_tokens: int = 1000) -> str:
        """Generate text using Vertex AI"""
        if not self.model:
            logger.error("Model not loaded")
            return ""
        
        try:
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.8,
                "top_k": 40
            }
            
            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            return response.text if response.text else ""
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            return ""
    
    def generate_json(self, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Generate JSON response using Vertex AI"""
        # Add JSON formatting instruction to prompt
        json_prompt = f"""Please respond with valid JSON only. No other text.

{prompt}

Response (JSON only):"""
        
        response_text = self.generate_text(json_prompt, temperature)
        
        if not response_text:
            return {}
        
        try:
            # Try to parse JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx+1]
                    return json.loads(json_str)
            except:
                pass
            
            logger.error(f"Failed to parse JSON from response: {response_text}")
            return {}
    
    def generate_fact_check_response(self, claim: str, evidence: List[Dict[str, Any]], 
                                   language: str = "en") -> Dict[str, Any]:
        """Generate fact-check response using Vertex AI"""
        
        # Build evidence text
        evidence_text = ""
        for i, item in enumerate(evidence, 1):
            evidence_text += f"{i}. {item.get('text', '')} (Source: {item.get('url', 'Unknown')})\n"
        
        # Create prompt based on language
        if language == "hi":
            prompt = f"""आप एक तथ्य-जांच विशेषज्ञ हैं। निम्नलिखित दावे और साक्ष्य का विश्लेषण करें:

दावा: {claim}

साक्ष्य:
{evidence_text}

कृपया निम्नलिखित JSON प्रारूप में उत्तर दें:
{{
    "verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIED" | "PARTIALLY TRUE",
    "trust_score": 0-100,
    "reasons": ["कारण 1", "कारण 2"],
    "evidence_list": ["साक्ष्य 1", "साक्ष्य 2"],
    "confidence": 0-100,
    "one_line_tip": "एक पंक्ति का सुझाव"
}}"""
        elif language == "ta":
            prompt = f"""நீங்கள் ஒரு உண்மை சரிபார்ப்பு நிபுணர். பின்வரும் கூற்று மற்றும் சான்றுகளை பகுப்பாய்வு செய்யுங்கள்:

கூற்று: {claim}

சான்றுகள்:
{evidence_text}

தயவுசெய்து பின்வரும் JSON வடிவத்தில் பதிலளிக்கவும்:
{{
    "verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIED" | "PARTIALLY TRUE",
    "trust_score": 0-100,
    "reasons": ["காரணம் 1", "காரணம் 2"],
    "evidence_list": ["சான்று 1", "சான்று 2"],
    "confidence": 0-100,
    "one_line_tip": "ஒரு வரி உதவி"
}}"""
        elif language == "kn":
            prompt = f"""ನೀವು ಸತ್ಯ ಪರಿಶೀಲನಾ ತಜ್ಞ. ಕೆಳಗಿನ ಹೇಳಿಕೆ ಮತ್ತು ಪುರಾವೆಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಿ:

ಹೇಳಿಕೆ: {claim}

ಪುರಾವೆಗಳು:
{evidence_text}

ದಯವಿಟ್ಟು ಕೆಳಗಿನ JSON ಸ್ವರೂಪದಲ್ಲಿ ಉತ್ತರಿಸಿ:
{{
    "verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIED" | "PARTIALLY TRUE",
    "trust_score": 0-100,
    "reasons": ["ಕಾರಣ 1", "ಕಾರಣ 2"],
    "evidence_list": ["ಪುರಾವೆ 1", "ಪುರಾವೆ 2"],
    "confidence": 0-100,
    "one_line_tip": "ಒಂದು ಸಾಲಿನ ಸಲಹೆ"
}}"""
        else:  # English
            prompt = f"""You are a fact-checking expert. Analyze the following claim and evidence:

Claim: {claim}

Evidence:
{evidence_text}

Please respond in the following JSON format:
{{
    "verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIED" | "PARTIALLY TRUE",
    "trust_score": 0-100,
    "reasons": ["reason 1", "reason 2"],
    "evidence_list": ["evidence 1", "evidence 2"],
    "confidence": 0-100,
    "one_line_tip": "One line tip"
}}"""
        
        # Generate response
        response = self.generate_json(prompt, temperature=0.1)
        
        # Validate and set defaults
        if not response:
            response = {
                "verdict": "UNVERIFIED",
                "trust_score": 0,
                "reasons": ["Unable to process claim"],
                "evidence_list": [],
                "confidence": 0,
                "one_line_tip": "Please verify this information from reliable sources"
            }
        
        # Ensure required fields exist
        response.setdefault("verdict", "UNVERIFIED")
        response.setdefault("trust_score", 0)
        response.setdefault("reasons", [])
        response.setdefault("evidence_list", [])
        response.setdefault("confidence", 0)
        response.setdefault("one_line_tip", "Please verify this information")
        
        return response
    
    def generate_mini_lesson(self, claim: str, verdict: str, evidence: List[Dict[str, Any]], 
                           language: str = "en") -> Dict[str, Any]:
        """Generate mini lesson using Vertex AI"""
        
        # Build evidence text
        evidence_text = ""
        for i, item in enumerate(evidence, 1):
            evidence_text += f"{i}. {item.get('text', '')}\n"
        
        # Create prompt based on language
        if language == "hi":
            prompt = f"""आप एक शिक्षक हैं। निम्नलिखित दावे के बारे में एक संक्षिप्त पाठ (20-45 सेकंड पढ़ने योग्य) बनाएं:

दावा: {claim}
निर्णय: {verdict}

साक्ष्य:
{evidence_text}

कृपया निम्नलिखित JSON प्रारूप में उत्तर दें:
{{
    "mini_lesson": "संक्षिप्त पाठ (1 पैराग्राफ)",
    "tips": ["सुझाव 1", "सुझाव 2"],
    "quiz": {{
        "question": "प्रश्न",
        "options": ["A", "B", "C"],
        "answer": "A"
    }}
}}"""
        elif language == "ta":
            prompt = f"""நீங்கள் ஒரு ஆசிரியர். பின்வரும் கூற்று பற்றி ஒரு சுருக்கமான பாடம் (20-45 வினாடிகள் படிக்கக்கூடியது) உருவாக்குங்கள்:

கூற்று: {claim}
தீர்ப்பு: {verdict}

சான்றுகள்:
{evidence_text}

தயவுசெய்து பின்வரும் JSON வடிவத்தில் பதிலளிக்கவும்:
{{
    "mini_lesson": "சுருக்கமான பாடம் (1 பத்தி)",
    "tips": ["உதவி 1", "உதவி 2"],
    "quiz": {{
        "question": "கேள்வி",
        "options": ["A", "B", "C"],
        "answer": "A"
    }}
}}"""
        elif language == "kn":
            prompt = f"""ನೀವು ಶಿಕ್ಷಕ. ಕೆಳಗಿನ ಹೇಳಿಕೆಯ ಬಗ್ಗೆ ಸಂಕ್ಷಿಪ್ತ ಪಾಠ (20-45 ಸೆಕೆಂಡುಗಳು ಓದಲು) ರಚಿಸಿ:

ಹೇಳಿಕೆ: {claim}
ನಿರ್ಣಯ: {verdict}

ಪುರಾವೆಗಳು:
{evidence_text}

ದಯವಿಟ್ಟು ಕೆಳಗಿನ JSON ಸ್ವರೂಪದಲ್ಲಿ ಉತ್ತರಿಸಿ:
{{
    "mini_lesson": "ಸಂಕ್ಷಿಪ್ತ ಪಾಠ (1 ಪ್ಯಾರಾಗ್ರಾಫ್)",
    "tips": ["ಸಲಹೆ 1", "ಸಲಹೆ 2"],
    "quiz": {{
        "question": "ಪ್ರಶ್ನೆ",
        "options": ["A", "B", "C"],
        "answer": "A"
    }}
}}"""
        else:  # English
            prompt = f"""You are a teacher. Create a brief lesson (20-45 seconds readable) about the following claim:

Claim: {claim}
Verdict: {verdict}

Evidence:
{evidence_text}

Please respond in the following JSON format:
{{
    "mini_lesson": "Brief lesson (1 paragraph)",
    "tips": ["tip 1", "tip 2"],
    "quiz": {{
        "question": "Question",
        "options": ["A", "B", "C"],
        "answer": "A"
    }}
}}"""
        
        # Generate response
        response = self.generate_json(prompt, temperature=0.2)
        
        # Validate and set defaults
        if not response:
            response = {
                "mini_lesson": "Unable to generate lesson at this time.",
                "tips": ["Verify information from reliable sources"],
                "quiz": {
                    "question": "What should you do when you see suspicious claims?",
                    "options": ["A) Share immediately", "B) Verify first", "C) Ignore"],
                    "answer": "B"
                }
            }
        
        # Ensure required fields exist
        response.setdefault("mini_lesson", "Unable to generate lesson at this time.")
        response.setdefault("tips", ["Verify information from reliable sources"])
        response.setdefault("quiz", {
            "question": "What should you do when you see suspicious claims?",
            "options": ["A) Share immediately", "B) Verify first", "C) Ignore"],
            "answer": "B"
        })
        
        return response

# Global service instance
_vertex_ai_service = None

def get_vertex_ai_service() -> VertexAIService:
    """Get the global Vertex AI service instance"""
    global _vertex_ai_service
    if _vertex_ai_service is None:
        _vertex_ai_service = VertexAIService()
    return _vertex_ai_service

def generate_fact_check_response(claim: str, evidence: List[Dict[str, Any]], 
                               language: str = "en") -> Dict[str, Any]:
    """Generate fact-check response (convenience function)"""
    service = get_vertex_ai_service()
    return service.generate_fact_check_response(claim, evidence, language)

def generate_mini_lesson(claim: str, verdict: str, evidence: List[Dict[str, Any]], 
                        language: str = "en") -> Dict[str, Any]:
    """Generate mini lesson (convenience function)"""
    service = get_vertex_ai_service()
    return service.generate_mini_lesson(claim, verdict, evidence, language)
