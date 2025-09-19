# Google Vertex AI Integration Setup

This guide will help you set up Google Vertex AI integration for the FactForge backend.

## 🎯 Overview

The FactForge backend now supports both **Google Vertex AI** and **Ollama** as LLM providers. Vertex AI provides access to Google's advanced language models like Gemini, while Ollama provides local inference capabilities.

## 🔧 Prerequisites

1. **Google Cloud Platform Account**
   - Active GCP account with billing enabled
   - Project with Vertex AI API enabled

2. **Google Cloud CLI**
   - Install from: https://cloud.google.com/sdk/docs/install

3. **Python Dependencies**
   - Already included in `api/requirements.txt`

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
# Make the script executable
chmod +x scripts/setup_gcp.py

# Run the setup
python scripts/setup_gcp.py
```

The script will:
- Check for Google Cloud CLI
- Authenticate with your GCP account
- Create a service account with necessary permissions
- Generate credentials file
- Update environment configuration
- Enable required APIs

### Option 2: Manual Setup

#### Step 1: Install Google Cloud CLI

**Windows:**
```bash
# Download and install from:
# https://cloud.google.com/sdk/docs/install
```

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

#### Step 2: Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### Step 3: Enable Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

#### Step 4: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create factforge-service-account \
    --display-name="FactForge Service Account" \
    --description="Service account for FactForge backend"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:factforge-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:factforge-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

#### Step 5: Create Credentials File

```bash
# Create key file
gcloud iam service-accounts keys create credentials/factforge-service-account-key.json \
    --iam-account=factforge-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### Step 6: Update Environment Configuration

Copy `infra/env.sample` to `.env` and update:

```bash
# Google Cloud Platform Configuration
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GCP_CREDENTIALS_PATH=./credentials/factforge-service-account-key.json
VERTEX_AI_MODEL=gemini-1.5-pro
VERTEX_AI_TEMPERATURE=0.1
VERTEX_AI_MAX_TOKENS=1000

# LLM Provider Selection (vertex_ai, ollama)
LLM_PROVIDER=vertex_ai
```

## 🔄 Switching Between Providers

### Using Environment Variable

Set `LLM_PROVIDER` in your `.env` file:
- `LLM_PROVIDER=vertex_ai` - Use Google Vertex AI
- `LLM_PROVIDER=ollama` - Use Ollama (local)

### Using Admin API

```bash
# Check current provider status
curl -X GET http://localhost:8000/admin/llm/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Switch to Vertex AI
curl -X POST http://localhost:8000/admin/llm/switch \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": "vertex_ai"}'

# Switch to Ollama
curl -X POST http://localhost:8000/admin/llm/switch \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": "ollama"}'
```

## 🧪 Testing the Integration

### Start the Services

```bash
# Start all services
docker-compose -f infra/docker-compose.yml up --build

# Or start in background
docker-compose -f infra/docker-compose.yml up -d --build
```

### Test Fact-Checking API

```bash
# Test English claim
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
    "language": "en"
  }'

# Test Hindi claim
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "तत्काल ₹1000 UPI abc@upi पर भेजें और ₹50,000 का लॉटरी पुरस्कार जीतें!",
    "language": "hi"
  }'

# Test Tamil claim
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "உடனடியாக ₹1000 UPI abc@upi க்கு அனுப்பி ₹50,000 லாட்டரி பரிசு வெல்லுங்கள்!",
    "language": "ta"
  }'
```

### Check Provider Status

```bash
# Check which provider is active
curl -X GET http://localhost:8000/admin/llm/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔍 Monitoring and Debugging

### Check Logs

```bash
# Check API logs
docker-compose -f infra/docker-compose.yml logs api

# Check specific service logs
docker-compose -f infra/docker-compose.yml logs -f api
```

### Common Issues

1. **Authentication Error**
   ```
   Error: Could not automatically determine credentials
   ```
   - Solution: Ensure credentials file path is correct
   - Check service account permissions

2. **API Not Enabled**
   ```
   Error: API [aiplatform.googleapis.com] not enabled
   ```
   - Solution: Enable Vertex AI API in GCP Console

3. **Project Not Found**
   ```
   Error: Project not found
   ```
   - Solution: Verify project ID is correct
   - Check billing is enabled

4. **Model Not Available**
   ```
   Error: Model not found
   ```
   - Solution: Check model name in environment
   - Verify model is available in your region

## 💰 Cost Considerations

### Vertex AI Pricing

- **Gemini 1.5 Pro**: ~$0.00125 per 1K input tokens, ~$0.005 per 1K output tokens
- **Free Tier**: $300 credit for new accounts
- **Estimated Cost**: ~$0.01-0.05 per fact-check request

### Cost Optimization

1. **Use Caching**: Responses are cached to reduce API calls
2. **Batch Processing**: Process multiple requests together
3. **Fallback to Ollama**: Use local inference for development
4. **Monitor Usage**: Set up billing alerts in GCP

## 🔒 Security Best Practices

1. **Credentials Management**
   - Store credentials file securely
   - Use environment variables in production
   - Rotate service account keys regularly

2. **Access Control**
   - Use least privilege principle
   - Monitor service account usage
   - Enable audit logging

3. **Data Privacy**
   - Claims are processed by Google's models
   - Consider data residency requirements
   - Implement data retention policies

## 🚀 Production Deployment

### Environment Variables

```bash
# Production environment
GCP_PROJECT_ID=your-production-project
GCP_REGION=us-central1
GCP_CREDENTIALS_PATH=/app/credentials/service-account-key.json
VERTEX_AI_MODEL=gemini-1.5-pro
LLM_PROVIDER=vertex_ai
```

### Docker Configuration

```dockerfile
# Copy credentials
COPY credentials/ /app/credentials/

# Set environment
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json
```

### Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gcp-credentials
type: Opaque
data:
  service-account-key.json: <base64-encoded-credentials>
```

## 📊 Performance Comparison

| Feature | Vertex AI | Ollama |
|---------|-----------|--------|
| **Speed** | Fast (cloud) | Medium (local) |
| **Quality** | High (Gemini) | Good (Llama) |
| **Cost** | Pay per use | Free |
| **Privacy** | Cloud processing | Local processing |
| **Scalability** | High | Limited |
| **Offline** | No | Yes |

## 🎯 Recommendations

### For Development
- Use **Ollama** for local development
- Switch to **Vertex AI** for testing

### For Production
- Use **Vertex AI** for high-quality results
- Implement **Ollama** as fallback
- Monitor costs and usage

### For Cost-Conscious Projects
- Use **Ollama** for most requests
- Use **Vertex AI** for complex cases only

## 📚 Additional Resources

- [Google Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Reference](https://ai.google.dev/docs)
- [Ollama Documentation](https://ollama.ai/docs)
- [FactForge API Documentation](http://localhost:8000/docs)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs api`
2. Verify credentials: `gcloud auth list`
3. Test API access: `gcloud ai models list`
4. Check service status: `curl http://localhost:8000/admin/llm/status`

For additional help, please refer to the main [README.md](../README.md) or create an issue in the repository.
