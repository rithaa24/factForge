"""
Embeddings module for FactForge backend
"""
from .embedding_service import EmbeddingService, get_embedding_service, generate_embedding, generate_batch_embeddings
from .model_config import get_model_config, get_language_config, is_language_supported

__all__ = [
    "EmbeddingService",
    "get_embedding_service", 
    "generate_embedding",
    "generate_batch_embeddings",
    "get_model_config",
    "get_language_config",
    "is_language_supported"
]
