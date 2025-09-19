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
cd FactForge/project
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

### 4. Initialize Database

```bash
# Database is automatically initialized with init.sql
# Check logs to ensure all tables are created
docker-compose logs postgres
```

### 5. Start Crawling

```bash
# Trigger crawler
curl -X POST http://localhost:8000/api/admin/crawler/run \
  -H "Authorization: Bearer <admin-token>"

# Or run crawler directly
docker exec -it factforge-backend_crawler_1 scrapy crawl seed_spider
```

### 6. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test fact-checking
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
    "language": "en"
  }'
```

## 📚 API Documentation

Once the services are running, visit:
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:5050 (PgAdmin)
- **RabbitMQ Management**: http://localhost:15672

## 🔧 Development

### Local Development Setup

```bash
# Install Python dependencies
pip install -r api/requirements.txt
pip install -r workers/enrichment_worker/requirements.txt
pip install -r workers/ingest_worker/requirements.txt
pip install -r crawler/requirements.txt

# Install Tesseract (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-tam tesseract-ocr-kan

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b

# Start services locally
python api/app/main.py
python workers/enrichment_worker/main.py
python workers/ingest_worker/main.py
scrapy crawl seed_spider
```

### Running Tests

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration_test.py
```

## 🌐 Multilingual Support

### Supported Languages
- **English (en)**: Primary language
- **Hindi (hi)**: Devanagari script
- **Tamil (ta)**: Tamil script  
- **Kannada (kn)**: Kannada script

### Language Detection
- Uses FastText model for automatic language detection
- Fallback to heuristic detection based on script analysis
- Confidence scoring for detection reliability

### Transliteration Support
- Hinglish (Hindi in Latin script) detection and conversion
- Automatic transliteration using indic-transliteration library
- Support for mixed-language content

### OCR Processing
- Tesseract OCR with language-specific models
- Automatic language selection based on detected language
- Image preprocessing for better OCR accuracy

## 🔍 Fact-Checking Process

1. **Input Processing**: Language detection and text normalization
2. **Embedding Generation**: Create vector embeddings using multilingual model
3. **Vector Search**: Find similar claims in Milvus vector database
4. **LLM Analysis**: Use Ollama to analyze claim against evidence
5. **Result Generation**: Return verdict, confidence, and evidence
6. **Mini-Lesson**: Generate educational content (optional)

## 📊 Monitoring and Observability

### Health Checks
- **API Health**: `GET /health`
- **Service Status**: Individual service health indicators
- **Database Connectivity**: PostgreSQL connection status
- **Vector DB Status**: Milvus connection and indexing status

### Metrics
- Request latency and throughput
- Classification accuracy by language
- Queue lengths and processing times
- Error rates and failure modes

### Logging
- Structured JSON logging
- HMAC-signed audit logs
- Error tracking and alerting
- Performance monitoring

## 🔒 Security

### Authentication
- JWT-based authentication
- Role-based access control (user, reviewer, admin)
- Token expiration and refresh

### Data Protection
- HMAC-signed audit logs
- PII redaction for public endpoints
- Secure credential management
- Rate limiting and abuse prevention

### Privacy
- Local processing (no external API calls)
- Data retention policies
- User data anonymization
- Compliance with privacy regulations

## 🚀 Deployment

### Production Considerations
- Use production-grade database (PostgreSQL with replication)
- Set up proper monitoring and alerting
- Configure backup and disaster recovery
- Use container orchestration (Kubernetes)
- Set up CI/CD pipelines
- Configure proper logging and metrics

### Scaling
- Horizontal scaling of workers
- Database read replicas
- Redis clustering
- Load balancing for API
- CDN for static assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- Scrapy team for the powerful web scraping framework
- Ollama team for local LLM inference
- Milvus team for vector database capabilities
- All open-source contributors who made this project possible

---

**Note**: This is a development/demo version. For production use, please review security settings, implement proper monitoring, and follow best practices for deployment and maintenance.