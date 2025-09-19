"""
Unit tests for embeddings service
"""
import pytest
import numpy as np
from embeddings.embedding_service import EmbeddingService, generate_embedding, generate_batch_embeddings

class TestEmbeddingService:
    """Test cases for EmbeddingService"""
    
    def test_embedding_service_init(self):
        """Test EmbeddingService initialization"""
        service = EmbeddingService()
        assert service.model_name is not None
        assert service.model_config is not None
    
    def test_generate_embedding_single(self):
        """Test single embedding generation"""
        text = "This is a test claim"
        language = "en"
        
        embedding = generate_embedding(text, language)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, (int, float)) for x in embedding)
    
    def test_generate_embedding_multilingual(self):
        """Test multilingual embedding generation"""
        texts = [
            "This is a test claim",
            "यह एक परीक्षण दावा है",
            "இது ஒரு சோதனை கூற்று",
            "ಇದು ಒಂದು ಪರೀಕ್ಷಾ ಹೇಳಿಕೆ"
        ]
        languages = ["en", "hi", "ta", "kn"]
        
        embeddings = generate_batch_embeddings(texts, languages)
        
        assert len(embeddings) == len(texts)
        for embedding in embeddings:
            assert isinstance(embedding, list)
            assert len(embedding) > 0
    
    def test_normalize_text(self):
        """Test text normalization"""
        service = EmbeddingService()
        
        # Test English normalization
        text = "  This   is   a   test  "
        normalized = service.normalize_text(text, "en")
        assert normalized == "This is a test"
        
        # Test Hindi normalization
        text = "  यह   एक   परीक्षण   है  "
        normalized = service.normalize_text(text, "hi")
        assert normalized == "यह एक परीक्षण है"
    
    def test_compute_similarity(self):
        """Test similarity computation"""
        service = EmbeddingService()
        
        # Test identical embeddings
        emb1 = [1.0, 2.0, 3.0]
        emb2 = [1.0, 2.0, 3.0]
        similarity = service.compute_similarity(emb1, emb2)
        assert abs(similarity - 1.0) < 0.001
        
        # Test orthogonal embeddings
        emb1 = [1.0, 0.0, 0.0]
        emb2 = [0.0, 1.0, 0.0]
        similarity = service.compute_similarity(emb1, emb2)
        assert abs(similarity - 0.0) < 0.001
    
    def test_find_similar_embeddings(self):
        """Test similarity search"""
        service = EmbeddingService()
        
        query_embedding = [1.0, 2.0, 3.0]
        candidates = [
            {"id": "1", "embedding": [1.0, 2.0, 3.0], "text": "exact match"},
            {"id": "2", "embedding": [0.9, 1.9, 2.9], "text": "similar"},
            {"id": "3", "embedding": [0.0, 0.0, 0.0], "text": "different"}
        ]
        
        results = service.find_similar_embeddings(query_embedding, candidates, top_k=2)
        
        assert len(results) == 2
        assert results[0]["id"] == "1"  # Most similar
        assert results[1]["id"] == "2"  # Second most similar
        assert "similarity" in results[0]
        assert "similarity" in results[1]
    
    def test_get_model_info(self):
        """Test model information retrieval"""
        service = EmbeddingService()
        info = service.get_model_info()
        
        assert "model_name" in info
        assert "model_config" in info
        assert "is_loaded" in info
        assert "dimension" in info
        assert isinstance(info["is_loaded"], bool)
        assert isinstance(info["dimension"], int)
