"""
Unit tests for LLM service
"""
import pytest
from unittest.mock import Mock, patch
from llm.llm_service import OllamaService, generate_fact_check_response, generate_mini_lesson

class TestOllamaService:
    """Test cases for OllamaService"""
    
    def test_ollama_service_init(self):
        """Test OllamaService initialization"""
        service = OllamaService()
        assert service.base_url is not None
        assert service.model is not None
        assert service.timeout > 0
        assert service.max_retries > 0
    
    def test_is_available_success(self):
        """Test successful availability check"""
        service = OllamaService()
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            assert service.is_available() is True
    
    def test_is_available_failure(self):
        """Test failed availability check"""
        service = OllamaService()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            assert service.is_available() is False
    
    def test_generate_text_success(self):
        """Test successful text generation"""
        service = OllamaService()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "Generated text"}
            mock_post.return_value = mock_response
            
            result = service.generate_text("Test prompt")
            assert result == "Generated text"
    
    def test_generate_text_failure(self):
        """Test failed text generation"""
        service = OllamaService()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response
            
            result = service.generate_text("Test prompt")
            assert result == ""
    
    def test_generate_json_success(self):
        """Test successful JSON generation"""
        service = OllamaService()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": '{"key": "value"}'}
            mock_post.return_value = mock_response
            
            result = service.generate_json("Test prompt")
            assert result == {"key": "value"}
    
    def test_generate_json_invalid_json(self):
        """Test invalid JSON handling"""
        service = OllamaService()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "Invalid JSON"}
            mock_post.return_value = mock_response
            
            result = service.generate_json("Test prompt")
            assert result == {}
    
    def test_generate_fact_check_response_english(self):
        """Test English fact-check response generation"""
        service = OllamaService()
        
        claim = "Test claim"
        evidence = [{"text": "Evidence 1", "url": "http://example.com"}]
        language = "en"
        
        with patch.object(service, 'generate_json') as mock_generate:
            mock_generate.return_value = {
                "verdict": "FALSE",
                "trust_score": 20,
                "reasons": ["Test reason"],
                "evidence_list": ["Evidence 1"],
                "confidence": 80,
                "one_line_tip": "Test tip"
            }
            
            result = service.generate_fact_check_response(claim, evidence, language)
            
            assert result["verdict"] == "FALSE"
            assert result["trust_score"] == 20
            assert "reasons" in result
            assert "evidence_list" in result
            assert "confidence" in result
            assert "one_line_tip" in result
    
    def test_generate_fact_check_response_hindi(self):
        """Test Hindi fact-check response generation"""
        service = OllamaService()
        
        claim = "परीक्षण दावा"
        evidence = [{"text": "साक्ष्य 1", "url": "http://example.com"}]
        language = "hi"
        
        with patch.object(service, 'generate_json') as mock_generate:
            mock_generate.return_value = {
                "verdict": "FALSE",
                "trust_score": 20,
                "reasons": ["परीक्षण कारण"],
                "evidence_list": ["साक्ष्य 1"],
                "confidence": 80,
                "one_line_tip": "परीक्षण सुझाव"
            }
            
            result = service.generate_fact_check_response(claim, evidence, language)
            
            assert result["verdict"] == "FALSE"
            assert result["trust_score"] == 20
            assert "reasons" in result
            assert "evidence_list" in result
            assert "confidence" in result
            assert "one_line_tip" in result
    
    def test_generate_mini_lesson_english(self):
        """Test English mini lesson generation"""
        service = OllamaService()
        
        claim = "Test claim"
        verdict = "FALSE"
        evidence = [{"text": "Evidence 1", "url": "http://example.com"}]
        language = "en"
        
        with patch.object(service, 'generate_json') as mock_generate:
            mock_generate.return_value = {
                "mini_lesson": "Test lesson",
                "tips": ["Tip 1", "Tip 2"],
                "quiz": {
                    "question": "Test question?",
                    "options": ["A", "B", "C"],
                    "answer": "A"
                }
            }
            
            result = service.generate_mini_lesson(claim, verdict, evidence, language)
            
            assert result["mini_lesson"] == "Test lesson"
            assert len(result["tips"]) == 2
            assert "quiz" in result
            assert "question" in result["quiz"]
            assert "options" in result["quiz"]
            assert "answer" in result["quiz"]
    
    def test_generate_mini_lesson_hindi(self):
        """Test Hindi mini lesson generation"""
        service = OllamaService()
        
        claim = "परीक्षण दावा"
        verdict = "FALSE"
        evidence = [{"text": "साक्ष्य 1", "url": "http://example.com"}]
        language = "hi"
        
        with patch.object(service, 'generate_json') as mock_generate:
            mock_generate.return_value = {
                "mini_lesson": "परीक्षण पाठ",
                "tips": ["सुझाव 1", "सुझाव 2"],
                "quiz": {
                    "question": "परीक्षण प्रश्न?",
                    "options": ["A", "B", "C"],
                    "answer": "A"
                }
            }
            
            result = service.generate_mini_lesson(claim, verdict, evidence, language)
            
            assert result["mini_lesson"] == "परीक्षण पाठ"
            assert len(result["tips"]) == 2
            assert "quiz" in result
            assert "question" in result["quiz"]
            assert "options" in result["quiz"]
            assert "answer" in result["quiz"]
    
    def test_generate_fact_check_response_fallback(self):
        """Test fallback when LLM fails"""
        service = OllamaService()
        
        claim = "Test claim"
        evidence = []
        language = "en"
        
        with patch.object(service, 'generate_json') as mock_generate:
            mock_generate.return_value = {}
            
            result = service.generate_fact_check_response(claim, evidence, language)
            
            assert result["verdict"] == "UNVERIFIED"
            assert result["trust_score"] == 0
            assert "reasons" in result
            assert "evidence_list" in result
            assert "confidence" in result
            assert "one_line_tip" in result
    
    def test_generate_mini_lesson_fallback(self):
        """Test fallback when LLM fails"""
        service = OllamaService()
        
        claim = "Test claim"
        verdict = "FALSE"
        evidence = []
        language = "en"
        
        with patch.object(service, 'generate_json') as mock_generate:
            mock_generate.return_value = {}
            
            result = service.generate_mini_lesson(claim, verdict, evidence, language)
            
            assert "mini_lesson" in result
            assert "tips" in result
            assert "quiz" in result
            assert len(result["tips"]) > 0
            assert "question" in result["quiz"]
            assert "options" in result["quiz"]
            assert "answer" in result["quiz"]
