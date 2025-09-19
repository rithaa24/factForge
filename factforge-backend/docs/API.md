# FactForge API Documentation

This document provides comprehensive API documentation for the FactForge backend system.

## 🔗 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.factforge.com`

## 🔐 Authentication

FactForge uses JWT-based authentication with role-based access control.

### Authentication Header
```http
Authorization: Bearer <jwt_token>
```

### Roles
- **user**: Basic fact-checking access
- **reviewer**: Review queue access
- **admin**: Full system access

## 📋 API Endpoints

### Health Check

#### GET /health
Check system health and service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "milvus": "healthy",
    "ollama": "healthy"
  }
}
```

### Fact Checking

#### POST /api/check
Perform fact-checking on a claim.

**Request Body:**
```json
{
  "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
  "language": "en",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "request_id": "uuid",
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
```

**Verdict Types:**
- `TRUE`: Claim is verified as true
- `FALSE`: Claim is verified as false
- `MISLEADING`: Claim is misleading or partially false
- `UNVERIFIED`: Unable to verify claim
- `PARTIALLY TRUE`: Claim is partially true

### Posts and Feed

#### GET /api/feed
Get paginated feed of posts.

**Query Parameters:**
- `cursor`: Pagination cursor (optional)
- `limit`: Number of posts to return (default: 20, max: 100)
- `filter`: Filter by category (optional)

**Response:**
```json
{
  "posts": [
    {
      "id": "post_123",
      "author": {
        "id": "user_456",
        "name": "John Doe",
        "avatar": "https://example.com/avatar.jpg"
      },
      "title": "Fact Check: UPI Lottery Scam",
      "content": "This is a common scam pattern...",
      "source_url": "https://example.com/article",
      "screenshot_url": "https://example.com/screenshot.jpg",
      "imageUrl": "https://example.com/image.jpg",
      "trust_score": 85,
      "verdict": "FALSE",
      "confidence": 90,
      "timestamp": "2024-01-01T12:00:00Z",
      "likes": 42,
      "comments": 8,
      "shares": 12,
      "views": 156
    }
  ],
  "next_cursor": "eyJpZCI6InBvc3RfMTIzIn0=",
  "has_more": true
}
```

#### POST /api/posts
Create a new post.

**Request Body:**
```json
{
  "claim_text": "Claim to fact-check",
  "screenshot": "base64-encoded-image",
  "tags": ["scam", "upi"],
  "community_id": "optional-community-id"
}
```

**Response:**
```json
{
  "id": "post_123",
  "author": {
    "id": "user_456",
    "name": "John Doe"
  },
  "title": "Auto-generated title",
  "content": "Processed content",
  "trust_score": 75,
  "verdict": "UNVERIFIED",
  "confidence": 60,
  "timestamp": "2024-01-01T12:00:00Z",
  "likes": 0,
  "comments": 0,
  "shares": 0,
  "views": 0
}
```

### Review Queue

#### GET /api/review/queue
Get items in review queue (reviewer role required).

**Query Parameters:**
- `limit`: Number of items to return (default: 20)
- `cursor`: Pagination cursor (optional)
- `status`: Filter by status (pending, approved, rejected)

**Response:**
```json
{
  "items": [
    {
      "id": "review_123",
      "doc_id": "doc_456",
      "url": "https://example.com/suspicious-page",
      "language": "hi",
      "heuristic_score": 0.75,
      "classifier_score": 0.68,
      "text_preview": "Send money to UPI...",
      "screenshot_url": "https://example.com/screenshot.jpg",
      "created_at": "2024-01-01T12:00:00Z",
      "assigned_to": "reviewer_789"
    }
  ],
  "next_cursor": "eyJpZCI6InJldmlld18xMjMifQ==",
  "has_more": true
}
```

#### POST /api/review/{id}/action
Take action on review item (reviewer role required).

**Request Body:**
```json
{
  "action": "approve",
  "note": "Clear scam pattern",
  "reviewer_id": "reviewer_789"
}
```

**Actions:**
- `approve`: Approve item as scam
- `reject`: Reject item as benign
- `escalate`: Escalate to admin

**Response:**
```json
{
  "success": true,
  "message": "Review action completed",
  "item_id": "review_123",
  "action": "approve"
}
```

### Admin Endpoints

#### GET /api/admin/crawler/status
Get crawler status and metrics (admin role required).

**Response:**
```json
{
  "status": "running",
  "last_run": "2024-01-01T12:00:00Z",
  "items_fetched_last_hour": 150,
  "active_workers": 3,
  "queue_length": 25,
  "success_rate": 0.95
}
```

#### POST /api/admin/crawler/run
Trigger immediate crawl (admin role required).

**Response:**
```json
{
  "success": true,
  "message": "Crawl started",
  "crawl_id": "crawl_123"
}
```

#### GET /api/admin/models
Get model information and thresholds (admin role required).

**Response:**
```json
{
  "classifier": {
    "version": "1.2.0",
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
```

#### POST /api/admin/models/update
Update model thresholds (admin role required).

**Request Body:**
```json
{
  "thresholds": {
    "en": 0.92,
    "hi": 0.88,
    "ta": 0.88,
    "kn": 0.88
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Thresholds updated",
  "new_thresholds": {
    "en": 0.92,
    "hi": 0.88,
    "ta": 0.88,
    "kn": 0.88
  }
}
```

#### GET /api/admin/audit/verify
Verify HMAC signature for audit entry (admin role required).

**Query Parameters:**
- `id`: Audit entry ID

**Response:**
```json
{
  "valid": true,
  "audit_id": "audit_123",
  "verified_at": "2024-01-01T12:00:00Z"
}
```

## 🌐 WebSocket Events

### Connection
Connect to WebSocket at `/ws/events` with optional query parameters:
- `user_id`: User ID for personal events
- `role`: User role (user, reviewer, admin)

### Event Types

#### Crawler Events
```json
{
  "type": "crawler:found",
  "data": {
    "url": "https://example.com/suspicious-page",
    "language": "hi",
    "heuristic_score": 0.75
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Ingestion Events
```json
{
  "type": "ingest:completed",
  "data": {
    "doc_id": "doc_123",
    "label": "scam",
    "score": 0.92
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Review Events
```json
{
  "type": "review:queued",
  "data": {
    "doc_id": "doc_123",
    "language": "hi",
    "score": 0.68
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Check Events
```json
{
  "type": "check:completed",
  "data": {
    "request_id": "req_123",
    "verdict": "FALSE",
    "latency_ms": 1250
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔍 Error Handling

### Error Response Format
```json
{
  "error": "Error message",
  "status_code": 400,
  "timestamp": 1640995200.0,
  "details": {
    "field": "claim_text",
    "message": "This field is required"
  }
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limited
- `500`: Internal Server Error

### Common Error Messages
- `"Invalid JWT token"`: Authentication failed
- `"Insufficient permissions"`: Role-based access denied
- `"Rate limit exceeded"`: Too many requests
- `"Invalid claim text"`: Input validation failed
- `"Service unavailable"`: External service down

## 📊 Rate Limiting

### Limits
- **Fact-checking**: 100 requests/hour per user
- **Feed access**: 1000 requests/hour per user
- **Review actions**: 500 requests/hour per reviewer
- **Admin actions**: 200 requests/hour per admin

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640998800
```

## 🔒 Security

### HTTPS
All production endpoints require HTTPS. HTTP is only allowed for development.

### CORS
CORS is configured to allow requests from authorized origins only.

### Input Validation
All inputs are validated using Pydantic models with strict type checking.

### PII Protection
Personal information is automatically redacted from public endpoints.

## 📱 SDK Examples

### Python
```python
import requests

# Fact-check a claim
response = requests.post(
    "https://api.factforge.com/api/check",
    headers={"Authorization": "Bearer your-token"},
    json={
        "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
        "language": "en"
    }
)

result = response.json()
print(f"Verdict: {result['verdict']}")
print(f"Trust Score: {result['trust_score']}")
```

### JavaScript
```javascript
// Fact-check a claim
const response = await fetch('https://api.factforge.com/api/check', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    claim_text: 'Send ₹1000 to UPI abc@upi to claim your lottery prize!',
    language: 'en'
  })
});

const result = await response.json();
console.log(`Verdict: ${result.verdict}`);
console.log(`Trust Score: ${result.trust_score}`);
```

### cURL
```bash
# Fact-check a claim
curl -X POST https://api.factforge.com/api/check \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
    "language": "en"
  }'
```

## 🧪 Testing

### Test Environment
- **Base URL**: `https://test-api.factforge.com`
- **Test Data**: Pre-loaded with sample claims
- **Rate Limits**: Higher limits for testing

### Test Claims
```json
{
  "english_scam": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
  "hindi_scam": "तत्काल ₹1000 UPI abc@upi पर भेजें और ₹50,000 का लॉटरी पुरस्कार जीतें!",
  "tamil_scam": "₹1000 ஐ UPI abc@upi க்கு உடனடியாக அனுப்பி ₹50,000 லாட்டரி பரிசை வெல்லுங்கள்!",
  "kannada_scam": "ತಕ್ಷಣ ₹1000 ಅನ್ನು UPI abc@upi ಗೆ ಕಳುಹಿಸಿ ₹50,000 ಲಾಟರಿ ಬಹುಮಾನವನ್ನು ಗೆಲ್ಲಿ!"
}
```

## 📈 Monitoring

### Metrics Endpoint
- **URL**: `/metrics`
- **Format**: Prometheus metrics
- **Authentication**: Not required

### Key Metrics
- `factforge_requests_total`: Total API requests
- `factforge_request_duration_seconds`: Request duration
- `factforge_classification_accuracy`: Classification accuracy
- `factforge_queue_length`: Queue lengths
- `factforge_error_rate`: Error rates

## 🔄 Webhooks

### Configuration
Webhooks can be configured to receive real-time events.

### Event Types
- `fact_check.completed`
- `review.approved`
- `review.rejected`
- `crawler.found`
- `admin.alert`

### Webhook Payload
```json
{
  "event_type": "fact_check.completed",
  "data": {
    "request_id": "req_123",
    "verdict": "FALSE",
    "trust_score": 15
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "signature": "hmac_signature"
}
```

---

**Note**: This API documentation is automatically generated from the OpenAPI specification. For the most up-to-date documentation, visit the interactive API docs at `/docs` when the service is running.
