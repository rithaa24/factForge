# FactForge Backend

A comprehensive multilingual fact-checking and misinformation detection backend system built with FastAPI, supporting Tamil, English, Hindi, and Kannada languages.

## 🚀 Features

- **Multilingual Support**: Tamil, English, Hindi, and Kannada
- **Real-time Fact Checking**: REST API for instant fact verification
- **Web Crawling**: Scrapy-based crawler with Playwright for JavaScript pages
- **OCR Processing**: Tesseract OCR with language-specific models
- **Language Detection**: FastText-based language identification
- **Transliteration**: Support for Hinglish and other transliterated content
- **Vector Search**: Milvus vector database for similarity search
- **LLM Integration**: Google Vertex AI (Gemini) and Ollama for local LLM inference
- **Review Queue**: Human review system for borderline cases
- **Audit Logging**: HMAC-signed audit trails
- **Admin Dashboard**: Management interface for system monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Workers       │
│   (React Native)│◄──►│   (FastAPI)     │◄──►│   (Enrichment)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Database      │    │   Vector DB     │
                       │   (PostgreSQL)  │    │   (Milvus)      │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Message Queue │
                       │   (RabbitMQ)    │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL 13
- **Vector DB**: Milvus
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **LLM**: Google Vertex AI (Gemini) + Ollama (local)
- **OCR**: Tesseract
- **Crawler**: Scrapy + Playwright
- **ML**: Sentence Transformers, FastText
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- 8GB+ RAM (for running all services)
- NVIDIA GPU (optional, for faster LLM inference)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd factforge-backend
cp infra/env.sample .env
```

### 2. Choose LLM Provider

**Option A: Google Vertex AI (Recommended for Production)**
```bash
# Run automated setup
python scripts/setup_gcp.py

# Or follow manual setup in docs/VERTEX_AI_SETUP.md
```

**Option B: Ollama (Free, Local)**
```bash
# No additional setup required
# Ollama will be used automatically if Vertex AI is not configured
```

### 3. Configure Environment

Edit `.env` file with your settings:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/factforge

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Milvus
MILVUS_HOST=milvus
MILVUS_PORT=19530

# Ollama
OLLAMA_URL=http://ollama:11434

# Security
HMAC_KEY=your_random_hex_key_32_chars_minimum
JWT_SECRET=your_random_jwt_secret_key_32_chars_minimum
```

### 4. Start Services

```bash
# Start all services
docker-compose -f infra/docker-compose.yml up --build

# Or start in background
docker-compose -f infra/docker-compose.yml up -d --build
```

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Test fact-checking
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"claim_text": "Test claim", "language": "en"}'
```

## 📚 API Documentation

Once the services are running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Development

### Local Development Setup

```bash
# Install dependencies
pip install -r api/requirements.txt
pip install -r embeddings/requirements.txt
pip install -r models/requirements.txt

# Start individual services
python api/app/main.py
python workers/enrichment_worker/main.py
python workers/ingest_worker/main.py
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_vertex_ai.py

# Run with coverage
pytest tests/ --cov=api --cov=llm
```

## 🎯 Key Endpoints

### Fact-Checking
- `POST /api/check` - Check a claim for misinformation
- `GET /api/feed` - Get fact-checked posts feed
- `POST /api/posts` - Create a new post

### Admin
- `GET /admin/llm/status` - Check LLM provider status
- `POST /admin/llm/switch` - Switch LLM provider
- `GET /admin/crawler/status` - Check crawler status
- `POST /admin/crawler/run` - Trigger crawler

### Review
- `GET /api/review/queue` - Get items for review
- `POST /api/review/{id}/action` - Take action on review item

## 🌍 Multilingual Support

The system supports fact-checking in multiple languages:

- **English**: "This is a test claim"
- **Hindi**: "यह एक परीक्षण दावा है"
- **Tamil**: "இது ஒரு சோதனை கூற்று"
- **Kannada**: "ಇದು ಪರೀಕ್ಷಾ ಹೇಳಿಕೆ"

## 🔒 Security

- JWT-based authentication
- HMAC-signed audit logs
- Rate limiting
- Input validation
- SQL injection protection

## 📊 Monitoring

- Prometheus metrics at `/metrics`
- Health checks at `/health`
- Admin dashboard for system monitoring
- Audit logs for all operations

## 🚀 Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Vertex AI Setup](docs/VERTEX_AI_SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in `docs/`
- Review the API documentation at `/docs`
- Create an issue in the repository

---

**Built with ❤️ for truth and transparency**
