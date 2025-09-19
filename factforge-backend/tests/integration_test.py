"""
Integration tests for FactForge backend
"""
import pytest
import time
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os

# Import the FastAPI app
from api.app.main import app

client = TestClient(app)

class TestFactCheckIntegration:
    """Integration tests for fact-checking flow"""
    
    def test_complete_fact_check_flow_english(self):
        """Test complete fact-checking flow for English"""
        # Mock all external dependencies
        with patch('api.app.routes.check.check_content') as mock_check:
            mock_check.return_value = {
                "request_id": "test-123",
                "verdict": "FALSE",
                "trust_score": 15,
                "reasons": [
                    "Contains UPI payment request",
                    "Promises unrealistic lottery winnings"
                ],
                "evidence_list": [
                    "Similar scam patterns found in database",
                    "UPI payment requests are common in fraud"
                ],
                "confidence": 85,
                "classifier_score": 0.92,
                "retrieved_ids": ["doc_123", "doc_456"],
                "latency_ms": 1250,
                "timestamp": "2024-01-01T12:00:00Z",
                "processingTime": 1.25
            }
            
            # Test fact-checking
            response = client.post(
                "/api/check",
                json={
                    "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
                    "language": "en",
                    "user_id": "test-user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "request_id" in data
            assert "verdict" in data
            assert "trust_score" in data
            assert "reasons" in data
            assert "evidence_list" in data
            assert "confidence" in data
            assert "classifier_score" in data
            assert "retrieved_ids" in data
            assert "latency_ms" in data
            assert "timestamp" in data
            assert "processingTime" in data
            
            # Verify specific values
            assert data["verdict"] == "FALSE"
            assert data["trust_score"] == 15
            assert data["confidence"] == 85
            assert len(data["reasons"]) == 2
            assert len(data["evidence_list"]) == 2
            assert len(data["retrieved_ids"]) == 2
    
    def test_complete_fact_check_flow_hindi(self):
        """Test complete fact-checking flow for Hindi"""
        with patch('api.app.routes.check.check_content') as mock_check:
            mock_check.return_value = {
                "request_id": "test-124",
                "verdict": "FALSE",
                "trust_score": 10,
                "reasons": [
                    "UPI भुगतान अनुरोध शामिल है",
                    "अवास्तविक लॉटरी जीत का वादा"
                ],
                "evidence_list": [
                    "डेटाबेस में समान घोटाला पैटर्न मिले",
                    "UPI भुगतान अनुरोध धोखाधड़ी में आम हैं"
                ],
                "confidence": 90,
                "classifier_score": 0.95,
                "retrieved_ids": ["doc_789", "doc_012"],
                "latency_ms": 1100,
                "timestamp": "2024-01-01T12:00:00Z",
                "processingTime": 1.1
            }
            
            response = client.post(
                "/api/check",
                json={
                    "claim_text": "तत्काल ₹1000 UPI abc@upi पर भेजें और ₹50,000 का लॉटरी पुरस्कार जीतें!",
                    "language": "hi",
                    "user_id": "test-user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["verdict"] == "FALSE"
            assert data["trust_score"] == 10
            assert data["confidence"] == 90
            assert len(data["reasons"]) == 2
            assert len(data["evidence_list"]) == 2
    
    def test_complete_fact_check_flow_tamil(self):
        """Test complete fact-checking flow for Tamil"""
        with patch('api.app.routes.check.check_content') as mock_check:
            mock_check.return_value = {
                "request_id": "test-125",
                "verdict": "FALSE",
                "trust_score": 12,
                "reasons": [
                    "UPI கட்டண கோரிக்கை உள்ளது",
                    "உண்மையற்ற லாட்டரி வெற்றியை உறுதியளிக்கிறது"
                ],
                "evidence_list": [
                    "தரவுத்தளத்தில் ஒத்த மோசடி வடிவங்கள் காணப்படுகின்றன",
                    "UPI கட்டண கோரிக்கைகள் மோசடியில் பொதுவானவை"
                ],
                "confidence": 88,
                "classifier_score": 0.93,
                "retrieved_ids": ["doc_345", "doc_678"],
                "latency_ms": 1300,
                "timestamp": "2024-01-01T12:00:00Z",
                "processingTime": 1.3
            }
            
            response = client.post(
                "/api/check",
                json={
                    "claim_text": "₹1000 ஐ UPI abc@upi க்கு உடனடியாக அனுப்பி ₹50,000 லாட்டரி பரிசை வெல்லுங்கள்!",
                    "language": "ta",
                    "user_id": "test-user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["verdict"] == "FALSE"
            assert data["trust_score"] == 12
            assert data["confidence"] == 88
            assert len(data["reasons"]) == 2
            assert len(data["evidence_list"]) == 2
    
    def test_complete_fact_check_flow_kannada(self):
        """Test complete fact-checking flow for Kannada"""
        with patch('api.app.routes.check.check_content') as mock_check:
            mock_check.return_value = {
                "request_id": "test-126",
                "verdict": "FALSE",
                "trust_score": 8,
                "reasons": [
                    "UPI ಪಾವತಿ ವಿನಂತಿ ಒಳಗೊಂಡಿದೆ",
                    "ಅವಾಸ್ತವಿಕ ಲಾಟರಿ ಬಹುಮಾನವನ್ನು ಭರವಸೆ ನೀಡುತ್ತದೆ"
                ],
                "evidence_list": [
                    "ಡೇಟಾಬೇಸ್ನಲ್ಲಿ ಹೋಲುವ ಮೋಸದ ಮಾದರಿಗಳು ಕಂಡುಬಂದಿವೆ",
                    "UPI ಪಾವತಿ ವಿನಂತಿಗಳು ಮೋಸದಲ್ಲಿ ಸಾಮಾನ್ಯವಾಗಿವೆ"
                ],
                "confidence": 92,
                "classifier_score": 0.96,
                "retrieved_ids": ["doc_901", "doc_234"],
                "latency_ms": 1200,
                "timestamp": "2024-01-01T12:00:00Z",
                "processingTime": 1.2
            }
            
            response = client.post(
                "/api/check",
                json={
                    "claim_text": "ತಕ್ಷಣ ₹1000 ಅನ್ನು UPI abc@upi ಗೆ ಕಳುಹಿಸಿ ₹50,000 ಲಾಟರಿ ಬಹುಮಾನವನ್ನು ಗೆಲ್ಲಿ!",
                    "language": "kn",
                    "user_id": "test-user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["verdict"] == "FALSE"
            assert data["trust_score"] == 8
            assert data["confidence"] == 92
            assert len(data["reasons"]) == 2
            assert len(data["evidence_list"]) == 2

class TestFeedIntegration:
    """Integration tests for feed functionality"""
    
    def test_feed_creation_and_retrieval(self):
        """Test creating posts and retrieving them from feed"""
        # Mock post creation
        with patch('api.app.routes.posts.create_post') as mock_create:
            mock_create.return_value = {
                "id": "post_123",
                "author": {"id": "user_456", "name": "Test User"},
                "title": "Test Post Title",
                "content": "Test post content",
                "trust_score": 75,
                "verdict": "UNVERIFIED",
                "confidence": 60,
                "timestamp": "2024-01-01T12:00:00Z",
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "views": 0
            }
            
            # Create a post
            create_response = client.post(
                "/api/posts",
                json={
                    "claim_text": "Test claim for feed",
                    "screenshot": "base64-encoded-image",
                    "tags": ["test", "claim"],
                    "community_id": "community_1"
                }
            )
            
            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data["id"] == "post_123"
            assert create_data["author"]["id"] == "user_456"
        
        # Mock feed retrieval
        with patch('api.app.routes.posts.get_posts') as mock_get_posts:
            mock_get_posts.return_value = {
                "posts": [
                    {
                        "id": "post_123",
                        "author": {"id": "user_456", "name": "Test User"},
                        "title": "Test Post Title",
                        "content": "Test post content",
                        "trust_score": 75,
                        "verdict": "UNVERIFIED",
                        "confidence": 60,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "likes": 5,
                        "comments": 2,
                        "shares": 1,
                        "views": 25
                    }
                ],
                "next_cursor": "eyJpZCI6InBvc3RfMTIzIn0=",
                "has_more": False
            }
            
            # Retrieve feed
            feed_response = client.get("/api/feed")
            
            assert feed_response.status_code == 200
            feed_data = feed_response.json()
            assert "posts" in feed_data
            assert len(feed_data["posts"]) == 1
            assert feed_data["posts"][0]["id"] == "post_123"
            assert feed_data["posts"][0]["likes"] == 5

class TestReviewIntegration:
    """Integration tests for review functionality"""
    
    def test_review_queue_workflow(self):
        """Test complete review queue workflow"""
        # Mock getting review queue
        with patch('api.app.routes.review.get_review_queue') as mock_get_queue:
            mock_get_queue.return_value = {
                "items": [
                    {
                        "id": "review_123",
                        "doc_id": "doc_456",
                        "url": "http://example.com/suspicious",
                        "language": "hi",
                        "heuristic_score": 0.8,
                        "classifier_score": 0.7,
                        "text_preview": "Send money to UPI...",
                        "screenshot_url": "http://example.com/screenshot.jpg",
                        "created_at": "2024-01-01T12:00:00Z",
                        "assigned_to": "reviewer_789"
                    }
                ],
                "next_cursor": "eyJpZCI6InJldmlld18xMjMifQ==",
                "has_more": False
            }
            
            # Get review queue
            queue_response = client.get("/api/review/queue")
            
            assert queue_response.status_code == 200
            queue_data = queue_response.json()
            assert "items" in queue_data
            assert len(queue_data["items"]) == 1
            assert queue_data["items"][0]["id"] == "review_123"
        
        # Mock review action
        with patch('api.app.routes.review.take_review_action') as mock_action:
            mock_action.return_value = {
                "success": True,
                "message": "Review action completed",
                "item_id": "review_123",
                "action": "approve"
            }
            
            # Take review action
            action_response = client.post(
                "/api/review/review_123/action",
                json={
                    "action": "approve",
                    "note": "Clear scam pattern",
                    "reviewer_id": "reviewer_789"
                }
            )
            
            assert action_response.status_code == 200
            action_data = action_response.json()
            assert action_data["success"] is True
            assert action_data["action"] == "approve"

class TestAdminIntegration:
    """Integration tests for admin functionality"""
    
    def test_admin_workflow(self):
        """Test complete admin workflow"""
        # Mock crawler status
        with patch('api.app.routes.admin.get_crawler_status') as mock_status:
            mock_status.return_value = {
                "status": "running",
                "last_run": "2024-01-01T12:00:00Z",
                "items_fetched_last_hour": 150,
                "active_workers": 3,
                "queue_length": 25,
                "success_rate": 0.95
            }
            
            # Get crawler status
            status_response = client.get("/api/admin/crawler/status")
            
            assert status_response.status_code == 200
            status_data = status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "running"
            assert "items_fetched_last_hour" in status_data
        
        # Mock crawler trigger
        with patch('api.app.routes.admin.trigger_crawler') as mock_trigger:
            mock_trigger.return_value = {
                "success": True,
                "message": "Crawl started",
                "crawl_id": "crawl_123"
            }
            
            # Trigger crawler
            trigger_response = client.post("/api/admin/crawler/run")
            
            assert trigger_response.status_code == 200
            trigger_data = trigger_response.json()
            assert trigger_data["success"] is True
            assert "crawl_id" in trigger_data
        
        # Mock models info
        with patch('api.app.routes.admin.get_models') as mock_models:
            mock_models.return_value = {
                "classifier": {
                    "version": "1.0.0",
                    "trained_on": "2024-01-01T00:00:00Z",
                    "languages_supported": ["en", "hi", "ta", "kn"],
                    "thresholds": {
                        "en": 0.9,
                        "hi": 0.85,
                        "ta": 0.85,
                        "kn": 0.85
                    }
                },
                "embedding": {
                    "model": "paraphrase-multilingual-mpnet-base-v2",
                    "dimension": 768,
                    "languages_supported": ["en", "hi", "ta", "kn"]
                },
                "llm": {
                    "model": "llama3.2:3b",
                    "version": "latest",
                    "status": "healthy"
                }
            }
            
            # Get models info
            models_response = client.get("/api/admin/models")
            
            assert models_response.status_code == 200
            models_data = models_response.json()
            assert "classifier" in models_data
            assert "embedding" in models_data
            assert "llm" in models_data

class TestErrorHandling:
    """Integration tests for error handling"""
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/check",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/check",
            json={
                "language": "en"
                # Missing claim_text
            }
        )
        
        assert response.status_code == 422
    
    def test_unsupported_language(self):
        """Test handling of unsupported language"""
        response = client.post(
            "/api/check",
            json={
                "claim_text": "Test claim",
                "language": "xyz"  # Unsupported language
            }
        )
        
        assert response.status_code == 422
    
    def test_empty_claim_text(self):
        """Test handling of empty claim text"""
        response = client.post(
            "/api/check",
            json={
                "claim_text": "",  # Empty claim
                "language": "en"
            }
        )
        
        assert response.status_code == 422

class TestPerformance:
    """Integration tests for performance"""
    
    def test_response_time(self):
        """Test API response time"""
        start_time = time.time()
        
        with patch('api.app.routes.check.check_content') as mock_check:
            mock_check.return_value = {
                "request_id": "test-123",
                "verdict": "FALSE",
                "trust_score": 20,
                "reasons": ["Test reason"],
                "evidence_list": ["Evidence 1"],
                "confidence": 80,
                "classifier_score": 0.9,
                "retrieved_ids": ["doc_1"],
                "latency_ms": 1000,
                "timestamp": "2024-01-01T12:00:00Z",
                "processingTime": 1.0
            }
            
            response = client.post(
                "/api/check",
                json={
                    "claim_text": "Test claim",
                    "language": "en"
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            with patch('api.app.routes.check.check_content') as mock_check:
                mock_check.return_value = {
                    "request_id": "test-123",
                    "verdict": "FALSE",
                    "trust_score": 20,
                    "reasons": ["Test reason"],
                    "evidence_list": ["Evidence 1"],
                    "confidence": 80,
                    "classifier_score": 0.9,
                    "retrieved_ids": ["doc_1"],
                    "latency_ms": 1000,
                    "timestamp": "2024-01-01T12:00:00Z",
                    "processingTime": 1.0
                }
                
                response = client.post(
                    "/api/check",
                    json={
                        "claim_text": "Test claim",
                        "language": "en"
                    }
                )
                
                results.put(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check all responses were successful
        while not results.empty():
            status_code = results.get()
            assert status_code == 200