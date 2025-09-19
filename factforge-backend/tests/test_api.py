"""
Unit tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

# Import the FastAPI app
from api.app.main import app

client = TestClient(app)

class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert isinstance(data["services"], dict)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "FactForge API"
        assert data["version"] == "1.0.0"
        assert "status" in data
        assert "timestamp" in data

class TestFactCheck:
    """Test cases for fact-checking endpoint"""
    
    def test_check_endpoint_success(self):
        """Test successful fact-checking"""
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
                    "language": "en",
                    "user_id": "test-user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["verdict"] == "FALSE"
            assert data["trust_score"] == 20
            assert "reasons" in data
            assert "evidence_list" in data
    
    def test_check_endpoint_invalid_input(self):
        """Test fact-checking with invalid input"""
        response = client.post(
            "/api/check",
            json={
                "claim_text": "",  # Empty claim
                "language": "en"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_check_endpoint_missing_claim(self):
        """Test fact-checking with missing claim"""
        response = client.post(
            "/api/check",
            json={
                "language": "en"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_check_endpoint_unsupported_language(self):
        """Test fact-checking with unsupported language"""
        response = client.post(
            "/api/check",
            json={
                "claim_text": "Test claim",
                "language": "xyz"  # Unsupported language
            }
        )
        
        assert response.status_code == 422  # Validation error

class TestPosts:
    """Test cases for posts endpoint"""
    
    def test_get_feed_success(self):
        """Test successful feed retrieval"""
        with patch('api.app.routes.posts.get_posts') as mock_get_posts:
            mock_get_posts.return_value = {
                "posts": [
                    {
                        "id": "post_1",
                        "author": {"id": "user_1", "name": "Test User"},
                        "title": "Test Post",
                        "content": "Test content",
                        "trust_score": 80,
                        "verdict": "TRUE",
                        "confidence": 90,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "likes": 10,
                        "comments": 5,
                        "shares": 2,
                        "views": 100
                    }
                ],
                "next_cursor": "eyJpZCI6InBvc3RfMSJ9",
                "has_more": False
            }
            
            response = client.get("/api/feed")
            
            assert response.status_code == 200
            data = response.json()
            assert "posts" in data
            assert len(data["posts"]) == 1
            assert data["posts"][0]["id"] == "post_1"
    
    def test_get_feed_with_pagination(self):
        """Test feed retrieval with pagination"""
        with patch('api.app.routes.posts.get_posts') as mock_get_posts:
            mock_get_posts.return_value = {
                "posts": [],
                "next_cursor": "eyJpZCI6InBvc3RfMSJ9",
                "has_more": True
            }
            
            response = client.get("/api/feed?cursor=eyJpZCI6InBvc3RfMSJ9&limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert "posts" in data
            assert "next_cursor" in data
            assert "has_more" in data
    
    def test_create_post_success(self):
        """Test successful post creation"""
        with patch('api.app.routes.posts.create_post') as mock_create_post:
            mock_create_post.return_value = {
                "id": "post_1",
                "author": {"id": "user_1", "name": "Test User"},
                "title": "Test Post",
                "content": "Test content",
                "trust_score": 80,
                "verdict": "TRUE",
                "confidence": 90,
                "timestamp": "2024-01-01T12:00:00Z",
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "views": 0
            }
            
            response = client.post(
                "/api/posts",
                json={
                    "claim_text": "Test claim",
                    "screenshot": "base64-encoded-image",
                    "tags": ["test", "claim"],
                    "community_id": "community_1"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "post_1"
            assert data["author"]["id"] == "user_1"
    
    def test_create_post_invalid_input(self):
        """Test post creation with invalid input"""
        response = client.post(
            "/api/posts",
            json={
                "claim_text": "",  # Empty claim
                "tags": ["test"]
            }
        )
        
        assert response.status_code == 422  # Validation error

class TestReview:
    """Test cases for review endpoint"""
    
    def test_get_review_queue_success(self):
        """Test successful review queue retrieval"""
        with patch('api.app.routes.review.get_review_queue') as mock_get_queue:
            mock_get_queue.return_value = {
                "items": [
                    {
                        "id": "review_1",
                        "doc_id": "doc_1",
                        "url": "http://example.com",
                        "language": "en",
                        "heuristic_score": 0.8,
                        "classifier_score": 0.7,
                        "text_preview": "Test text...",
                        "screenshot_url": "http://example.com/screenshot.jpg",
                        "created_at": "2024-01-01T12:00:00Z",
                        "assigned_to": "reviewer_1"
                    }
                ],
                "next_cursor": "eyJpZCI6InJldmlld18xIn0=",
                "has_more": False
            }
            
            response = client.get("/api/review/queue")
            
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) == 1
            assert data["items"][0]["id"] == "review_1"
    
    def test_review_action_success(self):
        """Test successful review action"""
        with patch('api.app.routes.review.take_review_action') as mock_action:
            mock_action.return_value = {
                "success": True,
                "message": "Review action completed",
                "item_id": "review_1",
                "action": "approve"
            }
            
            response = client.post(
                "/api/review/review_1/action",
                json={
                    "action": "approve",
                    "note": "Clear scam pattern",
                    "reviewer_id": "reviewer_1"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["action"] == "approve"
    
    def test_review_action_invalid_action(self):
        """Test review action with invalid action"""
        response = client.post(
            "/api/review/review_1/action",
            json={
                "action": "invalid_action",
                "note": "Test note",
                "reviewer_id": "reviewer_1"
            }
        )
        
        assert response.status_code == 422  # Validation error

class TestAdmin:
    """Test cases for admin endpoint"""
    
    def test_get_crawler_status_success(self):
        """Test successful crawler status retrieval"""
        with patch('api.app.routes.admin.get_crawler_status') as mock_status:
            mock_status.return_value = {
                "status": "running",
                "last_run": "2024-01-01T12:00:00Z",
                "items_fetched_last_hour": 100,
                "active_workers": 2,
                "queue_length": 10,
                "success_rate": 0.95
            }
            
            response = client.get("/api/admin/crawler/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "running"
            assert "items_fetched_last_hour" in data
            assert "active_workers" in data
    
    def test_trigger_crawler_success(self):
        """Test successful crawler trigger"""
        with patch('api.app.routes.admin.trigger_crawler') as mock_trigger:
            mock_trigger.return_value = {
                "success": True,
                "message": "Crawl started",
                "crawl_id": "crawl_123"
            }
            
            response = client.post("/api/admin/crawler/run")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "crawl_id" in data
    
    def test_get_models_success(self):
        """Test successful models retrieval"""
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
            
            response = client.get("/api/admin/models")
            
            assert response.status_code == 200
            data = response.json()
            assert "classifier" in data
            assert "embedding" in data
            assert "llm" in data
    
    def test_update_models_success(self):
        """Test successful models update"""
        with patch('api.app.routes.admin.update_models') as mock_update:
            mock_update.return_value = {
                "success": True,
                "message": "Thresholds updated",
                "new_thresholds": {
                    "en": 0.92,
                    "hi": 0.88,
                    "ta": 0.88,
                    "kn": 0.88
                }
            }
            
            response = client.post(
                "/api/admin/models/update",
                json={
                    "thresholds": {
                        "en": 0.92,
                        "hi": 0.88,
                        "ta": 0.88,
                        "kn": 0.88
                    }
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "new_thresholds" in data
    
    def test_verify_audit_success(self):
        """Test successful audit verification"""
        with patch('api.app.routes.admin.verify_audit') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "audit_id": "audit_123",
                "verified_at": "2024-01-01T12:00:00Z"
            }
            
            response = client.get("/api/admin/audit/verify?id=audit_123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert data["audit_id"] == "audit_123"
