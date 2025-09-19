"""
Fact-checking API endpoints
"""
import time
import uuid
import hashlib
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import requests
import json

from ..core.db import get_db_session, get_redis
from ..core.auth import get_current_user
from ..core.audit import create_audit_entry
from ..core.models import User
from ...llm import get_unified_llm_service, get_llm_provider_info

router = APIRouter()

class CheckRequest(BaseModel):
    claim_text: str = Field(..., min_length=1, max_length=5000)
    language: str = Field(default="auto", regex="^(auto|hi|ta|kn|en)$")
    user_id: Optional[str] = None
    include_translation: bool = Field(default=False)

class CheckResponse(BaseModel):
    request_id: str
    verdict: str
    trust_score: int
    confidence: int
    reasons: list[str]
    evidence_list: list[dict]
    classifier_score: Optional[float] = None
    retrieved_ids: list[str]
    latency_ms: int
    language_detected: Optional[str] = None
    mini_lesson: Optional[dict] = None

def detect_language(text: str) -> tuple[str, float]:
    """
    Detect language using fastText or heuristics
    """
    # Simple heuristic-based language detection
    # In production, use fastText or similar
    
    # Check for Tamil script
    if any('\u0B80' <= char <= '\u0BFF' for char in text):
        return 'ta', 0.9
    
    # Check for Hindi/Devanagari script
    if any('\u0900' <= char <= '\u097F' for char in text):
        return 'hi', 0.9
    
    # Check for Kannada script
    if any('\u0C80' <= char <= '\u0CFF' for char in text):
        return 'kn', 0.9
    
    # Check for English (Latin script with common English words)
    english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
    text_lower = text.lower()
    english_score = sum(1 for word in english_words if word in text_lower) / len(english_words)
    
    if english_score > 0.3:
        return 'en', english_score
    
    # Default to English if uncertain
    return 'en', 0.5

def get_embedding(text: str, language: str) -> list[float]:
    """
    Generate embedding for text using sentence-transformers
    """
    # In production, use sentence-transformers
    # For now, return a dummy embedding
    import hashlib
    hash_obj = hashlib.md5(f"{text}_{language}".encode())
    hash_hex = hash_obj.hexdigest()
    
    # Convert hash to 384-dimensional vector (paraphrase-multilingual-mpnet-base-v2 size)
    embedding = []
    for i in range(0, len(hash_hex), 2):
        val = int(hash_hex[i:i+2], 16) / 255.0  # Normalize to 0-1
        embedding.append(val)
    
    # Pad or truncate to 384 dimensions
    while len(embedding) < 384:
        embedding.append(0.0)
    embedding = embedding[:384]
    
    return embedding

def search_similar_claims(embedding: list[float], language: str, top_k: int = 6) -> list[dict]:
    """
    Search for similar claims in vector database
    """
    # In production, use Milvus vector search
    # For now, return dummy results
    return [
        {
            "id": f"evidence_{i}",
            "url": f"https://example.com/evidence_{i}",
            "title": f"Evidence {i}",
            "snippet": f"This is evidence snippet {i} related to the claim",
            "date": "2024-01-15",
            "language": language,
            "similarity": 0.9 - (i * 0.1)
        }
        for i in range(min(top_k, 3))
    ]

def call_llm_explainer(claim: str, language: str, evidence: list[dict]) -> dict:
    """
    Call LLM service for fact-checking explanation using unified service
    """
    try:
        # Use unified LLM service (Vertex AI or Ollama)
        llm_service = get_unified_llm_service()
        
        # Convert evidence format for LLM service
        evidence_for_llm = [
            {
                "text": f"{item['title']}: {item['snippet']}",
                "url": item.get('url', 'Unknown')
            }
            for item in evidence
        ]
        
        # Generate fact-check response
        result = llm_service.generate_fact_check_response(claim, evidence_for_llm, language)
        
        # Ensure all required fields are present
        result.setdefault("verdict", "UNVERIFIED")
        result.setdefault("trust_score", 0)
        result.setdefault("confidence", 0)
        result.setdefault("reasons", [])
        result.setdefault("evidence_list", evidence)
        result.setdefault("one_line_tip", "Please verify this information independently")
        result.setdefault("suggested_action", "Check multiple reliable sources")
        
        return result
        
    except Exception as e:
        print(f"LLM explainer failed: {e}")
        # Fallback response
        return {
            "verdict": "UNVERIFIED",
            "trust_score": 0,
            "confidence": 0,
            "reasons": [f"LLM service error: {str(e)}"],
            "evidence_list": evidence,
            "one_line_tip": "Please verify this information independently",
            "suggested_action": "Check multiple reliable sources"
        }

