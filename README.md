# FactForge Mobile - Expo React Native App

A comprehensive mobile-first application for AI-powered fact-checking and community-driven scam alerts, built with Expo and React Native. Now featuring Tamil language support alongside English and Hindi.

## 🚀 Quick Start with Expo Go

### Prerequisites
- Install [Expo Go](https://expo.dev/client) on your mobile device
- Install [Node.js](https://nodejs.org/) (v16 or later)
- Install Expo CLI: `npm install -g @expo/cli`

### Running the App

1. **Navigate to the mobile app directory:**
   ```bash
   cd FactForgeMobile
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npx expo start
   ```

4. **Open on your device:**
   - **iOS**: Open Camera app and scan the QR code
   - **Android**: Open Expo Go app and scan the QR code
   - **Simulator**: Press `i` for iOS simulator or `a` for Android emulator

## 📱 Features

### Core Functionality
- **Social Feed**: Browse community scam alerts and fact-checks
- **AI Fact Checker**: Analyze text, URLs, and images for credibility
- **Communities**: Join public and private groups for targeted discussions
- **User Profiles**: Track contributions, badges, and activity

### Mobile-Specific Features
- **Camera Integration**: Take photos for fact-checking
- **Image Picker**: Select images from gallery
- **Haptic Feedback**: Tactile responses for interactions
- **Native Sharing**: Share results using device share sheet
- **Offline Support**: Basic caching for improved performance
- **Push Notifications**: Real-time alerts (configured but not active in demo)
- **Multi-language Support**: English, Hindi, and Tamil with i18n integration

### UI/UX Highlights
- **Responsive Design**: Optimized for all screen sizes
- **Native Navigation**: Tab-based navigation with stack screens
- **Smooth Animations**: Native performance with React Native Reanimated
- **Accessibility**: Screen reader support and proper contrast ratios
- **Touch-Friendly**: 44px minimum touch targets
- **Mobile-First Design**: Completely redesigned for mobile-first experience

## 🏗️ App Structure

```
FactForgeMobile/
├── app/                    # Expo Router pages
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── index.tsx      # Feed screen
│   │   ├── check.tsx      # Fact-check screen
│   │   ├── communities.tsx # Communities screen
│   │   └── profile.tsx    # Profile screen
│   ├── check-result.tsx   # Modal result screen
│   └── _layout.tsx        # Root layout
├── components/            # Reusable components
│   ├── TrustMeter.tsx    # Circular trust score widget
│   └── FeedCard.tsx      # Social post card
├── i18n/                 # Internationalization
│   ├── index.ts          # i18n configuration
│   └── locales/          # Language files (en, hi, ta)
├── services/             # API and data services
│   └── api.ts           # Mock API implementation
├── types/               # TypeScript definitions
│   └── index.ts        # Shared type definitions
└── assets/             # Images and static files
```

## 🎯 Demo Scenarios

### 1. Fact-Check a Scam Message
1. Go to **Check** tab
2. Paste: "Send ₹1000 to UPI abc@upi to claim lottery prize!"
3. Tap **Check Content**
4. View trust score and evidence
5. Tap **Publish as Alert** to share with community

### 2. Browse Community Feed
1. Go to **Feed** tab
2. Scroll through scam alerts
3. Tap heart to upvote posts
4. View trust scores and evidence counts

### 3. Join Communities
1. Go to **Communities** tab
2. Browse available communities
3. Tap **Join Community** for public groups
4. View community stats and member counts

### 4. Camera Integration
1. Go to **Check** tab
2. Tap **Camera** button
3. Take photo of suspicious message
4. Process for fact-checking

## 🔧 Development

### Available Scripts
- `npm start` - Start Expo development server
### 5. Language Support
1. Go to **Profile** tab
2. Tap **Language** in menu
3. Choose from English, Hindi, or Tamil
4. App interface updates immediately
- `npm run android` - Open on Android device/emulator
- `npm run ios` - Open on iOS device/simulator
- `npm run web` - Open in web browser

### Key Dependencies
- **Expo SDK 51** - Development platform
- **React Native 0.74** - Mobile framework
- **Expo Router** - File-based navigation
- **React Native SVG** - Vector graphics for TrustMeter
- **Expo Image Picker** - Camera and gallery access
- **Expo Haptics** - Tactile feedback
- **Expo Sharing** - Native sharing capabilities
- **i18next** - Internationalization framework
- **react-i18next** - React integration for i18n

### Mock Data
The app includes comprehensive mock data:
- Sample users with avatars and verification status
- Demo posts with various trust scores and categories
- Community examples with different privacy levels
- Realistic API response simulation with delays

## 📊 Performance Optimizations

- **Lazy Loading**: Components load on demand
- **Image Optimization**: Expo Image with caching
- **Memory Management**: Proper cleanup of listeners
- **Bundle Splitting**: Optimized for fast startup
- **Native Performance**: Leverages platform-specific optimizations
- **Mobile-First Rendering**: Optimized component rendering for mobile

## 🔒 Security & Privacy

- **No Real Data**: All demo data is mock/simulated
- **Permission Handling**: Proper camera/gallery permissions
- **Secure Storage**: AsyncStorage for local data
- **API Security**: Prepared for JWT authentication
- **Privacy Compliance**: GDPR-ready data handling

## 🌐 Deployment Options

### Expo Go (Current)
- Instant testing on device
- No app store required
- Perfect for demos and development

### Standalone Builds
```bash
# Build for app stores
npx eas build --platform all

# Create development build
npx eas build --profile development
```

### Web Version
```bash
# Run as web app
npx expo start --web
```

## 🎨 Customization

### Theming
Colors and styles are centralized in component StyleSheets:
- Primary: `#0d9488` (Teal)
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Orange)
- Error: `#ef4444` (Red)

### Language Support
Add new languages by:
1. Creating new JSON file in `i18n/locales/`
2. Adding language to `i18n/index.ts`
3. Updating language selector in profile
### Adding Features
1. Create new screen in `app/` directory
2. Add components in `components/`
3. Update navigation in `_layout.tsx`
4. Add API endpoints in `services/api.ts`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test on device
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-name`
6. Submit Pull Request

## 📞 Support

For issues or questions:
- Check Expo documentation: https://docs.expo.dev/
- React Native guides: https://reactnative.dev/
- File issues in the repository

---

**Built with ❤️ for transparent, trustworthy fact-checking on mobile devices. Now supporting English, Hindi, and Tamil languages.**



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
