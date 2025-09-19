"""
Embedding service for generating and managing embeddings
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from .model_config import get_model_config, get_language_config, is_language_supported

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
        self.model = None
        self.model_config = get_model_config()
        self.load_model()
    
    def load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Use fallback model
            try:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Fallback model loaded")
            except Exception as e2:
                logger.error(f"Failed to load fallback model: {e2}")
                self.model = None
    
    def generate_embedding(self, text: str, language: str = "en") -> List[float]:
        """Generate embedding for a single text"""
        try:
            if self.model:
                # Normalize text
                normalized_text = self.normalize_text(text, language)
                
                # Generate embedding
                embedding = self.model.encode(normalized_text)
                return embedding.tolist()
            else:
                # Fallback: generate dummy embedding
                return self._generate_dummy_embedding(text, language)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._generate_dummy_embedding(text, language)
    
    def generate_batch_embeddings(self, texts: List[str], languages: List[str] = None) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        if languages is None:
            languages = ["en"] * len(texts)
        
        try:
            if self.model:
                # Normalize texts
                normalized_texts = [self.normalize_text(text, lang) for text, lang in zip(texts, languages)]
                
                # Generate embeddings
                embeddings = self.model.encode(normalized_texts)
                return embeddings.tolist()
            else:
                # Fallback: generate dummy embeddings
                embeddings = []
                for text, lang in zip(texts, languages):
                    embedding = self._generate_dummy_embedding(text, lang)
                    embeddings.append(embedding)
                return embeddings
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            return [self._generate_dummy_embedding(text, lang) for text, lang in zip(texts, languages)]
    
    def normalize_text(self, text: str, language: str = "en") -> str:
        """Normalize text for embedding generation"""
        if not text:
            return ""
        
        # Get language-specific config
        lang_config = get_language_config(language)
        
        # Basic text normalization
        text = text.strip()
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Unicode normalization for Indic languages
        if language in ["hi", "ta", "kn"] and lang_config.get("unicode_normalization"):
            import unicodedata
            text = unicodedata.normalize(lang_config["unicode_normalization"], text)
        
        # Lowercase if configured
        if lang_config.get("lowercase", False):
            text = text.lower()
        
        # Truncate if too long
        max_length = lang_config.get("max_length", 512)
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    def _generate_dummy_embedding(self, text: str, language: str) -> List[float]:
        """Generate a dummy embedding for fallback"""
        import hashlib
        
        # Create a hash-based embedding
        hash_obj = hashlib.md5(f"{text}_{language}".encode())
        hash_hex = hash_obj.hexdigest()
        
        embedding = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad or truncate to model dimension
        model_dim = self.model_config.get("dimension", 384)
        while len(embedding) < model_dim:
            embedding.append(0.0)
        embedding = embedding[:model_dim]
        
        return embedding
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return 0.0
    
    def find_similar_embeddings(self, query_embedding: List[float], 
                               candidate_embeddings: List[Dict[str, Any]], 
                               top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar embeddings"""
        try:
            similarities = []
            
            for candidate in candidate_embeddings:
                similarity = self.compute_similarity(query_embedding, candidate["embedding"])
                similarities.append({
                    **candidate,
                    "similarity": similarity
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_config": self.model_config,
            "is_loaded": self.model is not None,
            "dimension": self.model_config.get("dimension", 384)
        }

# Global service instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def generate_embedding(text: str, language: str = "en") -> List[float]:
    """Generate embedding for text (convenience function)"""
    service = get_embedding_service()
    return service.generate_embedding(text, language)

def generate_batch_embeddings(texts: List[str], languages: List[str] = None) -> List[List[float]]:
    """Generate embeddings for batch of texts (convenience function)"""
    service = get_embedding_service()
    return service.generate_batch_embeddings(texts, languages)
