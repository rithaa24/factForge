"""
Pytest configuration and fixtures
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"
os.environ["MILVUS_HOST"] = "localhost"
os.environ["MILVUS_PORT"] = "19530"
os.environ["OLLAMA_URL"] = "http://localhost:11434"
os.environ["HMAC_KEY"] = "test_hmac_key_32_chars_minimum"
os.environ["JWT_SECRET"] = "test_jwt_secret_32_chars_minimum"

@pytest.fixture
def client():
    """Create test client"""
    from api.app.main import app
    return TestClient(app)

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    with patch('api.app.core.db.get_redis') as mock:
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = True
        mock.return_value = mock_redis
        yield mock_redis

@pytest.fixture
def mock_milvus():
    """Mock Milvus client"""
    with patch('pymilvus.Collection') as mock:
        mock_collection = Mock()
        mock_collection.query.return_value = []
        mock_collection.search.return_value = []
        mock_collection.insert.return_value = Mock()
        mock.return_value = mock_collection
        yield mock_collection

@pytest.fixture
def mock_ollama():
    """Mock Ollama client"""
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        # Mock availability check
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": []}
        
        # Mock text generation
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "Generated text"}
        
        yield mock_post

@pytest.fixture
def mock_database():
    """Mock database session"""
    with patch('api.app.core.db.get_db_session') as mock:
        mock_session = Mock()
        mock_session.execute.return_value = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock.return_value.__enter__.return_value = mock_session
        yield mock_session

@pytest.fixture
def sample_claim_data():
    """Sample claim data for testing"""
    return {
        "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
        "language": "en",
        "user_id": "test-user"
    }

@pytest.fixture
def sample_evidence_data():
    """Sample evidence data for testing"""
    return [
        {
            "text": "Similar scam patterns found in database",
            "url": "http://example.com/evidence1",
            "score": 0.9
        },
        {
            "text": "UPI payment requests are common in fraud",
            "url": "http://example.com/evidence2",
            "score": 0.8
        }
    ]

@pytest.fixture
def sample_fact_check_response():
    """Sample fact-check response for testing"""
    return {
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

@pytest.fixture
def sample_post_data():
    """Sample post data for testing"""
    return {
        "id": "post_123",
        "author": {
            "id": "user_456",
            "name": "Test User",
            "avatar": "https://example.com/avatar.jpg"
        },
        "title": "Test Post Title",
        "content": "Test post content",
        "source_url": "https://example.com/source",
        "screenshot_url": "https://example.com/screenshot.jpg",
        "imageUrl": "https://example.com/image.jpg",
        "trust_score": 75,
        "verdict": "UNVERIFIED",
        "confidence": 60,
        "timestamp": "2024-01-01T12:00:00Z",
        "likes": 10,
        "comments": 5,
        "shares": 2,
        "views": 100
    }

@pytest.fixture
def sample_review_item():
    """Sample review item for testing"""
    return {
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

@pytest.fixture
def sample_crawler_status():
    """Sample crawler status for testing"""
    return {
        "status": "running",
        "last_run": "2024-01-01T12:00:00Z",
        "items_fetched_last_hour": 150,
        "active_workers": 3,
        "queue_length": 25,
        "success_rate": 0.95
    }

@pytest.fixture
def sample_models_info():
    """Sample models info for testing"""
    return {
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

@pytest.fixture
def sample_audit_entry():
    """Sample audit entry for testing"""
    return {
        "id": "audit_123",
        "event_type": "check",
        "payload": {
            "claim_text": "Test claim",
            "language": "en",
            "user_id": "test-user"
        },
        "signature": "test_signature",
        "created_at": "2024-01-01T12:00:00Z"
    }

@pytest.fixture
def sample_websocket_event():
    """Sample WebSocket event for testing"""
    return {
        "type": "check:completed",
        "data": {
            "request_id": "req_123",
            "verdict": "FALSE",
            "latency_ms": 1250
        },
        "timestamp": "2024-01-01T12:00:00Z"
    }

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing"""
    return {
        "filename": "test_screenshot.jpg",
        "content_type": "image/jpeg",
        "content": b"fake_image_content"
    }

@pytest.fixture
def mock_embedding():
    """Mock embedding for testing"""
    return [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional embedding

@pytest.fixture
def mock_classifier_result():
    """Mock classifier result for testing"""
    return {
        "label": "scam",
        "score": 0.92,
        "confidence": 0.85
    }

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "verdict": "FALSE",
        "trust_score": 15,
        "reasons": ["Test reason"],
        "evidence_list": ["Evidence 1"],
        "confidence": 80,
        "one_line_tip": "Test tip"
    }

@pytest.fixture
def mock_mini_lesson_response():
    """Mock mini lesson response for testing"""
    return {
        "mini_lesson": "Test lesson content",
        "tips": ["Tip 1", "Tip 2"],
        "quiz": {
            "question": "Test question?",
            "options": ["A", "B", "C"],
            "answer": "A"
        }
    }

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add unit marker to unit tests
        if "test_" in item.name and "integration" not in item.name:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in item.name:
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to performance tests
        if "performance" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow)