def generate_mini_lesson(claim: str, language: str, evidence: list[dict], verdict: str) -> dict:
    """
    Generate mini-lesson using unified LLM service
    """
    try:
        # Use unified LLM service (Vertex AI or Ollama)
        llm_service = get_unified_llm_service()
        
        # Convert evidence format for LLM service
        evidence_for_llm = [
            {
                "text": f"{item['title']}: {item['snippet']}",
                "url": item.get('url', 'Unknown')
            }
            for item in evidence[:3]  # Limit to top 3 evidence items
        ]
        
        # Generate mini lesson
        result = llm_service.generate_mini_lesson(claim, verdict, evidence_for_llm, language)
        
        # Ensure all required fields are present
        result.setdefault("mini_lesson", f"This claim has been {verdict.lower()}. Always verify information from multiple reliable sources.")
        result.setdefault("tips", [
            "Check the source's credibility and reputation",
            "Look for corroborating evidence from other sources"
        ])
        result.setdefault("quiz", {
            "question": "What should you do when you see suspicious claims?",
            "options": ["Share immediately", "Verify from multiple sources", "Ignore completely"],
            "answer": "B"
        })
        
        return result
        
    except Exception as e:
        print(f"Mini-lesson generation failed: {e}")
        # Fallback response
        return {
            "mini_lesson": f"This claim has been {verdict.lower()}. Always verify information from multiple reliable sources.",
            "tips": [
                "Check the source's credibility and reputation",
                "Look for corroborating evidence from other sources"
            ],
            "quiz": {
                "question": "What should you do when you see suspicious claims?",
                "options": ["Share immediately", "Verify from multiple sources", "Ignore completely"],
                "answer": "B"
            }
        }

@router.post("/check", response_model=CheckResponse)
async def check_claim(
    request: CheckRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Check a claim for misinformation
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Step 1: Language detection
        if request.language == "auto":
            detected_lang, lang_confidence = detect_language(request.claim_text)
        else:
            detected_lang = request.language
            lang_confidence = 1.0
        
        # Step 2: Generate embedding
        embedding = get_embedding(request.claim_text, detected_lang)
        
        # Step 3: Search for similar claims
        evidence = search_similar_claims(embedding, detected_lang, top_k=6)
        
        # Step 4: Call LLM explainer
        llm_result = call_llm_explainer(request.claim_text, detected_lang, evidence)
        
        # Step 5: Generate mini-lesson (optional)
        mini_lesson = None
        if llm_result.get("verdict") in ["FALSE", "MISLEADING"]:
            mini_lesson = generate_mini_lesson(
                request.claim_text, 
                detected_lang, 
                evidence, 
                llm_result.get("verdict", "UNVERIFIED")
            )
        
        # Step 6: Prepare response
        response = CheckResponse(
            request_id=request_id,
            verdict=llm_result.get("verdict", "UNVERIFIED"),
            trust_score=llm_result.get("trust_score", 0),
            confidence=llm_result.get("confidence", 0),
            reasons=llm_result.get("reasons", []),
            evidence_list=llm_result.get("evidence_list", evidence),
            classifier_score=None,  # Would be set by classifier in production
            retrieved_ids=[item["id"] for item in evidence],
            latency_ms=int((time.time() - start_time) * 1000),
            language_detected=detected_lang,
            mini_lesson=mini_lesson
        )
        
        # Step 7: Create audit log
        audit_payload = {
            "request_id": request_id,
            "claim_text": request.claim_text,
            "language": detected_lang,
            "user_id": str(current_user.id) if current_user else None,
            "verdict": response.verdict,
            "trust_score": response.trust_score,
            "latency_ms": response.latency_ms
        }
        
        background_tasks.add_task(
            create_audit_entry,
            "check",
            audit_payload
        )
        
        return response
        
    except Exception as e:
        # Log error and return safe response
        print(f"Error in check_claim: {e}")
        
        # Create error audit log
        background_tasks.add_task(
            create_audit_entry,
            "check_error",
            {
                "request_id": request_id,
                "error": str(e),
                "claim_text": request.claim_text
            }
        )
        
        return CheckResponse(
            request_id=request_id,
            verdict="UNVERIFIED",
            trust_score=0,
            confidence=0,
            reasons=["An error occurred during processing"],
            evidence_list=[],
            retrieved_ids=[],
            latency_ms=int((time.time() - start_time) * 1000),
            language_detected=request.language if request.language != "auto" else "en"
        )

@router.get("/check/{request_id}")
async def get_check_result(request_id: str):
    """
    Get result of a previous check request
    """
    # In production, store and retrieve results from database
    raise HTTPException(
        status_code=501,
        detail="Check result retrieval not implemented yet"
    )
